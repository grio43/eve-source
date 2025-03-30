#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\destructionEffect\destructioneffectmanager.py
import math
import random
import geo2

class DestructionEffectManager(object):

    def __init__(self, spaceObject):
        self.spaceObject = spaceObject

    def PlayDissolveEffect(self):
        idx = self.GetLastHitDamageLocator()
        locatorsSets = self.spaceObject.model.locatorSets.FindByName('damage')
        if idx > -1:
            locatorPos = locatorsSets.locators[idx][0]
        else:
            locatorPos = random.choice(locatorsSets.locators)[0]
        self.spaceObject.SetControllerVariable('IsDissolving', 1.0)

    def GetLastHitDamageLocator(self):
        damageLocator = getattr(self.spaceObject.model, 'lastDamageLocatorHit', -1)
        return damageLocator

    def SetClipSphereCenter(self, locatorPos):
        unitLocatorPos = geo2.Vec3Normalize(locatorPos)
        radius = self.spaceObject.model.boundingSphereRadius
        x = unitLocatorPos[0] * radius
        y = unitLocatorPos[1] * radius
        z = unitLocatorPos[2] * radius
        self.spaceObject.model.clipSphereCenter = (x, y, z)
