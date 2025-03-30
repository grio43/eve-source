#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\svc_fittingspawner.py
from collections import defaultdict
import blue
import dynamicitemattributes
import evetypes
from carbon.common.script.sys.service import Service
from eve.client.script.ui.shared.fittingScreen.fittingWnd import FittingWindow
from eve.client.script.ui.util import uix
from eveexceptions import UserError
from inventorycommon.util import IsSubsystemFlag

class FittingSpawner(Service):
    __guid__ = 'svc.fittingspawner'
    __startupdependencies__ = ['invCache',
     'loading',
     'gameui',
     'station']

    def MassSpawnFitting(self, ownerID, fitting):
        quantity = uix.QtyPopup(maxvalue=50, minvalue=1, caption='Mass Spawn Fitting', label='', hint='Specify amount of ships to spawn (Max. 50).<br>Note: this function cannot be aborted once running.')
        self.SpawnFitting(ownerID, fitting, quantity['qty'])

    def SpawnFitting(self, ownerID, fitting, quantity = 1):
        self.fittingSvc = sm.GetService('fittingSvc')
        if session.stationid is None and session.structureid is None:
            raise UserError('CannotLoadFittingInSpace')
        if session.structureid and session.shipid == session.structureid:
            raise UserError('CannotLoadFittingInSpace')
        if fitting is None:
            raise UserError('FittingDoesNotExist')
        wnd = FittingWindow.GetIfOpen()
        wasOpen = False
        if wnd:
            wasOpen = True
            wnd.Close()
        cleanFitting = fitting.copy()
        cleanFitData = []
        removedItems = defaultdict(int)
        for typeID, flag, qty in fitting.fitData:
            if dynamicitemattributes.IsDynamicType(typeID):
                removedItems[typeID] += 1
                continue
            cleanFitData.append((typeID, flag, qty))

        cleanFitting.fitData = cleanFitData
        try:
            subsystems = []
            for i, (typeID, flag, qty) in enumerate(cleanFitting.fitData):
                self.loading.ProgressWnd('Preparing ship', 'MAking items...', i, len(cleanFitting.fitData))
                itemID = sm.RemoteSvc('slash').SlashCmd('/createitem %d %d' % (typeID, qty * quantity))
                if IsSubsystemFlag(flag):
                    subsystems.append(itemID)

            self.loading.StopCycle()
            for i in xrange(quantity):
                self.loading.ProgressWnd('Preparing ship', 'Fitting ship', 1, 2)
                shipID = sm.RemoteSvc('slash').SlashCmd('/createitem %d 1' % cleanFitting.shipTypeID)
                self.gameui.GetShipAccess().AssembleShip(shipID, cleanFitting.name, subSystems=subsystems)
                shipItem = self.invCache.GetInventoryFromId(shipID).GetItem()
                self.station.TryActivateShip(shipItem)
                blue.pyos.synchro.SleepWallclock(500)
                self.fittingSvc.LoadFitting(cleanFitting)

        finally:
            self.loading.StopCycle()
            if wasOpen:
                self.fittingSvc.SetSimulationState(False)
                FittingWindow.Open()

        if removedItems:
            infoTextList = ['Removed the following modules from the fit:']
            for eachTypeID, qty in removedItems.iteritems():
                t = '<a href="showinfo:%s">%s</a> : %sx' % (eachTypeID, evetypes.GetName(eachTypeID), qty)
                infoTextList.append(t)

            infoText = '<br>'.join(infoTextList)
            eve.Message('CustomInfo', {'info': infoText}, modal=False)
