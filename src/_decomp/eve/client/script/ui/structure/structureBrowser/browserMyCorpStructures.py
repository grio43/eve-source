#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\structureBrowser\browserMyCorpStructures.py
import gametime
import uthread
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.control.dragResizeCont import DragResizeCont
from carbonui.primitives.container import Container
from carbonui.util.bunch import Bunch
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.scrollUtil import TabFinder
from carbonui.control.tabGroup import TabGroup
from eve.client.script.ui.shared.fitting.fittingUtil import EatSignalChangingErrors
from eve.client.script.ui.structure import ChangeSignalConnect
import eve.client.script.ui.structure.structureBrowser.browserUIConst as browserUIConst
from eve.client.script.ui.structure.structureBrowser.controllers.filterContController import FilterContControllerMyStructures
from eve.client.script.ui.structure.structureBrowser.controllers.structureEntryController import StructureEntryController
from eve.client.script.ui.structure.structureBrowser.corpStructureSettingsCont import CorpStructureSettingsCont
from eve.client.script.ui.structure.structureBrowser.entries.structureEntryMyCorp import StructureEntryMyCorp, StructureEntryMyCorpAllProfiles
from eve.client.script.ui.structure.structureBrowser.filterCont import FilterContMyStructures
from eve.client.script.ui.structure.structureBrowser.filterContUtil import IsFilteredOutByText, IsFilteredOutByServices
from eve.client.script.ui.structure.structureBrowser.moonminingEventsCont import MoonminingEventsCont
from eve.client.script.ui.structure.structureBrowser.structureProfiles import StructureProfiles
from eve.client.script.ui.structure.structureSettings.structureSettingsWnd import StructureProfileSettingCont
from localization import GetByLabel
import carbonui.const as uiconst
from eve.client.script.ui.control.eveLabel import EveCaptionSmall, EveLabelMedium, EveLabelLarge

class BrowserMyCorpStructures(Container):
    default_name = 'BrowserMyStructures'

    def __init__(self, **kwargs):
        self.structureBrowserController = None
        self.allStructuresProfileController = None
        self.currentProfileLoaded = None
        self.tabs = None
        self.myFilterContController = None
        self.isInitialized = False
        self.display = False
        self.structureListAndProfileSettingsCont = None
        self.profileSettings = None
        self.moonMiningEvents = None
        self.corpStructureSettings = None
        self.profileDescLabel = None
        self.profileNameLabel = None
        super(BrowserMyCorpStructures, self).__init__(**kwargs)

    def ApplyAttributes(self, attributes):
        super(BrowserMyCorpStructures, self).ApplyAttributes(attributes)
        self.myFilterContController = FilterContControllerMyStructures()
        self.structureBrowserController = attributes.structureBrowserController

    def OnTabSelect(self):
        self.LoadPanel()

    def LoadPanel(self):
        self.display = True
        if self.isInitialized:
            return
        self.isInitialized = True
        self.allStructuresProfileController = sm.GetService('structureControllers').GetAllStructuresProfileController()
        self.ChangeSignalConnection(connect=True)
        profileParent = DragResizeCont(name='profileParent', parent=self, align=uiconst.TOLEFT_PROP, minSize=0.1, maxSize=0.5, defaultSize=0.5, settingsID='myStructuresSplitter')
        StructureProfiles(parent=profileParent, allStructuresProfileController=self.allStructuresProfileController, structureBrowserController=self.structureBrowserController)
        self.structureListAndProfileSettingsCont = Container(name='structureListAndProfileSettingsCont', parent=self, padding=(4, 0, 4, 4))
        self.LoadTabs()

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.structureBrowserController.on_profile_selected, self.OnProfileSelected),
         (self.allStructuresProfileController.on_profile_saved, self.OnProfileSaved),
         (self.structureBrowserController.on_profile_deleted, self.OnProfileDeleted),
         (self.structureBrowserController.on_corp_structures_changed, self.OnCorpStructuresChanged)]
        ChangeSignalConnect(signalAndCallback, connect)

    def LoadTabs(self):
        self.VerifySelectedProfileIdIsValid()
        profileID = self.structureBrowserController.GetSelectedProfileID()
        self.structureListAndProfileSettingsCont.Flush()
        myStructuresPanel = MyStructuresPanel(parent=self.structureListAndProfileSettingsCont, allStructuresProfileController=self.allStructuresProfileController, structureBrowserController=self.structureBrowserController, filterContController=self.myFilterContController)
        tabs = [(GetByLabel('UI/StructureBrowser/StructuresWithProfile'),
          myStructuresPanel,
          None,
          'myStructuresPanel',
          None,
          GetByLabel('UI/StructureBrowser/StructuresWithProfileHint'))]
        if profileID != browserUIConst.ALL_PROFILES:
            self.profileSettings = StructureProfileSettingCont(parent=self.structureListAndProfileSettingsCont, allStructuresProfileController=self.allStructuresProfileController, structureBrowserController=self.structureBrowserController)
            profileTab = (GetByLabel('UI/StructureBrowser/ProfileSettings'),
             self.profileSettings,
             None,
             'profileSettings',
             None,
             GetByLabel('UI/StructureBrowser/ProfileSettingsHint'))
            tabs.append(profileTab)
        self.moonMiningEvents = MoonminingEventsCont(parent=self.structureListAndProfileSettingsCont, structureBrowserController=self.structureBrowserController)
        moonMiningTab = (GetByLabel('UI/Moonmining/UpcomingExtractionsTab'),
         self.moonMiningEvents,
         None,
         'moonMiningEvents',
         None,
         GetByLabel('UI/Moonmining/UpcomingExtractionsTabHint'))
        tabs.append(moonMiningTab)
        if profileID == browserUIConst.ALL_PROFILES:
            self.corpStructureSettings = CorpStructureSettingsCont(parent=self.structureListAndProfileSettingsCont, structureBrowserController=self.structureBrowserController)
            corpSettingsTab = (GetByLabel('UI/StructureBrowser/CorpSettingsTab'),
             self.corpStructureSettings,
             None,
             'corpStructureSettings',
             None,
             GetByLabel('UI/StructureBrowser/CorpSettingsTabHint'))
            tabs.append(corpSettingsTab)
        self.tabs = TabGroup(parent=self.structureListAndProfileSettingsCont, tabs=tabs, height=32, idx=0, padLeft=0, groupID='profile_structuresAndsettings', padTop=0)
        self.profileDescLabel = EveLabelMedium(parent=self.structureListAndProfileSettingsCont, name='profileDescLabel', align=uiconst.TOTOP, idx=0)
        self.profileNameLabel = EveCaptionSmall(parent=self.structureListAndProfileSettingsCont, name='profileNameLabel', align=uiconst.TOTOP, idx=0)
        self.SetProfileName()

    def VerifySelectedProfileIdIsValid(self):
        profileID = self.structureBrowserController.GetSelectedProfileID()
        validProfileIDs = sm.GetService('structureControllers').GetValidProfileIDs()
        isProfileValid = profileID not in validProfileIDs
        if isProfileValid:
            self.structureBrowserController.SelectProfile(browserUIConst.ALL_PROFILES, sendSignal=False)
            self.currentProfileLoaded = browserUIConst.ALL_PROFILES

    def ForceProfileSettingsSelected(self):
        if self.tabs:
            self.tabs.AutoSelect()

    def OnProfileSelected(self, profileID):
        self.SetProfileName()
        if self.currentProfileLoaded is None or self._ProfileTypeHasChanged(profileID):
            self.LoadTabs()
        self.currentProfileLoaded = profileID

    def _ProfileTypeHasChanged(self, profileID):
        if profileID == self.currentProfileLoaded:
            return False
        if browserUIConst.ALL_PROFILES not in (profileID, self.currentProfileLoaded):
            return False
        return True

    def OnProfileSaved(self, profileID):
        self.structureBrowserController.SetProfileChangedValue(False)
        self.SetProfileName()

    def OnProfileDeleted(self, profileID, selectedProfileChanged):
        if selectedProfileChanged:
            self.LoadTabs()

    def OnCorpStructuresChanged(self):
        if self.structureBrowserController.GetSelectedTab() != MyStructuresPanel.TAB_ID:
            return
        self.LoadTabs()

    def SetProfileName(self):
        if self.structureBrowserController.GetSelectedProfileID() == browserUIConst.ALL_PROFILES:
            name = GetByLabel('UI/Structures/Browser/AnyProfile')
            desc = ''
        else:
            selectedProfileID = self.structureBrowserController.GetSelectedProfileID()
            selectedProfileController = self.allStructuresProfileController.GetSlimProfileController(selectedProfileID)
            name = selectedProfileController.GetProfileName()
            desc = selectedProfileController.GetProfileDescription()
        self.profileNameLabel.text = name
        self.profileDescLabel.text = desc
        self.profileNameLabel.display = False
        self.profileDescLabel.display = False

    def Close(self):
        if self.isInitialized:
            with EatSignalChangingErrors(errorMsg='BrowserMyCorpStructures'):
                self.ChangeSignalConnection(connect=False)
        self.structureBrowserController = None
        Container.Close(self)


class MyStructuresPanel(Container):
    TAB_ID = 'STRUCTURES'

    def __init__(self, **kwargs):
        self.serviceChangedTimestamp = None
        self.filterContController = None
        self.allStructuresProfileController = None
        self.allStructuresProfileController = None
        self.topPanel = None
        self.profileNameLabel = None
        self.comboCont = None
        self.scroll = None
        self.serviceChangedTimer = None
        self.structureBrowserController = None
        self.isInitialized = False
        super(MyStructuresPanel, self).__init__(**kwargs)

    def ApplyAttributes(self, attributes):
        self.serviceChangedTimestamp = gametime.GetWallclockTimeNow()
        Container.ApplyAttributes(self, attributes)
        self.filterContController = attributes.filterContController
        self.allStructuresProfileController = attributes.allStructuresProfileController
        self.structureBrowserController = attributes.structureBrowserController
        self.ChangeSignalConnection(connect=True)

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.structureBrowserController.on_profile_selected, self.OnProfileSelected),
         (self.allStructuresProfileController.on_profile_saved, self.OnProfileAssigned),
         (self.allStructuresProfileController.on_profile_assigned, self.OnProfileAssigned),
         (self.filterContController.on_text_filter_changed, self.OnTextFilterChanged),
         (self.filterContController.on_lower_power_filter_changed, self.OnLowerPowerChanged),
         (self.filterContController.structureTypeFilterController.on_filter_changed, self.OnStructuresChanged),
         (self.filterContController.serviceFilterController.on_filter_changed, self.OnServiceSettingsChanged)]
        ChangeSignalConnect(signalAndCallback, connect)

    def OnTabSelect(self):
        self.structureBrowserController.SetTabSelected(self.TAB_ID)
        self.LoadPanel()

    def LoadPanel(self):
        if self.isInitialized:
            self.UpdateScroll()
            return
        self.topPanel = Container(name='topPanel', parent=self, align=uiconst.TOTOP, height=20, padding=(0, 6, 0, 6))
        self.profileNameLabel = EveLabelLarge(text='', parent=self.topPanel, state=uiconst.UI_DISABLED, align=uiconst.TOPLEFT, top=2)
        self.comboCont = FilterContMyStructures(name='filterContMyStructures', parent=self, filterContController=self.filterContController, padBottom=8)
        self.scroll = Scroll(parent=self, id='MyStructuresScroll')
        self.scroll.sr.fixedColumns = StructureEntryMyCorp.GetFixedColumns()
        self.scroll.OnSelectionChange = self.OnScrollSelectionChange
        self.scroll.GetTabStops = self.GetTabStops
        self.UpdateScroll()
        self.isInitialized = True

    def GetTabStops(self, headertabs, idx = None):
        decoClass = self.GetDecoClass()
        return TabFinder().GetTabStops(self.scroll.sr.nodes, headertabs, decoClass, idx=idx)

    def LoadProfile(self, profileID):
        self.UpdateScroll()

    def UpdateScroll(self):
        if self.structureBrowserController.GetSelectedTab() != self.TAB_ID:
            return
        self.SetLabelProfileName()
        decoClass = self.GetDecoClass()
        scrollList, somethingFilteredOut = self.GetScrollList(decoClass=decoClass)
        if somethingFilteredOut:
            noContentHint = GetByLabel('UI/Structures/Browser/NoStructuresFoundWithFilters')
        else:
            noContentHint = GetByLabel('UI/Structures/Browser/NoStructuresFound')
        structureServicesChecked = self._GetServicesChecked()
        self.scroll.LoadContent(contentList=scrollList, headers=decoClass.GetHeaders(structureServicesChecked), noContentHint=noContentHint)

    def SetLabelProfileName(self):
        currentProfileID = self.structureBrowserController.GetSelectedProfileID()
        c = self.allStructuresProfileController.GetSlimProfileController(currentProfileID)
        if c:
            text = c.GetProfileName()
            displayTopPanel = True
        else:
            text = ''
            displayTopPanel = False
        self.profileNameLabel.text = text
        self.topPanel.display = displayTopPanel

    def IsFilteredOut(self, structureController):
        currentProfileID = self.structureBrowserController.GetSelectedProfileID()
        if currentProfileID != browserUIConst.ALL_PROFILES and currentProfileID != structureController.GetProfileID():
            return True
        if self._IsFilteredOutByPower(structureController):
            return True
        if self._IsFilteredOutByStructureType(structureController):
            return True
        if self._IsFilteredOutByServices(structureController):
            return True
        if self._IsFilteredOutByText(structureController):
            return True
        return False

    def _IsFilteredOutByPower(self, structureController):
        if not self.filterContController.OnlyShowLowPower():
            return False
        return not structureController.IsLowPower()

    def _IsFilteredOutByStructureType(self, structureController):
        if not self.filterContController.structureTypeFilterController.IsActive():
            return False
        groupingsChecked = self.filterContController.GetStructureTypesChecked()
        structureTypeID = structureController.GetTypeID()
        if structureTypeID in groupingsChecked:
            return False
        else:
            return True

    def _IsFilteredOutByText(self, structureController):
        filterText = self.filterContController.GetTextFilter()
        return IsFilteredOutByText(structureController, filterText)

    def _IsFilteredOutByServices(self, structureController):
        filterContController = self.filterContController
        return IsFilteredOutByServices(structureController, filterContController)

    def GetScrollList(self, decoClass):
        scrollList = []
        structureControllers = self.structureBrowserController.GetMyStructures()
        somethingFilteredOut = False
        structureServicesChecked = self._GetServicesChecked()
        for controller in structureControllers:
            if self.IsFilteredOut(controller):
                somethingFilteredOut = True
                continue
            slimProfileController = self.allStructuresProfileController.GetSlimProfileController(controller.GetProfileID())
            node = Bunch(controller=controller, decoClass=decoClass, columnSortValues=decoClass.GetColumnSortValues(controller, slimProfileController, structureServicesChecked), charIndex=controller.GetName(), slimProfileController=slimProfileController, GetSortValue=decoClass.GetSortValue, structureServicesChecked=structureServicesChecked)
            scrollList.append(node)

        return (scrollList, somethingFilteredOut)

    def _GetServicesChecked(self):
        if self.filterContController.AreServiceFiltersDisbled():
            structureServicesChecked = browserUIConst.ALL_SERVICES
        else:
            structureServicesChecked = self.filterContController.GetServicesChecked()
        return structureServicesChecked

    def GetDecoClass(self):
        allProfilesVisible = self.structureBrowserController.GetSelectedProfileID() == browserUIConst.ALL_PROFILES
        if allProfilesVisible:
            return StructureEntryMyCorpAllProfiles
        else:
            return StructureEntryMyCorp

    def OnScrollSelectionChange(self, entries):
        pass

    def OnServiceCombo(self, *args):
        self.UpdateScroll()

    def OnTextFilterChanged(self):
        self.UpdateScroll()

    def OnLowerPowerChanged(self):
        self.UpdateScroll()

    def OnStructureTypeChanged(self):
        self.UpdateScroll()

    def OnStructuresChanged(self, *args):
        self.UpdateScroll()

    def OnServiceSettingsChanged(self, *args):
        uthread.new(self.OnServiceSettingsChanged_thread)

    def OnServiceSettingsChanged_thread(self):
        DELAY = 500
        recentlyLoaded = gametime.GetTimeDiff(self.serviceChangedTimestamp, gametime.GetWallclockTimeNow()) / const.MSEC < DELAY
        if recentlyLoaded:
            self.serviceChangedTimer = AutoTimer(DELAY, self.DoUpdateScroll)
        else:
            self.DoUpdateScroll()

    def DoUpdateScroll(self):
        self.serviceChangedTimestamp = gametime.GetWallclockTimeNow()
        self.serviceChangedTimer = None
        self.UpdateScroll()

    def OnProfileSelected(self, profileID):
        if not self or self.destroyed:
            return
        if self.structureBrowserController.GetSelectedTab() == self.TAB_ID:
            self.LoadProfile(profileID)

    def OnProfileAssigned(self, profileID):
        self.UpdateScroll()

    def Close(self):
        with EatSignalChangingErrors(errorMsg='MyStructuresPanel'):
            self.ChangeSignalConnection(connect=False)
        self.filterContController = None
        self.allStructuresProfileController = None
        self.structureBrowserController = None
        Container.Close(self)
