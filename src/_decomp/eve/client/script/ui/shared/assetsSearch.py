#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\assetsSearch.py
import carbonui.const as uiconst
import localization
from carbon.common.script.util import timerstuff
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.sprite import Sprite
from eveAssets.assetSearchUtil import IsPartOfText, IsTextMatch, ParseString

class SearchBox(SingleLineEditText):
    __guid__ = 'assets.SearchBox'
    default_dynamicHistoryWidth = True

    def ApplyAttributes(self, attributes):
        super(SearchBox, self).ApplyAttributes(attributes)
        self.blockSetValue = True
        self.textRightMargin = 1
        self.searchKeywords = attributes.get('keywords', [])
        self.CreateLayout()

    def SetValue(self, text, *args, **kwargs):
        oldText = self.GetValue()
        super(SearchBox, self).SetValue(text, *args, **kwargs)
        self.caretIndex = self.GetCursorFromIndex(self.GetSmartCaretIndex(oldText, text))
        self.RefreshCaretPosition()

    def GetSmartCaretIndex(self, oldText, newText):
        oldText = oldText[::-1]
        newText = newText[::-1]
        for i in xrange(len(oldText)):
            if oldText[i] != newText[i]:
                return len(newText) - i

        return len(newText)

    def CreateLayout(self):
        self.optionIcon = Sprite(parent=self.sr.maincontainer, name='options', texturePath='res:/UI/Texture/Icons/38_16_229.png', pos=(0, 0, 16, 16), align=uiconst.TORIGHT, idx=0, hint=localization.GetByLabel('UI/Inventory/AssetSearch/KeywordOptionsHint'))
        self.optionIcon.SetAlpha(0.8)
        self.optionIcon.OnClick = self.OnOptionClick

    def OnOptionClick(self):
        self.ShowHistoryMenu(self.GetStaticHints())

    def GetStaticHints(self):
        currentText = self.GetValue(registerHistory=0)
        currentText = currentText.rstrip()
        if currentText:
            currentText += ' '
        hints = []
        for kw in self.searchKeywords:
            hints.append((localization.GetByLabel('UI/Inventory/AssetSearch/KeywordHint', keyword=kw.keyword, description=kw.optionDescription), '%s%s: ' % (currentText, kw.keyword)))

        return hints

    def GetDynamicHints(self):
        hints = []
        caretIndex = self.caretIndex[0]
        currentText = self.GetValue(registerHistory=0)
        headText, tailText = currentText[:caretIndex], currentText[caretIndex:]
        tailText = tailText.lstrip()
        trimmedText = headText.rstrip()
        if trimmedText.endswith(':'):
            strippedText, lastWord = self.SplitText(trimmedText, removeSeprator=True)
            if lastWord:
                for kw in self.IterMatchingKeywords(lastWord):
                    if kw.specialOptions:
                        for option in kw.specialOptions:
                            hints.append((localization.GetByLabel('UI/Inventory/AssetSearch/OptionHint', keyword=kw.keyword, option=option), '%s%s: %s %s' % (strippedText,
                              kw.keyword,
                              option,
                              tailText)))

        else:
            strippedText, lastWord = self.SplitText(trimmedText, removeSeprator=False)
            freeText, matches = ParseString(trimmedText)
            if lastWord:
                if matches and IsTextMatch(lastWord, matches[-1][1]):
                    keyword, value = matches[-1]
                    for kw in self.IterMatchingKeywords(keyword):
                        if kw.specialOptions:
                            for option in kw.specialOptions:
                                if IsPartOfText(option, value):
                                    hints.append((localization.GetByLabel('UI/Inventory/AssetSearch/OptionHint', keyword=kw.keyword, option=option), '%s%s %s' % (strippedText, option, tailText)))

                            break

                else:
                    for kw in self.IterMatchingKeywords(lastWord):
                        hints.append((localization.GetByLabel('UI/Inventory/AssetSearch/KeywordHint', keyword=kw.keyword, description=kw.optionDescription), '%s%s: %s' % (strippedText, kw.keyword, tailText)))

        return hints

    def IterMatchingKeywords(self, keyword):
        for kw in self.searchKeywords:
            if IsPartOfText(kw.keyword, keyword):
                yield kw

    def SplitText(self, baseText, removeSeprator = False):
        strippedText, lastWord = (None, None)
        parts = baseText.split()
        if parts:
            lastWord = parts[-1]
            strippedText = baseText[:-len(lastWord)]
            if removeSeprator:
                lastWord = lastWord[:-1]
            if strippedText:
                strippedText = strippedText.rstrip() + ' '
        return (strippedText, '' if lastWord is None else lastWord.lower())

    def TryRefreshHistory(self, currentString):
        self.refreshHistoryTimer = timerstuff.AutoTimer(200, self.TryRefreshHistory_Thread, currentString)

    def TryRefreshHistory_Thread(self, currentString):
        if currentString.rstrip().endswith(':'):
            self.CheckHistory()
        self.refreshHistoryTimer = None

    def OnHistoryClick(self, clickedString, *args):
        self.TryRefreshHistory(clickedString)

    def OnComboChange(self, combo, label, value, *args):
        self.SetValue(label, updateIndex=0)
        self.TryRefreshHistory(value)

    def GetValid(self):
        valid = super(SearchBox, self).GetValid()
        history = [ (text, text) for text in valid ]
        hints = self.GetDynamicHints()
        return hints + history

    def Confirm(self, *args):
        active = getattr(self, 'active', None)
        text = ''
        if active:
            text = active.string
            self.SetValue(text)
        super(SearchBox, self).Confirm(*args)
        if active:
            self.TryRefreshHistory(text)
