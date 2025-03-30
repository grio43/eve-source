#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\langutils\client\utils.py
from langutils.client.errors import LanguageNotSupported
from langutils.logic import any_to_comfy_language, get_client_language, is_equal_to_client_language
from logging import getLogger
logger = getLogger(__name__)

def set_language(language_id):
    try:
        _validate_language(language_id)
        sm.GetService('gameui').SetLanguage(language_id, doReload=True)
    except Exception as exc:
        logger.exception('Failed to set client language to {language_id}: {exc}'.format(language_id=language_id, exc=exc))


def get_language():
    language = get_client_language()
    return language.code


def is_in_language(language_id):
    try:
        _validate_language(language_id)
        return is_equal_to_client_language(language_id)
    except Exception as exc:
        logger.exception('Failed to check if client is in language {language_id}: {exc}'.format(language_id=language_id, exc=exc))


def get_language_name_from_code(language_id):
    try:
        _validate_language(language_id)
        language = any_to_comfy_language(language_id)
        return language.name
    except Exception as exc:
        logger.exception('Failed to get language name from code {language_id}: {exc}'.format(language_id=language_id, exc=exc))


def _validate_language(language_id):
    from langutils.langconst import VALID_CLIENT_LANGUAGE_CODES
    if not language_id or language_id not in VALID_CLIENT_LANGUAGE_CODES:
        raise LanguageNotSupported('Language code provided ({language_id}) does not match any of the supported client languages ({valid})'.format(language_id=language_id, valid=VALID_CLIENT_LANGUAGE_CODES))
