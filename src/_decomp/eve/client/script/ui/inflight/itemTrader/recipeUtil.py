#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\itemTrader\recipeUtil.py
from collections import defaultdict
import eveicon
import evetypes
from carbonui import TextColor
from carbonui.primitives.sprite import Sprite
from carbonui.util.sortUtil import SortListOfTuples
from eve.common.script.util.eveFormat import FmtISK
from localization import GetByLabel
import carbonui.const as uiconst

def LoadRecipeTooltipPanel(tooltipPanel, recipe):
    tooltipPanel.LoadStandardSpacing()
    tooltipPanel.columns = 2
    displayName = recipe.displayName
    if displayName:
        tooltipPanel.AddTextBodyLabel(text=displayName, bold=True, colSpan=tooltipPanel.columns)
    tooltipPanel.AddTextBodyLabel(text=GetByLabel('UI/Inflight/SpaceComponents/ItemTrader/RequiredItems'), colSpan=tooltipPanel.columns)
    if recipe.inputIsk:
        Sprite(parent=tooltipPanel, align=uiconst.CENTERLEFT, pos=(0, 0, 20, 20), texturePath=eveicon.isk)
        tooltipPanel.AddTextDetailsLabel(text=FmtISK(recipe.inputIsk))
        tooltipPanel.FillRow()
    for typeID, quantity in recipe.inputItems.iteritems():
        typeIcon = Sprite(parent=tooltipPanel, align=uiconst.CENTERLEFT, pos=(0, 0, 20, 20))
        sm.GetService('photo').GetIconByType(typeIcon, typeID)
        tooltipPanel.AddTextDetailsLabel(text=str(quantity) + ' ' + evetypes.GetName(typeID))
        tooltipPanel.FillRow()

    tooltipPanel.AddTextBodyLabel(text=GetByLabel('UI/Inflight/SpaceComponents/ItemTrader/DeliveredItems'), colSpan=tooltipPanel.columns)
    for typeID, quantity in recipe.outputItems.iteritems():
        typeIcon = Sprite(parent=tooltipPanel, align=uiconst.CENTERLEFT, pos=(0, 0, 20, 20))
        sm.GetService('photo').GetIconByType(typeIcon, typeID)
        tooltipPanel.AddTextDetailsLabel(text=str(quantity) + ' ' + evetypes.GetName(typeID))
        tooltipPanel.FillRow()


GROUP_SHIP_BLUEPRINTS = 'SHIP_BLUEPRINTS'
GROUP_MODULES_AMMO = 'MODULES_AMMO'
GROUP_SKINR = 'SKINR'
GROUP_SKILLBOOKS = 'SKILLBOOKS'
_recipeGroupLabelPathByGroupID = {None: 'UI/Inflight/SpaceComponents/ItemTrader/GroupMisc',
 GROUP_SHIP_BLUEPRINTS: 'UI/Inflight/SpaceComponents/ItemTrader/GroupShipBlueprints',
 GROUP_MODULES_AMMO: 'UI/Inflight/SpaceComponents/ItemTrader/GroupModulesAndAmmoBlueprints',
 GROUP_SKINR: 'UI/Inflight/SpaceComponents/ItemTrader/GroupSkinrComponents',
 GROUP_SKILLBOOKS: 'UI/Inflight/SpaceComponents/ItemTrader/GroupSkillbooks'}
_recipeGroupTexturepathByGroupID = {GROUP_SHIP_BLUEPRINTS: eveicon.spaceship_command,
 GROUP_MODULES_AMMO: eveicon.gunnery,
 GROUP_SKINR: eveicon.skinr,
 GROUP_SKILLBOOKS: eveicon.skill_book}

def GetRecipeGroupName(groupID):
    return GetByLabel(_recipeGroupLabelPathByGroupID.get(groupID, 'UI/Inflight/SpaceComponents/ItemTrader/GroupMisc'))


def GetRecipeGroupTexturepath(groupID):
    return _recipeGroupTexturepathByGroupID.get(groupID)


def GetSortedRecipeGroupsAndData(allRecipes):
    recipeDataByGroups = defaultdict(list)
    for recipe in allRecipes:
        name, sortValue = recipe.GetRecipeNameAndSortValue()
        data = {'recipe': recipe,
         'label': name,
         'sortValue': sortValue,
         'sublevel': 1,
         'line': 1,
         'labelColor': TextColor.SECONDARY}
        recipeDataByGroups[recipe.groupID].append(data)

    for recipeDataList in recipeDataByGroups.itervalues():
        recipeDataList.sort(key=lambda x: x['sortValue'])

    forSorting = []
    for groupID, recipeDataList in recipeDataByGroups.iteritems():
        groupName = GetRecipeGroupName(groupID)
        forSorting.append((groupName.lower(), (groupName, recipeDataList)))

    return SortListOfTuples(forSorting)
