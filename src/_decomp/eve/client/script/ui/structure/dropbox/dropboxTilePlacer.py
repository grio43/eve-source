#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\dropbox\dropboxTilePlacer.py
from carbonui import uiconst
from reprocessing.ui.tileplacer import TilePlacer

class DropBoxTilePlacer(TilePlacer):

    def __init__(self, container):
        super(DropBoxTilePlacer, self).__init__(container)

    def AddItem(self, ctrlID, item):
        if ctrlID in self.items:
            return
        return super(DropBoxTilePlacer, self).AddItem(ctrlID, item)

    def RemoveItem(self, itemID):
        if itemID not in self.items:
            return
        return super(DropBoxTilePlacer, self).RemoveItem(itemID)

    def ReplaceItem(self, itemID, newItem):
        oldItem = self.GetItem(itemID)
        newItem.align = uiconst.NOALIGN
        newItem.SetParent(oldItem.parent)
        self.items[itemID] = newItem
        oldItem.Close()
