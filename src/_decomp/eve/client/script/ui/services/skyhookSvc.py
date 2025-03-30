#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\skyhookSvc.py
from carbon.common.script.sys.service import Service
from spacecomponents.common.components.linkWithShip import LINKSTATE_RUNNING

class SkyhookSvc(Service):
    __guid__ = 'svc.skyhookSvc'
    __servicename__ = 'skyhookSvc'
    __displayname__ = 'Skyhook client service'
    __notifyevents__ = ['OnLinkedWithShipSiloItemUpdated']

    def Run(self, *args):
        super(SkyhookSvc, self).Run(*args)
        self._Initialize()

    def _Initialize(self):
        self.infoPanelSvc = sm.GetService('infoPanel')
        self.onGoingTheft = {}

    def OnLinkedWithShipSiloItemUpdated(self, itemID, solarsystemID, completeAtTime, state, duration):
        if state == LINKSTATE_RUNNING and solarsystemID == session.solarsystemid2:
            startTime = completeAtTime - duration
            self.onGoingTheft[itemID] = (startTime, completeAtTime)
            self.UpdatePanelContainer()
        else:
            self.onGoingTheft.pop(itemID, None)
            if state is None or solarsystemID != session.solarsystemid2:
                self.UpdatePanelContainer()

    def UpdatePanelContainer(self):
        self.infoPanelSvc.UpdateSkyhookTheftPanel()

    def GetOnGoingTheft(self):
        return self.onGoingTheft

    def HasOnGoingTheft(self):
        if len(self.onGoingTheft) > 0:
            return True
        return False
