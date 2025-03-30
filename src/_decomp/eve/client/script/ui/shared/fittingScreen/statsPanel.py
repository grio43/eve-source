#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\statsPanel.py
import dogma.data as dogma_data
from carbonui import const as uiconst, fontconst
from carbonui.primitives.container import Container
import dogma.const as dogmaConst
from eve.client.script.ui.control.expandablemenu import ExpandableMenuContainer
from eve.client.script.ui.shared.fitting.fittingUtil import EatSignalChangingErrors
from eve.client.script.ui.shared.fittingScreen.fittingPanels.capacitorPanel import CapacitorPanel
from eve.client.script.ui.shared.fittingScreen.fittingPanels.defensePanel import DefensePanel
from eve.client.script.ui.shared.fittingScreen.fittingPanels.dronePanel import DronePanel
from eve.client.script.ui.shared.fittingScreen.fittingPanels.fighterPanel import FighterPanel
from eve.client.script.ui.shared.fittingScreen.fittingPanels.fuelPanel import FuelPanel
from eve.client.script.ui.shared.fittingScreen.fittingPanels.navigationPanel import NavigationPanel
from eve.client.script.ui.shared.fittingScreen.fittingPanels.offensePanel import OffensePanel
from eve.client.script.ui.shared.fittingScreen.fittingPanels.targetingPanel import TargetingPanel
from eve.client.script.ui.shared.fittingScreen.priceLabel import LabelPriceLabelCont
from eveui.decorators import lock_and_set_pending
from signals.signalUtil import ChangeSignalConnect
import inventorycommon.const as invConst
from localization import GetByLabel
import uthread
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
NO_HILITE_GROUPS_DICT = {invConst.groupRemoteSensorBooster: [dogmaConst.attributeCpu, dogmaConst.attributePower],
 invConst.groupRemoteSensorDamper: [dogmaConst.attributeCpu, dogmaConst.attributePower]}
MENU_NAME_BY_UI_NAME = {pConst.UNIQUE_NAME_FITTING_CAP: 'Capacitor',
 pConst.UNIQUE_NAME_FITTING_OFFENSE: 'Offense',
 pConst.UNIQUE_NAME_FITTING_DEFENSE: 'Defense',
 pConst.UNIQUE_NAME_FITTING_NAVIGATION: 'Navigation',
 pConst.UNIQUE_NAME_FITTING_TARGETING: 'Targeting',
 pConst.UNIQUE_NAME_FITTING_DRONES: 'Drones',
 pConst.UNIQUE_NAME_FITTING_FIGHTERS: 'Fighters',
 pConst.UNIQUE_NAME_FITTING_FUEL: 'Fuel'}

class StatsPanel(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.subCont = Container(parent=self)
        self.controller = attributes.controller
        self.ChangeSignalConnection(connect=True)
        self.ConstructPriceLabel()
        self.CreateCapacitorPanel()
        self.CreateOffensePanel()
        self.CreateDefensePanel()
        self.CreateTargetingPanel()
        self.CreateNavigationPanel()
        self.CreateDronePanel()
        self.CreateFighterPanel()
        self.CreateFuelPanel()
        self.CreateExpandableMenus()
        uthread.new(self.UpdateStats)

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.controller.on_new_itemID, self.OnNewItemID),
         (self.controller.on_stats_changed, self.UpdateStatsOnSignal),
         (self.controller.on_drones_changed, self.UpdateStatsOnSignal),
         (self.controller.on_item_ghost_fitted, self.UpdateStatsOnSignal)]
        ChangeSignalConnect(signalAndCallback, connect)

    def ConstructPriceLabel(self):
        self.priceLabelCont = LabelPriceLabelCont(parent=self)

    def CreateCapacitorPanel(self):
        self.capacitorStatsParent = CapacitorPanel(name='capacitorStatsParent', controller=self.controller)
        return self.capacitorStatsParent

    def CreateOffensePanel(self):
        self.offenseStatsParent = OffensePanel(name='offenseStatsParent', tooltipName='DamagePerSecond', labelHint=GetByLabel('UI/Fitting/FittingWindow/ShipDpsTooltip'), controller=self.controller)
        return self.offenseStatsParent

    def CreateDefensePanel(self):
        self.defenceStatsParent = DefensePanel(name='defenceStatsParent', state=uiconst.UI_PICKCHILDREN, tooltipName='EffectiveHitPoints', labelHint=GetByLabel('UI/Fitting/FittingWindow/EffectiveHitpoints'), controller=self.controller)
        return self.defenceStatsParent

    def CreateTargetingPanel(self):
        self.targetingStatsParent = TargetingPanel(name='targetingStatsParent', tooltipName='MaxTargetingRange', controller=self.controller)
        return self.targetingStatsParent

    def CreateNavigationPanel(self):
        self.navigationStatsParent = NavigationPanel(name='navigationStatsParent', state=uiconst.UI_PICKCHILDREN, tooltipName='MaximumVelocity', labelHint=GetByLabel('UI/Fitting/FittingWindow/MaxVelocityHint'), controller=self.controller)
        return self.navigationStatsParent

    def CreateDronePanel(self):
        self.droneStatsParent = DronePanel(name='droneStatsParent', tooltipName='DamagePerSecondDrones', labelHint=GetByLabel('UI/Fitting/FittingWindow/ShipDpsTooltip'), controller=self.controller)
        return self.droneStatsParent

    def CreateFighterPanel(self):
        self.fighterStatsParent = FighterPanel(name='fighterStatsParent', tooltipName='DamagePerSecondDrones', labelHint=GetByLabel('UI/Fitting/FittingWindow/ShipDpsTooltip'), controller=self.controller)
        return self.fighterStatsParent

    def CreateFuelPanel(self):
        self.fuelStatsParent = FuelPanel(name='fuelStatsParent', tooltipName='FuelUsage', controller=self.controller)
        return self.fuelStatsParent

    def GetSingleMenuPanelInfo(self, menuDict):
        return (GetByLabel(menuDict['label']),
         menuDict['content'],
         menuDict['callback'],
         None,
         menuDict['maxHeight'],
         menuDict['headerContent'],
         False,
         menuDict.get('expandedByDefault', False),
         menuDict.get('uniqueUiName', None),
         menuDict.get('name', None))

    def GetMenuData(self):
        sizeFactor = fontconst.fontSizeFactor ** 0.1
        capInfo = self.GetSingleMenuPanelInfo({'label': 'UI/Fitting/FittingWindow/Capacitor',
         'content': self.capacitorStatsParent,
         'callback': self.LoadCapacitorStats,
         'maxHeight': 64 * sizeFactor,
         'headerContent': self.capacitorStatsParent.headerParent,
         'expandedByDefault': True,
         'uniqueUiName': pConst.UNIQUE_NAME_FITTING_CAP,
         'name': MENU_NAME_BY_UI_NAME[pConst.UNIQUE_NAME_FITTING_CAP]})
        offenseInfo = self.GetSingleMenuPanelInfo({'label': 'UI/Fitting/FittingWindow/Offense',
         'content': self.offenseStatsParent,
         'callback': self.LoadOffenseStats,
         'maxHeight': 50 * sizeFactor,
         'headerContent': self.offenseStatsParent.headerParent,
         'uniqueUiName': pConst.UNIQUE_NAME_FITTING_OFFENSE,
         'name': MENU_NAME_BY_UI_NAME[pConst.UNIQUE_NAME_FITTING_OFFENSE]})
        defenseInfo = self.GetSingleMenuPanelInfo({'label': 'UI/Fitting/FittingWindow/Defense',
         'content': self.defenceStatsParent,
         'callback': self.LoadDefenceStats,
         'maxHeight': 146 * sizeFactor,
         'headerContent': self.defenceStatsParent.headerParent,
         'uniqueUiName': pConst.UNIQUE_NAME_FITTING_DEFENSE,
         'name': MENU_NAME_BY_UI_NAME[pConst.UNIQUE_NAME_FITTING_DEFENSE]})
        targetingInfo = self.GetSingleMenuPanelInfo({'label': 'UI/Fitting/FittingWindow/Targeting',
         'content': self.targetingStatsParent,
         'callback': self.LoadTargetingStats,
         'maxHeight': 76 * sizeFactor,
         'headerContent': self.targetingStatsParent.headerParent,
         'uniqueUiName': pConst.UNIQUE_NAME_FITTING_TARGETING,
         'name': MENU_NAME_BY_UI_NAME[pConst.UNIQUE_NAME_FITTING_TARGETING]})
        menuData = [capInfo,
         offenseInfo,
         defenseInfo,
         targetingInfo]
        if self.controller.HasNavigationPanel():
            navigationInfo = self.GetSingleMenuPanelInfo({'label': 'UI/Fitting/FittingWindow/Navigation',
             'content': self.navigationStatsParent,
             'callback': self.LoadNavigationStats,
             'maxHeight': 76 * sizeFactor,
             'headerContent': self.navigationStatsParent.headerParent,
             'uniqueUiName': pConst.UNIQUE_NAME_FITTING_NAVIGATION,
             'name': MENU_NAME_BY_UI_NAME[pConst.UNIQUE_NAME_FITTING_NAVIGATION]})
            menuData += [navigationInfo]
        if self.controller.HasDronePanel():
            droneInfo = self.GetSingleMenuPanelInfo({'label': 'UI/Drones/Drones',
             'content': self.droneStatsParent,
             'callback': self.LoadDroneStats,
             'maxHeight': 90 * sizeFactor,
             'headerContent': self.droneStatsParent.headerParent,
             'uniqueUiName': pConst.UNIQUE_NAME_FITTING_DRONES,
             'name': MENU_NAME_BY_UI_NAME[pConst.UNIQUE_NAME_FITTING_DRONES]})
            menuData += [droneInfo]
        droneInfo = self.GetSingleMenuPanelInfo({'label': 'UI/Common/Fighters',
         'content': self.fighterStatsParent,
         'callback': self.LoadFighterStats,
         'maxHeight': 70 * sizeFactor,
         'headerContent': self.fighterStatsParent.headerParent,
         'uniqueUiName': pConst.UNIQUE_NAME_FITTING_FIGHTERS,
         'name': MENU_NAME_BY_UI_NAME[pConst.UNIQUE_NAME_FITTING_FIGHTERS]})
        menuData += [droneInfo]
        if self.controller.HasFuelPanel():
            fuelInfo = self.GetSingleMenuPanelInfo({'label': 'UI/Fitting/FittingWindow/Fuel',
             'content': self.fuelStatsParent,
             'callback': self.LoadFuelStats,
             'maxHeight': 60 * sizeFactor,
             'headerContent': self.fuelStatsParent.headerParent,
             'uniqueUiName': pConst.UNIQUE_NAME_FITTING_FUEL,
             'name': MENU_NAME_BY_UI_NAME[pConst.UNIQUE_NAME_FITTING_FUEL]})
            menuData += [fuelInfo]
        return menuData

    def CreateExpandableMenus(self):
        self.expandableMenu = ExpandableMenuContainer(parent=self.subCont, pos=(0, 0, 0, 0), clipChildren=True)
        self.expandableMenu.multipleExpanded = True
        menuData = self.GetMenuData()
        self.expandableMenu.Load(menuData=menuData, prefsKey='fittingRightside')
        self.ChangeDroneAndFighterPanelDisplays()

    def LoadDroneStats(self, initialLoad = False):
        if self.controller.HasDronePanel():
            self.droneStatsParent.LoadPanel(initialLoad=initialLoad)

    def LoadFighterStats(self, initialLoad = False):
        if self.controller.HasFighterBay():
            self.fighterStatsParent.LoadPanel(initialLoad=initialLoad)

    def LoadNavigationStats(self, initialLoad = False):
        if self.controller.HasNavigationPanel():
            self.navigationStatsParent.LoadPanel(initialLoad=initialLoad)

    def LoadTargetingStats(self, initialLoad = False):
        self.targetingStatsParent.LoadPanel(initialLoad=initialLoad)

    def LoadOffenseStats(self, initialLoad = False):
        self.offenseStatsParent.LoadPanel(initialLoad)

    def LoadFuelStats(self, initialLoad = False):
        if self.controller.HasFuelPanel():
            self.fuelStatsParent.LoadPanel(initialLoad=initialLoad)

    def UpdateOffenseStats(self):
        self.offenseStatsParent.UpdateOffenseStats()

    def UpdateDroneStats(self):
        if self.controller.HasDronePanel():
            self.droneStatsParent.UpdateDroneStats()

    def UpdateFighterStats(self):
        if self.controller.HasFighterBay():
            self.fighterStatsParent.UpdateFighterStats()

    def LoadDefenceStats(self, initialLoad = False):
        self.defenceStatsParent.LoadPanel(initialLoad)

    def LoadCapacitorStats(self, initialLoad = False):
        self.capacitorStatsParent.LoadPanel(initialLoad)

    def ExpandBestRepair(self, *args):
        self.defenceStatsParent.ExpandBestRepair(*args)

    def UpdateBestRepair(self):
        return self.defenceStatsParent.UpdateBestRepair()

    def UpdateNavigationPanel(self):
        if self.controller.HasNavigationPanel():
            self.navigationStatsParent.UpdateNavigationPanel()

    def UpdateTargetingPanel(self):
        self.targetingStatsParent.UpdateTargetingPanel()

    def UpdateCapacitor(self):
        self.capacitorStatsParent.UpdateCapacitorPanel()

    def UpdateDefensePanel(self):
        return self.defenceStatsParent.UpdateDefensePanel()

    def UpdateFuelPanel(self):
        if self.controller.HasFuelPanel():
            self.fuelStatsParent.UpdateFuelPanel()

    def UpdateStatsOnSignal(self):
        uthread.new(self.UpdateStats)

    @lock_and_set_pending()
    def UpdateStats(self):
        if not self.controller or not self.controller.CurrentShipIsLoaded():
            return
        dsp = getattr(self, 'defenceStatsParent', None)
        if not dsp or dsp.destroyed:
            return
        self.UpdateDefensePanel()
        self.UpdateBestRepair()
        self.UpdateNavigationPanel()
        self.UpdateTargetingPanel()
        self.UpdateCapacitor()
        self.UpdateOffenseStats()
        self.UpdateDroneStats()
        self.UpdateFighterStats()
        self.UpdateFuelPanel()
        uthread.new(self.priceLabelCont.UpdateLabel, self.controller)

    def MaxTargetRangeBonusMultiplier(self, typeID):
        for effect in dogma_data.get_type_effects(typeID):
            if effect.effectID in (dogmaConst.effectShipMaxTargetRangeBonusOnline, dogmaConst.effectMaxTargetRangeBonus):
                return 1

    def ArmorOrShieldMultiplier(self, typeID):
        for effect in dogma_data.get_type_effects(typeID):
            if effect.effectID == dogmaConst.effectShieldResonanceMultiplyOnline:
                return 1

    def ArmorShieldStructureMultiplierPostPercent(self, typeID):
        ret = []
        for effect in dogma_data.get_type_effects(typeID):
            if effect.effectID == dogmaConst.effectModifyArmorResonancePostPercent:
                ret.append('armor')
            elif effect.effectID == dogmaConst.effectModifyShieldResonancePostPercent:
                ret.append('shield')
            elif effect.effectID == dogmaConst.effectModifyHullResonancePostPercent:
                ret.append('structure')

        return ret

    def OnNewItemID(self, *args):
        if self.destroyed:
            return
        self.ChangeDroneAndFighterPanelDisplays()
        for eachPanel in [self.capacitorStatsParent,
         self.offenseStatsParent,
         self.defenceStatsParent,
         self.targetingStatsParent,
         self.navigationStatsParent,
         self.droneStatsParent,
         self.fighterStatsParent]:
            eachPanel.SetDogmaLocation()

        self.UpdateStats()

    def ChangeDroneAndFighterPanelDisplays(self):
        if self.controller.HasFighterBay():
            self.expandableMenu.HideMenuByLabel(GetByLabel('UI/Drones/Drones'))
            self.expandableMenu.ShowMenuByLabel(GetByLabel('UI/Common/Fighters'))
        else:
            self.expandableMenu.HideMenuByLabel(GetByLabel('UI/Common/Fighters'))
            self.expandableMenu.ShowMenuByLabel(GetByLabel('UI/Drones/Drones'))

    def IsPanelExpanded(self, uniqueUiName):
        if self.expandableMenu and not self.expandableMenu.destroyed:
            return self.expandableMenu.IsMenuExpanded(uniqueUiName)
        return False

    def Close(self):
        with EatSignalChangingErrors(errorMsg='StatsPanelGhost'):
            self.ChangeSignalConnection(connect=False)
        Container.Close(self)
