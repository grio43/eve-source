#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\subtitles\eveclient\__init__.py
from nodegraph.subtitles import get_subtitle as _get_subtitle
_HAS_REGISTERED_FUNCS = False

def get_subtitle(node_type, **kwargs):
    global _HAS_REGISTERED_FUNCS
    if not _HAS_REGISTERED_FUNCS:
        register()
    return _get_subtitle(node_type, **kwargs)


def register():
    global _HAS_REGISTERED_FUNCS
    from nodegraph.subtitles.common.entity_names import register_entity_name_getters as register_common_entity_name_getters
    from nodegraph.subtitles.common.custom import register_subtitle_functions as register_common_subtitle_functions
    from nodegraph.subtitles.eveclient.custom import register_subtitle_functions
    from nodegraph.subtitles.eveclient.entity_names import register_entity_name_getters
    _HAS_REGISTERED_FUNCS = True
    register_common_entity_name_getters()
    register_common_subtitle_functions()
    register_entity_name_getters()
    register_subtitle_functions()
