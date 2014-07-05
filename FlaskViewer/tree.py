from datetime import datetime as dtdt
import traceback, json

def tree_json(request):
    tree = TreeGenerater()
    json = tree.json_data
    if 'node' in request.GET:
        json = tree.get_values(request.GET['node'])
    return HttpResponse(json, content_type="application/json")

class TreeGenerater:
    _id = 0
    comms = {}
    
    def __init__(self):
        self._data = {'DATA': []}
        for db in m.Database.objects.filter(live=True):
            self._get_dbs(db)
        self._generate_json()
            
    def _generate_json(self):
        self.json_data = json.dumps(self._data, indent=2)
    
    def get_values(self, node_id):
        node_id = int(node_id)
        db_id, table = self._find_table(node_id)
        comms = self._get_comms(m.Database.objects.get(id=db_id))
        table_name = table['table_name']
        fields = [f[0] for f in table['fields']]
        rows = self._get_rows(comms.get_values(table_name), fields)
        table['children'] = rows
        if 'load_on_demand' in table:
            del table['load_on_demand']
        self._generate_json()
        return json.dumps(rows)
    
    # def execute_query(self, query):
    #     comms = self._get_comms(m.Database.objects.get(id=query.db.id))
    #     success, result, fields = comms.execute(query.code, query.function)
    #     if success:
    #         rows = self._get_rows(result, fields)
    #         d = {'id': self._get_id(), 'label': 'QUERY: %s' % str(query), 'children': rows}
    #         d['info'] = [('Query Properties', [])]
    #         d['info'][0][1].append(('Results', len(rows)))
    #         d['info'][0][1].append(('Code', query.code))
    #         self._data['DATA'].append(d)
    #         self._generate_json()
    #         return None
    #     else:
    #         return result
            
    def _get_rows(self, raw_rows, fields):
        rows = []
        for v, label in raw_rows:
            row = {'id': self._get_id(), 'label': label}
            row['info'] = [['', []]]
            row['info'][0][1] = [(name, val) for name, val in zip(fields, v)]
            rows.append(row)
        return rows
    
    def _find_table(self, node_id):
        for db_info in self._data['DATA']:
            db_id = db_info['db_id']
            for table in db_info['children']:
                if table['id'] == node_id:
                    return db_id, table
    
    def _get_dbs(self, db):
        try:
            comms = self._get_comms(db)
            d = {'id': self._get_id(), 'label': 'DATABASE: %s' % db.name, 'db_id': db.id}
            d['info'] = [('Database Properties', [])]
            for name, value in db.conn_values():
                d['info'][0][1].append((name, value))
            d['info'][0][1].append(('DB Version', comms.get_version()))
            dbs = []
            for name in comms.get_databases():
                dbs.append(('', name))
            if len(dbs) > 0:
                d['info'].append(('Databases', dbs))
            d['children'] = self._get_tables(comms, db)
        except Exception, e:
            traceback.print_exc()
            self._data['ERROR'] = str(e)
        else:
            self._data['DATA'].append(d)
    
    def _get_comms(self, db):
        if db.id not in self.comms:
            self.comms[db.id] = db.get_comms()
        return self.comms[db.id]
        
    def _get_tables(self, comms, db):
        t_data = []
        tables, prop_names = comms.get_tables()
        for t_name, t_info in tables:
            table = {'id': self._get_id(), 'label': t_name, 'table_name': t_name, 'load_on_demand': True}
            table['info'] = [('Table Properties', []), ('Fields', [])]
            for name, value in zip(prop_names, t_info):
                if type(value) == dtdt:
                    value = value.strftime('%Y-%m-%d %H:%M:%S %Z')
                table['info'][0][1].append((name, value))
            fields = comms.get_table_fields(t_name)
            table['info'][0][1].append(('Field Count', len(fields)))
            table['fields'] = fields
            for field in fields:
                table['info'][1][1].append((field[0], str(field[1])))
            t_data.append(table)
        return t_data
            
    def _get_id(self):
        self._id += 1
        return self._id
    
    def _get_max_id(self):
        if self._id != 0 or len(self._data['DATA']) == 0:
            return self._id
        return self._get_max_id_rec(self._data['DATA'][-1])
    
    def _get_max_id_rec(self, ob):
        if 'children' in ob and len(ob['children']) > 0:
            return self._get_max_id_rec(ob['children'][-1])
        elif 'id' in ob:
            return ob['id']
        return self._id
