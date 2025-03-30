#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\redeemsvc.py
import eveexceptions
import localization
import redeem.client
import uthread
from carbon.common.script.sys.service import Service
from carbonui import uiconst
from crates.crateutil import is_fixed_crate
from eve.client.script.ui.crate.fixedcratewindow import FixedCrateWindow
from eve.client.script.ui.shared.neocom.neocom.fixedButtonExtension import SeenItemStorage
from eve.client.script.ui.shared.redeem.neocom import UnseenRedeemItemsBtnData, RedeemIconExtension
from eve.client.script.ui.shared.redeem.window import GetRedeemWindow
from eve.client.script.ui.shared.activateMultiTraining import ActivateMultiTraining
from eve.client.script.ui.shared.cloneGrade import cloneStateUtil
from inventorycommon import const as invconst
from carbonui.uicore import uicore

class RedeemService(Service):
    __guid__ = 'svc.redeem'
    __notifyevents__ = ['OnRedeemingQueueUpdated', 'OnSessionReset']

    def Run(self, *args):
        super(RedeemService, self).Run(*args)
        self.Initialize()

    def Initialize(self):
        self.tokens = None
        self.redeemData = redeem.get_redeem_data()
        self._seenTokenStorage = None
        self._neocomRedeemNotificationExtension = None
        self._extensionsInitialized = False

    def InitializeNeocomExtension(self):
        if self._extensionsInitialized is True:
            return
        self._extensionsInitialized = True
        self._seenTokenStorage = SeenItemStorage(get_items_function=self.GetTokenData, settings_container=settings.user.ui, settings_key='SeenTokenStorage_SeenTokens')
        self._neocomRedeemNotificationExtension = RedeemIconExtension(button_data_class=UnseenRedeemItemsBtnData, get_badge_count=lambda : len(self._seenTokenStorage.get_unseen()), get_item_count=self.GetRedeemTokenCount)
        self._neocomRedeemNotificationExtension.connect_item_changes(self._seenTokenStorage.on_items_changed)
        sm.GetService('neocom').RegisterFixedButtonExtension(self._neocomRedeemNotificationExtension)
        self.FetchRedeemTokens()

    def GetTokenData(self):
        return set(((token.tokenID, token.massTokenID) for token in self.GetRedeemTokens()))

    def GetRedeemTokens(self, force = False):
        if self.tokens is None or force:
            self.FetchRedeemTokens()
        return self.tokens

    def GetRedeemTokenCount(self):
        tokens = self.GetRedeemTokens()
        if tokens is None:
            return 0
        return len(tokens)

    def FetchRedeemTokens(self):
        self.tokens = sm.RemoteSvc('userSvc').GetRedeemTokens()

    def ReverseRedeem(self, item):
        if eve.Message('ConfirmReverseRedeem', {'type': (eveexceptions.UE_TYPEID, item.typeID),
         'quantity': item.stacksize}, uiconst.YESNO) != uiconst.ID_YES:
            return
        try:
            sm.RemoteSvc('userSvc').ReverseRedeem(item.itemID)
        finally:
            self.OnRedeemingQueueUpdated()

    def ToggleRedeemWindow(self):
        redeemWindow = GetRedeemWindow()
        redeemWindow.ToggleOpenClose(charID=session.charid, stationID=session.stationid or session.structureid, redeemData=self.redeemData)

    def OpenRedeemWindow(self):
        redeemWindow = GetRedeemWindow()
        wnd = redeemWindow.GetIfOpen()
        if wnd is None:
            wnd = redeemWindow.Open(charID=session.charid, stationID=session.stationid or session.structureid, useDefaultPos=True, redeemData=self.redeemData)
            wnd.left -= 160
        if wnd is not None and not wnd.destroyed:
            wnd.Maximize()

    def CloseRedeemWindow(self):
        redeemWindow = GetRedeemWindow()
        redeemWindow.CloseIfOpen()

    def ClaimRedeemTokens(self, tokens, charID, useHomeStation = False):
        redeemInfo = None
        tokens = self._HandleMctTokens(tokens, charID, useHomeStation=useHomeStation)
        try:
            redeemInfo = sm.RemoteSvc('userSvc').ClaimRedeemTokens(tokens, charID, useHomeStation=useHomeStation)
        except eveexceptions.UserError as e:
            eve.Message(e.msg, e.dict)
        except RuntimeError:
            self.OnRedeemingQueueUpdated()
            raise
        else:
            if self._ShouldOfferOpenFixedCrates(redeemInfo):
                self._OfferOpenFixedLootCrates(redeemInfo)
            elif not session.charid:
                uthread.new(redeem.client.ShowFulfillmentReport, redeemInfo, eve)

        if redeemInfo['errors']:
            displayed = set()
            for tokenID, error in redeemInfo['errors']:
                if error.dict:
                    typeID = error.dict.get('itemTypeID')
                    if (error.msg, typeID) not in displayed:
                        displayed.add((error.msg, typeID))
                        eve.Message(error.msg, error.dict)
                elif error.msg not in displayed:
                    displayed.add(error.msg)
                    eve.Message(error.msg)

        self.OnRedeemingQueueUpdated()
        numItemsCreated = len(redeemInfo.get('itemsCreated', [])) if redeemInfo else 0
        stationID = redeemInfo.get('stationID', None)
        self.NotifyOfTokensRedeemed(charID, stationID, tokens, numItemsCreated)
        return redeemInfo

    def NotifyOfTokensRedeemed(self, characterID, stationID, tokens, numItemsCreated):
        sm.ScatterEvent('OnTokensRedeemed', characterID, stationID, tokens, numItemsCreated)

    def _ShouldOfferOpenFixedCrates(self, redeemInfo):
        if not session.charid:
            return False
        return redeemInfo['stationID'] in (session.stationid, session.structureid)

    def _OfferOpenFixedLootCrates(self, redeemInfo):
        cratesToOpen = []
        for itemData in redeemInfo['itemsCreated']:
            itemID = itemData['itemID']
            typeID = itemData['typeID']
            quantity = itemData['quantity']
            if is_fixed_crate(typeID):
                cratesToOpen.append((typeID, itemID, quantity))

        if cratesToOpen:
            FixedCrateWindow(crate_stack_list=cratesToOpen)

    def TrashRedeemTokens(self, tokens):
        sm.RemoteSvc('userSvc').TrashRedeemTokens(tokens)
        self.OnRedeemingQueueUpdated()

    def OnRedeemingQueueUpdated(self):
        self.FetchRedeemTokens()
        if self._seenTokenStorage:
            self._seenTokenStorage.update_unseen_count()
        if self._neocomRedeemNotificationExtension:
            self._neocomRedeemNotificationExtension.on_items_changed()
        sm.ScatterEvent('OnRedeemingTokensUpdated')

    def OnSessionReset(self):
        if self._neocomRedeemNotificationExtension:
            self._neocomRedeemNotificationExtension.disconnect_item_changes(self._seenTokenStorage.on_items_changed)
        self.Initialize()

    def GetTokenLabel(self, token):
        if token.label:
            return self._GetMessageOrLabel(token.label)
        return ''

    def GetTokenDescription(self, token):
        if token.description:
            return self._GetMessageOrLabel(token.description)
        return ''

    def _GetMessageOrLabel(self, text):
        try:
            messageID = int(text)
            if localization.IsValidMessageID(messageID):
                return localization.GetByMessageID(messageID)
        except ValueError:
            if localization.IsValidLabel(text):
                return localization.GetByLabel(text)

        return text

    def _HandleMctTokens(self, tokens, charID, useHomeStation = False):
        mctTokens = [ (token['tokenID'], token['massTokenID']) for token in tokens if token['typeID'] == invconst.typeSoulboundMultiTrainingToken ]
        tokens = [ (token['tokenID'], token['massTokenID']) for token in tokens if token['typeID'] != invconst.typeSoulboundMultiTrainingToken ]
        if mctTokens:
            if cloneStateUtil.IsOmega():
                ActivateMultiTraining(tokens=mctTokens, charId=charID, useHomeStation=useHomeStation)
            else:
                uicore.Message('CustomInfo', {'info': localization.GetByLabel('UI/CloneState/RequiresOmegaClone')})
        return tokens

    def MarkAllTokensSeen(self):
        if self._seenTokenStorage:
            self._seenTokenStorage.mark_all_seen()

    def HasUnseenTokens(self):
        if self._seenTokenStorage:
            return bool(self._seenTokenStorage.unseen_count)
        return False

    def GetUnseenTokensCount(self):
        if self._seenTokenStorage:
            return self._seenTokenStorage.unseen_count or 0
        return 0

    def GetTypeIDAndStackSize(self, tokenID, massTokenID):
        for token in self.tokens:
            if token.tokenID == tokenID or token.massTokenID == massTokenID:
                return (token.typeID, token.quantity)

        return (None, None)

    def ResetCache(self):
        self.tokens = None
