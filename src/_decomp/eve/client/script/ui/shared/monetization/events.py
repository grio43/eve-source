#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\monetization\events.py
from eveexceptions.exceptionEater import ExceptionEater

def _LogEvent(event, columns, *args):
    with ExceptionEater('eventLog'):
        sm.ProxySvc('eventLog').LogClientEvent('monetization', columns, event, *args)


def LogMultiPilotTrainingBannerImpression():
    _LogEvent('MultiPilotTrainingBannerImpression', ['activeQueues', 'usedQueues'], None, None)


def LogCharacterSheetPilotLicenseImpression():
    _LogEvent('CharacterSheetPilotLicenseImpression', [])


def LogMultiPilotTrainingOpenAurOffer():
    _LogEvent('MultiPilotTrainingOpenAurOffer', [])


def LogMultiPilotTrainingOpenIskOffer():
    _LogEvent('MultiPilotTrainingOpenIskOffer', [])
