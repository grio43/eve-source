#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evemissions\client\qa_tools.py
from __future__ import absolute_import
import blue
import carbon.common.script.sys.serviceConst as serviceConst
from carbonui.control.contextMenu.menuData import MenuData
from objectives.client.qa_tools import key_value_entry

def get_agent_mission_context_menu(mission_content_id, agent_id, objective_chain = None, group = 'QA'):
    result = MenuData()
    if not session.role & (serviceConst.ROLE_EXT_GM1_PLUS | serviceConst.ROLE_CONTENT):
        return result
    elif not agent_id:
        return result
    result.AddEntry('Agent', subMenuData=_get_agent_context_menu(agent_id, mission_content_id))
    if mission_content_id:
        result.AddEntry('Mission', subMenuData=_get_agent_mission_context_menu(mission_content_id, agent_id, objective_chain))
    if group:
        data = MenuData()
        data.AddEntry(group, subMenuData=result)
        return data
    else:
        return result


def _get_agent_context_menu(agent_id, mission_content_id):
    slash_command = sm.GetService('slash')
    result = MenuData()
    result.AddEntry(text=u'agent_id={}'.format(agent_id), func=lambda *args: blue.pyos.SetClipboardData(unicode(agent_id)))
    result.AddEntry(text='Open Agent in FSD Editor', func=lambda : _open_fsd_agent(agent_id))
    result.AddSeparator()
    result.AddEntry(text=u'Cheat: Toggle {} completed objectives cheat'.format('OFF' if sm.GetService('agents').IsCheatingWithAgent(agent_id) else 'ON'), func=lambda *args: slash_command.SlashCmd('agent %s cheat' % agent_id))
    result.AddEntry(text=u'Cheat: Toggle {} replayability cheat for next mission'.format('OFF' if sm.GetService('agents').ShouldAlwaysAllowReplay(agent_id) else 'ON'), func=lambda *args: slash_command.SlashCmd('agent %s replay' % agent_id))
    result.AddEntry(text='Reset standings', func=lambda *args: _clear_standings(agent_id))
    result.AddEntry(text='Maximize standings', func=lambda *args: _max_standings(agent_id))
    result.AddEntry(text='Clear memory', func=lambda *args: _slash_and_open('agent %s reset' % agent_id, agent_id))
    result.AddEntry(text='Select a mission', func=lambda *args: _select_mission(agent_id))
    if mission_content_id:
        result.AddEntry(text='Reset mission', func=lambda *args: _slash_and_open('agent %s offer %s' % (agent_id, mission_content_id), agent_id))
    return result


def _get_agent_mission_context_menu(mission_content_id, agent_id, objective_chain = None):
    result = MenuData()
    result.AddEntry(text=u'mission_id={}'.format(mission_content_id), func=lambda *args: blue.pyos.SetClipboardData(unicode(mission_content_id)))
    result.AddEntry(text='Open Mission in FSD Editor', func=lambda : _open_fsd_agent_mission(mission_content_id))
    result.AddSeparator()
    agent_mission = sm.GetService('missionObjectivesTracker').agentMissions.get(agent_id)
    if agent_mission:
        if agent_mission.node_graph:
            result.AddEntry(text='Open Mission Node Graph', func=lambda : _open_active_node_graph(agent_mission.node_graph.instance_id))
        result.AddSeparator()
        if agent_mission.objective_chain:
            result.entrylist.extend(agent_mission.objective_chain.get_context_menu())
            result.AddSeparator()
        result.entrylist.append(key_value_entry('Blackboard Values', agent_mission.context.values, agent_mission.context))
    elif objective_chain:
        result.AddSeparator()
        result.entrylist.extend(objective_chain.get_context_menu())
        result.entrylist.append(key_value_entry('Blackboard Values', objective_chain.context.values, objective_chain.context))
    return result


def _clear_standings(agent_id):
    agent = sm.GetService('agents').GetAgentByID(agent_id)
    slashCmdSvc = sm.GetService('slash')
    slashCmdSvc.SlashCmd('setstanding %s me 0.0' % agent_id)
    slashCmdSvc.SlashCmd('setstanding %s me 0.0' % agent.corporationID)
    slashCmdSvc.SlashCmd('setstanding %s me 0.0' % agent.factionID)


def _max_standings(agent_id):
    agent = sm.GetService('agents').GetAgentByID(agent_id)
    slashCmdSvc = sm.GetService('slash')
    slashCmdSvc.SlashCmd('setstanding %s me 10.0' % agent_id)
    slashCmdSvc.SlashCmd('setstanding %s me 10.0' % agent.corporationID)
    slashCmdSvc.SlashCmd('setstanding %s me 10.0' % agent.factionID)


def _select_mission(agent_id):
    mission_ids = sm.RemoteSvc('agentMgr').GetPlausibleMissionIDs(agent_id)
    if not mission_ids:
        return
    from evemissions.client.data import get_mission
    from eve.client.script.ui.util import uix
    from localization import GetByMessageID
    entry_list = []
    for mission_id in mission_ids:
        mission = get_mission(mission_id)
        entry_list.append((u'{} ({})'.format(GetByMessageID(mission.nameID), mission_id), mission_id))

    result = uix.ListWnd(sorted(entry_list), listtype='generic', caption='Select a mission')
    if result:
        _slash_and_open('agent %s offer %s' % (agent_id, result[1]), agent_id)


def _slash_and_open(slash_command, agent_id):
    sm.GetService('slash').SlashCmd(slash_command)
    sm.GetService('agents').OpenDialogueWindow(agent_id)


def _open_fsd_agent(agent_id):
    import webbrowser
    webbrowser.open_new('http://localhost:8000/npccharacters/{}/'.format(agent_id))


def _open_fsd_agent_mission(content_id):
    import webbrowser
    webbrowser.open_new('http://localhost:8000/missions/missions/{}/'.format(content_id))


def _open_active_node_graph(node_graph_instance_id):
    from nodegraph.client.ui.window import NodeGraphEditorWindow
    NodeGraphEditorWindow.Open(node_graph_id=node_graph_instance_id)
