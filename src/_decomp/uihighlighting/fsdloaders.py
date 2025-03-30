#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uihighlighting\fsdloaders.py
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import uiHighlightsLoader
except ImportError:
    uiHighlightsLoader = None

try:
    import spaceObjectHighlightsLoader
except ImportError:
    spaceObjectHighlightsLoader = None

try:
    import menuHighlightsLoader
except ImportError:
    menuHighlightsLoader = None

class UIHighlightsLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/uiHighlights.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/uiHighlights.fsdbinary'
    __loader__ = uiHighlightsLoader

    @classmethod
    def GetByID(cls, highlightID):
        return cls.GetData().get(highlightID, None)


class SpaceObjectHighlightsLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/spaceObjectHighlights.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/spaceObjectHighlights.fsdbinary'
    __loader__ = spaceObjectHighlightsLoader

    @classmethod
    def GetByID(cls, highlightID):
        return cls.GetData().get(highlightID, None)


class MenuHighlightsLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/menuHighlights.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/menuHighlights.fsdbinary'
    __loader__ = menuHighlightsLoader

    @classmethod
    def GetByID(cls, highlightID):
        return cls.GetData().get(highlightID, None)
