#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\actions\hauling.py
from collections import deque
from behaviors.tasks import Task
from ccpProfile import TimedFunction

class GetHaulerPickUpDestination(Task):

    @TimedFunction('behaviors::actions::utility::GetHaulerPickUpDestination::OnEnter')
    def OnEnter(self):
        self.SetStatusToFailed()
        chosenBallId, ballsStillPendingPickUp = self._ChooseBallIdForPickUp()
        if chosenBallId is not None:
            self.SendBlackboardValue(self.attributes.chosenBallAddress, chosenBallId)
            self.SetStatusToSuccess()
        self.SendBlackboardValue(self.attributes.availableBallsAddress, ballsStillPendingPickUp)

    def _ChooseBallIdForPickUp(self):
        availableBallIds = self._GetAvailableBallIds()
        if len(availableBallIds) == 0:
            chosenBallId = None
        else:
            chosenBallId = availableBallIds.pop()
        return (chosenBallId, availableBallIds)

    def _GetAvailableBallIds(self):
        availableBallIds = self.GetLastBlackboardValue(self.attributes.availableBallsAddress)
        if availableBallIds is None:
            return deque()
        return availableBallIds


class AddMeToHaulerPickUpDestination(Task):

    @TimedFunction('behaviors::actions::utility::AddMeToHaulerPickUpDestination::OnEnter')
    def OnEnter(self):
        self.SetStatusToSuccess()
        availableBallIds = self._GetAvailableBallIds()
        if self.context.myItemId in availableBallIds:
            return
        availableBallIds.appendleft(self.context.myItemId)
        self.SendBlackboardValue(self.attributes.availableBallsAddress, availableBallIds)

    def _GetAvailableBallIds(self):
        availableBallIds = self.GetLastBlackboardValue(self.attributes.availableBallsAddress)
        if availableBallIds is None:
            return deque()
        return availableBallIds
