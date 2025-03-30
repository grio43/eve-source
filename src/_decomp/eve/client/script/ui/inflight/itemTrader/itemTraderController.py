#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\itemTrader\itemTraderController.py
import math
from collections import defaultdict
import evetypes
import itertoolsext
from carbonui.services.setting import CharSettingNumeric, CharSettingBool
from fsdBuiltData.common.itemTraderRecipesFSDLoader import ItemTraderRecipesFSDLoader
from localization import GetByMessageID, GetByLabel
from signals import Signal

class ItemTraderController(object):

    def __init__(self, item_trader):
        self.on_recipe_clicked = Signal('on_recipe_cliced')
        self.recipes = {}
        self.cargo_input_quantity = {}
        recipeIDs = item_trader.GetRecipes()
        self.LoadRecipes(recipeIDs)
        self._selectedRecipe = None
        self._searchString = ''
        self._tempWndWidth = None
        settingName = 'item_trader_browser_%s' % item_trader.typeID
        self.selectedRecipeSetting = CharSettingNumeric(settingName, 0, min_value=0, max_value=1000000)
        self.affordableSetting = CharSettingBool(settings_key='item_trader_affordable', default_value=False)
        self.affordableSetting.set(False)
        self.UpdateCargoQty()

    @property
    def selectedRecipe(self):
        if not self._selectedRecipe:
            lastSelectedID = self.selectedRecipeSetting.get()
            lastSelectedRecipe = itertoolsext.first_or_default(self.recipes.values(), lambda x: x.recipeID == lastSelectedID and not self.IsFilteredOut(x))
            if lastSelectedRecipe:
                self.selectedRecipe = lastSelectedRecipe
            else:
                defaultSelection = itertoolsext.first_or_default(self.recipes.values(), lambda x: not self.IsFilteredOut(x), self.recipes.values()[0])
                self.selectedRecipe = defaultSelection
        return self._selectedRecipe

    @selectedRecipe.setter
    def selectedRecipe(self, value):
        self._selectedRecipe = value
        self.on_recipe_clicked(value)
        self.selectedRecipeSetting.set(value.recipeID)

    @property
    def searchString(self):
        return self._searchString

    @searchString.setter
    def searchString(self, value):
        self._searchString = value.lower() if value else ''

    @property
    def tempWndWidth(self):
        return self._tempWndWidth

    @tempWndWidth.setter
    def tempWndWidth(self, value):
        self._tempWndWidth = value

    def LoadRecipes(self, recipeIDs):
        for recipeID in recipeIDs:
            self.recipes[recipeID] = Recipe(recipeID)

    def GetRecipes(self):
        return self.recipes

    def GetCargoQtyForTypeID(self, typeID):
        return self.cargo_input_quantity.get(typeID, 0)

    def GetQuantityFromCargo(self):
        cargo_items = self._GetShipCargoItems()
        cargo_input_quantity = defaultdict(int)
        for item in cargo_items:
            cargo_input_quantity[item.typeID] += item.quantity

        return cargo_input_quantity

    def _GetShipCargoItems(self):
        ship_inventory = sm.GetService('invCache').GetInventoryFromId(session.shipid)
        cargo_items = ship_inventory.List(const.flagCargo)
        cargo_items += ship_inventory.List(const.flagGeneralMiningHold)
        cargo_items += ship_inventory.List(const.flagSpecializedIceHold)
        return cargo_items

    def UpdateCargoQty(self):
        self.cargo_input_quantity = self.GetQuantityFromCargo()

    def GetInputMaxMultiplier(self):
        currentRecipe = self.selectedRecipe
        mults = []
        for type_id, qty in currentRecipe.inputItems.iteritems():
            cargo_quantity = self.cargo_input_quantity.get(type_id)
            if not cargo_quantity or cargo_quantity < qty:
                return 0
            amount = int(math.floor(cargo_quantity / qty))
            mults.append(amount)

        return min(mults)

    def MatchesSearchQuery(self, recipe):
        return recipe.MatchesSearchQuery(self.searchString)

    def IsRecipeAffordable(self, recipe):
        return recipe.IsAffordable(self.cargo_input_quantity)

    def IsFilteredOut(self, recipe):
        if self.affordableSetting.get():
            if not self.IsRecipeAffordable(recipe):
                return True
        if not self.MatchesSearchQuery(recipe):
            return True
        return False


class Recipe(object):

    def __init__(self, recipeID):
        data = ItemTraderRecipesFSDLoader.GetByID(recipeID)
        self.recipeID = recipeID
        self.data = data

    @property
    def inputIsk(self):
        return self.data.inputIsk

    @property
    def inputItems(self):
        return self.data.inputItems

    @property
    def outputItems(self):
        return self.data.outputItems

    @property
    def groupID(self):
        return self.data.groupID

    @property
    def displayName(self):
        if self.data.displayNameID:
            return GetByMessageID(self.data.displayNameID)

    def GetRecipeNameAndSortValue(self):
        if self.displayName:
            return (self.displayName, self.displayName.lower())
        inputLabels = []
        for typeID, quantity in self.outputItems.iteritems():
            typeName = evetypes.GetName(typeID)
            if quantity > 1:
                text = GetByLabel('UI/Inventory/QuantityAndName', quantity=quantity, name=typeName)
            else:
                text = typeName
            internalSortValue = (typeName.lower(), quantity)
            inputLabels.append((internalSortValue, text))

        sortedListWithSortValues = sorted(inputLabels, key=lambda data: data[0])
        sortedInputLabels = [ item[1] for item in sortedListWithSortValues ]
        sortValueForEntry = [ item[0] for item in sortedListWithSortValues ]
        return (', '.join(sortedInputLabels), sortValueForEntry)

    def MatchesSearchQuery(self, searchString):
        if not searchString:
            return True
        if self.data.displayNameID:
            recipeName = GetByMessageID(self.data.displayNameID)
            if searchString in recipeName.lower():
                return True
        for collection in (self.outputItems, self.inputItems):
            for typeID, quantity in collection.iteritems():
                typeName = evetypes.GetName(typeID)
                if searchString in typeName.lower():
                    return True

        return False

    def IsAffordable(self, qtyInCargoByTypeID):
        for typeID, quantity in self.inputItems.iteritems():
            if qtyInCargoByTypeID.get(typeID, 0) < quantity:
                return False

        return True
