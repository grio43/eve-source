#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\subtitles\fsdeditor\entity_names.py
import evetypes
from fsdeditor.modules.conversations import CONVERSATION_DATA_FORMAT
from platformtools.compatibility.exposure.fsdeditor import fsdutil
from fsdeditor.utils import localization
from nodegraph.subtitles.common.entity_names import register_entity_name_getters as register_common_entity_name_getters
from nodegraph.subtitles.common.entity_names import register_entity_name_getter
from evedungeons.server.data import GetDungeonNameID
from eve.common.script.sys.idCheckers import IsRegion
from eve.common.script.sys.idCheckers import IsConstellation
from eve.common.script.sys.idCheckers import IsSolarSystem
from eve.common.script.sys.idCheckers import IsStation
from fsdeditor.utils.universe import get_constellation_name
from fsdeditor.utils.universe import get_region_name
from fsdeditor.utils.universe import get_solarsystem_name
from fsdeditor.utils.universe import get_station_name
from fsdeditor.modules.nodegraphs.utils import get_node_graph_fsd

def get_conversation_name(conversation_id):
    conversation = fsdutil.data(CONVERSATION_DATA_FORMAT, conversation_id)
    if conversation:
        return conversation[conversation_id].name


def get_ui_highlight_name(highlight_id):
    ui_highlight = fsdutil.data('uiHighlights/uiHighlights.staticdata', highlight_id)
    if ui_highlight:
        return ui_highlight.name


def get_menu_highlight_name(highlight_id):
    menu_highlight = fsdutil.data('uiHighlights/menuHighlights.staticdata', highlight_id)
    if menu_highlight:
        return menu_highlight.name


def get_space_object_highlight_name(highlight_id):
    space_obj_highlight = fsdutil.data('uiHighlights/spaceObjectHighlights.staticdata', highlight_id)
    if space_obj_highlight:
        return space_obj_highlight.name


def ui_hiding_template_name(template_id):
    template = fsdutil.data('uihiding/uihidingtemplatesdata/{}.staticdata', template_id)
    if template:
        return template[template_id].name


def get_music_trigger_event(trigger_id):
    music_trigger = fsdutil.data('musicTriggers/musicTriggers.staticdata', trigger_id)
    if music_trigger:
        return music_trigger.trigger


def get_dungeon_name(dungeon_id):
    try:
        dungeon_name_id = GetDungeonNameID(dungeon_id)
        dungeon_name = localization.GetMessage('EVE/Dungeons/{}'.format(dungeon_id), dungeon_name_id)
    except (ImportError, KeyError):
        dungeon_name = 'Dungeon <no name>'

    return dungeon_name


def get_location_name(location_id):
    name = None
    if IsRegion(location_id):
        name = get_region_name(location_id)
    elif IsConstellation(location_id):
        name = get_constellation_name(location_id)
    elif IsSolarSystem(location_id):
        name = get_solarsystem_name(location_id)
    elif IsStation(location_id):
        name = get_station_name(location_id)
    if name:
        return '{} ({})'.format(name, location_id)


def get_node_graph_name(node_graph_id):
    graph = get_node_graph_fsd(node_graph_id)
    if graph:
        return graph['name']


def get_checkpoint_name(checkpoint_id):
    checkpoint = fsdutil.data('checkpoints/checkpoints.staticdata', checkpoint_id)
    if checkpoint:
        return checkpoint.name


def get_objective_name(objective_id):
    objective = fsdutil.data('objectives/objectivedata/{}.staticdata', objective_id)
    if objective:
        return objective[objective_id].name


def register_entity_name_getters():
    register_common_entity_name_getters()
    register_entity_name_getter('type', evetypes.GetName)
    register_entity_name_getter('checkpoint', get_checkpoint_name)
    register_entity_name_getter('conversation', get_conversation_name)
    register_entity_name_getter('ui_highlight', get_ui_highlight_name)
    register_entity_name_getter('menu_highlight', get_menu_highlight_name)
    register_entity_name_getter('space_object_highlight', get_space_object_highlight_name)
    register_entity_name_getter('ui_hiding_template', ui_hiding_template_name)
    register_entity_name_getter('music_trigger', get_music_trigger_event)
    register_entity_name_getter('dungeon', get_dungeon_name)
    register_entity_name_getter('location', get_location_name)
    register_entity_name_getter('node_graph', get_node_graph_name)
    register_entity_name_getter('objective', get_objective_name)
