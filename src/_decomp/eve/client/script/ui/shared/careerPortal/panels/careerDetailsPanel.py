#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\careerPortal\panels\careerDetailsPanel.py
from carbonui import ButtonVariant, Density, TextAlign, uiconst
from carbonui.control.button import Button
from carbonui.primitives.line import Line
from careergoals.client.career_goal_svc import get_career_goals_svc
from characterdata.careerpath import get_career_path
from eve.client.script.ui.control.eveLabel import EveCaptionLarge, EveLabelMedium, EveCaptionMedium, Label
from eve.client.script.ui.control.infoIcon import InfoGlyphIcon
from eve.client.script.ui.shared.careerPortal import careerConst
from eve.client.script.ui.shared.careerPortal.careerControllerUI import get_career_portal_controller_svc
from eve.client.script.ui.shared.careerPortal.panels.basePanel import BasePanel
from eve.client.script.ui.shared.careerPortal.rewards.rewardsTooltip import RewardBundleTooltip
from eveui import Sprite, Container
from localization import GetByLabel, GetByMessageID
ICON_SIZE = 16
CRATE_SIZE = 64

class CareerDetailsPanel(BasePanel):
    default_name = 'CareerDetailsPanel'

    def __init__(self, *args, **kwargs):
        super(CareerDetailsPanel, self).__init__(*args, **kwargs)
        self.ConstructLayout()
        careerConst.SELECTED_CAREER_PATH_SETTING.on_change.connect(self.LoadCareer)
        self.LoadCareer(careerConst.SELECTED_CAREER_PATH_SETTING.get())

    def Close(self):
        careerConst.SELECTED_CAREER_PATH_SETTING.on_change.disconnect(self.LoadCareer)
        super(CareerDetailsPanel, self).Close()

    def ConstructLayout(self):
        self._ConstructTitle()
        self._ConstructDescription()
        self._ConstructPlayButton()
        Line(parent=self, align=uiconst.TOTOP, top=ICON_SIZE)
        self._ConstructRewardContainer()

    def _ConstructRewardContainer(self):
        rewardContainer = Container(name='rewardContainer', parent=self, align=uiconst.TOTOP, top=ICON_SIZE, height=CRATE_SIZE)
        self.crateSprite = Sprite(name='crateSprite', parent=Container(parent=rewardContainer, align=uiconst.TOLEFT, width=CRATE_SIZE), align=uiconst.TOLEFT, pos=(0,
         0,
         CRATE_SIZE,
         CRATE_SIZE), state=uiconst.UI_NORMAL)
        rewardLabelContainer = Container(name='rewardLabelContainer', parent=rewardContainer, align=uiconst.TOALL, left=8)
        rewardText = GetByLabel('UI/CareerPortal/GraduationReward')
        EveCaptionMedium(name='rewardCrateLabel', parent=rewardLabelContainer, align=uiconst.CENTERLEFT, text=rewardText)
        textWidth, _ = Label.MeasureTextSize(text=rewardText, fontsize=20)
        self.infoIcon = InfoGlyphIcon(parent=rewardLabelContainer, align=uiconst.CENTERLEFT, left=textWidth + 8)

    def _ConstructPlayButton(self):
        self.playVideoButton = Button(parent=Container(name='playVideoButtonContainer', parent=self, align=uiconst.TOTOP, height=20, top=ICON_SIZE), name='playVideoButton', align=uiconst.CENTERLEFT, label=GetByLabel('UI/CareerPortal/PlayVideo'), texturePath='res:/UI/Texture/classes/careerPortal/playVideo.png', iconSize=ICON_SIZE, density=Density.COMPACT, variant=ButtonVariant.GHOST)

    def _ConstructDescription(self):
        self.descriptionLabel = EveLabelMedium(parent=self, align=uiconst.TOTOP, textAlign=TextAlign.LEFT, top=10)

    def _ConstructTitle(self):
        titleCont = Container(name='titleCont', parent=self, align=uiconst.TOTOP, height=30)
        self.careerIcon = Sprite(name='careerIcon', parent=Container(parent=titleCont, align=uiconst.TOLEFT, width=32), align=uiconst.CENTER, pos=(0, 0, 32, 32))
        self.careerNameLabel = EveCaptionLarge(name='careerNameLabel', parent=Container(parent=titleCont, align=uiconst.TOALL, left=8), align=uiconst.CENTERLEFT)

    def LoadCareer(self, careerID):
        if not careerID:
            return
        self.careerIcon.texturePath = careerConst.CAREERS_32_SIZES.get(careerID, '')
        career = get_career_path(careerID)
        if not career:
            return
        self.careerNameLabel.text = GetByMessageID(career.nameID)
        self.descriptionLabel.text = GetByMessageID(career.descriptionID)
        self.crateSprite.texturePath = careerConst.CRATE_64_SIZES.get(careerID, '')
        career_goal = get_career_goals_svc().get_goal_data_controller().get_career_path_goal(careerID)
        if not career_goal:
            return
        rewards = career_goal.definition.rewards
        rewardTooltip = RewardBundleTooltip(rewards=rewards)
        self.crateSprite.tooltipPanelClassInfo = rewardTooltip
        self.infoIcon.tooltipPanelClassInfo = rewardTooltip
        videoPath = careerConst.CAREER_VIDEOS.get(careerID, '')
        self.playVideoButton.func = lambda x: get_career_portal_controller_svc().play_video(videoPath)
