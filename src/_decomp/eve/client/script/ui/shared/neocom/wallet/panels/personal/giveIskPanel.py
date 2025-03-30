#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\panels\personal\giveIskPanel.py
from carbon.common.script.util.format import FmtAmt
from carbonui import uiconst
from carbonui.control.combo import Combo
from carbonui.control.singlelineedits.singleLineEditFloat import SingleLineEditFloat
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from eve.client.script.ui import eveColor
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.button import Button
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelLarge
from eve.client.script.ui.control.searchinput import SearchInput
from eve.client.script.ui.control.themeColored import FillThemeColored
from eve.client.script.ui.shared.userentry import User
from eve.client.script.ui.util import searchUtil
from eve.common.script.search.const import MatchBy
from localization import GetByLabel
from qtyTooltip.qtyConst import EDIT_INPUT_TYPE_ISK
from qtyTooltip.tooltip import GetQtyText
MAX_NAME_LENGTH = 64

class GiveIskPanel(Container):
    __notifyevents__ = ['OnPersonalAccountChangedClient']
    default_name = 'GiveIskPanel'

    def ApplyAttributes(self, attributes):
        super(GiveIskPanel, self).ApplyAttributes(attributes)
        sm.RegisterNotify(self)
        self.photoSvc = sm.GetService('photo')
        self.walletSvc = sm.GetService('wallet')
        self.selectedCharacterID = None
        self.minISKvalue = 0.1
        self.maxISKvalue = self.walletSvc.GetWealth()
        self.ConstructLayout()

    def ConstructLayout(self):
        self.mainCont = ContainerAutoSize(name='mainCont', align=uiconst.CENTERTOP, alignMode=uiconst.TOTOP, width=360, parent=self)
        self.searchInputCont = Container(parent=self.mainCont, name='searchInputCont', height=32, padTop=14, align=uiconst.TOTOP)
        self.resultParCont = ContainerAutoSize(name='resultParCont', parent=self.mainCont, align=uiconst.TOTOP)
        self.ConstructSearchTermsCombo()
        self.ConstructSearchInput()
        self.ConstructErrorLabel()
        self.ConstructResultContainer()
        self.ConstructAmountContainer()
        self.ConstructAmountLabel()
        self.ConstructTransferButton()

    def ConstructAmountLabel(self):
        self.amountLabel = EveLabelMedium(parent=self.mainCont, align=uiconst.TOTOP_NOPUSH, opacity=0.75)

    def OnAmountFocusLost(self, amountInput):
        self.UpdateAmountLabel(amountInput.text)

    def OnPersonalAccountChangedClient(self, newBalance, transaction):
        self._UpdateMaxISKValue(newBalance)

    def _UpdateMaxISKValue(self, value):
        self.maxISKvalue = value
        if self.amountInput:
            self.amountInput.SetMaxValue(self.maxISKvalue)

    def UpdateAmountLabel(self, amount):
        if not amount:
            return
        self.amountLabel.SetText(GetQtyText(float(amount), EDIT_INPUT_TYPE_ISK))

    def ConstructAmountContainer(self):
        self.amountInput = SingleLineEditFloat(name='iskAmountInput', parent=self.mainCont, align=uiconst.TOTOP, padTop=48, hintText=GetByLabel('UI/Wallet/WalletWindow/ISK'), minValue=self.minISKvalue, maxValue=self.maxISKvalue, decimalPlaces=2, OnChange=self.UpdateAmountLabel, OnFocusLost=self.OnAmountFocusLost, label=GetByLabel('UI/Wallet/WalletWindow/GiveAmount'))

    def ConstructTransferButton(self):
        cont = ContainerAutoSize(parent=self.mainCont, align=uiconst.TOTOP, padTop=32)
        grid = LayoutGrid(parent=cont, columns=2, cellSpacing=(16, 0))
        self.transferButton = Button(name='transferButton', parent=grid, align=uiconst.CENTERLEFT, label=GetByLabel('UI/HangarTransfer/TransferBtn'), func=self.TransferISK)
        self.transferButton.Disable()
        self.successLabel = EveLabelLarge(parent=grid, align=uiconst.CENTERLEFT, color=eveColor.SUCCESS_GREEN, text=GetByLabel('UI/Wallet/WalletWindow/TransferSuccessful'), opacity=0.0)

    def TransferISK(self, *args):
        amount = self.amountInput.GetValue()
        if amount <= 0:
            return
        message = GetByLabel('UI/Wallet/WalletWindow/TransactionConfirmation', amount=FmtAmt(amount), player=self.selectedCharacterID)
        if eve.Message('AskAreYouSure', {'cons': message}, uiconst.YESNO) != uiconst.ID_YES:
            return
        ret = sm.RemoteSvc('account').GiveCash(self.selectedCharacterID, amount)
        if ret:
            self.ResetSearch()
            self.amountInput.SetValue(0)
            animations.FadeIn(self.successLabel)

    def ConstructSearchInput(self):
        self.searchInput = SearchInput(parent=self.searchInputCont, align=uiconst.TOALL, pos=(0, 0, 0, 0), GetSearchEntries=self.SearchForCharacter, maxLength=MAX_NAME_LENGTH, OnSearchEntrySelected=self.OnSearchEntrySelected, hintText=GetByLabel('UI/ActivatePlex/SearchHint'), allowBrowsing=True, isCharacterField=True, label=GetByLabel('UI/Wallet/WalletWindow/TransferTo'))
        self.searchInput.SetHistoryVisibility(False)

    def ConstructResultContainer(self):
        self.resultContainer = Container(name='resultContainer', parent=self.resultParCont, align=uiconst.TOTOP, height=44, padTop=2, state=uiconst.UI_HIDDEN)
        FillThemeColored(bgParent=self.resultContainer, colorType=uiconst.COLORTYPE_UIBASECONTRAST)
        self.resultIcon = Sprite(name='resultIcon', parent=self.resultContainer, align=uiconst.CENTERLEFT, pos=(2, 0, 42, 42))
        self.characterNameLabel = EveLabelMedium(parent=self.resultContainer, align=uiconst.CENTERLEFT, text='', width=150, left=50)
        self.entryContainerButton = ButtonIcon(parent=self.resultContainer, texturePath='res:/UI/Texture/Icons/73_16_210.png', align=uiconst.TOPRIGHT, func=self.ResetSearch, width=7, height=7, iconSize=14, left=5, top=5)

    def ConstructSearchTermsCombo(self):
        self.searchTermsCombo = Combo(label=GetByLabel('UI/Common/SearchBy'), parent=self.searchInputCont, options=searchUtil.GetSearchByChoices(), name='walletGiveISKComboSearchBy', select=settings.user.ui.Get('ppSearchBy', MatchBy.partial_terms), width=115, align=uiconst.TORIGHT, padLeft=8, callback=self.ChangeSearchBy)

    def ConstructErrorLabel(self):
        self.errorLabel = EveLabelMedium(name='errorLabel', parent=self.mainCont, align=uiconst.TOTOP_NOPUSH, text=GetByLabel('UI/Common/NothingFound'), color=eveColor.WARNING_ORANGE, opacity=0.75, state=uiconst.UI_HIDDEN)

    def ChangeSearchBy(self, entry, header, value, *args):
        settings.user.ui.Set('ppSearchBy', value)

    def ResetSearch(self, *args, **kwargs):
        self.searchInputCont.Show()
        self.resultContainer.Hide()
        self.searchTermsCombo.Show()
        self.transferButton.Disable()
        self.selectedCharacterID = None
        uicore.registry.SetFocus(self.searchInput)

    def OnSearchEntrySelected(self, result):
        if isinstance(result, User):
            result = result.sr.node
        else:
            result = result[0]
        self.selectedCharacterID = result.charID
        self.photoSvc.GetPortrait(self.selectedCharacterID, size=64, sprite=self.resultIcon)
        self.characterNameLabel.SetText(result.label)
        self.searchInput.SetValue('')
        self.successLabel.SetAlpha(0)
        self.searchInputCont.Hide()
        self.resultContainer.Show()
        self.searchTermsCombo.Hide()
        self.transferButton.Enable()
        self.searchInput.CloseResultMenu()

    def SearchForCharacter(self, search_string):
        if len(search_string) < 3:
            return []
        else:
            searchTerms = settings.user.ui.Get('ppSearchBy', MatchBy.partial_terms)
            validCharacters = searchUtil.SearchCharacters(search_string, searchBy=searchTerms)
            if not validCharacters:
                self.ShowNoResultsError()
            else:
                self.errorLabel.Hide()
            return validCharacters

    def ShowNoResultsError(self):
        self.errorLabel.Show()
