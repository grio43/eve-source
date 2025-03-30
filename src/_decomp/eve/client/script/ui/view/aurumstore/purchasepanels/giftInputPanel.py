#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\view\aurumstore\purchasepanels\giftInputPanel.py
import carbonui.const as uiconst
import localization
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.util.color import Color
from eve.client.script.ui.control import eveLabel
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.searchinput import SearchInput
from eve.client.script.ui.shared.userentry import User
from eve.client.script.ui.util import searchUtil
from eve.client.script.ui.view.aurumstore.purchasepanels.basePurchasePanel import BasePurchasePanel
from eve.client.script.ui.view.aurumstore.errorTooltip import ErrorTooltip
from utillib import KeyVal
DEFAULT_PADDING = 10
MAX_SUBJECT_LENGTH = 78
MAX_MESSAGE_LENGTH = 140
MAX_NAME_LENGTH = 64

class GiftingInputPanel(BasePurchasePanel):
    __notifyevents__ = ['OnEndChangeDevice']
    default_name = 'giftingInputPanel'

    def ApplyAttributes(self, attributes):
        super(GiftingInputPanel, self).ApplyAttributes(attributes)
        self.selectedCharacterID = None
        self.offer = attributes.offer
        self.photoSvc = sm.GetService('photo')
        self.construct_layout()
        sm.RegisterNotify(self)

    def construct_layout(self):
        self.mainContainer = Container(parent=self, padding=(DEFAULT_PADDING,) * 4)
        self.construct_search_input()
        self.construct_message_input()

    def construct_message_input(self):
        self.messageMainContainer = Container(name='MessageMainContainer', parent=self.mainContainer, align=uiconst.TOALL, bgColor=Color.GRAY1, top=5)
        subject_container = Container(name='SubjectContainer', parent=self.messageMainContainer, align=uiconst.TOTOP, height=32)
        Sprite(parent=subject_container, align=uiconst.TOLEFT, texturePath='res:/UI/Texture/WindowIcons/evemail.png', width=32, height=32, opacity=0.7)
        self.subjectEdit = SingleLineEditText(name='SubjectTextEdit', parent=subject_container, align=uiconst.TOALL, maxLength=MAX_SUBJECT_LENGTH, hintText=localization.GetByLabel('UI/VirtualGoodsStore/GiftingSubjectPlaceholder'), isCharacterField=True, bgColor=Color.GRAY1, width=0, top=0)
        message_container = Container(name='MessageContainer', parent=self.messageMainContainer, bgColor=Color.GRAY1)
        self.characterCounter = Label(text='0/%s' % MAX_MESSAGE_LENGTH, parent=message_container, color=(1.0, 1.0, 1.0, 0.6), fontsize=12, left=5, top=2, align=uiconst.BOTTOMRIGHT, state=uiconst.UI_DISABLED, opacity=0.7)
        self.messageEdit = EditPlainText(name='messageTextEdit', parent=message_container, hintText=localization.GetByLabel('UI/VirtualGoodsStore/GiftingMessagePlaceholder'), counterMax=MAX_MESSAGE_LENGTH, maxLength=MAX_MESSAGE_LENGTH, customCounter=self.characterCounter)

    def construct_search_input(self):
        self.searchContainer = Container(name='SearchBarContainer', parent=self.mainContainer, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN, height=32, bgColor=Color.GRAY1)
        search_icon_container = Container(parent=self.searchContainer, align=uiconst.TOLEFT, left=5, width=24)
        Sprite(name='SearchIcon', parent=search_icon_container, align=uiconst.CENTER, width=24, height=24, texturePath='res:/UI/Texture/Icons/searchMagnifyingGlass.png', opacity=0.5)
        self.searchInput = SearchInput(parent=self.searchContainer, align=uiconst.TOALL, GetSearchEntries=self.search, maxLength=MAX_NAME_LENGTH, OnSearchEntrySelected=self.on_search_entry_selected, hintText=localization.GetByLabel('UI/ActivatePlex/SearchHint'), width=0, top=0, padLeft=5, allowBrowsing=True)
        self.searchInput.SetHistoryVisibility(False)
        self.searchInput.underlay.Close()
        self.errorTooltip = ErrorTooltip(errorMessage=localization.GetByLabel('UI/VirtualGoodsStore/Purchase/NoRecipientErrorBody'))
        self.entryContainer = Container(name='EntryContainer', parent=self.searchContainer, align=uiconst.TOTOP, state=uiconst.UI_DISABLED, height=32, bgColor=Color.GRAY1, padLeft=5, display=False)
        self.entryContainerIcon = Sprite(parent=self.entryContainer, align=uiconst.CENTERLEFT, pos=(0, 0, 32, 32))
        clip_container = Container(parent=self.entryContainer, clipChildren=True, padding=(40, 0, 36, 0))
        self.entryContainerTitle = eveLabel.EveLabelMediumBold(parent=clip_container, align=uiconst.CENTERLEFT, text='', width=150)
        self.entryContainerButton = ButtonIcon(parent=self.entryContainer, texturePath='res:/UI/Texture/Icons/73_16_210.png', align=uiconst.CENTERRIGHT, func=self.reset_search, width=16, height=16, iconSize=16, left=5, state=uiconst.UI_HIDDEN)

    def search(self, search_string):
        self.fade_out_error_tooltip()
        if len(search_string) < 3:
            return []
        else:
            return searchUtil.SearchCharacters(search_string)

    def on_search_entry_selected(self, result):
        if isinstance(result, User):
            result = result.sr.node
        else:
            result = result[0]
        self.selectedCharacterID = result.charID
        self.entryContainerIcon.texturePath = self.photoSvc.GetPortrait(self.selectedCharacterID, size=64)
        self.entryContainerTitle.text = result.label
        self.entryContainerButton.SetState(uiconst.UI_NORMAL)
        self.searchInput.SetValue('')
        self.searchInput.display = False
        self.entryContainer.display = True
        self.entryContainer.SetState(uiconst.UI_NORMAL)

    def reset_search(self, *args, **kwargs):
        self.selectedCharacterID = None
        self.searchInput.display = True
        self.entryContainer.display = False
        uicore.registry.SetFocus(self.searchInput)

    def OnPanelActivated(self):
        self.SetState(uiconst.UI_NORMAL)
        animations.FadeIn(self)
        uicore.registry.SetFocus(self.searchInput)

    def get_gifting_information(self):
        if not self.selectedCharacterID:
            if not self.errorTooltip.tooltipPanel:
                self.errorTooltip.CreateTooltip(parent=uicore.layer.menu, owner=self.searchInput, idx=0)
                self.errorTooltip.tooltipPanel.SetOpacity(1)
            return
        return KeyVal(toCharacterID=self.selectedCharacterID, message=self.get_message())

    def get_message(self):
        subject = self.subjectEdit.GetValue()
        message = self.messageEdit.GetValue(html=0)
        if subject or message:
            if not subject:
                return message
            elif not message:
                return subject
            else:
                return '%s\n%s' % (subject, message)
        else:
            return ''

    def fade_out_error_tooltip(self):
        if self.errorTooltip.tooltipPanel:
            animations.FadeOut(self.errorTooltip.tooltipPanel, duration=0.5, callback=self.errorTooltip.Close)

    def OnEndChangeDevice(self, *args):
        if self.errorTooltip.tooltipPanel:
            self.errorTooltip.Close()
            self.create_error_tooltip()

    def create_error_tooltip(self):
        self.errorTooltip.CreateTooltip(parent=uicore.layer.menu, owner=self.searchInput, idx=0)
        self.errorTooltip.tooltipPanel.SetOpacity(1)

    def Close(self):
        self.errorTooltip.Close()
        super(GiftingInputPanel, self).Close()
