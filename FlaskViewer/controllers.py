from flask import render_template, jsonify, request, abort
from FlaskViewer import app
import json, os, traceback
import Inspect

def jsonabort(e):
    traceback.print_exc()
    print 'ERROR: %s' % str(e)
    return jsonify(error = str(e)), 400

def connections():
    fn = app.config['CONNECTION_DEFS']
    if os.path.exists(fn):
        text = open(fn, 'r').read()
        if len(text) > 0:
            return json.loads(text)
    return []

def selectcon(conid):
    return next((con for con in connections() if con['id'] == conid), None)

def update_cons(con):
    cons = connections()
    if 'id' in con:
        old = next((con2 for con2 in cons if con2['id'] == con['id']), None)
        if old: cons.remove(old)
    else:
        if len(cons) == 0:
            con['id'] = 0
        else:
            con['id'] = max(cons, key=lambda con2: con2['id'])['id'] + 1
    cons.append(con)
    json.dump(cons, 
        open(app.config['CONNECTION_DEFS'], 'w'), 
        indent=2, 
        separators=(',', ': '), 
        sort_keys = True)
    return con

@app.route('/')
@app.route('/about')
@app.route('/addcon')
@app.route('/editcon/<x>')
@app.route('/con/<x>')
def index(x=None):
    print connections()
    return render_template('main.html')

@app.route('/api/cons')
def conlist():
    return jsonify(cons=connections())

@app.route('/api/condef/<conid>')
def condef(conid):
    try:
        return jsonify(con=selectcon(int(conid)))
    except Exception, e: return jsonabort(e)

@app.route('/api/viewcon/<conid>')
def view_connection(conid):
    print type(conid), conid
    data = [
        {
            'label': 'node1',
            'children': [{ 'label': 'child1' },{ 'label': 'child2' }]
        },
        {
            'label': 'node2',
            'children': [ { 'label': 'child3' } ]
        }
    ]
    return jsonify(DATA=data)

@app.route('/api/submitcon', methods=['POST'])
def submitcon():
    try:
        data = json.loads(request.data)
        data = update_cons(data)
        return jsonify(status='success', data=data)
    except Exception, e: return jsonabort(e)


@app.route('/api/testcon/<conid>')
def test_connection(conid):
    try:
        con = selectcon(int(conid))
        response = ''
        try:
            Cls = getattr(Inspect, con['dbtype'])
            response += 'connecting with %s\n' % Cls.__name__
            cls = Cls(con)
            response += 'Successfully connected\n'
            response += 'Version %s\n' % cls.get_version()
        except Exception, e:
            response += '\n** Error Connecting: %s **' % str(e)
        else:
            response += '\n** Successfully Connected **'
        return response
    except Exception, e: return jsonabort(e)



@app.errorhandler(404)
def page_not_found(e):
    # return index()
    return '404 - page not found', 404