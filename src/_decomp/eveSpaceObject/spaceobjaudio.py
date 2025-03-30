#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveSpaceObject\spaceobjaudio.py
import logging
import audio2
import trinity
from eveaudio.fsdUtils import GetSoundUrlForType
from inventorycommon import const
import shipmode.data as stancedata
L = logging.getLogger(__name__)
__all__ = ['SetupAudioEntity', 'SendEvent', 'PlayAmbientAudio']
BILLBOARDS_PLAYING_AUDIO = {}

def SetupAudioEntity(model, itemID):
    triObserver = trinity.TriObserverLocal()
    result = audio2.AudEmitter('spaceObject_%s_general' % itemID)
    triObserver.observer = result
    model.observers.append(triObserver)
    return result


def SendEvent(audEntity, eventName):
    L.debug('playing audio event %s on emitter %s', eventName, id(audEntity))
    audEntity.SendEvent(unicode(eventName))


def PlayAmbientAudio(audEntity, soundUrl = None):
    if soundUrl is not None:
        SendEvent(audEntity, soundUrl)


def GetSoundUrl(slimItem = None, defaultSoundUrl = None):
    soundUrl = None
    if slimItem:
        soundUrl = GetSoundUrlForType(slimItem)
    if soundUrl is None:
        soundUrl = defaultSoundUrl
    return soundUrl


def GetBoosterSizeStr(groupID):
    boosterMappings = {const.groupCapDrainDrone: 'd',
     const.groupCombatDrone: 'd',
     const.groupElectronicWarfareDrone: 'd',
     const.groupLogisticDrone: 'd',
     const.groupMiningDrone: 'd',
     const.groupProximityDrone: 'd',
     const.groupRepairDrone: 'd',
     const.groupSalvageDrone: 'd',
     const.groupStasisWebifyingDrone: 'd',
     const.groupUnanchoringDrone: 'd',
     const.groupWarpScramblingDrone: 'd',
     const.groupSupportFighter: 'fs',
     const.groupLightFighter: 'fs',
     const.groupHeavyFighter: 'fs',
     const.groupStructureSupportFighter: 'fs',
     const.groupStructureLightFighter: 'fs',
     const.groupStructureHeavyFighter: 'fs',
     const.groupCapsule: 'd',
     const.groupRookieship: 'f',
     const.groupFrigate: 'f',
     const.groupShuttle: 'f',
     const.groupAssaultFrigate: 'f',
     const.groupCovertOps: 'f',
     const.groupInterceptor: 'f',
     const.groupStealthBomber: 'f',
     const.groupElectronicAttackShips: 'f',
     const.groupPrototypeExplorationShip: 'f',
     const.groupExpeditionFrigate: 'f',
     const.groupLogisticsFrigate: 'f',
     const.groupDestroyer: 'c',
     const.groupCruiser: 'c',
     const.groupStrategicCruiser: 'c',
     const.groupAttackBattlecruiser: 'c',
     const.groupBattlecruiser: 'c',
     const.groupInterdictor: 'c',
     const.groupHeavyAssaultCruiser: 'c',
     const.groupLogistics: 'c',
     const.groupForceReconShip: 'c',
     const.groupCombatReconShip: 'c',
     const.groupCommandShip: 'c',
     const.groupHeavyInterdictors: 'c',
     const.groupMiningBarge: 'c',
     const.groupExhumer: 'c',
     const.groupTacticalDestroyer: 'c',
     const.groupCommandDestroyer: 'c',
     const.groupFlagCruiser: 'c',
     const.groupIndustrial: 'bs',
     const.groupIndustrialCommandShip: 'bs',
     const.groupTransportShip: 'bs',
     const.groupBlockadeRunner: 'bs',
     const.groupBattleship: 'bs',
     const.groupEliteBattleship: 'bs',
     const.groupMarauders: 'bs',
     const.groupBlackOps: 'bs',
     const.groupFreighter: 'dr',
     const.groupJumpFreighter: 'dr',
     const.groupDreadnought: 'dr',
     const.groupLancerDreadnought: 'dr',
     const.groupCarrier: 'dr',
     const.groupSupercarrier: 'dr',
     const.groupCapitalIndustrialShip: 'dr',
     const.groupForceAux: 'dr',
     const.groupTitan: 't'}
    return boosterMappings.get(groupID, 'f')


def GetSharedAudioEmitter(itemID, eventName):
    return sm.GetService('audio').GetOrCreateAudioEmitterForItem(itemID, emitterName='spaceObject_{}_{}'.format(itemID, eventName))


def SetupSharedEmitterForAudioEvent(itemID, model, eventName):
    triObserver = trinity.TriObserverLocal()
    emitter = GetSharedAudioEmitter(itemID, eventName)
    triObserver.observer = emitter
    model.observers.append(triObserver)
    if emitter:
        emitter.SendEvent(eventName)


def bindAudioParameterToAttribute(sourceObject, attributeName, bindingsList):
    audparam = audio2.AudParameter()
    audparam.name = u'ship_invulnerability_link_strength'
    binding = trinity.TriValueBinding()
    binding.name = 'AudParameterBinding'
    binding.sourceObject = sourceObject
    binding.sourceAttribute = attributeName
    binding.destinationObject = audparam
    binding.destinationAttribute = 'value'
    bindingsList.append(binding)
    return audparam


def SetBillboardAudio(billboard_model, enabled = True):
    try:
        for attachment in billboard_model.attachments.Find('trinity.EvePlaneSet'):
            resource = attachment.effect.resources.FindByName('ImageMap')
            if resource.resourcePath == 'dynamic:/inspacevideos' and enabled:
                resource.resourcePath = 'dynamic:/inspacevideowithsounds'
            elif resource.resourcePath == 'dynamic:/inspacevideowithsounds' and not enabled:
                resource.resourcePath = 'dynamic:/inspacevideos'

    except AttributeError:
        L.warning('Audio for the given billboard was not able to be activated due to an unexpected error. Check that the model given is actually for a billboard.')
        return


def PlayBillboardAudio(emitter, entityID):
    for channel in [0,
     1,
     2,
     3]:
        if channel in BILLBOARDS_PLAYING_AUDIO.values():
            continue
        eventName = 'Play_billboard_stream_{}'.format(channel)
        emitter.SendEvent(eventName)
        BILLBOARDS_PLAYING_AUDIO[entityID] = channel
        break


def StopBillboardAudio(entityID):
    try:
        del BILLBOARDS_PLAYING_AUDIO[entityID]
    except KeyError:
        pass
