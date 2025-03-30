#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\loginRewards\loginRewardsWnd.py
import blue
import uthread2
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.sys.serviceConst import ROLE_PROGRAMMER
from carbonui import uiconst
from carbonui.control.checkbox import Checkbox
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.util.color import Color
from carbonui.control.button import Button
from eve.client.script.ui.control.toggleButtonGroup import ToggleButtonGroup
from eve.client.script.ui.shared.loginRewards.evergreenRewardPanel import EvergreenRewardPanel
from eve.client.script.ui.shared.loginRewards.rewardToggleButtonGroupButton import RewardToggleButtonGroupButtonHeader
from eve.client.script.ui.shared.loginRewards.rewardUiConst import BACKGROUND_HEIGHT, BACKGROUND_WIDTH, BLUE_TEXT_COLOR, BOTTOM_BORDER_HEIGHT, DEFAULT_BANNER, LOGIN_REWARDS_WINDOW_ID, REWARD_EVERGREEN_BTN, REWARD_ROOKIE_BTN, REWARD_SEASONAL_BTN, REWARD_WND_HEIGHT, REWARD_WND_OPEN_ON_LOGIN_SETTING, REWARD_WND_WIDTH, SEASON_BACKGROUND_HEIGHT, SEASON_BACKGROUND_WIDTH, TOP_HEIGHT
from eve.client.script.ui.shared.loginRewards.rookieRewardPanel import RookieRewardPanel
from eve.client.script.ui.shared.loginRewards.seasonRewardPanel import SeasonRewardPanel
from localization import GetByLabel, GetByMessageID
from loginrewards.common.fsdloaders import SeasonalCampaignsStaticData
from utillib import KeyVal
TAB_SELECTED = 'rewardWndTabSelected'

class DailyLoginRewardsWnd(Window):
    __notifyevents__ = ['OnUIScalingChange', 'OnSubscriptionChanged_Local']
    __guid__ = 'DailyLoginRewardsWnd'
    default_height = REWARD_WND_HEIGHT
    default_width = REWARD_WND_WIDTH
    default_minSize = (default_width, default_height)
    default_isStackable = False
    default_isOverlayable = False
    default_windowID = LOGIN_REWARDS_WINDOW_ID
    default_captionLabelPath = 'UI/LoginRewards/WindowCaption'
    default_descriptionLabelPath = 'UI/LoginRewards/WindowDescription'

    def DebugReload(self, *args):
        self.Close()
        DailyLoginRewardsWnd.Open()

    def ApplyAttributes(self, attributes):
        self.triggersModalAdjustment = False
        super(DailyLoginRewardsWnd, self).ApplyAttributes(attributes)
        self.MakeUnResizeable()
        self.LoadWnd()
        PlaySound('daily_login_atmo_play')

    def LoadWnd(self):
        if session.role & ROLE_PROGRAMMER:
            reloadBtn = Button(parent=self.sr.main, label='Reload', align=uiconst.TOPRIGHT, func=self.DebugReload, top=14, idx=0)
        RewardsContainer(parent=self.sr.main, align=uiconst.CENTER, width=1075, height=656)
        self.width, self.height = self.GetWindowSizeForContentSize(1075, 656)

    def OnUIScalingChange(self, *args):
        self.sr.main.Flush()
        self.LoadWnd()

    def OnSubscriptionChanged_Local(self):
        self.sr.main.Flush()
        self.LoadWnd()

    def Close(self, setClosed = False, *args, **kwds):
        super(DailyLoginRewardsWnd, self).Close(setClosed=setClosed, *args, **kwds)
        PlaySound('daily_login_atmo_stop')


class RewardsContainer(Container):
    default_name = 'rewardsContainer'
    default_clipChildren = True

    def ApplyAttributes(self, attributes):
        self._adjustingThread = None
        self.isScrolling = False
        self.currentFirstVisibleDay = 0
        Container.ApplyAttributes(self, attributes)
        self.BuildBottomBorder()
        innerCont = Container(name='innerCont', parent=self)
        bgCont = Container(name='bgCont', parent=self, padding=(12, 2, 12, 3), clipChildren=True)
        topCont = Container(name='topCont', parent=innerCont, align=uiconst.TOTOP, height=TOP_HEIGHT)
        self.campaignCont = Container(name='campaignCont', parent=innerCont, align=uiconst.TOALL, padTop=10)
        self.btnGroup = ToggleButtonGroup(parent=topCont, align=uiconst.TOALL, padding=(12, 2, 12, 3), height=0, callback=self.OnMainTabGroup)
        self.backgroundImage = Sprite(name='backgroundImage', parent=bgCont, align=uiconst.CENTERTOP, pos=(0,
         0,
         BACKGROUND_WIDTH,
         BACKGROUND_HEIGHT), opacity=1.0)
        loginCampaignService = sm.GetService('loginCampaignService')
        seasonalLoginCampaignService = sm.GetService('seasonalLoginCampaignService')
        seasonalCampaignID = seasonalLoginCampaignService.get_active_login_campaign()
        dailyCampaign = loginCampaignService.get_active_campaign()
        totalBtnNum = 1 if bool(seasonalCampaignID) else 0
        if dailyCampaign:
            totalBtnNum += 1
        if not totalBtnNum:
            return
        groupWidth = REWARD_WND_WIDTH - self.btnGroup.padLeft - self.btnGroup.padRight
        btnWidth = groupWidth / totalBtnNum
        midIdx = (totalBtnNum - 1) / 2.0
        activeBtnID = None
        currentBtns = []
        tabsWithAvailableRewards = []
        if dailyCampaign:
            static_data = dailyCampaign.static_data
            titleMessageID = static_data.titleMessageID
            subtitleMessageID = static_data.subtitleMessageID
            bgNarrow = static_data.windowHeaderBackgroundNarrow
            bgWide = static_data.windowHeaderBackgroundWide
            texturePath = None
            if totalBtnNum == 1:
                if bgWide:
                    texturePath = bgWide
            elif bgNarrow:
                texturePath = bgNarrow
            texturePath = texturePath or DEFAULT_BANNER
            textureInfo = KeyVal(texturePath=texturePath, textureWidth=BACKGROUND_WIDTH, textureHeight=BACKGROUND_HEIGHT, textureOpacity=self.backgroundImage.opacity, textureOffset=0, textureAlign=uiconst.TOPLEFT)
            btn = None
            tabName = None
            if static_data.is_rookie_campaign:
                panel = RookieRewardPanel(parent=self.campaignCont)
                panel.Hide()
                btn = self.btnGroup.AddButton(btnID=REWARD_ROOKIE_BTN, label=GetByMessageID(titleMessageID) if titleMessageID else GetByLabel('UI/LoginRewards/RewardHeaderDefault'), subLabel=GetByMessageID(subtitleMessageID) if subtitleMessageID else GetByLabel('UI/LoginRewards/CollectText'), btnClass=RewardToggleButtonGroupButtonHeader, panel=panel, btnIdx=len(currentBtns), totalBtnNum=totalBtnNum, textureInfo=textureInfo, btnWidth=btnWidth)
                if loginCampaignService.can_claim_now():
                    tabsWithAvailableRewards.append(REWARD_ROOKIE_BTN)
            else:
                panel = EvergreenRewardPanel(parent=self.campaignCont)
                panel.Hide()
                btn = self.btnGroup.AddButton(btnID=REWARD_EVERGREEN_BTN, label=GetByMessageID(titleMessageID) if titleMessageID else GetByLabel('UI/LoginRewards/RewardHeaderDefault'), subLabel=GetByMessageID(subtitleMessageID) if subtitleMessageID else GetByLabel('UI/LoginRewards/CollectText'), btnClass=RewardToggleButtonGroupButtonHeader, panel=panel, btnIdx=len(currentBtns), totalBtnNum=totalBtnNum, textureInfo=textureInfo, btnWidth=btnWidth)
                if loginCampaignService.can_claim_now():
                    tabsWithAvailableRewards.append(REWARD_EVERGREEN_BTN)
            if btn:
                currentBtns.append(btn)
        if seasonalCampaignID:
            seasonCampaignData = SeasonalCampaignsStaticData().get_campaign(seasonalCampaignID)
            titleMessageID = seasonCampaignData.campaignName
            bgWide = seasonCampaignData.windowHeaderBackground or DEFAULT_BANNER
            days_remaining = seasonalLoginCampaignService.get_days_remaining()
            formattingStart = '<color=%s>' % Color.RGBtoHex(*BLUE_TEXT_COLOR)
            formattingEnd = '</color>'
            if days_remaining > 1:
                time_remaining_text = GetByLabel('UI/LoginRewards/DaysRemainingWithFormatting', numDays=days_remaining, formattingStart=formattingStart, formattingEnd=formattingEnd)
            else:
                hours = seasonalLoginCampaignService.get_hours_until_next_reward_date()
                time_remaining_text = GetByLabel('UI/LoginRewards/HoursRemainingWithFormatting', numHours=hours, formattingStart=formattingStart, formattingEnd=formattingEnd)
            btnIdx = len(currentBtns)
            textureInfo = KeyVal(texturePath=bgWide, textureWidth=SEASON_BACKGROUND_WIDTH, textureHeight=SEASON_BACKGROUND_HEIGHT, textureOpacity=self.backgroundImage.opacity, textureOffset=int((btnIdx - midIdx) * btnWidth))
            panel = SeasonRewardPanel(parent=self.campaignCont)
            panel.Hide()
            btn = self.btnGroup.AddButton(btnID=REWARD_SEASONAL_BTN, label=GetByMessageID(titleMessageID) if titleMessageID else GetByLabel('UI/LoginRewards/RewardHeaderDefault'), subLabel=GetByLabel('UI/LoginRewards/CollectText'), topText=time_remaining_text, btnClass=RewardToggleButtonGroupButtonHeader, texturePath=bgWide, panel=panel, btnIdx=btnIdx, totalBtnNum=totalBtnNum, textureInfo=textureInfo, btnWidth=btnWidth)
            currentBtns.append(btn)
            if seasonalLoginCampaignService.can_claim_now():
                tabsWithAvailableRewards.append(REWARD_SEASONAL_BTN)
                activeBtnID = REWARD_SEASONAL_BTN
        defaultBtnID = currentBtns[0].btnID
        activeBtnID = activeBtnID or settings.user.ui.Get(TAB_SELECTED, defaultBtnID)
        if tabsWithAvailableRewards and activeBtnID not in tabsWithAvailableRewards:
            activeBtnID = tabsWithAvailableRewards[0]
        if activeBtnID not in self.btnGroup.buttonsByID:
            activeBtnID = defaultBtnID
        self.btnGroup.SelectByID(activeBtnID)

    def OnMainTabGroup(self, btnID, oldBtnID, *args):
        settings.user.ui.Set(TAB_SELECTED, btnID)
        self.btnGroup.SetSelected(btnID)
        newBtn = self.btnGroup.GetButton(btnID)
        if not newBtn:
            return
        textureInfo = newBtn.textureInfo
        newBtnIdx = newBtn.btnIdx
        loginCampaignService = sm.GetService('loginCampaignService')
        btnsWithAvailableRewards = loginCampaignService.get_rewards_available()
        for eacButton in self.btnGroup.buttons:
            eacButton.ChangePositionBasedTextures(newBtnIdx)
            showAsUnseen = eacButton.btnID in btnsWithAvailableRewards and eacButton.btnID != btnID
            eacButton.UpdateUnseenCont(showAsUnseen)

        self.AdjustBackgroundImage(newBtn, textureInfo)
        loginCampaignService.AddSeenSettingValue(btnID)
        sm.ScatterEvent('OnLoginRewardWindowOpened')

    def AdjustBackgroundImage(self, newBtn, textureInfo):
        self.backgroundImage.width = textureInfo.textureWidth
        self.backgroundImage.height = textureInfo.textureHeight
        self.backgroundImage.texturePath = textureInfo.texturePath
        self.backgroundImage.SetAlign(getattr(textureInfo, 'textureAlign', uiconst.CENTERTOP))
        self.backgroundImage.left = textureInfo.textureOffset
        if self._adjustingThread:
            self._adjustingThread.kill()
            self._adjustingThread = None
        self._adjustingThread = uthread2.start_tasklet(self._AdjustBgResolution, textureInfo.texturePath, textureInfo.textureWidth, textureInfo.textureHeight)

    def _AdjustBgResolution(self, texturePath, w, h):
        try:
            for x in xrange(3):
                if self.backgroundImage.texturePath != texturePath:
                    return
                textureWidth = self.backgroundImage.renderObject.texturePrimary.atlasTexture.width
                textureHeight = self.backgroundImage.renderObject.texturePrimary.atlasTexture.height
                if textureWidth and textureHeight:
                    if w != textureWidth:
                        self.backgroundImage.width = textureWidth
                    if h != textureHeight:
                        self.backgroundImage.height = textureHeight
                    break
                blue.synchro.Sleep(100)

        except StandardError as e:
            pass

    def BuildBottomBorder(self):
        bottomCont = Container(name='bottomCont', parent=self, align=uiconst.TOBOTTOM, height=BOTTOM_BORDER_HEIGHT)
        Checkbox(parent=bottomCont, align=uiconst.CENTERLEFT, left=20, setting=REWARD_WND_OPEN_ON_LOGIN_SETTING, text=GetByLabel('UI/LoginRewards/ShowOnLogIn'))
