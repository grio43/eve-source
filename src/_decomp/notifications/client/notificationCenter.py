#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\client\notificationCenter.py
import blue
from carbon.client.script.environment.AudioUtil import PlaySound
import carbonui.const as uiconst
from carbonui.decorative.panelUnderlay import PanelUnderlay
from carbonui.primitives.container import Container
from carbonui.primitives.line import Line
from carbonui.primitives.transform import Transform
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from carbonui.window.underlay import WindowUnderlay
from eve.client.script.ui.shared.neocom.corporation.corpPanelConst import CorpPanel
from eve.client.script.ui.shared.neocom.wallet.walletWnd import WalletWindow
from eve.client.script.ui.shared.pointerTool.pointerToolConst import UNIQUE_NAME_NOTIFICATION_FEED, UNIQUE_NAME_NOTIFICATION_CONTAINER, UNIQUE_NAME_NOTIFICATION_POPUP, UNIQUE_NAME_BADGE_MASTER
import eve.common.script.util.notificationconst as notificationConst
import eveprefs
import localization
from eve.common.lib import appConst
from notifications.client.controls.autoCloser import AutoCloser
from notifications.client.controls.badgeContainer import BadgeContainer
from notifications.client.controls.dragMovable import DragMovable
from notifications.client.controls.notificationEntry import NotificationEntry
from notifications.client.controls.notificationScrollContainer import NotificationScrollContainer
from notifications.client.controls.stackFader import StackFader
from notifications.client.mailInteractor import MailInteractor
from notifications.client.notificationCenterUtil import AlignmentTransitioner
from notifications.client.notificationCenterUtil import ExpandEvaluator
from notifications.client.notificationSettings.notificationSettingConst import ExpandAlignmentConst
from notifications.client.notificationSettings.notificationSettingHandler import NotificationSettingHandler
from notifications.client.notificationUIConst import NOTIFICATION_CENTER_WIDTH, NOTIFICATION_CENTER_PADDING_H
from notifications.common.formatters.contractAssigned import ContractAssignedFormatter
from notifications.common.formatters.contractAttention import ContractNeedsAttentionFormatter
from notifications.common.formatters.killMailBase import KillMailBaseFormatter
from notifications.common.notification import Notification
from seasons.client.util import OpenSeasonsWindow
from uihider import UiHiderMixin
import uthread

class NotificationCenter():
    __notifyevents__ = ['OnNotificationStackSizeChanged',
     'OnNotificationFadeTimeChanged',
     'OnNotificationAlignmentChanged',
     'OnSetDevice',
     'OnUIScalingChange',
     'OnUIColorsChanged']
    FADE_IN_SECONDS = 0.25
    FADE_OUT_SECONDS = 0.25

    def __init__(self, onReconstructCallBack, developerMode, audioCallback):
        self.audioCallback = audioCallback
        self.entryHeight = 52
        self.constructed = False
        self.reconstructCallBack = onReconstructCallBack
        self.widgetWidth = 32
        self.widgetHeight = 32
        self.popupEntryWidth = 300
        self.isDeveloperMode = developerMode
        self.historyHeader = None
        self.addictionWarning = None

    def capWidgetPosition(self):
        self.customY = min(max(0, self.customY), uicore.desktop.height - self.widgetHeight)
        self.customX = min(max(0, self.customX), uicore.desktop.width - self.widgetWidth)

    def LoadPositionValues(self):
        self.customX, self.customY = self.notificationSettingHandler.GetNotificationBadgeOffset()
        self.capWidgetPosition()
        self.expandEvaluator.SetWidgetInversePosition(self.customX, self.customY)

    def SavePositionValues(self):
        self.notificationSettingHandler.SetNotificationBadgeOffset((self.customX, self.customY))

    def _ConstructStackFader(self):
        isDown = self.verticalAlignment is ExpandAlignmentConst.EXPAND_ALIGNMENT_VERTICAL_DOWN
        multiplyer = -2 if isDown else 1
        self.stackFader = StackFader(container=self.stackFaderContainer, startPosition=(40, 100 * multiplyer), down=isDown, audioCallback=self.audioCallback, maxStackSize=self.notificationSettingHandler.GetStackSize(), stackTimeSeconds=self.notificationSettingHandler.GetFadeTime())

    def _initializeVariables(self, neededVerticalAlignment = None, neededHorizontalAlignment = None):
        self.cacheIsInitialized = False
        self.layer = uicore.layer.abovemain
        self.notificationSettingHandler = NotificationSettingHandler()
        self.badgeContainer = None
        self.badgeContainerContainer = None
        self.scrollList = None
        self.enablePositionDebug = False
        self.isShowingDrawer = False
        self.isAnimating = False
        self.displayingSingleNotification = False
        self.clickInterruptedByDrag = False
        self.RegisterForNotifyEvents()
        self.settingsButton = None
        self.leftLine = self.rightLine = self.topLine = self.bottomLine = None
        self.preferredHeight = self.notificationSettingHandler.GetPreferredHeight()
        wantedHorizontalAlignment = self.notificationSettingHandler.GetHorizontalExpandAlignment()
        wantedVerticalAlignment = self.notificationSettingHandler.GetVerticalExpandAlignment()
        self.wantedHorizontalAlignment = wantedHorizontalAlignment
        self.wantedVerticalAlignment = wantedVerticalAlignment
        self.neededVerticalAlignment = neededVerticalAlignment
        self.neededHorizontalAlignment = neededHorizontalAlignment
        self.verticalAlignment = neededVerticalAlignment if neededVerticalAlignment else wantedVerticalAlignment
        self.horizontalAlignment = neededHorizontalAlignment if neededHorizontalAlignment else wantedHorizontalAlignment
        self.expandEvaluator = ExpandEvaluator(screenWidth=uicore.desktop.width, screenHeight=uicore.desktop.height, preferredHeight=self.preferredHeight, minHistoryHeight=self.notificationSettingHandler.MIN_HISTORY_HEIGHT, maxHistoryHeight=self.notificationSettingHandler.MAX_HISTORY_HEIGHT, expandWidth=NOTIFICATION_CENTER_WIDTH)
        self.transitioner = AlignmentTransitioner(verticalAlignment=self.verticalAlignment, horizontalAlignment=self.horizontalAlignment, wantedVertical=self.notificationSettingHandler.GetVerticalExpandAlignment(), wantedHorizontal=self.notificationSettingHandler.GetHorizontalExpandAlignment(), expandEvaluator=self.expandEvaluator)

    def SetCacheIsInitialized(self, isInitialized):
        self.cacheIsInitialized = isInitialized
        if self.cacheIsInitialized:
            self._EnableUI()
        else:
            self._DisableUI()

    def _DisableUI(self):
        self.controlBottomContainer.state = uiconst.UI_DISABLED

    def _EnableUI(self):
        self.controlBottomContainer.state = uiconst.UI_PICKCHILDREN

    def Construct(self, notificationProviderFunction, neededVerticalAlignment = None, neededHorizontalAlignment = None):
        self.notificationProviderFunction = notificationProviderFunction
        self._initializeVariables(neededVerticalAlignment, neededHorizontalAlignment)
        self.LoadPositionValues()
        self.verticalAlignment = self.transitioner.GetActualVerticalAlignment()
        self.horizontalAlignment = self.transitioner.GetActualHorizontalAlignment()
        self._ConstructUI()
        self.constructed = True

    def _GetAdjustedCustomX(self):
        if self.horizontalAlignment is ExpandAlignmentConst.EXPAND_ALIGNMENT_HORIZONTAL_RIGHT:
            return self.customX - NOTIFICATION_CENTER_WIDTH + self.widgetWidth
        else:
            return self.customX

    def GetCurrentMousePosition(self):
        return (uicore.uilib.x, uicore.uilib.y)

    def SetBadgeValue(self, value):
        if self.badgeContainer:
            self.badgeContainer.SetBadgeValue(value)

    def showBadge(self):
        if self.badgeContainer:
            self.badgeContainer.ShowBadge()

    def hideBadge(self):
        if self.badgeContainer:
            self.badgeContainer.HideBadge()

    def GetContainerArea(self):
        area = self.notificationContainer.GetAbsolute()
        return area

    def _AutoPositionNotificationContainer(self, widgetWidth):
        if self.notificationContainer:
            contWidth = max(widgetWidth, self.notificationContainer.width)
            self.notificationContainer.left = self.expandEvaluator.actualX - contWidth
            self.notificationContainer.top = self.expandEvaluator.actualY - self.notificationContainer.height

    def _AutoPositionBadgeContainer(self, widgetWidth):
        if self.badgeContainerContainer:
            area = self.GetClosedArea()
            leftplus = 0
            if self.horizontalAlignment is ExpandAlignmentConst.EXPAND_ALIGNMENT_HORIZONTAL_RIGHT:
                leftplus = widgetWidth
            self.badgeContainerContainer.left = area[0] + leftplus * 2 + 8
            self.badgeContainerContainer.top = area[1] + 6

    def _AutoPositionStackFader(self):
        if self.stackFader:
            x = self.expandEvaluator.actualX
            y = self.expandEvaluator.actualY
            if self.horizontalAlignment is ExpandAlignmentConst.EXPAND_ALIGNMENT_HORIZONTAL_RIGHT:
                x = x + self.popupEntryWidth - self.widgetWidth
            if self.verticalAlignment is ExpandAlignmentConst.EXPAND_ALIGNMENT_VERTICAL_UP:
                self.stackFader.SetAnchorPosition((x - self.popupEntryWidth, y - self.widgetHeight))
            else:
                self.stackFader.SetAnchorPosition((x - self.popupEntryWidth, y))

    def AutoPositionContainer(self):
        self._AutoPositionNotificationContainer(self.widgetWidth)
        self._AutoPositionBadgeContainer(self.widgetWidth)
        self._AutoPositionStackFader()
        if self.enablePositionDebug:
            self._AutoPositionGuidelines()

    def deconstruct(self):
        if self.constructed:
            self.CleanUpNotifyEvents()
            self.notificationContainer.Close()
            self.badgeContainerContainer.Close()
            self.stackFaderContainer.Close()
            if self.stackFader:
                self.stackFader.Cleanup()
            if self.enablePositionDebug:
                self._DestroyGuideLines()
            if self.dragMovable:
                self.dragMovable.StopDragMode()
                self.dragMovable = None
            self.constructed = False

    def CleanUpNotifyEvents(self):
        sm.UnregisterNotify(self)

    def RegisterForNotifyEvents(self):
        sm.RegisterNotify(self)

    def OnUIColorsChanged(self):
        if not self.isShowingDrawer:
            uthread.new(self.FadeOutHeaders)

    def OnUIScalingChange(self, args):
        self.OnSetDevice()

    def OnSetDevice(self):
        savedX = self.expandEvaluator.actualX
        savedY = self.expandEvaluator.actualY
        self.expandEvaluator.SetScreenSize(width=uicore.desktop.width, height=uicore.desktop.height)
        if self.horizontalAlignment == ExpandAlignmentConst.EXPAND_ALIGNMENT_HORIZONTAL_RIGHT:
            self.expandEvaluator.SetWidgetPositon(savedX, self.expandEvaluator.actualY)
            self.customX = self.expandEvaluator.customX
            self.SavePositionValues()
        if self.verticalAlignment == ExpandAlignmentConst.EXPAND_ALIGNMENT_VERTICAL_DOWN:
            self.expandEvaluator.SetWidgetPositon(self.expandEvaluator.actualX, savedY)
            self.customY = self.expandEvaluator.customY
            self.SavePositionValues()
        self.dragMovable.customX = self.customX
        self.dragMovable.customY = self.customY
        self.AutoPositionContainer()
        self._adjustAlignment()

    def GetUnwantedIds(self):
        unwanted = []
        settings = NotificationSettingHandler().LoadSettings()
        for k, v in settings.iteritems():
            if v.showAtAll == False:
                unwanted.append(k)

        return unwanted

    def MakeAndDisplayNormalNotification(self, notification):
        settingObject = self.notificationSettingHandler.LoadSettings()
        thisTypeSetting = settingObject.get(notification.typeID)
        if not thisTypeSetting:
            from notifications.client.notificationSettings.notificationSettingHandler import NotificationSettingData
            thisTypeSetting = NotificationSettingData(notificationID=notification.typeID, showPopup=True, showAtAll=True, group=-1)
        isAlwaysPopupType = notification.typeID in notificationConst.notificationAlwaysPopup
        if isAlwaysPopupType or thisTypeSetting.showPopup and self.notificationSettingHandler.GetPopupsEnabled():
            self.displayingSingleNotification = True
            entry = None
            if notification.metaType is Notification.NORMAL_NOTIFICATION:
                entry = self._ConstructNotificationPopup(notification)
            elif notification.metaType is Notification.CONTACT_NOTIFICATION:
                entry = self._ConstructNotificationContactPopup(notification)
            entry.LoadContent()
            entry.OnClick = self.GetNotificationAction(entry, notification)
            self.displayingEntry = entry
            self.stackFader.AddItem(entry)

    def DisplaySingleNotification(self, notification):
        self.MakeAndDisplayNormalNotification(notification)

    def OpenKillReport(self, notification):
        import eve.client.script.ui.shared.killReportUtil as killReportUtil
        kmID, kmHash = KillMailBaseFormatter.GetKillMailIDandHash(notification.data)
        theRealKm = sm.RemoteSvc('warStatisticMgr').GetKillMail(kmID, kmHash)
        killReportUtil.OpenKillReport(theRealKm)

    def OnEntryClick(self, entry, notification):
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        if notification.metaType == Notification.CONTACT_NOTIFICATION:
            characterID = notification.senderID
            sm.GetService('info').ShowInfo(cfg.eveowners.Get(characterID).typeID, characterID)
        elif notification.typeID == notificationConst.notificationTypeSkillFinished:
            skillIds = notification.data.get('callbackargs', [])
            sm.StartService('charactersheet').ForceShowSkillHistoryHighlighting(skillIds)
        elif notification.typeID in (notificationConst.notificationTypeSkillEmptyQueue, notificationConst.notificationTypeUnusedSkillPoints, notificationConst.notificationTypeSkillInjected):
            from eve.client.script.ui.skillPlan.skillPlanDockablePanel import SkillPlanDockablePanel
            SkillPlanDockablePanel.Open()
        elif notification.typeID == notificationConst.notificationTypeSkillsAddedFromSkillPlan:
            pass
        elif notification.typeID == notificationConst.notificationTypeSeasonalChallengeCompleted:
            OpenSeasonsWindow()
        elif notification.typeID in (notificationConst.notificationTypeImplantPluggedIn, notificationConst.notificationTypeBoosterConsumed):
            from eve.client.script.ui.shared.neocom.characterSheetWindow import CharacterSheetWindow
            CharacterSheetWindow.OpenImplantsAndBoosters()
        elif notification.typeID == notificationConst.notificationTypeMailSummary:
            sm.GetService('cmd').OpenMail()
        elif notification.typeID == notificationConst.notificationTypeNewMailFrom:
            sm.GetService('mailSvc').OnOpenPopupMail(notification.data['msg'])
        elif notification.typeID == notificationConst.notificationTypeGameTimeAdded:
            sm.GetService('charactersheet').OpenPlexPanel()
        elif notification.typeID == notificationConst.notificationTypeContractNeedsAttention:
            contractSvc = sm.GetService('contracts')
            count = ContractNeedsAttentionFormatter.GetNeedsAttentionFromData(notification.data)
            if count == 1:
                contractSvc.ShowContract(ContractNeedsAttentionFormatter.GetFirstContractId(notification.data))
            else:
                isForCorp = ContractNeedsAttentionFormatter.GetIsForCorp(notification.data)
                contractSvc.ShowContracts(status=0, forCorp=isForCorp)
        elif notification.typeID == notificationConst.notificationTypeContractAssigned:
            contractSvc = sm.GetService('contracts')
            count = ContractAssignedFormatter.GetAssignedCount(notification.data)
            if count == 1:
                contractSvc.ShowContract(ContractAssignedFormatter.GetContractID(notification.data))
            else:
                contractSvc.ShowAssignedTo()
        elif notification.typeID == notificationConst.notificationTypeContractAccepted:
            contractSvc = sm.GetService('contracts')
            contractSvc.ShowContract(notification.data['contractId'])
        elif notification.typeID in [notificationConst.notificationTypeKillReportFinalBlow, notificationConst.notificationTypeKillReportVictim]:
            self.OpenKillReport(notification)
        elif notification.typeID == notificationConst.notificationTypeCorpAppNewMsg:
            sm.GetService('corpui').Show(CorpPanel.RECRUITMENT_APPLICATIONS)
        elif notification.typeID in (notificationConst.notificationTypeCorpAppInvitedMsg,
         notificationConst.notificationTypeCorpAppAcceptMsg,
         notificationConst.notificationTypeCorpAppRejectMsg,
         notificationConst.notificationTypeCorpAppRejectCustomMsg):
            sm.GetService('corpui').Show(CorpPanel.MY_APPLICATIONS)
        elif notification.typeID in notificationConst.groupTypes[notificationConst.groupCCPNotifications]:
            eve.Message('CustomInfo', {'info': notification.data['text']}, modal=False)
            sm.RemoteSvc('notificationMgr').LogNotificationInteraction(notification.data.get('reference_id', None))
        elif notification.typeID == notificationConst.notificationTypeTicketReply:
            import webbrowser
            petitioner = sm.RemoteSvc('petitioner')
            if eveprefs.boot.region == 'optic':
                pass
            else:
                webbrowser.open_new(petitioner.GetZendeskJwtLink(ticketID=notification.data['text']))
        elif notification.typeID == notificationConst.notificationTypeServerShutdown:
            eve.Message('CustomInfo', {'info': notification.data['text']}, modal=False)
        elif notification.typeID == notificationConst.notificationTypeCalendarEvent:
            sm.GetService('calendar').OpenEventWnd(notification.data['eventInfo'])
        elif notification.typeID == notificationConst.notificationTypeNPCStandingsChanged:
            from eve.client.script.ui.shared.neocom.characterSheetWindow import CharacterSheetWindow
            CharacterSheetWindow.OpenStandings()
            sm.ScatterEvent('OnStandingNotificationClicked', entryToOpen=notification.data[0][0])
        elif notification.typeID == notificationConst.notificationTypeAlphaInjectorAvailable:
            sm.GetService('info').ShowInfo(appConst.typeAlphaTrainingInjector)
        elif notification.typeID == notificationConst.notificationTypeCharMedalMsg:
            from eve.client.script.ui.shared.neocom.characterSheetWindow import CharacterSheetWindow
            CharacterSheetWindow.OpenDecorations()
        elif notification.typeID == notificationConst.notificationTypeGameTimeReceived:
            from eve.client.script.ui.shared.cloneGrade.cloneUpgradeWindow import CloneUpgradeWindow
            CloneUpgradeWindow.ShowFanfare(giftData=notification.data)
        elif notification.typeID == notificationConst.notificationTypeCorpAllBillMsg:
            WalletWindow.OpenCorpWallet()
        elif notification.typeID in notificationConst.groupTypes[notificationConst.groupRaffle]:
            sm.GetService('raffleSvc').open_link(notification.data['raffle_id'])
        elif notification.typeID in [notificationConst.notificationTypeEssMainBankLink, notificationConst.notificationTypeEssLinkDisconnected, notificationConst.notificationTypeEssInventoryFull]:
            pass
        elif notification.typeID == notificationConst.notificationTypeEssReserveBankUnlocked:
            pass
        elif notification.typeID in [notificationConst.notificationTypeCorpCosmeticLicensePurchased, notificationConst.notificationTypeAllianceCosmeticLicensePurchased]:
            pass
        elif notification.typeID == notificationConst.notificationTypeDailyGoalCompleted:
            from jobboard.client import open_daily_goal
            open_daily_goal(notification.data['goalID'])
        elif notification.typeID in (notificationConst.notificationTypeDailyMilestoneCompleted, notificationConst.notificationTypeDailyRewardTrackCompleted):
            from jobboard.client import open_browse_page
            from metadata.common.content_tags import ContentTags
            open_browse_page(content_tag_id=ContentTags.feature_daily_goals)
        elif notification.typeID in notificationConst.groupTypes[notificationConst.groupInsurgencies]:
            sm.GetService('cmd').OpenInsurgencyDashboard()
        elif notification.typeID == notificationConst.notificationTypeShipGroupUnlocked:
            sm.GetService('shipTreeUI').Open()
        else:
            MailInteractor().SelectByNotificationID(notification.notificationID, notificationTypeID=notification.typeID)

    def ClearNotification(self):
        if self.scrollList and not self.isShowingDrawer:
            self.scrollList.Flush()

    def OnWidgetButtonClick(self):
        self.dragMovable.Interrupt()
        self.clickedInMeanTime = True
        if self.clickInterruptedByDrag:
            self.clickInterruptedByDrag = False
            return
        if self.isShowingDrawer:
            self.CloseDrawer()
        else:
            self.OpenDrawer()

    def onWidgetDragFinished(self):
        self.SavePositionValues()
        self._adjustAlignment()

    def onWidgetDragEnter(self):
        self.clickInterruptedByDrag = True

    def onWidgetDrag(self, x, y):
        self.customX = x
        self.customY = y
        self.capWidgetPosition()
        self.dragMovable.customX = self.customX
        self.dragMovable.customY = self.customY
        self.expandEvaluator.SetWidgetInversePosition(self.customX, self.customY)
        self.AutoPositionContainer()

    def OnNotificationAlignmentChanged(self, *args):
        if self.wantedHorizontalAlignment is not self.notificationSettingHandler.GetHorizontalExpandAlignment() or self.wantedVerticalAlignment is not self.notificationSettingHandler.GetVerticalExpandAlignment():
            self.wantedHorizontalAlignment = self.notificationSettingHandler.GetHorizontalExpandAlignment()
            self.wantedVerticalAlignment = self.notificationSettingHandler.GetVerticalExpandAlignment()
            self.transitioner.wantedVerticalAlignment = self.notificationSettingHandler.GetVerticalExpandAlignment()
            self.transitioner.wantedHorizontalAlignment = self.notificationSettingHandler.GetHorizontalExpandAlignment()
            self._adjustAlignment()

    def OnNotificationFadeTimeChanged(self, value):
        if self.stackFader:
            self.stackFader.SetStackTimeSeconds(value)

    def OnNotificationStackSizeChanged(self, value):
        if self.stackFader:
            self.stackFader.SetStackSize(value)

    def OnResizeLineMouseDown(self, *args):
        if not self.isShowingDrawer:
            return
        self.dragThing = self.notificationContainer
        self.startDragHeight = self.dragThing.height
        self.startDragY = uicore.uilib.y
        self.startDragTop = self.dragThing.top
        if uicore.uilib.leftbtn:
            uthread.new(self.OnResizerDrag)

    def _OnResizerResize(self, diff):
        wantedHeight = self.startDragHeight + diff
        adjustedWantedHeight = min(max(wantedHeight, self.notificationSettingHandler.MIN_HISTORY_HEIGHT + self.widgetHeight), self.notificationSettingHandler.MAX_HISTORY_HEIGHT + 2)
        self.dragThing.height = adjustedWantedHeight
        self.preferredHeight = adjustedWantedHeight
        self.expandEvaluator.preferredHeight = adjustedWantedHeight
        self.notificationSettingHandler.SetPreferredHeight(adjustedWantedHeight)

    def OnResizerDrag(self, *args):
        self.isResizing = True
        self.activeAutoCloser.Pause()
        x, y, endWidth, endHeightValue = self.GetClosedArea()
        minY = y - self.notificationSettingHandler.MIN_HISTORY_HEIGHT
        while uicore.uilib.leftbtn:
            diff = self.startDragY - uicore.uilib.y
            if self.verticalAlignment is ExpandAlignmentConst.EXPAND_ALIGNMENT_VERTICAL_DOWN:
                diff = -diff
            self._OnResizerResize(diff)
            if self.verticalAlignment is ExpandAlignmentConst.EXPAND_ALIGNMENT_VERTICAL_UP:
                self.dragThing.top = min(self.startDragTop - diff, minY)
            blue.synchro.SleepWallclock(1)

        self.isResizing = False
        self.activeAutoCloser.UnPause()

    def OnSettingsClick(self, *args):
        from notifications.client.controls.notificationSettingsWindow import NotificationSettingsWindow
        NotificationSettingsWindow.ToggleOpenClose()

    def SetupDrawerAutoCloser(self):
        self.activeAutoCloser = AutoCloser(None, self.OnAutoCloserFire, self.notificationContainer, thresholdInSeconds=1.0, buffer=10)
        self.activeAutoCloser.monitor()
        self.watcherThread = uthread.new(self.ScrollWatcherThread)

    def ScrollWatcherThread(self):
        while True:
            nowvalue = self.scrollList._scrollbar_vertical.scrolling
            if nowvalue != self.lastobservedValue:
                if nowvalue:
                    self.activeAutoCloser.Abort()
                else:
                    self.SetupDrawerAutoCloser()
            self.lastobservedValue = self.scrollList._scrollbar_vertical.scrolling
            blue.synchro.Yield()

    def OnAutoCloserFire(self, autocloser):
        self.CloseDrawer()

    def FillWithNotifications(self, notifications):
        unwantedIDs = self.GetUnwantedIds()
        maxFill = 999
        self.scrollList.EnableEntryLoad()
        for i, notification in enumerate(notifications):
            if not self.scrollList or self.scrollList.destroyed or not self.isShowingDrawer:
                return
            if notification.typeID in unwantedIDs:
                continue
            if i > maxFill:
                break
            if notification.metaType is Notification.NORMAL_NOTIFICATION:
                entry = self._ConstructNormalNotificationListEntry(notification, parent=self.scrollList)
                entry.OnClick = self.GetNotificationAction(entry, notification)
            elif notification.metaType is Notification.CONTACT_NOTIFICATION:
                entry = self._ConstructContactNotificationListEntry(notification, parent=self.scrollList)
                entry.OnClick = (self.OnEntryClick, entry, notification)
            blue.pyos.BeNice()

        self.scrollList.LoadVisibleEntries()

    def GetNotificationAction(self, entry, notification):
        if hasattr(notification, 'Activate'):
            return notification.Activate
        else:
            return (self.OnEntryClick, entry, notification)

    def CloseDrawer(self):
        if self.isAnimating:
            return
        self.isAnimating = True
        self.scrollList.DisableEntryLoad()
        if self.activeAutoCloser:
            self.activeAutoCloser.Abort()
            self.activeAutoCloser = None
            self.watcherThread.kill()
            self.watcherThread = None
        self.isShowingDrawer = False
        self._frameCloseAnimation()

    def ReconstructWithAlignments(self, neededVerticalAlignment = None, neededHorizontalAlignment = None, reOpen = False):
        self.deconstruct()
        self.Construct(self.notificationProviderFunction, neededVerticalAlignment=neededVerticalAlignment, neededHorizontalAlignment=neededHorizontalAlignment)
        self.reconstructCallBack()
        if reOpen:
            self.OpenDrawer()

    def _adjustAlignment(self):
        adjustedV = self.transitioner.GetActualVerticalAlignment()
        adjustedH = self.transitioner.GetActualHorizontalAlignment()
        if adjustedV != self.verticalAlignment or adjustedH != self.horizontalAlignment:
            self.ReconstructWithAlignments()

    def _realignIfNeeded(self):
        didRealign = False
        if self.transitioner.CheckChangeBackNeeded():
            willSwitchHAlign = self.transitioner.CheckHorizontalAlignBackNeeded()
            willSwitchVAlign = self.transitioner.CheckVerticalAlignBackNeeded()
            self.ReconstructWithAlignments(neededVerticalAlignment=willSwitchVAlign, neededHorizontalAlignment=willSwitchHAlign)
            didRealign = True
        return didRealign

    def StartOpenAnimation(self, endHeightValue, endTopValue, obj):
        animation = uicore.animations.MorphScalar
        duration = self.FADE_IN_SECONDS
        self.FadeInHeaders()
        if endTopValue != obj.top:
            animation(obj, 'top', startVal=obj.top, endVal=endTopValue, duration=duration)
        animation(obj, 'height', startVal=obj.height, endVal=endHeightValue, duration=duration)
        animation(obj, 'width', startVal=obj.width, endVal=NOTIFICATION_CENTER_WIDTH, duration=duration, callback=self._postOpenAnimation)
        if self.horizontalAlignment is ExpandAlignmentConst.EXPAND_ALIGNMENT_HORIZONTAL_LEFT:
            endleftpoint = self.expandEvaluator.actualX - NOTIFICATION_CENTER_WIDTH
            animation(obj, 'left', startVal=obj.left, endVal=endleftpoint, duration=duration)

    def _frameOpenAnimation(self):
        self.dragMovable.SetEnabled(False)
        obj = self.notificationContainer
        endHeightValue = 400
        height = uicore.desktop.height
        endTopValue = obj.top
        self.audioCallback('notify_slide_open_play')
        if True:
            if self.verticalAlignment is ExpandAlignmentConst.EXPAND_ALIGNMENT_VERTICAL_UP:
                if self.expandEvaluator.CanExpandUp():
                    endHeightValue = self.expandEvaluator.GetAdjustedHeightValue()
                    endTopValue = height - endHeightValue - self.customY
            elif self.expandEvaluator.CanExpandDown():
                endHeightValue = self.expandEvaluator.GetAdjustedHeightForDownExpand()
            self.StartOpenAnimation(endHeightValue, endTopValue, obj)

    def FadeInHeaders(self):
        for container in [self.historyHeader, self.addictionWarning]:
            if container:
                uicore.animations.FadeIn(container, duration=self.FADE_IN_SECONDS)

    def FadeOutHeaders(self):
        for container in [self.historyHeader, self.addictionWarning]:
            if container:
                uicore.animations.FadeOut(container, duration=self.FADE_OUT_SECONDS)

    def FadeInSettingsButton(self):
        if not self.settingsButton:
            self._ConstructSettingsButton()
        uicore.animations.FadeIn(self.settingsButton, duration=self.FADE_IN_SECONDS)

    def FadeOutSettingsButton(self):
        if self.settingsButton:
            uicore.animations.FadeOut(self.settingsButton, duration=self.FADE_OUT_SECONDS)

    def _postOpenAnimation(self):
        notifications = self.notificationProviderFunction()
        uthread.new(self.FillWithNotifications, notifications)
        self.FadeInSettingsButton()
        self._EnableResize()
        self.isAnimating = False

    def GetClosedArea(self):
        obj = self.notificationContainer
        endWidth = self.widgetWidth
        endHeight = self.widgetHeight
        bottomContainerHeight = 0
        endHeightValue = endHeight + bottomContainerHeight
        heightDifference = obj.height - endHeightValue
        endTopValue = obj.top + heightDifference
        widthDifference = obj.width - endWidth
        if self.horizontalAlignment is ExpandAlignmentConst.EXPAND_ALIGNMENT_HORIZONTAL_LEFT:
            x = obj.left + widthDifference
        else:
            x = obj.left
        y = endTopValue
        return (x,
         y,
         endWidth,
         endHeightValue)

    def _frameCloseAnimation(self):
        self.isClosing = True
        self.dragMovable.SetEnabled(False)
        self.FadeOutSettingsButton()
        self.FadeOutHeaders()
        animation = uicore.animations.MorphScalar
        duration = self.FADE_OUT_SECONDS
        obj = self.notificationContainer
        x, y, w, h = self.GetClosedArea()
        self.audioCallback('notify_slide_close_play')
        animation(obj, 'height', startVal=obj.height, endVal=h, duration=duration)
        if self.verticalAlignment is ExpandAlignmentConst.EXPAND_ALIGNMENT_VERTICAL_UP:
            animation(obj, 'top', startVal=obj.top, endVal=y, duration=duration)
        animation(obj, 'width', startVal=obj.width, endVal=w, duration=duration, callback=self._postCloseAnimation)
        if self.horizontalAlignment is ExpandAlignmentConst.EXPAND_ALIGNMENT_HORIZONTAL_LEFT:
            animation(obj, 'left', startVal=obj.left, endVal=x, duration=duration)

    def _postCloseAnimation(self):
        self.FadeOutHeaders()
        self.dragMovable.SetEnabled(True)
        self._DisableResize()
        uthread.new(self.__CleanUpDrawer)

    def __CleanUpDrawer(self):
        self.ClearNotification()
        self.isClosing = False
        self.dragMovable.SetEnabled(True)
        self.isAnimating = False

    def OpenDrawer(self):
        if self.isAnimating:
            return
        self.isShowingDrawer = True
        self.isAnimating = True
        self._frameOpenAnimation()
        self.SetupDrawerAutoCloser()

    def _ConstructUI(self):
        self.stackFaderContainer = NotificationPopupContainer(parent=self.layer)
        self._ConstructStackFader()
        self._ConstructBadge()
        self.notificationContainer = NotificationContainer(parent=self.layer, align=uiconst.TOPLEFT, width=self.widgetWidth, height=self.widgetHeight, clipChildren=True)
        self.subNotificationContainer = Transform(name='SubNotificationContainer', parent=self.notificationContainer, align=uiconst.TOALL, clipChildren=True)
        self.actualUnderlay = WindowUnderlay(parent=self.notificationContainer)
        self.topContainer = Container(name='topContainer', parent=self.subNotificationContainer, align=uiconst.TOALL, padding=(0, 0, 0, 0))
        self.AutoPositionContainer()
        self._ConstructNotificationArea()
        if self.enablePositionDebug:
            self._ConstructGuideLines()
        self.AutoPositionContainer()
        self.FadeOutHeaders()

    def _ConstructSettingsButton(self):
        if self.horizontalAlignment is ExpandAlignmentConst.EXPAND_ALIGNMENT_HORIZONTAL_LEFT:
            buttonAlignment = uiconst.TOLEFT
        else:
            buttonAlignment = uiconst.TORIGHT
        self.settingsButton = ButtonIcon(name='MyButtonIcon2', parent=self.controlBottomContainer, align=buttonAlignment, width=24, height=24, iconSize=24, texturePath='res:/UI/Texture/Icons/77_32_30.png', func=self.OnSettingsClick, hint=localization.GetByLabel('Notifications/NotificationWidget/NotificationSettingsTooltip'), padding=(5, 0, 5, 0), opacity=0)

    def _LoadWidgetTooltipPanel(self, tooltipPanel, *args):
        if self.dragMovable.IsDragging():
            return
        tooltipPanel.LoadGeneric1ColumnTemplate()
        tooltipPanel.AddLabelShortcut(localization.GetByLabel('Notifications/NotificationWidget/NotificationWidgetTooltip'), None)
        tooltipPanel.AddLabelMedium(text=localization.GetByLabel('Notifications/NotificationWidget/NotificationWidgetTooltipDesc'), wrapWidth=200)

    def _ConstructResizeLine(self):
        if self.verticalAlignment is ExpandAlignmentConst.EXPAND_ALIGNMENT_VERTICAL_UP:
            resizeAlignment = uiconst.TOTOP
        else:
            resizeAlignment = uiconst.TOBOTTOM
        self.resizeLineCont = Container(parent=self.windowunderlay, name='resizeLineCont', align=uiconst.TOALL)
        self.resizeLine = Line(parent=self.resizeLineCont, color=(0, 0, 0, 0), align=resizeAlignment, weight=3, state=uiconst.UI_NORMAL)
        self.resizeLine.OnMouseDown = self.OnResizeLineMouseDown
        self.resizeLine.cursor = uiconst.UICURSOR_TOP_BOTTOM_DRAG
        self._DisableResize()

    def _DisableResize(self):
        self.resizeLine.state = uiconst.UI_DISABLED

    def _EnableResize(self):
        self.resizeLine.state = uiconst.UI_NORMAL

    def _ConstructNotificationArea(self):
        self.windowunderlay = Container(parent=self.topContainer, name='windowUnderlay', align=uiconst.TOALL)
        self._ConstructResizeLine()
        self._ConstructHistoryHeader()
        self._ConstructControlContainer()
        self._ConstructScroll()

    def _ConstructHistoryHeader(self):
        self.historyHeader = Container(name='HistoryContainer', parent=self.windowunderlay, align=uiconst.TOTOP, height=13, padding=(0, 4, 0, 0), clipChildren=True, opacity=0.0)
        self.historyHeaderLabel = EveLabelSmall(name='history', parent=self.historyHeader, align=uiconst.CENTER, text=localization.GetByLabel('Notifications/NotificationWidget/NotificationHistoryCaption'), bold=True)
        self.historyHeader.height = max(self.historyHeader.height, self.historyHeaderLabel.textheight + 2)

    def _ConstructControlContainer(self):
        if self.verticalAlignment is ExpandAlignmentConst.EXPAND_ALIGNMENT_VERTICAL_UP:
            controlContainerAlignment = uiconst.TOBOTTOM
        else:
            controlContainerAlignment = uiconst.TOTOP
        ctop = 0
        if self.verticalAlignment is ExpandAlignmentConst.EXPAND_ALIGNMENT_VERTICAL_DOWN:
            ctop = -self.historyHeader.height - 4
        self.controlBottomContainer = Transform(parent=self.windowunderlay, name='buttonControlContainer', align=controlContainerAlignment, height=32, width=32, top=ctop, clipChilren=False)
        buttonAlignment = uiconst.TORIGHT
        if self.horizontalAlignment is ExpandAlignmentConst.EXPAND_ALIGNMENT_HORIZONTAL_RIGHT:
            buttonAlignment = uiconst.TOLEFT
        self.widgetButton2 = ButtonIcon(name='WidgetIcon', uniqueUiName=UNIQUE_NAME_NOTIFICATION_FEED, align=buttonAlignment, width=32, height=32, iconSize=32, texturePath='res:/UI/Texture/classes/Notifications/widgetIcon.png', func=self.OnWidgetButtonClick)
        self.widgetButton2.LoadTooltipPanel = self._LoadWidgetTooltipPanel
        self.controlBottomContainer.children.append(self.widgetButton2)
        self.dragMovable = DragMovable(self.notificationContainer, buttonObject=self.widgetButton2, onDrag=self.onWidgetDrag, onDragEnter=self.onWidgetDragEnter, onDragFinished=self.onWidgetDragFinished, startPosition=(self.customX, self.customY))

    def _ConstructScroll(self):
        isExpandAlignmentVerticalUp = self.verticalAlignment == ExpandAlignmentConst.EXPAND_ALIGNMENT_VERTICAL_UP
        paddingBottom = 0 if isExpandAlignmentVerticalUp else NOTIFICATION_CENTER_PADDING_H
        self.scrollList = NotificationScrollContainer(name='myScrollCont', parent=self.windowunderlay, align=uiconst.TOALL, padding=(NOTIFICATION_CENTER_PADDING_H,
         0,
         NOTIFICATION_CENTER_PADDING_H,
         paddingBottom))
        self.lastobservedValue = self.scrollList._scrollbar_vertical.scrolling
        self.underlay = PanelUnderlay(bgParent=self.scrollList)

    def _ConstructNormalNotificationListEntry(self, notification, parent = None):
        entry = NotificationEntry(parent=parent, align=uiconst.NOALIGN, created=notification.created, notification=notification, developerMode=self.isDeveloperMode)
        return entry

    def _ConstructContactNotificationListEntry(self, notification, parent = None):
        entry = NotificationEntry(parent=parent, align=uiconst.NOALIGN, created=notification.created, notification=notification, developerMode=self.isDeveloperMode)
        return entry

    def _ConstructNotificationPopup(self, notification, parent = None):
        entry = NotificationEntry(parent=parent, align=uiconst.TOPLEFT, created=0, title=notification.subject, width=self.popupEntryWidth, notification=notification)
        return entry

    def _ConstructNotificationContactPopup(self, notification, parent = None):
        entry = NotificationEntry(parent=parent, align=uiconst.TOPLEFT, created=0, title=notification.subject, width=self.popupEntryWidth, notification=notification)
        return entry

    def _ConstructBadge(self):
        self.badgeContainerContainer = BadgeMasterContainer(align=uiconst.TOPLEFT, parent=self.layer, clipChildren=False, height=20, width=100, left=100, top=100)
        leftmultiplyer = 1 if self.horizontalAlignment is ExpandAlignmentConst.EXPAND_ALIGNMENT_HORIZONTAL_LEFT else -1
        self.badgeContainer = BadgeContainer(name='BadgeContainer', align=uiconst.TOPLEFT, parent=self.badgeContainerContainer, height=20, left=-120 * leftmultiplyer, opacity=0, pointfromleft=self.horizontalAlignment is ExpandAlignmentConst.EXPAND_ALIGNMENT_HORIZONTAL_LEFT)

    def _MakeGuideLine(self, name, width, height, color):
        return Line(name=name, align=uiconst.TOPLEFT, weight=2, opacity=1.0, parent=self.layer, width=width, height=height, color=color)

    def _ConstructGuideLines(self):
        self.centerDot = Line(name='centerDot', align=uiconst.TOPLEFT, weight=2, opacity=1.0, parent=self.layer, width=2, height=2, color=(0.6, 0.6, 0.6))
        self.leftLine = self._MakeGuideLine(name='leftline', width=10, height=2, color=(1, 0, 0))
        self.rightLine = self._MakeGuideLine(name='rightline', width=10, height=2, color=(0, 1, 0))
        self.topLine = self._MakeGuideLine(name='topLine', width=10, height=2, color=(0, 0, 1))
        self.bottomLine = self._MakeGuideLine(name='bottomLine', width=10, height=2, color=(0.5, 0.5, 1))
        self.allLines = [self.leftLine,
         self.rightLine,
         self.topLine,
         self.bottomLine,
         self.centerDot]

    def _AutoPositionGuidelines(self):
        if self.leftLine:
            for line in self.allLines:
                line.left = self.expandEvaluator.actualX
                line.top = self.expandEvaluator.actualY

            self.leftLine.left -= 10
            self.topLine.top -= 10
            self.bottomLine.opacity = float(self.expandEvaluator.CanExpandDown())
            self.topLine.opacity = float(self.expandEvaluator.CanExpandUp())
            self.leftLine.opacity = float(self.expandEvaluator.CanExpandLeft())
            self.rightLine.opacity = float(self.expandEvaluator.CanExpandRight())

    def _DestroyGuideLines(self):
        for line in self.allLines:
            line.Close()

        self.allLines = []


class BadgeMasterContainer(UiHiderMixin, Container):
    default_name = 'badgeMasterContainer'
    uniqueUiName = UNIQUE_NAME_BADGE_MASTER

    def ApplyAttributes(self, attributes):
        super(BadgeMasterContainer, self).ApplyAttributes(attributes)

    def AnimateReveal(self):
        self.Show()
        animations.FadeTo(self, duration=0.25, curveType=uiconst.ANIM_LINEAR)


class NotificationPopupContainer(UiHiderMixin, Container):
    default_name = 'notificationPopupContainer'
    uniqueUiName = UNIQUE_NAME_NOTIFICATION_POPUP

    def ApplyAttributes(self, attributes):
        super(NotificationPopupContainer, self).ApplyAttributes(attributes)

    def AnimateReveal(self):
        self.Show()
        animations.FadeTo(self, duration=0.25, curveType=uiconst.ANIM_LINEAR)


class NotificationContainer(UiHiderMixin, Transform):
    default_name = 'NotificationContainer'
    uniqueUiName = UNIQUE_NAME_NOTIFICATION_CONTAINER

    def ApplyAttributes(self, attributes):
        super(NotificationContainer, self).ApplyAttributes(attributes)

    def _SetOpacity(self, value):
        if self.background:
            display = True if value else False
            self.background[0].display = display
        super(NotificationContainer, self)._SetOpacity(value)
