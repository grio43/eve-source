#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\objectives\client\objective_task\location.py
from evePathfinder.core import IsUnreachableJumpCount
from eve.common.script.sys.idCheckers import IsStation, IsDockableStructure
from eve.common.script.sys.eveCfg import InShipInSpace, IsDocked, InStructure, IsAtLocation
import eve.client.script.parklife.states as states
import eve.client.script.ui.services.menuSvcExtras.movementFunctions as movement_functions
import eveformat.client
import localization
from objectives.client.objective_task.base import ObjectiveTask
from objectives.client.ui.objective_task_widget import ProgressBarTaskWidget, TravelToLocationButtonTaskWidget

class TravelToLocationTask(ObjectiveTask):
    objective_task_content_id = 1
    WIDGET = ProgressBarTaskWidget
    BUTTON_WIDGET = TravelToLocationButtonTaskWidget
    __notifyevents__ = ['OnSessionChanged',
     'OnClientEvent_JumpFinished',
     'OnClientEvent_DestinationSet',
     'OnDestinationCleared',
     'OnAutopilotUpdated',
     'OnDestinationSet']

    def __init__(self, location_id = None, **kwargs):
        super(TravelToLocationTask, self).__init__(**kwargs)
        self._location_id = None
        self._location = None
        self._current_jumps = None
        self._current_progress = 0
        self._max_progress = 1
        self._is_dockable_location = False
        self._target_item_id = None
        self.location_id = location_id

    @property
    def location_id(self):
        return self._location_id

    @location_id.setter
    def location_id(self, value):
        if self._location_id == value:
            return
        self._location_id = value
        self._location = cfg.evelocations.Get(self.location_id)
        self._title = u'{} {}'.format(eveformat.solar_system_security_status(self._location.solarSystemID), self._location.locationName)
        self._current_progress = 0
        self._max_progress = 1
        if self._location_id is None:
            self._is_dockable_location = False
        if IsStation(self.location_id):
            self._is_dockable_location = True
        else:
            structure_info = sm.GetService('structureDirectory').GetStructureInfo(self._location_id)
            self._is_dockable_location = structure_info is not None and IsDockableStructure(structure_info.typeID)
        self._target_item_id = None
        self.update()

    @property
    def solar_system_id(self):
        if not self._location:
            return None
        return self._location.solarSystemID

    @property
    def current_jumps(self):
        return self._current_jumps

    def next_travel_action(self):
        if self.completed:
            return
        if self._current_jumps is None:
            return
        if IsDocked() or InStructure():
            return 'undock'
        if self._current_jumps == 0:
            return 'dock'
        return 'jump'

    def OnSessionChanged(self, is_remote, session, change):
        if 'locationid' in change:
            self.update()

    def OnAutopilotUpdated(self):
        if sm.GetService('starmap').GetDestination():
            self._reset_progress()

    def OnDestinationSet(self, destination_id):
        self.update()

    def OnClientEvent_DestinationSet(self, destination_id):
        if destination_id != self.location_id:
            self._reset_progress()

    def OnDestinationCleared(self):
        self._reset_progress()

    def _reset_progress(self):
        self._max_progress = 1
        self.update()

    def OnClientEvent_JumpFinished(self, *args, **kwargs):
        self._update_target_item()

    def _update(self):
        if not self.location_id:
            return
        previous_jumps = self._current_jumps
        if session.solarsystemid2 == self._location.solarSystemID:
            self._current_jumps = 0
        else:
            self._current_jumps = sm.GetService('clientPathfinderService').GetAutopilotJumpCount(session.solarsystemid2, self._location.solarSystemID)
        destination_id = sm.GetService('starmap').GetDestination()
        if IsAtLocation(self.location_id):
            progress = 1.0
        elif destination_id != self.location_id:
            progress = 0.0
        elif IsUnreachableJumpCount(self._current_jumps):
            self._current_jumps = None
            progress = 0.0
        else:
            self._current_progress = float(self._current_jumps or 0)
            if self._is_dockable_location or self._current_jumps == 0:
                self._current_progress += 1
            self._max_progress = max(self._max_progress, self._current_progress)
            progress = 1.0 - min(self._current_progress / self._max_progress, 1.0)
        if self._current_progress != progress or previous_jumps != self._current_jumps:
            self._current_progress = progress
            self.on_update(objective_task=self)
        self.completed = progress == 1.0
        self._update_target_item()

    @property
    def target_item_id(self):
        if not self._target_item_id:
            if self.completed or not InShipInSpace():
                return None
            self._update_target_item()
        return self._target_item_id

    def mouse_down(self, ui_widget):
        target_item_id = self.target_item_id
        if target_item_id:
            sm.GetService('stateSvc').SetState(target_item_id, states.selected, 1)
            sm.GetService('menu').TacticalItemClicked(target_item_id)
            sm.GetService('menu').TryExpandActionMenu(target_item_id, ui_widget)

    def click(self):
        if not InShipInSpace():
            return
        target_item_id = self.target_item_id
        if target_item_id:
            camera = sm.GetService('sceneManager').GetActiveSpaceCamera()
            if camera:
                camera.Track(target_item_id)

    def double_click(self, *args):
        if self.completed:
            return
        if IsDocked():
            sm.GetService('undocking').ExitDockableLocation()
        else:
            target_item_id = self.target_item_id
            if target_item_id:
                movement_functions.DockOrJumpOrActivateGate(target_item_id)

    def _update_target_item(self):
        target_item_id = self._get_target_item_id()
        if self._target_item_id == target_item_id:
            return
        self._target_item_id = target_item_id
        if target_item_id:
            from nodegraph.client.actions.highlights import HighlightSpaceObject
            self.highlight = HighlightSpaceObject(item_id=target_item_id or self.location_id)
        else:
            self.highlight = None

    def _get_target_item_id(self):
        if self.completed or not InShipInSpace():
            return
        if not self._current_jumps:
            return self.location_id
        if sm.GetService('starmap').GetDestination() == self.location_id:
            path = sm.GetService('starmap').GetDestinationPath()
            next_system = path[0] if path else None
        else:
            path = sm.GetService('clientPathfinderService').GetWaypointPath([session.locationid, self.location_id])
            next_system = path[1] if path else None
        ballpark = sm.GetService('michelle').GetBallpark(doWait=True)
        if next_system and ballpark:
            next_object_in_route, _ = sm.GetService('autoPilot').GetGateOrStation(ballpark, next_system, addWarning=False)
            return next_object_in_route

    def get_context_menu(self):
        location = sm.GetService('map').GetItem(self.location_id)
        if location:
            return sm.GetService('menu').GetMenuFromItemIDTypeID(itemID=self.location_id, typeID=location.typeID)

    @property
    def value(self):
        if self.completed or self._current_jumps is None:
            return ''
        if self._current_jumps:
            if IsUnreachableJumpCount(self._current_jumps):
                return localization.GetByLabel('UI/Generic/NoGateToGateRouteShort')
            else:
                return localization.GetByLabel('UI/Common/numberOfJumps', numJumps=self._current_jumps)
        else:
            if self._is_dockable_location and not IsDocked():
                return localization.GetByLabel('UI/Inflight/DockInStation')
            return localization.GetByLabel('UI/Neocom/UndockBtn')

    @property
    def progress(self):
        return self._current_progress


class TravelToCharacterTask(TravelToLocationTask):
    objective_task_content_id = 11

    def __init__(self, character_id = None, **kwargs):
        self._character_id = None
        super(TravelToCharacterTask, self).__init__(**kwargs)
        self.character_id = character_id

    @property
    def character_id(self):
        return self._character_id

    @character_id.setter
    def character_id(self, value):
        if self._character_id == value:
            return
        self._character_id = value
        self.location_id = sm.GetService('agents').GetAgentLocation(self._character_id)
