#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\itemTrader\offerBrowser.py
from collections import defaultdict
import eveicon
import evetypes
from carbonui import TextColor
from carbonui.button.menu import MenuButtonIcon
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.control.scroll import Scroll
from carbonui.primitives.container import Container
from carbonui.util.sortUtil import SortListOfTuples
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.listgroup import ListGroup
from eve.client.script.ui.inflight.itemTrader.recipeUtil import LoadRecipeTooltipPanel, GetRecipeGroupName, GetRecipeGroupTexturepath
from eve.client.script.ui.quickFilter import QuickFilterEdit
from localization import GetByLabel
from carbonui.uicore import uicore
import blue
import carbonui.const as uiconst

class OfferBrowser(Container):
    default_clipChildren = True

    def ApplyAttributes(self, attributes):
        self.item_trader = attributes.item_trader
        self.itemTraderController = attributes.itemTraderController
        super(OfferBrowser, self).ApplyAttributes(attributes)
        self.searchparent = SearchCont(name='searchparent', parent=self, align=uiconst.TOTOP, top=4, itemTraderController=self.itemTraderController, searchFunc=self.Search, collapseFunc=self.CollapseGroups)
        self.scroll = Scroll(parent=self)
        self.LoadRecipes()
        self.OpenOnRecipeID(self.itemTraderController.selectedRecipe.recipeID)

    def LoadRecipes(self):
        scrollList = self.GetScrollList()
        self.scroll.Load(contentList=scrollList)

    def GetScrollList(self):
        scrollList = []
        outputByGroups = defaultdict(list)
        for recipeID, recipe in self.itemTraderController.GetRecipes().iteritems():
            if self.itemTraderController.IsFilteredOut(recipe):
                continue
            outputByGroups[recipe.groupID].append(recipe)

        if len(outputByGroups) == 1:
            recipeList = outputByGroups.values()[0]
            return self.GetFlatRecipeScrollList(recipeList, 0)
        for groupID, recipeList in outputByGroups.iteritems():
            groupName = GetRecipeGroupName(groupID)
            groupTexturePath = GetRecipeGroupTexturepath(groupID)
            recipeIDs = {x.recipeID for x in recipeList}
            entry = GetFromClass(ListGroup, {'GetSubContent': self.GetRecipeSubContent,
             'label': groupName,
             'id': ('recipeGroupList', groupID),
             'state': 'locked',
             'BlockOpenWindow': 1,
             'showicon': groupTexturePath,
             'iconColor': TextColor.NORMAL,
             'showlen': 1,
             'groupItems': recipeList,
             'typeGroupID': groupID,
             'recipeIDs': recipeIDs})
            scrollList.append((groupName.lower(), entry))

        scrollList = SortListOfTuples(scrollList)
        return scrollList

    def GetRecipeSubContent(self, nodedata, *args):
        recipeList = nodedata.groupItems
        scrollList = self.GetFlatRecipeScrollList(recipeList, 1)
        return scrollList

    def GetFlatRecipeScrollList(self, recipeList, sublevel):
        scrollList = []
        for recipe in recipeList:
            affordable = self.itemTraderController.IsRecipeAffordable(recipe)
            recipeName, sortValue = recipe.GetRecipeNameAndSortValue()
            data = {'label': recipeName,
             'OnClick': self.OnEntryClicked,
             'recipe': recipe,
             'sublevel': sublevel,
             'recipeID': recipe.recipeID,
             'affordable': affordable,
             'labelColor': TextColor.NORMAL if affordable else eveColor.DANGER_RED}
            scrollList.append((sortValue, GetFromClass(RecipeEntry, data)))

        scrollList = SortListOfTuples(scrollList)
        return scrollList

    def _GetRecipeNameAndSortValueInGroup(self, recipe):
        inputLabels = []
        for typeID, quantity in recipe.outputItems.iteritems():
            typeName = evetypes.GetName(typeID)
            if quantity > 1:
                text = GetByLabel('UI/Inventory/QuantityAndName', quantity=quantity, name=typeName)
            else:
                text = typeName
            internalSortValue = (typeName, quantity)
            inputLabels.append((internalSortValue, text))

        sortedListWithSortValues = sorted(inputLabels, key=lambda data: data[0])
        sortedInputLabels = [ item[1] for item in sortedListWithSortValues ]
        sortValueForEntry = [ item[0] for item in sortedListWithSortValues ]
        return (', '.join(sortedInputLabels), sortValueForEntry)

    def OnEntryClicked(self, entry, *args):
        node = entry.sr.node
        self.itemTraderController.selectedRecipe = node.recipe

    def OpenOnRecipeID(self, recipeID, *args):
        for node in self.scroll.GetNodes():
            if recipeID in node.get('recipeIDs', []):
                if self.scroll.scrollingRange:
                    position = node.scroll_positionFromTop / float(self.scroll.scrollingRange)
                    self.scroll.ScrollToProportion(position, threaded=False)
                if not node.open:
                    if node.panel is not None:
                        node.panel.OnClick(openGroup=False)
                    else:
                        uicore.registry.SetListGroupOpenState(node.id, True)
                    blue.synchro.Yield()
                    return self.OpenOnRecipeID(recipeID)
            elif node.get('recipeID', None) == recipeID:
                self.scroll.SelectNode(node)
                break

    def CollapseGroups(self, *args):
        self.scroll.CollapseAll()

    def Search(self, searchString):
        self.itemTraderController.searchString = searchString
        self.LoadRecipes()


class RecipeEntry(Generic):

    def Load(self, node):
        super(RecipeEntry, self).Load(node)
        labelColor = node.get('labelColor', TextColor.NORMAL)
        self.sr.label.SetTextColor(labelColor)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        node = self.sr.node
        recipe = node.recipe
        LoadRecipeTooltipPanel(tooltipPanel, recipe)


class SearchCont(Container):
    default_height = 36

    def ApplyAttributes(self, attributes):
        super(SearchCont, self).ApplyAttributes(attributes)
        self.itemTraderController = attributes.itemTraderController
        self.searchFunc = attributes.searchFunc
        self.collapseFunc = attributes.collapseFunc
        ButtonIcon(name='collapse', parent=self, align=uiconst.CENTERLEFT, pos=(0, 0, 24, 24), iconSize=12, texturePath='res:/UI/Texture/classes/Scroll/Collapse.png', func=self.CollapseAll, hint=GetByLabel('UI/Common/Buttons/CollapseAll'))
        MenuButtonIcon(parent=self, align=uiconst.CENTERLEFT, pos=(24, 0, 24, 24), iconSize=16, texturePath=eveicon.filter, get_menu_func=self.GeFilterMenu, hint=GetByLabel('UI/Generic/Filters'))
        self.searchInput = QuickFilterEdit(name='searchField', parent=self, setvalue='', hintText=GetByLabel('UI/Common/Search'), padLeft=52, padRight=4, maxLength=64, align=uiconst.TOTOP, OnClearFilter=self.Search, isTypeField=True)
        self.searchInput.OnReturn = self.Search
        self.searchInput.ReloadFunction = self.Search

    def Search(self):
        searchString = self.searchInput.GetValue()
        self.searchFunc(searchString)

    def CollapseAll(self, *args):
        if self.collapseFunc:
            self.collapseFunc()

    def GeFilterMenu(self):
        menu = MenuData()
        menu.AddCheckbox(text=GetByLabel('UI/Inflight/SpaceComponents/ItemTrader/OnlyShowAffordableTrades'), setting=self.itemTraderController.affordableSetting)
        return menu
