#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\contents\SkillPlanContentsSkillEntry.py
from carbonui import uiconst
from eve.client.script.ui.shared.tooltip.skill import LoadSkillEntryTooltipInfoOnly
from eve.client.script.ui.skillPlan.contents.skillEntryPrimaryButton import SkillLevelEntryPrimaryButton
from eve.client.script.ui.skillPlan.contents.skillPlanSkillEntry import SkillPlanSkillEntry
from signals import Signal

class SkillPlanContentsSkillEntry(SkillPlanSkillEntry):

    def ApplyAttributes(self, attributes):
        super(SkillPlanContentsSkillEntry, self).ApplyAttributes(attributes)
        self.onSkillAddedToQueue = Signal('SkillPlanSkillEntry_onSkillAddedToQueue')
        self.primaryButton = SkillLevelEntryPrimaryButton(parent=self, align=uiconst.TORIGHT, iconAlign=uiconst.CENTER, iconLeft=0, fixedwidth=36, padRight=2, skillController=self.controller, skillLevel=self.level, onAddToQueueActionCallback=self.OnAddToQueuePrimaryAction, onDefaultActionCallback=self.OnDefaultPrimaryAction, idx=0)
        self.primaryButton.UpdateState()

    def OnAddToQueuePrimaryAction(self):
        sm.GetService('skillqueue').AddSkillToQueue(self.typeID, skillLevel=self.level)
        self.onSkillAddedToQueue(self.typeID, self.level)

    def OnDefaultPrimaryAction(self):
        sm.GetService('skillqueue').AddSkillAndRequirementsToQueue(self.typeID, skillLevel=self.level)
        self.onSkillAddedToQueue(self.typeID, self.level)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        LoadSkillEntryTooltipInfoOnly(tooltipPanel, self.typeID)

    def GetTooltipPointer(self):
        return uiconst.POINT_RIGHT_2

    def Refresh(self):
        super(SkillPlanContentsSkillEntry, self).Refresh()
        self.primaryButton.UpdateState()
