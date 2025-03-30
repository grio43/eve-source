#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsdBuiltData\common\itemTraderRecipesFSDLoader.py
try:
    import itemTraderRecipesLoader
except ImportError:
    itemTraderRecipesLoader = None

from fsdBuiltData.common.base import BuiltDataLoader

class ItemTraderRecipesFSDLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/itemTraderRecipes.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/itemTraderRecipes.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticdata/server/itemTraderRecipes.fsdbinary'
    __loader__ = itemTraderRecipesLoader

    @classmethod
    def GetByID(cls, recipeID):
        return cls.GetData().get(recipeID, None)
