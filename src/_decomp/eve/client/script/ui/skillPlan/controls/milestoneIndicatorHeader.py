#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\controls\milestoneIndicatorHeader.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveLabelLarge, EveCaptionLarge, EveLabelMedium
from localization import GetByLabel

class LegendEntry(Container):
    default_height = 18
    default_padTop = 4

    def ApplyAttributes(self, attributes):
        super(LegendEntry, self).ApplyAttributes(attributes)
        color = attributes.color
        text = attributes.text
        Fill(parent=self, align=uiconst.TOLEFT, width=self.default_height, color=color)
        EveLabelMedium(parent=self, align=uiconst.CENTERLEFT, left=self.default_height + 8, text=text)


def LoadMilestonesTooltipPanel(tooltipPanel, *args):
    tooltipPanel.LoadStandardSpacing()
    tooltipPanel.columns = 1
    tooltipPanel.AddMediumHeader(text=GetByLabel('UI/SkillPlan/Milestones'))
    tooltipPanel.AddLabelMedium(text=GetByLabel('UI/SkillPlan/SkillMilestonesDescText'), wrapWidth=300)


class MilestoneIndicatorHeader(ContainerAutoSize):
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        super(MilestoneIndicatorHeader, self).ApplyAttributes(attributes)
        captionText = attributes.captionText
        self.highlightNotInTraining = attributes.highlightNotInTraining
        self.captionLabel = EveLabelLarge(parent=self, align=uiconst.TOTOP, state=uiconst.UI_DISABLED, text=captionText)
        self.skillPlanNameCaption = EveCaptionLarge(parent=self, align=uiconst.TOTOP, state=uiconst.UI_DISABLED)

    def SetCaption(self, text):
        self.captionLabel.SetText(text)

    def SetSkillPlanName(self, name):
        self.skillPlanNameCaption.SetText(name)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadStandardSpacing()
        tooltipPanel.columns = 1
        tooltipPanel.AddMediumHeader(text=GetByLabel('UI/SkillPlan/SkillPlansAndMilestonesHeader'))
        tooltipPanel.AddLabelMedium(text=GetByLabel('UI/SkillPlan/SkillPlansDescText'), wrapWidth=300)
        tooltipPanel.AddLabelMedium(text=GetByLabel('UI/SkillPlan/SkillMilestonesDescText'), wrapWidth=300)
        tooltipPanel.AddCell(LegendEntry(color=eveColor.WHITE, text=GetByLabel('UI/SkillPlan/TrainedSkills'), align=uiconst.TOTOP))
        tooltipPanel.AddCell(LegendEntry(color=eveColor.CRYO_BLUE, text=GetByLabel('UI/SkillPlan/SkillsInTrainingQueue'), align=uiconst.TOTOP))
        if self.highlightNotInTraining:
            tooltipPanel.AddCell(LegendEntry(color=eveColor.WARNING_ORANGE, text=GetByLabel('UI/SkillPlan/SkillsMissingFromTrainingQueue'), align=uiconst.TOTOP))
