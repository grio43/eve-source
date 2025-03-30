#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\checkpoints\common\fsdloader.py
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import checkPointsLoader
except ImportError:
    checkPointsLoader = None

class CheckpointsLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/checkPoints.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/checkPoints.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/checkPoints.fsdbinary'
    __loader__ = checkPointsLoader

    @classmethod
    def GetByID(cls, checkpointID):
        return cls.GetData().get(checkpointID, None)


class Checkpoint(object):

    @staticmethod
    def from_id(checkpoint_id):
        checkpoint_data = CheckpointsLoader.GetData()[checkpoint_id]
        return Checkpoint(checkpoint_id=checkpoint_id, name=checkpoint_data.name, description=checkpoint_data.description, feature_id=checkpoint_data.featureID)

    @staticmethod
    def iter_all():
        for checkpoint_id in CheckpointsLoader.GetData():
            yield Checkpoint.from_id(checkpoint_id)

    def __init__(self, checkpoint_id, name, description, feature_id):
        self.id = checkpoint_id
        self.name = name
        self.description = description
        self.feature_id = feature_id
