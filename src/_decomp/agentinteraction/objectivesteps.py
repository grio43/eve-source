#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\agentinteraction\objectivesteps.py
from evePathfinder.core import IsUnreachableJumpCount
from agentinteraction.constUI import PADDING_SMALL
from agentinteraction.objectivestep import ObjectiveStep
from agentinteraction.objectivetests import TEST_OBJECTIVE_SETS
from agentinteraction.textutils import fix_text
import carbonui
from carbonui import const as uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.util.color import Color
from eve.client.script.ui.station.agents.agentDialogueUtil import LocationWrapper
from eve.common.script.sys.idCheckers import IsStation, IsSolarSystem, IsShip
import evelink.client
from evemissions.client.objectives import TalkToAgentObjective, CargoObjective, PickUpObjective, DropOffObjective, DungeonObjective, ObjectivesType
from evetypes import GetCategoryID
from inventorycommon.util import GetPackagedVolume
from localization import GetByLabel
OBJECTIVES_LINE_COLOR = Color.GRAY5
PADDING_BETWEEN_STEPS_BEFORE = 4
PADDING_BETWEEN_STEPS_AFTER = 8
PADDING_AFTER_STEPS = 4

class ObjectiveSteps(ContainerAutoSize):
    __notifyevents__ = ['OnDestinationSet']

    def ApplyAttributes(self, attributes):
        super(ObjectiveSteps, self).ApplyAttributes(attributes)
        self.test_set = attributes.get('test_set', None)
        self._steps = None
        self._objective_type = None
        self.briefing = carbonui.TextBody(name='briefing', parent=self, align=uiconst.TOTOP, padding=(0,
         0,
         0,
         PADDING_SMALL), state=uiconst.UI_NORMAL)
        self.steps_container = ContainerAutoSize(name='steps_container', parent=self, align=uiconst.TOTOP)
        sm.RegisterNotify(self)

    def Close(self):
        sm.UnregisterNotify(self)
        super(ObjectiveSteps, self).Close()

    def OnDestinationSet(self, *args, **kwargs):
        if self._steps:
            self.steps_container.Flush()
            self.update_objective_steps(self._steps, self._objective_type)

    def update_objective_steps(self, steps, objective_type):
        self._steps = steps
        self._objective_type = objective_type
        if self.test_set:
            objective_type = self.test_set
            steps = TEST_OBJECTIVE_SETS[objective_type]
        number_of_steps = len(steps)
        for order, step in enumerate(steps):
            self._add_step(step, objective_type, order, number_of_steps)

    def update_briefing(self, text):
        if text:
            text = fix_text(text)
            self.briefing.SetText(text)
            self.briefing.Show()
        else:
            self.briefing.Hide()

    def _add_step(self, step, objectives_type, order, number_of_steps):
        title = self._get_title(step)
        text = self._get_text(step)
        briefing = self._get_briefing(step, objectives_type)
        location_info = self._get_location_info(step)
        owner_id = self._get_owner_id(step)
        is_last_step = order >= number_of_steps - 1
        if is_last_step:
            bottom_pad = PADDING_AFTER_STEPS
        else:
            bottom_pad = PADDING_BETWEEN_STEPS_AFTER
        if order == 0:
            top_pad = 0
        else:
            top_pad = PADDING_BETWEEN_STEPS_BEFORE
        ObjectiveStep(name='container_step_%s' % step.name, parent=self.steps_container, align=uiconst.TOTOP, title_left=title, title_right=location_info, text=text, step_state=step.state, content_padding_bottom=bottom_pad, content_padding_top=top_pad, owner_id=owner_id, step=step)
        self.update_briefing(briefing)

    def _get_title(self, step):
        if isinstance(step, TalkToAgentObjective):
            return GetByLabel('UI/Agents/StandardMission/AgentLocation')
        if isinstance(step, CargoObjective):
            return GetByLabel('UI/Agents/StandardMission/TransportCargo')
        if isinstance(step, PickUpObjective):
            return GetByLabel('UI/Agents/StandardMission/TransportPickupLocation')
        if isinstance(step, DropOffObjective):
            return GetByLabel('UI/Agents/StandardMission/TransportDropOffLocation')
        if isinstance(step, DungeonObjective):
            return GetByLabel('UI/Agents/StandardMission/ObjectiveLocation')
        return ''

    def _get_text(self, step):
        if isinstance(step, TalkToAgentObjective):
            return LocationWrapper(step.location, 'agenthomebase')
        if isinstance(step, CargoObjective):
            type_id = step.type_id
            category_id = GetCategoryID(type_id)
            quantity = step.quantity
            text = GetByLabel('UI/Common/QuantityAndItem', quantity=quantity, item=type_id)
            if IsShip(category_id):
                volume = GetPackagedVolume(type_id)
                label = 'UI/Agents/StandardMission/CargoDescriptionWithSizePackaged'
            else:
                volume = step.volume
                label = 'UI/Agents/StandardMission/CargoDescriptionWithSize'
            if volume > 0:
                text = GetByLabel(label, cargoDescription=text, size=volume)
            return evelink.type_link(type_id, link_text=text)
        if isinstance(step, PickUpObjective) or isinstance(step, DropOffObjective) or isinstance(step, DungeonObjective):
            return LocationWrapper(step.location)
        return ''

    def _get_briefing(self, step, objectives_type):
        if isinstance(step, TalkToAgentObjective):
            return GetByLabel('UI/Agents/StandardMission/ObjectiveReportTo', agentLink=evelink.owner_link(step.agent_id))
        if isinstance(step, DropOffObjective):
            if objectives_type == ObjectivesType.TRANSPORT:
                return GetByLabel('UI/Agents/StandardMission/TransportBlurb')
            if objectives_type == ObjectivesType.FETCH:
                return GetByLabel('UI/Agents/StandardMission/FetchObjectiveBlurb')
        if isinstance(step, DungeonObjective):
            if step.briefing is not None:
                return step.briefing
            if step.is_killing_optional:
                return GetByLabel('UI/Agents/StandardMission/OptionalObjectiveBody')
            return GetByLabel('UI/Agents/StandardMission/DungeonObjectiveBody')
        return ''

    def _get_location_info(self, step):
        location_info = ''
        location = getattr(step, 'location', None)
        if location:
            location_id = location['locationID']
            solar_system_id = location['solarsystemID']
            current_solar_system_id = session.solarsystemid2
            current_station = session.stationid
            jumps = sm.GetService('clientPathfinderService').GetAutopilotJumpCount(session.solarsystemid2, solar_system_id)
            if IsStation(location_id):
                if current_station == location_id:
                    return GetByLabel('UI/Agents/StandardMission/ThisStation')
                location_id = solar_system_id
            if IsSolarSystem(location_id):
                if current_solar_system_id == location_id:
                    return GetByLabel('UI/Agents/StandardMission/ThisSolarSystem')
                elif IsUnreachableJumpCount(jumps):
                    return GetByLabel('UI/Generic/NoGateToGateRoute')
                else:
                    return GetByLabel('UI/Agents/StandardMission/JumpsAway', jumps=jumps)
        return location_info

    def _get_owner_id(self, step):
        if isinstance(step, TalkToAgentObjective):
            return step.agent_id
