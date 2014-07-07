from MonQL import Connections
from pprint import pprint

def con(conid = 0):
    print '\n  **testing con with connection id = %d**' % conid
    response = Connections.test_connection(conid)
    print response

def tree(conid = 0):
    print '\n  **testing tree with connection id = %d**' % conid
    data = Connections.tree_json(conid)
    pprint(data)

TEST_DB = 0

con(TEST_DB)
tree(TEST_DB)