#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveaudio\helpers.py
import sys
import audio2
from .utils import create_emitter
from .trinity_utils import create_observer
import inventorycommon.const as invC

def CreateReloadBankMessage(failedBanks):
    msg = ''
    if len(failedBanks) == 0:
        msg += 'All SoundBanks were reloaded successfully!'
    else:
        msg += 'Reloading SoundBanks was not successful. The following SoundBanks failed to load: {}'.format(failedBanks)
    return msg


def IsRunningInJessicaStandalone():
    try:
        from carbon.tools.jessica import jessica
        if jessica.IsStandAlone():
            return True
    except ImportError:
        return False


def FindEmitterByName(emitterName, redInstance):
    emitters = redInstance.Find('audio2.AudEmitter')
    for emitter in emitters:
        if emitter.name == emitterName:
            return emitter


def CreateAudioObserver(name):
    return create_observer(name)


def CreateAudioEmitter(name):
    return create_emitter(name)


def CreateShipSizeClassLookUpTable():
    sizeMapping = [['drone', 'drone_traffic'],
     ['capsule',
      'shuttle',
      'frigate',
      'destroyer',
      'fighter',
      'strategiccruiser',
      'structure_small'],
     ['cruiser',
      'battlecruiser',
      'industrial',
      'barge'],
     ['battleship', 'industrialcommandship'],
     ['dreadnought',
      'carrier',
      'titan',
      'freighter',
      'forceauxillary',
      'station']]
    classMapping = []
    sizes = {0: 'XXS',
     1: 'S',
     2: 'M',
     3: 'L',
     4: 'XL'}
    for i in range(0, len(sizeMapping)):
        classMapping = classMapping + [sizes[i]] * len(sizeMapping[i])

    return dict(zip(sum(sizeMapping, []), classMapping))
