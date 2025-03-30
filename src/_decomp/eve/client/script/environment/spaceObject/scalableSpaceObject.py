#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\spaceObject\scalableSpaceObject.py
from destructionEffect import destructionType
from eve.client.script.environment.spaceObject.spaceObject import SpaceObject
from evegraphics.utils import BuildSOFDNAFromGraphicID
from evetypes import GetGraphicID
from fsdBuiltData.client.groupGraphics import GetGraphicIdsFromTypeID
from fsdBuiltData.common.graphicIDs import GetGraphic, GetExplosionBucketID

class ScalableSpaceObject(SpaceObject):

    def _GetGraphicID(self):
        typeID = self.typeData.get('typeID')
        graphics = GetGraphicIdsFromTypeID(typeID)
        if graphics is None or len(graphics) == 0:
            graphicid = GetGraphicID(typeID)
            if graphicid is None:
                raise RuntimeError('Error adding scalable object %d it has no graphicId or groupGraphic information', typeID)
            return graphicid
        return graphics[self.id % len(graphics)]

    def GetDNA(self):
        graphicID = self._GetGraphicID()
        return BuildSOFDNAFromGraphicID(graphicID)

    def Assemble(self):
        if self.model is None:
            self.logger.error('Cannot Assemble ScalableObject, model failed to load')
            return
        self.model.modelScale = self.radius
        graphicInfo = GetGraphic(self._GetGraphicID())
        self.explosionBucketID = GetExplosionBucketID(graphicInfo)
        self.ActivateExplodeOnRemove()

    def ActivateExplodeOnRemove(self):
        if self.explosionBucketID is not None:
            self.destructionEffectId = destructionType.EXPLOSION_OVERRIDE

    def DeactivateExplodeOnRemove(self):
        self.destructionEffectId = destructionType.NONE
