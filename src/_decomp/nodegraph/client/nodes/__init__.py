#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\nodes\__init__.py
_class_map = None

def get_all_node_classes():
    global _class_map
    if not _class_map:
        from nodegraph.client.nodes.class_registry import get_class_map
        _class_map = get_class_map()
    return _class_map


def get_node_class(node_type_id):
    return get_all_node_classes().get(node_type_id, None)
