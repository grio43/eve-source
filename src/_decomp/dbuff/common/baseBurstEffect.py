#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dbuff\common\baseBurstEffect.py
import dogma.const as dogmaConst

def GetModuleBuffValues(dogmaLM, moduleID):
    buffValues = {}
    for buffIDAttribute, buffValueAttribute in dogmaConst.dbuffAttributeValueMappings.iteritems():
        dbuffCollectionID = int(dogmaLM.GetAttributeValue(moduleID, buffIDAttribute))
        if dbuffCollectionID > 0:
            buffValues[dbuffCollectionID] = dogmaLM.GetAttributeValue(moduleID, buffValueAttribute)

    return buffValues


def GetBuffValuesAndDurationMillis(dogmaLM, itemID):
    effectDurationMillis = dogmaLM.GetAttributeValue(itemID, dogmaConst.attributeBuffDuration)
    buffValues = GetModuleBuffValues(dogmaLM, itemID)
    return (buffValues, effectDurationMillis)


def ApplyBuffToSourceShip(dogmaLM, charID, shipID, buffDuration, buffValues):
    dbuffRegistry = dogmaLM.dbuffRegistry
    dbuffRegistry.ApplyBuffsToItems([shipID], buffDuration, buffValues, charID)


class BurstEffectDecorator(object):

    def __init__(self, arg):
        self.variableDict = arg

    def __call__(self, cls):

        class Wrapped(cls):
            for key, value in self.variableDict.iteritems():
                setattr(cls, key, value)

        return Wrapped


def GetArmorEffectClassVariables():
    return {'__guid__': 'dogmaXP.CommandBurstArmorEffect',
     '__effectIDs__': ['effectModuleBonusWarfareLinkArmor'],
     'sourceVFXEffect': 'effects.WarfareLinkSphereArmor',
     'targetVFXEffect': 'effects.WarfareLinkArmor'}


def GetInfoEffectClassVariables():
    return {'__guid__': 'dogmaXP.CommandBurstInfoEffect',
     '__effectIDs__': ['effectModuleBonusWarfareLinkInfo'],
     'sourceVFXEffect': 'effects.WarfareLinkSphereInformation',
     'targetVFXEffect': 'effects.WarfareLinkInformation'}


def GetMiningEffectClassVariables():
    return {'__guid__': 'dogmaXP.CommandBurstMiningEffect',
     '__effectIDs__': ['effectModuleBonusWarfareLinkMining'],
     'sourceVFXEffect': 'effects.WarfareLinkSphereMining',
     'targetVFXEffect': 'effects.WarfareLinkMining'}


def GetShieldEffectClassVariables():
    return {'__guid__': 'dogmaXP.CommandBurstShieldEffect',
     '__effectIDs__': ['effectModuleBonusWarfareLinkShield'],
     'sourceVFXEffect': 'effects.WarfareLinkSphereShield',
     'targetVFXEffect': 'effects.WarfareLinkShield'}


def GetSkirmishEffectClassVariables():
    return {'__guid__': 'dogmaXP.CommandBurstSkirmishEffect',
     '__effectIDs__': ['effectModuleBonusWarfareLinkSkirmish'],
     'sourceVFXEffect': 'effects.WarfareLinkSphereSkirmish',
     'targetVFXEffect': 'effects.WarfareLinkSkirmish'}
