#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\planet\clientColony.py
from eve.common.lib import appConst
from eve.common.script.planet.baseColony import BaseColony
from eve.common.script.planet.surfacePoint import SurfacePoint
import eve.common.script.util.planetCommon as planetCommon
import blue
import localization
import evetypes
from eve.common.script.util.eveFormat import FmtISK
from eveexceptions import UserError

class ClientColony(BaseColony):
    __name__ = 'ClientColony'

    def Init(self):
        BaseColony.Init(self)
        self.nextTemporaryPinID = 0
        self.nextTemporaryRouteID = 0
        self.cumulativePinCreationCost = 0L
        self.cumulativeUpgradeCost = 0L

    def ResetPinCreationCost(self):
        self.cumulativePinCreationCost = 0L
        self.cumulativeUpgradeCost = 0L

    def RemoveCreationCost(self, typeID):
        self.cumulativePinCreationCost -= evetypes.GetBasePrice(typeID)
        if self.cumulativePinCreationCost < 0:
            self.cumulativePinCreationCost = 0L

    def GetTemporaryPinID(self):
        self.nextTemporaryPinID += 1
        return (1, self.nextTemporaryPinID)

    def GetTemporaryRouteID(self):
        self.nextTemporaryRouteID += 1
        return (2, self.nextTemporaryRouteID)

    def GetLinksAttachedToPin(self, pinID):
        if pinID not in self.linksByPin:
            return []
        return self.linksByPin[pinID]

    def SetColonyData(self, newData):
        BaseColony.SetColonyData(self, newData)

    def PostValidateCreatePin(self, charID, typeID, latitude, longitude):
        skillsSvc = sm.GetService('skills')
        if evetypes.GetGroupID(typeID) != appConst.groupCommandPins:
            basePrice = evetypes.GetBasePrice(typeID)
            totalIskCost = self.cumulativePinCreationCost + basePrice
            currentBalance = sm.GetService('wallet').GetWealth()
            if totalIskCost > currentBalance:
                raise UserError('CannotBuildNotEnoughCash', {'cost': FmtISK(basePrice)})
            self.cumulativePinCreationCost += basePrice
        else:
            planetRows = sm.GetService('planetSvc').GetMyPlanets()
            if len(planetRows) > 0 and skillsSvc.GetEffectiveLevel(appConst.typeOmnipotent) is None:
                deploymentSkillLevel = skillsSvc.GetEffectiveLevel(appConst.typeInterplanetaryConsolidation)
                if deploymentSkillLevel is None:
                    raise UserError('CannotPlaceCommandCenterNotEnoughSkill', {'maxPlanets': 1})
                elif deploymentSkillLevel < len(planetRows):
                    raise UserError('CannotPlaceCommandCenterNotEnoughSkill', {'maxPlanets': len(planetRows)})
        requiredSkills = sm.GetService('skills').GetRequiredSkills(typeID)
        lackingSkills = []
        for skillTypeID, requiredLevel in requiredSkills.iteritems():
            myLevel = skillsSvc.GetEffectiveLevel(skillTypeID)
            if myLevel < requiredLevel:
                if requiredLevel:
                    levelTxt = localization.GetByLabel('UI/PI/Common/SkillLevel', skillLevel=requiredLevel)
                else:
                    levelTxt = ''
                lacked = localization.GetByLabel('UI/PI/Common/SkillNameAndLevel', skillName=evetypes.GetName(skillTypeID), skillLevel=levelTxt)
                lackingSkills.append(lacked)

        if len(lackingSkills) > 0:
            raise UserError('CannotPlacePinNotEnoughSkill', {'requiredSkills': ', '.join(lackingSkills),
             'itemName': evetypes.GetName(typeID)})

    def PostValidateRemovePin(self, charID, pinID):
        pin = self.GetPin(pinID)
        typeID = pin.typeID
        if evetypes.GetGroupID(typeID) == appConst.groupExtractorPins:
            self.cumulativePinCreationCost -= evetypes.GetBasePrice(typeID)

    def PostValidateCommandCenterUpgrade(self, level):
        skillLevel = sm.GetService('skills').GetEffectiveLevel(appConst.typeCommandCenterUpgrade)
        if level > skillLevel:
            raise UserError('CantUpgradeCommandCenterSkillRequired', {'skillName': (appConst.UE_TYPEID, appConst.typeCommandCenterUpgrade),
             'currentLevel': skillLevel,
             'requestedLevel': level})
        cost = planetCommon.GetUpgradeCost(self.colonyData.level, level)
        self.cumulativeUpgradeCost += cost

    def PostValidateInstallProgram(self, pinID, typeID, headRadius):
        pin = self.GetPin(pinID)
        if not pin.inEditMode:
            currentTime = blue.os.GetWallclockTime()
            pin.CanInstallProgram(currentTime)

    def ValidateAddExtractorHead(self, pinID, headID):
        if self.colonyData is None:
            raise RuntimeError('Unable to validate new extractor head - no colony data')
        pin = self.GetPin(pinID)
        if not pin:
            raise UserError('PinDoesNotExist')
        if not pin.IsExtractor():
            raise UserError('PinDoesNotHaveHeads')
        if pin.FindHead(headID) is not None:
            raise UserError('CannotAddHeadAlreadyExists')
        if len(pin.heads) > planetCommon.ECU_MAX_HEADS:
            raise UserError('CannotPlaceHeadLimitReached')
        cpuDelta = pin.GetCpuUsage(numHeads=len(pin.heads) + 1) - pin.GetCpuUsage()
        powerDelta = pin.GetPowerUsage(numHeads=len(pin.heads) + 1) - pin.GetPowerUsage()
        if cpuDelta + self.colonyData.GetColonyCpuUsage() > self.colonyData.GetColonyCpuSupply():
            raise UserError('CannotAddToColonyCPUUsageExceeded', {'typeName': localization.GetByLabel('UI/PI/Common/ExtractorHead')})
        if powerDelta + self.colonyData.GetColonyPowerUsage() > self.colonyData.GetColonyPowerSupply():
            raise UserError('CannotAddToColonyPowerUsageExceeded', {'typeName': localization.GetByLabel('UI/PI/Common/ExtractorHead')})

    def OnPinRemoved(self, pinID):
        BaseColony.OnPinRemoved(self, pinID)

    def GetTypeAttribute(self, typeID, attributeID):
        return sm.GetService('godma').GetTypeAttribute2(typeID, attributeID)

    def Dijkstra(self, sourcePin, destinationPin):
        D = {}
        P = {}
        Q = planetCommon.priority_dict()
        Q[sourcePin] = 0.0
        while len(Q) > 0:
            vPin = Q.smallest()
            D[vPin] = Q[vPin]
            if vPin == destinationPin:
                break
            Q.pop_smallest()
            for wDestinationID in self.colonyData.GetLinksForPin(vPin.id):
                wLink = self.GetLink(vPin.id, wDestinationID)
                wPin = self.GetPin(wDestinationID)
                vwLength = D[vPin] + self._GetLinkWeight(wLink, wPin, vPin)
                if wPin in D:
                    if vwLength < D[wPin]:
                        raise ValueError, 'Dijkstra: found better path to already-final vertex'
                elif wPin not in Q or vwLength < Q[wPin]:
                    Q[wPin] = vwLength
                    P[wPin] = vPin

        return (D, P)

    def _GetLinkWeight(self, link, pinA, pinB):
        spA = SurfacePoint(radius=1.0, theta=pinA.longitude, phi=pinA.latitude)
        spB = SurfacePoint(radius=1.0, theta=pinB.longitude, phi=pinB.latitude)
        return spA.GetDistanceToOther(spB)

    def FindShortestPath(self, sourcePin, destinationPin):
        if sourcePin is None or destinationPin is None:
            return
        if sourcePin == destinationPin:
            return []
        distanceDict, predecessorDict = self.Dijkstra(sourcePin, destinationPin)
        if destinationPin not in distanceDict or destinationPin not in predecessorDict:
            return []
        path = []
        currentPin = destinationPin
        while currentPin is not None:
            path.append(currentPin.id)
            if currentPin is sourcePin:
                break
            if currentPin not in predecessorDict:
                raise RuntimeError("CurrentPin not in predecessor dict. There's no path. How did we get here?!")
            currentPin = predecessorDict[currentPin]

        path.reverse()
        if path[0] != sourcePin.id:
            return []
        return path

    def FindShortestPathIDs(self, sourcePinID, destinationPinID):
        return self.FindShortestPath(self.GetPin(sourcePinID), self.GetPin(destinationPinID))
