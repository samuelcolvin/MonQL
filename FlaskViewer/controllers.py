from flask import render_template, jsonify
from FlaskViewer import app

@app.route('/')
@app.route('/about')
@app.route('/db/<x>')
def index(x=None):
	print 'x =', x
	return render_template('main.html')

@app.route('/api/dbs')
def dblist():
	dbs = [{'id': '1', 'name': 'db1'}, {'id': '2', 'name': 'db2'}]
	return jsonify(dblist=dbs)

@app.route('/api/db/<dbid>')
def dbdetails(dbid):
	print type(dbid), dbid
	# dbs = [, {'id': '2', 'name': 'db2'}]
	return jsonify(db={'id': '1', 'name': 'db1'})

@app.errorhandler(404)
def page_not_found(e):
	# return index()
	return '404 - page not found', 404