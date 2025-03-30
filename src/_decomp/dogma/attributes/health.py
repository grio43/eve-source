#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dogma\attributes\health.py
from dogma.const import attributeHp, attributeDamage
from dogma.const import attributeArmorHP, attributeArmorDamage
from dogma.const import attributeShieldCharge, attributeShieldCapacity

def GetCurrentArmorRatio(dogmaLM, itemId):
    maxArmorHP = GetMaxArmorAmount(dogmaLM, itemId)
    currentArmorHP = GetCurrentArmorDamage(dogmaLM, itemId)
    currentArmorRatio = (maxArmorHP - currentArmorHP) / maxArmorHP
    return currentArmorRatio


def GetCurrentStructureDamage(dogmaLM, itemId):
    return dogmaLM.GetAttributeValue(itemId, attributeDamage)


def GetMaxStructureAmount(dogmaLM, itemId):
    return dogmaLM.GetAttributeValue(itemId, attributeHp)


def GetCurrentArmorDamage(dogmaLM, itemId):
    return dogmaLM.GetAttributeValue(itemId, attributeArmorDamage)


def GetMaxArmorAmount(dogmaLM, itemId):
    return dogmaLM.GetAttributeValue(itemId, attributeArmorHP)


def GetCurrentShieldAmount(dogmaLM, itemId):
    return dogmaLM.GetAttributeValue(itemId, attributeShieldCharge)


def GetMaxShieldAmount(dogmaLM, itemId):
    return dogmaLM.GetAttributeValue(itemId, attributeShieldCapacity)


def GetCurrentShieldRatio(dogmaLM, itemId):
    return GetCurrentShieldAmount(dogmaLM, itemId) / GetMaxShieldAmount(dogmaLM, itemId)


def SetArmorAmount(dogmaLM, itemId, amount):
    dogmaLM.SetAttributeValue(itemId, attributeArmorDamage, amount)


def SetArmorRatio(dogmaLM, itemId, ratio):
    maxArmorHP = GetMaxArmorAmount(dogmaLM, itemId)
    SetArmorAmount(dogmaLM, itemId, maxArmorHP * (1 - ratio))


def SetShieldAmount(dogmaLM, itemId, amount):
    dogmaLM.SetAttributeValue(itemId, attributeShieldCapacity, amount)


def SetShieldRatio(dogmaLM, itemId, ratio):
    maxShieldHp = GetMaxShieldAmount(dogmaLM, itemId)
    SetShieldAmount(dogmaLM, itemId, maxShieldHp * ratio)


def SetStructureAmount(dogmaLM, itemId, amount):
    dogmaLM.SetAttributeValue(itemId, attributeDamage, amount)


def SetStructureRatio(dogmaLM, itemId, ratio):
    maxStructureHp = GetMaxStructureAmount(dogmaLM, itemId)
    SetStructureAmount(dogmaLM, itemId, maxStructureHp * (1 - ratio))
