#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dynamicitemattributes\loader.py
import dynamicItemAttributesLoader
from fsdBuiltData.common.base import BuiltDataLoader
import evetypes

class DynamicItemAttributes(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/dynamicItemAttributes.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/dynamicItemAttributes.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticdata/server/dynamicItemAttributes.fsdbinary'
    __loader__ = dynamicItemAttributesLoader


def GetData():
    return DynamicItemAttributes.GetData()


def IsMutator(typeID):
    return typeID in GetData()


def GetMutator(mutatorID):
    return GetData()[mutatorID]


def GetApplicableTypes(mutatorID):
    mutator = GetMutator(mutatorID)
    applicableTypes = []
    for mapping in mutator.inputOutputMapping:
        publishedTypes = filter(evetypes.IsPublished, mapping.applicableTypes)
        applicableTypes.extend(publishedTypes)

    return applicableTypes


def GetMutatorAttributes(mutatorID):
    mutator = GetMutator(mutatorID)
    return mutator.attributeIDs


def GetResultType(mutatorID, sourceTypeID):
    mutator = GetMutator(mutatorID)
    for mapping in mutator.inputOutputMapping:
        for applicableType in mapping.applicableTypes:
            if sourceTypeID == applicableType:
                return mapping.resultingType

    raise ValueError('Source typeID {} is not applicable'.format(sourceTypeID))


def GetResultTypes(mutatorID):
    mutator = GetMutator(mutatorID)
    return [ m.resultingType for m in mutator.inputOutputMapping ]


def GetAllMutatorTypes():
    return GetData().keys()


def GetMutatorTypesByResultTypes(resultTypes):
    if not hasattr(resultTypes, '__iter__'):
        resultTypes = [resultTypes]
    mutatorTypeIDs = []
    for mutatorID, mutator in GetData().iteritems():
        for mapping in mutator.inputOutputMapping:
            if mapping.resultingType in resultTypes:
                mutatorTypeIDs.append(mutatorID)

    return mutatorTypeIDs
