#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\components\underConstruction.py
import logging
import mathext
import evetypes
from spacecomponents.common.componentConst import UNDER_CONSTRUCTION
from inventorycommon.typeHelpers import GetAveragePrice
from spacecomponents import Component
from spacecomponents.client import MSG_ON_SLIM_ITEM_UPDATED, MSG_ON_LOAD_OBJECT, MSG_ON_ADDED_TO_SPACE, MSG_ON_REMOVED_FROM_SPACE
import uthread
import blue
from spacecomponents.client.ui.underConstruction.bracket import UnderContructionBracket
logger = logging.getLogger(__name__)

class UnderConstruction(Component):

    def __init__(self, itemID, typeID, attributes, componentRegistry):
        Component.__init__(self, itemID, typeID, attributes, componentRegistry)
        self.SubscribeToMessage(MSG_ON_SLIM_ITEM_UPDATED, self.OnSlimItemUpdated)
        self.SubscribeToMessage(MSG_ON_LOAD_OBJECT, self.OnLoadObject)
        self.SubscribeToMessage(MSG_ON_ADDED_TO_SPACE, self.OnAddedToSpace)
        self.SubscribeToMessage(MSG_ON_REMOVED_FROM_SPACE, self.OnRemovedFromSpace)
        self._bracket_ui = None
        self.itemID = itemID
        self.completed = False
        self.progressDict = {}
        self.estimatedProgress = 0
        self.currentProgress = 0
        self.estimatedValueProgress = None
        self.buildEffectThread = None
        self.buildAmountControllerVariable = None

    def OnAddedToSpace(self, slimItem):
        self.progressDict = slimItem.component_underConstruction_progress or {}
        uthread.new(self._AddUiToSpace, slimItem)

    def _AddUiToSpace(self, slimItem):
        if self._bracket_ui is None:
            self._bracket_ui = UnderContructionBracket(slimItem.itemID, slimItem.typeID)

    def ReloadUI(self):
        if self._bracket_ui:
            self._bracket_ui.close()
            self._bracket_ui = None
        slimItem = sm.GetService('michelle').GetItem(self.itemID)
        self._bracket_ui = UnderContructionBracket(slimItem.itemID, slimItem.typeID)

    def OnSlimItemUpdated(self, slimItem):
        progress = slimItem.component_underConstruction_progress or {}
        self.completed = slimItem.component_underConstruction_completed or False
        self.CalculateProgress(slimItem)
        sm.ScatterEvent('OnUnderConstructionUpdated', slimItem.itemID, progress, self.GetEstimatedValueProgress(), self.completed)
        ball = sm.GetService('michelle').GetBall(self.itemID)
        if ball is not None:
            self._UpdateModel(ball)
        self.progressDict = progress

    def OnLoadObject(self, ball):
        bp = sm.GetService('michelle').GetBallpark()
        if bp is None:
            return
        slimItem = bp.GetInvItem(self.itemID)
        self.CalculateProgress(slimItem)
        self.currentProgress = self.estimatedProgress
        ball.SetControllerVariable('isBuilt', 1.0)
        ball.SetControllerVariable('isBuildByValue', 1.0)
        ball.SetControllerVariable('buildAmount', self.estimatedProgress)
        if ball.model is not None:
            ball.model.StartControllers()
        self._UpdateModel(ball)

    def CalculateProgress(self, slimItem):
        progress = slimItem.component_underConstruction_progress
        if progress is None or not len(progress) > 0:
            return
        self._CalculateVisualProgress(progress)
        self._CalculatePriceProgress(progress)

    def _CalculateVisualProgress(self, progress):
        estimateByComponentSum = sum(list(progress.values())) / len(progress)
        self.estimatedProgress = min(1.0, max(0.0, estimateByComponentSum))

    def _CalculatePriceProgress(self, progress):
        valueOfComponents = 0
        totalValueOfNeeded = 0
        try:
            for typeID, inputInfo in self.attributes.inputItems.iteritems():
                typePrice = GetAveragePrice(typeID)
                if not typePrice:
                    return
                neededQty = inputInfo.qtyRequired
                totalValueOfNeeded += typePrice * neededQty
                typeProgress = progress.get(typeID, 0)
                currentQty = typeProgress * neededQty
                valueOfComponents += currentQty * typePrice

            if totalValueOfNeeded:
                self.estimatedValueProgress = float(valueOfComponents) / totalValueOfNeeded
            else:
                self.estimatedValueProgress = None
        except StandardError as e:
            logger.exception('Failed _CalculatePriceProgress')

    def _UpdateModel(self, ball):
        if not hasattr(ball, 'model') or ball.model is None or self.estimatedProgress == self.currentProgress:
            return
        structureController = ball.model.controllers.FindByName('structure')
        if structureController is not None:
            targetLerpVariable = structureController.variables.FindByName('buildAmount')
            if targetLerpVariable is not None:
                self.buildAmountControllerVariable = targetLerpVariable
        if self.buildAmountControllerVariable is not None and not self.buildEffectThread:
            self.buildEffectThread = uthread.new(self.BuildEffectThread)

    def BuildEffectThread(self):
        try:
            while True:
                currentDifference = self.estimatedProgress - self.currentProgress
                if abs(currentDifference) < 0.01 or self.buildAmountControllerVariable is None:
                    self.buildAmountControllerVariable.value = self.estimatedProgress
                    break
                lerpSpeed = 0.005
                frameRateAdjustment = 60 / blue.os.fps
                adjustedLerpSpeed = lerpSpeed * frameRateAdjustment
                self.currentProgress = self.currentProgress + currentDifference * adjustedLerpSpeed
                self.buildAmountControllerVariable.value = self.currentProgress
                blue.synchro.Yield()

        finally:
            self.currentProgress = self.estimatedProgress
            self.buildAmountControllerVariable = None
            self.buildEffectThread = None

    def GetEstimatedValueProgress(self):
        if self.estimatedValueProgress is None:
            return self.estimatedProgress
        return self.estimatedValueProgress

    def OpenUnderConstructionWnd(self):
        from eve.client.script.ui.shared.underConstruction.underConstructionWnd import UnderConstructionWnd
        windowID = 'underConstructionWnd_%s' % self.itemID
        wnd = UnderConstructionWnd.GetIfOpen(windowID=windowID)
        if wnd and not wnd.destroyed:
            wnd.Maximize()
        else:
            UnderConstructionWnd.Open(windowID=windowID, itemID=self.itemID)

    def OnRemovedFromSpace(self):
        if self._bracket_ui:
            self._bracket_ui.close()
            self._bracket_ui = None

    def DepositItemsFromShip(self, typeAndQty):
        remoteBallpark = sm.GetService('michelle').GetRemotePark()
        failedToMove = remoteBallpark.CallComponentFromClient(self.itemID, UNDER_CONSTRUCTION, 'DepositItemsFromShip', typeAndQty=typeAndQty)
        return failedToMove
