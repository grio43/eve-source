#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\itemcompression\client\gasDecompression.py
from carbonui.uicore import uicore
from itemcompression.gasDecompression import get_gas_decompression_efficiency

def decompress_gas(compressed_gas_item_id):
    result = sm.RemoteSvc('structureCompressionMgr').DecompressGasInStructure(compressed_gas_item_id)
    if result is not None:
        sourceItemID, sourceTypeID, sourceQuantity, outputItemID, outputTypeID, outputQuantity = result
        if outputItemID is None or outputQuantity == 0:
            pass
        else:
            uicore.Message('ItemCompression_DecompressedGasInStructure', {'sourceTypeID': sourceTypeID,
             'outputTypeID': outputTypeID,
             'outputQuantity': outputQuantity})
    return result


def get_my_decompression_efficiencies():
    structureEfficiency, characterEfficiency = sm.RemoteSvc('structureCompressionMgr').GetMyGasDecompressionEfficiency()
    totalEfficiency = get_gas_decompression_efficiency(structureEfficiency, characterEfficiency)
    return (structureEfficiency, characterEfficiency, totalEfficiency)
