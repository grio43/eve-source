#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\langutils\langconst.py
from langutils import comfylang
import logging
log = logging.getLogger(__name__)
_IN_CHINA = False
try:
    from eveprefs import boot
    _IN_CHINA = boot and boot.region == 'optic'
except Exception as ex:
    log.warning(u'exception while trying to set up langutils.langconst for china -> %r', ex)

LANG_DE = comfylang.ComfyLanguage(u'German', u'Deutsch', 'de', code3='deu', code3b='ger', sub='DE', sub_name=u'Germany', win_id=1031, db_num=1050)
LANG_EN = comfylang.ComfyLanguage(u'English', u'English', 'en', code3='eng', sub='US', sub_name=u'United States', win_id=1033)
LANG_ES = comfylang.ComfyLanguage(u'Spanish', u'Espa\xf1ol', 'es', code3='spa', sub='ES', sub_name=u'Spain (Traditional)', win_id=1034)
LANG_FR = comfylang.ComfyLanguage(u'French', u'Fran\xe7ais', 'fr', code3='fra', code3b='fre', sub='FR', sub_name=u'France', win_id=1036)
LANG_IT = comfylang.ComfyLanguage(u'Italian', u'Italiano', 'it', code3='ita', sub='IT', sub_name=u'Italy', win_id=1040)
LANG_JA = comfylang.ComfyLanguage(u'Japanese', u'\u65e5\u672c\u8a9e', 'ja', code3='jpn', sub='JP', sub_name=u'Japan', win_id=1041)
LANG_KO = comfylang.ComfyLanguage(u'Korean', u'\ud55c\uad6d\uc5b4', 'ko', code3='kor', sub='KR', sub_name=u'Korea', win_id=1042)
LANG_PT = comfylang.ComfyLanguage(u'Portuguese', u'Portugu\xeas', 'pt', code3='por', sub='BR', sub_name=u'Brazil', win_id=1046)
LANG_RU = comfylang.ComfyLanguage(u'Russian', u'\u0420\u0443\u0441\u0441\u043a\u0438\u0439', code='ru', code3='rus', sub='RU', sub_name=u'Russia', win_id=1049)
LANG_ZH = comfylang.ComfyLanguage(u'Chinese', u'\u4e2d\u6587', 'zh', code3='zho', code3b='chi', sub='CN', sub_name=u'Simplified', win_sub_id=0, win_id=2052, db_num=1051)
LANGUAGES = {LANG_DE,
 LANG_EN,
 LANG_ES,
 LANG_FR,
 LANG_IT,
 LANG_JA,
 LANG_KO,
 LANG_PT,
 LANG_RU,
 LANG_ZH}
VALID_CLIENT_LANGUAGES = {LANG_ZH} if _IN_CHINA else {LANG_DE,
 LANG_EN,
 LANG_FR,
 LANG_JA,
 LANG_RU,
 LANG_KO,
 LANG_ES,
 LANG_ZH}
VALID_CLIENT_LANGUAGE_CODES = {language.code for language in VALID_CLIENT_LANGUAGES}
SECRET_CLIENT_LANGUAGES = {LANG_EN} if _IN_CHINA else set()
DEFAULT_CLIENT_LANGUAGE = LANG_ZH if _IN_CHINA else LANG_EN
INTRO_MOVIE_FILE_MAP = {LANG_KO: 'res:/UI/Texture/classes/Intro/intro_ko.webm'}
INTRO_MOVIE_FILE_NAME = 'intro_netease.webm' if _IN_CHINA else 'intro.webm'
INTRO_MOVIE_FILE_DEFAULT = 'res:/UI/Texture/classes/Intro/{filename}'.format(filename=INTRO_MOVIE_FILE_NAME)
USE_INTRO_SUBTITLE_MAP = {}
USE_INTRO_SUBTITLE_DEFAULT = True
LEGACY_HELP_CHANNEL_DEFAULT = 'system_263238_263262'
LEGACY_HELP_CHANNEL_MAP = {LANG_EN: LEGACY_HELP_CHANNEL_DEFAULT,
 LANG_DE: 'system_263238_263267',
 LANG_RU: 'system_263238_263301',
 LANG_JA: 'system_263238_263302',
 LANG_FR: 'system_263238_504075',
 LANG_KO: 'system_263238_553782',
 LANG_ES: LEGACY_HELP_CHANNEL_DEFAULT,
 LANG_ZH: LEGACY_HELP_CHANNEL_DEFAULT}
LEGACY_ROOKIE_CHANNEL_DEFAULT = 'system_263238_263259'
LEGACY_ROOKIE_CHANNEL_MAP = {LANG_EN: LEGACY_ROOKIE_CHANNEL_DEFAULT,
 LANG_DE: LEGACY_ROOKIE_CHANNEL_DEFAULT,
 LANG_RU: LEGACY_ROOKIE_CHANNEL_DEFAULT,
 LANG_JA: LEGACY_ROOKIE_CHANNEL_DEFAULT,
 LANG_FR: LEGACY_ROOKIE_CHANNEL_DEFAULT,
 LANG_KO: LEGACY_ROOKIE_CHANNEL_DEFAULT,
 LANG_ZH: LEGACY_ROOKIE_CHANNEL_DEFAULT,
 LANG_ES: LEGACY_ROOKIE_CHANNEL_DEFAULT}
