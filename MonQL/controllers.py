from flask import render_template, jsonify, request
import json, traceback
from MonQL.Connections import app, connections, test_connection, tree_json

def jsonabort(e):
    traceback.print_exc()
    print 'ERROR: %s' % str(e)
    return jsonify(error = str(e)), 400

def jsonifyany(ob):
    if isinstance(ob, list):
        return json.dumps(ob)
    else:
        return jsonify(**ob)

@app.route('/')
@app.route('/about')
@app.route('/addcon')
@app.route('/editcon/<_>')
@app.route('/con/<_>')
def index(_=None):
    return render_template('main.html')

@app.route('/api/cons')
def conlist():
    return jsonify(cons=connections())

@app.route('/api/condef/<conid>')
def condef(conid):
    try:
        return jsonify(con = connections.select(int(conid)))
    except Exception, e: return jsonabort(e)

@app.route('/api/viewtree/<conid>')
def viewtree(conid):
    node = None
    if 'node' in request.args:
        node = int(request.args.get('node'))
    data = tree_json(int(conid), node)
    # pprint(data)
    return jsonifyany(data)

@app.route('/api/submitcon', methods=['POST'])
def submitcon():
    try:
        data = json.loads(request.data)
        data = connections.update(data)
        return jsonify(status='success', data=data)
    except Exception, e: return jsonabort(e)

@app.route('/api/testcon/<conid>')
def test_connection_response(conid):
    try:
        return test_connection(conid)
    except Exception, e: return jsonabort(e)

@app.route('/api/delete/<conid>')
def deletecon(conid):
    try:
        response = connections.delete(int(conid))
        return jsonify(status='success', data = response)
    except Exception, e: return jsonabort(e)

@app.errorhandler(404)
def page_not_found(_):
    # return index()
    return '404 - page not found', 404