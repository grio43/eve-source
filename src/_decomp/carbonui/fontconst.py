#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\fontconst.py
import os
import sys
import blue
from carbonui import languageConst
from carbonui.text.const import FontSizePreset
EVE_SMALL_FONTSIZE = FontSizePreset.DEPRECATED_SMALL
EVE_MEDIUM_FONTSIZE = FontSizePreset.DEPRECATED_MEDIUM
EVE_LARGE_FONTSIZE = FontSizePreset.DEPRECATED_LARGE
EVE_XLARGE_FONTSIZE = FontSizePreset.DEPRECATED_XLARGE
EVE_DETAIL_FONTSIZE = FontSizePreset.DETAIL
EVE_BODY_FONTSIZE = FontSizePreset.BODY
EVE_HEADER_FONTSIZE = FontSizePreset.HEADER
EVE_HEADLINE_FONTSIZE = FontSizePreset.HEADLINE
EVE_DISPLAY_FONTSIZE = FontSizePreset.DISPLAY
DEFAULT_FONTSIZE = EVE_MEDIUM_FONTSIZE
DEFAULT_LINESPACING = 0.0
DEFAULT_LETTERSPACE = 0
DEFAULT_UPPERCASE = False
STYLE_DEFAULT = 'STYLE_DEFAULT'
STYLE_HEADER = 'STYLE_HEADER'
STYLE_SMALLTEXT = 'STYLE_SMALLTEXT'
EVESANS_BOLD = 'res:/UI/Fonts/EveSansNeue-Bold.otf'
SYSTEMFONTROOT = blue.sysinfo.GetSystemFontsDirectory()
FONT_FAMILY_OVERRIDE = None
fontSizeFactor = 1.0
EVEFONTFAMILY = {STYLE_DEFAULT: ('res:/UI/Fonts/EveSansNeue-Regular.otf',
                 'res:/UI/Fonts/EveSansNeue-Italic.otf',
                 EVESANS_BOLD,
                 'res:/UI/Fonts/EveSansNeue-BoldItalic.otf'),
 STYLE_HEADER: ('res:/UI/Fonts/EveSansNeue-Condensed.otf', 'res:/UI/Fonts/EveSansNeue-CondensedItalic.otf', 'res:/UI/Fonts/EveSansNeue-CondensedBold.otf', 'res:/UI/Fonts/EveSansNeue-CondensedBoldItalic.otf'),
 STYLE_SMALLTEXT: ('res:/UI/Fonts/EveSansNeue-Expanded.otf', 'res:/UI/Fonts/EveSansNeue-ExpandedItalic.otf', 'res:/UI/Fonts/EveSansNeue-ExpandedBold.otf', 'res:/UI/Fonts/EveSansNeue-ExpandedBoldItalic.otf')}
KOREANFONTFAMILY = {STYLE_DEFAULT: ('res:/UI/Fonts/NotoSansCJKkr-Medium.otf', 'res:/UI/Fonts/NotoSansCJKkr-Medium.otf', 'res:/UI/Fonts/NotoSansCJKkr-Medium.otf', 'res:/UI/Fonts/NotoSansCJKkr-Medium.otf')}
MSGOTHIC_PATH = os.path.join(SYSTEMFONTROOT, 'msgothic.ttc')
ARIAL_PATH = os.path.join(SYSTEMFONTROOT, 'arial.ttf')
CONSOLA_PATH = os.path.join(SYSTEMFONTROOT, 'CONSOLA.TTF')
ARIALUNI_PATH = 'res:/ui/fonts/arialuni.ttf'
JAPANESE_FONT = {'darwin': ARIALUNI_PATH,
 'win32': MSGOTHIC_PATH}[sys.platform]
JAPANESEFONTFAMILY = {STYLE_DEFAULT: (JAPANESE_FONT,
                 JAPANESE_FONT,
                 JAPANESE_FONT,
                 JAPANESE_FONT)}
FONTFAMILY_PER_WINDOWS_LANGUAGEID = {languageConst.LANG_ENGLISH: EVEFONTFAMILY,
 languageConst.LANG_KOREAN: KOREANFONTFAMILY,
 languageConst.LANG_JAPANESE: JAPANESEFONTFAMILY}
CHINESE_FONTS = {'win32': ((os.path.join(SYSTEMFONTROOT, 'msyh.ttc'),
            os.path.join(SYSTEMFONTROOT, 'msyh.ttc'),
            os.path.join(SYSTEMFONTROOT, 'msyhbd.ttc'),
            os.path.join(SYSTEMFONTROOT, 'msyhbd.ttc')), (os.path.join(SYSTEMFONTROOT, 'msyh.ttf'),
            os.path.join(SYSTEMFONTROOT, 'msyh.ttf'),
            os.path.join(SYSTEMFONTROOT, 'msyhbd.ttf'),
            os.path.join(SYSTEMFONTROOT, 'msyhbd.ttf')), (os.path.join(SYSTEMFONTROOT, 'simsun.ttc'),
            os.path.join(SYSTEMFONTROOT, 'simsun.ttc'),
            os.path.join(SYSTEMFONTROOT, 'simsun.ttc'),
            os.path.join(SYSTEMFONTROOT, 'simsun.ttc'))),
 'darwin': ((os.path.join(SYSTEMFONTROOT, 'PingFang.ttc'),
             os.path.join(SYSTEMFONTROOT, 'PingFang.ttc'),
             os.path.join(SYSTEMFONTROOT, 'PingFang.ttc'),
             os.path.join(SYSTEMFONTROOT, 'PingFang.ttc')), (os.path.join(SYSTEMFONTROOT, 'Hiragino Sans GB.ttc'),
             os.path.join(SYSTEMFONTROOT, 'Hiragino Sans GB.ttc'),
             os.path.join(SYSTEMFONTROOT, 'Hiragino Sans GB.ttc'),
             os.path.join(SYSTEMFONTROOT, 'Hiragino Sans GB.ttc')))}[sys.platform]
prioritizedFontPaths = ((languageConst.LANG_CHINESE, STYLE_DEFAULT, CHINESE_FONTS),)

def ResolvePriorityList(priorityListPerLanguage):
    for languageID, fontStyle, priorityList in priorityListPerLanguage:
        for each in priorityList:
            if type(each) == tuple:
                for variantPath in each:
                    isThere = os.path.exists(variantPath)
                    if not isThere:
                        break

                if isThere:
                    FONTFAMILY_PER_WINDOWS_LANGUAGEID[languageID] = {fontStyle: each}
                    break
            else:
                isThere = os.path.exists(each)
                if isThere:
                    FONTFAMILY_PER_WINDOWS_LANGUAGEID[languageID] = {fontStyle: each}
                    break


ResolvePriorityList(prioritizedFontPaths)
del ResolvePriorityList
del prioritizedFontPaths
LANGUAGES_USING_EVE_FONT = (languageConst.LANG_ALBANIAN,
 languageConst.LANG_ARMENIAN,
 languageConst.LANG_BASQUE,
 languageConst.LANG_BELARUSIAN,
 languageConst.LANG_BOSNIAN,
 languageConst.LANG_BULGARIAN,
 languageConst.LANG_CATALAN,
 languageConst.LANG_CROATIAN,
 languageConst.LANG_CZECH,
 languageConst.LANG_DANISH,
 languageConst.LANG_DUTCH,
 languageConst.LANG_ENGLISH,
 languageConst.LANG_ESTONIAN,
 languageConst.LANG_FAEROESE,
 languageConst.LANG_FINNISH,
 languageConst.LANG_FRENCH,
 languageConst.LANG_GALICIAN,
 languageConst.LANG_GEORGIAN,
 languageConst.LANG_GERMAN,
 languageConst.LANG_GREEK,
 languageConst.LANG_GREENLANDIC,
 languageConst.LANG_HUNGARIAN,
 languageConst.LANG_ICELANDIC,
 languageConst.LANG_IRISH,
 languageConst.LANG_ITALIAN,
 languageConst.LANG_LATVIAN,
 languageConst.LANG_LITHUANIAN,
 languageConst.LANG_LUXEMBOURGISH,
 languageConst.LANG_MACEDONIAN,
 languageConst.LANG_MALTESE,
 languageConst.LANG_NORWEGIAN,
 languageConst.LANG_POLISH,
 languageConst.LANG_PORTUGUESE,
 languageConst.LANG_ROMANIAN,
 languageConst.LANG_ROMANSH,
 languageConst.LANG_RUSSIAN,
 languageConst.LANG_SAMI,
 languageConst.LANG_SERBIAN,
 languageConst.LANG_SLOVAK,
 languageConst.LANG_SLOVENIAN,
 languageConst.LANG_SPANISH,
 languageConst.LANG_SWEDISH,
 languageConst.LANG_UKRAINIAN)
TRIGLAVIAN = 'res:/UI/Fonts/Triglavian.ttf'
