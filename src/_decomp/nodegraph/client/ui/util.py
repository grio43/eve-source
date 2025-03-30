#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\ui\util.py


def position_to_ui(x, y):
    return (x * 75, y * 35)


def ui_to_position(x, y):
    return (max(0, round(x / 75.0)), max(0, round(y / 35.0)))


connection_color = {'input': (1, 0, 1, 0.7),
 'output': (0, 1, 1, 0.7),
 'on_next': (0, 1, 1, 0.7),
 'on_failure': (1, 0, 0, 0.7),
 'on_stop': (1, 0, 0, 0.7),
 'validation': (1, 1, 0, 0.7),
 'variables': (0, 1, 0, 0.7),
 'on_end': (1, 0.5, 0, 0.7),
 'nodes': (1, 0, 1, 0.7),
 'on_incomplete': (1, 0.5, 0, 0.7),
 'group_nodes': (1, 0, 0, 0.7)}

def get_connection_color(connection_id):
    return connection_color.get(connection_id, (0, 1, 1, 0.7))


connection_name = {'input': 'input',
 'output': 'output',
 'on_next': 'on_next',
 'on_failure': 'on_failure',
 'on_stop': 'on_stop',
 'validation': 'conditions',
 'variables': 'variables',
 'on_end': 'on_end',
 'nodes': 'nodes',
 'on_incomplete': 'on_incomplete',
 'group_nodes': 'events'}

def get_connection_name(connection_id):
    return connection_name.get(connection_id, connection_id)


def is_server_graph(tags):
    if not tags:
        return False
    return 'server' in tags or 'Server' in tags


def is_client_graph(tags):
    if not tags:
        return False
    return 'client' in tags or 'Client' in tags


def is_qa_graph(tags):
    if not tags:
        return False
    return 'qa' in tags or 'QA' in tags or 'Qa' in tags


def copy_value(value):
    import blue
    return blue.pyos.SetClipboardData(unicode(value))


class GraphColor(object):
    server = (0.25, 0.9, 0.9)
    client = (0.9, 0.1, 0.9)
    qa = (0.1, 0.9, 0.1)
    warning = (1, 0, 0)
