#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\station\pvptrade\pvptradesvc.py
from carbon.common.script.sys.service import Service
from carbonui.control.window import Window
from eve.client.script.ui.station.pvptrade.pvptradewnd import PVPTrade
from eveexceptions import UserError
from localization import GetByLabel

class PVPTradeService(Service):
    __guid__ = 'svc.pvptrade'
    __notifyevents__ = ['OnTradeInitiate',
     'OnTradeCancel',
     'OnTradeOffer',
     'OnTradeOfferReset',
     'OnTradeMoneyOffer',
     'OnTradeComplete',
     'OnPrimingNeededForTradeItems']

    def _ShowTradeSessionWindow(self, tradeSession, charID, tradeItems):
        windowID = self.GetWindowID()
        tradeContainerID = tradeSession.List().tradeContainerID
        existingWindow = Window.GetIfOpen(windowID=windowID, windowInstanceID=tradeContainerID)
        if existingWindow and not existingWindow.destroyed:
            existingWindow.Maximize()
        else:
            self.OnTradeInitiate(charID, tradeSession, tradeItems)

    def StartTradeSession(self, charID, tradeItems = None):
        tradeSession = sm.RemoteSvc('trademgr').InitiateTrade(charID)
        self._ShowTradeSessionWindow(tradeSession, charID, tradeItems)

    def GetWindowID(self):
        return 'tradeWnd'

    def OnTradeInitiate(self, charID, tradeSession, tradeItems = None):
        self.LogInfo('OnInitiate', charID, tradeSession)
        windowID = self.GetWindowID()
        tradeContainerID = tradeSession.List().tradeContainerID
        existingWindow = Window.GetIfOpen(windowID=windowID, windowInstanceID=tradeContainerID)
        if existingWindow:
            return
        showIfInStack = self.ShouldShowIfInStack(windowID)
        PVPTrade.Open(windowID=windowID, windowInstanceID=tradeContainerID, tradeSession=tradeSession, tradeItems=tradeItems, showIfInStack=showIfInStack)

    def ShouldShowIfInStack(self, windowID):
        defaultValue = True
        otherTradeWnd = Window.GetIfOpen(windowID=windowID)
        if not otherTradeWnd:
            return defaultValue
        stackID = PVPTrade.GetRegisteredOrDefaultStackID(windowID)
        if not stackID:
            return defaultValue
        from carbonui.uicore import uicore
        stack = uicore.registry.GetWindow(stackID)
        if not stack:
            return defaultValue
        if not isinstance(stack.GetActiveWindow(), PVPTrade):
            return defaultValue
        stack.ForceUpdateSelectedTabSetting()
        return False

    def OnTradeCancel(self, containerID):
        windowID = self.GetWindowID()
        w = Window.GetIfOpen(windowID=windowID, windowInstanceID=containerID)
        if w:
            w.OnCancel()

    def OnTradeOffer(self, containerID, state):
        windowID = self.GetWindowID()
        w = Window.GetIfOpen(windowID=windowID, windowInstanceID=containerID)
        if w:
            w.OnStateToggle(state)

    def OnTradeOfferReset(self, containerID, manifestError = None):
        windowID = self.GetWindowID()
        w = Window.GetIfOpen(windowID=windowID, windowInstanceID=containerID)
        if w:
            w.OnTradeOfferReset()
            if manifestError:
                eve.Message('CustomNotify', {'notify': GetByLabel('UI/Messages/DirectTradeManifestMismatch')})
            else:
                raise UserError('ItemExchangeFailed')

    def OnTradeMoneyOffer(self, containerID, money):
        windowID = self.GetWindowID()
        w = Window.GetIfOpen(windowID=windowID, windowInstanceID=containerID)
        if w:
            w.OnMoneyOffer(money)

    def OnTradeComplete(self, containerID, items = None):
        windowID = self.GetWindowID()
        w = Window.GetIfOpen(windowID=windowID, windowInstanceID=containerID)
        if w:
            w.OnTradeComplete(items)

    def OnPrimingNeededForTradeItems(self, itemIDsToPrime):
        cfg.evelocations.Prime(itemIDsToPrime)
