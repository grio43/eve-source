#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\neocom\neocomSvc.py
import logging
import blue
import carbonui.const as uiconst
import eveicon
import localization
import neocomPanelEntries
import threadutils
import uthread
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceConst import ROLEMASK_ELEVATEDPLAYER
from carbonui.control.contextMenu.menuEntryData import MenuEntryData
from carbonui.uicore import uicore
from eve.client.script.sys import eveinit
from carbonui.window.stack import WindowStack
from eve.client.script.ui.shared.inventory.neocomInventoryBadging import NeocomInventoryBadging
from eve.client.script.ui.shared.loginRewards.loginRewardsWnd import DailyLoginRewardsWnd
from eve.client.script.ui.shared.maps.browserwindow import MapBrowserWnd
from eve.client.script.ui.shared.neocom.neocom import neocomConst, neocomUtil, neocomSignals
from eve.client.script.ui.shared.neocom.neocom.btnData.btnDataNodeRoot import BtnDataNodeRoot
from eve.client.script.ui.shared.neocom.neocom.neocomRawData import GetEveMenuRawData, GetNeocomDefaultRawData, GetAvailableRawData
from eve.client.script.ui.shared.neocom.wallet.walletUtil import GetSettingValue
from jobboard.client import job_board_signals
from menu import MenuLabel
from neocom2.btnIDs import CHARACTER_SHEET_ID, SKILLS_ID
from chat.client.window import BaseChatWindow
from .btnData import btnDataFactory
from .btnData.btnDataRaw import GetCmdNameForWindowFromRawData
from .neocomContainer import NeocomContainer
from .neocomPanels import PanelEveMenu, PanelBase
from .neocomSettings import neocom_light_background_setting
from .neocomUtil import IsInventoryBadgingEnabled, ResetNeocomButtons
log = logging.getLogger(__name__)
DEBUG_ALWAYSLOADRAW = False
IGNORECLASSES = (BaseChatWindow, MapBrowserWnd, DailyLoginRewardsWnd)

class NeocomSvc(Service):
    __update_on_reload__ = 1
    __guid__ = 'svc.neocom'
    __notifyevents__ = ['OnSessionChanged',
     'OnSessionReset',
     'OnWindowOpened',
     'OnWindowSetActive',
     'OnWindowSetInactive',
     'OnWindowClosed',
     'OnWindowMinimized',
     'OnWindowMaximized',
     'OnOfferAvailabilityChange',
     'OnCharacterLPBalanceChange_Local']

    def __init__(self):
        super(NeocomSvc, self).__init__()
        self.eveMenu = None
        self.folderDropCookie = None
        self.currPanels = []
        self.neocomContainer = None
        self.updatingWindowPush = False
        self.blinkQueue = []
        self.inventoryBadging = None
        self.blinkThread = None
        self.mainBtnDataRoot = None
        self.fixedButtonDataRoot = None
        self._fixedButtonExtensions = []
        self.eveMenuBtnDataRoot = None
        self.skillsBtnDataRoot = None
        self.charSheetBtnDataRoot = None
        self.ConnectSignals()

    def ConnectSignals(self):
        neocomSignals.on_all_button_blinking_setting_changed.connect(self.OnAllButtonBlinkSettingChanged)
        neocomSignals.on_show_badging_setting_changed.connect(self.UpdateInventoryBadging)
        neocomSignals.on_reset_buttons.connect(self.Reload)
        job_board_signals.on_job_board_feature_availability_changed.connect(self.OnJobBoardAvailabilityChanged)
        job_board_signals.on_missions_feature_availability_changed.connect(self.OnJobBoardAvailabilityChanged)

    def OnAllButtonBlinkSettingChanged(self):
        if not neocomUtil.IsBlinkingEnabled():
            self.BlinkStopAll()

    def Run(self, *args):
        self.ReInitialize()

    def Stop(self, memStream = None):
        self.CloseAllPanels()
        for cont in uicore.layer.sidePanels.children:
            if cont.name == 'Neocom':
                cont.Close()

        for cont in uicore.layer.abovemain.children:
            if isinstance(cont, PanelBase):
                cont.Close()

        if self.neocomContainer:
            self.neocomContainer.Close()
            sm.ScatterEvent('OnNeocomAvailableChanged')
        if self.blinkThread:
            self.blinkThread.kill()
        if self.inventoryBadging:
            sm.UnregisterNotify(self.inventoryBadging)
        self.ReInitialize()

    def ReInitialize(self):
        self.eveMenu = None
        self.folderDropCookie = None
        self.currPanels = []
        self.neocomContainer = None
        self.updatingWindowPush = False
        self.blinkQueue = []
        self.mainBtnDataRoot = None
        self.fixedButtonDataRoot = None
        self.skillsBtnDataRoot = None
        self.charSheetBtnDataRoot = None
        self.inventoryBadging = None
        if self.blinkThread is not None:
            self.blinkThread.kill()
        self.blinkThread = None
        self.eveMenuBtnDataRoot = None

    def Reload(self):
        self.Stop()
        self.Run()
        if self.neocomContainer:
            self.neocomContainer.Close()
        self.CreateNeocom()
        self.UpdateNeocomButtons()

    @threadutils.throttled(1.0)
    def OnJobBoardAvailabilityChanged(self, _oldValue, _newValue):
        self.mainBtnDataRoot = None
        self.Reload()

    def _CheckNewDefaultButtons(self, rawData):
        defaultRawData = GetNeocomDefaultRawData()
        originalRawData = settings.char.ui.Get('neocomButtonRawDataOriginal', defaultRawData)
        newOriginalData = []
        for data in defaultRawData:
            data = neocomUtil.ConvertOldTypeOfRawData(data)
            newOriginalData.append(data)
            if not self._IsWndIDInRawData(data.id, originalRawData):
                if not self._IsWndIDInRawData(data.id, rawData):
                    rawData.append(data)

        settings.char.ui.Set('neocomButtonRawDataOriginal', tuple(newOriginalData))

    def _IsWndIDInRawData(self, checkWndID, rawData):
        if not rawData:
            return False
        for data in rawData:
            data = neocomUtil.ConvertOldTypeOfRawData(data)
            if checkWndID == data.id or self._IsWndIDInRawData(checkWndID, data.children):
                return True

        return False

    def OnSessionChanged(self, isRemote, sess, change):
        if 'stationid' in change or 'structureid' in change:
            self._ReconstructFixedButtonDataRoot()

    def OnSessionReset(self):
        self.Stop()
        self._fixedButtonExtensions = []

    def _GetButtonNodesRawData(self):
        defaultRawData = GetNeocomDefaultRawData()
        rawData = settings.char.ui.Get('neocomButtonRawData', defaultRawData)
        self._CheckNewDefaultButtons(rawData)
        rawData = neocomUtil.ConvertOldButtonTypes(rawData)
        rawData = GetAvailableRawData(rawData)
        if DEBUG_ALWAYSLOADRAW:
            rawData = defaultRawData
        return rawData

    def CreateNeocom(self):
        if not self.mainBtnDataRoot:
            sm.GetService('redeem').InitializeNeocomExtension()
            self._ConstructMainBtnDataRoot()
            self._ConstructFixedButtonDataRoot()
            self._ConstructEveMenuBtnDataRoot()
            self._ConstructSkillsBtnDataRoot()
            self._ConstructCharSheetBtnDataRoot()
        if not self.neocomContainer:
            self.neocomContainer = NeocomContainer(parent=uicore.layer.sidePanels, idx=0, align=neocomUtil.GetNeocomAlign(), mainBtnDataRoot=self.mainBtnDataRoot, eveMenuBtnDataRoot=self.eveMenuBtnDataRoot, skillsBtnDataRoot=self.skillsBtnDataRoot, fixedButtonDataRoot=self.fixedButtonDataRoot, charSheetBtnDataRoot=self.charSheetBtnDataRoot)
            for wnd in uicore.registry.GetWindows():
                self._CheckConstructWindowButtonData(wnd)

            self._ApplyBlinkQueue()
            sm.ScatterEvent('OnNeocomAvailableChanged')
        self.UpdateInventoryBadging()
        self._RestartBlinkThread()

    def _ConstructSkillsBtnDataRoot(self):
        self.skillsBtnDataRoot = BtnDataNodeRoot(btnID='skillsBtnDataRoot', persistChildren=False)
        btnDataFactory.ConstructButtonDataFromRawData(self.skillsBtnDataRoot, neocomConst.RAWDATA_SKILLS, isRemovable=False)

    def _ConstructCharSheetBtnDataRoot(self):
        self.charSheetBtnDataRoot = BtnDataNodeRoot(btnID='charSheetBtnDataRoot', persistChildren=False)
        btnDataFactory.ConstructButtonDataFromRawData(self.charSheetBtnDataRoot, neocomConst.RAWDATA_CHARSHEET, isRemovable=False)

    def _ApplyBlinkQueue(self):
        for blinkData in self.blinkQueue:
            self.Blink(*blinkData)

        self.blinkQueue = []

    def _ConstructEveMenuBtnDataRoot(self):
        self.eveMenuBtnDataRoot = BtnDataNodeRoot(btnID='eveMenu', persistChildren=False, isTopLevel=False)
        data = GetEveMenuRawData()
        btnDataFactory.ConstructButtonDataFromRawData(self.eveMenuBtnDataRoot, data, isRemovable=False)

    def _ConstructMainBtnDataRoot(self):
        rawData = self._GetButtonNodesRawData()
        self.mainBtnDataRoot = BtnDataNodeRoot(btnID='neocom')
        btnDataFactory.ConstructButtonDataFromRawData(self.mainBtnDataRoot, rawData, isRemovable=True)

    def GetNeocomContainer(self):
        return self.neocomContainer

    def _RestartBlinkThread(self):
        if self.blinkThread:
            self.blinkThread.kill()
            self.blinkThread = None
        self.blinkThread = uthread.new(self._BlinkThread)

    def _BlinkThread(self):
        while True:
            blue.pyos.synchro.SleepWallclock(1000 * neocomConst.BLINK_INTERVAL)
            neocomSignals.on_blink_pulse()

    def IsAvailable(self):
        return self.neocomContainer is not None

    def UpdateInventoryBadging(self):
        isEnabled = IsInventoryBadgingEnabled()
        if not self.inventoryBadging and isEnabled:
            self.inventoryBadging = NeocomInventoryBadging(inventory_cache=sm.GetService('invCache'), neocom=self)
            sm.ScatterEvent('OnInventoryBadgingCreated')
            return
        if not isEnabled and self.inventoryBadging:
            self.inventoryBadging.clear()
            self.inventoryBadging = None
            sm.ScatterEvent('OnInventoryBadgingDestroyed')

    def HasUnseenInventoryItems(self):
        if self.inventoryBadging:
            return self.inventoryBadging.has_unseen_items()
        return False

    def GetUnseenInventoryItemsCount(self):
        if self.inventoryBadging:
            return self.inventoryBadging.get_unseen_items_count()
        return 0

    def HasUnseenInventoryItemsInLocation(self, locationID):
        if self.inventoryBadging:
            return self.inventoryBadging.has_unseen_items_in_location(locationID)
        return False

    def IsInventoryItemUnseen(self, itemID, typeID, flagID, locationID):
        if self.inventoryBadging:
            return self.inventoryBadging.is_item_unseen(itemID, typeID, flagID, locationID)
        return False

    def MarkInventoryItemSeen(self, itemID, typeID, flagID, locationID):
        if self.inventoryBadging:
            return self.inventoryBadging.mark_item_seen(itemID, typeID, flagID, locationID)
        return False

    def OnWindowOpened(self, wnd):
        self._CheckConstructWindowButtonData(wnd)
        btnData = self._GetBtnDataByWndCls(wnd.__class__)
        if btnData:
            btnData.SetHasNewActivityOff()

    def _CheckConstructWindowButtonData(self, wnd):
        if not self.neocomContainer:
            return
        if not wnd or wnd.destroyed:
            return
        if self._IsWindowIgnored(wnd):
            return
        if not wnd.IsKillable() and not wnd.IsMinimized():
            return
        self.ConstructWindowButtonData(wnd)

    def ConstructWindowButtonData(self, wnd):
        btnData = self._GetBtnDataByWndCls(wnd.__class__)
        if not btnData:
            uniqueUiNameFromWnd = getattr(wnd, 'uniqueUiName', None) or wnd.windowID
            btnData = btnDataFactory.ConstructBtnData(parent=self.mainBtnDataRoot, btnID=wnd.__guid__, btnType=neocomConst.BTNTYPE_WINDOW, label=wnd.GetCaption(), iconPath=wnd.iconNum, wndCls=wnd.__class__, isOpen=True, uniqueUiNameFromWnd=uniqueUiNameFromWnd)
            cmdName = GetCmdNameForWindowFromRawData(wnd)
            btnData.cmdName = cmdName
        else:
            btnData.SetOpen()
        cmdName = GetCmdNameForWindowFromRawData(wnd)
        btnDataFactory.ConstructBtnData(parent=btnData, btnID=wnd.windowID, btnType=neocomConst.BTNTYPE_WINDOW, label=wnd.GetCaption(), iconPath=wnd.iconNum, wnd=wnd, isDraggable=False, wndCls=wnd.__class__, cmdName=cmdName)

    def OnWindowSetActive(self, wnd):
        btnData = self._GetBtnDataByWndCls(wnd.__class__)
        if btnData:
            btnData.SetActive()

    def OnWindowSetInactive(self, wnd):
        btnData = self._GetBtnDataByWndCls(wnd.__class__)
        if btnData:
            btnData.SetInactive()

    def _GetBtnDataByWndCls(self, wndCls, btnType = None):
        for btnRootData in self.GetTopLevelVisibleButtonsRootNodes():
            if not btnRootData:
                continue
            for btnData in btnRootData.children:
                if btnData.wndCls == wndCls:
                    if btnType and btnType != btnData.btnType:
                        continue
                    return btnData

    def _IsWindowIgnored(self, wnd):
        for classType in IGNORECLASSES:
            if isinstance(wnd, classType):
                return True

        if wnd.isModal:
            return True
        if isinstance(wnd, WindowStack) and wnd.IsKillable():
            return True
        return False

    def RemoveWindowButton(self, wndInstanceID, wndCls):
        btnData = self._GetBtnDataByWndCls(wndCls)
        if not btnData:
            return
        btnData.RemoveChildWindow(wndInstanceID)

    def UpdateNeocomButtons(self):
        if self.neocomContainer is not None:
            self.neocomContainer.UpdateButtons()

    def OnWindowMinimized(self, wnd):
        if not self.neocomContainer:
            return
        if not wnd or wnd.destroyed:
            return
        if self._IsWindowIgnored(wnd):
            return
        if not wnd.IsKillable():
            self.ConstructWindowButtonData(wnd)

    def OnWindowMaximized(self, wnd, wasMinimized):
        if not self.neocomContainer:
            return
        if not wnd or wnd.destroyed:
            return
        if not wnd.IsKillable():
            self.RemoveWindowButton(wnd.windowInstanceID, wnd.__class__)

    def OnWindowClosed(self, wndID, wndInstanceID, wndCls):
        if not self.neocomContainer:
            return
        self.RemoveWindowButton(wndInstanceID, wndCls)

    def GetMainBtnDataRoot(self):
        return self.mainBtnDataRoot

    def GetEveMenuBtnDataRoot(self):
        return self.eveMenuBtnDataRoot

    def OnOfferAvailabilityChange(self):
        self.OnFixedButtonVisibleChanged(None)

    def RegisterFixedButtonExtension(self, extension):
        if extension in self._fixedButtonExtensions:
            raise ValueError('extension already registered')
        extension.on_visible_changed.connect(self.OnFixedButtonVisibleChanged)
        self._fixedButtonExtensions.append(extension)
        self.OnFixedButtonVisibleChanged(extension)

    def UnregisterFixedButtonExtension(self, extension):
        extension.on_visible_changed.disconnect(self.OnFixedButtonVisibleChanged)
        self._fixedButtonExtensions.remove(extension)
        self.OnFixedButtonVisibleChanged(extension)

    @threadutils.threaded
    def OnFixedButtonVisibleChanged(self, extension):
        if self.neocomContainer is None:
            return
        self._ReconstructFixedButtonDataRoot()

    def _ConstructFixedButtonDataRoot(self):
        self.fixedButtonDataRoot = BtnDataNodeRoot(btnID='mainBtnDataRoot', persistChildren=False)
        for extension in self._fixedButtonExtensions:
            if extension.is_visible:
                extension.create_button_data(self.fixedButtonDataRoot)

    def _ReconstructFixedButtonDataRoot(self):
        self._ConstructFixedButtonDataRoot()
        if self.neocomContainer:
            self.neocomContainer.SetFixedButtonDataRoot(self.fixedButtonDataRoot)

    def GetFixedButtonData(self):
        return self.fixedButtonDataRoot

    def GetMinimizeToPos(self, wnd):
        if not self.mainBtnDataRoot:
            return (0, 0)
        else:
            if isinstance(wnd, WindowStack):
                wnd = wnd.GetActiveWindow()
            if isinstance(wnd, BaseChatWindow):
                btnData = self.mainBtnDataRoot.GetBtnDataByTypeAndID('chat')
            else:
                btnData = self._GetBtnDataByWndCls(wnd.__class__)
            if btnData and btnData.btnUI:
                if self.IsBtnInOverflowList(btnData):
                    uiObj = self.neocomContainer.overflowBtn
                else:
                    uiObj = btnData.btnUI
                uiObj.BlinkOnMinimize()
                l, t, w, h = uiObj.GetAbsolute()
                return (l + w / 2, t + h / 2)
            uiObj = self.neocomContainer.buttonCont.children[-1]
            if uiObj.state == uiconst.UI_HIDDEN:
                uiObj = self.neocomContainer.overflowBtn
                uiObj.BlinkOnMinimize()
            l, t, w, h = uiObj.GetAbsolute()
            return (l + w / 2, t + h / 2)

    def IsBtnInOverflowList(self, btnData):
        if btnData and getattr(btnData, 'btnUI', None):
            return btnData.btnUI.state == uiconst.UI_HIDDEN
        return False

    def GetBtnData(self, btnID):
        return self._GetBtnData(btnID, self.GetAllRootNodes())

    def GetTopLevelBtnData(self, btnID):
        return self._GetBtnData(btnID, self.GetTopLevelVisibleButtonsRootNodes())

    def _GetBtnData(self, btnID, rootNodes):
        for rootBtnData in rootNodes:
            if rootBtnData is None:
                continue
            btnData = rootBtnData.GetBtnDataByTypeAndID(btnID, recursive=True)
            if btnData is not None:
                return btnData

    def GetAllRootNodes(self):
        return (self.charSheetBtnDataRoot,
         self.skillsBtnDataRoot,
         self.mainBtnDataRoot,
         self.fixedButtonDataRoot,
         self.eveMenuBtnDataRoot)

    def GetTopLevelVisibleButtonsRootNodes(self):
        return (self.charSheetBtnDataRoot,
         self.skillsBtnDataRoot,
         self.mainBtnDataRoot,
         self.fixedButtonDataRoot)

    def Blink(self, wndID, hint = None):
        if not self.neocomContainer:
            self.blinkQueue.append((wndID, hint))
            return
        if not neocomUtil.IsBlinkingEnabled():
            return
        if wndID == 'eveMenuBtn':
            self.eveMenuBtnDataRoot.SetBlinkingOn()
        else:
            btnData = self.GetBtnData(wndID)
            if btnData:
                btnData.SetBlinkingOn(hint)

    def BlinkOff(self, wndID):
        if not self.neocomContainer:
            return
        btnData = self.GetBtnData(wndID)
        if not btnData:
            return
        btnData.SetBlinkingOff()

    def OnNeocomButtonsRecreated(self):
        self.CloseAllPanels()

    def ShowPanel(self, triggerCont, panelClass, panelAlign, *args, **kw):
        panel = panelClass(idx=0, *args, **kw)
        self.currPanels.append(panel)
        uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEDOWN, self.OnGlobalMouseDown)
        self.CheckPanelPosition(panel, triggerCont, panelAlign)
        panel.EntryAnimation()
        return panel

    def CheckPanelPosition(self, panel, triggerCont, panelAlign):
        l, t, w, h = triggerCont.GetAbsolute()
        if panelAlign == neocomConst.PANEL_SHOWABOVE:
            panel.left = l
            panel.top = t - panel.height
            if panel.left + panel.width > uicore.desktop.width:
                panel.left = l - panel.width + w
        elif panelAlign == neocomConst.PANEL_SHOWONSIDE:
            if self.neocomContainer.align == uiconst.TOLEFT:
                panel.left = l + w
            else:
                panel.left = l - panel.width
            panel.top = t
            if panel.top + panel.height > uicore.desktop.height - self.neocomContainer.height:
                panel.top = t - panel.height + h
            if panel.left + panel.width > uicore.desktop.width:
                panel.left = l - panel.width
        dw = uicore.desktop.width
        dh = uicore.desktop.height
        if panel.top < 0:
            panel.top = 0
        elif panel.top + panel.height > dh:
            panel.top = dh - panel.height
        if panel.left < 0:
            panel.left = 0
        elif panel.left + panel.width > dw:
            panel.left = dw - panel.width

    def IsSomePanelOpen(self):
        return len(self.currPanels) > 0

    def OnGlobalMouseDown(self, cont, *args):
        if hasattr(cont, 'ToggleNeocomPanel'):
            return True
        if not isinstance(cont, neocomPanelEntries.PanelEntryBase):
            sm.ScatterEvent('OnNeocomPanelsClosed')
            self.CloseAllPanels()
            return False
        return True

    def CloseAllPanels(self):
        for panel in self.currPanels:
            panel.Close()

        self.currPanels = []

    def ClosePanel(self, panel):
        self.currPanels.remove(panel)
        panel.Close()

    def CloseChildrenPanels(self, btnData):
        toRemove = []
        for panel in self.currPanels:
            if panel.btnData and panel.btnData.IsDescendantOf(btnData):
                toRemove.append(panel)

        for panel in toRemove:
            panel.Close()
            self.currPanels.remove(panel)

    def ToggleEveMenu(self):
        if self.eveMenu and not self.eveMenu.destroyed:
            self.CloseAllPanels()
            self.eveMenu = None
        else:
            self.ShowEveMenu()

    def GetEveMenuButtonSize(self):
        if self.neocomContainer:
            return self.neocomContainer.GetEveMenuButtonSize()
        return (0, 0)

    def ShowEveMenu(self):
        PlaySound(uiconst.SOUND_EXPAND)
        self.neocomContainer.UnhideNeocom(sleep=True)
        self.eveMenu = self.ShowPanel(self.neocomContainer, PanelEveMenu, neocomConst.PANEL_SHOWONSIDE, parent=uicore.layer.abovemain, btnData=self.eveMenuBtnDataRoot)
        sm.ScatterEvent('OnEveMenuShown')
        return self.eveMenu

    def GetUIObjectAndNodeByID(self, wndID):
        if not self.neocomContainer:
            return (None, None)
        for btnData in self.GetTopLevelVisibleButtonsRootNodes():
            if btnData:
                node = btnData.GetBtnDataByTypeAndID(wndID, recursive=True)
                if node:
                    if wndID == CHARACTER_SHEET_ID:
                        return (self.neocomContainer.charSheetBtn, node)
                    if wndID == SKILLS_ID:
                        return (self.neocomContainer.skillPlannerBtn, node)
                    if not node.btnUI or node.btnUI.destroyed:
                        return (None, None)
                    return (node.btnUI, node)

        node = self.eveMenuBtnDataRoot.GetBtnDataByTypeAndID(wndID, recursive=True)
        if node:
            return (self.neocomContainer.eveMenuBtn, node)
        return (None, None)

    def GetUIObjectByUniqueUiName(self, uniqueUiName):
        if not self.neocomContainer:
            return None
        for btnData in self.GetTopLevelVisibleButtonsRootNodes():
            if btnData:
                node = btnData.GetBtnDataByUniqueUiName(uniqueUiName, recursive=True)
                if node:
                    if not node.btnUI or node.btnUI.destroyed:
                        return None
                    return node.btnUI

        node = self.eveMenuBtnDataRoot.GetBtnDataByUniqueUiName(uniqueUiName, recursive=True)
        if node:
            return self.neocomContainer.eveMenuBtn

    def IsButtonVisible(self, wndID):
        for btnData in self.GetTopLevelVisibleButtonsRootNodes():
            if btnData is None:
                continue
            node = btnData.GetBtnDataByTypeAndID(wndID)
            if node:
                return True

        return False

    def OnNeocomTaskbarMouseEnter(self, btnData):
        if not self.IsValidDropData(btnData):
            return
        self.OnButtonDragEnter(self.mainBtnDataRoot, btnData)

    def OnButtonDragEnter(self, btnData, dragBtnData, *args):
        if not self.IsValidDropData(dragBtnData):
            return
        btns = self.mainBtnDataRoot.GetChildrenInScope()
        if btnData in btns:
            index = btns.index(btnData)
        else:
            index = len(btns)
        self.neocomContainer.ShowDropIndicatorLine(index)

    def OnButtonDragExit(self, *args):
        self.neocomContainer.HideDropIndicatorLine()

    def OnBtnDataDropped(self, btnData, index = None):
        if not self.mainBtnDataRoot.IsValidDropData(btnData):
            return
        oldRootNode = btnData.GetRootNode()
        if btnData.btnType == neocomConst.BTNTYPE_GROUP and oldRootNode != self.mainBtnDataRoot.GetRootNode():
            toRemove = []
            for child in btnData.children:
                btnDataFound = self.mainBtnDataRoot.GetBtnDataByWndCls(child.wndCls, recursive=True)
                if btnDataFound:
                    toRemove.append(child)
                else:
                    child.isRemovable = True

            for child in toRemove:
                child.Remove()

        self.AddButtonToRoot(btnData, index)

    def AddButtonToRoot(self, btnData, index = -1):
        oldRootNode = btnData.GetRootNode()
        oldBtnData = self.mainBtnDataRoot.GetBtnDataByWndCls(btnData.wndCls, recursive=False)
        btnData.MoveTo(self.mainBtnDataRoot, index)
        if oldBtnData and oldBtnData != btnData:
            for child in oldBtnData.children:
                child.SetParent(btnData)

            btnData.SetOpen()
            oldBtnData.Remove()
        if oldRootNode == self.eveMenuBtnDataRoot:
            self._ConstructEveMenuBtnDataRoot()
            btnData.isRemovable = True

    def IsValidDropData(self, btnData):
        return self.mainBtnDataRoot.IsValidDropData(btnData)

    def GetMenu(self):
        m = []
        if self.neocomContainer.IsSizeLocked():
            m.append(MenuEntryData(MenuLabel('UI/Neocom/UnlockNeocom'), lambda : self.neocomContainer.SetSizeLocked(False), texturePath=eveicon.locked))
        else:
            m.append(MenuEntryData(MenuLabel('UI/Neocom/LockNeocom'), lambda : self.neocomContainer.SetSizeLocked(True), texturePath=eveicon.unlocked))
        if neocom_light_background_setting.get():
            m.append(MenuEntryData(text=localization.GetByLabel('/Carbon/UI/Controls/Window/DisableLightBackground'), func=neocom_light_background_setting.disable, texturePath=eveicon.light_background_on))
        else:
            m.append(MenuEntryData(text=localization.GetByLabel('/Carbon/UI/Controls/Window/EnableLightBackground'), func=neocom_light_background_setting.enable, texturePath=eveicon.light_background_off))
        m.extend([None, (localization.GetByLabel('UI/Neocom/CreateNewGroup'), self.mainBtnDataRoot.AddNewGroup), None])
        if self.neocomContainer.IsAutoHideActive():
            m.append((MenuLabel('UI/Neocom/AutohideOff'), self.neocomContainer.SetAutoHideOff))
        else:
            m.append((MenuLabel('UI/Neocom/AutohideOn'), self.neocomContainer.SetAutoHideOn))
        if self.neocomContainer.align == uiconst.TOLEFT:
            m.append((MenuLabel('UI/Neocom/AlignRight'), self.neocomContainer.SetAlignRight))
        else:
            m.append((MenuLabel('UI/Neocom/AlignLeft'), self.neocomContainer.SetAlignLeft))
        if neocomUtil.IsBlinkingEnabled():
            m.append((MenuLabel('UI/Neocom/ConfigAllBlinkOff'), neocomUtil.DisableAllButtonBlinking))
        else:
            m.append((MenuLabel('UI/Neocom/ConfigAllBlinkOn'), neocomUtil.EnableAllButtonBlinking))
        m.append((MenuLabel('UI/Neocom/ResetButtons'), ResetNeocomButtons))
        if eveinit.Eve().session.role & ROLEMASK_ELEVATEDPLAYER:
            m.extend([None, ('Reload Insider', sm.StartService('insider').Reload), ('Toggle Insider', lambda : sm.StartService('insider').Toggle(forceShow=True))])
        return m

    def BlinkStopAll(self):
        self.eveMenuBtnDataRoot.SetBlinkingOff()
        self.mainBtnDataRoot.SetBlinkingOff()
        self.fixedButtonDataRoot.SetBlinkingOff()

    def FindParentGroupBtn(self, wndID):
        btnData = self.GetBtnData(wndID)
        if not btnData:
            return
        if not getattr(btnData, 'parent', None):
            return
        if getattr(btnData.parent, 'btnType', None) == neocomConst.BTNTYPE_GROUP:
            return getattr(btnData.parent, 'btnUI', None)

    def OnCharacterLPBalanceChange_Local(self, issuerCorpID, lpBefore, lpAfter):
        if issuerCorpID is not None and GetSettingValue('walletShowLpUpdates'):
            hint = localization.GetByLabel('UI/Neocom/Blink/LoyaltyPointsChanged', corpID=issuerCorpID)
            sm.GetService('neocom').Blink('wallet', hint)
            if lpBefore is not None and lpAfter is not None:
                sm.ScatterEvent('OnCharacterLpUpdatedInWallet', issuerCorpID, lpBefore, lpAfter)
