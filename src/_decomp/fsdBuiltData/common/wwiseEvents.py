#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsdBuiltData\common\wwiseEvents.py
import wwiseEventsLoader
from fsdBuiltData.common.base import BuiltDataLoader

class WwiseEvents(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/wwiseEvents.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/wwiseEvents.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticdata/server/wwiseEvents.fsdbinary'
    __loader__ = wwiseEventsLoader

    def __init__(self):
        super(WwiseEvents, self).__init__()
        self.wwiseEventsByEventName = self.GenerateReverseLookup()

    def GenerateReverseLookup(self):
        wwiseEventsByEvent = {}
        wwiseEvents = self.GetData()
        for wwiseID, eventData in wwiseEvents.iteritems():
            eventName = eventData.eventName
            wwiseEventsByEvent[eventName] = {'wwiseID': wwiseID,
             'isLoop': eventData.isLoop,
             'eventID': eventData.eventID,
             'maxRadiusAttenuation': eventData.maxRadiusAttenuation,
             'is2D': eventData.is2D,
             'isVital': eventData.isVital,
             'eventsStoppedBy': list(eventData.eventsStoppedBy),
             'soundbanks': list(eventData.soundbanks)}

        return wwiseEventsByEvent


def GetWwiseEvent(wwiseID):
    return WwiseEvents.GetData().get(wwiseID, None)


def GetWwiseEventName(wwiseID):
    wwiseEvent = WwiseEvents.GetData().get(wwiseID, None)
    if wwiseEvent:
        return wwiseEvent.eventName
    else:
        return ''
