#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\controllerGhostFittingExtension.py
import evetypes

class FittingControllerGhostFittingExtension(object):

    def __init__(self):
        self.ghostFittingSvc = sm.GetService('ghostFittingSvc')

    def GetDogmaLocation(self):
        return sm.GetService('clientDogmaIM').GetFittingDogmaLocation()

    def PreviewFitItem(self, item):
        if item:
            return self._PreviewFitItemFromTypeID(item.typeID, item.itemID)
        self.ghostFittingSvc.SendOnFeedbackTextChanged(None)

    def _PreviewFitItemFromTypeID(self, typeID, itemID):
        dogmaItem = self.ghostFittingSvc.TryFitModuleToOneSlot(typeID, preview=True, originalItemID=itemID)
        if dogmaItem:
            dogmaItem.isPreviewItem = True
        return dogmaItem

    def UnFitItem(self, dogmaItem):
        if dogmaItem:
            categoryID = evetypes.GetCategoryID(dogmaItem.typeID)
            if categoryID == const.categoryDrone:
                self.ghostFittingSvc.UnfitDrone(dogmaItem.itemID)
            elif categoryID == const.categoryFighter:
                self.ghostFittingSvc.UnfitOneFighter(dogmaItem.itemID)
            else:
                self.ghostFittingSvc.UnfitModule(dogmaItem.itemID)
