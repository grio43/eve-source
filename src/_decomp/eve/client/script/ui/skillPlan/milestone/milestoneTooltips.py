#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\milestone\milestoneTooltips.py
import eveformat
import evetypes
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import TextColor, uiconst
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import StreamingVideoSprite
from carbonui.util.color import Color
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveLabelLarge
from eve.client.script.ui.control.skillBar.skillBar import SkillBar
from eve.client.script.ui.control.tooltips import TooltipPanel
from eve.client.script.ui.shared.neocom.skillConst import COLOR_SKILL_1
from eve.client.script.ui.skillPlan.skillPlanConst import MILESTONE_ICON_BY_SUBTYPE
from eveui import Sprite
from localization import GetByLabel
from eve.client.script.ui.control import tooltips
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from localization.formatters import FormatTimeIntervalShortWritten
from skills.skillConst import skill_max_level
from skills.skillplan.milestone.const import MilestoneSubType
from skills.skillplan.milestone.milestonesUtil import GetMilestoneSubType
from carbonui.uicore import uicore
WRAP_WIDTH = 300

class AddMilestonesTooltip(TooltipBaseWrapper):

    def __init__(self):
        super(AddMilestonesTooltip, self).__init__()

    def CreateTooltip(self, parent, owner, idx):
        if uicore.IsDragging():
            return
        self.tooltipPanel = tooltips.TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.LoadStandardSpacing()
        self.tooltipPanel.columns = 2
        self.tooltipPanel.AddMediumHeader(text=GetByLabel('UI/SkillPlan/AddingMilestones'))
        video = StreamingVideoSprite(state=uiconst.UI_DISABLED, videoPath='res:/video/SkillPlan/SkillPlanCreationTutorial.webm', width=320, height=192, videoLoop=True)
        self.tooltipPanel.AddCell(cellObject=video, colSpan=2)
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/SkillPlan/MilestonesDragDropInformation'), wrapWidth=WRAP_WIDTH, colSpan=self.tooltipPanel.columns)
        iconColor = (1, 1, 1, 0.75)
        self.tooltipPanel.AddSpriteLabel(texturePath=MILESTONE_ICON_BY_SUBTYPE[MilestoneSubType.SHIP_MILESTONE], label=GetByLabel('UI/SkillPlan/MilestoneShip'), iconOffset=5, iconColor=iconColor)
        self.tooltipPanel.AddSpriteLabel(texturePath=MILESTONE_ICON_BY_SUBTYPE[MilestoneSubType.MODULE_MILESTONE], label=GetByLabel('UI/SkillPlan/MilestoneModule'), iconOffset=-5, iconColor=iconColor)
        self.tooltipPanel.AddSpriteLabel(texturePath=MILESTONE_ICON_BY_SUBTYPE[MilestoneSubType.SKILL_MILESTONE], label=GetByLabel('UI/SkillPlan/MilestoneSkill'), iconOffset=5, iconColor=iconColor)
        self.tooltipPanel.AddSpriteLabel(texturePath=MILESTONE_ICON_BY_SUBTYPE[MilestoneSubType.OTHER_MILESTONE], label=GetByLabel('UI/SkillPlan/MilestoneOther'), iconOffset=-5, iconColor=iconColor)
        return self.tooltipPanel


class MilestoneCompletedBanner(Container):
    default_height = 36

    def ApplyAttributes(self, attributes):
        super(MilestoneCompletedBanner, self).ApplyAttributes(attributes)
        leftCont = Container(name='leftcont', parent=self, align=uiconst.TOLEFT, width=42, bgColor=eveColor.COPPER_OXIDE_GREEN)
        Sprite(name='completedIcon', parent=leftCont, align=uiconst.CENTER, pos=(0, 0, 34, 34), texturePath='res:/UI/Texture/classes/SkillPlan/completedIcon.png')
        mainCont = Container(name='mainCont', parent=self, bgColor=eveColor.WHITE, padLeft=4)
        EveLabelLarge(parent=mainCont, align=uiconst.CENTERLEFT, text=GetByLabel('UI/SkillPlan/Completed'), color=eveColor.BLACK, left=14)


class MilestoneInfoTooltip(TooltipPanel):

    def ApplyAttributes(self, attributes):
        super(MilestoneInfoTooltip, self).ApplyAttributes(attributes)
        self.skillPlan = attributes.skillPlan
        self.milestone = attributes.milestone
        self.isEditable = attributes.isEditable
        self.milestoneSubType = GetMilestoneSubType(self.milestone.GetTypeID())
        self.iconSize = attributes.iconSize
        self.timeLabel = None
        self.ReconstructLayout()

    def ReconstructLayout(self):
        self.Flush()
        self.LoadStandardSpacing()
        self.columns = 2
        if self.isEditable:
            self.SetState(uiconst.UI_NORMAL)
        self.CreateTopSection()
        self.CreateMiddleSection()
        self.CreateBottomSection()
        if self.milestone.IsCompleted():
            banner = MilestoneCompletedBanner(align=uiconst.TOTOP, padTop=6)
            self.AddCell(banner, colSpan=self.columns, cellPadding=0)

    def CreateTopSection(self):
        text = '%s: %s' % (GetByLabel('UI/SkillPlan/Milestone'), self._GetTypeLabel())
        self.AddMediumHeader(text=text)
        self.AddLabelMedium(text=self._GetUnlocksText(), width=WRAP_WIDTH, cellPadding=(self.cellPadding[0], 5), colSpan=self.columns)

    def CreateMiddleSection(self):
        pass

    def CreateBottomSection(self):
        self.FillRow()
        showInfoCont = ContainerAutoSize(name='showInfoCont', align=uiconst.CENTERLEFT, height=35)
        ContainerAutoSize(parent=showInfoCont, name='textCont', align=uiconst.TOLEFT)
        self.timeLabel = None
        totalTime = self.GetTotalTimeDate()
        if totalTime:
            totalTimeText = GetByLabel('UI/SkillPlan/TotalTrainingTime', color=Color(*COLOR_SKILL_1).GetHex())
            row, label = self.AddMediumHeader(text=totalTimeText, labelColSpan=1)
            self.timeLabel = EveLabelLarge(text=totalTime, align=uiconst.CENTERRIGHT, color=COLOR_SKILL_1)
            row.AddCell(self.timeLabel)
        if self.isEditable:

            def OnRemoveBtn(*args):
                PlaySound('skills_planner_skill_remove_play')
                self.skillPlan.RemoveMilestone(self.milestone.GetID())
                self.Close()

            removeBtn = Button(name='removeBtn', align=uiconst.TOTOP, label=GetByLabel('UI/SkillPlan/RemoveMilestone'), func=OnRemoveBtn)
            self.AddCell(cellObject=removeBtn, colSpan=self.columns, cellPadding=(0, self.cellPadding[1]))

    def GetTotalTimeDate(self):
        totalTime = sm.GetService('skills').GetSkillTrainingTimeLeftToUseType(self.milestone.GetTypeID(), includeBoosters=False)
        if not totalTime:
            return None
        dateText = FormatTimeIntervalShortWritten(long(totalTime), showFrom='day')
        return dateText

    def _GetTypeLabel(self):
        if self.milestoneSubType == MilestoneSubType.SHIP_MILESTONE:
            return GetByLabel('UI/SkillPlan/MilestoneShip')
        if self.milestoneSubType == MilestoneSubType.SKILL_MILESTONE:
            return GetByLabel('UI/SkillPlan/MilestoneSkill')
        if self.milestoneSubType == MilestoneSubType.MODULE_MILESTONE:
            return GetByLabel('UI/SkillPlan/MilestoneModule')
        if self.milestoneSubType == MilestoneSubType.OTHER_MILESTONE:
            return GetByLabel('UI/SkillPlan/MilestoneOther')

    def _GetUnlocksText(self):
        if self.milestoneSubType == MilestoneSubType.SKILL_MILESTONE:
            return GetByLabel('UI/SkillPlan/CompleteMilestoneUnlocks')
        else:
            return GetByLabel('UI/SkillPlan/CompleteMilestoneUnlocks')


class TypeIDMilestoneInfoTooltip(MilestoneInfoTooltip):

    def CreateMiddleSection(self):
        super(TypeIDMilestoneInfoTooltip, self).CreateMiddleSection()
        sprite, _ = self.AddSpriteLabel(texturePath='', label=evetypes.GetName(self.milestone.GetTypeID()), iconOffset=0, labelOffset=0, mainAlign=uiconst.CENTER, align=uiconst.TOTOP, textAlign=uiconst.CENTER, iconSize=self.iconSize, colSpan=self.columns)
        sm.GetService('photo').GetIconByType(sprite, self.milestone.GetTypeID(), size=self.iconSize, ignoreSize=False)


class SkillMilestoneInfoTooltip(MilestoneInfoTooltip):

    def CreateMiddleSection(self):
        super(SkillMilestoneInfoTooltip, self).CreateMiddleSection()
        cont = ContainerAutoSize(name='cont', alignt=uiconst.CENTERLEFT, height=30)
        self.skillBar = SkillBar(parent=cont, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, skillID=self.milestone.GetTypeID(), requiredLevel=self.milestone.GetLevel())
        self.levelLabel = EveLabelLarge(parent=cont, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL, left=self.skillBar.width + 10)
        self.AddCell(cont, colSpan=self.columns)
        if self.isEditable:
            self._ConstructLevelEdit()
        self._UpdateLevelDisplay()

    def GetTotalTimeDate(self):
        skillSvc = sm.GetService('skills')
        required = skillSvc.GetRequiredSkillsRecursive(self.milestone.GetTypeID())
        required[self.milestone.GetTypeID()] = max(self.milestone.GetLevel(), required.get(self.milestone.GetTypeID(), 0))
        totalTime = skillSvc.GetSkillTrainingTimeLeftForTypesAndLevels(required, includeBoosters=False)
        if not totalTime:
            return None
        dateText = FormatTimeIntervalShortWritten(long(totalTime), showFrom='day')
        return dateText

    def _ConstructLevelEdit(self):
        cont = Container(colSpan=self.columns, align=uiconst.CENTER)
        padding = 40
        minusBtn = Button(name='minusBtn', parent=cont, align=uiconst.CENTERLEFT, texturePath='res:/UI/Texture/Shared/DarkStyle/buttonIconMinus.png', soundClick='skills_planner_skill_decrease_play')
        self.modifyLevelLabel = EveLabelLarge(parent=cont, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL, left=minusBtn.width + padding, text=GetByLabel('UI/SkillPlan/LevelNum', levelNum=self.milestone.GetLevel()))
        plusBtn = Button(name='plusBtn', parent=cont, align=uiconst.CENTERLEFT, left=self.modifyLevelLabel.left + self.modifyLevelLabel.width + padding, texturePath='res:/UI/Texture/Shared/DarkStyle/buttonIconPlus.png', soundClick='skills_planner_skill_increase_play')
        minusBtn.SetFunc(lambda *args: self._ModifyLevelInTooltip(minusBtn, plusBtn, -1))
        plusBtn.SetFunc(lambda *args: self._ModifyLevelInTooltip(minusBtn, plusBtn, 1))
        self._UpdateBtns(minusBtn, plusBtn)
        cont.height = max(minusBtn.height, plusBtn.height, self.modifyLevelLabel.height)
        cont.width = plusBtn.left + plusBtn.width
        self.AddCell(cellObject=cont, colSpan=self.columns)

    def _ModifyLevelInTooltip(self, minusBtn, plusBtn, direction):
        milestone = self.skillPlan.GetMilestone(self.milestone.GetID())
        if not milestone:
            return
        milestone.SetLevel(self.milestone.GetLevel() + direction)
        totalTime = self.GetTotalTimeDate()
        if totalTime and not self.timeLabel:
            self.ReconstructLayout()
        elif not totalTime and self.timeLabel:
            self.ReconstructLayout()
        else:
            self._UpdateLevelDisplay()
            self._UpdateBtns(minusBtn, plusBtn)

    def _UpdateBtns(self, minusBtn, plusBtn):
        minusBtn.Enable()
        plusBtn.Enable()
        if self.milestone.GetLevel() <= 1:
            minusBtn.Disable()
        elif self.milestone.GetLevel() >= skill_max_level:
            plusBtn.Disable()

    def _UpdateLevelDisplay(self):
        if self.milestone.GetLevel():
            color = Color.RGBtoHex(*TextColor.NORMAL)
            text = GetByLabel('UI/InfoWindow/RequiredSkillNameAndLevel', skill=self.milestone.GetTypeID(), level=eveformat.number_roman(self.milestone.GetLevel()), levelColor=color)
            self.skillBar.SetRequiredLevel(self.milestone.GetLevel())
        else:
            text = evetypes.GetName(self.milestone.GetTypeID())
        self.levelLabel.text = text
        if getattr(self, 'modifyLevelLabel', None):
            self.modifyLevelLabel.text = GetByLabel('UI/SkillPlan/LevelNum', levelNum=self.milestone.GetLevel())
        if self.timeLabel:
            totalTime = self.GetTotalTimeDate()
            self.timeLabel.text = totalTime if totalTime else '-'
        return text
