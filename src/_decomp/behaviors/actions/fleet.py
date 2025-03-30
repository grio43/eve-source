#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\actions\fleet.py
import logging
from ballpark.const import DESTINY_MODE_WARP
from ballpark.messenger.const import MESSAGE_ON_BALL_MODE_CHANGED
from ballpark.warpFormations import FormationPicker
from behaviors.groups.mixin import GroupTaskMixin
from behaviors.tasks import BlockingTask
from behaviors.tasks import Task
from eve.common.script.sys.idCheckers import IsEvePlayerCharacter
logger = logging.getLogger(__name__)

class FormationWarpGroup(Task, GroupTaskMixin):

    def OnEnter(self):
        self.SetStatusToFailed()
        formation_picker = self.get_formation_picker()
        formation_destination_coordinates = formation_picker.GetDestinationVectors()
        jitter_radius = formation_picker.GetJitterRadius()
        min_range = formation_picker.GetMinimumRange()
        warp_speed = formation_picker.GetMinWarpSpeed()
        for ship_id, char_id in formation_picker.GetFleetCandidates():
            destination_coordinate = formation_destination_coordinates[ship_id]
            if char_id:
                if self.context.ballpark.CancelIfDoingStuff(ship_id):
                    logger.error('char %s in ship %s unable to do warp due to CancelIfDoingStuff', char_id, ship_id)
                    continue
                self.warp_player(ship_id, destination_coordinate, jitter_radius, min_range, warp_speed)
            else:
                self.warp_npc(ship_id, destination_coordinate, jitter_radius, min_range, warp_speed)

        self.SetStatusToSuccess()

    def warp_player(self, ship_id, destination_coordinate, jitter_radius, min_range, warp_speed):
        logger.info('fleet warp player: ship_id=%s destination_coordinate=%s jitter_radius=%s min_range=%s warp_speed=%s', ship_id, destination_coordinate, jitter_radius, min_range, warp_speed)
        if self.context.ballpark.CancelIfDoingStuff(ship_id):
            logger.warning('%s unable to do warp due to CancelIfDoingStuff', ship_id)
            return
        self.context.ballpark.WarpTo(ship_id, destination_coordinate, minRange=min_range, cheatWarp=False, warpSpeed=warp_speed, jitterRadius=jitter_radius)

    def warp_npc(self, ship_id, destination_coordinate, jitter_radius, min_range, warp_speed):
        logger.info('fleet warp npc: ship_id=%s destination_coordinate=%s jitter_radius=%s min_range=%s warp_speed=%s', ship_id, destination_coordinate, jitter_radius, min_range, warp_speed)
        ball = self.context.ballpark.balls.get(ship_id)
        if ball is None:
            logger.warning('Item %s was not found in ballpark', ship_id)
            return
        if not hasattr(ball, 'NPCWarpTo'):
            logger.warning("Item %s does not support 'NPCWarpTo' in order that a behavior fleet warp", ship_id)
            return
        try:
            ball.NPCWarpTo(destination_coordinate, jitterRadius=jitter_radius, warpAtRange=min_range, warpSpeed=warp_speed)
        except Exception as e:
            logger.exception('item %s failed to warp' % ship_id)

    def get_formation_picker(self):
        destination_coordinates = self.GetLastBlackboardValue(self.attributes.destinationCoordinatesAddress)
        jump_candidates = self.get_fleet_warp_candidates()
        fleet_formation_settings = self.get_formation_settings()
        formation_picker = FormationPicker(self.context.ballpark, jump_candidates[0][0], None, destination_coordinates, jump_candidates, 0.0, None, fleet_formation_settings, applySkills=False)
        formation_picker.validateFormation = lambda *args: None
        return formation_picker

    def get_formation_settings(self):
        return {'formationType': self.attributes.formationType,
         'formationSpacing': self.attributes.formationSpacing,
         'formationSize': self.attributes.formationSize}

    def get_fleet_warp_candidates(self):
        fleet_warp_candidates = {member_id:None for member_id in self.GetMemberIdList()}
        self.add_additional_fleet_members(fleet_warp_candidates)
        return fleet_warp_candidates.items()

    def add_additional_fleet_members(self, fleet_warp_candidates):
        additional_candidates = self.GetLastBlackboardValue(self.attributes.additionalFleetMembersAddress)
        if additional_candidates:
            for member_id in additional_candidates:
                if member_id in fleet_warp_candidates:
                    continue
                char_id = None
                slimitem = self.context.ballpark.slims.get(member_id)
                if slimitem is None:
                    continue
                if IsEvePlayerCharacter(slimitem.ownerID):
                    char_id = slimitem.ownerID
                fleet_warp_candidates[member_id] = char_id


class AlignFleet(Task, GroupTaskMixin):

    def OnEnter(self):
        self.SetStatusToFailed()
        candidates = self.get_fleet_candidates()
        destination_coordinates = self.GetLastBlackboardValue(self.attributes.destinationCoordinatesAddress)
        ballpark = self.context.ballpark
        for member_id in candidates:
            try:
                ballpark.GotoPoint(member_id, *destination_coordinates)
                ballpark.SetSpeedFraction(member_id, 1.0)
            except Exception as e:
                logger.exception('Failure while trying to align object %s', member_id)

        self.SetStatusToSuccess()

    def get_fleet_candidates(self):
        fleet_warp_candidates = [ member_id for member_id in self.GetMemberIdList() ]
        self.add_additional_fleet_members(fleet_warp_candidates)
        return fleet_warp_candidates

    def add_additional_fleet_members(self, fleet_warp_candidates):
        additional_candidates = self.GetLastBlackboardValue(self.attributes.additionalFleetMembersAddress)
        if not additional_candidates:
            return
        for member_id in additional_candidates:
            if member_id not in self.context.ballpark.slims:
                continue
            fleet_warp_candidates.append(member_id)


class BlockWaitUntilWarpComplete(BlockingTask):

    def OnEnter(self):
        super(BlockWaitUntilWarpComplete, self).OnEnter()
        self.SubscribeItem(self.context.myItemId, MESSAGE_ON_BALL_MODE_CHANGED, self._destiny_mode_change)
        self.SetStatusToSuspended()

    def _destiny_mode_change(self, old_mode, new_mode):
        if old_mode == DESTINY_MODE_WARP and self.context.ballpark is not None:
            self.UnsubscribeItem(self.context.myItemId, MESSAGE_ON_BALL_MODE_CHANGED, self._destiny_mode_change)
            self.SetStatusToSuccess()
            self.OnStatusUpdate()

    def CleanUp(self):
        if not self.IsInvalid():
            self.UnsubscribeItem(self.context.myItemId, MESSAGE_ON_BALL_MODE_CHANGED, self._destiny_mode_change)
            self.SetStatusToInvalid()


class WaitUntilWarpComplete(Task):

    def OnEnter(self):
        super(WaitUntilWarpComplete, self).OnEnter()
        self.SubscribeItem(self.context.myItemId, MESSAGE_ON_BALL_MODE_CHANGED, self._destiny_mode_change)
        self.SetStatusToBlocked()

    def _destiny_mode_change(self, old_mode, new_mode):
        if old_mode == DESTINY_MODE_WARP and self.context.ballpark is not None:
            self.UnsubscribeItem(self.context.myItemId, MESSAGE_ON_BALL_MODE_CHANGED, self._destiny_mode_change)
            self.SetStatusToSuccess()
            self.behaviorTree.StartTaskNextTick(self)

    def CleanUp(self):
        if not self.IsInvalid():
            self.UnsubscribeItem(self.context.myItemId, MESSAGE_ON_BALL_MODE_CHANGED, self._destiny_mode_change)
            self.SetStatusToInvalid()
