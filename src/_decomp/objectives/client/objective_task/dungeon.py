#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\objectives\client\objective_task\dungeon.py
from ballparkCommon.parkhelpers.warpSubjects import WarpSubjects
from evedungeons.common.instance_identifier import DungeonInstanceIdentifier
from inventorycommon.const import groupWarpGate
from carbonui.uicore import uicore
import carbonui
from evedungeons.client.data import GetDungeon
from evedungeons.client.util import CanEnterDungeonInCurrentShip
from evedungeons.client.ship_restrictions_window import ShipRestrictionsWindow
from eve.common.script.sys.eveCfg import InShipInSpace
from eve.client.script.ui.shared.agencyNew.contentGroups.contentGroupConst import contentGroupCombatAnomalies
import eve.client.script.ui.services.menuSvcExtras.movementFunctions as movement_functions
import localization
import signals
from objectives.client.objective_task.base import ObjectiveTask, ObjectiveTaskGroupWidget
from objectives.client.objective_task.target import TargetTask
from objectives.client.ui.objective_task_widget import TravelStateButtonTaskWidget
from uuid import UUID

class InDungeonTask(ObjectiveTask):
    objective_task_content_id = 12
    WIDGET = None
    BUTTON_WIDGET = TravelStateButtonTaskWidget
    __notifyevents__ = ['OnDungeonEntered', 'OnDungeonExited']

    def __init__(self, dungeon_id = None, bookmark = None, scan_result = None, **kwargs):
        super(InDungeonTask, self).__init__(**kwargs)
        self._dungeon_id = None
        self._bookmark = bookmark
        self._scan_result = scan_result
        self.dungeon_id = dungeon_id

    @property
    def dungeon_id(self):
        return self._dungeon_id

    @dungeon_id.setter
    def dungeon_id(self, value):
        if self._dungeon_id == value:
            return
        self._dungeon_id = value
        self.update()

    @property
    def bookmark(self):
        return self._bookmark

    @bookmark.setter
    def bookmark(self, value):
        if self._bookmark == value:
            return
        self._bookmark = value
        self.update()

    @property
    def scan_result(self):
        return self._scan_result

    @scan_result.setter
    def scan_result(self, value):
        if self._scan_result == value:
            return
        self._scan_result = value
        self.update()

    @property
    def button_action(self):
        return 'warp'

    @property
    def button_target(self):
        if self.scan_result:
            return {'item_id': self.scan_result.targetID}

    def OnDungeonEntered(self, dungeon_id, instance_id):
        if dungeon_id == self.dungeon_id and sm.GetService('space').IsWarping():
            sm.RegisterForNotifyEvent(self, 'OnWarpFinished')
        else:
            self._update_completed_state()

    def OnDungeonExited(self, dungeon_id, instance_id):
        self._update_completed_state()

    def OnWarpFinished(self, *args, **kwargs):
        sm.UnregisterForNotifyEvent(self, 'OnWarpFinished')
        self._update_completed_state()

    def _update(self):
        if not self.dungeon_id:
            return
        self.on_update(objective_task=self)
        self._update_completed_state()

    def _update_completed_state(self):
        current_dungeon = sm.GetService('dungeonTracking').current_dungeon
        if not current_dungeon:
            self.completed = False
        elif self.scan_result and current_dungeon.instance_id and hasattr(self.scan_result, 'instanceID'):
            self.completed = self.scan_result.instanceID == current_dungeon.instance_id
        else:
            self.completed = current_dungeon.dungeon_id == self.dungeon_id

    def double_click(self, *args):
        if self.scan_result:
            self.scan_result.WarpToAction(None, sm.GetService('menu').GetDefaultActionDistance('WarpTo'))
        if self.bookmark:
            return movement_functions.WarpToBookmark(self.bookmark)

    def get_context_menu(self):
        if self.scan_result:
            return sm.GetService('scanSvc').GetScanResultMenuWithoutIgnore(self.scan_result)
        if self.bookmark:
            return sm.GetService('menu').BookmarkMenu(self.bookmark)


class EnterNextDungeonRoom(TargetTask):
    objective_task_content_id = 15
    WIDGET = ObjectiveTaskGroupWidget
    __notifyevents__ = ['OnDungeonEntered', 'OnDungeonExited']

    def __init__(self, gate_id = None, **kwargs):
        self._gate_id = gate_id
        self._current_dungeon = None
        self._event = None
        super(EnterNextDungeonRoom, self).__init__(**kwargs)
        self._restriction_task = ShipRestrictionsTask(task_id='ship_restrictions')
        self.on_group_changed = signals.Signal('on_task_group_changed')

    @property
    def gate_id(self):
        return self._gate_id

    @gate_id.setter
    def gate_id(self, value):
        if self._gate_id == value:
            return
        self._gate_id = value
        self._update_dungeon()

    def get_task_ids(self):
        return ('ship_restrictions', 'enter_dungeon_room')

    def get_total_tasks(self):
        return 2

    def construct_task_widget(self, task_id, *args, **kwargs):
        if task_id == 'enter_dungeon_room':
            return TargetTask.WIDGET(objective_task=self, *args, **kwargs)
        if task_id == 'ship_restrictions':
            return self._restriction_task.WIDGET(objective_task=self._restriction_task, *args, **kwargs)

    def _start(self):
        super(EnterNextDungeonRoom, self)._start()
        self._restriction_task.start()
        self._update_dungeon()

    def _stop(self):
        self._restriction_task.stop()
        self.target = None
        super(EnterNextDungeonRoom, self)._stop()

    def _update_dungeon(self):
        if not self.is_active:
            return
        self.target = None
        self._current_dungeon = sm.GetService('dungeonTracking').current_dungeon
        if not self._current_dungeon:
            return
        self._current_dungeon.on_room_changed.connect(self._room_changed)
        self.target = {'group_id': groupWarpGate,
         'dungeon_object_id': self.gate_id}

    def _slim_item_initialized(self):
        self._restriction_task.gate_id = self.dungeon_object_id

    def _room_changed(self):
        if sm.GetService('space').IsWarping():
            sm.RegisterForNotifyEvent(self, 'OnWarpFinished')
        else:
            self.completed = True

    def OnDungeonEntered(self, dungeon_id, instance_id):
        self._update_dungeon()

    def OnDungeonExited(self, dungeon_id, instance_id):
        if self._current_dungeon:
            self._current_dungeon.on_room_changed.disconnect(self._room_changed)
            self._current_dungeon = None
            self.target = None
        self.completed = False

    def OnWarpFinished(self, *args, **kwargs):
        sm.UnregisterForNotifyEvent(self, 'OnWarpFinished')
        self.completed = True


class EnterCombatAnomaly(ObjectiveTask):
    objective_task_content_id = 29
    __notifyevents__ = ['OnDungeonEntered', 'OnDungeonExited']

    def __init__(self, dungeon_id = None, **kwargs):
        super(EnterCombatAnomaly, self).__init__(**kwargs)
        self._dungeon_id = None
        self.dungeon_id = dungeon_id

    @property
    def dungeon_id(self):
        return self._dungeon_id

    @dungeon_id.setter
    def dungeon_id(self, value):
        if self._dungeon_id == value:
            return
        self._dungeon_id = value
        dungeon_data = GetDungeon(self.dungeon_id)
        self._title = localization.GetByMessageID(dungeon_data.dungeonNameID)
        self.update()

    def OnDungeonEntered(self, dungeon_id, instance_id):
        if dungeon_id == self.dungeon_id:
            if sm.GetService('space').IsWarping():
                sm.RegisterForNotifyEvent(self, 'OnWarpFinished')
            else:
                self.completed = True
        else:
            self.completed = False

    def OnDungeonExited(self, dungeon_id, instance_id):
        if dungeon_id == self.dungeon_id:
            self.completed = False

    def OnWarpFinished(self, *args, **kwargs):
        sm.UnregisterForNotifyEvent(self, 'OnWarpFinished')
        current_dungeon_id = sm.GetService('dungeonTracking').GetCurrentDungeonID()
        self.completed = current_dungeon_id == self.dungeon_id

    def _update(self):
        if not self.dungeon_id:
            return
        current_dungeon_id = sm.GetService('dungeonTracking').GetCurrentDungeonID()
        self.on_update(objective_task=self)
        self.completed = self.dungeon_id == current_dungeon_id

    def _get_valid_anomalies(self):
        anomalies = sm.GetService('sensorSuite').GetAnomalies()
        return [ anomaly for anomaly in anomalies if anomaly.dungeonID == self.dungeon_id ]

    def double_click(self):
        if self.completed:
            return
        if InShipInSpace():
            if self._get_valid_anomalies():
                uicore.cmd.OpenProbeScanner()
                return
        sm.GetService('agencyNew').OpenWindow(contentGroupCombatAnomalies)


class InInstanceDungeonTask(InDungeonTask):
    objective_task_content_id = None
    WIDGET = None
    BUTTON_WIDGET = TravelStateButtonTaskWidget

    def __init__(self, dungeon_id = None, instance_id = None, **kwargs):
        self._instance_id = instance_id
        super(InInstanceDungeonTask, self).__init__(dungeon_id=dungeon_id, **kwargs)

    @property
    def instance_id(self):
        return self._instance_id

    @instance_id.setter
    def instance_id(self, value):
        if self._instance_id == value:
            return
        self._instance_id = value
        self.update()

    @property
    def button_action(self):
        return 'warp'

    @property
    def button_target(self):
        return None

    def _update_completed_state(self):
        current_dungeon = sm.GetService('dungeonTracking').current_dungeon
        if not current_dungeon:
            self.completed = False
        else:
            self.completed = self.instance_id == current_dungeon.instance_id

    def get_context_menu(self):
        return []


class InEscalationSiteTask(InInstanceDungeonTask):
    objective_task_content_id = 36
    WIDGET = None
    BUTTON_WIDGET = TravelStateButtonTaskWidget

    def double_click(self, *args):
        sm.GetService('michelle').CmdWarpToStuff(WarpSubjects.EPIC_INSTANCE, self.instance_id)


class InExternalActivitySiteTask(InInstanceDungeonTask):
    objective_task_content_id = 47
    WIDGET = None
    BUTTON_WIDGET = TravelStateButtonTaskWidget

    def __init__(self, dungeon_id = None, instance_id = None, **kwargs):
        super(InExternalActivitySiteTask, self).__init__(dungeon_id=dungeon_id, instance_id=instance_id, **kwargs)
        self._dungeon_instance_id = DungeonInstanceIdentifier.create_external_activity_instance_id(UUID(hex=instance_id))

    @property
    def instance_id(self):
        return self._dungeon_instance_id

    @instance_id.setter
    def instance_id(self, value):
        new_dungeon_instance_id = DungeonInstanceIdentifier.create_external_activity_instance_id(UUID(hex=value))
        if self._dungeon_instance_id == new_dungeon_instance_id:
            return
        self._dungeon_instance_id = new_dungeon_instance_id
        self.update()

    def double_click(self, *args):
        sm.GetService('michelle').CmdWarpToStuff(WarpSubjects.EXTERNAL_DUNGEON, self._dungeon_instance_id)

    def _update_completed_state(self):
        current_dungeon = sm.GetService('dungeonTracking').current_dungeon
        self.completed = False
        if not current_dungeon or not current_dungeon.instance_id:
            return
        instance_id = current_dungeon.instance_id
        if not isinstance(instance_id, DungeonInstanceIdentifier):
            return
        if not instance_id.is_external_activity:
            return
        if instance_id.external_activity_id == self._dungeon_instance_id.external_activity_id:
            self.completed = True


class ShipRestrictionsTask(ObjectiveTask):
    objective_task_content_id = 39
    __notifyevents__ = ['ProcessActiveShipChanged']

    def __init__(self, dungeon_id = None, gate_id = None, **kwargs):
        super(ShipRestrictionsTask, self).__init__(**kwargs)
        self._dungeon_id = dungeon_id
        self._gate_id = gate_id
        import logging
        logger = logging.getLogger(__name__)
        logger.info('ShipRestrictionsTask %s, %s', self._dungeon_id, self._gate_id)
        if dungeon_id or gate_id:
            self.update()

    @property
    def dungeon_id(self):
        if not self._dungeon_id and self._gate_id:
            return sm.GetService('dungeonTracking').GetCurrentDungeonID()
        return self._dungeon_id

    @dungeon_id.setter
    def dungeon_id(self, value):
        if self._dungeon_id == value:
            return
        self._dungeon_id = value
        self.update()

    @property
    def gate_id(self):
        return self._gate_id

    @gate_id.setter
    def gate_id(self, value):
        if self._gate_id == value:
            return
        self._gate_id = value
        self.update()

    @property
    def icon_color(self):
        return carbonui.TextColor.DANGER

    def ProcessActiveShipChanged(self, *args, **kwargs):
        self.update()

    def _update(self):
        super(ShipRestrictionsTask, self)._update()
        self.completed = CanEnterDungeonInCurrentShip(dungeonID=self.dungeon_id, gateID=self.gate_id)

    def double_click(self, *args):
        ShipRestrictionsWindow.Open(dungeon_id=self.dungeon_id, gate_id=self.gate_id)
