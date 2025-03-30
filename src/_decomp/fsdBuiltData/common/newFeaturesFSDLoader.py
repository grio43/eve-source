#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsdBuiltData\common\newFeaturesFSDLoader.py
import newFeaturesLoader
from fsdBuiltData.common.base import BuiltDataLoader

class NewFeaturesFSDLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/newFeatures.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/newFeatures.fsdbinary'
    __loader__ = newFeaturesLoader
