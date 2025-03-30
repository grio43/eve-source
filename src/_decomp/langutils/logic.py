#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\langutils\logic.py
import operator
from langutils import comfylang
from langutils import langconst
import logging
log = logging.getLogger(__name__)
_IN_CLIENT = False
try:
    from eveprefs import boot
    _IN_CLIENT = boot and boot.role == 'client'
except Exception as ex:
    log.warning(u'exception while checking if we are running as a client -> %r', ex)

_LANGUAGE_BY_CODE_MAP = {l.code:l for l in langconst.LANGUAGES}
_LANGUAGE_BY_CODE3_MAP = {l.code3:l for l in langconst.LANGUAGES}
_LANGUAGE_BY_CODE3_MAP.update({l.code3b:l for l in langconst.LANGUAGES})
_LANGUAGE_BY_NAME = {l.name.lower():l for l in langconst.LANGUAGES}
_LANGUAGE_BY_NAME.update({l.native.lower():l for l in langconst.LANGUAGES})
_LANGUAGE_BY_INT_MAP = {l.win_id:l for l in langconst.LANGUAGES}
_LANGUAGE_BY_INT_MAP.update({l.win_primary_id:l for l in langconst.LANGUAGES})
_LANGUAGE_BY_INT_MAP.update({l.db_num:l for l in langconst.LANGUAGES})

def any_to_comfy_language(lang_idenifier, default = langconst.DEFAULT_CLIENT_LANGUAGE):
    if not lang_idenifier:
        return default
    if isinstance(lang_idenifier, comfylang.ComfyLanguage):
        return lang_idenifier
    if isinstance(lang_idenifier, (str, unicode)):
        lang_idenifier = lang_idenifier.strip().lower()
        length = len(lang_idenifier)
        found = None
        if length == 2:
            found = _LANGUAGE_BY_CODE_MAP.get(lang_idenifier, None)
            if not found:
                found = _LANGUAGE_BY_NAME.get(lang_idenifier, None)
        else:
            if length >= 5 and lang_idenifier[2] == '-':
                return _LANGUAGE_BY_CODE_MAP.get(lang_idenifier[:2], default)
            if length > 2:
                if length == 3:
                    found = _LANGUAGE_BY_CODE3_MAP.get(lang_idenifier, None)
                if not found:
                    found = _LANGUAGE_BY_NAME.get(lang_idenifier, None)
                if not found and lang_idenifier.startswith('0x'):
                    try:
                        return any_to_comfy_language(int(lang_idenifier, 16), default)
                    except ValueError:
                        pass

        if found:
            return found
        if lang_idenifier.isdigit():
            return any_to_comfy_language(int(lang_idenifier), default)
    else:
        if isinstance(lang_idenifier, (int, long)):
            found = _LANGUAGE_BY_INT_MAP.get(lang_idenifier, None)
            if not found and lang_idenifier > 255:
                found = _LANGUAGE_BY_INT_MAP.get(lang_idenifier & 255, None)
            return found or default
        if isinstance(lang_idenifier, dict):
            hint = lang_idenifier.get('languageID', None) or lang_idenifier.get('numericLanguageID', None)
            if hint and isinstance(hint, (str,
             unicode,
             int,
             long)):
                return any_to_comfy_language(hint, default)
        elif isinstance(lang_idenifier, object):
            hint = getattr(lang_idenifier, 'languageID', None) or getattr(lang_idenifier, 'numericLanguageID', None)
            if hint and isinstance(hint, (str,
             unicode,
             int,
             long)):
                return any_to_comfy_language(hint, default)
    return default


def is_client_valid(lang_identifier):
    cl = any_to_comfy_language(lang_identifier, None)
    if cl:
        return cl in langconst.VALID_CLIENT_LANGUAGES
    return False


def client_valid_or_default(lang_identifier):
    cl = any_to_comfy_language(lang_identifier, None)
    if cl and cl in langconst.VALID_CLIENT_LANGUAGES:
        return cl
    return langconst.DEFAULT_CLIENT_LANGUAGE


def is_equal(lang_identifier_a, lang_identifier_b):
    lang_identifier_a = any_to_comfy_language(lang_identifier_a, None)
    if not lang_identifier_a:
        return False
    return lang_identifier_a == lang_identifier_b


def set_to_sorted_list(lang_set, by_attribute = 'name'):
    return_list = []
    for l in sorted(lang_set, key=operator.attrgetter(by_attribute)):
        if l == langconst.DEFAULT_CLIENT_LANGUAGE:
            return_list.insert(0, l)
        else:
            return_list.append(l)

    return return_list


def get_session_language():
    try:
        import __builtin__
        sess = getattr(__builtin__, 'session', None)
        if sess and sess.userid:
            return any_to_comfy_language(sess.languageID)
        if _IN_CLIENT:
            from eveprefs import prefs
            return any_to_comfy_language(prefs.GetValue('languageID', langconst.DEFAULT_CLIENT_LANGUAGE))
    except Exception as ex:
        log.warning(u'exception while getting client language (are we perhaps not running in exefile): %r', ex)

    return langconst.DEFAULT_CLIENT_LANGUAGE


def get_client_language():
    if not _IN_CLIENT:
        log.warning(u'trying to get client language from a non-client environment... returning default')
        return langconst.DEFAULT_CLIENT_LANGUAGE
    return get_session_language()


def is_equal_to_client_language(lang_identifier):
    return is_equal(lang_identifier, get_client_language())


def get_intro_movie_file(lang_identifier):
    return langconst.INTRO_MOVIE_FILE_MAP.get(any_to_comfy_language(lang_identifier), langconst.INTRO_MOVIE_FILE_DEFAULT)


def get_use_intro_subtitles(lang_identifier):
    return langconst.USE_INTRO_SUBTITLE_MAP.get(any_to_comfy_language(lang_identifier), langconst.USE_INTRO_SUBTITLE_DEFAULT)
