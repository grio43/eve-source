#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\journey\tracker.py
import uuid
import localstorage
_journey_id = None

def get_journey_id():
    global _journey_id
    return str(_journey_id)


def set_journey_id(journey_id):
    global _journey_id
    _journey_id = journey_id


def reset_journey_id():
    set_journey_id(uuid.uuid4())


def get_journey_id_for_event():
    ls = localstorage.GetLocalStorage()
    if 'journeyID' in ls and ls['journeyID']:
        return uuid.UUID(ls['journeyID'])


def set_current_journey_id(journeyID):
    ls = localstorage.GetLocalStorage()
    ls['journeyID'] = journeyID


def create_and_set_journey_id():
    journeyID = str(uuid.uuid4())
    ls = localstorage.GetLocalStorage()
    ls['journeyID'] = journeyID
    return journeyID


def create_journey_id_link():
    set_current_journey_id(get_journey_id())
    reset_journey_id()
    return get_journey_id()
