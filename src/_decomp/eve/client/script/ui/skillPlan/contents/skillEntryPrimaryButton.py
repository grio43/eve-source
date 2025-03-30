#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\contents\skillEntryPrimaryButton.py
from carbonui import ButtonStyle
from carbonui.control.button import Button
from carbonui.uicore import uicore
from eve.client.script.ui.shared.cloneGrade import ORIGIN_SKILLPLAN
from eve.client.script.ui.tooltips import tooltipUtil
from eveexceptions import UserError
from itertoolsext.Enum import Enum
from localization import GetByLabel
from localization.formatters import FormatNumeric
from skills import skillConst

@Enum

class State(object):
    OMEGA_MISSING = 'REQUIRES_OMEGA'
    OMEGA_MISSING_FOR_NEXT_LEVEL = 'OMEGA_MISSING_FOR_NEXT_LEVEL'
    SKILLBOOK_MISSING = 'SKILLBOOK_MISSING'
    IN_QUEUE_CAN_REMOVE = 'IN_QUEUE_CAN_REMOVE'
    IN_QUEUE_CANT_REMOVE = 'IN_QUEUE_CANT_REMOVE'
    TRAINED = 'FULLY_TRAINED'
    CAN_ADD_TO_QUEUE = 'CAN_ADD_TO_QUEUE'
    ALL_IN_QUEUE = 'ALL_IN_QUEUE'


class SkillEntryPrimaryButton(Button):
    default_iconSize = 20
    STYLE_PER_STATE = {State.OMEGA_MISSING: ButtonStyle.MONETIZATION,
     State.OMEGA_MISSING_FOR_NEXT_LEVEL: ButtonStyle.MONETIZATION,
     State.SKILLBOOK_MISSING: ButtonStyle.DANGER,
     State.IN_QUEUE_CAN_REMOVE: ButtonStyle.NORMAL,
     State.IN_QUEUE_CANT_REMOVE: ButtonStyle.NORMAL,
     State.TRAINED: ButtonStyle.NORMAL,
     State.CAN_ADD_TO_QUEUE: ButtonStyle.NORMAL,
     State.ALL_IN_QUEUE: ButtonStyle.NORMAL}
    HINT_PER_STATE = {State.OMEGA_MISSING: 'UI/CloneState/RequiresOmegaClone',
     State.OMEGA_MISSING_FOR_NEXT_LEVEL: 'UI/SkillPlan/RequiresOmegaCloneForNextLevel',
     State.SKILLBOOK_MISSING: 'UI/SkillPlan/ClickToBuyMissingSkillAndRequirements',
     State.IN_QUEUE_CAN_REMOVE: 'UI/SkillPlan/RemoveFromQueue',
     State.IN_QUEUE_CANT_REMOVE: 'UI/SkillPlan/RemoveFromQueueLocked',
     State.TRAINED: 'UI/SkillPlan/AlreadyTrained',
     State.ALL_IN_QUEUE: 'UI/SkillPlan/AllInQueue',
     State.CAN_ADD_TO_QUEUE: 'UI/SkillPlan/AddToQueue'}
    TEXTUREPATH_PER_STATE = {State.OMEGA_MISSING: 'res:/UI/Texture/classes/Seasons/omega_32x32.png',
     State.OMEGA_MISSING_FOR_NEXT_LEVEL: 'res:/UI/Texture/classes/Seasons/omega_32x32.png',
     State.SKILLBOOK_MISSING: 'res:/UI/Texture/WindowIcons/skills.png',
     State.IN_QUEUE_CAN_REMOVE: 'res:/UI/Texture/classes/SkillPlan/buttonIcons/removeIcon.png',
     State.IN_QUEUE_CANT_REMOVE: 'res:/UI/Texture/classes/SkillPlan/buttonIcons/removeIcon.png',
     State.TRAINED: 'res:/UI/Texture/classes/SkillPlan/buttonIcons/checkMark.png',
     State.ALL_IN_QUEUE: 'res:/UI/Texture/classes/SkillPlan/buttonIcons/buttonIconPlus.png',
     State.CAN_ADD_TO_QUEUE: 'res:/UI/Texture/classes/SkillPlan/buttonIcons/buttonIconPlus.png'}
    DISABLED_STATES = [State.IN_QUEUE_CANT_REMOVE, State.TRAINED, State.ALL_IN_QUEUE]

    def ApplyAttributes(self, attributes):
        if 'func' not in attributes:
            attributes['func'] = self._OnClick
        super(SkillEntryPrimaryButton, self).ApplyAttributes(attributes)
        self.controller = attributes.get('skillController', None)
        self.primaryButtonState = State.CAN_ADD_TO_QUEUE
        self.onOmegaMissingActionCallback = attributes.get('onOmegaMissingAction', self.OnOmegaMissingAction)
        self.onSkillbookMissingActionCallback = attributes.get('onSkillbookMissingAction', self.OnSkillbookMissingAction)
        self.onAlreadyTrainedActionCallback = attributes.get('onAlreadyTrainedAction', self.OnAlreadyTrainedAction)
        self.onAddToQueueActionCallback = attributes.get('onAddToQueueAction', self.OnAddToQueueAction)
        self.onRemoveFromQueueActionCallback = attributes.get('onRemoveFromQueueAction', self.OnRemoveFromQueueAction)
        self.onCantRemoveFromQueueActionCallback = attributes.get('onCantRemoveFromQueueAction', self.OnCantRemoveFromQueueAction)
        self.onAllInQueueActionCallback = attributes.get('onAllInQueueAction', self.OnAllInQueueAction)
        self.onDefaultActionCallback = attributes.get('onDefaultAction', self.OnDefaultAction)
        self.UpdateState()

    def UpdateState(self):
        if not self.controller:
            return
        self.primaryButtonState = self._GetState()
        if self.primaryButtonState in self.DISABLED_STATES:
            self.Disable()
        else:
            self.Enable()
        self.texturePath = self.TEXTUREPATH_PER_STATE[self.primaryButtonState]
        self.style = self.STYLE_PER_STATE[self.primaryButtonState]

    def GetTooltipText(self):
        hintLabel = self.HINT_PER_STATE[self.primaryButtonState]
        if self.primaryButtonState == State.CAN_ADD_TO_QUEUE:
            hint = GetByLabel(hintLabel, skillLevel=self._GetSkillLevel() or 1)
        else:
            hint = GetByLabel(hintLabel)
        return hint

    def LoadTooltipPanel(self, panel, *args):
        if uicore.IsDragging():
            return
        panel.LoadStandardSpacing()
        panel.columns = 2
        text = self.GetTooltipText()
        panel.AddMediumHeader(text=text)
        if self.primaryButtonState == State.CAN_ADD_TO_QUEUE:
            self._AddSkillPointAndTrainingTime(panel)

    def _AddSkillPointAndTrainingTime(self, panel):
        nextLevel = self._GetSkillLevel() or 1
        self._AddSPRequired(nextLevel, panel)
        self._AddSPPerMinute(panel)

    def _AddSPRequired(self, nextLevel, panel):
        panel.AddLabelMedium(text=GetByLabel('UI/Skills/SkillPointsRequired'))
        skillPoints = self.controller.GetSkillPointsMissingForLevel(nextLevel)
        panel.AddLabelMedium(text=FormatNumeric(skillPoints, useGrouping=True))

    def _AddSPPerMinute(self, panel):
        spPerMin = sm.GetService('skills').GetSkillpointsPerMinute(self.controller.GetTypeID())
        panel.AddLabelMedium(text=GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/SpPerMinute', spPerMin=spPerMin), colSpan=2)

    def _GetSkillLevel(self):
        return self.controller.GetNextLevelToAddToQueue()

    def _GetState(self):
        if self.controller.IsFullyTrained():
            return State.TRAINED
        if not sm.GetService('cloneGradeSvc').IsOmega() and not self.controller.IsCloneStateMet():
            return State.OMEGA_MISSING
        restrictLevel = self.controller.GetCurrCloneStateMaxLevel()
        levelToCheck = max(self.controller.GetMyLevel(), sm.GetService('skillqueue').FindHighestLevelInQueue(self.controller.GetTypeID()))
        levelToCheck = min(levelToCheck + 1, skillConst.skill_max_level)
        if levelToCheck > restrictLevel:
            return State.OMEGA_MISSING_FOR_NEXT_LEVEL
        if not self.controller.IsInjected() or not self.controller.IsAllPrereqsInjected():
            return State.SKILLBOOK_MISSING
        queueLevel = sm.GetService('skillqueue').FindHighestLevelInQueue(self.controller.GetTypeID())
        if queueLevel == skillConst.skill_max_level:
            return State.ALL_IN_QUEUE
        return State.CAN_ADD_TO_QUEUE

    def _OnClick(self, *args):
        if self.primaryButtonState == State.OMEGA_MISSING:
            self.onOmegaMissingActionCallback()
        elif self.primaryButtonState == State.OMEGA_MISSING_FOR_NEXT_LEVEL:
            self.onOmegaMissingActionCallback()
        elif self.primaryButtonState == State.SKILLBOOK_MISSING:
            self.onSkillbookMissingActionCallback()
        elif self.primaryButtonState == State.TRAINED:
            self.onAlreadyTrainedActionCallback()
        elif self.primaryButtonState == State.IN_QUEUE_CANT_REMOVE:
            self.onCantRemoveFromQueueActionCallback()
        elif self.primaryButtonState == State.IN_QUEUE_CAN_REMOVE:
            self.onRemoveFromQueueActionCallback()
        elif self.primaryButtonState == State.CAN_ADD_TO_QUEUE:
            self.onAddToQueueActionCallback()
        else:
            self.onDefaultActionCallback()

    def OnClick(self, *args):
        super(SkillEntryPrimaryButton, self).OnClick(*args)
        tooltipUtil.RefreshTooltipForOwner(self)

    def OnOmegaMissingAction(self):
        uicore.cmd.OpenCloneUpgradeWindow(ORIGIN_SKILLPLAN)

    def OnSkillbookMissingAction(self):
        self.controller.BuyAllRequiredSkillbooks()

    def OnAlreadyTrainedAction(self):
        pass

    def OnAddToQueueAction(self):
        sm.GetService('skillqueue').AddSkillAndRequirementsToQueue(self.controller.GetTypeID(), skillLevel=None)

    def OnRemoveFromQueueAction(self):
        levelToRemove = sm.GetService('skillqueue').FindHighestLevelInQueue(self.controller.GetTypeID())
        sm.GetService('skillqueue').RemoveSkillsFromQueue([(self.controller.GetTypeID(), levelToRemove)])

    def OnCantRemoveFromQueueAction(self):
        pass

    def OnAllInQueueAction(self):
        pass

    def OnDefaultAction(self):
        sm.GetService('skillqueue').AddSkillAndRequirementsToQueue(self.controller.GetTypeID(), skillLevel=None)


class SkillLevelEntryPrimaryButton(SkillEntryPrimaryButton):

    def ApplyAttributes(self, attributes):
        self.level = attributes.get('skillLevel', None)
        super(SkillLevelEntryPrimaryButton, self).ApplyAttributes(attributes)

    def _GetState(self):
        if not sm.GetService('cloneGradeSvc').IsOmega() and self.level > self.controller.GetCurrCloneStateMaxLevel():
            return State.OMEGA_MISSING
        if not self.controller.IsInjected() or not self.controller.IsAllPrereqsInjected():
            return State.SKILLBOOK_MISSING
        if self.controller.IsInQueue(level=self.level):
            try:
                sm.GetService('skillqueue').CheckCanRemoveSkillFromQueue(self.controller.GetTypeID(), self.level)
            except UserError:
                return State.IN_QUEUE_CANT_REMOVE

            return State.IN_QUEUE_CAN_REMOVE
        if self.controller.GetMyLevel() >= self.level:
            return State.TRAINED
        return State.CAN_ADD_TO_QUEUE

    def _GetSkillLevel(self):
        return self.level or super(SkillLevelEntryPrimaryButton, self)._GetSkillLevel()

    def OnAddToQueueAction(self):
        sm.GetService('skillqueue').AddSkillAndRequirementsToQueue(self.controller.GetTypeID(), skillLevel=self.level)

    def OnRemoveFromQueueAction(self):
        sm.GetService('skillqueue').RemoveSkillsFromQueue([(self.controller.GetTypeID(), self.level)])

    def OnDefaultAction(self):
        sm.GetService('skillqueue').AddSkillAndRequirementsToQueue(self.controller.GetTypeID(), skillLevel=self.level)
