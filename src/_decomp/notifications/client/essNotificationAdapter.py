#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\client\essNotificationAdapter.py
import eve.common.script.util.notificationconst as notificationConst
from uthread2.callthrottlers import BufferedCall
from dynamicresources.common.ess.const import UNLINKED_MANUAL

class ESSNotificationAdapter(object):
    __notifyevents__ = ['OnESSMainBankLinkNotification',
     'OnMainBankPlayerLinkDisconnected',
     'OnReserveBankUnlock',
     'OnEssReserveBankInventoryFull']

    def __init__(self):
        self.onCooldown = False

    @BufferedCall(30000)
    def beginCooldown(self):
        self.onCooldown = False

    def OnESSMainBankLinkNotification(self, solarSystemID):
        if not self.onCooldown:
            sm.GetService('notificationSvc').MakeAndScatterNotification(notificationConst.notificationTypeEssMainBankLink, data={'solarSystemID': solarSystemID})
        self.onCooldown = True
        self.beginCooldown()

    def OnMainBankPlayerLinkDisconnected(self, data):
        if data.get('reason', None) is not UNLINKED_MANUAL:
            system = data['solarSystemID']
            characterID = data['characterID']
            sm.GetService('notificationSvc').MakeAndScatterNotification(notificationConst.notificationTypeEssLinkDisconnected, data={'solarSystemID': system,
             'characterID': characterID})

    def OnReserveBankUnlock(self, data):
        regionID = data['regionID']
        if session.regionid == regionID:
            sm.GetService('notificationSvc').MakeAndScatterNotification(notificationConst.notificationTypeEssReserveBankUnlocked, data={})

    def OnEssReserveBankInventoryFull(self):
        sm.GetService('notificationSvc').MakeAndScatterNotification(notificationConst.notificationTypeEssInventoryFull, data={})
