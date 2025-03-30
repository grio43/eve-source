#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\components\autoMoonMiner.py
import logging
from spacecomponents import Component
from spacecomponents.client import MSG_ON_SLIM_ITEM_UPDATED, MSG_ON_LOAD_OBJECT
from spacecomponents.client.display import EntryData, CYCLE_TIME_ICON
from eve.client.script.ui.control.entries.header import Header
from eve.client.script.ui.control.entries.label_text import LabelTextSides
from carbon.common.script.util.format import FmtTimeInterval
import carbon.common.script.util.mathCommon as mathCommon
from carbon.common.lib.const import SEC
from moonmining.autoMoonMining.common import REAGENT_FUEL_TYPE, OPERATING_CTRL_MAPPINGS, UPKEEP_CTRL_MAPPINGS
import evetypes
import gametime
import geo2
logger = logging.getLogger(__name__)

class AutoMoonMiner(Component):

    def __init__(self, itemID, typeID, attributes, componentRegistry):
        Component.__init__(self, itemID, typeID, attributes, componentRegistry)
        self.SubscribeToMessage(MSG_ON_LOAD_OBJECT, self.OnLoadObject)
        self.SubscribeToMessage(MSG_ON_SLIM_ITEM_UPDATED, self.OnSlimItemUpdated)
        self.lastHarvestTime = None
        self.moonID = None
        self.itemID = None

    def _UpdateEffect(self, info = None):
        fxSequencer = sm.GetService('FxSequencer')
        ballActivations = fxSequencer.GetAllBallActivations(self.itemID)
        for activation in ballActivations:
            if activation.effect and activation.guid == 'effects.AutoMoonMinerBeam':
                activation.effect.CheckEndPoints()
                if info is not None:
                    activation.effect.UpdateGraphicInfo(info)

    def _ActivateBeam(self, slimItem, isFiring):
        if self.model is not None and self.moonID:
            fxSequencer = sm.GetService('FxSequencer')
            info = {'isFiring': isFiring,
             'timeAddedToSpace': slimItem.timeAddedToSpace}
            fxSequencer.OnSpecialFX(self.itemID, None, None, self.moonID, None, 'effects.AutoMoonMinerBeam', 0, True, None, graphicInfo=info)
            self.model.SetControllerVariable('isFiring', info['isFiring'])
            self._UpdateEffect(info)
            self.lastHarvestTime = slimItem.component_autoMoonMiner_lastHarvest

    def _RotateModelToFaceMoon(self, ball):
        yaw, pitch, roll = geo2.QuaternionRotationGetYawPitchRoll(self.model.rotationCurve.value)
        moonBall = ball.ballpark.balls[self.moonID]
        moonCenter = (moonBall.x, moonBall.y, moonBall.z)
        modelPosition = (ball.x, ball.y, ball.z)
        yaw, pitch = mathCommon.GetYawAndPitchAnglesRad(modelPosition, moonCenter)
        quat = geo2.QuaternionRotationSetYawPitchRoll(-yaw, -pitch, roll)
        self.model.rotationCurve.value = quat

    def _UpdateModel(self, ball):
        try:
            self.model = ball.GetModel()
        except AttributeError:
            return

        if self.model and self.moonID:
            self._RotateModelToFaceMoon(ball)

    def OnLoadObject(self, ball):
        if ball is not None:
            ballPark = ball.ballpark
            slimItem = ballPark.slimItems.get(ball.id)
            self.itemID = slimItem.itemID
            if slimItem is not None and hasattr(slimItem, 'moonID'):
                self.moonID = slimItem.moonID
            self._UpdateModel(ball)
            self._UpdateEffect()

    def _UpdateState(self, controllerVariable, slimItemVariable, mappings):
        slimItemState = slimItemVariable or 0
        if slimItemVariable in mappings:
            enumValue = mappings.index(slimItemState)
            self.model.SetControllerVariable(controllerVariable, enumValue)

    def OnSlimItemUpdated(self, slimItem):
        self.moonID = slimItem.moonID
        self.itemID = slimItem.itemID
        ball = sm.GetService('michelle').GetBall(self.itemID)
        self._UpdateModel(ball)
        if self.model:
            timeNow = gametime.GetWallclockTime()
            if slimItem.component_autoMoonMiner_lastHarvest is not None:
                if (self.lastHarvestTime is None or self.lastHarvestTime != slimItem.component_autoMoonMiner_lastHarvest) and timeNow > slimItem.component_autoMoonMiner_lastHarvest:
                    self._ActivateBeam(slimItem, 1.0)
            else:
                self._UpdateEffect()
            self._UpdateState('operatingState', slimItem.state, OPERATING_CTRL_MAPPINGS)
            self._UpdateState('upkeepState', slimItem.upkeepState, UPKEEP_CTRL_MAPPINGS)

    @staticmethod
    def GetAttributeInfo(typeID, attributes, instance, localization):
        attributeEntries = [EntryData(Header, localization.GetByLabel('UI/Moonmining/AutoMoonMiner/InfoAttributesHeader')),
         EntryData(LabelTextSides, localization.GetByLabel('UI/Moonmining/AutoMoonMiner/MiningEfficiency'), localization.GetByLabel('UI/Common/Formatting/PercentageDecimal', percentage=attributes.miningEfficiency * 100)),
         EntryData(LabelTextSides, localization.GetByLabel('UI/Moonmining/AutoMoonMiner/MiningCycleTime'), FmtTimeInterval(long(attributes.miningCycleTime * SEC), breakAt='sec'), iconID=CYCLE_TIME_ICON),
         EntryData(LabelTextSides, localization.GetByLabel('UI/Moonmining/AutoMoonMiner/ReagentsConsumedPerCycle'), str(attributes.reagentsConsumedPerCycle)),
         EntryData(LabelTextSides, localization.GetByLabel('UI/Moonmining/AutoMoonMiner/ReagentType'), evetypes.GetName(REAGENT_FUEL_TYPE), iconID=evetypes.GetIconID(REAGENT_FUEL_TYPE), typeID=REAGENT_FUEL_TYPE)]
        return attributeEntries
