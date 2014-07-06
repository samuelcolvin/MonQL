from flask import render_template, jsonify, request
import json, traceback
from FlaskViewer.Connections import app, connections, test_connection

def jsonabort(e):
    traceback.print_exc()
    print 'ERROR: %s' % str(e)
    return jsonify(error = str(e)), 400

@app.route('/')
@app.route('/about')
@app.route('/addcon')
@app.route('/editcon/<_>')
@app.route('/con/<_>')
def index(_=None):
    print connections()
    return render_template('main.html')

@app.route('/api/cons')
def conlist():
    return jsonify(cons=connections())

@app.route('/api/condef/<conid>')
def condef(conid):
    try:
        return jsonify(con = connections.select(int(conid)))
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