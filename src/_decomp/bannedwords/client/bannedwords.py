#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\bannedwords\client\bannedwords.py
bannedwords_client = None

def get_bannedwords_client():
    global bannedwords_client
    if bannedwords_client is None:
        bannedwords_client = sm.GetService('bannedwords_client')
    return bannedwords_client


def check_words_allowed(*wordsList, **kwargs):
    get_bannedwords_client().check_words_allowed(*wordsList, **kwargs)


def check_search_words_allowed(*wordsList, **kwargs):
    get_bannedwords_client().check_search_words_allowed(*wordsList, **kwargs)


def check_chat_words_allowed(*wordsList):
    get_bannedwords_client().check_chat_words_allowed(err_message='ChatContentInvalidBannedWords', *wordsList)


def check_chat_character_allowed(characterID):
    get_bannedwords_client().check_chat_character_allowed(characterID)
