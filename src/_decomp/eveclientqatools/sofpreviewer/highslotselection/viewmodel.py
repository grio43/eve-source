#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveclientqatools\sofpreviewer\highslotselection\viewmodel.py


class HighSlot(object):

    def __init__(self, typeID, graphicID, name):
        self.typeID = typeID
        self.graphicID = graphicID
        self.name = name


class HighSlotSelectionViewModel(object):

    def __init__(self, model, highSlotCount):
        self.availableHighSlots = self.CreateHighSlotSelection(model)
        self.turretLocatorCount = highSlotCount
        self.selectedHighSlotItem = self.availableHighSlots[0]

    @staticmethod
    def CreateHighSlotSelection(model, filter = ''):
        highSlots = []
        highSlotItemsTypes = model.highSlotTypeIDs
        for typeID in highSlotItemsTypes:
            name = model.GetHighSlotItemName(typeID)
            if filter.upper() not in name.upper():
                continue
            graphicID = model.GetGraphicIdFromTypeId(typeID)
            highSlot = HighSlot(typeID, graphicID, name)
            highSlots.append(highSlot)

        highSlots.sort(key=lambda highSlot: highSlot.name)
        return highSlots
