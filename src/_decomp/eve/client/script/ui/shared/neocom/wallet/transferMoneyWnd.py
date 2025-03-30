#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\transferMoneyWnd.py
from localization import GetByLabel
from eve.client.script.ui.control.message import ShowQuickMessage
from carbonui.primitives.containerAutoSize import ContainerAutoSize
import localization
from carbonui import uiconst
from carbonui.control.combo import Combo
from carbonui.control.singlelineedits.singleLineEditFloat import SingleLineEditFloat
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.uicore import uicore
from eve.client.script.ui.control import eveIcon, eveLabel
from carbonui.button.group import ButtonGroup
from carbonui.control.window import Window
from eve.client.script.ui.shared.neocom.wallet import walletConst
from eve.common.lib import appConst as const
from eve.common.script.sys import idCheckers

class TransferMoneyWnd(Window):
    __notifyevents__ = ['OnPersonalAccountChangedClient', 'OnCorpAccountChangedClient']
    default_windowID = 'TransferMoney'
    default_captionLabelPath = 'UI/Wallet/WalletWindow/TransferMoney'
    default_fixedHeight = 300
    default_fixedWidth = 300

    def ApplyAttributes(self, attributes):
        super(TransferMoneyWnd, self).ApplyAttributes(attributes)
        sm.RegisterNotify(self)
        self.currency = const.creditsISK
        self.maxISKvalue = 0
        self.minISKvalue = 0.1
        self.fromID = attributes.fromID
        self.fromAccountKey = attributes.fromAccountKey
        self.toID = attributes.toID
        self.toAccountKey = attributes.toAccountKey
        self.isCorpTransfer = bool(idCheckers.IsCorporation(self.toID) or idCheckers.IsCorporation(self.fromID))
        self.walletSvc = sm.GetService('wallet')
        self._InitVariables()
        self.ConstructLayout()

    def ConstructLayout(self):
        self.mainCont = ContainerAutoSize(name='mainCont', parent=self.sr.main, align=uiconst.TOTOP, callback=self.OnMainContResized)
        giverCont = Container(name='topCont', parent=self.mainCont, align=uiconst.TOTOP, pos=(0, 0, 0, 70), padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         0))
        giverImgCont = Container(name='imgCont', parent=giverCont, align=uiconst.TOLEFT, pos=(0, 0, 64, 0), padding=(0,
         0,
         const.defaultPadding,
         0))
        giverCont = Container(name='topRightCont', parent=giverCont, align=uiconst.TOALL, pos=(0, 0, 0, 0), padding=(const.defaultPadding,
         0,
         0,
         0))
        eveIcon.GetOwnerLogo(giverImgCont, self.fromID, size=64, noServerCall=True)
        if self.showFromAccount:
            label = localization.GetByLabel('UI/Wallet/WalletWindow/FromCharacterAcct', charID=self.fromID, acctName=sm.GetService('corp').GetCorpAccountName(self.fromAccountKey))
        else:
            label = localization.GetByLabel('UI/Wallet/WalletWindow/FromCharacter', charID=self.fromID)
        eveLabel.EveLabelMedium(text=label, parent=giverCont, left=0, top=0, align=uiconst.CENTERLEFT, width=170, state=uiconst.UI_DISABLED, idx=0)
        receiverCont = Container(name='bottomCont', parent=self.mainCont, align=uiconst.TOTOP, pos=(0, 0, 0, 70), padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        receiverimgCont = Container(name='imgCont', parent=receiverCont, align=uiconst.TOLEFT, pos=(0, 0, 64, 0), padding=(0,
         0,
         const.defaultPadding,
         0))
        receiverCont = Container(name='nameCont', parent=receiverCont, align=uiconst.TOALL, pos=(0, 0, 0, 0), padding=(const.defaultPadding,
         0,
         0,
         0))
        eveIcon.GetOwnerLogo(receiverimgCont, self.toID, size=64, noServerCall=True)
        eveLabel.EveLabelMedium(text=localization.GetByLabel('UI/Wallet/WalletWindow/ToCharacter', charID=self.toID), parent=receiverCont, left=0, top=0, align=uiconst.CENTERLEFT, width=170, state=uiconst.UI_DISABLED, idx=0)
        textLeft = 0
        editLeft = 72
        width = 172
        top = 0
        if self.showToAccount:
            opt = []
            for i in walletConst.corpWalletRoles:
                opt.append((sm.GetService('corp').GetCorpAccountName(i), i))

            self.combo = Combo(parent=self.mainCont, align=uiconst.TOTOP, padTop=16, options=opt, name='AccountCombo', select=self.toAccountKey, label=localization.GetByLabel('UI/Wallet/WalletWindow/Account'))
            top += 25
        self.amount = SingleLineEditFloat(name='amount', parent=self.mainCont, align=uiconst.TOTOP, padTop=24, setvalue='%s' % self.minISKvalue, minValue=self.minISKvalue, maxValue=float(self.maxISKvalue), decimalPlaces=2, autoselect=True, label=localization.GetByLabel('UI/Wallet/WalletWindow/ColHeaderAmount'))
        self.reason = SingleLineEditText(name='reason', parent=self.mainCont, padTop=24, maxLength=40, align=uiconst.TOTOP, label=localization.GetByLabel('UI/Wallet/WalletWindow/Reason'))
        self.btnGroup = ButtonGroup(parent=self.mainCont, align=uiconst.TOTOP, padTop=24, btns=((localization.GetByLabel('UI/Common/Buttons/OK'),
          self.Confirm,
          (),
          81,
          1,
          1,
          0), (localization.GetByLabel('UI/Common/Buttons/Cancel'),
          self.CloseByUser,
          (),
          81,
          0,
          0,
          0)))
        uicore.registry.SetFocus(self.amount)

    def OnMainContResized(self):
        _, height = self.GetWindowSizeForContentSize(height=self.mainCont.height)
        self.SetFixedHeight(height)

    def _InitVariables(self):
        if self.fromID == session.charid:
            self.maxISKvalue = self.walletSvc.GetWealth()
            self.showFromAccount = False
        else:
            self.maxISKvalue = self.walletSvc.GetCorpWealth(self.fromAccountKey)
            self.showFromAccount = True
            if self.fromAccountKey is None:
                self.fromAccountKey = session.corpAccountKey
        if self.toID == session.corpid:
            self.showToAccount = True
        else:
            self.showToAccount = False

    def OnPersonalAccountChangedClient(self, newBalance, transaction):
        if self.fromID == session.charid:
            self._UpdateMaxISKValue(newBalance)

    def OnCorpAccountChangedClient(self, balance, corpAccountKey, difference):
        if self.fromID != session.charid:
            self._UpdateMaxISKValue(balance)

    def _UpdateMaxISKValue(self, value):
        self.maxISKvalue = value
        self.amount.SetMaxValue(self.maxISKvalue)

    def Confirm(self, *args):
        toAccountKey = None
        amount = self.amount.GetValue()
        reason = self.reason.GetValue()
        if amount <= 0:
            return
        if self.showToAccount:
            toAccountKey = self.combo.GetValue()
        if self.fromID == session.charid:
            sm.RemoteSvc('account').GiveCash(self.toID, amount, reason, toAccountKey=toAccountKey)
        else:
            sm.RemoteSvc('account').GiveCashFromCorpAccount(self.toID, amount, self.fromAccountKey, toAccountKey=toAccountKey, reason=reason)
        ShowQuickMessage(GetByLabel('UI/Wallet/WalletWindow/TransferSuccessful'))
        self.CloseByUser()
