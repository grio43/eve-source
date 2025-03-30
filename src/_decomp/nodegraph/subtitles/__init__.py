#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\subtitles\__init__.py
from logging import getLogger
from nodegraph.subtitles.common.entity_names import get_entity_name_getter
from nodegraph.subtitles.format import format
logger = getLogger(__name__)
GENERATOR_BY_NODE_PROPERTIES = {}

def get_subtitle(node_type, node_type_fmt_string = None, node_type_params = None, atom_id = None, atom_fmt_string = None, atom_params = None):
    try:
        node_type_subtitle = get_node_type_subtitle(node_type, node_type_fmt_string, node_type_params)
        atom_subtitle = get_atom_subtitle(node_type, atom_id, atom_fmt_string, atom_params)
        if node_type_subtitle and atom_subtitle:
            return '{} - {}'.format(node_type_subtitle, atom_subtitle)
        if atom_subtitle:
            return atom_subtitle
        return node_type_subtitle
    except Exception as exc:
        logger.exception('Failed to get subtitle for node; exception: %s', exc)
        return ''


def get_node_type_subtitle(node_type, fmt_string = None, node_type_params = None):
    params = node_type_params if node_type_params else {}
    if fmt_string:
        return format(fmt_string, **params)
    generator = GENERATOR_BY_NODE_PROPERTIES.get((node_type,))
    if generator:
        return generator(**params)


def get_atom_subtitle(node_type, atom_id, fmt_string = None, atom_params = None):
    params = atom_params if atom_params else {}
    if fmt_string:
        return format(fmt_string, **params)
    generator = GENERATOR_BY_NODE_PROPERTIES.get((node_type, atom_id))
    if generator:
        return generator(**params)


def register_subtitle_function(node_type, atom_ids = None, func = None):
    if atom_ids:
        for atom_id in atom_ids:
            GENERATOR_BY_NODE_PROPERTIES[node_type, atom_id] = func

    else:
        GENERATOR_BY_NODE_PROPERTIES[node_type] = func
