#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\dbuffClient.py
from carbon.common.script.sys.service import CoreService
from dbuff.client.incomingDbuffTracker import IncomingDbuffTracker

class DbuffClientService(CoreService):
    __guid__ = 'svc.dbuffClient'
    __notifyevents__ = ['OnFleetBoosted']

    def Run(self, memStream = None):
        self.incomingDbuffTracker = IncomingDbuffTracker()

    def OnFleetBoosted(self, moduleTypeID, numBoosted):
        eve.Message('OnSuccessfulFleetBoost', {'moduleTypeID': moduleTypeID,
         'numBoosted': numBoosted})
