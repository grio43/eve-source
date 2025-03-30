#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\itemcompression\gasDecompression.py
from evetypes import GetPortionSize
from typematerials.data import is_decompressible_gas_type, get_type_materials_by_id

def get_gas_decompression_efficiency(structureEfficiency, characterEfficiency):
    if structureEfficiency < 0.0 or structureEfficiency > 1.0:
        raise ValueError('structureEfficiency out of range')
    if characterEfficiency < 0.0 or characterEfficiency > 1.0:
        raise ValueError('characterEfficiency out of range')
    efficiency = structureEfficiency + characterEfficiency
    efficiency = min(efficiency, 1.0)
    return efficiency


def get_decompression_fractional_output(sourceTypeID, sourceQuantity, efficiency):
    if efficiency < 0.0 or efficiency > 1.0:
        raise ValueError('efficiency out of range')
    if not is_decompressible_gas_type(sourceTypeID):
        raise ValueError('Source item is not decompressible gas')
    portionSize = GetPortionSize(sourceTypeID)
    if portionSize != 1:
        raise RuntimeError('Source item portion size must be exactly 1')
    outputMaterials = get_type_materials_by_id(sourceTypeID)
    if len(outputMaterials) != 1:
        raise RuntimeError('Source item does not have exactly 1 output material')
    if outputMaterials[0].quantity != 1:
        raise RuntimeError('Output material quantity must be exactly 1')
    outputTypeID = outputMaterials[0].materialTypeID
    outputFractionalQuantity = sourceQuantity * efficiency
    return (outputTypeID, outputFractionalQuantity)
