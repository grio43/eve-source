#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\dragdrop\dragDropUtil.py
from carbonui.control.dragdrop import dragdata

def GetTypeID(dragData):
    if isinstance(dragData, dragdata.TypeDragData):
        return dragData.typeID
    if hasattr(dragData, 'typeID') and dragData.typeID is not None:
        return dragData.typeID
    if hasattr(dragData, 'item') and dragData.item is not None and hasattr(dragData.item, 'typeID'):
        return dragData.item.typeID
