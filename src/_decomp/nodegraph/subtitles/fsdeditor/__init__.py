#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\subtitles\fsdeditor\__init__.py
from nodegraph.subtitles import get_subtitle as _get_subtitle
_HAS_REGISTERED_FUNCS = False

def get_subtitle(node_type, **kwargs):
    global _HAS_REGISTERED_FUNCS
    if not _HAS_REGISTERED_FUNCS:
        register()
    return _get_subtitle(node_type, **kwargs)


def register():
    global _HAS_REGISTERED_FUNCS
    _HAS_REGISTERED_FUNCS = True
    from nodegraph.subtitles.common.entity_names import register_entity_name_getters as register_common_entity_name_getters
    from nodegraph.subtitles.common.custom import register_subtitle_functions as register_common_subtitle_functions
    from nodegraph.subtitles.fsdeditor.entity_names import register_entity_name_getters
    from nodegraph.subtitles.fsdeditor.custom import register_subtitle_functions
    register_common_subtitle_functions()
    register_common_entity_name_getters()
    register_entity_name_getters()
    register_subtitle_functions()
