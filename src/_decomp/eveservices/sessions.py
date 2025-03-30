#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveservices\sessions.py
from carbon.common.script.sys import basesession

def _get_session_for_character(character_id):
    return basesession.FindSessions('charid', [character_id])


def has_character_session(character_id):
    return bool(len(_get_session_for_character(character_id)))


def get_session_for_character(character_id):
    sessions = _get_session_for_character(character_id)
    if len(sessions):
        return sessions[0]
