#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\browser\skillPlanEntryTooltip.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from clonegrade import COLOR_OMEGA_GOLD
from eve.client.script.ui.control.eveLabel import EveLabelLarge
from eve.client.script.ui import eveColor
from localization import GetByLabel
bgColor = (1, 1, 1, 0.15)
horizontalPadding = 10

class SkillPlanEntryTooltip(object):

    def __init__(self, skillPlan, tooltipPanel, *args, **kwargs):
        super(SkillPlanEntryTooltip, self).__init__(*args, **kwargs)
        self.skillPlan = skillPlan
        self.tooltipPanel = tooltipPanel
        self.tooltipPanel.columns = 1
        self.tooltipPanel.LoadStandardSpacing()
        containersAdded = []
        row = self.tooltipPanel.AddHeaderRow()
        skillPlan = SkillPlanEntryTooltipRow(text=GetByLabel('UI/SkillPlan/SkillPlan'))
        row.AddCell(cellObject=skillPlan)
        containersAdded.append(skillPlan)
        desc = self.skillPlan.GetDescription()
        if desc:
            self.tooltipPanel.AddLabelMedium(text=desc, wrapWidth=250, state=uiconst.UI_NORMAL, linkStyle=uiconst.LINKSTYLE_REGULAR)
            self.tooltipPanel.state = uiconst.UI_NORMAL
        if self.skillPlan.IsMissingSkillbooks():
            row = self.tooltipPanel.AddHeaderRow()
            nbMissing = len(self.skillPlan.GetMissingSkillbooks())
            missingSkillsEntry = SkillPlanEntryTooltipRowWithNumber(text=GetByLabel('UI/SkillPlan/SkillbooksMissing2'), textureColor=eveColor.HOT_RED, texturePath='res:/UI/Texture/classes/SkillPlan/lockButtonSkillbook.png', counterNum=nbMissing)
            row.AddCell(cellObject=missingSkillsEntry)
            containersAdded.append(missingSkillsEntry)
        numOmegaSkills = self.skillPlan.GetNumOmegaSkills()
        if numOmegaSkills and not sm.GetService('cloneGradeSvc').IsOmega():
            row = self.tooltipPanel.AddHeaderRow()
            requiresOmega = SkillPlanEntryTooltipRowWithNumber(text=GetByLabel('UI/SkillPlan/RequireOmega'), texturePath='res:/UI/Texture/classes/SkillPlan/lockButtonOmega.png', textureColor=COLOR_OMEGA_GOLD, counterNum=numOmegaSkills)
            row.AddCell(cellObject=requiresOmega)
            containersAdded.append(requiresOmega)
        maxContHeight = max((x.height for x in containersAdded))
        for c in containersAdded:
            c.height = maxContHeight


class SkillPlanEntryTooltipRow(Container):
    default_align = uiconst.CENTERLEFT

    def ApplyAttributes(self, attributes):
        super(SkillPlanEntryTooltipRow, self).ApplyAttributes(attributes)
        text = attributes.text
        texturePath = attributes.texturePath
        textureColor = attributes.textureColor
        left = 0
        iconHeight = 0
        if texturePath:
            icon = Sprite(parent=self, align=uiconst.CENTERLEFT, texturePath=texturePath, pos=(0, 0, 20, 20), color=textureColor)
            left = icon.width + horizontalPadding
            iconHeight = icon.height
        self.label = EveLabelLarge(parent=self, text=text, align=uiconst.CENTERLEFT, left=left)
        self.height = max(self.height, self.label.height, iconHeight)
        self.width = self.label.left + self.label.width


class SkillPlanEntryTooltipRowWithNumber(SkillPlanEntryTooltipRow):

    def ApplyAttributes(self, attributes):
        super(SkillPlanEntryTooltipRowWithNumber, self).ApplyAttributes(attributes)
        counterNum = attributes.counterNum
        left = self.label.left + self.label.width + horizontalPadding
        counterCont = Container(parent=self, align=uiconst.CENTERLEFT, pos=(left,
         0,
         20,
         20))
        counterText = 'x%s' % counterNum
        counterLabel = EveLabelLarge(parent=counterCont, text=counterText, align=uiconst.CENTER)
        Frame(name='badgeFrame', bgParent=counterCont, texturePath='res:/UI/Texture/Shared/counterFrame.png', cornerSize=8, offset=-1, color=bgColor)
        counterCont.height = max(counterCont.height, counterLabel.height + 4)
        counterCont.width = max(counterCont.width, counterLabel.width + 4)
        self.height = max(self.height, counterCont.height + 4)
        self.width = counterCont.left + counterCont.width
