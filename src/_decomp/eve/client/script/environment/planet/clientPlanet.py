#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\planet\clientPlanet.py
import sys
import blue
import bluepy
import geo2
import utillib
import uthread
import evetypes
from carbon.common.script.util.format import FmtTimeInterval
from carbonui import uiconst
from eve.client.script.environment.planet.clientColony import ClientColony
from eve.client.script.ui.util import uix
from eve.common.lib import appConst as const
from eve.common.lib.PlanetResources import builder
from eve.common.script.net import eveMoniker
from eve.common.script.planet import commandStream
from eve.common.script.planet.basePlanet import BasePlanet
from eve.common.script.planet.colonyData import ColonyData
from eve.common.script.sys.idCheckers import IsKnownSpaceSystem
from eve.common.script.util import planetCommon
from eveexceptions import UserError
from localization import GetByLabel
from menucheckers import SessionChecker
CP_COMMANDPINREMOVED = -1
CP_NOCHANGE = 0
CP_COMMANDPINADDED = 1

class ClientPlanet(BasePlanet):
    __name__ = 'ClientPlanet'

    def Init(self):
        BasePlanet.Init(self)
        self.ticking = False
        self.tickThread = None
        self.remoteHandler = eveMoniker.GetPlanet(self.planetID)
        self.PreparePlanet()
        self.changes = commandStream.CommandStream()
        self.commandPinChange = CP_NOCHANGE
        self.backupData = None
        self.enteredEditModeTime = None
        self.isInEditMode = False

    def GetPlanetTypeID(self):
        if self.planetTypeID is None:
            planetData = sm.GetService('mapsvc').GetPlanetInfo(self.planetID)
            self.planetTypeID = planetData.typeID
        return self.planetTypeID

    def GetNewColony(self, ownerID):
        return ClientColony(self, ownerID)

    def GetCommandCenterForCharacter(self, characterID):
        colony = self.GetColony(characterID)
        if colony is None or colony.colonyData is None:
            return
        return colony.colonyData.commandPin

    def _PrimeColony(self, ownerID, serializedColony):
        if ownerID not in self.colonies:
            self.colonies[ownerID] = colony = self.GetNewColony(ownerID)
        else:
            colony = self.GetColony(ownerID)
        freshColonyData = ColonyData(session.charid, None)
        colony.SetColonyData(freshColonyData)
        freshColonyData.SetLevel(serializedColony.level)
        for pin in serializedColony.pins:
            freshColonyData.RestorePinFromRow(pin)

        for linkData in serializedColony.links:
            freshColonyData.RestoreLinkFromRow(linkData)

        for route in serializedColony.routes:
            freshColonyData.RestoreRouteFromRow(route)

        colony.currentSimTime = serializedColony.currentSimTime
        colony.PrimeSimulation(serializedColony.currentSimTime)
        self.colonies[ownerID] = colony
        self.colony = colony
        return colony

    @bluepy.TimedFunction('ClientPlanet::PreparePlanet')
    def PreparePlanet(self):
        planetInfo = self.remoteHandler.GetPlanetInfo()
        self.solarSystemID = planetInfo.solarSystemID
        self.planetTypeID = planetInfo.planetTypeID
        self.radius = planetInfo.radius
        self.colony = None
        self.celestialIndex = planetInfo.celestialIndex
        if hasattr(planetInfo, 'currentSimTime') or hasattr(planetInfo, 'pins'):
            colony = self._PrimeColony(session.charid, planetInfo)
            self.colony = colony
            self.colony.RunSimulation(beNice=True)
            self.StartTicking()

    def IsInEditMode(self):
        if self.isInEditMode:
            return True
        if self.commandPinChange != CP_NOCHANGE:
            return True
        if self.changes.GetStreamLength() > 0:
            return True
        return False

    def GetEditModeData(self):
        return self.backupData

    def ValidateMakeChanges(self):
        if self.commandPinChange == CP_COMMANDPINREMOVED:
            raise UserError('CannotModifyAbandonedColony')

    def _EnterEditMode(self):
        if not self.colony:
            colony = self.GetColony(session.charid)
            if colony is None:
                self.LogInfo('No colony found, creating a blank one')
                colony = self.GetNewColony(session.charid)
                colony.SetColonyData(ColonyData(session.charid, None))
                self.colonies[session.charid] = colony
                self.colony = colony
            else:
                self.colony = colony
        if not self.isInEditMode:
            self.backupData = self.colony.colonyData.GetCopy()
            self.backupData.SetEventHandler(self)
            self.enteredEditModeTime = blue.os.GetWallclockTime()
            self.StopTicking()
            self.isInEditMode = True
            sm.GetService('planetUI').EnteredEditMode(self.planetID)

    def _ExitEditMode(self):
        self.changes.Reset()
        self.commandPinChange = CP_NOCHANGE
        self.backupData = None
        if self.colony is not None:
            self.colony.ResetPinCreationCost()
            if self.colony.colonyData is not None:
                for pin in self.colony.colonyData.pins.itervalues():
                    if getattr(pin, 'inEditMode', False):
                        pin.inEditMode = False

        self.enteredEditModeTime = None
        self.isInEditMode = False
        self.StartTicking()
        sm.GetService('planetUI').ExitedEditMode(self.planetID)

    def RevertChanges(self):
        if self.backupData is not None:
            colony = self.GetColony(session.charid)
            if colony is not None:
                colony.SetColonyData(self.backupData)
            else:
                self.LogWarn('RevertChanges - Reverting changes without reapplying old data; colony not found')
            self.backupData = None
        self._ExitEditMode()

    def SubmitChanges(self):
        planetSvc = sm.GetService('planetSvc')
        try:
            planetSvc.SetSubmittingInProgressForPlanet(self.planetID)
            return self._SubmitChanges()
        finally:
            planetSvc.RemoveSubmittingInProgressForPlanet(self.planetID)

    def _SubmitChanges(self):
        simulationEndTime = None
        if self.commandPinChange == CP_COMMANDPINREMOVED:
            self.remoteHandler.UserAbandonPlanet()
            newColonyData = ColonyData(session.charid, None)
            self.colonies[session.charid].SetColonyData(newColonyData)
        else:
            serializedChanges = self.changes.Serialize()
            try:
                updatedColony = self.remoteHandler.UserUpdateNetwork(serializedChanges)
            except Exception:
                self.changes.LogCommandStream(self)
                raise

            self._PrimeColony(session.charid, updatedColony)
        if self.commandPinChange != CP_NOCHANGE:
            sm.GetService('planetSvc').ScatterOnPlanetCommandCenterDeployedOrRemoved(self.planetID)
        if self.commandPinChange == CP_COMMANDPINADDED:
            sm.GetService('neocom').Blink('planets', GetByLabel('UI/Neocom/Blink/NewPlanetaryColony'))
        self._ExitEditMode()
        sm.ScatterEvent('OnPlanetChangesSubmitted', self.planetID)

    def CreateCommandPin(self, charID, typeID, latitude, longitude):
        if charID in self.colonies:
            colony = self.GetColony(charID)
            if colony is not None and colony.colonyData is not None and colony.colonyData.commandPin is not None:
                raise UserError('CannotBuildMultipleCommandPins')
        if session.shipid is None or SessionChecker(session, sm).IsPilotControllingStructure():
            raise UserError('CannotBuildCommandPinWithoutShip')
        shipInv = sm.GetService('invCache').GetInventoryFromId(session.shipid)
        commandCenterID = None
        invList = shipInv.List(const.flagSpecializedCommandCenterHold)
        invList.extend(shipInv.List(const.flagColonyResourcesHold))
        invList.extend(shipInv.List(const.flagCargo))
        for item in invList:
            if item.typeID == typeID:
                commandCenterID = item.itemID
                break

        if commandCenterID is None:
            raise UserError('CannotBuildCommandPin')
        colony = self.GetNewColony(charID)
        self.colonies[charID] = colony
        self.colony = colony
        colony.SetColonyData(ColonyData(charID, None))
        colony.ValidateCreatePin(charID, typeID, latitude, longitude)
        wasInEditMode = self.IsInEditMode()
        self._EnterEditMode()
        colony.colonyData.PrimePin(commandCenterID, typeID, charID, latitude, longitude)
        self.changes.AddCommand(commandStream.COMMAND_CREATEPIN, pinID=commandCenterID, typeID=typeID, latitude=latitude, longitude=longitude)
        self.commandPinChange = CP_COMMANDPINADDED
        sm.ScatterEvent('OnPlanetPinPlaced', commandCenterID)
        sm.ScatterEvent('OnEditModeBuiltOrDestroyed', self.planetID)
        pin = colony.GetPin(commandCenterID)
        pin.inEditMode = True
        level = evetypes.GetMetaLevel(typeID)
        colony.colonyData.SetLevel(level)
        return pin

    def CreatePin(self, typeID, latitude, longitude):
        self.ValidateMakeChanges()
        charID = session.charid
        if evetypes.GetGroupID(typeID) == const.groupCommandPins:
            return self.CreateCommandPin(charID, typeID, latitude, longitude)
        colony = self.GetColony(charID)
        if colony is None:
            raise UserError('CannotManagePlanetWithoutCommandCenter')
        colony.ValidateCreatePin(charID, typeID, latitude, longitude)
        pinID = colony.GetTemporaryPinID()
        wasInEditMode = self.IsInEditMode()
        self._EnterEditMode()
        colony.colonyData.PrimePin(pinID, typeID, charID, latitude, longitude)
        pin = colony.GetPin(pinID)
        pin.inEditMode = True
        self.changes.AddCommand(commandStream.COMMAND_CREATEPIN, pinID=pinID, typeID=typeID, latitude=latitude, longitude=longitude)
        sm.ScatterEvent('OnPlanetPinPlaced', pinID)
        sm.ScatterEvent('OnEditModeBuiltOrDestroyed', self.planetID)
        return pin

    def RemovePin(self, pinID):
        self.ValidateMakeChanges()
        charID = session.charid
        colony = self.GetColony(charID)
        if colony is None:
            raise UserError('CannotManagePlanetWithoutCommandCenter')
        pin = colony.GetPin(pinID)
        if pin is None:
            raise UserError('PinDoesNotExist')
        colony.ValidateRemovePin(charID, pinID)
        self._EnterEditMode()
        for endPointID in colony.colonyData.GetLinksForPin(pinID):
            self.RemoveLink(pinID, endPointID)

        colony.colonyData.RemovePin(charID, pinID)
        if pin.IsCommandCenter():
            if self.commandPinChange == CP_COMMANDPINADDED:
                self.commandPinChange = CP_NOCHANGE
            else:
                self.commandPinChange = CP_COMMANDPINREMOVED
            for subPinID in colony.colonyData.pins.keys():
                colony.colonyData.RemovePin(charID, subPinID)

            self.changes.Reset()
        else:
            if colony.IsTemporaryID(pinID):
                colony.RemoveCreationCost(pin.typeID)
            self.changes.AddCommand(commandStream.COMMAND_REMOVEPIN, pinID=pinID)
        sm.ScatterEvent('OnEditModeBuiltOrDestroyed', self.planetID)

    def InstallSchematic(self, pinID, schematicID):
        self.ValidateMakeChanges()
        charID = session.charid
        colony = self.GetColony(charID)
        if colony is None:
            raise UserError('CannotManagePlanetWithoutCommandCenter')
        colony.ValidateInstallSchematic(charID, pinID, schematicID)
        self._EnterEditMode()
        colony.InstallSchematicForPin(charID, pinID, schematicID)
        pin = colony.GetPin(pinID)
        pin.inEditMode = True
        self.changes.AddCommand(commandStream.COMMAND_SETSCHEMATIC, pinID=pinID, schematicID=schematicID)
        sm.ScatterEvent('OnRefreshPins', [pinID])

    def CreateLink(self, pin1ID, pin2ID, typeID):
        self.ValidateMakeChanges()
        if pin1ID > pin2ID:
            pin1ID, pin2ID = pin2ID, pin1ID
        charID = session.charid
        colony = self.GetColony(charID)
        if colony is None:
            raise UserError('CannotManagePlanetWithoutCommandCenter')
        colony.ValidateCreateLink(charID, pin1ID, pin2ID, typeID)
        self._EnterEditMode()
        link = colony.colonyData.PrimeLink(typeID, pin1ID, pin2ID)
        link.editModeLink = True
        self.changes.AddCommand(commandStream.COMMAND_CREATELINK, endpoint1=pin1ID, endpoint2=pin2ID, level=0)
        sm.ScatterEvent('OnEditModeBuiltOrDestroyed', self.planetID)

    def RemoveLink(self, pin1ID, pin2ID):
        self.ValidateMakeChanges()
        if pin1ID > pin2ID:
            pin1ID, pin2ID = pin2ID, pin1ID
        charID = session.charid
        colony = self.GetColony(charID)
        if colony is None:
            raise UserError('CannotManagePlanetWithoutCommandCenter')
        colony.ValidateRemoveLink(charID, pin1ID, pin2ID)
        self._EnterEditMode()
        link = self.colony.GetLink(pin1ID, pin2ID)
        for routeID in link.routesTransiting[:]:
            self.RemoveRoute(routeID)

        colony.colonyData.RemoveLink(pin1ID, pin2ID)
        self.changes.AddCommand(commandStream.COMMAND_REMOVELINK, endpoint1=pin1ID, endpoint2=pin2ID)
        sm.ScatterEvent('OnEditModeBuiltOrDestroyed', self.planetID)

    def SetLinkLevel(self, pin1ID, pin2ID, newLevel):
        self.ValidateMakeChanges()
        charID = session.charid
        colony = self.GetColony(charID)
        if colony is None:
            raise UserError('CannotManagePlanetWithoutCommandCenter')
        colony.ValidateSetLinkLevel(charID, pin1ID, pin2ID, newLevel)
        self._EnterEditMode()
        colony.colonyData.SetLinkLevel(pin1ID, pin2ID, newLevel)
        link = self.colony.GetLink(pin1ID, pin2ID)
        link.editModeLink = True
        self.changes.AddCommand(commandStream.COMMAND_SETLINKLEVEL, endpoint1=pin1ID, endpoint2=pin2ID, level=newLevel)
        sm.ScatterEvent('OnEditModeBuiltOrDestroyed', self.planetID)

    def CreateRoute(self, path, typeID, quantity):
        self.ValidateMakeChanges()
        charID = session.charid
        colony = self.GetColony(charID)
        if colony is None:
            raise UserError('CannotManagePlanetWithoutCommandCenter')
        colony.ValidateCreateRoute(charID, path, typeID, quantity)
        routeID = colony.GetTemporaryRouteID()
        self._EnterEditMode()
        colony.colonyData.PrimeRoute(routeID, path, typeID, quantity)
        self.changes.AddCommand(commandStream.COMMAND_CREATEROUTE, routeID=routeID, path=path, typeID=typeID, quantity=quantity)
        sm.ScatterEvent('OnEditModeBuiltOrDestroyed', self.planetID)

    def RemoveRoute(self, routeID):
        self.ValidateMakeChanges()
        charID = session.charid
        colony = self.GetColony(charID)
        if colony is None:
            raise UserError('CannotManagePlanetWithoutCommandCenter')
        colony.ValidateRemoveRoute(charID, routeID)
        self._EnterEditMode()
        colony.colonyData.RemoveRoute(routeID)
        self.changes.AddCommand(commandStream.COMMAND_REMOVEROUTE, routeID=routeID)
        sm.ScatterEvent('OnEditModeBuiltOrDestroyed', self.planetID)

    def UpgradeCommandCenter(self, pinID, level):
        self.ValidateMakeChanges()
        charID = session.charid
        colony = self.GetColony(charID)
        colony.ValidateCommandCenterUpgrade(level)
        self._EnterEditMode()
        colony.colonyData.SetLevel(level)
        self.changes.AddCommand(commandStream.COMMAND_UPGRADECOMMANDCENTER, pinID=pinID, level=level)
        sm.ScatterEvent('OnEditModeBuiltOrDestroyed', self.planetID)

    def GetLocalDistributionReport(self, surfacePoint):
        return self.remoteHandler.GMGetLocalDistributionReport(self.planetID, (surfacePoint.theta, surfacePoint.phi))

    def GetCostOfCurrentEdits(self):
        colony = self.GetColony(session.charid)
        if not colony:
            return 0.0
        return colony.cumulativePinCreationCost + colony.cumulativeUpgradeCost

    def LaunchCommodities(self, commandPinID, commoditiesToLaunch):
        if self.IsInEditMode():
            raise UserError('CannotLaunchInEditMode')
        if len(commoditiesToLaunch) < 1:
            raise UserError('PleaseSelectCommoditiesToLaunch')
        colony = self.GetColony(session.charid)
        if colony is None:
            raise UserError('CannotLaunchWithoutColony')
        commandPin = colony.GetPin(commandPinID)
        if not commandPin or not commandPin.IsCommandCenter():
            raise UserError('CanOnlyLaunchFromCommandCenters')
        nextLaunchTime = commandPin.GetNextLaunchTime()
        if nextLaunchTime is not None and nextLaunchTime > blue.os.GetWallclockTime():
            raise UserError('CannotLaunchCommandPinNotReady')
        if not commandPin.CanLaunch(commoditiesToLaunch):
            raise UserError('CannotLaunchCommoditiesNotFound')
        oldData = colony.colonyData.GetCopy()
        try:
            lastLaunchTime = self.remoteHandler.UserLaunchCommodities(commandPinID, commoditiesToLaunch)
            commandPin.lastLaunchTime = lastLaunchTime
            colony.RunSimulation(runSimUntil=lastLaunchTime)
            for typeID, qty in commoditiesToLaunch.iteritems():
                commandPin.RemoveCommodity(typeID, qty)

        except:
            colony.SetColonyData(oldData)
            sm.ChainEvent('ProcessColonyDataSet', self.planetID)
            raise

        sm.ScatterEvent('OnRefreshPins', [commandPin.id])
        if not self.ticking:
            self.StartTicking()

    def OpenTransferWindow(self, path):
        from eve.client.script.ui.shared.planet.expeditedTransferUI import ExpeditedTransferManagementWindow
        ExpeditedTransferManagementWindow.CloseIfOpen()
        ExpeditedTransferManagementWindow.Open(planet=self, path=path)

    def TransferCommodities(self, path, commodities):
        if self.IsInEditMode():
            raise UserError('CannotTransferInEditMode')
        colony = self.GetColony(session.charid)
        if colony is None:
            raise UserError('CannotManagePlanetWithoutCommandCenter')
        if len(path) < 2:
            raise UserError('CreateRouteTooShort')
        if len(commodities) < 1:
            raise UserError('CreateRouteWithoutCommodities')
        runTime = blue.os.GetWallclockTime()
        minBandwidth = colony.ValidateExpeditedTransfer(session.charid, path, commodities, runTime)
        oldData = colony.colonyData.GetCopy()
        try:
            simTime, sourceRunTime = self.remoteHandler.UserTransferCommodities(path, commodities)
            colony.RunSimulation(runSimUntil=simTime)
            colony.ExecuteExpeditedTransfer(path[0], path[-1], commodities, minBandwidth, runTime)
            sourcePin = colony.GetPin(path[0])
            sourcePin.lastRunTime = sourceRunTime
        except:
            colony.SetColonyData(oldData)
            sm.ChainEvent('ProcessColonyDataSet', self.planetID)
            raise

        sm.ScatterEvent('OnRefreshPins', [path[0], path[-1]])
        self.StartTicking(forceRestart=True)

    def AddExtractorHead(self, pinID, headID, latitude, longitude):
        self.ValidateMakeChanges()
        charID = session.charid
        colony = self.GetColony(charID)
        if colony is None:
            raise UserError('CannotManagePlanetWithoutCommandCenter')
        if headID is None:
            headID = self.GetPin(pinID).GetNextAvailableHeadID()
        colony.ValidateAddExtractorHead(pinID, headID)
        self._EnterEditMode()
        colony.colonyData.AddExtractorHead(pinID, headID, latitude, longitude)
        self.changes.AddCommand(commandStream.COMMAND_ADDEXTRACTORHEAD, pinID=pinID, headID=headID, latitude=latitude, longitude=longitude)
        try:
            self.MoveExtractorHead(pinID, headID, latitude, longitude)
        except:
            self.RemoveExtractorHead(pinID, headID)
            raise

        sm.ScatterEvent('OnEditModeBuiltOrDestroyed', self.planetID)
        return headID

    def RemoveExtractorHead(self, pinID, headID):
        self.ValidateMakeChanges()
        charID = session.charid
        colony = self.GetColony(charID)
        if colony is None:
            raise UserError('CannotManagePlanetWithoutCommandCenter')
        colony.ValidateRemoveExtractorHead(pinID, headID)
        self._EnterEditMode()
        colony.colonyData.RemoveExtractorHead(pinID, headID)
        self.changes.AddCommand(commandStream.COMMAND_KILLEXTRACTORHEAD, pinID=pinID, headID=headID)
        sm.ScatterEvent('OnEditModeBuiltOrDestroyed', self.planetID)

    def MoveExtractorHead(self, pinID, headID, latitude, longitude):
        self.ValidateMakeChanges()
        charID = session.charid
        colony = self.GetColony(charID)
        if colony is None:
            raise UserError('CannotManagePlanetWithoutCommandCenter')
        colony.ValidateMoveExtractorHead(pinID, headID, latitude, longitude)
        self._EnterEditMode()
        colony.colonyData.MoveExtractorHead(pinID, headID, latitude, longitude)
        self.changes.AddCommand(commandStream.COMMAND_MOVEEXTRACTORHEAD, pinID=pinID, headID=headID, latitude=latitude, longitude=longitude)
        sm.ScatterEvent('OnEditModeBuiltOrDestroyed', self.planetID)

    def SetExtractorHeadRadius(self, pinID, radius):
        pin = self.GetPin(pinID)
        pin.SetExtractorHeadRadius(radius)

    def InstallProgram(self, pinID, typeID, headRadius):
        self.ValidateMakeChanges()
        charID = session.charid
        colony = self.GetColony(charID)
        if colony is None:
            raise UserError('CannotManagePlanetWithoutCommandCenter')
        pin = self.GetPin(pinID)
        if len(pin.heads) < 1:
            typeID = None
        colony.ValidateInstallProgram(pinID, typeID, headRadius)
        if typeID is not None:
            qtyToDistribute, cycleTime, numCycles = self.remoteHandler.GetProgramResultInfo(pinID, typeID, pin.heads, headRadius)
        else:
            qtyToDistribute, cycleTime, numCycles = (0, 0, 0)
        qtyToRoute = pin.GetMaxOutput(qtyToDistribute, cycleTime)
        self._EnterEditMode()
        routes = colony.colonyData.GetSourceRoutesForPin(pinID)
        if typeID is None:
            colony.colonyData.InstallProgram(pinID, typeID, headRadius, maxValue=qtyToDistribute, numCycles=numCycles)
            pin.inEditMode = True
            self.changes.AddCommand(commandStream.COMMAND_INSTALLPROGRAM, pinID=pinID, typeID=typeID, headRadius=headRadius)
        else:
            storageRouteQty = {}
            processRouteQty = {}
            pathsByID = {}
            formerQtyToStorage = 0
            for route in routes:
                if route is None:
                    self.LogWarn('Unable to find route for recreation:', route.routeID)
                    continue
                if typeID != route.GetType():
                    self.RemoveRoute(route.routeID)
                    continue
                destPin = colony.GetPin(route.GetDestinationPinID())
                if not destPin or not destPin.IsStorage() and not destPin.IsConsumer():
                    continue
                pathsByID[route.routeID] = route.path
                if destPin.IsStorage():
                    dictToUse = storageRouteQty
                    formerQtyToStorage += route.GetQuantity()
                else:
                    dictToUse = processRouteQty
                if route.routeID not in dictToUse:
                    dictToUse[route.routeID] = 0
                dictToUse[route.routeID] += route.GetQuantity()
                self.RemoveRoute(route.routeID)

            colony.colonyData.InstallProgram(pinID, typeID, headRadius, maxValue=qtyToDistribute, cycleTime=cycleTime, numCycles=numCycles)
            pin.inEditMode = True
            self.changes.AddCommand(commandStream.COMMAND_INSTALLPROGRAM, pinID=pinID, typeID=typeID, headRadius=headRadius)
            if len(processRouteQty) + len(storageRouteQty) > 0:
                for routeID, formerQty in processRouteQty.iteritems():
                    amtToRoute = formerQty
                    if qtyToRoute <= 0:
                        break
                    elif qtyToRoute < formerQty:
                        amtToRoute = qtyToRoute
                    path = pathsByID[routeID]
                    try:
                        self.CreateRoute(path, typeID, amtToRoute)
                        qtyToRoute -= amtToRoute
                    except UserError as e:
                        self.LogInfo('Encountered problem when trying to reroute', amtToRoute, 'units of', typeID, 'along path', path, ':', e.msg)
                        sys.exc_clear()

                storageTotalLeft = qtyToRoute
                if formerQtyToStorage > 0:
                    qtyRemainder = 0.0
                    for routeID, formerQty in storageRouteQty.iteritems():
                        if qtyToRoute <= 0:
                            break
                        floatAmtToRoute = float(formerQty) / formerQtyToStorage * storageTotalLeft
                        amtToRoute = int(round(floatAmtToRoute))
                        qtyRemainder += floatAmtToRoute - amtToRoute
                        amtToRoute += int(round(qtyRemainder))
                        path = pathsByID[routeID]
                        amtToRoute = self.FindRoutableQuantityOfResource(colony, path, typeID, amtToRoute, pin.GetCycleTime())
                        qtyRemainder -= round(qtyRemainder)
                        try:
                            self.CreateRoute(path, typeID, amtToRoute)
                            qtyToRoute -= amtToRoute
                        except UserError as e:
                            self.LogInfo('Encountered problem when trying to reroute', amtToRoute, 'units of', typeID, 'along path', path, ':', e.msg)
                            sys.exc_clear()

    def CancelInstallProgram(self, pinID, pinData):
        if not self.isInEditMode:
            return None
        if not self.changes.stream:
            self.RevertChanges()
            return None
        pin = self.GetPin(pinID)
        return pin

    def FindRoutableQuantityOfResource(self, colony, path, typeID, quantity, cycleTime):
        minimumBandwidth = None
        prevPinID = None
        for pinID in path:
            if prevPinID is None:
                prevPinID = pinID
                continue
            link = colony.colonyData.GetLink(prevPinID, pinID)
            availableBandwidth = link.GetTotalBandwidth() - link.GetBandwidthUsage()
            if minimumBandwidth is None or availableBandwidth < minimumBandwidth:
                minimumBandwidth = availableBandwidth
            prevPinID = pinID

        baseVolume = evetypes.GetVolume(typeID)
        requiredBandwidth = planetCommon.GetBandwidth(baseVolume * quantity, cycleTime)
        if requiredBandwidth > minimumBandwidth:
            quantity = int(minimumBandwidth * float(cycleTime) / (const.HOUR * baseVolume))
        return quantity

    def OnSchematicInstalled(self, charID, pinID, schematicID):
        colony = self.GetColony(charID)
        pin = colony.GetPin(pinID)
        obsoleteRoutes = colony.colonyData.GetObsoleteRoutesForPin(pin)
        for routeID in obsoleteRoutes:
            self.RemoveRoute(routeID)

    def GMInstallProgram(self, pinID):
        colony = self.GetColonyByPinID(pinID)
        if colony is None:
            raise RuntimeError('Unable to find colony for pinID')
        pin = colony.GetPin(pinID)
        resourceInfo = self.remoteHandler.GetPlanetResourceInfo()
        typeOptions = [ (evetypes.GetName(typeID), typeID) for typeID in resourceInfo.keys() ]
        format = [{'type': 'combo',
          'key': 'typeID',
          'label': 'Type',
          'options': typeOptions,
          'frame': 0,
          'labelwidth': 80},
         {'type': 'edit',
          'key': 'qtyPerCycle',
          'label': 'Output per cycle',
          'setvalue': '100',
          'frame': 0,
          'labelwidth': 140,
          'required': True},
         {'type': 'btline'},
         {'type': 'edit',
          'key': 'cycleTime',
          'label': 'Cycle time (seconds)',
          'setvalue': '60',
          'frame': 0,
          'labelwidth': 140,
          'required': True},
         {'type': 'edit',
          'key': 'lifetime',
          'label': 'Lifetime (hours)',
          'setvalue': '24',
          'frame': 0,
          'labelwidth': 140,
          'required': True}]
        icon = 'ui_35_64_11'
        retval = uix.HybridWnd(format=format, caption='Deposit designer: %s' % planetCommon.GetGenericPinName(pin.typeID, pin.id), windowID='installProgramGM', modal=1, buttons=uiconst.OKCANCEL, minW=300, minH=132, icon=icon)
        if retval is None:
            return
        typeID, qtyPerCycle, cycleTime, lifetimeHours = (retval['typeID'],
         retval['qtyPerCycle'],
         retval['cycleTime'],
         retval['lifetime'])
        typeID = int(typeID)
        qtyPerCycle = int(qtyPerCycle)
        cycleTime = long(cycleTime) * const.SEC
        lifetimeHours = int(lifetimeHours)
        headRadius = 1.0
        if typeID not in resourceInfo or qtyPerCycle < 0 or cycleTime < 10 * const.SEC or lifetimeHours < 1 or headRadius <= 0.0:
            return
        self.remoteHandler.GMForceInstallProgram(pinID, typeID, cycleTime, lifetimeHours, qtyPerCycle, headRadius)

    def GMConvertCommandCenter(self, pinID):
        self.remoteHandler.GMConvertCommandCenter(pinID)

    def GMAddCommodity(self, pinID, typeID):
        quantity = uix.QtyPopup(None, 1, 100).get('qty', None)
        if not quantity:
            return
        self.remoteHandler.GMAddCommodity(pinID, typeID, quantity)

    def GMVerifySimulation(self):
        self.LogNotice('VerifySimulation -- starting')
        simulationDuration, remoteColonyData = self.remoteHandler.GMGetSynchedServerState(session.charid)
        simEndTime = remoteColonyData.currentSimTime
        colony = self.GetColony(session.charid)
        startTime = blue.os.GetWallclockTimeNow()
        colony.RunSimulation(runSimUntil=simEndTime)
        clientSimulationRuntime = blue.os.GetWallclockTimeNow() - startTime
        pins = remoteColonyData.pins
        self.LogNotice('simulation ran for', clientSimulationRuntime, 'on client, ', simulationDuration, 'on server')
        for pin in pins:
            clientPin = colony.GetPin(pin.id)
            if clientPin is None:
                self.LogError(pin.id, 'exists on server but not on client')
                continue
            for key, value in pin.__dict__.iteritems():
                if not hasattr(clientPin, key):
                    self.LogError(pin.id, 'on client does not have attribute ', key)
                    continue
                clientValue = getattr(clientPin, key)
                if clientValue != value:
                    self.LogError(pin.id, 'does not agree on a value for', key, 'Client says ', clientValue, 'but server', value)

        self.LogNotice('VerifySimulation -- finished')

    def GetPlanetRadius(self):
        return self.radius

    def GetTypeAttribute(self, typeID, attributeID):
        return sm.GetService('godma').GetTypeAttribute2(typeID, attributeID)

    def GetResourceData(self, resourceTypeID):
        if not hasattr(self, 'resources'):
            self.LogInfo('GetResourceData: creating resource collection')
            self.resources = {}
        if resourceTypeID not in self.resources:
            self.LogInfo('GetResourceData: creating new resource entry for resource', resourceTypeID)
            entry = self.CreateResourceEntry()
            self.resources[resourceTypeID] = entry
        else:
            entry = self.resources[resourceTypeID]
        inRange = True
        info = self.CreateResourceInfo(resourceTypeID, entry)
        if getattr(info, 'skillMissing', False):
            inRange = False
            eve.Message('PISkillRequiredToSurveyPlanetResources', {'skill': evetypes.GetName(const.typeRemoteSensing)})
        elif getattr(info, 'unreachableSystem', False):
            inRange = False
            eve.Message('PIUnableToScanWorholeSystemRemotely')
        elif hasattr(info, 'requiredSkill'):
            inRange = False
            eve.Message('PISkillLevelToLowForRemoteSensing', {'level': info.requiredSkill})
        elif hasattr(info, 'systemOutOfRange'):
            inRange = False
            eve.Message('PISkillLevelToLowForRemoteSensingDistance', {'systemDistance': info.systemDistance,
             'maxScanDistance': info.maxScanDistance})
        elif info.newBand > entry.numBands or blue.os.GetWallclockTime() > entry.updateTime:
            self.LogInfo('GetResourceData: refreshing data: newBand', info.newBand, 'currentBand', entry.numBands, 'updateTime', entry.updateTime)
            shData = self.remoteHandler.GetResourceData(info)
            if shData.data is not None:
                entry.sh = builder.CreateSHFromBuffer(shData.data, shData.numBands)
                entry.updateTime = blue.os.GetWallclockTime() + planetCommon.RESOURCE_CACHE_TIMEOUT
                entry.proximity = shData.proximity
                entry.numBands = shData.numBands
                self.LogInfo('GetResourceData: creating SH for ', resourceTypeID, 'upto band', shData.numBands)
            else:
                self.LogInfo('GetResourceData: no new data received')
        else:
            self.LogInfo('GetResourceData: no need to refresh data')
        return (inRange, self.resources[resourceTypeID].sh)

    def GetResourceHarmonic(self, typeID):
        inRange, sh = self.GetResourceData(typeID)
        return sh

    def CreateResourceInfo(self, resourceTypeID, entry):
        info = utillib.KeyVal(resourceTypeID=resourceTypeID, updateTime=entry.updateTime, oldBand=entry.numBands, planetology=0, advancedPlanetology=0, remoteSensing=0)
        planetInfo = sm.GetService('map').GetPlanetInfo(self.planetID)
        planetLoc = cfg.evelocations.Get(planetInfo.solarSystemID)
        planetPos = (planetLoc.x, planetLoc.y, planetLoc.z)
        playerLoc = cfg.evelocations.Get(session.solarsystemid2)
        playerPos = (playerLoc.x, playerLoc.y, playerLoc.z)
        dist = geo2.Vec3Distance(playerPos, planetPos) / const.LIGHTYEAR
        info.remoteSensing = sm.GetService('skills').GetEffectiveLevel(const.typeRemoteSensing) or 0
        if info.remoteSensing == 0:
            info.skillMissing = True
            return info
        if session.solarsystemid2 == planetInfo.solarSystemID or sm.GetService('planetSvc').IsPlanetColonizedByMe(self.planetID):
            info.proximity = const.planetResourceProximityPlanet
        else:
            if not IsKnownSpaceSystem(session.solarsystemid2) or sm.GetService('clientPathfinderService').GetJumpCountFromCurrent(planetInfo.solarSystemID) > 1000:
                info.unreachableSystem = True
                return info
            info.proximity = None
            for i, scanRange in enumerate(const.planetResourceScanningRanges):
                if scanRange >= dist:
                    info.proximity = i

            if info.proximity is None or dist > const.planetResourceScanningRanges[5 - info.remoteSensing]:
                info.systemOutOfRange = True
                info.systemDistance = dist
                info.maxScanDistance = const.planetResourceScanningRanges[5 - info.remoteSensing]
                return info
        info.planetology = sm.GetService('skills').GetEffectiveLevel(const.typePlanetology) or 0
        info.advancedPlanetology = sm.GetService('skills').GetEffectiveLevel(const.typeAdvancedPlanetology) or 0
        minBand, maxBand = const.planetResourceProximityLimits[info.proximity]
        info.newBand = min(maxBand, minBand + info.planetology + info.advancedPlanetology * 2)
        requiredSkill = 5 - info.proximity
        if info.remoteSensing < requiredSkill:
            info.requiredSkill = requiredSkill
        return info

    def CreateResourceEntry(self):
        entry = utillib.KeyVal(sh=builder.CreateConstantSH(0.0, 1), updateTime=0, numBands=0, proximity=None)
        return entry

    def StartTicking(self, forceRestart = False):
        if forceRestart:
            self.ticking = False
            if self.tickThread is not None:
                self.LogInfo('StartTicking :: Forcing restart of tick thread')
                self.tickThread.kill()
                self.tickThread = None
        elif self.ticking:
            return
        self.ticking = True
        self.tickThread = uthread.new(self._Tick, session.charid)

    def StopTicking(self):
        self.ticking = False
        if self.tickThread is not None:
            self.tickThread.kill()
            self.tickThread = None

    def GetNextTickTime(self, charID):
        if self.colony is None or self.colony.colonyData is None:
            return
        nextTickTime = None
        for pin in self.colony.colonyData.pins.itervalues():
            if pin.IsActive() or pin.CanActivate():
                pinTickTime = pin.GetNextRunTime()
                if pinTickTime is None or pinTickTime < blue.os.GetWallclockTime():
                    nextTickTime = blue.os.GetWallclockTime()
                    break
                elif nextTickTime is None or pinTickTime < nextTickTime:
                    nextTickTime = pinTickTime

        return nextTickTime

    def _Tick(self, charID):
        while self.ticking:
            if not self:
                return
            if self.colony is not None:
                self.colony.RunSimulation(beNice=True)
                if self.colony.colonyData is not None:
                    sm.ScatterEvent('OnRefreshPins', self.colony.colonyData.pins.keys())
            nextTime = self.GetNextTickTime(charID)
            if nextTime is None:
                self.ticking = False
            else:
                nextTime = max(const.SEC, nextTime - blue.os.GetWallclockTime() + 1L)
                self.LogInfo(self.planetID, ': Active Client Tick: sleeping for', FmtTimeInterval(nextTime))
                blue.pyos.synchro.SleepWallclock(nextTime / const.MSEC)

        self.tickThread = None

    def GMRunDepletionSim(self, typeID, info):
        self.remoteHandler.GMRunDepletionSim(typeID, info)

    def RestartExtractors(self):
        if self.IsEditingPlanet():
            raise UserError('CustomNotify', {'notify': GetByLabel('UI/PI/Common/CannotRestartWhileEditing')})
        if sm.GetService('planetSvc').IsSubmittingInProgressOrThrottled():
            raise UserError('CustomNotify', {'notify': GetByLabel('UI/PI/Common/PlanetBusyUpdating')})
        ecuPins = self.colony.colonyData.GetECUPins()
        for pin in ecuPins:
            if not pin.programType:
                continue
            if pin.IsActive():
                continue
            currentRadius = max(min(pin.headRadius, planetCommon.RADIUS_DRILLAREAMAX), planetCommon.RADIUS_DRILLAREAMIN)
            self.InstallProgram(pin.id, pin.programType, currentRadius)

        try:
            if self.changes.GetStreamLength():
                if sm.GetService('planetSvc').IsSubmittingInProgressOrThrottled():
                    raise UserError('CustomNotify', {'notify': GetByLabel('UI/PI/Common/PlanetBusyUpdating')})
                sm.ScatterEvent('OnPlanetSubmittingChanges')
                self.SubmitChanges()
                return True
            return False
        except StandardError as e:
            self.RevertChanges()
            raise

    def IsEditingPlanet(self):
        if self.commandPinChange == CP_COMMANDPINREMOVED:
            return True
        if self.changes.GetStreamLength():
            return True
        return False
