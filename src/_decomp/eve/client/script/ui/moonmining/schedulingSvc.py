#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\moonmining\schedulingSvc.py
import blue
import carbonui.const as uiconst
import gametime
import inventorycommon.const as invConst
import moonmining.const as extractionConst
from eve.common.lib.appConst import SEC, HOUR, corpRoleStationManager
from carbon.common.script.sys.service import Service
from eveexceptions import UserError

class SchedulingSvc(Service):
    __guid__ = 'svc.scheduling'
    __servicename__ = 'SchedulingSvc'
    __notifyevents__ = ['OnMoonExtractionUpdate']

    def Run(self, memStream = None):
        self.LogInfo('Starting Scheduling Service')
        self.laserFiredTimestamp = None

    def OpenSchedulingWndForStructure(self, structureID):
        eventID, extraction = self.GetExtractionAndEventIDFromStructureID()
        moonMaterialInfo = self.GetMoonResourcesForStructure()
        moonID = self.GetMoonForStructureYourContolling(structureID)
        structureInfo = sm.GetService('structureDirectory').GetStructureInfo(structureID)
        from eve.client.script.ui.moonmining.scheduling import SchedulingWindow
        SchedulingWindow.CloseIfOpen()
        SchedulingWindow(structureID=structureID, moonID=moonID, extraction=extraction, structureOwnerID=structureInfo.ownerID, eventID=eventID)

    def GetExtractionAndEventIDFromStructureID(self):
        extraction, eventID = sm.RemoteSvc('moonExtractions').GetExtractionAndEventIDFromStructureID()
        return (eventID, extraction)

    def GetExtractionsForCorp(self):
        if not session.corprole & corpRoleStationManager:
            eve.Message('CantConfigureCorpStationMgrRoleLacking')
            return []
        return sm.RemoteSvc('moonExtractions').GetExtractionsForCorp()

    def StartMoonminingEvent(self, structureID, structureOwnerID, endtime, addToCalendar):
        now = gametime.GetWallclockTime()
        diff = endtime - now
        durationSeconds = diff / SEC
        if durationSeconds < extractionConst.MINIMUM_EXTRACTION_DURATION:
            raise UserError('MoonminingEventTooShort')
        if endtime > self.GetFuelExpiryTime():
            if eve.Message('NotEnoughFuelForExtractionDuration', {}, uiconst.YESNO) != uiconst.ID_YES:
                return False
        if structureOwnerID != session.corpid or not session.corprole & corpRoleStationManager:
            if eve.Message('ConfirmStartMoonminingEventWithoutRolesToStop', {}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
                return False
        sm.RemoteSvc('moonExtractions').StartNewExtraction(structureID, durationSeconds, addToCalendar)
        return True

    def FireLaser(self):
        self.laserFiredTimestamp = gametime.GetWallclockTime()
        try:
            sm.ScatterEvent('OnMiningLaserFiredLocal')
            sm.GetService('audio').SendUIEvent('moon_mining_fire_at_moon_button_play')
            sm.RemoteSvc('moonExtractions').FractureChunkWithStructure()
        except StandardError:
            self.laserFiredTimestamp = None
            sm.ScatterEvent('OnMiningLaserFiredFailedLocal')
            raise

    def CancelExtraction(self):
        if eve.Message('CancelExtraction', {}, uiconst.YESNO) != uiconst.ID_YES:
            return
        sm.RemoteSvc('moonExtractions').CancelExtraction()

    def GetMoonResourcesForStructure(self):
        moonResources = sm.RemoteSvc('moonExtractions').GetMoonResourcesForStructure()
        return moonResources

    def GetMoonForStructureYourContolling(ballpark, structureID):
        if structureID != session.shipid:
            raise RuntimeError('Trying to get the moon structure without controlling the structure')
        bp = sm.GetService('michelle').GetBallpark()
        if not bp:
            return None
        ball = bp.GetBall(structureID)
        if not ball:
            return None
        structurePosition = (ball.x, ball.y, ball.z)
        from moonmining.miningBeacons import FindMoonBeaconInRangeOfPosition
        closestMoonID = FindMoonBeaconInRangeOfPosition(session.solarsystemid, structurePosition, extractionConst.MAXIMUM_MINING_BEACON_DISTANCE)
        return closestMoonID

    def GetFuelExpiryTime(self):
        from shipfitting.fittingDogmaLocationUtil import GetFuelUsagePerHour
        fuelUsagePerHour = int(GetFuelUsagePerHour(sm.GetService('clientDogmaIM').GetDogmaLocation()))
        timeRemaining = 0
        if fuelUsagePerHour:
            structureInv = sm.GetService('invCache').GetInventoryFromId(session.structureid)
            if structureInv:
                unitsInFuelBay = sum((item.stacksize for item in structureInv.List(invConst.flagStructureFuel) if item.groupID == invConst.groupFuelBlock))
                remaining = min(unitsInFuelBay / fuelUsagePerHour, 876600)
                timeRemaining = remaining * HOUR
        now = blue.os.GetWallclockTime()
        year, month, weekday, day, hour, _, _, _ = blue.os.GetTimeParts(now)
        lastHourTimeStamp = blue.os.GetTimeFromParts(year, month, day, hour, 0, 0, 0)
        fuelExpires = lastHourTimeStamp + timeRemaining
        return fuelExpires

    def OnMoonExtractionUpdate(self, extraction):
        self.laserFiredTimestamp = None

    def GetLaserFiredTimestamp(self):
        return self.laserFiredTimestamp
