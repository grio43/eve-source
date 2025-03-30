#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\charsheet\emblemsPanel.py
from carbon.common.script.sys.serviceConst import ROLE_GML
from carbonui.primitives.layoutGrid import LayoutGrid
from eve.client.script.ui.cosmetics.structure.cosmeticLicenseErrorScreen import CosmeticLicenseErrorScreen
from cosmetics.common.cosmeticsConst import ICON_PATH_BY_TYPE, CATEGORY_NAME_BY_TYPE
from functools import partial
import evetypes
import eveicon
import localization
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.entries.item import Item
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.listgroup import ListGroup
from eve.client.script.ui.control.utilMenu import UtilMenu
from eve.client.script.ui.quickFilter import QuickFilterEdit
from shipcosmetics.client.licensegateway.licenseSignals import on_ship_cosmetics_license_change
SETTING_SHOW_EMBLEMS = 'charsheet_shipEmblems_showEmblems'
SHOW_ALL_EMBLEMS = 'all_emblems'
SHOW_OWNED_EMBLEMS = 'owned_emblems'
SHOW_UNOWNED_EMBLEMS = 'unowned_emblems'
SETTING_DEFAULTS = {SETTING_SHOW_EMBLEMS: SHOW_ALL_EMBLEMS}

class EmblemsPanel(Container):
    default_name = 'EmblemsPanel'
    default_padTop = 16

    def ApplyAttributes(self, attributes):
        super(EmblemsPanel, self).ApplyAttributes(attributes)
        self.cosmeticsLicenseSvc = sm.GetService('cosmeticsLicenseSvc')
        self.ConstructErrorScreen(attributes.errorScreenPadding)
        on_ship_cosmetics_license_change.connect(self._OnLicenseStatusChanged)
        self.isConstructed = False

    def Close(self):
        super(EmblemsPanel, self).Close()
        on_ship_cosmetics_license_change.disconnect(self._OnLicenseStatusChanged)

    def ConstructLayout(self):
        if self.isConstructed:
            return
        self.isConstructed = True
        menuBar = ContainerAutoSize(parent=self, align=uiconst.TOTOP, padBottom=16, alignMode=uiconst.CENTERLEFT)
        UtilMenu(parent=menuBar, align=uiconst.CENTERLEFT, GetUtilMenu=self.GetSettingsMenu, texturePath=eveicon.settings, width=24, height=24, iconSize=16)
        self.filter = QuickFilterEdit(parent=menuBar, name='filter', align=uiconst.CENTERRIGHT, left=2, width=150, hintText=localization.GetByLabel('UI/Inventory/Filter'))
        Container(parent=menuBar, name='spacer', align=uiconst.CENTERLEFT, pos=(0,
         0,
         1,
         self.filter.height))
        self.counterText = EveLabelMedium(parent=ContainerAutoSize(parent=menuBar, align=uiconst.TOLEFT, left=30), align=uiconst.CENTERLEFT, text='')
        self.filter.ReloadFunction = self.LoadPanel
        self.scroll = Scroll(parent=self, align=uiconst.TOALL)

    def ConstructErrorScreen(self, errorScreenPadding):
        self.errorScreen = CosmeticLicenseErrorScreen(name='errorScreen', parent=self, align=uiconst.TOALL, padding=(-errorScreenPadding[0],
         -errorScreenPadding[1],
         -errorScreenPadding[2],
         -errorScreenPadding[3]))
        self.errorScreen.CloseScreen(animate=False)

    def _OnSizeChange_NoBlock(self, *args):
        super(EmblemsPanel, self)._OnSizeChange_NoBlock(*args)
        if hasattr(self, 'errorScreen'):
            self.errorScreen.AdjustWidth(args[0])

    @property
    def filterText(self):
        return self.filter.GetValue().strip().lower()

    def LoadPanel(self, *args):
        self.ConstructLayout()
        self.scroll.Clear()
        try:
            licensesByType = self._GetFilteredLicensesByType()
            entries = []
            for licenseType, licenses in licensesByType.iteritems():
                entry = self._CreateGroupEntry(licenseType, licenses)
                if entry is not None:
                    entries.append(entry)

            self.scroll.Load(contentList=entries, noContentHint=localization.GetByLabel('UI/SkillQueue/NoResultsForFilters'))
            numOwnedLicenses = len(self.cosmeticsLicenseSvc.get_owned_ship_licenses())
            self.counterText.text = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/ShipEmblems/YouHaveNumShipEmblems', numEmblems=numOwnedLicenses)
        except RuntimeError:
            self.errorScreen.ShowScreen(localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/ShipEmblems/FetchLicensesFailedErrorMessage'), localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/ShipEmblems/FetchLicensesFailedErrorSubtext'), localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/ShipEmblems/FetchingFailedButton'), self._RetryFetchingCosmeticsLicenses)

    def _RetryFetchingCosmeticsLicenses(self):
        self.errorScreen.CloseScreen(True)
        self.LoadPanel()

    def _GetFilteredLicensesByType(self):
        licenses = []
        showFilter = GetSetting(SETTING_SHOW_EMBLEMS)
        if showFilter == SHOW_ALL_EMBLEMS:
            licenses = self.cosmeticsLicenseSvc.get_all_ship_licenses()
        elif showFilter == SHOW_OWNED_EMBLEMS:
            licenses = self.cosmeticsLicenseSvc.get_owned_ship_licenses()
        elif showFilter == SHOW_UNOWNED_EMBLEMS:
            licenses = self.cosmeticsLicenseSvc.get_unowned_ship_licenses()
        licensesByType = {}
        for license in licenses:
            if self.filterText == '' or self.filterText in evetypes.GetName(license.fsdTypeID).lower():
                if license.cosmeticType not in licensesByType:
                    licensesByType[license.cosmeticType] = []
                licensesByType[license.cosmeticType].append(license)

        return licensesByType

    def _CreateGroupEntry(self, cosmeticType, licenses):
        licensesByLicenseID = {license.licenseID:(license, self.cosmeticsLicenseSvc.is_ship_license_owned(license.licenseID)) for license in licenses}
        groupName = localization.GetByLabel(CATEGORY_NAME_BY_TYPE[cosmeticType])
        emblemsOwned = sum((1 for each in licensesByLicenseID.values() if each[1]))
        emblemsTotal = len(licensesByLicenseID)
        iconPath = ICON_PATH_BY_TYPE[cosmeticType]
        return GetFromClass(ListGroup, {'label': localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/ShipEmblems/EmblemsGroupWithCount', groupName=groupName, emblemsOwned=emblemsOwned, emblemsTotal=emblemsTotal),
         'id': ('ShipEmblems', groupName),
         'showicon': iconPath,
         'groupItems': licensesByLicenseID,
         'GetSubContent': self._GetEmblemSubContent,
         'showlen': False,
         'BlockOpenWindow': True,
         'state': 'locked'})

    def _GetEmblemSubContent(self, nodedata, *args):
        licensesByLicenseID = nodedata.groupItems
        nodes = []
        for licenseID, (license, owned) in licensesByLicenseID.iteritems():
            data = self._GetDataForEmblemEntry(license, owned)
            entry = GetFromClass(ShipEmblemEntry, data)
            nodes.append(entry)

        nodes = sorted(nodes, key=lambda x: x.label)
        return nodes

    def _GetDataForEmblemEntry(self, license, owned):
        data = {'typeID': license.shipTypeID,
         'licenseID': license.licenseID,
         'itemID': None,
         'label': evetypes.GetName(license.shipTypeID),
         'getIcon': True,
         'sublevel': 1,
         'skin': license,
         'owned': owned}
        return data

    def GetSettingsMenu(self, menuParent):
        menuParent.AddRadioButton(text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/ShipEmblems/ShowAllEmblems'), checked=GetSetting(SETTING_SHOW_EMBLEMS) == SHOW_ALL_EMBLEMS, callback=partial(self.SetSettingAndReload, SETTING_SHOW_EMBLEMS, SHOW_ALL_EMBLEMS))
        menuParent.AddRadioButton(text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/ShipEmblems/ShowOwnedEmblems'), checked=GetSetting(SETTING_SHOW_EMBLEMS) == SHOW_OWNED_EMBLEMS, callback=partial(self.SetSettingAndReload, SETTING_SHOW_EMBLEMS, SHOW_OWNED_EMBLEMS))
        menuParent.AddRadioButton(text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/ShipEmblems/ShowNotOwnedEmblems'), checked=GetSetting(SETTING_SHOW_EMBLEMS) == SHOW_UNOWNED_EMBLEMS, callback=partial(self.SetSettingAndReload, SETTING_SHOW_EMBLEMS, SHOW_UNOWNED_EMBLEMS))

    def SetSettingAndReload(self, key, value):
        SetSetting(key, value)
        self.LoadPanel()

    def _OnLicenseStatusChanged(self, _cosmeticsLicenseID, _enable):
        if self.display:
            self.LoadPanel()


class ShipEmblemEntry(Item):

    def Startup(self, *args):
        super(ShipEmblemEntry, self).Startup(*args)

    def Load(self, node):
        super(ShipEmblemEntry, self).Load(node)
        self.sr.label.opacity = 1 if node.owned else 0.5
        self.sr.icon.opacity = 1 if node.owned else 0.5
        if node.owned:
            grid = LayoutGrid(parent=self, align=uiconst.CENTERRIGHT, columns=2, left=26)
            EveLabelMedium(parent=grid, text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/ShipEmblems/ShipEmblemAcquired'))

    def GetMenu(self):
        menu = super(ShipEmblemEntry, self).GetMenu()
        if session.role & ROLE_GML:
            menu.insert(0, ('GM: Revoke me this emblem', self._DebugRevokeCosmeticLicense))
            menu.insert(0, ('GM: Grant me this emblem', self._DebugGrantCosmeticLicense))
        return menu

    def _DebugRevokeCosmeticLicense(self):
        sm.GetService('cosmeticsLicenseSvc').debug_revoke_ship_cosmetics_license(self.sr.node.licenseID)

    def _DebugGrantCosmeticLicense(self):
        sm.GetService('cosmeticsLicenseSvc').debug_grant_ship_cosmetics_license(self.sr.node.licenseID)


def GetSetting(key):
    return settings.user.ui.Get(key, SETTING_DEFAULTS[key])


def SetSetting(key, value):
    settings.user.ui.Set(key, value)
