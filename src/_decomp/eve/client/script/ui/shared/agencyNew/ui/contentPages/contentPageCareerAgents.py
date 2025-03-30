#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPages\contentPageCareerAgents.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.uianimations import animations
from eve.client.script.ui.control.eveLabel import Label, EveCaptionMedium
from eve.client.script.ui.shared.agencyNew.ui.contentPages.singleColumnContentPage import SingleColumnContentPage
from carbonui.control.section import Section
from localization import GetByLabel
from eve.client.script.ui.control.statefulButton import StatefulButton
from eve.client.script.ui.shared.pointerTool import pointerToolConst as pConst

class ContentPageCareerAgents(SingleColumnContentPage):
    scrollSectionWidth = 400

    def ConstructLayout(self):
        super(ContentPageCareerAgents, self).ConstructLayout()
        self.rightContainer = Section(name='rightContainer', parent=self, align=uiconst.TOLEFT, width=self.scrollSectionWidth, padLeft=10, headerText=GetByLabel('UI/Agency/CareerDetails'))
        self.careerTitleLabel = EveCaptionMedium(parent=self.rightContainer, align=uiconst.TOTOP)
        self.descriptionLabel = Label(parent=self.rightContainer, align=uiconst.TOTOP, padTop=10)
        self.recommendedTitleLabel = EveCaptionMedium(parent=self.rightContainer, align=uiconst.TOTOP, text=GetByLabel('UI/SkillPlan/RecommendedSkillPlanTitle'), padTop=20)
        self.skillPlanLabel = Label(parent=self.rightContainer, align=uiconst.TOTOP, padTop=10, state=uiconst.UI_NORMAL)
        self.ConstructButtonContainer()

    def ConstructButtonContainer(self):
        self.buttonRowCont = Container(name='buttonRowContainer', parent=self.rightContainer, align=uiconst.TOTOP, padding=(0, 10, 0, 10), height=30)
        self.primaryActionButton = StatefulButton(name='Agency_CareerAgents_InteractionButton', uniqueUiName=pConst.UNIQUE_NAME_CAREER_AGENT_INTERACTION_BTN, parent=self.buttonRowCont, align=uiconst.CENTERRIGHT, iconAlign=uiconst.TORIGHT)

    def OnCardSelected(self, selectedCard):
        super(ContentPageCareerAgents, self).OnCardSelected(selectedCard)
        contentPiece = selectedCard.contentPiece
        self.descriptionLabel.text = contentPiece.GetCareerAgentDescription()
        self.careerTitleLabel.text = contentPiece.GetCareerAgentPathName()
        skillPlanLink = contentPiece.SkillPlanLink()
        if skillPlanLink:
            self.recommendedTitleLabel.Show()
            self.skillPlanLabel.text = GetByLabel('UI/SkillPlan/RecommendedSkillPlanMsg', skillPlanLink=skillPlanLink)
        else:
            self.recommendedTitleLabel.Hide()
            self.skillPlanLabel.text = ''
        self.primaryActionButton.SetController(contentPiece)
        animations.FadeTo(self.rightContainer, 0.0, 1.0, duration=0.3)
