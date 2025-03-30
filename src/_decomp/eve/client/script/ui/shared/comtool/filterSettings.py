#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\comtool\filterSettings.py
import localization
import carbonui.const as uiconst
from carbonui.primitives.line import Line
from carbonui.button.group import ButtonGroup
from carbonui.control.checkbox import Checkbox
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from carbonui.control.window import Window
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from carbonui.control.dragResizeCont import DragResizeCont
from carbonui.primitives.container import Container
from carbon.common.script.util.commonutils import StripTags
from eveservices.xmppchat import GetChatService
SPLITTER = ','

class ChatFilterSettings(Window):
    default_width = 380
    default_height = 480
    default_minSize = (default_width, default_height)
    default_windowID = 'ChatFilterSettings'
    default_captionLabelPath = 'UI/Chat/ChannelWindow/ChatWordFilters'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        chatFilters = GetChatService().GetChatFilters() or {}
        bannedWordsList = chatFilters.get('bannedWords', [])
        highlightWordsList = chatFilters.get('highlightWords', [])
        blinkOnHighlightWords = chatFilters.get('blinkOnHighlightWords', False)
        btnGroup = ButtonGroup(parent=self.sr.main, padTop=16, line=True)
        btnGroup.AddButton(label=localization.GetByLabel('UI/Common/Buttons/Save'), func=self.Save, args=(), isDefault=True)
        btnGroup.AddButton(label=localization.GetByLabel('UI/Common/Buttons/Cancel'), func=self.Cancel, isDefault=False)
        padding = 4
        bannedWordsCont = DragResizeCont(name='bannedWordsCont', parent=self.sr.main, align=uiconst.TOTOP_PROP, minSize=0.3, maxSize=0.7, defaultSize=0.45)
        self.bannedWordsLabel = EveLabelMedium(parent=bannedWordsCont, name='bannedWordsLabel', align=uiconst.TOTOP, state=uiconst.UI_DISABLED, text=localization.GetByLabel('UI/Chat/ChannelWindow/BannedWordText'), padBottom=4)
        bannedWords = SPLITTER.join(bannedWordsList)
        self.bannedWordsField = EditPlainText(name='bannedWordsField', parent=bannedWordsCont, align=uiconst.TOALL, ignoreTags=True, setvalue=bannedWords, hintText=localization.GetByLabel('UI/Chat/ChannelWindow/WordSeparatorText'))
        lowerCont = Container(parent=self.sr.main, name='lowerCont', align=uiconst.TOALL, padLeft=padding, padRight=padding)
        self.highlightWordsLabel = EveLabelMedium(parent=lowerCont, name='highlightWordsLabel', align=uiconst.TOTOP, state=uiconst.UI_DISABLED, text=localization.GetByLabel('UI/Chat/ChannelWindow/HighlightWordText'), padBottom=4)
        self.blinkOnHighlightWordsCb = Checkbox(name='blinkCb', parent=lowerCont, align=uiconst.TOBOTTOM, padTop=4, checked=blinkOnHighlightWords, text=localization.GetByLabel('UI/Chat/ChannelWindow/AlwaysBlink'))
        highlightWords = SPLITTER.join(highlightWordsList)
        self.highlightWordsField = EditPlainText(name='highlightWordsField', parent=lowerCont, align=uiconst.TOALL, ignoreTags=True, setvalue=highlightWords, hintText=localization.GetByLabel('UI/Chat/ChannelWindow/WordSeparatorText'))

    def Save(self):

        def GetTextParts(editField):
            text = editField.GetValue()
            text = StripTags(text)
            textParts = text.strip(SPLITTER).split(SPLITTER)
            textParts = filter(None, (word.strip() for word in textParts))
            return textParts

        bannedWords = GetTextParts(self.bannedWordsField)
        hightlightWords = GetTextParts(self.highlightWordsField)
        blinkOnHighlightWords = self.blinkOnHighlightWordsCb.checked
        GetChatService().SaveChatFiltersOnServer(bannedWords, hightlightWords, blinkOnHighlightWords)
        self.CloseByUser()

    def Cancel(self, btn):
        self.CloseByUser()
