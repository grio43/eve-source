#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\characterdata\careerpath.py
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import careerPathsLoader
except ImportError:
    careerPathsLoader = None

class CareerPathLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticData/careerPaths.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/careerPaths.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/careerPaths.fsdbinary'
    __loader__ = careerPathsLoader


def get_career_paths():
    return CareerPathLoader.GetData()


def get_career_path(career_path_id):
    return get_career_paths().get(career_path_id, None)


def get_career_path_name_id(career_path_id):
    career_path = get_career_path(career_path_id)
    if career_path:
        return career_path.nameID


def get_career_path_internal_name(career_path_id):
    career_path = get_career_path(career_path_id)
    if career_path:
        return career_path.internalName
