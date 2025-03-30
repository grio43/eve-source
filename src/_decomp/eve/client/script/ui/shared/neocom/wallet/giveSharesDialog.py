#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\giveSharesDialog.py
import localization
from carbonui import const as uiconst
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.layoutGrid import LayoutGrid
from eve.client.script.ui.control import eveIcon, eveLabel
from carbonui.button.group import ButtonGroup
from carbonui.control.button import Button
from carbonui.control.window import Window
from eve.client.script.ui.util import searchOld
from eve.common.lib import appConst as const
from eveexceptions import UserError

class GiveSharesDialog(Window):
    default_windowID = 'GiveSharesDialog'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        corporationID = attributes.corporationID
        maxShares = attributes.maxShares
        shareholderID = attributes.shareholderID
        self.ownerID = None
        self.searchStr = ''
        self.corporationID = corporationID
        self.maxShares = maxShares
        self.shareholderID = shareholderID
        self.scope = 'all'
        self.SetCaption(localization.GetByLabel('UI/Wallet/WalletWindow/CaptionGiveSharesTo', who=cfg.eveowners.Get(self.shareholderID).name))
        self.SetMinSize([400, 130])
        self.Layout()

    def Layout(self):
        self.sr.standardBtns = ButtonGroup(parent=self.GetMainArea(), btns=[[localization.GetByLabel('UI/Common/Buttons/OK'), self.OnOK], [localization.GetByLabel('UI/Common/Buttons/Cancel'), self.OnCancel]], align=uiconst.TOBOTTOM, padTop=8)
        self.topParent = ContainerAutoSize(name='topParent', parent=self.GetMainArea(), align=uiconst.TOTOP, clipChildren=True, callback=self._on_main_cont_size_changed, only_use_callback_when_size_changes=True)
        self.layout_container = LayoutGrid(parent=self.topParent, columns=4, align=uiconst.TOPLEFT, cellSpacing=(8, 8))
        self.ShowCorpLogo(self.corporationID)
        give_shares_label = eveLabel.EveCaptionMedium(text=localization.GetByLabel('UI/Wallet/WalletWindow/CaptionGiveShares'))
        self.layout_container.AddCell(give_shares_label, colSpan=3)
        self.sharesLabel = eveLabel.EveLabelSmall(text=localization.GetByLabel('UI/Wallet/WalletWindow/NumberOfShares'), align=uiconst.CENTERLEFT, parent=self.layout_container, state=uiconst.UI_NORMAL)
        inptShares = SingleLineEditInteger(name='edit', setvalue=self.maxShares, minValue=1, maxValue=self.maxShares, align=uiconst.CENTERLEFT, maxLength=32)
        self.layout_container.AddCell(inptShares, colSpan=2)
        self.sr.inptShares = inptShares
        self.ownerLabel = eveLabel.EveLabelSmall(text=localization.GetByLabel('UI/Wallet/WalletWindow/ToOwner'), parent=self.layout_container, state=uiconst.UI_NORMAL, align=uiconst.CENTERLEFT)
        inptOwner = SingleLineEditText(name='edit', parent=self.layout_container, align=uiconst.CENTERLEFT, maxLength=48)
        inptOwner.OnReturn = self.Search
        self.sr.inptOwner = inptOwner
        Button(parent=self.layout_container, label=localization.GetByLabel('UI/Wallet/WalletWindow/BtnSearch'), func=self.Search, btn_default=1, align=uiconst.CENTERLEFT)

    def _on_main_cont_size_changed(self):
        width, height = self.GetWindowSizeForContentSize(height=self.topParent.height + self.sr.standardBtns.height + self.sr.standardBtns.padTop, width=self.topParent.width)
        self.SetMinSize(size=(width, height), refresh=True)

    def ShowCorpLogo(self, corporationID):
        loc = ContainerAutoSize(name='logoContainer', align=uiconst.TOPLEFT)
        self.layout_container.AddCell(loc, rowSpan=4)
        if loc is not None:
            loc.Flush()
            logo = eveIcon.GetLogoIcon(itemID=corporationID, parent=loc, idx=0, state=uiconst.UI_PICKCHILDREN, size=64, ignoreSize=True)
            if hasattr(logo, 'children'):
                for child in logo.children:
                    child.state = uiconst.UI_DISABLED

    def Search(self, *args):
        self.searchStr = self.sr.inptOwner.GetValue().strip()
        self.ownerID = searchOld.Search(self.searchStr.lower(), const.groupCharacter, const.categoryOwner, hideNPC=1, searchWndName='walletSearchSearch', hideDustChars=True)
        if self.ownerID:
            self.sr.inptOwner.SetText(cfg.eveowners.Get(self.ownerID).name)

    def OnOK(self, *args):
        if not self.ownerID:
            self.Search()
        if self.ownerID:
            self.TransferShares(self.ownerID, self.sr.inptShares.GetValue())
            self.CloseByUser()
        else:
            raise UserError('GiveSharesSelectOwner')

    def OnCancel(self, *args):
        self.ownerID = None
        self.CloseByUser()

    def TransferShares(self, toShareholderID, numberOfShares):
        if cfg.eveowners.Get(self.shareholderID).typeID == const.typeCorporation:
            sm.GetService('corp').MoveCompanyShares(self.corporationID, toShareholderID, numberOfShares)
        else:
            sm.GetService('corp').MovePrivateShares(self.corporationID, toShareholderID, numberOfShares)
