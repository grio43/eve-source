#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\dungeonTracking.py
import localization
import signals
from carbon.common.script.sys.service import Service
from eve.common.script.sys.rowset import Rowset
from eve.common.script.sys.eveCfg import IsDocked
from evedungeons.client.anomalyTracker import CombatAnomalyTracker, FactionalWarfareSiteTracker, HomefrontOperationTracker, IceBeltTracker, OreAnomalyTracker, PirateInsurgencySiteTracker, TriglavianSiteTracker
from evedungeons.client.data import GetDungeon, GetDungeonObjectivesData
from logging import getLogger
from nodegraph.common.nodedata import is_client_graph
from objectives.client.objective_chain import ObjectiveChain
from objectives.common.objective_context import ObjectivesContext, get_authored_parameter_values_as_dict
logger = getLogger(__name__)

class DungeonTracking(Service):
    __guid__ = 'svc.dungeonTracking'
    __notifyevents__ = ['ProcessSessionChange',
     'OnCharacterSessionChanged',
     'OnDistributionDungeonEntered',
     'OnEscalatingPathDungeonEntered',
     'OnEnteringDungeonRoom',
     'OnExitingDungeon',
     'OnDungeonMessage',
     'OnDungeonValues',
     'OnDungeonCompleted']

    def __init__(self):
        super(DungeonTracking, self).__init__()
        self.distributionDungeonsEntered = None
        self.escalatingPathDungeonsEntered = None
        self.trackers = {'combat_anomalies': CombatAnomalyTracker(),
         'factional_warfare': FactionalWarfareSiteTracker(),
         'homefront_operations': HomefrontOperationTracker(),
         'ice_belts': IceBeltTracker(),
         'ore_anomalies': OreAnomalyTracker(),
         'pirate_insurgency': PirateInsurgencySiteTracker(),
         'triglavian': TriglavianSiteTracker()}
        self.current_dungeon = None

    def Run(self, memStream = None):
        super(DungeonTracking, self).Run(memStream)
        for tracker in self.trackers.values():
            tracker.initialize()

    def ProcessSessionChange(self, isRemote, session, change):
        if 'locationid' in change:
            self.distributionDungeonsEntered = None
            self.escalatingPathDungeonsEntered = None
            self._clear_dungeon()

    def OnCharacterSessionChanged(self, oldCharacterID, newCharacterID):
        if not newCharacterID or IsDocked():
            return
        dungeon_info = sm.RemoteSvc('keeper').GetCurrentDungeonForCharacter()
        if dungeon_info:
            dungeon_id, room_id, instance_id, dungeon_values = dungeon_info
            self.OnEnteringDungeonRoom(dungeon_id=dungeon_id, room_id=room_id, room_position=None, instance_id=instance_id, dungeon_values=dungeon_values)

    def OnDistributionDungeonEntered(self, row):
        if self.distributionDungeonsEntered is None:
            self.distributionDungeonsEntered = Rowset(row.header)
        self.distributionDungeonsEntered.append(row)

    def OnEscalatingPathDungeonEntered(self, row):
        if self.escalatingPathDungeonsEntered is None:
            self.escalatingPathDungeonsEntered = Rowset(row.header)
        if getattr(row, 'dungeonNameID', None):
            row.name = localization.GetByMessageID(row.dungeonNameID)
        self.escalatingPathDungeonsEntered.append(row)

    def GetDistributionDungeonsEntered(self):
        return self.distributionDungeonsEntered

    def GetEscalatingPathDungeonsEntered(self):
        return self.escalatingPathDungeonsEntered

    def GetCurrentDungeonID(self):
        if self.current_dungeon:
            return self.current_dungeon.dungeon_id
        else:
            return None

    def OnEnteringDungeonRoom(self, dungeon_id, room_id, room_position, instance_id, dungeon_values):
        if not self.current_dungeon or self.current_dungeon.dungeon_id != dungeon_id:
            logger.info('Dungeon Entered - dungeon_id: %s - room_id: %s - instance_id: %s - values: %s', dungeon_id, room_id, instance_id, dungeon_values)
            self.current_dungeon = ActiveDungeon(dungeon_id, room_id, instance_id, dungeon_values)
            self.current_dungeon.start()
            sm.ScatterEvent('OnDungeonEntered', dungeon_id, instance_id)
        else:
            self.current_dungeon.room_id = room_id

    def OnExitingDungeon(self, dungeon_id):
        self._clear_dungeon(dungeon_id)

    def OnDungeonMessage(self, dungeon_id, message_key, message_value):
        if self.current_dungeon and self.current_dungeon.dungeon_id == dungeon_id:
            self.current_dungeon.message(message_key, message_value)

    def OnDungeonValues(self, dungeon_id, values):
        logger.info('Dungeon Values received - current_dungeon_id: %s - dungeon_id: %s - values: %s', self.GetCurrentDungeonID(), dungeon_id, values)
        if self.current_dungeon and self.current_dungeon.dungeon_id == dungeon_id:
            self.current_dungeon.update_dungeon_values(values)
            for key, value in values.iteritems():
                self.current_dungeon.update_context_value(key, value)

    def OnDungeonCompleted(self, dungeon_id):
        if self.current_dungeon and self.current_dungeon.dungeon_id == dungeon_id:
            self.current_dungeon.update_context_value('dungeon_completed', True)

    def _clear_dungeon(self, dungeon_id = None):
        if not self.current_dungeon:
            return
        if not dungeon_id or self.current_dungeon.dungeon_id == dungeon_id:
            instance_id = self.current_dungeon.instance_id
            self.current_dungeon.stop()
            self.current_dungeon = None
            sm.ScatterEvent('OnDungeonExited', dungeon_id, instance_id)

    def get_tracker(self, tracker_id):
        return self.trackers[tracker_id]


class ActiveDungeon(object):

    def __init__(self, dungeon_id, room_id, instance_id, dungeon_values):
        self._context = ObjectivesContext()
        self._context.set_values(dungeon_id=dungeon_id, dungeon_room_id=room_id)
        self.update_dungeon_values(dungeon_values or {})
        self._mission = None
        self._node_graph = None
        self._objective_chain = None
        self._instance_id = instance_id
        self.on_room_changed = signals.Signal('on_room_changed')

    def message(self, key, value):
        if not key.startswith('dungeon_'):
            key = u'dungeon_{}'.format(key)
        self._context.send_message(key, value=value)

    def update_dungeon_values(self, values):
        for key, value in values.iteritems():
            keys = key.split('.')
            self._context.update_value(keys[0], value, object_path=keys[1:])

    def update_context_value(self, key, value):
        self._context.update_value(key, value)

    @property
    def objective_chain(self):
        return self._objective_chain

    @property
    def dungeon_id(self):
        return self._context.get_value('dungeon_id')

    @property
    def instance_id(self):
        return self._instance_id

    @property
    def room_id(self):
        return self._context.get_value('dungeon_room_id')

    @room_id.setter
    def room_id(self, value):
        if self.room_id == value:
            return
        self.update_context_value('dungeon_room_id', value)
        self.on_room_changed()

    @property
    def data(self):
        return GetDungeon(self.dungeon_id)

    @property
    def title(self):
        return localization.GetByMessageID(self.data.dungeonNameID)

    @property
    def description(self):
        return localization.GetByMessageID(self.data.descriptionID)

    @property
    def archetype_id(self):
        return self.data.archetypeID

    @property
    def faction_id(self):
        return self.data.factionID

    @property
    def difficulty(self):
        return self.data.factionID

    @property
    def mission_briefing_id(self):
        return self.data.missionBriefingID

    @property
    def entry_type_id(self):
        return self.data.entryTypeID

    @property
    def standing_restrictions(self):
        return self.data.standingRestrictions

    @property
    def objectives_data(self):
        return GetDungeonObjectivesData(self.dungeon_id)

    def start(self):
        sm.RegisterForNotifyEvent(self, 'OnExpandedMissionChanged')
        self.OnExpandedMissionChanged(**sm.GetService('infoPanel').GetExpandedMission())
        dungeon_objectives = self.objectives_data
        if dungeon_objectives:
            self._context.set_values(**get_authored_parameter_values_as_dict(dungeon_objectives.blackboardParameters))
            self._start_objective_chain(dungeon_objectives.objectiveChainID, dungeon_objectives.overrides)
            self._start_node_graph(dungeon_objectives.nodeGraphID)

    def stop(self):
        sm.UnregisterForNotifyEvent(self, 'OnExpandedMissionChanged')
        self.update_context_value('dungeon_room_id', None)
        self._stop_node_graph()
        if self._mission:
            self._mission = None
        if self._objective_chain:
            self._objective_chain.stop()
            self._objective_chain = None
        self._context.clear()

    def _start_objective_chain(self, objective_chain_id, overrides):
        if not objective_chain_id:
            return
        self._objective_chain = ObjectiveChain(content_id=objective_chain_id, context=self._context, overrides=overrides)
        self._objective_chain.start()

    def _start_node_graph(self, node_graph_id):
        if not node_graph_id or self._node_graph:
            return
        if is_client_graph(node_graph_id):
            self._node_graph = sm.GetService('node_graph').start_node_graph(node_graph_id=node_graph_id, context=self._context)

    def get_context_menu(self):
        from carbonui.control.contextMenu.menuData import MenuData
        from objectives.client.qa_tools import is_qa, key_value_entry
        data = MenuData()
        if not is_qa():
            return data
        result = MenuData()
        dungeon_objectives_id = GetDungeon(self.dungeon_id).objectivesID
        if dungeon_objectives_id:
            result.AddEntry(text='Open Dungeon Objectives in FSD Editor', func=lambda : _open_fsd_dungeon_objectives(dungeon_objectives_id))
        if self._node_graph:
            result.AddEntry(text='Open Dungeon Node Graph', func=lambda : _open_active_node_graph(self._node_graph.instance_id))
        result.AddSeparator()
        if self.objective_chain:
            result.entrylist.extend(self.objective_chain.get_context_menu())
        result.entrylist.append(key_value_entry('Blackboard Values', self._context.values, self._context))
        data.AddEntry('QA', subMenuData=result)
        return data

    def OnExpandedMissionChanged(self, featureID = None, missionID = None):
        is_focused = False
        if featureID == 'opportunities' and missionID and missionID != -1:
            provider_id, instance_id = missionID.split(':')
            if instance_id == str(self.instance_id) and _is_dungeon_provider(provider_id):
                is_focused = True
        self._context.update_value('mission_focused', is_focused)

    def _stop_node_graph(self):
        if self._node_graph:
            sm.GetService('node_graph').stop_node_graph(self._node_graph.instance_id)
            self._node_graph = None


def _is_dungeon_provider(provider_id):
    from jobboard.client.provider_type import DUNGEON_PROVIDERS
    return provider_id in DUNGEON_PROVIDERS


def _open_fsd_dungeon_objectives(content_id):
    import webbrowser
    webbrowser.open_new('http://localhost:8000/dungeons/dungeon_objectives/{}/'.format(content_id))


def _open_active_node_graph(node_graph_instance_id):
    from nodegraph.client.ui.window import NodeGraphEditorWindow
    NodeGraphEditorWindow.Open(node_graph_id=node_graph_instance_id)
