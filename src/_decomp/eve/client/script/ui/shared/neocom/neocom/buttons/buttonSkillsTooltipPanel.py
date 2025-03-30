#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\neocom\buttons\buttonSkillsTooltipPanel.py
import uthread2
from carbonui import const as uiconst, fontconst, TextColor
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from eve.client.script.ui import eveColor, eveThemeColor
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.skillBar.skillBar import SkillBar
from eve.client.script.ui.control.tooltips import TooltipPanel
from eve.client.script.ui.skillPlan.milestone.skillPlanProgressIndicator import SkillPlanProgressIndicator
from eve.client.script.ui.skillPlan.skillPlanDockablePanel import SkillPlanDockablePanel
from localization import GetByLabel
GAUGE_SIZE = 160

class ButtonSkillsTooltipPanel(TooltipPanel):
    default_columns = 2

    def ApplyAttributes(self, attributes):
        super(ButtonSkillsTooltipPanel, self).ApplyAttributes(attributes)
        self.skill = attributes.skill
        self.skillPlan = attributes.skillPlan
        self.LoadStandardSpacingOld()
        self.cellSpacing = (8, 8)
        self.ReconstructLayout()
        uthread2.StartTasklet(self.UpdateThread)

    def ReconstructLayout(self):
        self.Flush()
        self._AddLabelShortcut()
        if self.skill:
            if self.skillPlan:
                self.AddSkillPlan()
            self.AddMediumHeader(text=GetByLabel('UI/Neocom/SkillInTraining'))
            self.AddSkillBarCont()
            self.AddLabelMedium(text=self.skill.GetDescription(), colSpan=self.columns, wrapWidth=260, minWidth=260)
        else:
            cont = ContainerAutoSize()
            EveLabelMedium(parent=cont, align=uiconst.CENTERLEFT, text=GetByLabel('UI/Neocom/NoSkillHint'), color=eveThemeColor.THEME_ALERT)
            self.AddCell(cont, colSpan=self.columns)
            self.AddLabelMedium(text=GetByLabel('UI/Neocom/NoSkillHintSubtext'), colSpan=self.columns)

    def AddSkillPlan(self):
        self.AddMediumHeader(text=GetByLabel('UI/Neocom/TrackedSkillPlanProgress'))
        skillPlanProgressIndicator = SkillPlanProgressIndicator(align=uiconst.CENTER, pos=(0,
         0,
         GAUGE_SIZE,
         GAUGE_SIZE), highlightNotInTraining=True, skillPlan=self.skillPlan)
        self.AddCell(skillPlanProgressIndicator, colSpan=self.columns)

    def AddSkillBarCont(self):
        skillBarCont = ContainerAutoSize(name='skillBarCont', align=uiconst.TOTOP, alignMode=uiconst.TOTOP)
        self.skillBar = SkillBar(parent=ContainerAutoSize(parent=skillBarCont, align=uiconst.TOLEFT), align=uiconst.TOPLEFT, top=3, state=uiconst.UI_DISABLED, skillID=self.skill.GetTypeID())
        self.trainingTimeLabel = EveLabelMedium(parent=ContainerAutoSize(parent=skillBarCont, align=uiconst.TORIGHT), text=self.skill.GetTimeLeftToTrainText(includeBoosters=True), align=uiconst.TOPRIGHT)
        EveLabelMedium(parent=skillBarCont, padding=(10, 0, 4, 0), text=self.skill.GetDescriptionAndLevelInRoman(self.skill.GetNextLevel()), align=uiconst.TOTOP, color=TextColor.HIGHLIGHT)
        self.AddCell(skillBarCont, colSpan=self.columns)

    def _AddLabelShortcut(self):
        label = GetByLabel(SkillPlanDockablePanel.default_captionLabelPath)
        shortcut = uicore.cmd.GetShortcutStringByFuncName('OpenSkillsWindow')
        self.AddLabelShortcut(label=label, shortcut=shortcut)

    def UpdateThread(self):
        while not self.destroyed:
            uthread2.Sleep(0.5)
            if self.skill:
                self.trainingTimeLabel.text = self.skill.GetTimeLeftToTrainText(includeBoosters=True)
