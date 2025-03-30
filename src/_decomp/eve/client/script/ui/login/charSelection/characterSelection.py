#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charSelection\characterSelection.py
import logging
import paperdoll
import blue
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.net import moniker
from carbon.common.script.sys.serviceConst import ROLEMASK_ELEVATEDPLAYER
from carbonui.control.layer import LayerCore
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.client.script.ui.login.charSelection.surveyBanner import SurveyBanner
from eve.client.script.ui.util import uix
from eve.client.script.ui.util.uiComponents import ButtonEffect, Component
import uthread
import log
import carbonui.const as uiconst
import localization
import evetypes
from carbonui.primitives.container import Container
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.shared.redeem.redeemPanel import GetRedeemPanel
from eve.client.script.ui.login.charSelection.lapsedGametimeWarning import LapsedGametimeWarning
from eve.client.script.ui.shared.cloneGrade.multiLoginBlockedWindow import MultiLoginBlockedWindow
from eve.client.script.ui.shared.cloneGrade import ORIGIN_CHARACTERSELECTION
from eve.common.lib import appConst
from eveexceptions import ServiceNotFound, UserError, ExceptionEater
from eve.client.script.ui.login.charSelection.characterSlots import SmallCharacterSlot, SmallEmptySlot
from eve.client.script.ui.login.charSelection.characterSlots import CharacterDetailsLocation as CharLocation
import evegraphics.settings as gfxsettings
import eve.client.script.ui.login.charSelection.characterSelectionUtils as csUtil
import eve.client.script.ui.login.charSelection.characterSelectionColors as csColors
from carbonui.uicore import uicore
from eveprefs import boot
import launchdarkly
LOGO_WIDTH = 205
if boot.region == 'optic':
    LOGO_WIDTH = 551
LOGO_HEIGHT = 81
LOGO_COLOR = (1,
 1,
 1,
 1)
MINIMUM_LOGOHEIGHT = 50
LOGO_PADDING = 40
BG_WIDTH = 2117
BG_HEIGHT = 1200
FEATURE_BAR_HEIGHT = 100
FEATURE_BAR_INNER_HEIGHT = 90
BANNER_WIDTH = 550
WARNING_BANNER_HEIGHT = 40
logger = logging.getLogger(__name__)

class CharacterSelection(LayerCore):
    __notifyevents__ = ['OnSetDevice',
     'OnJumpQueueMessage',
     'OnCharacterHandler',
     'OnUIRefresh',
     'OnUIScalingChange',
     'OnGraphicSettingsChanged',
     'OnUIoffsetChanged']
    isTopLevelWindow = True
    minSidePadding = 50

    def ApplyAttributes(self, attributes):
        self.bannerAdService = None
        self.isInitialLogin = True
        super(CharacterSelection, self).ApplyAttributes(attributes)

    def OnSetDevice(self):
        if not self.isopen:
            return
        self.OnRefreshScreen()

    def OnUIRefresh(self):
        self.OnRefreshScreen()

    def OnUIScalingChange(self, *args):
        self.OnRefreshScreen()

    def OnGraphicSettingsChanged(self, changes):
        if gfxsettings.UI_CAMERA_OFFSET in changes:
            self.ChangeUIoffset()

    def OnUIoffsetChanged(self):
        self.ChangeUIoffset()

    def ChangeUIoffset(self):
        cameraOffset = settings.user.ui.offsetUIwithCamera
        uiOffsetWithCamera = settings.user.ui.cameraOffset
        if self.uiOffset != (cameraOffset, uiOffsetWithCamera):
            self.OnRefreshScreen()

    def OnCloseView(self):
        self.isTabStop = False
        screen = self.selectionScreen
        self.selectionScreen = None
        self.ClearBackground()
        if screen is not None and not screen.destroyed:
            screen.Close()
        self.characterSlotList = []
        self.slotsByCharID.clear()
        self.slotsByIdx.clear()
        self.ResetVariablesForUiElements()

    def OnJumpQueueMessage(self, msgtext, ready):
        if ready:
            log.LogInfo('Jump Queue: ready, slamming through...')
            self.__Confirm(sm.GetService('jumpQueue').GetPreparedQueueCharID())
        else:
            log.LogInfo('Jump Queue: message=', msgtext)
            ShowQuickMessage(msgtext)

    def OnCharacterHandler(self, *_):
        self.SetData()
        self.OnRefreshScreen()

    def GetChars(self):
        return sm.GetService('cc').GetCharactersToSelect()

    def ReduceCharacterGraphics(self):
        gfxsettings.Set(gfxsettings.GFX_CHAR_FAST_CHARACTER_CREATION, True, pending=False)
        gfxsettings.Set(gfxsettings.GFX_CHAR_TEXTURE_QUALITY, 2, pending=False)

    def OnOpenView(self, **kwargs):
        self.isTabStop = True
        self.remoteCharacterSvc = sm.RemoteSvc('charUnboundMgr')
        self.mapSvc = sm.GetService('map')
        self.SetData()
        self.OnRefreshScreen()
        self.AnimateScreenIn()
        sm.GetService('audio').SendUIEvent('character_selection_start')
        with ExceptionEater('Failing to perform survey checks'):
            sm.GetService('survey').PerformSurveyChecks()
        uthread.new(evetypes.GetTypeIDByNameDict)
        charId = blue.os.GetStartupArgValue('character')
        if charId:
            self.ready = True
            self.ConfirmWithCharID(int(charId))
        isElevated = session.role & ROLEMASK_ELEVATEDPLAYER
        if isElevated and settings.public.ui.Get('Insider', True):
            try:
                insider = sm.GetService('insider')
                uthread.new(insider.Show, True, True)
            except ServiceNotFound:
                pass

        is_auto_select = self._CheckAutoSelectCharacter()
        self._CheckOpenRewardsWindow(is_auto_select)
        self.isInitialLogin = False

    def _CheckOpenRewardsWindow(self, is_auto_select):
        if not self._ShouldOpenRewardsWindow():
            return
        if is_auto_select:
            sm.GetService('loginCampaignService').blink_reward_window_on_dock()
        else:
            with ExceptionEater('Failing to open reward window'):
                uthread.new(self._OpenRewardsWindow)

    def _ShouldOpenRewardsWindow(self):
        if sm.GetService('loginCampaignService').should_open_reward_window_on_login():
            return True
        if sm.GetService('seasonalLoginCampaignService').should_open_reward_window_on_login():
            return True
        if sm.GetService('loginCampaignService').should_reopen_DLI_window():
            return True
        return False

    def _CheckAutoSelectCharacter(self):
        if not self.isInitialLogin:
            return False
        try:
            for arg in blue.pyos.GetArg()[1:]:
                if arg.startswith('/autoSelectCharacter:'):
                    try:
                        slotNum = int(arg.split(':')[1])
                        slot = self.slotsByCharID.get(slotNum, None)
                        if not slot:
                            slot = self.slotsByIdx[slotNum]
                    except:
                        raise RuntimeError('Format of parameter incorrect, should be /autoSelectCharacter:slotID<int> (slotNum can characterID or index (0, 1 or 2)')

                    self.EnterGameWithCharacter(slot)
                    return True

        except Exception as e:
            logger.exception(e)

        return False

    def _OpenRewardsWindow(self):
        from eve.client.script.ui.shared.loginRewards.loginRewardsWnd import DailyLoginRewardsWnd
        wnd = DailyLoginRewardsWnd.Open()
        wnd.Lock()
        wnd.ShowDialog(modal=True, closeWhenClicked=True)

    def SetData(self, force = False):
        characterSelectionData = self.GetCharacterSelectionData(force=force)
        self.chars = characterSelectionData.GetChars()
        self.subscriptionEndTimes = characterSelectionData.GetSubscriptionEndTime()
        self.numSlotsOwnedByUser = characterSelectionData.GetNumCharacterSlots()
        self.slotsToDisplay = characterSelectionData.GetMaxServerCharacters()
        self.surveyID = None
        uthread.new(self.FetchSurveyID)

    def FetchSurveyID(self):
        self.surveyID = sm.GetService('survey').GetActiveSurveyID()
        if self.surveyID:
            self.DisplaySurveyBanner()

    def OnRefreshScreen(self):
        if self._IsSelectionScreenDisabled():
            return
        uicore.registry.SetFocus(self)
        self.ready = False
        self.countDownThread = None
        self.characterSlotList = []
        self.adSprite = None
        self.uiOffset = (0, 0)
        self.maxFullSlotSize = None
        self.Flush()
        self.ClearBackground()
        self.selectionScreen = Container(name='selectionScreen', parent=self, state=uiconst.UI_PICKCHILDREN)
        self.InitUI()
        self.AddBackground()
        self.AddFeatureContainer()
        self.LoadCharacterSlots()
        self.AdjustFeatureBarPosition()
        self.CollapseOrExpandSlots(animate=False, loadingSlots=False)
        self.AdjustLogo()
        self.AddLoginRewardWindowButton()
        self.loadingWheel = LoadingWheel(parent=self.selectionScreen, align=uiconst.CENTER, state=uiconst.UI_NORMAL, idx=0)
        self.loadingWheel.display = False

    def AddLoginRewardWindowButton(self):
        with ExceptionEater('Failing to add reward button'):
            loginCampaignService = sm.GetService('loginCampaignService')
            if loginCampaignService.should_reward_btn_be_visible():
                ButtonIcon(parent=self.featureContainer, align=uiconst.BOTTOMRIGHT, texturePath='res:/UI/Texture/\\WindowIcons/gift.png', iconSize=64, width=64, height=64, padRight=30, padLeft=-30, state=uiconst.UI_NORMAL, func=self._OpenRewardsWindow, idx=0)

    def _IsSelectionScreenDisabled(self):
        return self._IsSelectionScreenAvailable() and self.selectionScreen.state == uiconst.UI_DISABLED

    def _IsSelectionScreenAvailable(self):
        return hasattr(self, 'selectionScreen') and self.selectionScreen and not self.selectionScreen.destroyed

    def AnimateScreenIn(self):
        uicore.animations.MorphScalar(self.bg, 'opacity', startVal=0.0, endVal=1.0, duration=1.0)
        uicore.animations.MorphScalar(self.logo, 'opacity', startVal=0.0, endVal=1.0, duration=0.5, timeOffset=0.5)
        uicore.animations.MorphScalar(self.featureContainer, 'opacity', startVal=0.0, endVal=1.0, duration=0.5, timeOffset=1.5)
        slotDelay = 0.5
        uthread.new(self.PlaySound_thread, event='character_selection_animstart', sleepTime=slotDelay)
        for idx, eachSlot in self.slotsByIdx.iteritems():
            baseAnimationOffset = slotDelay + idx * 0.1
            eachSlot.AnimateSlotIn(animationOffset=baseAnimationOffset, soundFunction=self.PlaySound_thread, charContHeight=self.charactersCont.height)

    def PlaySound_thread(self, event, sleepTime):
        blue.pyos.synchro.Sleep(1000 * sleepTime)
        sm.GetService('audio').SendUIEvent(event)

    def AnimateScreenOut(self, excludeSlotForCharID):
        self.selectionScreen.state = uiconst.UI_DISABLED
        slotDelay = 0.5
        slots = self.slotsByIdx.values()
        slots = sorted(slots, key=lambda x: x.slotIdx, reverse=True)
        counter = 0
        uthread.new(self.PlaySound_thread, event='character_selection_animstart', sleepTime=slotDelay)
        for eachSlot in slots:
            if eachSlot.charID == excludeSlotForCharID:
                continue
            baseAnimationOffset = slotDelay + counter * 0.1
            eachSlot.AnimateSlotOut(animationOffset=baseAnimationOffset, soundFunction=self.PlaySound_thread, charContHeight=self.charactersCont.height)
            counter += 1

        uicore.animations.MorphScalar(self.logo, 'opacity', startVal=1.0, endVal=0.0, duration=0.5, timeOffset=2.0)
        uicore.animations.MorphScalar(self.featureContainer, 'opacity', startVal=1.0, endVal=0.0, duration=0.3, timeOffset=0)
        self.redeemPanel.FadeOut()

    def _HandleSubscriptionDowngradeStatus(self):
        try:
            if self.remoteCharacterSvc.GetCharOmegaDowngradeStatus():
                self.warningBar.height = self._GetWarningHeight()
                self.lapsedWarning = LapsedGametimeWarning(parent=self.warningBar, name='lapsed_sub_warning', height=0)
                uicore.animations.MorphScalar(self.lapsedWarning, 'height', startVal=self.lapsedWarning.height, endVal=self.lapsedWarning.default_height, duration=0.1, timeOffset=0)
        except Exception:
            log.LogTraceback('Failed to construct lapsed game time warning in character selection')

    def EnableScreen(self):
        self.selectionScreen.state = uiconst.UI_PICKCHILDREN
        self.AnimateScreenIn()

    def GetCharacterSelectionData(self, force = False):
        return sm.GetService('cc').GetCharacterSelectionData(force=force)

    def ResetVariablesForUiElements(self):
        self.redeemPanel = None
        self.topBorder = None
        self.warningBar = None
        self.centerArea = None
        self.logoCont = None
        self.logo = None
        self.charactersCont = None
        self.adContainer = None
        self.featureContainer = None
        self.openStoreContainer = None

    def InitUI(self):
        self.selectionScreen.Flush()
        redeemPanelClass = GetRedeemPanel()
        self.redeemPanel = redeemPanelClass(name='redeemPanel', width=uicore.desktop.width, align=uiconst.TOBOTTOM, parent=self.selectionScreen, animationDuration=csUtil.COLLAPSE_TIME, dragEnabled=True, instructionText=localization.GetByLabel('UI/RedeemWindow/DragAndDropToGive'), redeemButtonBorderColor=csColors.REDEEM_BORDER, redeemButtonBackgroundColor=csColors.REDEEM_BORDER_BACKGROUND, redeemButtonFillColor=csColors.REDEEM_BORDER_FILL, textColor=csColors.REDEEM_PANEL_AVAILABLE_TEXT, redeemPanelBackgroundColor=csColors.REDEEM_PANEL_FILL, onVisibilityChanged=self.OnRedeemPanelVisibilityChanged, onCollapsibilityChanged=self.OnRedeemPanelCollapsibilityChanged)
        self.topBorder = Container(name='topBorder', parent=self.selectionScreen, align=uiconst.TOTOP_NOPUSH, height=40, state=uiconst.UI_PICKCHILDREN)
        warningWrapper = Container(name='warningWrapper', parent=self.selectionScreen, align=uiconst.TOALL)
        self.warningBar = Container(name='warningBar', parent=warningWrapper, align=uiconst.TOTOP, height=0, state=uiconst.UI_PICKCHILDREN)
        self.centerArea = Container(name='centerAra', parent=self.selectionScreen, align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN)
        self.logoCont = Container(parent=self, name='logoCont', align=uiconst.TOTOP_NOPUSH, height=100, state=uiconst.UI_NORMAL)
        self.logo = Sprite(parent=self.logoCont, texturePath='res:/UI/Texture/classes/CharacterSelection/logo.png', align=uiconst.CENTER, pos=(0,
         0,
         LOGO_WIDTH,
         LOGO_HEIGHT), color=LOGO_COLOR)
        self.charactersCont = Container(name='charactersCont', parent=self.centerArea, align=uiconst.CENTER, state=uiconst.UI_PICKCHILDREN, width=1050, height=600)
        self.SetupCharacterSlots()
        uthread.new(self._HandleSubscriptionDowngradeStatus)

    def AddBackground(self):
        clientHeight = uicore.desktop.height
        percentOfClientHeight = float(clientHeight) / BG_HEIGHT
        newHeight = clientHeight
        newWidth = int(percentOfClientHeight * BG_WIDTH)
        self.bg = Sprite(parent=uicore.desktop, name='charselBackground', texturePath='res:/UI/Texture/classes/CharacterSelection/background.png', align=uiconst.CENTER, pos=(0,
         0,
         newWidth,
         newHeight), state=uiconst.UI_DISABLED)
        if csUtil.IsMonochromeStyleEnabled():
            csUtil.SetMonochromeStyle(self.bg, True)
        self.bgOverlay = Fill(bgParent=uicore.desktop, color=(0, 0, 0, 1.0))
        push = sm.GetService('window').GetCameraLeftOffset(self.bg.width, align=uiconst.CENTER, left=0)
        self.bg.left = push

    def ClearBackground(self):
        if getattr(self, 'bg', None):
            self.bg.Close()
            self.bgOverlay.Close()
        if getattr(self, 'logoCont', None):
            self.logoCont.Close()

    def ResetOpenStoreVisibility(self):
        self.openStoreContainer.StopAnimations()
        self.openStoreContainer.opacity = 1.0

    def FadeInOpenStoreContainer(self, duration):
        self.openStoreContainer.StopAnimations()
        uicore.animations.FadeIn(self.openStoreContainer, duration=duration)

    def FadeOutOpenStoreContainer(self, duration):
        self.openStoreContainer.StopAnimations()
        uicore.animations.FadeOut(self.openStoreContainer, duration=duration)

    def OnRedeemPanelVisibilityChanged(self):
        self.ResetOpenStoreVisibility()
        self.AdjustFeatureBarPosition()
        self.CollapseOrExpandSlots(animate=False, loadingSlots=False)
        self.AdjustLogo()

    def OnRedeemPanelCollapsibilityChanged(self):
        if self.redeemPanel.IsCollapsed():
            self.FadeInOpenStoreContainer(duration=csUtil.COLLAPSE_TIME)
        else:
            self.FadeOutOpenStoreContainer(duration=csUtil.COLLAPSE_TIME)

    def CollapseOrExpandSlots(self, animate = True, loadingSlots = False):
        shouldShipBeVisible = self.ShouldShipBeVisible()
        self.ChangeSlotCollapsedState(animate=animate, loadingSlots=loadingSlots)
        for eachSlot in self.slotsByIdx.itervalues():
            if shouldShipBeVisible:
                eachSlot.ExpandSlot(animate=animate)
            else:
                eachSlot.CollapseSlot(animate=animate)

    def ShouldShipBeVisible(self):
        if self.maxFullSlotSize:
            maxFullSlotSize = self.maxFullSlotSize
        else:
            l, ct, cw, ch = self.charactersCont.GetAbsolute()
            maxFullSlotSize = ch
        redeemPanelHeight = self.redeemPanel.height
        emptySpace = uicore.desktop.height - maxFullSlotSize
        if emptySpace < 2 * (MINIMUM_LOGOHEIGHT + LOGO_PADDING) or emptySpace < FEATURE_BAR_HEIGHT + redeemPanelHeight:
            shipVisible = False
        else:
            shipVisible = True
        return shipVisible

    def ChangeSlotCollapsedState(self, animate, loadingSlots = False):
        shouldShipBeVisible = self.ShouldShipBeVisible()
        maxCurrentCharacterSlotHeight = self.GetMaxCharacterSlotHeight(shipVisible=shouldShipBeVisible)
        charactersContTop = 0
        diff = self.charactersCont.height - maxCurrentCharacterSlotHeight
        if animate or loadingSlots and not self.redeemPanel.IsCollapsed():
            charactersContTop = min(0, int(-diff / 2.0))
        freeSpace = uicore.desktop.height - maxCurrentCharacterSlotHeight

        def FindExtraShift(componentHeight):
            shift = 0
            if freeSpace / 2.0 < componentHeight:
                shift = componentHeight - int(freeSpace / 2.0)
            return shift

        extraShift = 0
        if self.redeemPanel.IsVisible() and not self.redeemPanel.IsCollapsed():
            extraShift = FindExtraShift(self.redeemPanel.height)
        if extraShift:
            charactersContTop = min(charactersContTop, -extraShift)
        uicore.animations.MorphScalar(self.logo, 'opacity', startVal=self.logo.opacity, endVal=1.0, duration=csUtil.COLLAPSE_TIME)
        if extraShift:
            cl, ct, cw, ch = self.charactersCont.GetAbsolute()
            if ct - extraShift < self.logoCont.height - LOGO_PADDING / 2:
                uicore.animations.MorphScalar(self.logo, 'opacity', startVal=self.logo.opacity, endVal=0.05, duration=csUtil.COLLAPSE_TIME)
        if animate:
            uicore.animations.MorphScalar(self.charactersCont, 'height', startVal=self.charactersCont.height, endVal=maxCurrentCharacterSlotHeight, duration=csUtil.COLLAPSE_TIME)
            uicore.animations.MorphScalar(self.charactersCont, 'top', startVal=self.charactersCont.top, endVal=charactersContTop, duration=csUtil.COLLAPSE_TIME)
        else:
            uicore.animations.StopAnimation(self.charactersCont, 'height')
            self.charactersCont.height = maxCurrentCharacterSlotHeight
            self.charactersCont.top = charactersContTop

    def GetSpaceForRedeemPanel(self):
        return min(self.redeemPanel.height, self.redeemPanel.GetCollapsedHeight())

    def AdjustFeatureBarPosition(self):
        shouldShipBeVisible = self.ShouldShipBeVisible()
        maxCurrentCharacterSlotHeight = self.GetMaxCharacterSlotHeight(shouldShipBeVisible)
        redeemPanelHeight = self.GetSpaceForRedeemPanel()
        availableHeight = int((uicore.desktop.height - maxCurrentCharacterSlotHeight) / 2.0) - redeemPanelHeight
        self.featureContainer.top = int(availableHeight / 2.0) + redeemPanelHeight - FEATURE_BAR_HEIGHT / 2

    def GetMaxCharacterSlotHeight(self, shipVisible = True):
        if self.characterSlotList:
            return max((slot.GetSlotHeight(shipVisible=shipVisible) for slot in self.characterSlotList))
        else:
            return max([ slot.GetSlotHeight(shipVisible=shipVisible) for slot in self.slotsByIdx.itervalues() ])

    def SetupCharacterSlots(self):
        self.characterSlotList = []
        self.slotsByCharID = {}
        self.slotsByIdx = {}
        self.slotsToDisplay = min(self.numSlotsOwnedByUser + 1, self.slotsToDisplay)
        paddingFromImage = SmallCharacterSlot.GetExtraWidth()
        spaceForEachSlot = (uicore.desktop.width - 2 * self.minSidePadding) / self.slotsToDisplay
        maxSize = SmallCharacterSlot.maxImageSize + paddingFromImage
        spaceForEachSlot = min(maxSize, spaceForEachSlot)
        occupiedSlots = len(self.chars[:self.slotsToDisplay])
        for idx in xrange(occupiedSlots):
            slot = SmallCharacterSlot(name='characterSlot_%s' % idx, parent=self.charactersCont, callback=self.EnterGameWithCharacter, deleteCallback=self.Terminate, undoDeleteCallback=self.UndoTermination, terminateCallback=self.Terminate, slotIdx=idx, width=spaceForEachSlot)
            slot.OnMouseEnter = (self.OnSlotOnMouseEnter, slot)
            slot.OnMouseExit = (self.OnSlotMouseExit, slot)
            self.characterSlotList.append(slot)
            self.slotsByIdx[idx] = slot

        for idx in xrange(occupiedSlots, self.slotsToDisplay):
            if idx > self.numSlotsOwnedByUser - 1:
                callback = self.GoBuySlot
                ownSlot = False
            else:
                callback = self.CreateCharacter
                ownSlot = True
            slot = SmallEmptySlot(name='emptySlot_%s' % idx, parent=self.charactersCont, callback=callback, slotIdx=idx, width=spaceForEachSlot, ownSlot=ownSlot)
            self.slotsByIdx[idx] = slot
            slot.OnMouseEnter = (self.OnSlotOnMouseEnter, slot)
            slot.OnMouseExit = (self.OnSlotMouseExit, slot)

        self.charactersCont.width = spaceForEachSlot * self.slotsToDisplay
        self.SetUIOffset()

    def SetUIOffset(self):
        cameraOffset = settings.user.ui.offsetUIwithCamera
        uiOffsetWithCamera = settings.user.ui.cameraOffset
        push = sm.GetService('window').GetCameraLeftOffset(self.charactersCont.width, align=uiconst.CENTER, left=0)
        self.uiOffset = (cameraOffset, uiOffsetWithCamera)
        self.charactersCont.left = push
        self.logo.left = push

    def LoadCharacterSlots(self):
        allSlots = self.characterSlotList[:]
        for characterInfo in self.chars[:self.slotsToDisplay]:
            charID = characterInfo.characterID
            characterSlot = allSlots.pop(0)
            self.LoadSlotForCharacter(charID, characterSlot)
            characterSlot.SetMouseExitState()

        if self.characterSlotList:
            maxShipIconHeight = max((slot.GetShipAndLocationContHeight() for slot in self.characterSlotList))
        else:
            shipPadding = CharLocation.paddingShipAlignmentTop + CharLocation.paddingShipAlignmentBottom
            maxShipIconHeight = CharLocation.minShipSize + CharLocation.locationContHeight + shipPadding
        for slot in self.slotsByIdx.itervalues():
            slot.SetShipContHeight(maxShipIconHeight)

        maxSlotHeight = self.GetMaxCharacterSlotHeight()
        self.maxFullSlotSize = maxSlotHeight
        self.charactersCont.height = maxSlotHeight
        self.ready = True

    def LoadSlotForCharacter(self, charID, characterSlot):
        self.slotsByCharID[charID] = characterSlot
        characterDetails = self.GetCharacterSelectionData().GetCharInfo(charID)
        characterSlot.LoadSlot(charID, characterDetails)

    def AddFeatureContainer(self):
        distanceFromBottom = self.GetSpaceForRedeemPanel()
        self.featureContainer = Container(parent=self.selectionScreen, name='featureContainer', align=uiconst.TOBOTTOM_NOPUSH, height=FEATURE_BAR_HEIGHT, top=distanceFromBottom)
        innerFeatureContainer = Container(parent=self.featureContainer, name='innerFeatureCont', align=uiconst.CENTER, width=834, height=FEATURE_BAR_HEIGHT)
        self.openStoreContainer = Container(name='openStoreContainer', parent=innerFeatureContainer, state=uiconst.UI_PICKCHILDREN, align=uiconst.CENTER, width=270, height=FEATURE_BAR_INNER_HEIGHT)
        OpenStoreButton(parent=self.openStoreContainer, align=uiconst.CENTER, onClick=uicore.cmd.ToggleAurumStore)
        self.adContainer = Container(name='adContainer', parent=innerFeatureContainer, align=uiconst.CENTERRIGHT, width=BANNER_WIDTH, height=FEATURE_BAR_INNER_HEIGHT)
        if self.surveyID:
            self.DisplaySurveyBanner()
        push = sm.GetService('window').GetCameraLeftOffset(innerFeatureContainer.width, align=uiconst.CENTER, left=0)
        innerFeatureContainer.left = push

    def DisplaySurveyBanner(self):
        with ExceptionEater('Failing to load survey banner'):
            if not getattr(self, 'adContainer', None) or self.adContainer.destroyed:
                return
            if getattr(self, 'adSprite', None):
                self.adSprite.Close()
                self.adSprite = None
            self.adContainer.Flush()
            SurveyBanner(parent=self.adContainer, surveyID=self.surveyID)
            self.openStoreContainer.align = uiconst.CENTERLEFT

    def AdjustLogo(self):
        cl, ct, cw, ch = self.charactersCont.GetAbsolute()
        if ct > 0:
            availableHeightAbove = ct
        else:
            availableHeightAbove = int((uicore.desktop.height - self.maxFullSlotSize) / 2.0)
        logoContHeight = max(availableHeightAbove, MINIMUM_LOGOHEIGHT + LOGO_PADDING)
        self.logoCont.height = logoContHeight
        self.logo.display = True
        availableHeightForLogo = logoContHeight - LOGO_PADDING
        percentage = max(0.55, min(1.0, availableHeightForLogo / float(LOGO_HEIGHT)))
        newHeight = int(percentage * LOGO_HEIGHT)
        newWidth = int(percentage * LOGO_WIDTH)
        self.logo.height = newHeight
        self.logo.width = newWidth

    def OnSlotOnMouseEnter(self, slot, *args):
        if not slot.mouseOverState:
            sm.GetService('audio').SendUIEvent('character_hover_picture')
        for eachSlot in self.slotsByIdx.itervalues():
            if eachSlot.charID:
                characterData = self.GetCharacterSelectionData().GetCharInfo(eachSlot.charID)
                deletePrepTime = characterData.GetDeletePrepareTime()
                if deletePrepTime:
                    continue
            if eachSlot == slot:
                eachSlot.SetMouseOverState(animate=True)
            else:
                eachSlot.SetMouseExitState(animate=True)

    def OnSlotMouseExit(self, slot, *args):
        if uicore.uilib.mouseOver.IsUnder(slot):
            return
        slot.SetMouseExitState(animate=True)

    def GoBuySlot(self, slotSelected):
        uicore.cmd.GetCommandAndExecute('OpenAccountManagement', origin='characterSelection')

    def CreateCharacter(self, slotSelected):
        if not self._CanLogin():
            return
        self.CreateNewCharacter()

    def _CanLogin(self):
        computerhash = sm.GetService('connection').GetComputerHash()
        if computerhash is not None:
            if not sm.RemoteSvc('multiLoginBlocker').Login(computerhash):
                MultiLoginBlockedWindow.Open(origin=ORIGIN_CHARACTERSELECTION)
                return False
        return True

    def EnterGameWithCharacter(self, slotSelected):
        characterData = self.GetCharacterSelectionData().GetCharInfo(slotSelected.charID)
        deletePrepTime = characterData.GetDeletePrepareTime()
        if deletePrepTime is not None:
            return
        if not self._CanLogin():
            return
        slotSelected.SetMouseOverState()
        slotSelected.PlaySelectedAnimation()
        self.ConfirmWithCharID(slotSelected.charID)

    def CreateNewCharacter(self):
        if not self.ready:
            eve.Message('Busy')
            return
        lowEnd = gfxsettings.GetDeviceClassification() == gfxsettings.DEVICE_LOW_END
        if lowEnd:
            msg2 = eve.Message('ReduceGraphicsSettings', {}, uiconst.YESNO, default=uiconst.ID_NO)
            if msg2 == uiconst.ID_YES:
                self.ReduceCharacterGraphics()
        eve.Message('CCNewChar')
        uthread.new(sm.GetService('gameui').GoCharacterCreation)

    def CreateNewAvatar(self, charID):
        charData = self.GetCharacterSelectionData().GetCharInfo(charID)
        charDetails = charData.charDetails
        if charData.GetPaperDollState == paperdoll.State.force_recustomize:
            eve.Message('ForcedPaperDollRecustomization')
        uthread.new(sm.GetService('gameui').GoCharacterCreation, charID, charDetails.gender, charDetails.raceID, charDetails.bloodlineID, dollState=charData.GetPaperDollState())

    def Confirm(self):
        if not self.characterSlotList:
            return
        slot = self.characterSlotList[0]
        self.EnterGameWithCharacter(slot)

    def ConfirmWithCharID(self, charID, *_):
        log.LogInfo('Character selection: Character selection confirmation')
        if not self.ready:
            log.LogInfo('Character selection: Denied character selection confirmation, not ready')
            eve.Message('Busy')
            return
        isInSync = self.WaitForClockSynchroAndGetSynchroState()
        if not isInSync:
            eve.Message('ClockSynchroInProgress')
            return
        if sm.GetService('jumpQueue').GetPreparedQueueCharID() != charID:
            self.__Confirm(charID)

    def WaitForClockSynchroAndGetSynchroState(self):
        for x in xrange(300):
            if not sm.GetService('connection').IsClockSynchronizing():
                return True
            if x > 30:
                log.general.Log('Clock synchronization still in progress after %d seconds' % x, log.LGINFO)
            blue.pyos.synchro.SleepWallclock(1000)

        return not sm.GetService('connection').IsClockSynchronizing()

    def CheckCharacterLockStatus(self, charID):
        lockTypeID = sm.RemoteSvc('charUnboundMgr').GetCharacterLockType(charID)
        if lockTypeID is not None:
            if lockTypeID == appConst.charLockInTransferQueue:
                raise UserError('CharacterTransferring')
            elif lockTypeID == appConst.charLockOnSale:
                raise UserError('CharacterOnSale')
            else:
                raise UserError('CharacterLocked')

    def EnterAsCharacter(self, charID, secondChoiceID, skipTutorial = False):
        MAX_RETRIES = 10
        RETRY_SECONDS = 6
        self.CheckCharacterLockStatus(charID)
        if secondChoiceID is not None:
            self.CheckCharacterLockStatus(secondChoiceID)
        for numTries in xrange(MAX_RETRIES):
            try:
                sm.GetService('sessionMgr').PerformSessionChange('charsel', self.remoteCharacterSvc.SelectCharacterID, charID, secondChoiceID, skipTutorial)
                launchdarkly.get_client().character_select(session.userid, charID, session.languageID)
                return
            except UserError as e:
                if e.msg == 'SystemCheck_SelectFailed_Loading' and numTries < MAX_RETRIES - 1:
                    log.LogNotice('System is currently loading. Retrying %s/%s' % (numTries, MAX_RETRIES))
                    blue.pyos.synchro.SleepWallclock(RETRY_SECONDS * 1000)
                else:
                    self.EnableScreen()
                    raise

        self.EnableScreen()

    def __Confirm(self, charID, secondChoiceID = None):
        charData = self.GetCharacterSelectionData().GetCharInfo(charID)
        dollState = charData.GetPaperDollState()
        sm.GetService('cc').StoreCurrentDollState(dollState)
        if dollState in (paperdoll.State.force_recustomize, paperdoll.State.no_existing_customization):
            self.CreateNewAvatar(charID)
            return
        self.ready = False
        self.TryEnterGame(charID, secondChoiceID)
        if charID:
            mailCount = charData.GetUnreaddMailCount()
            if mailCount > 0:
                uthread.new(sm.GetService('mailSvc').CheckNewMessages_thread, mailCount)

    def TryEnterGame(self, charID, secondChoiceID, skipTutorial = False):
        sm.GetService('audio').SendUIEvent('msg_OnLogin_play')
        sm.GetService('audio').SendUIEvent('msg_OnConnecting_play')
        self.ShowLoading()
        try:
            eve.Message('OnCharSel')
            sm.GetService('jumpQueue').PrepareQueueForCharID(charID)
            populationCap = moniker.Moniker('populationCap', (charID, appConst.groupCharacter))
            locations = populationCap.GetCharacterLoadSlot(charID)
            if len(locations) > 1:
                selectedSolarSystemID = self.AskForAlternativeSystems(locations.keys())
                if selectedSolarSystemID is None:
                    sm.GetService('jumpQueue').PrepareQueueForCharID(None)
                    self.ready = True
                    return
                slotKey = locations[selectedSolarSystemID]
                populationCap.MoveCharacterToNewSystem(charID, selectedSolarSystemID, slotKey)
            try:
                self.selectionScreen.state = uiconst.UI_DISABLED
                self.AnimateScreenOut(excludeSlotForCharID=charID)
                self.EnterAsCharacter(charID, secondChoiceID, skipTutorial)
            except UserError as e:
                self.EnableScreen()
                if e.msg != 'SystemCheck_SelectFailed_Queued':
                    sm.GetService('jumpQueue').PrepareQueueForCharID(None)
                    raise
            except:
                self.EnableScreen()
                sm.GetService('jumpQueue').PrepareQueueForCharID(None)
                raise

        except:
            self.EnableScreen()
            self.HideLoading()
            sm.GetService('loading').FadeOut()
            self.ready = True
            raise

    def AskForAlternativeSystems(self, neighbors):
        selectText = localization.GetByLabel('UI/CharacterSelection/SelectAlternativeSystem')
        validNeighbors = []
        for ssid in neighbors:
            systemItem = self.mapSvc.GetItem(ssid)
            regionID = self.mapSvc.GetRegionForSolarSystem(ssid)
            regionItem = self.mapSvc.GetItem(regionID)
            factionID = systemItem.factionID
            factionName = ''
            if factionID:
                factionName = cfg.eveowners.Get(factionID).ownerName
            label = '%s<t>%s<t>%s<t>%s' % (systemItem.itemName,
             regionItem.itemName,
             self.mapSvc.GetSecurityStatus(ssid),
             factionName)
            validNeighborTuple = (label, ssid, None)
            validNeighbors.append(validNeighborTuple)

        loadingSvc = sm.StartService('loading')
        self.HideLoading()
        loadingSvc.FadeOut()
        scrollHeaders = [localization.GetByLabel('UI/Common/LocationTypes/SolarSystem'),
         localization.GetByLabel('UI/Common/LocationTypes/Region'),
         localization.GetByLabel('UI/Common/Security'),
         localization.GetByLabel('UI/Sovereignty/Sovereignty')]
        ret = uix.ListWnd(validNeighbors, None, localization.GetByLabel('UI/CharacterSelection/SystemCongested'), selectText, 1, scrollHeaders=scrollHeaders, minw=555, windowName='AlternativeSystemSelect')
        if ret:
            return ret[1]

    def Terminate(self, charID, *args):
        if not self.ready:
            eve.Message('Busy')
            return
        try:
            self.ready = 0
            characterData = self.GetCharacterSelectionData().GetCharInfo(charID)
            deletePrepTime = characterData.GetDeletePrepareTime()
            if deletePrepTime:
                now = blue.os.GetWallclockTime()
                if deletePrepTime < now:
                    self.DeleteCharacter(charID, characterData.charDetails.gender)
                else:
                    timeLeft = deletePrepTime - now
                    infoMsg = localization.GetByLabel('UI/CharacterSelection/AlreadyInBiomassQueue', charID=charID, timeLef=timeLeft)
                    eve.Message('CustomInfo', {'info': infoMsg})
            else:
                self.SubmitToBiomassQueue(charID)
        finally:
            self.ready = 1

    def DeleteCharacter(self, charID, gender):
        eve.Message('CCTerminate')
        if eve.Message('AskDeleteCharacter', {'charID': charID}, uiconst.YESNO) != uiconst.ID_YES:
            return
        self.ShowLoading()
        if gender == appConst.genderFemale:
            beginMsg = 'CCTerminateForGoodFemaleBegin'
            endMsg = 'CCTerminateForGoodFemale'
        else:
            beginMsg = 'CCTerminateForGoodMaleBegin'
            endMsg = 'CCTerminateForGoodMale'
        eve.Message(beginMsg)
        try:
            error = self.remoteCharacterSvc.DeleteCharacter(charID)
            eve.Message(endMsg)
        finally:
            self.HideLoading()
            self.ready = 1

        if error:
            eve.Message(error)
            return
        self.SetData(force=True)
        self.OnRefreshScreen()

    def SubmitToBiomassQueue(self, charID):
        if eve.Message('AskSubmitToBiomassQueue', {'charID': charID}, uiconst.YESNO) != uiconst.ID_YES:
            return
        ret = self.remoteCharacterSvc.PrepareCharacterForDelete(charID)
        if ret:
            eve.Message('SubmitToBiomassQueueConfirm', {'charID': charID,
             'when': ret - blue.os.GetWallclockTime()})
        self.UpdateSlot(charID)

    def UndoTermination(self, charID, *args):
        sm.RemoteSvc('charUnboundMgr').CancelCharacterDeletePrepare(charID)
        self.UpdateSlot(charID)

    def UpdateSlot(self, charID):
        self.GetCharacterSelectionData(force=True)
        slot = self.slotsByCharID.get(charID, None)
        if slot:
            characterDetails = self.GetCharacterSelectionData().GetCharInfo(charID)
            slot.RefreshCharacterDetails(characterDetails)
            slot.SetDeleteUI()
        else:
            self.OnRefreshScreen()

    def ShowLoading(self, forceOn = 0):
        try:
            self.loadingWheel.forcedOn = forceOn
            self.loadingWheel.Show()
        except:
            log.LogError('Failed to show the loading wheel')

    def HideLoading(self, forceOff = 0):
        try:
            if not self.loadingWheel.forcedOn or forceOff:
                self.loadingWheel.Hide()
                self.loadingWheel.forcedOn = 0
        except:
            log.LogError('Failed to hide the loading wheel')

    def _GetWarningHeight(self):
        if uicore.desktop.height < 810:
            return 1
        return WARNING_BANNER_HEIGHT

    def OnBannerAdDisplayed(self):
        self.adContainer.display = True
        self.openStoreContainer.align = uiconst.CENTERLEFT

    def OnBannerAdHidden(self):
        self.adContainer.display = False
        self.openStoreContainer.align = uiconst.CENTER


@Component(ButtonEffect(opacityIdle=0.0, opacityHover=1.4, opacityMouseDown=1.7, bgElementFunc=lambda parent, _: parent.highlight, audioOnEntry=uiconst.SOUND_BUTTON_HOVER))

class OpenStoreButton(Container):
    default_name = 'OpenStoreButton'
    default_width = 270
    default_height = 90
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.logo = Sprite(name='Logo', bgParent=self, texturePath='res:/UI/Texture/Vgs/storeLogo.png', align=uiconst.TOALL)
        self.highlight = Sprite(name='Highlight', bgParent=self, texturePath='res:/UI/Texture/Vgs/storeLogoGlow.png', align=uiconst.TOALL)
        if csUtil.IsMonochromeStyleEnabled():
            csUtil.SetMonochromeStyle(self.logo, True)
        self.onClick = attributes.onClick

    def OnClick(self):
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        self.onClick()
