#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\crates\storage.py
from fsdBuiltData.common.base import BuiltDataLoader

class CrateDoesNotExistError(RuntimeError):
    pass


try:
    import cratesLoader
except ImportError:
    cratesLoader = None

class CratesBuiltDataLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticData/crates.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/crates.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/crates.fsdbinary'
    __loader__ = cratesLoader


class CratesStaticData(object):

    def __init__(self):
        self.crates_by_type = None

    @staticmethod
    def _get_data():
        loader = CratesBuiltDataLoader()
        data = loader.GetData()
        return data

    def get_crate_by_type_id(self, type_id):
        crates_by_type = self.get_crates_by_type()
        if type_id not in crates_by_type:
            raise CrateDoesNotExistError('Trying to load a crate that does not exist for type %s.' % type_id)
        return crates_by_type[type_id]

    def get_crates_by_type(self):
        if self.crates_by_type is None:
            crates_by_type = {}
            data = self._get_data()
            for crate in data.values():
                crates_by_type[crate.typeID] = crate

            self.crates_by_type = crates_by_type
        return self.crates_by_type

    def is_crate(self, type_id):
        return type_id in self.get_crates_by_type()

    def get_crate_nameID(self, type_id):
        crates_by_type = self.get_crates_by_type()
        crate = crates_by_type.get(type_id, None)
        if crate:
            return crate.nameID
