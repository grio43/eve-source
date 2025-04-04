#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\editPlainText.py
import logging
import re
import sys
import types
from collections import defaultdict
import threadutils
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.util import mathUtil
from carbonui.control.scrollentries import ScrollEntryNode, SE_BaseClassCore, SE_TextlineCore
from carbonui.control.label import LabelOverride as Label
from carbonui.control.singlelineedits.caret import Caret
from carbonui.control.link import Link
from carbonui.fontconst import DEFAULT_FONTSIZE
from carbonui.text.color import TextColor
from carbonui.text.settings import check_convert_font_size
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from carbon.common.script.util.commonutils import StripTags
import blue
import telemetry
import uthread
import eveLocalization
import log
import carbonui.const as uiconst
import trinity
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.util.various_unsorted import GetBrowser, GetClipboardData, StringColorToHex
from carbonui.uicore import uicore
from eve.client.script.ui.control.eveScroll import Scroll
from menu import MenuLabel
logger = logging.getLogger(__name__)
LINESPLIT = re.compile('<br>|<br />|<br/>|\r\n|\n')
BOOLTAGS = [('loc', 'loc'),
 ('b', 'bold'),
 ('i', 'italic'),
 ('u', 'underline')]
VALUETAGS = [('url', None), ('fontsize', 'defaultFontSize'), ('color', 'defaultFontColor')]
HTMLCONVERSION = {'fontsize': 'font size',
 '/fontsize': '/font',
 'color': 'font color',
 '/color': '/font',
 'url': 'a href',
 '/url': '/a'}
HTMLFONTTAG = (('fontsize', 'size'), ('color', 'color'))
ENDLINKCHARS = u' ,'
TEXTSIDEMARGIN = 0
TEXTLINEMARGIN = 0

class EditPlainTextCore(Scroll):
    default_name = 'edit_plaintext'
    default_align = uiconst.TOTOP
    default_height = 100
    default_maxLength = None
    default_readonly = False
    default_showattributepanel = 0
    default_setvalue = ''
    default_allowFormatChanges = True
    default_fontsize = None
    default_fontStyle = None
    default_fontFamily = None
    default_fontPath = None
    default_fontcolor = TextColor.NORMAL
    default_linkStyle = uiconst.LINKSTYLE_REGULAR
    default_hintText = ''
    default_ignoreTags = False
    default_innerPadding = 8
    _autoSize = False

    def ApplyAttributes(self, attributes):
        if self.default_fontsize is None:
            self.default_fontsize = DEFAULT_FONTSIZE
        self.readonly = attributes.get('readonly', self.default_readonly)
        if self.readonly:
            attributes['hasUnderlay'] = False
        super(EditPlainTextCore, self).ApplyAttributes(attributes)
        self.sr.scrollTimer = None
        self.keybuffer = []
        self._activeParams = None
        self._activeNode = None
        self._selecting = 0
        self._showCursor = True
        self._maxGlobalCursorIndex = 0
        self._currentLen = None
        self.sr.paragraphs = []
        self.globalSelectionRange = (None, None)
        self.globalSelectionInitpos = None
        self.globalCursorPos = 0
        self.OnReturn = None
        self.resizeTasklet = None
        self.updating = 0
        self.readonly = attributes.get('readonly', self.default_readonly)
        self.autoScrollToBottom = 0
        self.defaultFontStyle = attributes.get('fontStyle', self.default_fontStyle)
        self.defaultFontFamily = attributes.get('fontFamily', self.default_fontFamily)
        self.defaultFontPath = attributes.get('fontPath', self.default_fontPath)
        self.defaultFontSize = attributes.get('fontsize', self.default_fontsize)
        self.defaultFontSize = check_convert_font_size(self.defaultFontSize)
        self.defaultFontColor = attributes.get('fontcolor', self.default_fontcolor)
        self.linkStyle = attributes.get('linkStyle', self.default_linkStyle)
        self.ignoreTags = attributes.get('ignoreTags', self.default_ignoreTags)
        self.allowFormatChanges = attributes.get('allowFormatChanges', self.default_allowFormatChanges)
        self.sr.content.GetMenu = self.GetMenuDelegate
        self.sr.content.OnKeyDown = self.OnKeyDown
        self.sr.content.OnDropData = self.OnContentDropData
        self.sr.content.OnMouseDown = self.OnMouseDown
        self.sr.content.OnMouseUp = self.OnMouseUp
        self.sr.content.cursor = uiconst.UICURSOR_IBEAM
        self._hintLabel = Label(parent=self.sr.clipper, align=uiconst.TOTOP, padding=6, state=uiconst.UI_DISABLED)
        maxLength = attributes.get('maxLength', self.default_maxLength)
        self.SetMaxLength(maxLength)
        self.counterMax = attributes.get('counterMax', maxLength)
        self.countWithTags = attributes.get('countWithTags', True)
        self.customCharCounter = attributes.get('customCounter')
        self.allowTruncating = attributes.get('allowTruncating', self.countWithTags)
        showattributepanel = attributes.get('showattributepanel', self.default_showattributepanel)
        if showattributepanel:
            self.ShowAttributePanel()
        self.SetHintText(attributes.get('hintText', self.default_hintText))
        setvalue = attributes.get('setvalue', self.default_setvalue)
        self.SetValue(setvalue)

    def DisableScrolling(self):
        self.scrollEnabled = False

    def EnableAutoSize(self):
        self._autoSize = True

    def CreateNode(self):
        entry = ScrollEntryNode(decoClass=SE_EditTextlineCore, SelectionHandler=self)
        return entry

    def Close(self, *args, **kwds):
        try:
            for glyphString in self.sr.paragraphs:
                glyphString.Reset()

            self.resizeTasklet = None
        except Exception as e:
            logger.error(e)

        super(EditPlainTextCore, self).Close(*args, **kwds)

    def ShowAttributePanel(self):
        if not self.readonly:
            from carbonui.control.fontAttributePanel import FontAttributePanel
            self.sr.attribPanel = FontAttributePanel(align=uiconst.TOTOP, padBottom=2, parent=self, idx=0, state=uiconst.UI_PICKCHILDREN, counterMax=self.counterMax, countWithTags=self.countWithTags, padding=(4, 0, 4, 0))

    def DoFontChange(self, *args):
        self.DoSizeUpdateDelayed()

    def IsLoading(self):
        return self._loading

    def CheckHintText(self):
        if self._hintText:
            self._hintLabel.fontsize = self.defaultFontSize
            self._hintLabel.fontColor = self.defaultFontColor
            self._hintLabel.opacity = 0.3
            self._hintLabel.text = self._hintText
        else:
            self._hintLabel.text = ''
        if self.HasText():
            self._hintLabel.display = False
        else:
            self._hintLabel.display = True

    def SetHintText(self, hint):
        self._hintText = hint
        self.CheckHintText()

    @telemetry.ZONE_METHOD
    def SetValue(self, text, scrolltotop = 0, cursorPos = None, preformatted = 0, html = 1, fontColor = None):
        if self.destroyed:
            return
        self._ResetCurrentLen()
        text = text or ''
        if not self.IsEnoughRoomForSet(text):
            if self.allowTruncating:
                text = text[:self.maxletters]
            else:
                return
        self.GetAbsolute()
        self._activeParams = None
        newGS = uicore.font.GetGlyphString()
        for glyphString in self.sr.paragraphs:
            glyphString.Reset()

        self.sr.paragraphs = [newGS]
        self.LoadContent(contentList=[])
        self.UpdateGlyphString(newGS)
        self.SetSelectionRange(None, None, updateCursor=False)
        self.SetCursorPos(0)
        self.SetSelectionInitPos(self.globalCursorPos)
        for tag, paramName in BOOLTAGS:
            setattr(self, 'tagStack_%s' % tag, [])

        for paramName, defaultAttrName in VALUETAGS:
            setattr(self, 'tagStack_%s' % paramName, [])

        self._activeParams = None
        scrollTo = None
        if scrolltotop:
            scrollTo = 0.0
        elif self.autoScrollToBottom and self.GetScrollProportion() == 0.0:
            scrollTo = 1.0
        self.InsertText(text)
        if not self.readonly:
            self.SetCursorPos(cursorPos or 0)
        if scrollTo is not None:
            self.ScrollToProportion(scrollTo)
        self.UpdateCharacterCounter()

    def Clear(self):
        self.SetText('')

    @telemetry.ZONE_METHOD
    def InsertText(self, text):
        if self.destroyed:
            return
        text = text or ''
        if not StripTags(text):
            text = ''
        if text.find('<h') != -1:
            text = text.replace('<h1>', '<br><fontsize=28><b>').replace('</h1>', '</b></fontsize><br>')
            text = text.replace('<h2>', '<br><fontsize=24><b>').replace('</h2>', '</b></fontsize><br>')
            text = text.replace('<h3>', '<br><fontsize=20><b>').replace('</h3>', '</b></fontsize><br>')
            text = text.replace('<h4>', '<br><fontsize=18><b>').replace('</h4>', '</b></fontsize><br>')
            text = text.replace('<h5>', '<br><fontsize=16><b>').replace('</h5>', '</b></fontsize><br>')
            text = text.replace('<h6>', '<br><fontsize=14><b>').replace('</h6>', '</b></fontsize><br>')
        text = text.replace('\t', '    ')
        lines = LINESPLIT.split(text)
        node = self.GetActiveNode()
        if node is None:
            return
        initCursor = self.globalCursorPos
        advance = 0
        stackCursorIndex = self.globalCursorPos - node.startCursorIndex + node.stackCursorIndex
        glyphString = node.glyphString
        nodesByGlyphStringIDs = self.GetDictNodesByGlyphStringIDs()
        for lineIdx, line in enumerate(lines):
            text = line
            if not self.ignoreTags and line.find('<') > -1 and line.find('>') > -1:
                for each in line.split(u'>'):
                    texttag = each.split(u'<', 1)
                    if len(texttag) == 1:
                        text, tag = self.Encode(texttag[0]), None
                    else:
                        text, tag = self.Encode(texttag[0]), texttag[1]
                    params = self.GetFontParams()
                    self.InsertToGlyphString(glyphString, params, text, stackCursorIndex)
                    stackCursorIndex += len(text)
                    advance += len(text)
                    if tag:
                        self.ParseTag(tag)

            else:
                text = self.Encode(text)
                self.InsertToGlyphString(glyphString, self.GetFontParams(), text, stackCursorIndex)
                stackCursorIndex += len(text)
                advance += len(text)
            gsNodes = self.UpdateGlyphString(glyphString, 0, 0, nodesByGlyphstringIDs=nodesByGlyphStringIDs)
            if lineIdx != len(lines) - 1:
                newGS = uicore.font.GetGlyphString()
                gsIndex = self.GetGlyphStringIndex(glyphString)
                self.InsertNewGlyphString(newGS, gsIndex + 1, gsNodes[-1].idx + 1, nodesByGlyphStringIDs)
                glyphString = newGS
                stackCursorIndex = len(newGS)
                advance += 1

        self.UpdatePosition()
        self.SetCursorPos(initCursor + advance)
        self.CheckHintText()

    SetText = SetValue

    def GetDictNodesByGlyphStringIDs(self):
        nodesByGlyphstringIDs = defaultdict(list)
        for node in self.sr.nodes:
            glyphStringID = id(node.glyphString)
            nodesByGlyphstringIDs[glyphStringID].append(node)

        return nodesByGlyphstringIDs

    def GetNodesByGlyphStringID(self, glyphStringID, nodesByGlyphstringIDs):
        nodes = nodesByGlyphstringIDs.get(glyphStringID, [])
        return sorted(nodes, key=lambda x: x.idx)

    def Encode(self, text):
        return text.replace(u'&gt;', u'>').replace(u'&lt;', u'<').replace(u'&amp;', u'&').replace(u'&GT;', u'>').replace(u'&LT;', u'<')

    def Decode(self, text):
        return text.replace(u'&', u'&amp;').replace(u'<', u'&lt;').replace(u'>', u'&gt;')

    def ParseTag(self, tag):
        orgtag = tag
        tag = tag.replace('"', '')
        tag = tag.replace("'", '')
        tag = tag.lower()
        if tag.startswith('font '):
            fontcolor = self.GetTagValue('color=', tag)
            if fontcolor:
                self.ParseTag('color=' + fontcolor)
            fontsize = self.GetTagValue('size=', tag)
            if fontsize:
                self.ParseTag('fontsize=' + fontsize)
            tagStack = getattr(self, 'tagStack_font', [])
            tagStack.append(tag)
            setattr(self, 'tagStack_font', tagStack)
            return
        if tag == '/font':
            tagStack = getattr(self, 'tagStack_font', [])
            if tagStack:
                closeFontTag = tagStack.pop()
                fontcolor = self.GetTagValue('color=', closeFontTag)
                if fontcolor:
                    self.ParseTag('/color')
                fontsize = self.GetTagValue('size=', closeFontTag)
                if fontsize:
                    self.ParseTag('/fontsize')
            return
        tag = tag.replace('a href=', 'url=').replace('/a', '/url').replace('bold', 'b').replace('/bold', '/b').replace('italic', 'i').replace('/italic', '/i')
        if tag[0] == '/':
            stackName = tag[1:]
        elif '=' in tag:
            stackName = tag.split('=')[0]
        else:
            stackName = tag
        tagStack = getattr(self, 'tagStack_%s' % stackName, [])
        if tag[0] == '/':
            if len(tagStack):
                tagStack.pop()
        elif tag.startswith(u'color='):
            colorSyntax = tag[6:]
            color = StringColorToHex(colorSyntax)
            if color:
                col = mathUtil.LtoI(long(color, 0))
                tagStack.append(col)
            else:
                hexColor = colorSyntax.replace('#', '0x')
                try:
                    col = mathUtil.LtoI(long(hexColor, 0))
                    if isinstance(col, long):
                        raise ValueError
                    tagStack.append(col)
                except ValueError:
                    if type(self.defaultFontColor) is types.IntType:
                        tagStack.append(-1)
                    else:
                        c = trinity.TriColor(*self.defaultFontColor)
                        tagStack.append(c.AsInt())

        elif '=' in tag:
            value = orgtag.split('=')
            value = '='.join(value[1:])
            if not value:
                return
            if value[0] == '"':
                value = value[1:]
            if value[-1] == '"':
                value = value[:-1]
            try:
                addVal = int(value)
            except:
                addVal = value

            tagStack.append(addVal)
        else:
            tagStack.append(1)
        setattr(self, 'tagStack_%s' % stackName, tagStack)

    def GetTagValue(self, tagtofind, tagstring):
        start = tagstring.find(tagtofind)
        if start != -1:
            end = tagstring.find(' ', start)
            if end == -1:
                end = tagstring.find('>', start)
            if end == -1:
                end = len(tagstring)
            return tagstring[start + len(tagtofind):end]

    def GetColorSyntax(self, color, html):
        if type(color) is types.IntType:
            c = trinity.TriColor()
            c.FromInt(color)
            color = (c.r,
             c.g,
             c.b,
             c.a)
        if html:
            colorString = '"#%02x%02x%02x%02x"' % (color[3] * 255,
             color[0] * 255,
             color[1] * 255,
             color[2] * 255)
        else:
            colorString = '0x%02x%02x%02x%02x' % (color[3] * 255,
             color[0] * 255,
             color[1] * 255,
             color[2] * 255)
        return colorString

    def GetValue(self, html = 1):
        return self.GetValueForParagraphs(html=html, paragraphs=self.sr.paragraphs)

    @telemetry.ZONE_METHOD
    def GetValueForParagraphs(self, html = 1, paragraphs = ()):

        def FormatValue(value, html):
            if html:
                return '"%s"' % value
            return value

        def FormatTag(fmttag, html):
            if html and fmttag in HTMLCONVERSION:
                return HTMLCONVERSION[fmttag]
            return fmttag

        defaultColorValue = self.GetColorSyntax(self.defaultFontColor, html)
        defaultFontSizeValue = FormatValue(self.defaultFontSize, html)
        defaultHtmlFontTagCombined = '<font size=%s color=%s>' % (defaultFontSizeValue, defaultColorValue)
        defaultAdded = False
        tagStacks = {}
        for tag, defaultAttrName in VALUETAGS:
            if defaultAttrName:
                tagStacks[tag] = [getattr(self, defaultAttrName, None)]
            else:
                tagStacks[tag] = [None]

        tagStacks['fontCombined'] = [defaultHtmlFontTagCombined]
        for tag, paramName in BOOLTAGS:
            tagStacks[tag] = [False]

        lastParams = None
        retString = ''
        addBreak = 0
        for glyphString in paragraphs:
            for charData in glyphString:
                advance, align, color, sbit, char, asc, des, params = charData
                if lastParams is not params:
                    lastParams = params
                    for paramName, defaultAttrName in VALUETAGS:
                        if html and paramName in ('font', 'color', 'fontsize'):
                            continue
                        if paramName == 'color' and tagStacks['url'][-1]:
                            continue
                        currentStack = tagStacks[paramName]
                        currentStackValue = currentStack[-1]
                        currentParamValue = params.get(paramName, None)
                        if currentParamValue != currentStackValue:
                            if len(currentStack) > 1:
                                retString += '<%s>' % FormatTag('/%s' % paramName, html)
                                currentStack.pop()

                    for tag, paramName in BOOLTAGS:
                        tagStack = tagStacks[tag]
                        paramValue = params.get(paramName, False)
                        if paramValue != tagStack[-1]:
                            if len(tagStack) > 1:
                                retString += '<%s>' % FormatTag('/%s' % tag, html)
                                tagStack.pop()

                    while addBreak > 0:
                        retString += '<br>'
                        addBreak -= 1

                    if html:
                        htmlFontTagCombined = ''
                        for fmtTag, htmlTag in HTMLFONTTAG:
                            paramValue = params.Get(fmtTag, None)
                            if paramValue:
                                if fmtTag == 'color':
                                    paramValue = self.GetColorSyntax(paramValue, html)
                                else:
                                    paramValue = FormatValue(paramValue, html)
                                if htmlFontTagCombined:
                                    htmlFontTagCombined += ' '
                                htmlFontTagCombined += '%s=%s' % (htmlTag, paramValue)

                        if htmlFontTagCombined:
                            htmlFontTagCombined = '<font %s>' % htmlFontTagCombined
                            currentStack = tagStacks['fontCombined']
                            if currentStack[-1] != htmlFontTagCombined:
                                if not defaultAdded:
                                    retString = defaultHtmlFontTagCombined + retString + '</font>'
                                    defaultAdded = True
                                if len(currentStack) > 1:
                                    retString += '</font>'
                                    currentStack.pop()
                                currentStack.append(htmlFontTagCombined)
                                retString += htmlFontTagCombined
                    for tag, paramName in BOOLTAGS:
                        if params.url and paramName != 'loc':
                            continue
                        tagStack = tagStacks[tag]
                        paramValue = params.get(paramName, False)
                        if paramValue != tagStack[-1] and paramValue:
                            retString += '<%s>' % FormatTag('%s' % tag, html)
                            tagStack.append(True)

                    for paramName, defaultAttrName in VALUETAGS:
                        if html and paramName in ('font', 'color', 'fontsize'):
                            continue
                        if paramName == 'color' and tagStacks['url'][-1]:
                            continue
                        currentStack = tagStacks[paramName]
                        currentStackValue = currentStack[-1]
                        currentParamValue = params.get(paramName, None)
                        if currentParamValue != currentStackValue:
                            if currentParamValue:
                                if paramName == 'color':
                                    formattedValue = self.GetColorSyntax(currentParamValue, html)
                                else:
                                    formattedValue = FormatValue(currentParamValue, html)
                                retString += '<%s=%s>' % (FormatTag(paramName, html), formattedValue)
                                currentStack.append(currentParamValue)

                retString += self.Decode(char)

            if glyphString is not self.sr.paragraphs[-1]:
                addBreak += 1

        for paramName, defaultAttrName in VALUETAGS:
            tagStack = tagStacks[paramName]
            while len(tagStack) > 1:
                retString += '<%s>' % FormatTag('/%s' % paramName, html)
                tagStack.pop()

        for tag, paramName in BOOLTAGS:
            tagStack = tagStacks[tag]
            while len(tagStack) > 1:
                retString += '<%s>' % FormatTag('/%s' % tag, html)
                tagStack.pop()

        if html:
            currentStack = tagStacks['fontCombined']
            while len(currentStack) > 1:
                currentStack.pop()
                retString += '</font>'

        if not StripTags(retString):
            return ''
        return retString

    def SetDefaultFontSize(self, size):
        size = check_convert_font_size(size)
        for glyphString in self.sr.paragraphs:
            for charData in glyphString:
                advance, align, color, sbit, char, asc, des, params = charData
                if params.fontsize == self.defaultFontSize:
                    params.fontsize = size

            self.ReloadGlyphString(glyphString)
            self.UpdateGlyphString(glyphString)

        self.SetCursorPos(self.globalCursorPos)
        if self._activeParams:
            self._activeParams.fontsize = size
        self.defaultFontSize = size
        self.UpdatePosition()

    def SetMaxLength(self, value):
        self.maxletters = value

    def OnSetFocus(self, *args, **kw):
        super(EditPlainTextCore, self).OnSetFocus(*args, **kw)
        if not self.readonly and uicore.imeHandler:
            uicore.imeHandler.SetFocus(self)
        self.RefreshCursorAndSelection()
        if hasattr(self, 'RegisterFocus'):
            self.RegisterFocus(self)

    def OnKillFocus(self, *args, **kw):
        super(EditPlainTextCore, self).OnKillFocus(*args, **kw)
        if not self.readonly and uicore.imeHandler:
            uicore.imeHandler.KillFocus(self)
        uthread.new(self.RefreshCursorAndSelection)
        uthread.new(self.OnFocusLost, self)

    def OnFocusLost(self, *args):
        pass

    def UpdateAttributePanel(self):
        params = self._activeParams
        if self.sr.attribPanel is not None:
            if type(params.color) is types.IntType:
                c = trinity.TriColor()
                c.FromInt(params.color)
                color = (c.r, c.g, c.b)
            else:
                color = params.color
            self.sr.attribPanel.AttribStateChange(params.bold, params.italic, params.underline, params.fontsize, color, params.url)

    @threadutils.throttled(0.5)
    def UpdateCharacterCounter_throttled(self):
        self.UpdateCharacterCounter()

    @telemetry.ZONE_METHOD
    def UpdateCharacterCounter(self):
        if self.sr.attribPanel is not None:
            self.sr.attribPanel.UpdateCounter(self._currentLen)
        if self.customCharCounter is not None:
            if self._currentLen is not None:
                currentLen = self._currentLen
            elif self.countWithTags:
                currentLen = len(self.GetValue())
                self._currentLen = currentLen
            elif isinstance(self, EditPlainTextCore):
                currentLen = len(self.GetAllText())
            else:
                currentLen = len(StripTags(self.GetSelectedText(getAll=True)))
            self.customCharCounter.SetText('%s/%s' % (currentLen, self.counterMax))

    def GetMenuDelegate(self, node = None):
        m = []
        m.append((MenuLabel('/Carbon/UI/Controls/Common/CopyAll'), self.CopyAll))
        if self.HasSelection():
            m.append((MenuLabel('/Carbon/UI/Controls/Common/CopySelected'), self.Copy))
            m.append((MenuLabel('/Carbon/UI/Controls/Common/CopySelectedWithFormatting'), self.CopyWithFormatting))
            if not self.readonly:
                m.append((MenuLabel('/Carbon/UI/Controls/Common/CutSelected'), self.Cut))
        clipboard = GetClipboardData()
        if clipboard and not self.readonly:
            m.append((MenuLabel('/Carbon/UI/Controls/Common/Paste'), self.Paste, (clipboard,)))
        return m

    def SelectLineUnderCursor(self):
        node = self.GetActiveNode()
        fromIdx, toIdx = node.startCursorIndex, node.endCursorIndex
        self.SetSelectionRange(fromIdx, toIdx, updateCursor=False)
        self.SetSelectionInitPos(fromIdx)
        self.SetCursorPos(toIdx)

    def FindWordBoundariesFromGlobalCursor(self, wordShift = 0):
        text = self.GetAllText(newLineStr=' ')
        boundaries = []
        counter = 0
        for each in uiconst.WORD_BOUNDARY_REGEX.split(text):
            if each:
                counter += len(each)
                boundaries.append(counter)

        wordStart = 0
        wordEnd = None
        for boundary in boundaries:
            if boundary >= self.globalCursorPos + wordShift:
                wordEnd = boundary
                break
            wordStart = boundary

        if wordEnd is None:
            wordEnd = len(text)
        leftOffset = wordStart - self.globalCursorPos
        rightOffset = wordEnd - self.globalCursorPos
        return (leftOffset, rightOffset, text)

    def SelectWordUnderCursor(self):
        leftBound, rightBound, allText = self.FindWordBoundariesFromGlobalCursor()
        fromIdx, toIdx = self.globalCursorPos + leftBound, self.globalCursorPos + rightBound
        while toIdx > fromIdx and allText[toIdx - 1] == ' ':
            toIdx -= 1

        self.SetSelectionRange(fromIdx, toIdx, updateCursor=False)
        self.SetSelectionInitPos(fromIdx)
        self.SetCursorPos(toIdx)

    def SetSelectionInitPos(self, globalIndex):
        self.globalSelectionInitpos = globalIndex

    @telemetry.ZONE_METHOD
    def SetSelectionRange(self, fromCharIndex, toCharIndex, updateCursor = True):
        if fromCharIndex == toCharIndex:
            fromCharIndex, toCharIndex = (None, None)
        globalSelectionRange = [fromCharIndex, toCharIndex]
        globalSelectionRange.sort()
        self.globalSelectionRange = globalSelectionRange
        if fromCharIndex is None or toCharIndex is None:
            self.SetSelectionInitPos(self.globalCursorPos)
        if updateCursor:
            self.RefreshCursorAndSelection()

    @telemetry.ZONE_METHOD
    def SetCursorPos(self, globalIndex, updateActiveParams = True):
        if globalIndex == -1:
            globalIndex = self._maxGlobalCursorIndex
        maxIndex = 0
        for gs in self.sr.paragraphs:
            maxIndex += len(gs) + 1

        maxIndex -= 1
        self._maxGlobalCursorIndex = max(0, maxIndex)
        self.globalCursorPos = max(0, min(self._maxGlobalCursorIndex, globalIndex))
        self.RefreshCursorAndSelection(updateActiveParams=updateActiveParams)

    @telemetry.ZONE_METHOD
    def RefreshCursorAndSelection(self, updateActiveParams = True):
        if self.destroyed:
            return
        i = 0
        stackShift = 0
        lastGlyphString = None
        globalCursorIndex = 0
        stackCursor = 0
        fromIdx, toIdx = self.globalSelectionRange
        for node in self.sr.nodes:
            if not issubclass(node.decoClass, SE_EditTextlineCore):
                continue
            if node._endIndex is None:
                letterCountInLine = 0
            else:
                letterCountInLine = node._endIndex - node._startIndex
            node.letterCountInLine = letterCountInLine
            if lastGlyphString is not None and lastGlyphString is not node.glyphString:
                stackShift += 1
                stackCursor = 0
            node.startCursorIndex = globalCursorIndex + stackShift
            node.endCursorIndex = node.startCursorIndex + letterCountInLine
            node.stackCursorIndex = stackCursor
            globalCursorIndex += letterCountInLine
            stackCursor += letterCountInLine
            lastGlyphString = node.glyphString
            if updateActiveParams and node.startCursorIndex <= self.globalCursorPos <= node.endCursorIndex:
                self._activeNode = node
                stackCursorIndex = self.globalCursorPos - node.startCursorIndex + node.stackCursorIndex
                self._activeParams = self.GetPriorParams(node.glyphString, stackCursorIndex) or self.GetFontParams()
                self._activeParams = self._activeParams.Copy()
                self.UpdateAttributePanel()
            if not self.readonly:
                if node.globalCursorPos is not None:
                    node.globalCursorPos = None
                    if node.panel:
                        node.panel.UpdateCursor()
            if fromIdx is None or not (fromIdx <= node.startCursorIndex <= toIdx or node.startCursorIndex <= fromIdx <= node.endCursorIndex):
                node.selectionStartIndex = None
                node.selectionEndIndex = None
            else:
                node.selectionStartIndex = max(0, fromIdx)
                node.selectionEndIndex = max(0, toIdx)
            if node.panel and hasattr(node.panel, 'UpdateSelectionHilite'):
                node.panel.UpdateSelectionHilite()
            i += 1

        if not self.readonly:
            node = self.GetActiveNode()
            if node:
                node.globalCursorPos = self.globalCursorPos
                if node.panel:
                    node.panel.UpdateCursor()

    @telemetry.ZONE_METHOD
    def GetActiveNode(self):
        ret = getattr(self, '_activeNode', None)
        if ret is None:
            ret = self.sr.nodes[0]
        return ret

    @telemetry.ZONE_METHOD
    def GetSelectedText(self):
        ret = ''
        selectedData = self.GetSeletedCharData()
        if not selectedData:
            return ret
        for glyphString, gsData in selectedData:
            for charIdx, (advance, align, color, sbit, char, asc, des, params) in gsData:
                ret += char

            ret += '\r\n'

        return ret[:-2]

    @telemetry.ZONE_METHOD
    def GetAllText(self, newLineStr = '\r\n'):
        ret = ''
        for glyphString in self.sr.paragraphs:
            ret += glyphString.GetText()
            ret += newLineStr

        return ret[:-len(newLineStr)]

    def OnMouseUpDelegate(self, _node, *args):
        self._selecting = 0
        self.sr.scrollTimer = None
        self.SetCursorPos(self.globalCursorPos)

    def OnMouseDownDelegate(self, _node, *args):
        self._selecting = 1
        if _node and _node.panel:
            self.SetCursorFromNodeAndMousePos(_node)
            if uicore.uilib.Key(uiconst.VK_SHIFT) and self.globalSelectionInitpos is not None:
                fromIdx, toIdx = self.globalSelectionRange
                newIndex = self.globalCursorPos
                toIndex = self.globalSelectionInitpos
                if newIndex > toIndex:
                    self.SetSelectionRange(toIndex, newIndex)
                else:
                    self.SetSelectionRange(newIndex, toIndex)
            else:
                self.SetSelectionRange(None, None)
                self.SetSelectionInitPos(self.globalCursorPos)
        self.sr.scrollTimer = AutoTimer(100, self.ScrollTimer)

    def SetCursorFromNodeAndMousePos(self, node):
        if node.panel is not None:
            internalPos = node.panel.GetInternalCursorPos()
            self.SetCursorPos(node.startCursorIndex + internalPos)
        else:
            self.SetCursorPos(-1)

    def GetLastTextline(self):
        totalLines = len(self.sr.content.children)
        for i in xrange(totalLines):
            nodePanel = self.sr.content.children[totalLines - i - 1]
            if isinstance(nodePanel, SE_EditTextlineCore):
                return nodePanel

    def CrawlForTextline(self, mo):
        if isinstance(mo, SE_EditTextlineCore):
            return mo
        if mo.parent:
            if mo.parent is uicore.desktop:
                return None
            return self.CrawlForTextline(mo.parent)

    def ScrollTimer(self):
        if not self._selecting or self.globalSelectionInitpos is None:
            self.sr.scrollTimer = None
            return
        if not uicore.uilib.leftbtn:
            self.sr.scrollTimer = None
            self._selecting = 0
            return
        toAffect = None
        if uicore.uilib.mouseOver.IsUnder(self):
            toAffect = self.CrawlForTextline(uicore.uilib.mouseOver)
        if toAffect is None:
            toAffect = self.GetLineAtCursorLevel()
        aL, aT, aW, aH = self.GetAbsolute()
        if uicore.uilib.y < aT:
            self.Scroll(1)
        elif uicore.uilib.y > aT + aH:
            self.Scroll(-1)
        if toAffect is None:
            return
        node = toAffect.sr.node
        if node is None:
            return
        self.SetCursorFromNodeAndMousePos(node)
        if self.globalCursorPos > self.globalSelectionInitpos:
            self.SetSelectionRange(self.globalSelectionInitpos, self.globalCursorPos)
        else:
            self.SetSelectionRange(self.globalCursorPos, self.globalSelectionInitpos)

    def GetLineAtCursorLevel(self):
        aL, aT, aW, aH = self.GetAbsolute()
        if uicore.uilib.y < aT:
            return self.sr.content.children[0]
        if uicore.uilib.y > aT + aH:
            return self.sr.content.children[-1]
        each = None
        for each in self.sr.content.children:
            l, t, w, h = each.GetAbsolute()
            if t < uicore.uilib.y <= t + h:
                return each

        return each

    def OnDragEnterDelegate(self, node, nodes):
        if self.readonly:
            return
        self.SetCursorFromNodeAndMousePos(node)

    def OnDragMoveDelegate(self, node, nodes):
        if self.readonly:
            return
        self.SetCursorFromNodeAndMousePos(node)

    def OnDropDataDelegate(self, node, nodes):
        pass

    def OnContentDropData(self, dragObj, nodes):
        self._ResetCurrentLen()
        self.SetCursorPos(self._maxGlobalCursorIndex)
        node = self.GetActiveNode()
        self.OnDropDataDelegate(node, nodes)
        self.UpdateCharacterCounter()

    def OnDropData(self, dragObj, nodes):
        return self.OnContentDropData(dragObj, nodes)

    def OnMouseUp(self, *args):
        self._selecting = 0
        self.sr.scrollTimer = None

    def OnMouseDown(self, button, *args):
        if button != uiconst.MOUSELEFT:
            return
        if len(self.sr.content.children):
            shift = uicore.uilib.Key(uiconst.VK_SHIFT)
            lastEntry = self.sr.content.children[-1]
            l, t, w, h = lastEntry.GetAbsolute()
            if uicore.uilib.y > t + h:
                if shift:
                    selectionStartIndex, selectionEndIndex = self.globalSelectionRange
                    self.SetSelectionRange(selectionStartIndex or self.globalCursorPos, self._maxGlobalCursorIndex, updateCursor=False)
                else:
                    self.SetSelectionRange(None, None, updateCursor=False)
                    self.SetSelectionInitPos(self._maxGlobalCursorIndex)
                self.SetCursorPos(self._maxGlobalCursorIndex)
        self._selecting = 1

    @telemetry.ZONE_METHOD
    def OnKeyDown(self, vkey, flag, *args, **kw):
        isMac = sys.platform.startswith('darwin')

        def k(win, mac):
            if isMac:
                return mac
            return win

        ctrl = uicore.uilib.Key(uiconst.VK_CONTROL)
        alt = uicore.uilib.Key(uiconst.VK_MENU)
        cmd = uicore.uilib.Key(uiconst.VK_LWIN)
        if vkey in (uiconst.VK_LEFT,
         uiconst.VK_RIGHT,
         uiconst.VK_UP,
         uiconst.VK_DOWN,
         uiconst.VK_HOME,
         uiconst.VK_END):
            if self.globalCursorPos is None:
                return
            preFromIdx, preToIdx = self.globalSelectionRange
            shift = uicore.uilib.Key(uiconst.VK_SHIFT)
            if not shift:
                self.SetSelectionRange(None, None)
            else:
                preFromIdx, preToIdx = (None, None)
            node = self.GetActiveNode()
            newCursorPos = self.globalCursorPos
            if vkey == uiconst.VK_LEFT and (not isMac or not cmd):
                if k(win=ctrl, mac=alt):
                    leftBound, rightBound, allText = self.FindWordBoundariesFromGlobalCursor()
                    newCursorPos = self.globalCursorPos + leftBound
                else:
                    fromIdx, toIdx = self.globalSelectionRange
                    if preFromIdx is not None and preToIdx is not None:
                        newCursorPos = min(preFromIdx, preToIdx)
                    else:
                        newCursorPos = max(0, self.globalCursorPos - 1)
                if shift:
                    selectionStartIndex, selectionEndIndex = self.globalSelectionRange
                    if selectionStartIndex is None:
                        self.SetSelectionRange(newCursorPos, self.globalCursorPos, updateCursor=False)
                    elif self.globalCursorPos == selectionStartIndex:
                        self.SetSelectionRange(newCursorPos, selectionEndIndex, updateCursor=False)
                    else:
                        self.SetSelectionRange(selectionStartIndex, newCursorPos, updateCursor=False)
            elif vkey == uiconst.VK_RIGHT and (not isMac or not cmd):
                if k(win=ctrl, mac=alt):
                    leftBound, rightBound, allText = self.FindWordBoundariesFromGlobalCursor(wordShift=1)
                    newCursorPos = self.globalCursorPos + rightBound
                elif preFromIdx is not None and preToIdx is not None:
                    newCursorPos = max(preFromIdx, preToIdx)
                else:
                    newCursorPos = self.globalCursorPos + 1
                if shift:
                    selectionStartIndex, selectionEndIndex = self.globalSelectionRange
                    if selectionStartIndex is None:
                        self.SetSelectionRange(self.globalCursorPos, newCursorPos, updateCursor=False)
                    elif self.globalCursorPos == selectionStartIndex:
                        self.SetSelectionRange(newCursorPos, selectionEndIndex, updateCursor=False)
                    else:
                        self.SetSelectionRange(selectionStartIndex, newCursorPos, updateCursor=False)
            elif vkey == uiconst.VK_UP:
                if not k(win=ctrl, mac=cmd):
                    self.OnUp()
                    posInLine = self.globalCursorPos - node.startCursorIndex
                    if node.idx > 0:
                        nodeAbove = self.GetNode(node.idx - 1)
                        if nodeAbove and nodeAbove.endCursorIndex is not None:
                            newCursorPos = min(nodeAbove.endCursorIndex, nodeAbove.startCursorIndex + posInLine)
                        else:
                            newCursorPos = 0
                        if shift:
                            selectionStartIndex, selectionEndIndex = self.globalSelectionRange
                            if selectionStartIndex is None:
                                self.SetSelectionRange(newCursorPos, self.globalCursorPos, updateCursor=False)
                            elif self.globalCursorPos == selectionStartIndex:
                                self.SetSelectionRange(newCursorPos, selectionEndIndex, updateCursor=False)
                            else:
                                self.SetSelectionRange(selectionStartIndex, newCursorPos, updateCursor=False)
            elif vkey == uiconst.VK_DOWN:
                if not k(win=ctrl, mac=cmd):
                    self.OnDown()
                    posInLine = self.globalCursorPos - node.startCursorIndex
                    nodeBelow = self.GetNode(node.idx + 1)
                    if nodeBelow and nodeBelow.startCursorIndex is not None:
                        newCursorPos = nodeBelow.startCursorIndex + min(posInLine, nodeBelow.letterCountInLine)
                    else:
                        newCursorPos = self._maxGlobalCursorIndex
                    if shift:
                        selectionStartIndex, selectionEndIndex = self.globalSelectionRange
                        if selectionStartIndex is None:
                            self.SetSelectionRange(self.globalCursorPos, newCursorPos, updateCursor=False)
                        elif self.globalCursorPos == selectionStartIndex:
                            self.SetSelectionRange(newCursorPos, selectionEndIndex, updateCursor=False)
                        else:
                            self.SetSelectionRange(selectionStartIndex, newCursorPos, updateCursor=False)
            elif vkey == uiconst.VK_HOME or vkey == uiconst.VK_LEFT and isMac and cmd:
                self.OnHome()
                if vkey == uiconst.VK_HOME and ctrl:
                    newCursorPos = 0
                else:
                    newCursorPos = node.startCursorIndex
                if shift:
                    selectionStartIndex, selectionEndIndex = self.globalSelectionRange
                    if selectionStartIndex is None:
                        self.SetSelectionRange(newCursorPos, self.globalCursorPos, updateCursor=False)
                    elif self.globalCursorPos == selectionStartIndex:
                        self.SetSelectionRange(newCursorPos, selectionEndIndex, updateCursor=False)
                    else:
                        self.SetSelectionRange(newCursorPos, selectionEndIndex, updateCursor=False)
            elif vkey == uiconst.VK_END or vkey == uiconst.VK_RIGHT and isMac and cmd:
                self.OnEnd()
                if vkey == uiconst.VK_END and ctrl:
                    newCursorPos = self._maxGlobalCursorIndex
                else:
                    newCursorPos = node.endCursorIndex
                if shift:
                    selectionStartIndex, selectionEndIndex = self.globalSelectionRange
                    if selectionStartIndex is None:
                        self.SetSelectionRange(self.globalCursorPos, newCursorPos, updateCursor=False)
                    elif self.globalCursorPos == selectionStartIndex:
                        self.SetSelectionRange(selectionStartIndex, newCursorPos, updateCursor=False)
                    else:
                        self.SetSelectionRange(selectionStartIndex, newCursorPos, updateCursor=False)
            self.SetCursorPos(newCursorPos)
            node = self.GetActiveNode()
            if node:
                self.ShowNodeIdx(node.idx)
        if self.readonly:
            return
        if k(win=ctrl, mac=cmd):
            if vkey == uiconst.VK_B:
                self.ToggleBold()
            if vkey == uiconst.VK_U:
                self.ToggleUnderline()
            if vkey == uiconst.VK_I:
                self.ToggleItalic()
            if vkey == uiconst.VK_ADD:
                self.EnlargeSize()
            if vkey == uiconst.VK_SUBTRACT:
                self.ReduceSize()
            if vkey == uiconst.VK_UP:
                self.CtrlUp(self)
            if vkey == uiconst.VK_DOWN:
                self.CtrlDown(self)
            if vkey in (uiconst.VK_B,
             uiconst.VK_U,
             uiconst.VK_I,
             uiconst.VK_ADD,
             uiconst.VK_SUBTRACT):
                self.UpdateCharacterCounter()
            return
        if vkey == uiconst.VK_DELETE:
            self.OnChar(127, flag)

    def ReadOnly(self, *args):
        self.readonly = True
        if self.sr.attribPanel is not None:
            self.sr.attribPanel.ShowOrHideCharacterCounter(showCounter=False)

    def Editable(self, *args):
        self.readonly = False
        if self.sr.attribPanel is not None:
            self.sr.attribPanel.ShowOrHideCharacterCounter(showCounter=True)

    @telemetry.ZONE_METHOD
    def OnChar(self, char, flag):
        if self.readonly:
            return False
        if char < 32 and char not in (uiconst.VK_RETURN, uiconst.VK_BACK):
            return False
        if self.globalCursorPos is None:
            return False
        self.keybuffer.append(char)
        if not self.updating:
            if char == uiconst.VK_RETURN and not uicore.uilib.Key(uiconst.VK_SHIFT) and self.OnReturn:
                self.keybuffer.pop(-1)
                return uthread.new(self.OnReturn)
            try:
                self.updating = 1
                while len(self.keybuffer):
                    char = self.keybuffer.pop(0)
                    if self.DeleteSelected() and char in [127, uiconst.VK_BACK]:
                        continue
                    self.Insert(char)

                if char == uiconst.VK_BACK:
                    self.UpdateCharacterCounter_throttled()
                else:
                    self.UpdateCharacterCounter()
            finally:
                self.updating = 0

        return True

    def SelectAll(self, *args):
        self.SetSelectionRange(0, self._maxGlobalCursorIndex)

    def Copy(self):
        selstring = self.GetSelectedText()
        if selstring:
            blue.pyos.SetClipboardData(selstring)

    def CopyAll(self):
        all = self.GetAllText()
        if all:
            blue.pyos.SetClipboardData(all)

    def CopyWithFormatting(self):
        selectedData = self.GetSeletedCharData()
        if not selectedData:
            return ''
        paragraphs = []
        for glyphString, gsData in selectedData:
            line = []
            for charIdx, charData in gsData:
                line.append(charData)

            paragraphs.append(line)

        text = self.GetValueForParagraphs(paragraphs=paragraphs)
        if text:
            blue.pyos.SetClipboardData(text)

    def _CopyAllWithFormatting(self):
        all = self.GetValue(html=True)
        if all:
            blue.pyos.SetClipboardData(all)

    def Cut(self):
        self.Copy()
        if not self.readonly:
            self.DeleteSelected()

    def IsEnoughRoomForInsert(self, textLen):
        if not self.maxletters:
            return True
        if self._currentLen is not None:
            currentLen = self._currentLen
        else:
            currentLen = self.GetLenghtOfCurrentText()
        if currentLen + textLen <= self.maxletters:
            return True
        return textLen <= self.RoomLeft()

    def IsEnoughRoomForSet(self, text):
        if not self.maxletters:
            return True
        if self.countWithTags:
            textLen = len(text)
        else:
            textLen = len(StripTags(text))
        if textLen <= self.maxletters:
            return True
        return textLen <= self.RoomLeft()

    def RoomLeft(self):
        if not self.maxletters:
            return None
        currentLen = self.GetLenghtOfCurrentText()
        return max(0, self.maxletters + len(self.GetSelectedText()) - currentLen)

    def GetLenghtOfCurrentText(self):
        if self.countWithTags:
            if self._currentLen is not None:
                return self._currentLen
            currentLen = len(self.GetValue())
            return currentLen
        else:
            return len(self.GetAllText())

    def Paste(self, text):
        self._ResetCurrentLen()
        if self.ValidatePaste:
            text = self.ValidatePaste(text)
        roomLeft = self.RoomLeft()
        if roomLeft is not None and roomLeft < len(text):
            uicore.Message('uiwarning03')
            text = text[:roomLeft]
        if self.readonly or not text:
            return
        self.DeleteSelected()
        self.InsertText(text)
        node = self.GetActiveNode()
        if node:
            self.ShowNodeIdx(node.idx)
        self.UpdatePosition()
        uicore.registry.SetFocus(self)
        self.UpdateCharacterCounter()
        self.OnChange()

    def ValidatePaste(self, text):
        return text

    def GetFontParams(self):
        std = uicore.font.GetParams()
        if self._activeParams:
            std.color = self._activeParams.color
            std.fontsize = self._activeParams.fontsize
        else:
            std.color = self.defaultFontColor
            std.fontsize = self.defaultFontSize
        for tag, paramName in BOOLTAGS:
            tagStack = getattr(self, 'tagStack_%s' % tag, [])
            std.Set(paramName, bool(tagStack))

        for paramName, defaultAttrName in VALUETAGS:
            tagStack = getattr(self, 'tagStack_%s' % paramName, [])
            if tagStack:
                std.Set(paramName, tagStack[-1])

        std.fontStyle = self.defaultFontStyle
        std.fontFamily = self.defaultFontFamily
        std.fontPath = self.defaultFontPath
        return std

    @telemetry.ZONE_METHOD
    def CheckLineWrap(self, glyphString):
        text = unicode(glyphString.GetText())
        if not text:
            return [(0, 0, 0, 12, 12)]
        maxWidth = self.GetContentWidth() - TEXTSIDEMARGIN - 1
        if maxWidth < 0:
            return [(0, 0, 0, 12, 12)]
        wpl = eveLocalization.WrapPointList(text, session.languageID)
        wrapPoints = wpl.GetLinebreakPoints()
        wrappedLines = []
        lineWidth = 0
        lineHeight = 0
        lineBaseLine = 0
        lineStartWrapPoint = 0
        lastWrapPoint = 0
        textLength = len(text)
        maxWidth = self.ScaleDpi(maxWidth)
        for wrapPoint in wrapPoints + [textLength]:
            if lastWrapPoint == wrapPoint:
                continue
            wordGlyphs = glyphString[lastWrapPoint:wrapPoint]
            sizeData = zip(*[ (glyph[0], glyph[5] - glyph[6], glyph[5]) for glyph in wordGlyphs ])
            wordWidth = sum(sizeData[0])
            if wordWidth > maxWidth:
                if lineWidth:
                    wrappedLines.append((lineStartWrapPoint,
                     lastWrapPoint,
                     lineWidth,
                     lineBaseLine,
                     lineHeight))
                    lineStartWrapPoint = lastWrapPoint
                lineWidth = 0
                lineHeight = 0
                lineBaseLine = 0
                glyphCounter = 0
                for glyph in wordGlyphs:
                    glyphWidth = glyph[0]
                    glyphBaseLine = glyph[5]
                    glyphHeight = glyphBaseLine - glyph[6]
                    if lineWidth + glyphWidth > maxWidth:
                        wrappedLines.append((lineStartWrapPoint,
                         lineStartWrapPoint + glyphCounter,
                         lineWidth,
                         lineBaseLine,
                         lineHeight))
                        lineWidth = glyphWidth
                        lineHeight = glyphHeight
                        lineBaseLine = glyphBaseLine
                        lineStartWrapPoint = lineStartWrapPoint + glyphCounter
                        glyphCounter = 1
                    else:
                        lineWidth += glyphWidth
                        lineHeight = max(lineHeight, glyphHeight)
                        lineBaseLine = max(lineBaseLine, glyphBaseLine)
                        glyphCounter += 1

            elif lineWidth + wordWidth > maxWidth:
                wrappedLines.append((lineStartWrapPoint,
                 lastWrapPoint,
                 lineWidth,
                 lineBaseLine,
                 lineHeight))
                lineWidth = wordWidth
                lineHeight = max(sizeData[1])
                lineBaseLine = max(sizeData[2])
                lineStartWrapPoint = lastWrapPoint
            else:
                lineWidth += wordWidth
                lineHeight = max(lineHeight, max(sizeData[1]))
                lineBaseLine = max(lineBaseLine, max(sizeData[2]))
            lastWrapPoint = wrapPoint

        if lineStartWrapPoint < textLength:
            wrappedLines.append((lineStartWrapPoint,
             textLength,
             lineWidth,
             lineBaseLine,
             lineHeight))
        return wrappedLines

    @telemetry.ZONE_METHOD
    def GetNodesWithGlyphString(self, glyphString):
        ret = []
        glyphStringID = id(glyphString)
        for node in self.sr.nodes:
            if id(node.glyphString) == glyphStringID:
                ret.append(node)
            elif ret:
                break

        return ret

    @telemetry.ZONE_METHOD
    def UpdateGlyphString(self, glyphString, advance = None, stackCursorIndex = None, nodesByGlyphstringIDs = None):
        if nodesByGlyphstringIDs:
            glyphStringID = id(glyphString)
            allNodesUsingGlyphString = self.GetNodesByGlyphStringID(glyphStringID, nodesByGlyphstringIDs)
        else:
            allNodesUsingGlyphString = self.GetNodesWithGlyphString(glyphString)
        lineIndexes = self.CheckLineWrap(glyphString)
        if stackCursorIndex is not None:
            lenNew = len(lineIndexes)
            lenOld = len(allNodesUsingGlyphString)
            if lenNew < lenOld:
                rem = allNodesUsingGlyphString[-(lenOld - lenNew):]
                for each in rem:
                    allNodesUsingGlyphString.remove(each)

                self.RemoveNodesRaw(rem, nodesByGlyphstringIDs)
            elif lenNew > lenOld:
                newNodes = []
                if allNodesUsingGlyphString:
                    startAt = allNodesUsingGlyphString[-1].idx + 1
                else:
                    startAt = 0
                for x in xrange(lenNew - lenOld):
                    newNode = self.CreateNode()
                    newNode.glyphString = glyphString
                    newNode._startIndex = 0
                    newNode._endIndex = 0
                    newNode._width = 0
                    newNode._baseHeight = self.ScaleDpi(12)
                    newNode._baseLine = 12
                    newNodes.append(newNode)

                self.InsertNodesRaw(startAt, newNodes, nodesByGlyphstringIDs)
                allNodesUsingGlyphString += newNodes
            updateCount = 0
            for i, lineData in enumerate(lineIndexes):
                old = allNodesUsingGlyphString[i]
                startIdx, endIdx, width, baseLine, baseHeight = lineData
                addAdv = 0
                if stackCursorIndex <= endIdx:
                    addAdv = advance
                if old._startIndex + addAdv != startIdx or old._endIndex + addAdv != endIdx:
                    doUpdate = True
                else:
                    doUpdate = False
                old._startIndex = startIdx
                old._endIndex = endIdx
                old._width = width
                old._baseHeight = baseHeight
                old._baseLine = baseLine
                if doUpdate:
                    if old.panel:
                        old.panel.Load(old)
                    updateCount += 1

        else:
            if allNodesUsingGlyphString:
                insertAt = allNodesUsingGlyphString[0].idx
                self.RemoveNodesRaw(allNodesUsingGlyphString, nodesByGlyphstringIDs)
            else:
                insertAt = 0
            newNodes = []
            for startIdx, endIdx, width, baseLine, baseHeight in lineIndexes:
                newNode = self.CreateNode()
                newNode.glyphString = glyphString
                newNode._startIndex = startIdx
                newNode._endIndex = endIdx
                newNode._width = width
                newNode._baseHeight = baseHeight
                newNode._baseLine = baseLine
                newNodes.append(newNode)

            self.InsertNodesRaw(insertAt, newNodes, nodesByGlyphstringIDs)
            allNodesUsingGlyphString = newNodes
        self.RefreshNodeIndexes()
        return allNodesUsingGlyphString

    @telemetry.ZONE_METHOD
    def RemoveNodesRaw(self, nodes, nodesByGlyphstringIDs = None):
        for node in nodes:
            if node.panel:
                node.panel.Close()
            if node in self.sr.nodes:
                self.sr.nodes.remove(node)

        self.RemoveNodesFromIDDict(nodesByGlyphstringIDs, nodes)

    @telemetry.ZONE_METHOD
    def InsertNodesRaw(self, fromIdx, nodesData, nodesByGlyphstringIDs = None):
        if fromIdx == -1:
            fromIdx = len(self.sr.nodes)
        idx = fromIdx
        for data in nodesData:
            newnode = self.AddNode(idx, data)
            idx += 1

        self.AddNodesToIDDict(nodesByGlyphstringIDs, nodesData)

    def UpdateContentSize(self, clipperWidth, clipperHeight, contentHeight):
        self.sr.content.width = clipperWidth
        oldHeight = self.sr.content.height
        if self._autoSize:
            self.sr.content.height = contentHeight
            self.height = contentHeight + self.sr.maincontainer.padTop + self.sr.maincontainer.padBottom + self.sr.clipper.padTop + self.sr.clipper.padBottom
        else:
            self.sr.content.height = max(clipperHeight, contentHeight)
        if oldHeight != contentHeight:
            if hasattr(self, 'OnContentSizeChanged'):
                self.OnContentSizeChanged(clipperWidth, self.sr.content.height)

    @telemetry.ZONE_METHOD
    def InsertNewGlyphString(self, glyphString, glyphStringIndex, nodeIndex, nodesByGlyphStringIDs = None):
        self.sr.paragraphs.insert(glyphStringIndex, glyphString)
        lineIndexes = self.CheckLineWrap(glyphString)
        newNodes = []
        for startIdx, endIdx, width, baseLine, baseHeight in lineIndexes:
            newNode = self.CreateNode()
            newNode.glyphString = glyphString
            newNode._startIndex = startIdx
            newNode._endIndex = endIdx
            newNode._width = width
            newNode._baseHeight = baseHeight
            newNode._baseLine = baseLine
            newNodes.append(newNode)

        self.InsertNodesRaw(nodeIndex, newNodes, nodesByGlyphStringIDs)

    def AddNodesToIDDict(self, nodesByGlyphstringIDs, newNodes):
        if nodesByGlyphstringIDs is None:
            return
        for eachNode in newNodes:
            glyphStringID = id(eachNode.glyphString)
            if eachNode not in nodesByGlyphstringIDs[glyphStringID]:
                nodesByGlyphstringIDs[glyphStringID].append(eachNode)

    def RemoveNodesFromIDDict(self, nodesByGlyphstringIDs, nodesToRemove):
        if not nodesByGlyphstringIDs:
            return
        for eachNode in nodesToRemove:
            glyphStringID = id(eachNode.glyphString)
            if glyphStringID in nodesByGlyphstringIDs and eachNode in nodesByGlyphstringIDs[glyphStringID]:
                nodesByGlyphstringIDs[glyphStringID].remove(eachNode)

    @telemetry.ZONE_METHOD
    def RemoveGlyphString(self, glyphString):
        allNodesInStack = self.GetNodesWithGlyphString(glyphString)
        if allNodesInStack:
            self.RemoveNodesRaw(allNodesInStack)
        gsIdx = self.GetGlyphStringIndex(glyphString)
        if gsIdx is not None:
            del self.sr.paragraphs[gsIdx]

    @telemetry.ZONE_METHOD
    def GetGlyphStringIndex(self, glyphString):
        for glyphStringIndex, _glyphString in enumerate(self.sr.paragraphs):
            if _glyphString is glyphString:
                return glyphStringIndex

    @telemetry.ZONE_METHOD
    def Insert(self, char):
        if char not in (uiconst.VK_BACK, 127) and not self.IsEnoughRoomForInsert(1):
            uicore.Message('uiwarning03')
            return
        node = self.GetActiveNode()
        if node is None:
            return
        stackCursorIndex = self.globalCursorPos - node.startCursorIndex + node.stackCursorIndex
        glyphString = node.glyphString
        glyphStringIndex = self.GetGlyphStringIndex(glyphString)
        cursorAdvance = 0
        setParams = None
        if char == uiconst.VK_RETURN:
            self._ResetCurrentLen()
            newGS = uicore.font.GetGlyphString()
            newGS += glyphString[stackCursorIndex:]
            glyphString.FlushFromIndex(stackCursorIndex)
            gsNodes = self.UpdateGlyphString(glyphString)
            gsIndex = self.GetGlyphStringIndex(glyphString)
            self.InsertNewGlyphString(newGS, gsIndex + 1, gsNodes[-1].idx + 1)
            self.RefreshNodes()
            cursorAdvance = 1
        elif char == 127:
            self._ResetCurrentLen()
            if stackCursorIndex == len(glyphString):
                if self.sr.paragraphs[-1] is not glyphString:
                    idx = self.GetGlyphStringIndex(glyphString)
                    glyphStringBelow = self.sr.paragraphs[idx + 1]
                    glyphString += glyphStringBelow
                    self.UpdateGlyphString(glyphString)
                    self.RemoveGlyphString(glyphStringBelow)
            else:
                glyphString.Remove(stackCursorIndex, stackCursorIndex + 1)
                self.UpdateGlyphString(glyphString, -1, stackCursorIndex + 1)
        elif char == uiconst.VK_BACK:
            setParams = self.GetPriorParams(node.glyphString, stackCursorIndex)
            if stackCursorIndex > 0:
                glyphString.Remove(stackCursorIndex - 1, stackCursorIndex)
                self.UpdateGlyphString(glyphString, -1, stackCursorIndex - 1)
                cursorAdvance = -1
                self._ResetCurrentLen()
            elif glyphStringIndex > 0:
                glyphStringAbove = self.sr.paragraphs[glyphStringIndex - 1]
                glyphStringAbove += glyphString
                self.RemoveGlyphString(glyphString)
                self.UpdateGlyphString(glyphStringAbove)
                cursorAdvance = -1
                self._ResetCurrentLen()
        else:
            currentParams = self._activeParams.Copy()
            unichar = unichr(char)
            fontFamily = uicore.font.GetFontFamilyBasedOnClientLanguageID()
            currentParams.fontFamily = fontFamily
            uicore.font.ResolveFontFamily(currentParams)
            if currentParams.url:
                if currentParams.has_key('loc'):
                    currentParams.pop('loc')
                nextParams = self.GetNextParams(glyphString, stackCursorIndex)
                cursorOffset = 1
                while nextParams and nextParams.has_key('loc') and nextParams.url is not None:
                    nextParams.pop('loc')
                    nextParams = self.GetNextParams(glyphString, stackCursorIndex + cursorOffset)
                    cursorOffset += 1

                prevParams = self.GetPriorParams(glyphString, stackCursorIndex)
                cursorOffset = -1
                while prevParams and prevParams.has_key('loc') and prevParams.url is not None:
                    prevParams.pop('loc')
                    prevParams = self.GetPriorParams(glyphString, stackCursorIndex + cursorOffset)
                    cursorOffset -= 1

                if unichar in ENDLINKCHARS:
                    nextParams = self.GetNextParams(glyphString, stackCursorIndex)
                    if not nextParams or nextParams.url != currentParams.url:
                        currentParams = currentParams.Copy()
                        currentParams.url = None
                        self.ResetToPreviousUrlParams(currentParams, glyphString, stackCursorIndex)
                elif stackCursorIndex == 0:
                    currentParams = currentParams.Copy()
                    currentParams.url = None
                    self.ResetToPreviousUrlParams(currentParams, glyphString, stackCursorIndex)
            self.InsertToGlyphString(glyphString, currentParams, unichar, stackCursorIndex)
            self.UpdateGlyphString(glyphString, advance=1, stackCursorIndex=stackCursorIndex)
            cursorAdvance = 1
            self.IncreaseCurrentLen()
        self.UpdatePosition()
        self.OnChange()
        self.SetCursorPos(self.globalCursorPos + cursorAdvance)
        self.CheckHintText()
        self.SetSelectionInitPos(self.globalCursorPos)
        node = self.GetActiveNode()
        if node:
            self.ShowNodeIdx(node.idx)
        if setParams:
            self._activeParams = setParams.Copy()
            self.UpdateAttributePanel()

    def DecreaseCurrentLen(self):
        self._AddOrRemoveOneFromCurrentLen(-1)

    def IncreaseCurrentLen(self):
        self._AddOrRemoveOneFromCurrentLen(1)

    def _AddOrRemoveOneFromCurrentLen(self, valueChange):
        if self._currentLen is None:
            self._currentLen = self.GetLenghtOfCurrentText()
        else:
            self._currentLen = max(0, self._currentLen + valueChange)

    def _ResetCurrentLen(self):
        self._currentLen = None

    def ResetToPreviousUrlParams(self, param, glyphString, stackCursorIndex):
        previousParams = None
        while stackCursorIndex:
            previousParams = self.GetPriorParams(glyphString, stackCursorIndex)
            stackCursorIndex = stackCursorIndex - 1

        if not previousParams or previousParams.url:
            param.color = self.defaultFontColor
            param.bold = False
            param.italic = False
            param.underline = False
        elif previousParams:
            param.color = previousParams.color
            param.bold = previousParams.bold
            param.italic = previousParams.italic
            param.underline = previousParams.underline

    def GetPriorParams(self, glyphString, stackCursorIndex):
        if len(glyphString):
            paramsInFront = glyphString[max(0, min(len(glyphString) - 1, stackCursorIndex - 1))][-1]
            return paramsInFront
        glyphStringIndex = self.GetGlyphStringIndex(glyphString)
        while glyphStringIndex > 0:
            glyphString = self.sr.paragraphs[glyphStringIndex - 1]
            if len(glyphString):
                return glyphString[-1][-1]
            glyphStringIndex = self.GetGlyphStringIndex(glyphString)

    def GetNextParams(self, glyphString, stackCursorIndex):
        if len(glyphString) > stackCursorIndex:
            paramsBehind = glyphString[stackCursorIndex][-1]
            return paramsBehind
        while glyphString is not self.sr.paragraphs[-1]:
            glyphStringIndex = self.GetGlyphStringIndex(glyphString)
            glyphString = self.sr.paragraphs[glyphStringIndex + 1]
            if len(glyphString):
                return glyphString[0][-1]

    def ReloadGlyphString(self, glyphString):
        data = [ (params, char) for advance, align, color, sbit, char, asc, des, params in glyphString ]
        del glyphString[:]
        for idx, (params, char) in enumerate(data):
            self.InsertToGlyphString(glyphString, params, char, idx)

    def RemoveFromGlyphString(self, glyphString, startIdx, endIdx):
        glyphString.Remove(startIdx, endIdx)

    @telemetry.ZONE_METHOD
    def InsertToGlyphString(self, glyphString, params, text, idx):
        if params.url:
            Link().FormatLinkParams(params, linkStyle=self.linkStyle)
        glyphString.Insert(params, text, idx)

    def OnClipperResize(self, width, height):
        self.RefreshNodes()
        self.DoSizeUpdateDelayed()

    def OnChange(self, *args):
        pass

    def GetSelection(self):
        return self.HasSelection()

    def HasSelection(self):
        fromIdx, toIdx = self.globalSelectionRange
        return fromIdx != toIdx

    def DeleteSelected(self):
        fromIdx, toIdx = self.globalSelectionRange
        if fromIdx == toIdx:
            return
        startGS = None
        endGS = None
        singleLineGS = None
        rmCompletely = []
        self._ResetCurrentLen()
        counter = 0
        for gsIdx, glyphString in enumerate(self.sr.paragraphs):
            gsLength = len(glyphString)
            if fromIdx <= counter and counter + gsLength <= toIdx:
                rmCompletely.append(glyphString)
            elif counter <= fromIdx <= counter + gsLength and counter <= toIdx <= counter + gsLength:
                singleLineGS = glyphString
                self.RemoveFromGlyphString(glyphString, fromIdx - counter, toIdx - counter)
            elif counter <= fromIdx <= counter + gsLength:
                startGS = glyphString
                startGS.FlushFromIndex(fromIdx - counter)
            elif counter <= toIdx <= counter + gsLength:
                endGS = glyphString
                glyphString.FlushToIndex(toIdx - counter)
            counter += gsLength
            counter += 1
            if counter >= toIdx:
                break

        if singleLineGS is not None:
            self.UpdateGlyphString(singleLineGS)
        elif startGS and endGS:
            startGS += endGS
            rmCompletely.append(endGS)
            self.UpdateGlyphString(startGS)
        elif startGS:
            self.UpdateGlyphString(startGS)
        elif endGS:
            self.UpdateGlyphString(endGS)
        for glyphString in rmCompletely:
            self.RemoveGlyphString(glyphString)

        if not self.sr.nodes:
            self.SetValue('')
        else:
            self.SetSelectionRange(None, None, updateCursor=False)
            self.SetCursorPos(fromIdx)
            self.SetSelectionInitPos(self.globalCursorPos)
        self.UpdatePosition()
        self.OnChange()
        return 1

    def GetSeletedCharData(self):
        fromIdx, toIdx = self.globalSelectionRange
        if fromIdx == toIdx:
            return
        startedCollection = False
        done = False
        ret = []
        counter = 0
        for gsIdx, glyphString in enumerate(self.sr.paragraphs):
            gData = []
            for cdIdx, charData in enumerate(glyphString):
                if counter == fromIdx:
                    startedCollection = True
                if startedCollection:
                    gData.append((cdIdx, charData))
                counter += 1
                if counter == toIdx:
                    done = True
                    break

            if counter == fromIdx:
                startedCollection = True
            if startedCollection:
                ret.append((glyphString, gData))
            if done:
                break
            counter += 1
            if counter == toIdx:
                done = True
                break

        return ret

    def ApplySelection(self, what, data = None, toggle = False):
        selectedData = self.GetSeletedCharData()
        if selectedData:
            node = self.GetActiveNode()
            stackCursorIndex = self.globalCursorPos - node.startCursorIndex + node.stackCursorIndex
            prevParams = self.GetPriorParams(node.glyphString, stackCursorIndex)
            if prevParams:
                params = prevParams.Copy()
            else:
                params = self.GetFontParams()
            changeGS = []
            changeParams = []
            for glyphString, gsData in selectedData:
                for charIdx, (advance, align, color, sbit, char, asc, des, _params) in gsData:
                    changeParams.append(_params)

                changeGS.append(glyphString)

            anchor = self.ApplyGameSelection(what, data, changeParams)
            if anchor == -1:
                anchor = None
            bBalance = 0
            uBalance = 0
            iBalance = 0
            for obj in changeParams:
                bBalance += 1 if obj.bold else -1
                uBalance += 1 if obj.underline else -1
                iBalance += 1 if obj.italic else -1

            params.bold = 1 if bBalance > 0 else 0
            params.italic = 1 if iBalance > 0 else 0
            params.underline = 1 if uBalance > 0 else 0
            if toggle:
                params.bold = not params.bold
                params.italic = not params.italic
                params.underline = not params.underline
            for obj in changeParams:
                if what == 1:
                    obj.bold = params.bold
                elif what == 2:
                    obj.italic = params.italic
                elif what == 3:
                    obj.underline = params.underline
                elif what == 4:
                    obj.color = data
                elif what == 5:
                    obj.fontsize = data
                elif what == 6 and anchor:
                    obj.url = anchor
                    obj.loc = 1

            for glyphString in changeGS:
                self.ReloadGlyphString(glyphString)
                self.UpdateGlyphString(glyphString)

            self._activeParams = params.Copy()
            self.UpdateAttributePanel()
            self.UpdatePosition()
            fromIdx, toIdx = self.globalSelectionRange
            self.SetCursorPos(max(fromIdx, toIdx))
            uicore.registry.SetFocus(self)
        else:
            self.UpdateAttributePanel()
        if what == 6:
            self.SetSelectionRange(None, None, updateCursor=False)
            self.SetSelectionInitPos(self.globalCursorPos)
            self.RemoveAnchor()
        self.RefreshCursorAndSelection(updateActiveParams=False)
        self.UpdatePosition()

    def ApplyGameSelection(self, *args):
        pass

    def OnUp(self):
        pass

    def OnDown(self):
        pass

    def OnHome(self):
        pass

    def OnEnd(self):
        pass

    def CtrlUp(self, *args):
        pass

    def CtrlDown(self, *args):
        pass

    @telemetry.ZONE_METHOD
    def DoSizeUpdateDelayed(self):
        if not self.sr.nodes:
            return
        try:
            self._DoSizeUpdateDelayed()
        except TaskletExit:
            pass
        except Exception as e:
            raise

    @telemetry.ZONE_METHOD
    def _DoSizeUpdateDelayed(self):
        if self.resizeTasklet:
            self.resizeTasklet.kill()
            self.resizeTasklet = None
        self.resizeTasklet = uthread.new(self.DoSizeUpdate)

    @telemetry.ZONE_METHOD
    def DoSizeUpdate(self):
        if self.destroyed:
            return
        self.resizing = 1
        nodesByGlyphstringIDs = self.GetDictNodesByGlyphStringIDs()
        for glyphString in self.sr.paragraphs:
            self.UpdateGlyphString(glyphString, 0, 0, nodesByGlyphstringIDs=nodesByGlyphstringIDs)

        self.RefreshNodes()
        if self.autoScrollToBottom and self.GetScrollProportion() == 0.0:
            self.ScrollToProportion(1.0)
        else:
            self.UpdatePosition()
        self.RefreshCursorAndSelection()
        self.resizeTasklet = None
        self.resizing = 1

    @telemetry.ZONE_METHOD
    def RefreshNodeIndexes(self, fromWhere = None):
        if self.destroyed:
            return
        for nodeidx, node in enumerate(self.sr.nodes):
            node.idx = nodeidx

    @telemetry.ZONE_METHOD
    def GetNodeHeight(self, node, clipperWidth):
        if node.idx == 0:
            xtraHeight = TEXTSIDEMARGIN
        else:
            xtraHeight = TEXTLINEMARGIN
        node.height = self.ReverseScaleDpi(node._baseHeight) + xtraHeight
        return node.height

    def EnlargeSize(self):
        if self.sr.attribPanel:
            self.sr.attribPanel.sr.comboFontSize.ShiftVal(1, 1)
            self.UpdateCharacterCounter()
            self.OnChange()

    def ReduceSize(self):
        if self.sr.attribPanel:
            self.sr.attribPanel.sr.comboFontSize.ShiftVal(-1, 1)
            self.UpdateCharacterCounter()
            self.OnChange()

    def ToggleBold(self):
        if not self.allowFormatChanges:
            return
        self._ResetCurrentLen()
        self._activeParams.bold = not self._activeParams.bold
        self.ApplySelection(1, toggle=True)
        self.UpdateCharacterCounter()
        self.OnChange()

    def ToggleUnderline(self):
        if not self.allowFormatChanges:
            return
        self._ResetCurrentLen()
        self._activeParams.underline = not self._activeParams.underline
        self.ApplySelection(3, toggle=True)
        self.UpdateCharacterCounter()
        self.OnChange()

    def ToggleItalic(self):
        if not self.allowFormatChanges:
            return
        self._ResetCurrentLen()
        self._activeParams.italic = not self._activeParams.italic
        self.ApplySelection(2, toggle=True)
        self.UpdateCharacterCounter()
        self.OnChange()

    def ChangeFontSize(self, newSize):
        self._ResetCurrentLen()
        uicore.registry.SetFocus(self)
        self._activeParams.fontsize = newSize
        self.ApplySelection(5, newSize)
        self.UpdateCharacterCounter()
        self.OnChange()

    def ChangeFontColor(self, newColor):
        self._ResetCurrentLen()
        uicore.registry.SetFocus(self)
        self._activeParams.color = newColor
        self.ApplySelection(4, newColor)
        self.UpdateCharacterCounter()
        self.OnChange()

    def AddAnchor(self):
        self._ResetCurrentLen()
        uicore.registry.SetFocus(self)
        self.RemoveAnchor()
        self.ApplySelection(6)
        self.OnChange()

    def RemoveAnchor(self):
        self._ResetCurrentLen()
        if self._activeParams.url:
            self._activeParams.url = None
            if self._activeParams.has_key('loc'):
                self._activeParams.pop('loc')
            node = self.GetActiveNode()
            stackCursorIndex = self.globalCursorPos - node.startCursorIndex + node.stackCursorIndex
            glyphString = node.glyphString
            self.ResetToPreviousUrlParams(self._activeParams, glyphString, stackCursorIndex)
            self.OnChange()

    def HasText(self):
        for each in self.sr.paragraphs:
            if each:
                return True

        return False

    def Disable(self):
        Scroll.Disable(self)
        self.opacity = 0.3

    def Enable(self):
        Scroll.Enable(self)
        self.opacity = 1.0


class SE_EditTextlineCore(SE_BaseClassCore, Link):
    __guid__ = 'uicls.SE_EditTextlineCore'
    default_showHilite = False
    sound_hover = None

    def ApplyAttributes(self, attributes):
        SE_BaseClassCore.ApplyAttributes(self, attributes)
        self.selectingtext = 0
        self.advanceByIndex = []
        self._currentWidth = 0
        self.sr.textcursor = None
        self.sr.cursortimer = None
        self.sr.textselection = None
        trinity.device.RegisterResource(self)
        uicore.textObjects.add(self)

    def OnChar(self, *args):
        pass

    @telemetry.ZONE_METHOD
    def Load(self, node):
        self.RenderLine()
        if node.idx == 0:
            xtraHeight = TEXTSIDEMARGIN
        else:
            xtraHeight = TEXTLINEMARGIN
        if self.height != self.ReverseScaleDpi(node._baseHeight) + xtraHeight:
            node.height = None
            node.scroll.UpdatePosition()
        self.UpdateSelectionHilite()
        self.UpdateCursor()

    def GetSprite(self):
        if self.sr.sprite is None:
            self.sr.sprite = Sprite(parent=self, state=uiconst.UI_PICKCHILDREN, spriteEffect=trinity.TR2_SFX_FONT, idx=0)
        return self.sr.sprite

    def OnCreate(self, dev):
        if self.sr.sprite:
            self.sr.sprite.texture = None
        if self.sr and self.sr.node:
            self.Load(self.sr.node)

    @telemetry.ZONE_METHOD
    def RenderLine(self, createLinks = True):
        if createLinks and self.sr.links:
            self.sr.links.Flush()
        node = self.sr.node
        if node.idx == 0:
            xtraHeight = TEXTSIDEMARGIN
        else:
            xtraHeight = TEXTLINEMARGIN
        self.advanceByIndex = []
        self._currentWidth = 0
        if node._startIndex is None or not node.glyphString or node._width == 0 or node._baseHeight == 0:
            if self.sr.sprite:
                self.sr.sprite.state = uiconst.UI_HIDDEN
            return
        sprite, surf = self.GetSurface(node._width, node._baseHeight)
        if not surf:
            return
        sprite.left = TEXTSIDEMARGIN
        sprite.top = xtraHeight
        k = surf.LockBuffer(None, False)
        try:
            buf = SE_TextlineCore.TexResBuf(k)
            trinity.fontMan.ClearBuffer(buf.data, buf.width, buf.height, buf.pitch)
            self.DrawLine(node.glyphString, buf, 0, node._baseHeight - node._baseLine, startIdx=node._startIndex, endIdx=node._endIndex, createLinks=createLinks)
        finally:
            surf.UnlockBuffer()

        sprite.state = uiconst.UI_DISABLED

    def GetUrlText(self, glyphString, startIdx, url):
        retText = ''
        for t in reversed(glyphString[:startIdx]):
            advance, align, color, sbit, char, asc, des, params = t
            if params.url == url:
                retText = char + retText
            else:
                break

        for t in glyphString[startIdx:]:
            advance, align, color, sbit, char, asc, des, params = t
            if params.url != url:
                return retText
            retText += char

        return retText

    @telemetry.ZONE_METHOD
    def DrawLine(self, glyphString, buf, bx0, by0, startIdx, endIdx, createLinks = True):
        sprite = self.GetSprite()
        x = 0
        self.advanceByIndex.append(x)
        openLink = None
        lastParams = None
        i = 0
        for t in glyphString[startIdx:endIdx]:
            advance, align, color, sbit, char, asc, des, params = t
            if lastParams and lastParams.url != params.url:
                openLink = None
            currentIdx = startIdx + i
            if params.url:
                if createLinks and (not lastParams or lastParams.url != params.url):
                    openLink = self.CreateLink(params.url)
                    openLink.left = uicore.ReverseScaleDpi(x) + sprite.left
                    openLink.height = self.height
                    openLink.top = sprite.top
                    openLink.linkText = self.GetUrlText(glyphString, currentIdx, params.url)
                    openLink.startIdx = currentIdx
                if self.sr.node.hiliteLink == params.url:
                    hiliteRange = self.sr.node.hiliteRange
                    if hiliteRange and not hiliteRange[0] <= currentIdx <= hiliteRange[1]:
                        linkState = uiconst.LINK_IDLE
                    else:
                        linkState = uiconst.LINK_HOVER
                else:
                    linkState = uiconst.LINK_IDLE
                params = params.Copy()
                Link().FormatLinkParams(params, linkState, linkStyle=self.sr.node.scroll.linkStyle)
            color = params.color or -1
            if type(color) != types.IntType:
                tricol = trinity.TriColor(*color)
                color = tricol.AsInt()
            if params.underline:
                extraSpace = advance - sbit.xadvance
                sbit.ToBufferWithUnderline(buf.data, buf.width, buf.height, buf.pitch, x + bx0, by0, color, extraSpace)
            else:
                sbit.ToBuffer(buf.data, buf.width, buf.height, buf.pitch, x + bx0, by0, color)
            if openLink:
                openLink.width = uicore.ReverseScaleDpi(x + advance) - openLink.left + sprite.left
                openLink.endIdx = currentIdx
            lastParams = params
            x += advance
            self.advanceByIndex.append(self.ReverseScaleDpi(x))
            i += 1

        self._currentWidth = self.ReverseScaleDpi(x)

    @telemetry.ZONE_METHOD
    def GetSurface(self, width, height):
        sprite = self.GetSprite()
        if sprite.texture and sprite.texture.atlasTexture:
            textureSize = (sprite.texture.atlasTexture.width, sprite.texture.atlasTexture.height)
        else:
            textureSize = (0, 0)
        sprite.useSizeFromTexture = True
        surf = None
        try:
            if textureSize != (width, height):
                texturePrimary = trinity.Tr2Sprite2dTexture()
                texturePrimary.atlasTexture = uicore.uilib.CreateTexture(width, height)
                sprite.texture = texturePrimary
                surf = texturePrimary.atlasTexture
            else:
                surf = sprite.texture.atlasTexture
            return (sprite, surf)
        except Exception as e:
            log.LogWarn('Failed to create surface', e)
            log.LogException()
            return (sprite, None)

    def CreateLink(self, url):
        if not self.sr.links:
            self.sr.links = Container(name='links', parent=self)
        link = Link(parent=self.sr.links, align=uiconst.RELATIVE, state=uiconst.UI_NORMAL)
        link.OnDblClick = self.OnDblClick
        link.OnMouseEnter = (self.LinkEnter, link)
        link.OnMouseExit = (self.LinkExit, link)
        link.cursor = uiconst.UICORSOR_FINGER
        link.url = url
        link.name = 'textlink'
        link.linkText = ''
        link.URLHandler = self.sr.node.Get('URLHandler', None)
        link.GetHint = lambda *args: link.GetStandardLinkHint(url)
        return link

    def LinkDown(self, link, *args):
        link.OnMouseDown.im_func()
        self.HiliteLink(link)

    def LinkUp(self, link, *args):
        if uicore.uilib.mouseOver is link:
            link.OnMouseUp.im_func()
            self.LinkEnter(link)

    def LinkEnter(self, link, *args):
        browser = GetBrowser(self)
        if browser and browser.sr.window and hasattr(browser.sr.window, 'ShowHint'):
            browser.sr.window.ShowHint(link.hint or link.url)
        PlaySound(uiconst.SOUND_BUTTON_HOVER)
        self.HiliteLink(link)

    def LinkExit(self, link, *args):
        browser = GetBrowser(self)
        if browser and browser.sr.window and hasattr(browser.sr.window, 'ShowHint'):
            browser.sr.window.ShowHint('')
        self.HiliteLink(link, False)

    def HiliteLink(self, link, doHilite = True):
        linkUrl = None
        if link and doHilite:
            linkUrl = link.url
        for entry in self.sr.node.scroll.sr.nodes:
            entry.hiliteLink = linkUrl
            if not entry.panel:
                continue
            linksCont = entry.panel.sr.Get('links', None)
            if linksCont and linksCont == getattr(link, 'parent', None):
                startIdx = getattr(link, 'startIdx', None)
                endIdx = getattr(link, 'endIdx', None)
                if startIdx is not None and endIdx is not None:
                    entry.hiliteRange = (startIdx, endIdx)
                else:
                    entry.hiliteRange = None
                entry.panel.RenderLine(createLinks=False)

    def SelectionHandlerDelegate(self, funcName, args):
        handler = self.sr.node.Get('SelectionHandler', None)
        if handler:
            func = getattr(handler, funcName, None)
            if func:
                return apply(func, args)

    def GetMenu(self):
        self.sr.node.scroll.ShowHint('')
        return self.SelectionHandlerDelegate('GetMenuDelegate', (self.sr.node,))

    def OnMouseDown(self, button, *args):
        if button == uiconst.MOUSELEFT:
            self.SelectionHandlerDelegate('OnMouseDownDelegate', (self.sr.node,))
        elif button == uiconst.MOUSERIGHT and not self.sr.node.scroll.HasSelection():
            self.SelectionHandlerDelegate('OnMouseDownDelegate', (self.sr.node,))

    def OnMouseUp(self, button, *args):
        if button == uiconst.MOUSELEFT:
            self.SelectionHandlerDelegate('OnMouseUpDelegate', (self.sr.node,))

    def OnDropData(self, dragObj, nodes):
        self.SelectionHandlerDelegate('OnDropDataDelegate', (self.sr.node, nodes))

    def OnDragMove(self, nodes, *args):
        self.SelectionHandlerDelegate('OnDragMoveDelegate', (self.sr.node, nodes))

    def OnDragEnter(self, dragObj, nodes):
        self.SelectionHandlerDelegate('OnDragExitDelegate', (self.sr.node, nodes))

    def OnDragExit(self, dragObj, nodes):
        self.SelectionHandlerDelegate('OnDragExitDelegate', (self.sr.node, nodes))

    def OnClick(self, *args):
        pass

    def OnDblClick(self, *args):
        self.SelectionHandlerDelegate('SelectWordUnderCursor', ())

    def OnTripleClick(self, *args):
        self.SelectionHandlerDelegate('SelectLineUnderCursor', ())

    def GetScrollAbove(self):
        item = self.parent
        while item:
            if isinstance(item, Scroll):
                return item
            item = item.parent

    @telemetry.ZONE_METHOD
    def UpdateSelectionHilite(self):
        if not self.sr.node:
            return
        scrollAbove = self.GetScrollAbove()
        f = uicore.registry.GetFocus()
        if not scrollAbove or scrollAbove is not f or not trinity.app.IsActive():
            selectionAlpha = 0.125
        else:
            selectionAlpha = 0.25
        if self.sr.node.selectionStartIndex is not None:
            if self.sr.textselection is None:
                self.sr.textselection = Fill(parent=self, align=uiconst.TOPLEFT, state=uiconst.UI_HIDDEN)
            self.sr.textselection.SetAlpha(selectionAlpha)
            if self.sr.node.startCursorIndex <= self.sr.node.selectionStartIndex <= self.sr.node.endCursorIndex:
                left = self.GetWidthToGlobalIndex(self.sr.node.selectionStartIndex)
            else:
                left = 0
            if self.sr.node.startCursorIndex <= self.sr.node.selectionEndIndex <= self.sr.node.endCursorIndex:
                width = self.GetWidthToGlobalIndex(self.sr.node.selectionEndIndex)
            elif len(self.sr.node.glyphString):
                width = getattr(self, '_currentWidth', 0) or self.GetSprite().width
            else:
                width = 0
            self.sr.textselection.left = left + TEXTSIDEMARGIN
            self.sr.textselection.width = max(2, width - left)
            self.sr.textselection.top = TEXTLINEMARGIN
            self.sr.textselection.height = self.height
            self.sr.textselection.state = uiconst.UI_DISABLED
        elif self.sr.textselection:
            self.sr.textselection.state = uiconst.UI_HIDDEN

    def GetInternalCursorPos(self):
        if not self.sr.sprite:
            return 0
        l, t, w, h = self.sr.sprite.GetAbsolute()
        toCursorPos = uicore.uilib.x - l
        idx = 0
        w = 0
        for charData in self.sr.node.glyphString[self.sr.node.stackCursorIndex:self.sr.node.stackCursorIndex + self.sr.node.letterCountInLine]:
            adv = charData[0]
            if uicore.ReverseScaleDpi(w + adv) >= toCursorPos:
                break
            w += adv
            idx += 1

        return idx

    @telemetry.ZONE_METHOD
    def UpdateCursor(self):
        if self.sr.node.globalCursorPos is not None:
            self.GetSprite()
            if self.sr.textcursor is None:
                self.sr.textcursor = Caret(name='caret', parent=self, align=uiconst.TOPLEFT, state=uiconst.UI_HIDDEN)
            left = self.GetWidthToGlobalIndex(self.sr.node.globalCursorPos)
            if self.sr.node.idx == 0:
                margin = TEXTSIDEMARGIN
            else:
                margin = TEXTLINEMARGIN
            self.sr.textcursor.top = margin
            self.sr.textcursor.left = left + TEXTSIDEMARGIN
            self.sr.textcursor.height = self.height - margin
            if self.sr.cursortimer is None:
                self.CursorBlink()
        elif self.sr.textcursor:
            self.sr.cursortimer = None
            self.sr.textcursor.state = uiconst.UI_HIDDEN

    def GetWidthToGlobalIndex(self, globalCursorPos):
        localIndex = globalCursorPos - self.sr.node.startCursorIndex
        if len(self.advanceByIndex) > localIndex:
            return self.advanceByIndex[localIndex]
        return 0

    def GetCursorOffset(self):
        if self.sr.textcursor:
            return self.sr.textcursor.left

    def CursorBlink(self):
        f = uicore.registry.GetFocus()
        if f is uicore.desktop or not trinity.app.IsActive():
            if self.sr.textcursor:
                self.sr.textcursor.state = uiconst.UI_HIDDEN
            self.sr.cursortimer = None
            return
        if f and self.IsUnder(f) and self.sr.node.globalCursorPos is not None and self.sr.textcursor is not None:
            self.sr.textcursor.state = [uiconst.UI_HIDDEN, uiconst.UI_DISABLED][self.sr.textcursor.state == uiconst.UI_HIDDEN]
            if self.sr.cursortimer is None:
                self.sr.cursortimer = AutoTimer(interval=uiconst.CARET_BLINK_INTERVAL_MS, method=self.CursorBlink)
        else:
            self.sr.cursortimer = None
            self.sr.textcursor.state = uiconst.UI_HIDDEN

    def GetCopyData(self, fromIdx, toIdx):
        return uicore.font.GetNodeCopyData(self.sr.node, fromIdx, toIdx)

    def GetText(self, node):
        if node.rawText:
            return node.rawText
        text = ''.join([ glyphData[4] for glyphData in self.sr.node.glyphString[self.sr.node.stackCursorIndex:self.sr.node.stackCursorIndex + self.sr.node.letterCountInLine] ])
        node.rawText = text
        return text
