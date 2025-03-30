#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\spaceObject\harvestableGasCloud.py
import math
import random
import geo2
import trinity
from eve.client.script.environment.spaceObject.cloud import Cloud
from eve.client.script.environment.spaceObject.spaceObject import SpaceObject

class HarvestableGasCloud(Cloud):

    def LoadModel(self, fileName = None, loadedModel = None):
        SpaceObject.LoadModel(self, fileName, loadedModel)

    def Assemble(self):
        Cloud.Assemble(self)
        self.model.rotation = geo2.QuaternionRotationSetYawPitchRoll(random.random() * math.pi * 2.0, random.random() * math.pi, random.random() * math.pi)
