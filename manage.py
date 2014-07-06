from flask.ext.script import Manager
import FlaskViewer

manager = Manager(FlaskViewer.app)
TEST_DB = 0

@manager.command
def test():
    """System Test"""
    import test
    test.con(TEST_DB)
    test.tree(TEST_DB)


# @manager.command
# def sync():
#     """Download new messages from twitter and forums"""
#     bf3.sync()
#     print 'Done syncing'


if __name__ == '__main__':
    manager.run()