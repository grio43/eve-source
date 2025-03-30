#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsdBuiltData\client\effectSequences.py
import effectSequencesLoader
from fsdBuiltData.common.base import BuiltDataLoader

class EffectSequences(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/effectSequences.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/effectSequences.fsdbinary'
    __loader__ = effectSequencesLoader


def GetSequence(sequenceID):
    return EffectSequences.GetData().get(sequenceID, None)


def GetSequenceAttribute(sequenceID, attributeName, default = None):
    if isinstance(sequenceID, str):
        return GetAttribute(GetSequence(sequenceID), attributeName, None) or default
    return GetAttribute(sequenceID, attributeName, None) or default


def GetAttribute(step, attributeName, default = None):
    return getattr(step, attributeName, None) or default


def GetEffectSequenceDictionary():
    return EffectSequences.GetData()


def GetStops(sequenceID, default = []):
    return GetSequenceAttribute(sequenceID, 'stops', default)


def GetStepStepsToStop(step, default = []):
    return GetAttribute(step, 'stepsToStop', default)


def GetStepGraphicFile(step, default = None):
    return GetAttribute(step, 'graphicFile', default)


def GetStepScaling(step, default = None):
    return GetAttribute(step, 'scaling', default)


def GetStepSource(step, default = None):
    return GetAttribute(step, 'source', default)


def GetStepTarget(step, default = None):
    return GetAttribute(step, 'target', default)


def GetStepFunctions(step, default = []):
    return GetAttribute(step, 'callFunctions', default)


def GetStepFunctionTarget(step, default = None):
    return GetAttribute(step, 'target', default)
