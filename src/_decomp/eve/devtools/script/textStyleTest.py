#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\textStyleTest.py
import logging
import os
from collections import defaultdict
import blue
import trinity
from carbonui import fontconst, TextColor, uiconst
from carbonui.control.combo import Combo
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.control.singlelineedits.singleLineEditFloat import SingleLineEditFloat
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.text.settings import check_convert_font_size
from carbonui.uicore import uicore
from eve.client.script.ui.control import eveLabel
from carbonui.button.group import ButtonGroup
from carbonui.control.checkbox import Checkbox
from carbonui.control.radioButton import RadioButton
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from eve.client.script.ui.control.eveLabel import EveStyleLabel, Label, EveHeaderLarge
from carbonui.control.window import Window
from carbonui.control.tabGroup import TabGroup
from eve.devtools.script import fontExtractor
from logmodule import LogException
variantLabelByID = ['Regular',
 'Italic',
 'Bold',
 'BoldItalic']
loadFlags = (('FT_LOAD_DEFAULT', 0),
 ('FT_LOAD_NO_SCALE', 1),
 ('FT_LOAD_NO_HINTING', 2),
 ('FT_LOAD_RENDER', 4),
 ('FT_LOAD_NO_BITMAP', 8),
 ('FT_LOAD_VERTICAL_LAYOUT', 16),
 ('FT_LOAD_FORCE_AUTOHINT', 32),
 ('FT_LOAD_CROP_BITMAP', 64),
 ('FT_LOAD_PEDANTIC', 128),
 ('FT_LOAD_IGNORE_GLOBAL_ADVANCE_WIDTH', 512),
 ('FT_LOAD_NO_RECURSE', 1024),
 ('FT_LOAD_IGNORE_TRANSFORM', 2048),
 ('FT_LOAD_MONOCHROME', 4096),
 ('FT_LOAD_LINEAR_DESIGN', 8192),
 ('FT_LOAD_NO_AUTOHINT', 32768))
renderFlags = (('FT_RENDER_MODE_NORMAL', 0),
 ('FT_RENDER_MODE_LIGHT', 65536),
 ('FT_RENDER_MODE_MONO', 131072),
 ('FT_RENDER_MODE_LCD', 262144),
 ('FT_RENDER_MODE_LCD_V', 524288))
samplText = u'Lorem ipsum dolor sit amet, ius in mundi eleifend, errem bonorum no mea. Ea wisi praesent imperdiet sit. His at modo debet imperdiet, cum oratio viderer facilisi ex. Et ornatus electram mel. \nLOREM IPSUM DOLOR SIT AMET, IUS IN MUNDI ELEIFEND, ERREM BONORUM NO MEA. EA WISI PRAESENT IMPERDIET SIT. HIS AT MODO DEBET IMPERDIET, CUM ORATIO VIDERER FACILISI EX. ET ORNATUS ELECTRAM MEL. \n1234567890$%&@'
ANSI = ' '.join([ unichr(i) for i in xrange(33, 126) ])
CYRILLIC = ' '.join([ unichr(i) for i in xrange(1024, 1279) ])
CYRILLIC += ' '.join([ unichr(i) for i in xrange(1280, 1327) ])
CYRILLIC += ' '.join([ unichr(i) for i in xrange(11744, 11775) ])
CYRILLIC += ' '.join([ unichr(i) for i in xrange(42560, 42655) ])
CLIENTFONTS = 'Client Fonts'
WINDOWSFONTS = 'Windows Fonts'
DEFAULT_COLOR = TextColor.NORMAL
DEFAULT_LINESPACING = fontconst.DEFAULT_LINESPACING
extractedFontPath = '../client/res/UI/Fonts/Extracted'
logger = logging.getLogger(__name__)

class TextStyleTest(Window):
    default_windowID = 'TextStyleTest'
    default_caption = 'Text style test'
    default_minSize = (500, 500)

    def ApplyAttributes(self, attributes):
        super(TextStyleTest, self).ApplyAttributes(attributes)
        try:
            fontExtractor.extracFonts(extractedFontPath)
        except Exception as e:
            logger.exception('Failed to load Adobe CC fonts: %s', e)

        self.styleCombosByID = defaultdict(dict)
        fontsParent = Container(parent=self.sr.main, align=uiconst.TOLEFT, width=180, padTop=4, padLeft=5)
        flagsParent = Container(parent=self.sr.main, align=uiconst.TORIGHT, width=180, padTop=4, padLeft=5)
        self.ConstructFontsPage(fontsParent)
        self.ConstructFlagsPage(flagsParent)
        self.tabGroup = TabGroup(parent=self.sr.main, settingsID='textStyleTestTabGroup')
        self.mainCont = ScrollContainer(name='mainCont', parent=self.sr.main, padding=10)
        self.labelClassesParent = ContainerAutoSize(name='labelClassesParent', parent=self.mainCont, align=uiconst.TOTOP)
        self.ConstructLabelClassesSamples()
        customParent = self.ConstructCustomSamplesCont()
        self.tabGroup.AddTab('Label Classes', self.labelClassesParent, tabID='LabelClasses')
        self.tabGroup.AddTab('Custom Text', customParent, tabID='CustomText')
        self.tabGroup.AutoSelect()
        btnGroup = ButtonGroup(parent=self.sr.main, idx=0)
        btnGroup.AddButton('Apply Style', self.ApplyStyleAndUpdate)
        btnGroup.AddButton('Reset Style', self.ResetStyle)
        self.UpdateSampleText()

    def ResetStyle(self, *args):
        fontconst.FONT_FAMILY_OVERRIDE = None
        TextColor.NORMAL = DEFAULT_COLOR
        fontconst.DEFAULT_LINESPACING = DEFAULT_LINESPACING
        self._ReloadUI()

    def _ReloadUI(self):
        import codereload
        codereload.xreload(eveLabel)
        sm.ScatterEvent('OnUIRefresh')

    def ApplyStyleAndUpdate(self, *args):
        self.ApplyFontStyle()
        self._ReloadUI()

    def ApplyFontStyle(self):
        override = defaultdict(list)
        for styleID, family in self.styleCombosByID.iteritems():
            for variantID, combo in family.iteritems():
                override[styleID].append(combo.GetValue())

        fontconst.FONT_FAMILY_OVERRIDE = dict(override)

    def ConstructLabelClassesSamples(self):
        self.labelClassesParent.Flush()
        classes = EveStyleLabel.__subclasses__()
        classes.append(Label)
        classes = sorted(classes, key=lambda x: (check_convert_font_size(x.default_fontsize), x.__name__))
        for cls in classes:
            Label(parent=self.labelClassesParent, align=uiconst.TOTOP, text='%s: Style: %s, FontSize: %s' % (cls.__name__, cls.default_fontStyle or 'STYLE_DEFAULT', check_convert_font_size(cls.default_fontsize)), opacity=0.5, padBottom=4)
            cls(parent=self.labelClassesParent, align=uiconst.TOTOP, text='This is some text', padBottom=14)

    def ConstructFlagsPage(self, flagsParent):
        current = trinity.fontMan.loadFlag
        self.loadFlagCheckBoxes = []
        for flagName, flagValue in loadFlags:
            active = current & flagValue == flagValue
            cb = Checkbox(parent=flagsParent, align=uiconst.TOTOP, text=flagName.replace('FT_LOAD_', ''), callback=self.OnLoadFlagChange, checked=active)
            cb.flagName = flagName
            cb.flagValue = flagValue
            self.loadFlagCheckBoxes.append(cb)

        Label(parent=flagsParent, text='Render flags', align=uiconst.TOTOP, padTop=10)
        self.renderFlagCheckBoxes = []
        for flagName, flagValue in renderFlags:
            active = current & flagValue == flagValue
            cb = RadioButton(parent=flagsParent, align=uiconst.TOTOP, text=flagName.replace('FT_RENDER_MODE_', ''), groupname='renderFlag', callback=self.OnRenderFlagChange, retval=flagValue, checked=active)
            cb.flagName = flagName
            cb.flagValue = flagValue
            self.renderFlagCheckBoxes.append(cb)

    def ConstructFontsPage(self, fontsParent):
        self._ConstructStyleCombos(fontsParent)
        self.ConstructColorInputs(fontsParent)
        self.fontSizeEditSmall = SingleLineEditInteger(parent=fontsParent, name='EVE_SMALL_FONTSIZE', align=uiconst.TOTOP, padTop=30, label='EVE_SMALL_FONTSIZE', setvalue=check_convert_font_size(fontconst.EVE_SMALL_FONTSIZE), OnChange=self.OnFontSizeEdit)
        self.fontSizeEditMedium = SingleLineEditInteger(parent=fontsParent, name='EVE_MEDIUM_FONTSIZE', align=uiconst.TOTOP, padTop=15, label='EVE_MEDIUM_FONTSIZE', setvalue=check_convert_font_size(fontconst.EVE_MEDIUM_FONTSIZE), OnChange=self.OnFontSizeEdit)
        self.fontSizeEditLarge = SingleLineEditInteger(parent=fontsParent, name='EVE_LARGE_FONTSIZE', align=uiconst.TOTOP, padTop=15, label='EVE_LARGE_FONTSIZE', setvalue=check_convert_font_size(fontconst.EVE_LARGE_FONTSIZE), OnChange=self.OnFontSizeEdit)
        self.lineSpacingEdit = SingleLineEditFloat(parent=fontsParent, name='LineSpacing', align=uiconst.TOTOP, padTop=30, label='LINE_SPACING', floats=(0.0, 2.0), setvalue=fontconst.DEFAULT_LINESPACING, OnChange=self.OnLineSpacingEdit, decimalPlaces=1)

    def OnLineSpacingEdit(self, *args):
        fontconst.DEFAULT_LINESPACING = self.lineSpacingEdit.GetValue()

    def OnFontSizeEdit(self, *args):
        self.UpdateSampleText()

    def ConstructColorInputs(self, fontsParent):
        EveHeaderLarge(parent=fontsParent, align=uiconst.TOTOP, padTop=16, text='LABEL_COLOR')
        color = TextColor.NORMAL
        colorCont = Container(parent=fontsParent, align=uiconst.TOTOP, height=22, padTop=10)
        widht = 42
        self.colorEditR = SingleLineEditFloat(parent=colorCont, name='attrColorR', align=uiconst.TOLEFT, label='R', floats=(0.0, 1.0), setvalue=color[0], OnChange=self.OnFontColorChanged, width=widht, decimalPlaces=2)
        self.colorEditG = SingleLineEditFloat(parent=colorCont, name='attrColorG', align=uiconst.TOLEFT, label='G', floats=(0.0, 1.0), setvalue=color[1], OnChange=self.OnFontColorChanged, width=widht, decimalPlaces=2)
        self.colorEditB = SingleLineEditFloat(parent=colorCont, name='attrColorB', align=uiconst.TOLEFT, label='B', floats=(0.0, 1.0), setvalue=color[2], OnChange=self.OnFontColorChanged, width=widht, decimalPlaces=2)
        self.colorEditA = SingleLineEditFloat(parent=colorCont, name='attrOpacity', align=uiconst.TOLEFT, label='A', floats=(0.0, 10.0), setvalue=color[3], OnChange=self.OnFontColorChanged, width=widht, decimalPlaces=2)

    def OnFontColorChanged(self, *args):
        TextColor.NORMAL = self.GetInputColor()
        self.UpdateSampleText()

    def GetInputColor(self):
        color = (self.colorEditR.GetValue(),
         self.colorEditG.GetValue(),
         self.colorEditB.GetValue(),
         self.colorEditA.GetValue())
        return color

    def _ConstructStyleCombos(self, fontsParent):
        familyByStyle = uicore.font.GetFontFamilyBasedOnClientLanguageID()
        styleIDs = [fontconst.STYLE_SMALLTEXT, fontconst.STYLE_DEFAULT, fontconst.STYLE_HEADER]
        for styleID in styleIDs:
            EveHeaderLarge(parent=fontsParent, align=uiconst.TOTOP, padTop=16, text=styleID)
            for variantID in xrange(4):
                self._ConstructStyleCombo(familyByStyle, fontsParent, styleID, variantID)

    def _ConstructStyleCombo(self, familyByStyle, fontsParent, styleID, variantID):
        label = variantLabelByID[variantID]
        select = familyByStyle[styleID][variantID] if styleID in familyByStyle else None
        combo = Combo(parent=fontsParent, align=uiconst.TOTOP, padTop=14, label=label, options=self.GetFontPathComboOptions(), select=select, callback=self.OnStyleCombo)
        self.styleCombosByID[styleID][variantID] = combo

    def GetFontPathComboOptions(self):
        clientOptions = [('-Client Fonts:', None)] + self.GetClientFontPaths()
        windowsOptions = [('-Windows Fonts:', None)] + self.GetWindowsFontPaths()
        adobeOptions = [('-Adobe Fonts:', None)] + self.GetAdobeFontPaths()
        return clientOptions + windowsOptions + adobeOptions

    def GetClientFontPaths(self):
        try:
            clientFonts = os.listdir(blue.paths.ResolvePathForWriting(u'res:') + '\\UI\\Fonts')
            clientFonts.sort()
        except WindowsError:
            clientFonts = []
            LogException()

        clientFaces = []
        for fontName in clientFonts:
            if fontName.lower().endswith('.ttf') or fontName.lower().endswith('.otf'):
                clientFaces.append((fontName, 'res:/UI/Fonts/' + fontName))

        return clientFaces

    def GetWindowsFontPaths(self):
        windowsFaces = []
        windowsFonts = os.listdir(blue.sysinfo.GetSharedFontsDirectory())
        windowsFonts.sort()
        for fontName in windowsFonts:
            if fontName.lower().endswith('.ttf') or fontName.lower().endswith('.otf'):
                windowsFaces.append((fontName, os.path.join(blue.sysinfo.GetSharedFontsDirectory(), fontName)))

        return windowsFaces

    def GetAdobeFontPaths(self):
        try:
            clientFonts = os.listdir(extractedFontPath)
            clientFonts.sort()
        except WindowsError:
            clientFonts = []
            LogException()

        clientFaces = []
        for fontName in clientFonts:
            if fontName.lower().endswith('.ttf') or fontName.lower().endswith('.otf'):
                clientFaces.append((fontName, os.path.join(extractedFontPath, fontName)))

        return clientFaces

    def ConstructCustomSamplesCont(self):
        sampleSelectionParent = ContainerAutoSize(name='sampleSectionParent', parent=self.mainCont, align=uiconst.TOTOP)
        optionsCont = Container(name='optionsCont', parent=sampleSelectionParent, align=uiconst.TOTOP, height=20)
        self.ConstructOptionsCont(optionsCont)
        textSelectCont = Container(name='textSelectCont', parent=sampleSelectionParent, align=uiconst.TOTOP, height=100, padTop=10)
        self.ConstructTextSelectCont(textSelectCont)
        self.sampleLabel = Label(name='sampleLabel', parent=sampleSelectionParent, align=uiconst.TOTOP, text=samplText, padTop=10)
        return sampleSelectionParent

    def ConstructTextSelectCont(self, textSelectCont):
        self.sampleCombo = Combo(parent=textSelectCont, align=uiconst.TOPLEFT, width=100, options=[('Lorem...', samplText), ('Ansi charset', ANSI), ('Cyrillic charset', CYRILLIC)], callback=self.OnSampleComboChange)
        Label(parent=textSelectCont, text='-or-', left=self.sampleCombo.left + self.sampleCombo.width + 10)
        self.sampleInput = EditPlainText(parent=textSelectCont, align=uiconst.TOALL, padLeft=140, padRight=10, text='asdf sfdasfasfdasfd safd')
        self.sampleInput.OnChange = self.OnCustomTextChange

    def ConstructOptionsCont(self, optionsCont):
        self.fontSizeEdit = SingleLineEditInteger(minValue=6, maxValue=128, parent=optionsCont, label='Fontsize', align=uiconst.TOLEFT, OnChange=self.OnFontSizeChange, setvalue=unicode(Label.default_fontsize))
        self.letterSpaceEdit = SingleLineEditInteger(minValue=-10, maxValue=10, parent=optionsCont, label='Letterspace', align=uiconst.TOLEFT, OnChange=self.OnLetterSpaceChange, setvalue=unicode(Label.default_letterspace))

    def OnLoadFlagChange(self, checkBox):
        self.UpdateFlags()

    def OnRenderFlagChange(self, checkBox):
        self.UpdateFlags()

    def UpdateFlags(self):
        loadFlag = 0
        for cb in self.loadFlagCheckBoxes:
            if cb.GetValue():
                loadFlag = loadFlag | cb.flagValue

        for cb in self.renderFlagCheckBoxes:
            if cb.GetValue():
                loadFlag = loadFlag | cb.flagValue
                break

        trinity.fontMan.loadFlag = loadFlag
        self.UpdateSampleText()

    def UpdateSampleText(self):
        self.sampleLabel.fontPath = self.styleCombosByID[fontconst.STYLE_DEFAULT][0].GetValue()
        self.sampleLabel.SetRGBA(*self.GetInputColor())
        self.sampleLabel.text = self.sampleLabel.text
        self.sampleLabel.Layout()
        self.ConstructLabelClassesSamples()

    def OnFontSizeChange(self, text):
        try:
            newFontSize = int(text)
            self.sampleLabel.fontsize = newFontSize
        except:
            pass

    def OnLetterSpaceChange(self, text):
        try:
            newLetterSpace = int(text)
            self.sampleLabel.letterspace = newLetterSpace
        except:
            pass

    def OnLineSpacingChange(self, text):
        try:
            newLineSpacing = float(text)
            self.sampleLabel.lineSpacing = newLineSpacing
        except:
            pass

    def LoadFontClass(self, fontClass):
        self.sampleLabel.fontPath = fontClass.default_fontPath
        self.sampleLabel.fontFamily = fontClass.default_fontFamily
        self.sampleLabel.fontStyle = fontClass.default_fontStyle
        self.fontSizeEdit.SetValue(fontClass.default_fontsize)
        self.letterSpaceEdit.SetValue(fontClass.default_letterspace)

    def OnStyleCombo(self, combo, header, value):
        self.ApplyFontStyle()
        self.UpdateSampleText()

    def OnSampleComboChange(self, combo, header, value):
        self.sampleLabel.text = value

    def OnCustomTextChange(self, *args):
        current = self.sampleInput.GetValue()
        self.sampleLabel.text = current
