from datetime import datetime as dtdt
import traceback, json, os
from FlaskViewer import app
import Inspect
from pprint import pprint

class Connections(object):
    _cons = None

    def __call__(self):
        return self.get_cons()

    def get_cons(self):
        if not self._cons:
            self._cons = self._get_cons()
        return self._cons

    def _get_cons(self):
        fn = app.config['CONNECTION_DEFS']
        if os.path.exists(fn):
            text = open(fn, 'r').read()
            if len(text) > 0:
                return json.loads(text)
        return []

    def select(self, conid):
        return next((con for con in self.get_cons() if con['id'] == conid), None)

    def update(self, con):
        cons = self.get_cons()
        if 'id' in con:
            old = next((con2 for con2 in cons if con2['id'] == con['id']), None)
            if old: cons.remove(old)
        else:
            if len(cons) == 0:
                con['id'] = 0
            else:
                con['id'] = max(cons, key=lambda con2: con2['id'])['id'] + 1
        cons.append(con)
        self._save_cons(cons)
        self._cons = None
        return con

    def delete(self, conid):
        cons = self.get_cons()
        print 'before:', len(cons)
        cons = [con for con in cons if con['id'] != conid]
        self._save_cons(cons)
        self._cons = None
        print 'after:', len(cons)

    def _save_cons(self, cons):
        json.dump(cons, 
            open(app.config['CONNECTION_DEFS'], 'w'), 
            indent=2, 
            separators=(',', ': '), 
            sort_keys = True)

connections = Connections()

def getcomms(con):
    return getattr(Inspect, con['dbtype'])(con)

def test_connection(conid):
    con = connections.select(int(conid))
    response = 'Connectiong to "%s"\n' % con['ref']
    try:
        comms = getcomms(con)
        response += 'connecting with %s\n' % comms.__class__.__name__
        response += 'Successfully connected\n'
        response += 'Version: %s\n' % comms.get_version()
        response += 'Server Info:\n%s\n' % comms.server_info()
        if 'dbname' in con:
            response += 'Connection to db %s\n' % con['dbname']
            tables, _ = comms.get_tables(con['dbname'])
            response += '%d tables found\n' % len(tables)
        else:
            response += 'No database name entered, not connecting to db'
    except Exception, e:
        traceback.print_exc()
        response += '\n** Error: %s %s **' % (e.__class__.__name__, str(e))
    else:
        response += '\n** Successfully Connected **'
    return response

def tree_json(conid, node = None):
    tree = TreeGenerater(conid)
    if node:
        return tree.get_values(node)
    else:
        return tree.data

class TreeGenerater(object):
    _id = 0
    comms = {}
    
    def __init__(self, conid):
        self.data = {'DATA': []}
        self._con = connections()[conid]
        self._comms = getcomms(self._con)
        self._get_con()
    
    def get_values(self, node_id):
        node_id = int(node_id)
        dbname, table = self._find_table(node_id)
        table_name = table['table_name']
        fields = [f[0] for f in table['fields']]
        rows = self._get_rows(self._comms.get_values(dbname, table_name), fields)
        table['children'] = rows
        if 'load_on_demand' in table:
            del table['load_on_demand']
        return rows

    @property
    def json_data(self):
        return self._2json(self.data)

    def _2json(self, data):
        return json.dumps(data, indent=2)
    
    # def execute_query(self, query):
    #     comms = self._get_comms(m.Database.objects.get(id=query.db.id))
    #     success, result, fields = comms.execute(query.code, query.function)
    #     if success:
    #         rows = self._get_rows(result, fields)
    #         d = {'id': self._get_id(), 'label': 'QUERY: %s' % str(query), 'children': rows}
    #         d['info'] = [('Query Properties', [])]
    #         d['info'][0][1].append(('Results', len(rows)))
    #         d['info'][0][1].append(('Code', query.code))
    #         self.data['DATA'].append(d)
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
        for con in self.data['DATA']:
            for db in con['children']:
                dbname = db['name']
                for table in db['children']:
                    if table['id'] == node_id:
                        return dbname, table
        raise Exception('Table %d not found' % node_id)
    
    def _get_con(self):
        try:
            c = {'id': self._get_id(), 'label': 'CONNECTION: %s' % self._con['ref'], 'con_id': self._con['id']}
            c['info'] = [('Database Properties', [])]
            for name, value in self._con.items():
                c['info'][0][1].append((name, value))
            c['info'][0][1].append(('DB Version', self._comms.get_version()))
            c['info'][0][1].append(('Server Info', self._comms.server_info()))
            dbs = []
            for name in self._comms.get_databases():
                dbs.append(('', name))
            if len(dbs) > 0:
                c['info'].append(('Databases', dbs))
            if 'dbname' in self._con:
                dbs = [self._con['dbname']]
            else:
                dbs = self._comms.get_databases()
            c['children'] = self._get_dbs(dbs)
        except Exception, e:
            traceback.print_exc()
            self.data['ERROR'] = str(e)
        else:
            self.data['DATA'].append(c)

    def _get_dbs(self, dbs):
        return [{'label': db, 
                 'children': self._get_tables(db), 
                 'id': self._get_id(),
                 'name': db} for db in dbs]

    def _get_tables(self, dbname):
        t_data = []
        tables, prop_names = self._comms.get_tables(dbname)
        for t_name, t_info in tables:
            table = {'id': self._get_id(), 'label': t_name, 'table_name': t_name, 'load_on_demand': True}
            table['info'] = [('Table Properties', []), ('Fields', [])]
            for name, value in zip(prop_names, t_info):
                if type(value) == dtdt:
                    value = value.strftime('%Y-%m-%d %H:%M:%S %Z')
                table['info'][0][1].append((name, value))
            fields = self._comms.get_table_fields(dbname, t_name)
            table['info'][0][1].append(('Field Count', len(fields)))
            table['fields'] = fields
            for name, field_type in fields:
                table['info'][1][1].append((name, str(field_type)))
            t_data.append(table)
        return t_data
            
    def _get_id(self):
        self._id += 1
        return self._id
    
    def _get_max_id(self):
        if self._id != 0 or len(self.data['DATA']) == 0:
            return self._id
        return self._get_max_id_rec(self.data['DATA'][-1])
    
    def _get_max_id_rec(self, ob):
        if 'children' in ob and len(ob['children']) > 0:
            return self._get_max_id_rec(ob['children'][-1])
        elif 'id' in ob:
            return ob['id']
        return self._id
