#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPages\contentPageMercDens.py
import eveicon
from carbonui import Axis, ButtonStyle, PickState, ButtonFrameType
from carbonui.button.group import ButtonGroup, ButtonSizeMode
from carbonui.control.button import Button
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.control.section import SectionAutoSize
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.statefulButton import StatefulButton
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentPieces.mercDenContentPiece import MercDenContentPiece
from eve.client.script.ui.shared.agencyNew.ui.agencyUIConst import CONTENT_PAGE_WIDTH_HALF
from eve.client.script.ui.shared.agencyNew.ui.common.helpPanel import MAIN_CONT_PADDING
from eve.client.script.ui.shared.agencyNew.ui.contentGroupPages.baseContentGroupPage import BaseContentGroupPage
import carbonui.const as uiconst
from eve.client.script.ui.shared.cloneGrade import ORGIN_AGENCY_MERCDEN
from inventorycommon.const import solarSystemZarzakh, typeMercenaryDenManagementSkill
from localization import GetByLabel
from carbonui.uicore import uicore
from metadata import ContentTags
FULL_SKILL_LEVEL = 5
BTN_TOP_PADDING = 12
COL_WIDTH = 500

class ContentPageMercDen(BaseContentGroupPage):
    default_name = 'ContentPageMercDen'
    contentGroupID = contentGroupConst.contentGroupZarzakh
    __notifyevents__ = ['OnSubscriptionChanged_Local', 'OnSkillsChanged']
    default_top = 0
    mainContHeight = 500 + 2 * MAIN_CONT_PADDING
    clippingParentTop = 0

    def ConstructLayout(self):
        super(ContentPageMercDen, self).ConstructLayout()
        self.leftMainContainer = Container(name='leftMainContainer', parent=self.mainCont, align=uiconst.CENTERTOP, pos=(0,
         0,
         COL_WIDTH,
         self.mainContHeight - 2 * MAIN_CONT_PADDING), insidePadding=(20,
         MAIN_CONT_PADDING,
         20,
         0))
        self.leftScrollContainer = ScrollContainer(name='leftScrollContainer', parent=self.leftMainContainer)
        self.rightMainContainer = Container(name='rightMainContainer', parent=self.mainCont, align=uiconst.CENTERTOP, pos=(0,
         0,
         COL_WIDTH,
         self.mainContHeight - 2 * MAIN_CONT_PADDING))
        self.rightScrollContainer = ScrollContainer(name='rightScrollContainer', parent=self.rightMainContainer)
        self.ConstructLeftContainerContent()
        self.ConstructRightContainerContent()
        sm.RegisterNotify(self)

    def ConstructLeftContainerContent(self):
        self.leftScrollContainer.Flush()
        self._ConstructOverviewContent(self.leftScrollContainer, 0)
        self._ConstructDeploymentContent(self.leftScrollContainer, 10)
        self._ConstructStateContent(self.leftScrollContainer, 10)

    def ConstructRightContainerContent(self):
        self.rightScrollContainer.Flush()
        self._ConstructActivityContent(self.rightScrollContainer, 0)
        self._ConstructMyMercDensContent(self.rightScrollContainer, 10)

    def _ConstructOverviewContent(self, parent, top):
        self.overviewCont = SectionAutoSize(name='overviewCont', parent=parent, align=uiconst.TOTOP, headerText=GetByLabel('UI/Agency/MercDen/OverviewHeader'), top=top)
        EveLabelMedium(name='overviewLabel', parent=self.overviewCont, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/MercDen/OverviewText'), pickState=PickState.ON)
        destController = MercDenContentPiece(solarSystemID=solarSystemZarzakh)
        StatefulButton(name='setDestToZ', parent=self.overviewCont, align=uiconst.TOTOP, label=GetByLabel('UI/Agency/MercDen/SetDestinationToZarzakh'), controller=destController, top=BTN_TOP_PADDING, frame_type=ButtonFrameType.CUT_BOTTOM_LEFT_RIGHT)

    def _ConstructStateContent(self, parent, top):
        self.statesCont = SectionAutoSize(name='statesCont', parent=parent, align=uiconst.TOTOP, headerText=GetByLabel('UI/Agency/MercDen/StatesHeader'), top=top)
        EveLabelMedium(parent=self.statesCont, name='statesLabel', align=uiconst.TOTOP, text=GetByLabel('UI/Agency/MercDen/StatesText'), pickState=PickState.ON)

    def _ConstructMyMercDensContent(self, parent, top):
        self.myMercDensCont = SectionAutoSize(name='myMercDensCont', parent=parent, align=uiconst.TOTOP, headerText=GetByLabel('UI/Agency/MercDen/MyMercDensHeader'), top=top)
        EveLabelMedium(parent=self.myMercDensCont, name='statesLabel', align=uiconst.TOTOP, text=GetByLabel('UI/Agency/MercDen/MyMercDensText'))
        Button(name='openMyMercDens', parent=self.myMercDensCont, align=uiconst.TOTOP, label=GetByLabel('UI/Agency/MercDen/OpenMyMercDenBtn'), func=self.OnMyMercDensClicked, top=BTN_TOP_PADDING, frame_type=ButtonFrameType.CUT_BOTTOM_LEFT_RIGHT)

    def _ConstructDeploymentContent(self, parent, top):
        self.deploymentCont = SectionAutoSize(name='deploymentCont', parent=parent, align=uiconst.TOTOP, headerText=GetByLabel('UI/Agency/MercDen/DeploymentHeader'), top=top)
        EveLabelMedium(name='deploymentLabel', parent=self.deploymentCont, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/MercDen/DeploymentText'), pickState=PickState.ON)
        deployBtnGroup = ButtonGroup(name='deployBtnGroup', parent=self.deploymentCont, align=uiconst.TOTOP, button_size_mode=ButtonSizeMode.DYNAMIC, top=BTN_TOP_PADDING, ignore_overflow=True)
        if not sm.GetService('cloneGradeSvc').IsOmega():
            Button(parent=deployBtnGroup, label=GetByLabel('Tooltips/SkillPlanner/UpgradeToOmega'), texturePath=eveicon.omega, style=ButtonStyle.MONETIZATION, func=self.OnOmegaBtnClicked)
        if sm.GetService('skills').GetMyLevelIncludingLapsed(typeMercenaryDenManagementSkill) < FULL_SKILL_LEVEL:
            Button(name='skillTrainingBtn', parent=deployBtnGroup, texturePath=eveicon.skill_book, label=GetByLabel('UI/Agency/MercDen/OpenSkillTraining'), func=self.OpenSkillTraining)
        if deployBtnGroup.buttons:
            maxWidth = max([ x.width for x in deployBtnGroup.buttons ])
            deployBtnGroup.button_size_mode = ButtonSizeMode.STRETCH
            if 2 * maxWidth + 20 > COL_WIDTH:
                deployBtnGroup.orientation = Axis.VERTICAL

    def _ConstructActivityContent(self, parent, top):
        self.activityCont = SectionAutoSize(name='activityCont', parent=parent, align=uiconst.TOTOP, headerText=GetByLabel('UI/Agency/MercDen/ActivitiesHeader'), top=top)
        EveLabelMedium(name='activityLabel', parent=self.activityCont, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/MercDen/ActivitiesText'), pickState=PickState.ON)
        from jobboard.client.ui.job_board_window import JobBoardWindow
        Button(name='openOpportunities', parent=self.activityCont, align=uiconst.TOTOP, label=GetByLabel('UI/Agency/MercDen/OpenMTOOpportunities'), func=lambda arg: JobBoardWindow.Open(page_id='browse', content_tag_id=ContentTags.feature_mercenary_tactical_ops), frame_type=ButtonFrameType.CUT_BOTTOM_LEFT_RIGHT, top=BTN_TOP_PADDING)

    def ConstructContentGroupCards(self):
        super(ContentPageMercDen, self).ConstructContentGroupCards()
        self.mainCont.columns = 2

    def OpenSkillTraining(self, *args):
        uicore.cmd.OpenSkillsWindow()

    def OnOmegaBtnClicked(self, *args):
        uicore.cmd.OpenCloneUpgradeWindow(origin=ORGIN_AGENCY_MERCDEN)

    def OnMyMercDensClicked(self, *args):
        uicore.cmd.OpenMyMercenaryDens()

    def OnSubscriptionChanged_Local(self):
        self.ConstructRightContainerContent()

    def OnSkillsChanged(self, skills):
        if typeMercenaryDenManagementSkill in skills:
            self.ConstructRightContainerContent()
