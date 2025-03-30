#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\subtitles\eveclient\entity_names.py
from checkpoints.common.fsdloader import CheckpointsLoader
from conversations.fsdloaders import ConversationsLoader
from fsdBuiltData.client.musicTriggers import GetMusicTrigger
from nodegraph.common.nodedata import get_node_graph_data
from nodegraph.subtitles.common.entity_names import register_entity_name_getter
from carbon.common.script.util.format import FmtDist
from uihider.fsd_loader import UiHidingTemplatesData
from uihighlighting.fsdloaders import MenuHighlightsLoader
from uihighlighting.fsdloaders import SpaceObjectHighlightsLoader
from uihighlighting.fsdloaders import UIHighlightsLoader
from nodegraph.client.util import get_location_name

def get_conversation_name(conversation_id):
    conversation = ConversationsLoader.GetByID(conversation_id)
    if conversation:
        return conversation.name


def get_ui_highlight_name(highlight_id):
    highlight = UIHighlightsLoader.GetByID(highlight_id)
    if highlight:
        return highlight.name


def get_menu_highlight_name(highlight_id):
    highlight = MenuHighlightsLoader.GetByID(highlight_id)
    if highlight:
        return highlight.name


def get_space_object_highlight_name(highlight_id):
    highlight = SpaceObjectHighlightsLoader.GetByID(highlight_id)
    if highlight:
        return highlight.name


def ui_hiding_template_name(template_id):
    template = UiHidingTemplatesData.get_ui_hiding_template_by_id(template_id)
    if template:
        return template.name


def get_music_trigger_event(music_trigger_id):
    music_trigger = GetMusicTrigger(music_trigger_id)
    if music_trigger:
        return music_trigger.trigger


def get_node_graph_name(node_graph_id):
    graph = get_node_graph_data(node_graph_id)
    if graph:
        return graph.name


def get_checkpoint_name(checkpoint_id):
    checkpoint = CheckpointsLoader().GetByID(checkpoint_id)
    if checkpoint:
        return checkpoint.name


def register_entity_name_getters():
    register_entity_name_getter('checkpoint', get_checkpoint_name)
    register_entity_name_getter('conversation', get_conversation_name)
    register_entity_name_getter('ui_highlight', get_ui_highlight_name)
    register_entity_name_getter('menu_highlight', get_menu_highlight_name)
    register_entity_name_getter('space_object_highlight', get_space_object_highlight_name)
    register_entity_name_getter('ui_hiding_template', ui_hiding_template_name)
    register_entity_name_getter('music_trigger', get_music_trigger_event)
    register_entity_name_getter('node_graph', get_node_graph_name)
    register_entity_name_getter('location', get_location_name)
    register_entity_name_getter('distance', FmtDist)
