#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\view\hangarBehaviours\capitalHangarBehaviours.py
import math
import evetypes
import geo2
import trinity
from eve.client.script.ui.view.hangarBehaviours.baseHangarBehaviours import BaseHangarShipBehaviour, BaseHangarShipDroneBehaviour
from eve.common.lib import appConst as const

class CapitalHangarShipBehaviour(BaseHangarShipBehaviour):

    def SetAnchorPoint(self, hangarModel, hangarScene):
        if hangarModel is None:
            self.log.error('CapitalHangarShipBehaviour.SetAnchorPoint: Setting anchor point when scene is None')
            return
        anchorPointLocatorSets = [ locatorSet for locatorSet in getattr(hangarModel, 'locatorSets', []) if locatorSet.name == 'anchorpoint' ]
        if len(anchorPointLocatorSets) > 0:
            if len(getattr(anchorPointLocatorSets[0], 'locators', [])) > 0:
                self.shipAnchorPoint = anchorPointLocatorSets[0].locators[0][0]
                return
        self.log.warning('CapitalHangarShipBehaviour.SetAnchorPoint: Could not find anchor point')

    def PlaceShip(self, model, typeID):
        model.translationCurve = trinity.Tr2TranslationAdapter()
        trinity.WaitForResourceLoads()
        self.endPos = self.GetShipCenter(model, typeID)
        model.translationCurve.value = self.endPos
        self.ApplyShipBobbing(model, (0.0, model.translationCurve.value[1], 0.0), (0.0, 250.0, 0.0), model.GetBoundingSphereRadius())

    def GetShipCenter(self, model, typeID):
        localBB = model.GetLocalBoundingBox()
        width = abs(localBB[0][0])
        if evetypes.GetGroupID(typeID) == const.groupTitan:
            width += 2000
        return geo2.Vec3Add(self.shipAnchorPoint, (width, 0.0, 0.0))

    def GetAnimEndPosition(self):
        return self.endPos

    def GetAnimStartPosition(self):
        return self.endPos


class CapitalHangarDroneBehaviour(BaseHangarShipDroneBehaviour):

    def SetRepairDroneCount(self, boundingRadius):
        count = int(math.ceil(boundingRadius / 60.0))
        if self.repairDroneBehaviourGroup:
            self.repairDroneBehaviourGroup.SetCount(count)
