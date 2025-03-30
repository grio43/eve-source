#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\reprocessing\ui\tileplacer.py
from collections import OrderedDict
from carbonui import uiconst

class TilePlacer(object):

    def __init__(self, container):
        self.mainContainer = container
        self.items = OrderedDict()

    def AddItem(self, ctrlID, item):
        self.items[ctrlID] = item
        item.align = uiconst.NOALIGN
        item.SetParent(self.mainContainer)

    def GetItems(self):
        return self.items.values()

    def GetItem(self, ctrlID):
        return self.items[ctrlID]

    def Clear(self):
        self.items.clear()
        self.mainContainer.Flush()

    def RemoveItem(self, ctrlID):
        self.items.pop(ctrlID).Close()
