#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\shipHud\__init__.py
from eve.client.script.ui.inflight.shipHud.activeShipController import ActiveShipController

def GetSlotOrder():
    defaultOrder = []
    for r in xrange(3):
        for i in xrange(8):
            slotFlag = getattr(const, 'flag%sSlot%s' % (['Hi', 'Med', 'Lo'][r], i), None)
            if slotFlag is not None:
                defaultOrder.append(slotFlag)

    try:
        return settings.user.ui.Get('slotOrder', {}).get(session.shipid, defaultOrder)
    except:
        import log
        LogException()
        sys.exc_clear()
        return defaultOrder
