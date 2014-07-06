from FlaskViewer import Connections
from pprint import pprint

def con(conid = 0):
    print '\n  **testing con with connection id = %d**' % conid
    response = Connections.test_connection(conid)
    print response

def tree(conid = 0):
    print '\n  **testing tree with connection id = %d**' % conid
    data = Connections.tree_json(conid)
    print data