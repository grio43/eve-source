#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\spaceObject\wormhole.py
from eve.client.script.environment.spaceObject.spaceObject import SpaceObject

class Wormhole(SpaceObject):

    def __init__(self):
        SpaceObject.__init__(self)
        self.targetNebulaPath = None

    def Assemble(self):
        slimItem = self.typeData.get('slimItem')
        resDict = self.spaceMgr.GetNebulaTextureForType(slimItem.nebulaType)
        self.targetNebulaPath = resDict['envMap1ResPath']
        self.logger.debug('Updating wormhole textures...')
        for param in self.model.externalParameters:
            if param.name == 'LQ_NebulaClass':
                param.destinationObject.resourcePath = resDict['lowQualityNebulaResPath']
            elif param.name == 'LQ_NebulaMix1' or param.name == 'LQ_NebulaMix2':
                param.destinationObject.resourcePath = resDict['lowQualityNebulaMixResPath']
            elif param.name == 'destinationReflectionCube':
                param.destinationObject.resourcePath = resDict['envMap1ResPath']

        self.logger.debug('Wormhole updated with the following textures: %s', resDict)
        self.logger.debug('Wormhole - Assemble : wormholeSize=%s, nebulaType=%s, wormholeAge=%s, maxShipJumpMass=%s', slimItem.wormholeSize, slimItem.nebulaType, slimItem.wormholeAge, slimItem.maxShipJumpMass)

    def Explode(self):
        if self.exploded:
            return 0
        if self.model is None:
            return 0
        self.exploded = True
        self.SetControllerVariablesFromSlimItem(self.typeData.get('slimItem'))
        return 12000

    def OnSlimItemUpdated(self, slimItem):
        self.typeData['slimItem'] = slimItem
        self.SetControllerVariablesFromSlimItem(slimItem)
        self.logger.debug('Wormhole updated.')
