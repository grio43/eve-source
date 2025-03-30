#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\spaceObject\nonInteractableObject.py
from eve.client.script.environment.spaceObject.LargeCollidableObject import LargeCollidableObject

class NonInteractableObject(LargeCollidableObject):

    def LoadModel(self, fileName = None, loadedModel = None, notify = True, addToScene = True):
        hasFile = fileName is not None or self.typeData.get('graphicFile', None) is not None
        hasDna = self.GetDNA() is not None
        if hasFile or hasDna or loadedModel is not None:
            super(NonInteractableObject, self).LoadModel(fileName, loadedModel, notify, addToScene)

    def Assemble(self):
        super(NonInteractableObject, self).Assemble()
        if self.model is not None and hasattr(self.model, 'isPickable'):
            self.model.isPickable = False


class ScalableNonInteractableObject(NonInteractableObject):

    def Assemble(self):
        super(ScalableNonInteractableObject, self).Assemble()
        self.SetRadius(self.radius)

    def SetRadius(self, r):
        if self.model is not None and hasattr(self.model, 'scaling'):
            self.model.scaling = (r, r, r)
