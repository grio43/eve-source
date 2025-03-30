#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\itemcompression\client\itemCompression.py
from carbonui.uicore import uicore

def CompressItemInSpace(compressibleItem, compressionFacilityBallID):
    result = sm.RemoteSvc('inSpaceCompressionMgr').CompressItemInSpace(compressibleItem.itemID, compressionFacilityBallID)
    if result is not None:
        sourceItemID, sourceTypeID, sourceQuantity, outputItemID, outputTypeID, outputQuantity = result
        uicore.Message('ItemCompression_CompressedItemInSpace', {'sourceTypeID': sourceTypeID,
         'outputTypeID': outputTypeID,
         'outputQuantity': outputQuantity})
        return True
    return False


def CompressItemInStructure(compressibleItem):
    result = sm.RemoteSvc('structureCompressionMgr').CompressItemInStructure(compressibleItem.itemID)
    if result is not None:
        sourceItemID, sourceTypeID, sourceQuantity, outputItemID, outputTypeID, outputQuantity = result
        uicore.Message('ItemCompression_CompressedItemInStructure', {'sourceTypeID': sourceTypeID,
         'outputTypeID': outputTypeID,
         'outputQuantity': outputQuantity})
