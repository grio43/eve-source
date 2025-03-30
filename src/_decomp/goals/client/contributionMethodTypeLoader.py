#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\goals\client\contributionMethodTypeLoader.py
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import contributionMethodsLoader
except ImportError:
    contributionMethodsLoader = None

class ContributionMethodLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticData/contributionMethods.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/contributionMethods.fsdbinary'
    __loader__ = contributionMethodsLoader


def get_data():
    return ContributionMethodLoader.GetData()


def get_contribution_method_authored_data(method_key):
    return get_data().get(method_key, None)
