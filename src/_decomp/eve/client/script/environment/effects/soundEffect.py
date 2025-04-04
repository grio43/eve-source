#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\effects\soundEffect.py
from eve.client.script.environment.effects.GenericEffect import GenericEffect, STOP_REASON_DEFAULT
from eveSpaceObject.spaceobjaudio import GetBoosterSizeStr

class SoundEffect(GenericEffect):
    __guid__ = 'effects.soundEffect'

    def __init__(self, trigger, *args, **kwargs):
        GenericEffect.__init__(self, trigger, *args, **kwargs)
        self.trigger = trigger

    def Start(self, duration):
        eventType = 'play'
        self.SendEffectEvent(eventType)

    def Stop(self, reason = STOP_REASON_DEFAULT):
        eventType = 'stop'
        self.SendEffectEvent(eventType)

    def GetShipSizeFromSlimItem(self, ship):
        slimItem = ship.typeData['slimItem']
        groupID = slimItem.groupID
        sizeStr = GetBoosterSizeStr(groupID)
        return sizeStr

    def GetEventName(self, eventType, ship):
        effectType = GetEffectTypeFromTrigger(self.trigger)
        sizeStr = self.GetShipSizeFromSlimItem(ship)
        parts = [effectType, sizeStr, eventType]
        soundEvent = '_'.join(parts)
        return soundEvent

    def SendEffectEvent(self, eventType):
        emitter = None
        ship = self.GetEffectShipBall()
        if ship is None or ship.model is None:
            return
        for item in ship.model.observers:
            if item.observer.name.startswith('ship') and item.observer.name.endswith('booster'):
                emitter = item.observer
                break

        if emitter is not None:
            soundEvent = self.GetEventName(eventType, ship)
            emitter.SendEvent(unicode(soundEvent))


def GetEffectTypeFromTrigger(trigger):
    guid = trigger.guid
    effectType = guid.split('.')[-1]
    return effectType.lower()
