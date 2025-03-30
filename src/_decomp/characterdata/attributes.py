#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\characterdata\attributes.py
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import characterAttributesLoader
except ImportError:
    characterAttributesLoader = None

class CharacterAttributesLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticData/characterAttributes.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/characterAttributes.fsdbinary'
    __loader__ = characterAttributesLoader


def get_character_attributes():
    return CharacterAttributesLoader.GetData()
