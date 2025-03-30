#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\planet\colonyData.py
import weakref
from collections import defaultdict
import blue
import bluepy
import dogma.data
import evetypes
import log
import types
import utillib
from blue import heapq
from eve.common.lib import appConst
from eve.common.script.planet.entities.baseLink import BaseLink
from eve.common.script.planet.entities.baseRoute import BaseRoute
from eve.common.script.util import planetCommon
PINTYPES_WITH_STORAGE = (appConst.groupSpaceportPins, appConst.groupStoragePins, appConst.groupCommandPins)

class ColonyData(object):
    __name__ = 'ColonyData'

    def __init__(self, ownerID, eventHandler):
        self.ownerID = ownerID
        if eventHandler is None:
            self.eventHandler = None
        else:
            self.eventHandler = weakref.proxy(eventHandler)
        self.Init()

    def Init(self):
        self.pins = {}
        self.temporaryIDMap = {}
        self.commandPin = None
        self.links = {}
        self.linksByEndpoint = {}
        self.routes = {}
        self.megaRoutesBySource = {}
        self.routesByDestination = {}
        self.routesBySource = {}
        self.level = 0
        self.ResetResourceUsage()

    def RegisterTemporaryID(self, oldID, newID):
        self.temporaryIDMap[oldID] = newID

    def IsTemporaryID(self, id):
        return isinstance(id, tuple)

    def GetRealIDFromTemporaryID(self, oldID):
        return self.temporaryIDMap.get(oldID, None)

    def ClearTemporaryIDs(self):
        self.temporaryIDMap.clear()

    def SetEventHandler(self, newEventHandler):
        oldEventHandlerWasNone = self.eventHandler is None
        if newEventHandler is None:
            self.eventHandler = None
        else:
            self.eventHandler = weakref.proxy(newEventHandler)
        if oldEventHandlerWasNone and newEventHandler is not None:
            self.RecalculatePowerAndCpuStatistics()

    def GetPin(self, pinID):
        pinData = self.pins.get(pinID, None)
        if pinData is None:
            possiblePinID = self.GetRealIDFromTemporaryID(pinID)
            pinData = self.pins.get(possiblePinID)
        return pinData

    def GetLink(self, endpoint1, endpoint2):
        if endpoint1 > endpoint2:
            endpoint1, endpoint2 = endpoint2, endpoint1
        return self.links.get((endpoint1, endpoint2), None)

    def GetRoute(self, routeID):
        return self.routes.get(routeID, None)

    def GetPlanetRadius(self):
        if self.eventHandler is not None:
            return self.eventHandler.GetPlanetRadius()
        else:
            return 1.0

    @bluepy.TimedFunction('ColonyData::PrimePin')
    def PrimePin(self, pinID, typeID, ownerID, latitude, longitude, lastRunTime = None, state = None):
        self.LogInfo('Priming pin', pinID, typeID, ownerID, latitude, longitude)
        entityType = planetCommon.GetPinEntityType(typeID)
        if entityType is None:
            self.LogError('Unable to prime pin of invalid type', typeID)
            return
        newPin = entityType(typeID)
        newPin.Startup(pinID, self, ownerID, latitude, longitude, lastRunTime, state)
        self.pins[pinID] = newPin
        if evetypes.GetGroupID(typeID) == appConst.groupCommandPins:
            self.commandPin = newPin
        self.AddPinResourceUsageToColony(newPin)
        if self.eventHandler is not None:
            self.eventHandler.OnPinCreated(pinID)
        return pinID

    @bluepy.TimedFunction('ColonyData::RemovePin')
    def RemovePin(self, charID, pinID, force = False):
        pin = self.GetPin(pinID)
        if not pin:
            self.LogWarn(charID, 'unable to remove pin', pinID, 'as it was not found')
            return
        linksToRemove = self.linksByEndpoint.get(pinID, [])[:]
        for destinationID in linksToRemove:
            self.RemoveLink(pinID, destinationID)

        self.RemovePinResourceUsageFromColony(pin)
        if self.commandPin is not None and self.commandPin.id == pinID:
            self.commandPin = None
        if pinID in self.pins:
            del self.pins[pinID]
        if self.eventHandler is not None:
            self.eventHandler.OnPinRemoved(pinID)

    @bluepy.TimedFunction('ColonyData::PrimeLink')
    def PrimeLink(self, linkTypeID, endpoint1ID, endpoint2ID, level = 0):
        if endpoint1ID > endpoint2ID:
            endpoint1ID, endpoint2ID = endpoint2ID, endpoint1ID
        endpoint1 = self.GetPin(endpoint1ID)
        endpoint2 = self.GetPin(endpoint2ID)
        link = BaseLink(self, linkTypeID, endpoint1, endpoint2, level=level)
        self.links[endpoint1ID, endpoint2ID] = link
        if endpoint1ID not in self.linksByEndpoint:
            self.linksByEndpoint[endpoint1ID] = []
        if endpoint2ID not in self.linksByEndpoint:
            self.linksByEndpoint[endpoint2ID] = []
        self.linksByEndpoint[endpoint1ID].append(endpoint2ID)
        self.linksByEndpoint[endpoint2ID].append(endpoint1ID)
        self.AddLinkResourceUsageToColony(link)
        if self.eventHandler is not None:
            self.eventHandler.OnLinkCreated(endpoint1ID, endpoint2ID)
        return link

    @bluepy.TimedFunction('ColonyData::RemoveLink')
    def RemoveLink(self, endpoint1ID, endpoint2ID):
        if endpoint1ID > endpoint2ID:
            endpoint1ID, endpoint2ID = endpoint2ID, endpoint1ID
        if (endpoint1ID, endpoint2ID) in self.links:
            link = self.links[endpoint1ID, endpoint2ID]
            self.RemoveLinkResourceUsageFromColony(link)
            routes = link.routesTransiting[:]
            for routeID in routes:
                self.RemoveRoute(routeID)

            del self.links[endpoint1ID, endpoint2ID]
        if endpoint1ID in self.linksByEndpoint:
            if endpoint2ID in self.linksByEndpoint[endpoint1ID]:
                self.linksByEndpoint[endpoint1ID].remove(endpoint2ID)
        if endpoint2ID in self.linksByEndpoint:
            if endpoint1ID in self.linksByEndpoint[endpoint2ID]:
                self.linksByEndpoint[endpoint2ID].remove(endpoint1ID)
        if self.eventHandler is not None:
            self.eventHandler.OnLinkRemoved(endpoint1ID, endpoint2ID)

    def GetLinksForPin(self, pinID):
        if pinID not in self.linksByEndpoint:
            return []
        return self.linksByEndpoint[pinID][:]

    def PrimeRoute(self, routeID, path, typeID, quantity):
        newRoute = BaseRoute(self, routeID, self.ownerID, typeID, quantity)
        newRoute.SetPath(path)
        sourceID = newRoute.GetSourcePinID()
        if sourceID not in self.megaRoutesBySource:
            self.megaRoutesBySource[sourceID] = {}
        routeKey = (path[-1], typeID)
        if routeKey not in self.megaRoutesBySource[sourceID]:
            self.megaRoutesBySource[sourceID][routeKey] = quantity
        else:
            self.megaRoutesBySource[sourceID][routeKey] += quantity
        if sourceID not in self.routesBySource:
            self.routesBySource[sourceID] = set()
        self.routesBySource[sourceID].add(newRoute)
        destID = newRoute.GetDestinationPinID()
        if destID not in self.routesByDestination:
            self.routesByDestination[destID] = [routeID]
        elif routeID not in self.routesByDestination[destID]:
            self.routesByDestination[destID].append(routeID)
        self.routes[routeID] = newRoute
        prevPinID = newRoute.path[0]
        for pinID in newRoute.path[1:]:
            link = self.GetLink(prevPinID, pinID)
            if link is None:
                raise RuntimeError('Unable to find link between pins', prevPinID, pinID)
            link.AddRoute(newRoute)
            prevPinID = pinID

        if self.eventHandler is not None:
            self.eventHandler.OnRouteCreated(routeID)

    def RemoveRoute(self, routeID):
        if routeID not in self.routes:
            self.LogWarn('Unable to remove route', routeID, ': route not found')
            return
        route = self.routes[routeID]
        del self.routes[routeID]
        sourceID = route.GetSourcePinID()
        routeKey = (route.path[-1], route.commodityTypeID)
        try:
            self.megaRoutesBySource[sourceID][routeKey] -= route.commodityQuantity
            if not self.megaRoutesBySource[sourceID][routeKey]:
                del self.megaRoutesBySource[sourceID][routeKey]
            if not self.megaRoutesBySource[sourceID]:
                del self.megaRoutesBySource[sourceID]
        except KeyError:
            log.LogException('RemoveRoute::Failed To remove route from megaRoutesBySource')

        if sourceID in self.routesBySource:
            self.routesBySource[sourceID].remove(route)
            if len(self.routesBySource[sourceID]) <= 0:
                del self.routesBySource[sourceID]
        destID = route.GetDestinationPinID()
        if destID in self.routesByDestination:
            self.routesByDestination[destID].remove(routeID)
            if len(self.routesByDestination[destID]) <= 0:
                del self.routesByDestination[destID]
        prevPinID = route.path[0]
        for pinID in route.path[1:]:
            link = self.GetLink(prevPinID, pinID)
            if link is None:
                raise RuntimeError('Unable to find link between pins', prevPinID, pinID)
            link.RemoveRoute(routeID)
            prevPinID = pinID

        if self.eventHandler:
            self.eventHandler.OnRouteRemoved(routeID)

    def SetLevel(self, level):
        self.level = level
        self.RecalculatePowerAndCpuStatistics()

    def GetLevel(self):
        if self.level is None:
            self.level = 0
        return self.level

    @bluepy.TimedFunction('ColonyData::GetSourceRoutesForPin')
    def GetSourceRoutesForPin(self, pinID):
        if pinID not in self.routesBySource:
            return []
        return self.routesBySource[pinID].copy()

    def IsSomeProductUnrouted(self, pinID):
        totalRouted = self.GetAmountRoutedFrom(pinID)
        pin = self.pins.get(pinID, None)
        if not pin:
            return False
        totalProduced = pin.GetTotalAmountProduced()
        return totalRouted < totalProduced

    def IsFullAndHasIncomingRoute(self, pinID):
        pin = self.pins.get(pinID, None)
        if not pin:
            return False
        if not pin.IsStorage():
            return False
        return pin.GetCapacityRemaining() == 0 and self.GetTypeIDsRoutedTo(pinID)

    def GetAmountRoutedFrom(self, pinID):
        return sum([ route.GetQuantity() for route in self.GetSourceRoutesForPin(pinID) ])

    def IsSomeConsumableUnfulfilled(self, pinID):
        pin = self.pins.get(pinID, None)
        if not pin:
            return False
        consumables = pin.GetConsumables()
        if not consumables:
            return False
        incomingTypeIDs = self.GetTypeIDsRoutedTo(pinID)
        for consumable in consumables.keys():
            if consumable not in incomingTypeIDs:
                return True

        return False

    def IsPinNeedingAttention(self, pinID):
        pin = self.pins.get(pinID, None)
        if pin:
            return pin.IsNeedingAttention() or self.IsSomeProductUnrouted(pinID) or self.IsSomeConsumableUnfulfilled(pinID) or self.IsFullAndHasIncomingRoute(pinID)

    def IsSomePinNeedingAttention(self):
        for pinID in self.pins:
            if self.IsPinNeedingAttention(pinID):
                return True

        return False

    def CanEcuPinsBeRestarted(self):
        pins = self.GetECUPins()
        for pin in pins:
            if pin.programType and not pin.IsActive():
                return True

        return False

    def HasIncomingRoute(self, pinID, typeID):
        incomingTypeIDs = self.GetTypeIDsRoutedTo(pinID)
        return typeID in incomingTypeIDs

    def GetTypeIDsRoutedTo(self, pinID):
        routeIDs = self.GetDestinationRoutesForPin(pinID)
        routes = [ self.routes[routeID] for routeID in routeIDs ]
        routeTypes = [ route.GetType() for route in routes ]
        return routeTypes

    def GetSortedRoutesForPin(self, pinID, commodities):
        processorRoutes = []
        storageRoutes = []
        with bluepy.TimerPush('SortingRoutes'):
            for (destID, commodityTypeID), qty in self.megaRoutesBySource.get(pinID, {}).iteritems():
                if not qty:
                    continue
                if commodityTypeID not in commodities:
                    continue
                destPin = self.GetPin(destID)
                if destPin.IsProcessor():
                    heapq.heappush(processorRoutes, (destPin.GetInputBufferState(), (destID, commodityTypeID, qty)))
                else:
                    heapq.heappush(storageRoutes, (destPin.GetFreeSpace(), (destID, commodityTypeID, qty)))

        return (processorRoutes, storageRoutes)

    def GetDestinationRoutesForPin(self, pinID):
        if pinID not in self.routesByDestination:
            return []
        return self.routesByDestination[pinID][:]

    def GetRoutesForChar(self, charID):
        return self.routes

    def SetLinkLevel(self, endpoint1, endpoint2, newLevel):
        link = self.GetLink(endpoint1, endpoint2)
        self.RemoveLinkResourceUsageFromColony(link)
        link.SetLinkLevel(newLevel)
        self.AddLinkResourceUsageToColony(link)

    def AddExtractorHead(self, pinID, headID = None, latitude = None, longitude = None):
        pin = self.GetPin(pinID)
        self.RemovePinResourceUsageFromColony(pin)
        pin.AddHead(headID=headID, latitude=latitude, longitude=longitude)
        self.AddPinResourceUsageToColony(pin)

    def SetHeads(self, pinID, heads):
        pin = self.GetPin(pinID)
        self.RemovePinResourceUsageFromColony(pin)
        pin.SetHeads(heads)
        self.AddPinResourceUsageToColony(pin)

    def RemoveExtractorHead(self, pinID, headID):
        pin = self.GetPin(pinID)
        self.RemovePinResourceUsageFromColony(pin)
        pin.RemoveHead(headID)
        self.AddPinResourceUsageToColony(pin)

    def MoveExtractorHead(self, pinID, headID, latitude, longitude):
        pin = self.GetPin(pinID)
        pin.SetHeadPosition(headID, latitude, longitude)

    def InstallProgram(self, pinID, typeID, headRadius, maxValue = None, cycleTime = None, numCycles = None):
        pin = self.GetPin(pinID)
        if typeID is not None:
            if maxValue is None or cycleTime is None or numCycles is None:
                sh = self.eventHandler.GetResourceType(typeID)
                maxValue, cycleTime, numCycles, overlapModifiers = self.eventHandler.CreateProgram(sh, pinID, typeID, headRadius=headRadius)
            startTime = blue.os.GetWallclockTime()
            endTime = startTime + cycleTime * numCycles
            pin.InstallProgram(typeID, cycleTime, endTime, maxValue, headRadius)
        else:
            pin.ClearProgram()

    def ResetResourceUsage(self):
        self.cpuUsage = self.cpuCapacity = self.powerUsage = self.powerCapacity = 0

    def AddPinResourceUsageToColony(self, pin):
        self.cpuUsage += pin.GetCpuUsage()
        self.cpuCapacity += pin.GetCpuOutput()
        self.powerUsage += pin.GetPowerUsage()
        self.powerCapacity += pin.GetPowerOutput()

    def RemovePinResourceUsageFromColony(self, pin):
        self.cpuUsage -= pin.GetCpuUsage()
        self.cpuCapacity -= pin.GetCpuOutput()
        self.powerUsage -= pin.GetPowerUsage()
        self.powerCapacity -= pin.GetPowerOutput()

    def AddLinkResourceUsageToColony(self, link):
        params = planetCommon.GetUsageParametersForLinkType(link.typeID)
        self.cpuUsage += link.GetCpuUsage(params)
        self.powerUsage += link.GetPowerUsage(params)

    def RemoveLinkResourceUsageFromColony(self, link):
        params = planetCommon.GetUsageParametersForLinkType(link.typeID)
        self.cpuUsage -= link.GetCpuUsage(params)
        self.powerUsage -= link.GetPowerUsage(params)

    def GetColonyCpuUsage(self):
        return self.cpuUsage

    def GetColonyCpuSupply(self):
        return self.cpuCapacity

    def GetColonyPowerUsage(self):
        return self.powerUsage

    def GetColonyPowerSupply(self):
        return self.powerCapacity

    def RecalculatePowerAndCpuStatistics(self):
        self.ResetResourceUsage()
        for pin in self.pins.itervalues():
            self.AddPinResourceUsageToColony(pin)

        for link in self.links.itervalues():
            self.AddLinkResourceUsageToColony(link)

    @bluepy.TimedFunction('ColonyData::RestorePinFromRow')
    def RestorePinFromRow(self, pinRow):
        pinID = self.PrimePin(pinRow.id, pinRow.typeID, pinRow.ownerID, pinRow.latitude, pinRow.longitude, lastRunTime=pinRow.lastRunTime, state=pinRow.state)
        if pinID is None:
            log.LogTraceback('Unable to prime pin being loaded from data')
            return
        groupID = evetypes.GetGroupID(pinRow.typeID)
        if groupID == appConst.groupProcessPins:
            if getattr(pinRow, 'schematicID', None) is not None:
                self.pins[pinRow.id].SetSchematic(pinRow.schematicID)
            if getattr(pinRow, 'hasReceivedInputs', None) is not None:
                self.pins[pinRow.id].hasReceivedInputs = pinRow.hasReceivedInputs
            if getattr(pinRow, 'receivedInputsLastCycle', None) is not None:
                self.pins[pinRow.id].receivedInputsLastCycle = pinRow.receivedInputsLastCycle
        elif groupID == appConst.groupCommandPins or groupID == appConst.groupSpaceportPins:
            self.pins[pinRow.id].lastLaunchTime = pinRow.lastLaunchTime
            if groupID == appConst.groupCommandPins:
                self.commandPin = self.pins[pinRow.id]
        elif groupID == appConst.groupExtractionControlUnitPins:
            if getattr(pinRow, 'heads', None) is not None:
                self.SetHeads(pinRow.id, pinRow.heads)
            if getattr(pinRow, 'programType', None) is None:
                self.LogInfo('Pin', pinRow.id, 'has none program type, clearing program')
                self.pins[pinRow.id].ClearProgram()
            else:
                self.LogInfo('Installing program on pin', pinRow.id, pinRow.programType, pinRow.cycleTime, pinRow.expiryTime, pinRow.qtyPerCycle, pinRow.headRadius, pinRow.installTime)
                self.pins[pinRow.id].InstallProgram(pinRow.programType, pinRow.cycleTime, pinRow.expiryTime, pinRow.qtyPerCycle, pinRow.headRadius, lastRunTime=pinRow.lastRunTime, installTime=pinRow.installTime)
        self.pins[pinRow.id].SetState(pinRow.state)
        for typeID, quantity in pinRow.contents.iteritems():
            self.pins[pinRow.id].SetContents(pinRow.contents)

        return pinID

    @bluepy.TimedFunction('ColonyData::RestoreLinkFromRow')
    def RestoreLinkFromRow(self, linkRow):
        self.PrimeLink(linkRow.typeID, linkRow.endpoint1, linkRow.endpoint2, level=linkRow.level)

    def RestoreRouteFromRow(self, routeRow):
        self.PrimeRoute(routeRow.routeID, routeRow.path, routeRow.commodityTypeID, routeRow.commodityQuantity)

    def GetObsoleteRoutesForPin(self, pin):
        routesToDelete = []
        if pin.IsProducer():
            outputTypeIDs = pin.GetProducts().keys()
            for route in self.GetSourceRoutesForPin(pin.id):
                if route.GetType() not in outputTypeIDs:
                    routesToDelete.append(route.routeID)

        if pin.IsConsumer():
            inputTypeIDs = pin.GetConsumables().keys()
            for routeID in self.GetDestinationRoutesForPin(pin.id):
                route = self.GetRoute(routeID)
                if route.GetType() not in inputTypeIDs:
                    routesToDelete.append(route.routeID)

        return routesToDelete

    def GetCopy(self, eventHandler = None):
        newColonyData = ColonyData(self.ownerID, eventHandler)
        newColonyData.SetLevel(self.level)
        for pin in self.pins.itervalues():
            data = pin.Serialize(full=True)
            newPinID = newColonyData.RestorePinFromRow(data)

        for link in self.links.itervalues():
            data = link.Serialize()
            if data.endpoint1 > data.endpoint2:
                data.endpoint1, data.endpoint2 = data.endpoint2, data.endpoint1
            newColonyData.RestoreLinkFromRow(data)

        for route in self.routes.itervalues():
            data = route.Serialize()
            newColonyData.RestoreRouteFromRow(data)

        return newColonyData

    def Serialize(self):
        data = utillib.KeyVal(ownerID=self.ownerID)
        pinData = []
        linkData = []
        routeData = []
        for pin in self.pins.itervalues():
            pinData.append(pin.Serialize())

        for link in self.links.itervalues():
            try:
                linkData.append(link.Serialize())
            except ReferenceError:
                continue

        for route in self.routes.itervalues():
            routeData.append(route.Serialize())

        data.pins = pinData
        data.links = linkData
        data.routes = routeData
        data.level = self.level
        return data

    def Diff(self, otherColonyData):
        pinsCreated = []
        pinsDeleted = []
        pinContentsChanged = []
        pinStatesChanged = []
        linksCreated = []
        linksDeleted = []
        linksAltered = []
        routesCreated = []
        routesDeleted = []
        programsUpdated = []
        programsDeleted = []
        headsUpdated = []
        headsDeleted = []
        for pin in self.pins.itervalues():
            otherPin = otherColonyData.GetPin(pin.id)
            if otherPin is None:
                pinsCreated.append((int(pin.id),
                 int(pin.typeID),
                 pin.latitude,
                 pin.longitude,
                 int(pin.ownerID)))
                for typeID, qty in pin.GetContents().iteritems():
                    pinContentsChanged.append((int(pin.id), int(typeID), int(qty)))

                pinStatesChanged.append([int(pin.id),
                 int(pin.activityState),
                 pin.lastRunTime,
                 getattr(pin, 'schematicID', None),
                 getattr(pin, 'lastLaunchTime', None)])
                if pin.IsExtractor() and evetypes.GetGroupID(pin.typeID) == appConst.groupExtractionControlUnitPins:
                    progInfo = pin.GetProgramInformation()
                    if progInfo is not None:
                        programsUpdated.append(progInfo)
                    for headID, latitude, longitude in pin.heads:
                        headsUpdated.append((pin.id,
                         headID,
                         latitude,
                         longitude))

            else:
                if pin.HasDifferingContents(otherPin.GetContents()):
                    contents = pin.GetContents()
                    for typeID, qty in contents.iteritems():
                        pinContentsChanged.append((int(pin.id), int(typeID), int(qty)))

                    if len(contents) < 1:
                        pinContentsChanged.append((int(pin.id), -1, -1))
                if pin.HasDifferingState(otherPin):
                    pinStatesChanged.append([int(pin.id),
                     int(pin.activityState),
                     pin.lastRunTime,
                     getattr(pin, 'schematicID', -1),
                     getattr(pin, 'lastLaunchTime', None)])
                if pin.IsExtractor() and evetypes.GetGroupID(pin.typeID) == appConst.groupExtractionControlUnitPins:
                    if pin.HasDifferingProgram(otherPin):
                        progInfo = pin.GetProgramInformation()
                        if progInfo is not None:
                            programsUpdated.append(progInfo)
                        else:
                            programsDeleted.append(pin.id)
                    for headID, latitude, longitude in pin.heads:
                        otherHead = otherPin.FindHead(headID)
                        if otherHead is None or otherHead[1] != latitude or otherHead[2] != longitude:
                            headsUpdated.append((pin.id,
                             headID,
                             latitude,
                             longitude))

                    for headID, latitude, longitude in otherPin.heads:
                        if pin.FindHead(headID) is None:
                            headsDeleted.append((pin.id, headID))

        for otherPinID in otherColonyData.pins.iterkeys():
            if otherPinID not in self.pins:
                pinsDeleted.append(otherPinID)

        for linkID, linkObject in self.links.iteritems():
            if linkID not in otherColonyData.links:
                linksCreated.append((int(linkObject.endpoint1.id), int(linkObject.endpoint2.id), int(linkObject.level)))
            elif linkObject.level != otherColonyData.links[linkID].level:
                linksAltered.append((int(linkObject.endpoint1.id), int(linkObject.endpoint2.id), int(linkObject.level)))

        for linkID, linkObject in otherColonyData.links.iteritems():
            if linkID not in self.links:
                linksDeleted.append((int(linkObject.endpoint1.id), int(linkObject.endpoint2.id)))

        for routeID, route in self.routes.iteritems():
            if routeID not in otherColonyData.routes:
                waypoints = [None,
                 None,
                 None,
                 None,
                 None]
                for i, waypoint in enumerate(route.path[1:-1]):
                    waypoints[i] = int(waypoint)

                tempRouteID = route.routeID
                if type(tempRouteID) is not types.TupleType:
                    self.LogError('ColonyData::Diff - Created route does not have tuple ID?!', routeID)
                else:
                    tempRouteID = tempRouteID[1]
                routesCreated.append([int(tempRouteID),
                 int(route.GetSourcePinID()),
                 int(route.GetDestinationPinID()),
                 int(route.GetType()),
                 int(route.GetQuantity()),
                 waypoints[0],
                 waypoints[1],
                 waypoints[2],
                 waypoints[3],
                 waypoints[4]])

        for otherRouteID in otherColonyData.routes.iterkeys():
            if otherRouteID not in self.routes:
                routesDeleted.append(int(otherRouteID))

        levelUpgraded = None
        if otherColonyData.level != self.level:
            levelUpgraded = self.level
        diff = utillib.KeyVal(pinsCreated=pinsCreated, pinsDeleted=pinsDeleted, pinContentsChanged=pinContentsChanged, pinStatesChanged=pinStatesChanged, linksCreated=linksCreated, linksDeleted=linksDeleted, linksAltered=linksAltered, routesCreated=routesCreated, routesDeleted=routesDeleted, programsUpdated=programsUpdated, programsDeleted=programsDeleted, headsUpdated=headsUpdated, headsDeleted=headsDeleted, levelUpgraded=levelUpgraded)
        return diff

    def GetTypeAttribute(self, typeID, attributeID):
        if self.eventHandler is None:
            value = None
            for r in dogma.data.get_type_attributes(typeID):
                if r.attributeID == attributeID:
                    value = r.value

            if value is None and dogma.data.is_attribute(attributeID):
                value = dogma.data.get_attribute_default_value(attributeID)
            return value
        else:
            return self.eventHandler.GetTypeAttribute(typeID, attributeID)

    def GetECUPins(self):
        return self.GetPinsOfType(appConst.groupExtractionControlUnitPins)

    def GetProcessorPins(self):
        return self.GetPinsOfType(appConst.groupProcessPins)

    def GetStoragePins(self):
        return self.GetPinsOfType(appConst.groupStoragePins)

    def GetSpaceportPins(self):
        return self.GetPinsOfType(appConst.groupSpaceportPins)

    def GetPinsOfType(self, pinTypeID):
        pins = set()
        for pin in self.pins.itervalues():
            if evetypes.GetGroupID(pin.typeID) == pinTypeID:
                pins.add(pin)

        return pins

    def LogInfo(self, *args):
        if self.eventHandler is not None:
            self.eventHandler.LogInfo(*args)

    def LogWarn(self, *args):
        if self.eventHandler is not None:
            self.eventHandler.LogWarn(*args)

    def LogError(self, *args):
        if self.eventHandler is not None:
            self.eventHandler.LogError(*args)

    def LogNotice(self, *args):
        if self.eventHandler is not None:
            self.eventHandler.LogNotice(*args)

    def GetAllProcessorProducts(self):
        pins = self.GetProcessorPins()
        return self._GetAllProducts(pins)

    def GetAllECUProducts(self):
        pins = self.GetECUPins()
        return self._GetAllProducts(pins)

    def GetAllStoredProducts(self):
        pins = [ pin for pin in self.pins.values() if evetypes.GetGroupID(pin.typeID) in PINTYPES_WITH_STORAGE ]
        return self._GetAllContents(pins)

    def _GetAllProducts(self, pins):
        ret = defaultdict(int)
        for pin in pins:
            products = pin.GetProducts()
            for typeID, amount in products.iteritems():
                ret[typeID] += amount

        return ret

    def _GetAllContents(self, pins):
        ret = defaultdict(int)
        for pin in pins:
            content = pin.GetContents()
            for typeID, amount in content.iteritems():
                ret[typeID] += amount

        return ret

    def GetErrorsForStorage(self):
        pins = [ pin for pin in self.pins.values() if evetypes.GetGroupID(pin.typeID) in PINTYPES_WITH_STORAGE ]
        for pin in pins:
            if self.IsPinNeedingAttention(pin.id):
                return {None}

        return set()

    def GetErrorsForECUPins(self):
        pins = self.GetECUPins()
        return self._GetErrorsForProducts(pins)

    def GetErrorsForProcessors(self):
        pins = self.GetProcessorPins()
        return self._GetErrorsForProducts(pins)

    def _GetErrorsForProducts(self, pins):
        productsWithErrors = set()
        for pin in pins:
            products = pin.GetProducts()
            if not products:
                productsWithErrors.add(None)
            elif self.IsPinNeedingAttention(pin.id):
                for typeID in products.iterkeys():
                    productsWithErrors.add(typeID)

        return productsWithErrors
