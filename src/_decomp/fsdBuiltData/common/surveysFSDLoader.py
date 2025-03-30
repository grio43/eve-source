#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsdBuiltData\common\surveysFSDLoader.py
import surveysLoader
from fsdBuiltData.common.base import BuiltDataLoader

class SurveyFSDLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/surveys.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/surveys.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticdata/server/surveys.fsdbinary'
    __loader__ = surveysLoader
