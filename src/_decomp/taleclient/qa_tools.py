#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\taleclient\qa_tools.py
from carbonui.services.setting import SessionSettingNumeric
from carbonui.control.contextMenu.menuUtil import CloseContextMenus
from carbonui.control.contextMenu.menuData import MenuData
from objectives.client.qa_tools import get_objective_chain_context_menu, is_qa
from talecommon.const import sceneTypesByID
import threadutils
_qa_set_influence_setting = SessionSettingNumeric(0, 0, 1.0)
_qa_current_tale_id = None

def get_qa_context_menu(tale):
    global _qa_current_tale_id
    if not is_qa():
        return
    _qa_current_tale_id = tale.tale_id
    result = MenuData()
    result.extend(get_objective_chain_context_menu(tale._objective_chain, include_blackboard=True))
    result.AddSeparator()
    result.AddEntry('Open Tale in FSD Editor', func=lambda : _qa_open_tale_in_fsd(tale.template_id))
    result.AddEntry('Tale Details', func=lambda : _qa_tale_details(tale.tale_id))
    start_scene = MenuData()
    start_scene.AddLabel('Available scenes depend on what has been authored, this is listing all scenes.')
    for scene_id, scene_data in sceneTypesByID.iteritems():
        start_scene.AddEntry(scene_data.display, func=lambda scene_id = scene_id: _qa_start_scene(tale.tale_id, scene_id))

    end_scene = MenuData()
    for scene_id in tale.context.get_value('scene_types_by_location', {}).get(session.solarsystemid2, []):
        end_scene.AddEntry(sceneTypesByID[scene_id].display, func=lambda scene_id = scene_id: _qa_end_scene(tale.tale_id, scene_id))

    result.AddEntry('Start Scene in system', subMenuData=start_scene)
    result.AddEntry('End Scene in system', subMenuData=end_scene)
    if tale.context.get_value('influence', None) is not None:
        _qa_set_influence_setting.set(tale.context.get_value('influence', 0))
        _qa_set_influence_setting.on_change.connect(_qa_influence_set)
        influence_data = MenuData()
        influence_data.AddEntry('Details', func=lambda : _qa_tale_influence_details(tale.tale_id))
        influence_data.AddSlider('Set', _qa_set_influence_setting)
        influence_data.AddLabel('Influence data can take some time to update.')
        result.AddEntry('Influence', subMenuData=influence_data)
    result.AddEntry('End Tale', func=lambda : _qa_end_tale(tale.tale_id))
    return result


@threadutils.threaded
def _qa_influence_set(value):
    _qa_tale_influence_set(_qa_current_tale_id, value)
    _qa_set_influence_setting.on_change.disconnect(_qa_influence_set)
    CloseContextMenus()


def _qa_end_tale(tale_id):
    sm.GetService('slash').SlashCmd(u'/tale end {}'.format(tale_id))


def _qa_tale_details(tale_id):
    sm.GetService('slash').SlashCmd(u'/tale detail {}'.format(tale_id))


def _qa_start_scene(tale_id, scene_id):
    sm.GetService('slash').SlashCmd(u'/talescene start {} for {}'.format(scene_id, tale_id))


def _qa_end_scene(tale_id, scene_id):
    sm.GetService('slash').SlashCmd(u'/talescene end {} for {}'.format(scene_id, tale_id))


def _qa_tale_influence_details(tale_id):
    sm.GetService('slash').SlashCmd(u'/influence list taleID={}'.format(tale_id))


def _qa_tale_influence_set(tale_id, value):
    sm.GetService('slash').SlashCmd(u'/influence set {} taleID={}'.format(value, tale_id))


def _qa_open_tale_in_fsd(template_id):
    import webbrowser
    webbrowser.open_new('http://localhost:8000/tales/{}/'.format(template_id))
