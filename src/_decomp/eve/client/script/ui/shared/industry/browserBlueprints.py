#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\industry\browserBlueprints.py
from collections import defaultdict
import gametime
from carbonui.control.combo import Combo
from carbonui.primitives.container import Container
from carbonui.util.bunch import Bunch
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.client.script.ui.control.utilMenu import UtilMenu
from eve.client.script.ui.quickFilter import QuickFilterEdit
from eve.client.script.ui.shared.industry.viewModeButtons import ViewModeButtons
from eve.client.script.ui.shared.industry.blueprintEntry import BlueprintEntry
from eve.common.lib import appConst as const
import evetypes
import industry
import localization
import carbonui.const as uiconst
import blue
import telemetry
from carbonui.uicore import uicore
from eveexceptions import UserError
FACILITY_CURRENT = -1
FACILITY_NONE = -2
FACILITY_ALL = -3
FACILITY_NO_SELECTION = -4
FACILITY_NOT_SPECIFIC = (FACILITY_NONE, FACILITY_ALL, FACILITY_NO_SELECTION)
OWNER_ME = 1
OWNER_CORP = 2
BLUEPRINTS_ALL = 1
BLUEPRINTS_ORIGINAL = 2
BLUEPRINTS_COPY = 3
BLUEPRINTS_ANCIENT_RELICS = 4
BLUEPRINTS_FORMULAS = 5
GROUPS_ALL = (None, None)

class BrowserBlueprints(Container):
    default_name = 'BrowserBlueprints'
    default_isCorp = False
    __notifyevents__ = ['OnBlueprintReload', 'OnIndustryJobClient', 'OnSessionChanged']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.callback = attributes.callback
        self.isInitialized = False
        self.jobData = None
        self.solarsystemIDbyFacilityID = {}
        self.maxBlueprintCount = sm.GetService('blueprintSvc').blueprintLimit
        self.updateScrollTimestamp = None

    def SetFocus(self, *args):
        if self.isInitialized:
            uicore.registry.SetFocus(self.scroll)

    def UpdateSelectedEntry(self):
        if self.jobData:
            self.OnActivitySelected(self.jobData.blueprintID, self.jobData.activityID)

    def OnNewJobData(self, jobData):
        self.jobData = jobData
        if self.isInitialized:
            self.UpdateSelectedEntry()

    def OnTabSelect(self):
        if self.isInitialized:
            self.UpdateOwnerCombo()
            self.UpdateScroll()
            return
        self.isInitialized = True
        self.topPanel = Container(name='topPanel', parent=self, align=uiconst.TOTOP, height=32, padding=(0, 6, 0, 6))
        self.scroll = Scroll(parent=self, id='BlueprintBrowser', discardNonVisibleNodes=True)
        self.scroll.OnSelectionChange = self.OnScrollSelectionChange
        self.scroll.OnKeyDown = self.OnScrollKeyDown
        self.scroll.OnChar = self.OnScrollChar
        utilMenuCont = Container(align=uiconst.TOLEFT, parent=self.topPanel, width=20)
        UtilMenu(menuAlign=uiconst.BOTTOMLEFT, parent=utilMenuCont, align=uiconst.CENTERLEFT, GetUtilMenu=self.GetSettingsMenu, texturePath='res:/UI/Texture/SettingsCogwheel.png', width=16, height=16, iconSize=18)
        self.ownerCombo = Combo(name='ownerCombo', parent=self.topPanel, align=uiconst.TOLEFT, callback=self.OnOwnerCombo, width=126)
        self.facilityCombo = Combo(name='facilityCombo', parent=self.topPanel, align=uiconst.TOLEFT, callback=self.OnFacilityCombo, width=200, padLeft=5)
        self.invLocationCombo = Combo(name='invLocationCombo', parent=self.topPanel, align=uiconst.TOLEFT, callback=self.OnInvLocationCombo, padLeft=5, width=180, settingsID='IndustryBlueprintBrowserInvLocation')
        self.blueprintTypeCombo = Combo(name='blueprintTypeCombo', parent=self.topPanel, align=uiconst.TOLEFT, callback=self.OnBlueprintTypeCombo, padLeft=5, width=124, settingsID='IndustryBlueprintBrowserType', options=self.GetBlueprintTypeComboOptions())
        self.categoryGroupCombo = Combo(name='categoryGroupCombo ', parent=self.topPanel, align=uiconst.TOLEFT, callback=self.OnCategoryGroupCombo, padLeft=5, width=104)
        self.viewModeButtons = ViewModeButtons(parent=self.topPanel, align=uiconst.TORIGHT, controller=self, settingsID='IndustryBlueprintBrowserViewMode')
        self.filterEdit = QuickFilterEdit(name='searchField', parent=self.topPanel, maxLength=64, align=uiconst.TORIGHT, padRight=4, isTypeField=True, width=144)
        self.filterEdit.ReloadFunction = self.OnFilterEdit
        self.UpdateOwnerCombo()
        self.UpdateBlueprintTypeCombo()
        self.UpdateScroll()

    def GetSettingsMenu(self, menuParent):
        (menuParent.AddCheckBox(text=localization.GetByLabel('UI/Industry/ShowBlueprintsInUse'), checked=self.IsBlueprintsInUseShown(), callback=self.ToggleShowBlueprintsInUse),)
        menuParent.AddCheckBox(text=localization.GetByLabel('UI/Industry/ShowAvailableOnly'), checked=self.IsAvailableBlueprintsOnlyShown(), callback=self.ToggleShowAvailableBlueprintsOnly)

    def ToggleShowBlueprintsInUse(self):
        settings.user.ui.Set('industryShowBlueprintsInUse', not self.IsBlueprintsInUseShown())
        self.UpdateScroll()

    def ToggleShowAvailableBlueprintsOnly(self):
        settings.user.ui.Set('industryShowAvailableBlueprintsOnly', not self.IsAvailableBlueprintsOnlyShown())
        self.UpdateScroll()

    @telemetry.ZONE_METHOD
    def OnActivitySelected(self, itemID, activityID = None):
        if not self.isInitialized or activityID is None:
            return
        for node in self.scroll.GetNodes():
            node.selected = node.bpData.blueprintID == itemID
            self.scroll.UpdateSelection(node)
            if node.panel is None:
                continue
            node.panel.OnActivitySelected(itemID, activityID)

    def OnBlueprintReload(self, ownerID):
        if self.destroyed or not self.isInitialized:
            return
        if self.isInitialized and self.display:
            currentOwnerID = session.corpid if self.IsCorpSelected() else session.charid
            if currentOwnerID == ownerID:
                self.UpdateScroll()

    @telemetry.ZONE_METHOD
    def OnIndustryJobClient(self, jobID = None, blueprintID = None, status = None, **kwargs):
        if not self.isInitialized:
            return
        for node in self.scroll.GetNodes():
            if node.bpData.blueprintID == blueprintID:
                if status < industry.STATUS_COMPLETED:
                    node.bpData.jobID = jobID
                else:
                    node.bpData.jobID = None
                if node.panel:
                    node.panel.OnJobStateChanged(status)

    def OnSessionChanged(self, isremote, session, change):
        if set(change.keys()) & {'stationid', 'structureid', 'solarsystemid2'}:
            self.UpdateScroll()

    def OnFilterEdit(self):
        self.UpdateScroll()

    def OnViewModeChanged(self, viewMode):
        self.UpdateScroll()

    def UpdateFacilityCombo(self, blueprintCountByfacilityID, suppressCollections):
        defaultFacilityID = self.GetDefaultFacilitySelection()
        if defaultFacilityID not in FACILITY_NOT_SPECIFIC:
            blueprintCountByfacilityID.setdefault(defaultFacilityID, 0)
        suppressCollections = suppressCollections or sum(blueprintCountByfacilityID.values()) >= self.maxBlueprintCount
        if not suppressCollections:
            options = [(localization.GetByLabel('UI/Industry/AllFacilities'), FACILITY_ALL)]
        elif defaultFacilityID in FACILITY_NOT_SPECIFIC:
            options = [(' - ', FACILITY_NO_SELECTION)]
        else:
            options = []
        facilitySvc = sm.GetService('facilitySvc')
        for facilityID, blueprintCount in blueprintCountByfacilityID.iteritems():
            if facilityID is None and not suppressCollections:
                label = localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/NonFacilityLocationsNumberOfBlueprints', blueprints=blueprintCount)
                options.append((label, FACILITY_NONE))
            elif facilityID is not None:
                try:
                    facility = facilitySvc.GetFacility(facilityID)
                    self.solarsystemIDbyFacilityID[facilityID] = facility.solarSystemID
                    options.append((self.GetFacilityLabel(facility, blueprintCount), facilityID))
                except UserError:
                    pass

        options = sorted(options, key=self._GetFacilitySortKey)
        self.facilityCombo.LoadOptions(options, select=defaultFacilityID)

    def GetDefaultFacilitySelection(self):
        if self.IsCorpSelected():
            facilityID = settings.user.ui.Get('BrowserBlueprintsFacilitiesCorp', FACILITY_CURRENT)
        else:
            facilityID = settings.user.ui.Get('BrowserBlueprintsFacilities', FACILITY_CURRENT)
        if isinstance(facilityID, tuple) or facilityID is None:
            facilityID = FACILITY_CURRENT
        if facilityID == FACILITY_CURRENT:
            facilityID = session.stationid or session.structureid
        return facilityID

    def GetDefaultInvLocationSelection(self):
        if self.IsCorpSelected():
            return settings.user.ui.Get('BrowserBlueprintsInvLocationCorp', None)
        else:
            return settings.user.ui.Get('BrowserBlueprintsInvLocation', None)

    def _GetFacilitySortKey(self, option):
        _, facilityID = option
        if facilityID in FACILITY_NOT_SPECIFIC:
            return facilityID
        if facilityID == session.stationid:
            return FACILITY_CURRENT
        solarsystemID = self.solarsystemIDbyFacilityID[facilityID]
        return self.GetJumpsTo(solarsystemID)

    def GetFacilityLabel(self, facility, blueprintCount):
        if session.stationid and facility.facilityID == session.stationid or session.structureid and facility.facilityID == session.structureid:
            return localization.GetByLabel('UI/Industry/CurrentStation')
        return localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/LocationNumberOfBlueprintsNumberOfJumps', locationName=facility.GetName(), blueprints=blueprintCount, jumps=facility.distance)

    def GetJumpsTo(self, solarsystemID):
        return sm.GetService('clientPathfinderService').GetJumpCountFromCurrent(solarsystemID) or 0

    def OnFacilityCombo(self, combo, key, value):
        if value == session.stationid:
            value = FACILITY_CURRENT
        if self.IsCorpSelected():
            settings.user.ui.Set('BrowserBlueprintsFacilitiesCorp', value)
        else:
            settings.user.ui.Set('BrowserBlueprintsFacilities', value)
        self.UpdateScroll()

    def GetInvLocations(self, blueprints):
        locations = {}
        for bpData in blueprints:
            flagID = bpData.flagID
            if self.IsContainerFlag(flagID):
                flagID = const.flagHangar
            locations[bpData.locationID, flagID] = bpData

        locations = sorted(locations.items(), cmp=self._CompareLocations)
        return locations

    def _CompareLocations(self, location1, location2):
        (locationID1, flagID1), bpData1 = location1
        (locationID2, flagID2), bpData2 = location2
        idx1 = const.corpDivisionsByFlag.get(flagID1)
        idx2 = const.corpDivisionsByFlag.get(flagID2)
        if idx1 is None and idx2 is None:
            return cmp(bpData1.GetLocationName(), bpData2.GetLocationName())
        elif idx1 is None and idx2 is not None:
            return 1
        elif idx1 is not None and idx2 is None:
            return -1
        else:
            return cmp(idx1, idx2)

    def GetSelectedFacilityID(self):
        facilityID = self.facilityCombo.GetValue()
        if facilityID == FACILITY_CURRENT:
            return session.stationid
        return facilityID

    def UpdateInvLocationCombo(self, blueprints):
        facilityID = self.GetSelectedFacilityID()
        options = []
        if facilityID and facilityID not in FACILITY_NOT_SPECIFIC:
            locations = self.GetInvLocations((b for b in blueprints if b.facilityID == facilityID))
            options = sorted([ (bpData.GetLocationName(),
             key,
             None,
             bpData.location.GetIcon()) for key, bpData in locations ])
        if len(options) != 1:
            options.insert(0, (localization.GetByLabel('UI/Industry/AllInventoryLocations'), (None, None)))
        selection = self.GetDefaultInvLocationSelection()
        if selection not in (o[1] for o in options):
            selection = options[0][1]
        self.invLocationCombo.LoadOptions(options, select=selection)

    def OnOwnerCombo(self, combo, key, value):
        settings.user.ui.Set('IndustryBlueprintBrowserOwner', value)
        self.UpdateBlueprintTypeCombo()
        self.UpdateScroll()

    def OnInvLocationCombo(self, combo, key, value):
        if self.IsCorpSelected():
            settings.user.ui.Set('BrowserBlueprintsInvLocationCorp', value)
        else:
            settings.user.ui.Set('BrowserBlueprintsInvLocation', value)
        self.UpdateScroll()

    def UpdateBlueprintTypeCombo(self):
        value = self.GetDefaultBlueprintTypeSelection()
        self.blueprintTypeCombo.SelectItemByValue(value)

    def GetDefaultBlueprintTypeSelection(self):
        if self.IsCorpSelected():
            return settings.user.ui.Get('BrowserBlueprintsBlueprintTypeCorp', BLUEPRINTS_ALL)
        else:
            return settings.user.ui.Get('BrowserBlueprintsBlueprintType', BLUEPRINTS_ALL)

    def OnBlueprintTypeCombo(self, combo, key, value):
        if self.IsCorpSelected():
            settings.user.ui.Set('BrowserBlueprintsBlueprintTypeCorp', value)
        else:
            settings.user.ui.Set('BrowserBlueprintsBlueprintType', value)
        self.UpdateScroll()

    def GetBlueprintTypeComboOptions(self):
        options = ((localization.GetByLabel('UI/Industry/AllBlueprints'), BLUEPRINTS_ALL),
         (localization.GetByLabel('UI/Industry/Originals'),
          BLUEPRINTS_ORIGINAL,
          None,
          'res:/UI/Texture/icons/bpo.png'),
         (localization.GetByLabel('UI/Industry/Copies'),
          BLUEPRINTS_COPY,
          None,
          'res:/UI/Texture/icons/bpc.png'),
         (localization.GetByLabel('UI/Industry/AncientRelics'),
          BLUEPRINTS_ANCIENT_RELICS,
          None,
          'res:/UI/Texture/icons/relic.png'),
         (localization.GetByLabel('UI/Industry/ReactionFormulas'),
          BLUEPRINTS_FORMULAS,
          None,
          'res:/UI/Texture/icons/reaction.png'))
        return options

    def OnCategoryGroupCombo(self, combo, key, value):
        if self.IsCorpSelected():
            settings.user.ui.Set('BrowserBlueprintsCategoryGroupCorp', value)
        else:
            settings.user.ui.Set('BrowserBlueprintsCategoryGroup', value)
        self.UpdateScroll()

    def GetDefaultCategoryGroup(self):
        if self.IsCorpSelected():
            return settings.user.ui.Get('BrowserBlueprintsCategoryGroupCorp', GROUPS_ALL)
        else:
            return settings.user.ui.Get('BrowserBlueprintsCategoryGroup', GROUPS_ALL)

    def UpdateCategoryGroupCombo(self, blueprints):
        groupsByCategories = self.GetGroupsByCategories(blueprints)
        options = [(localization.GetByLabel('UI/Industry/AllGroups'), GROUPS_ALL)]
        for (categoryName, categoryID), groups in groupsByCategories:
            options.append((categoryName, (categoryID, None)))
            for groupName, groupID in groups:
                options.append((groupName,
                 (categoryID, groupID),
                 '',
                 None,
                 1))

        self.categoryGroupCombo.LoadOptions(options, select=self.GetDefaultCategoryGroup())

    @telemetry.ZONE_METHOD
    def GetGroupsByCategories(self, blueprints):
        ids = defaultdict(set)
        uniqueBluprintTypes = set()
        for bpData in blueprints:
            typeID = bpData.GetProductOrBlueprintTypeID()
            if typeID in uniqueBluprintTypes:
                continue
            uniqueBluprintTypes.add(typeID)
            groupAndCategory = bpData.GetProductGroupAndCategory()
            ids[groupAndCategory.categoryName, groupAndCategory.categoryID].add((groupAndCategory.groupName, groupAndCategory.groupID))

        ret = []
        for category, groups in ids.iteritems():
            ret.append((category, list(groups)))

        ret.sort()
        for category, groups in ret:
            groups.sort()

        return ret

    def IsCorpSelected(self):
        return self.ownerCombo.GetValue() == OWNER_CORP

    def UpdateScroll(self):
        if self.IsHidden() or self.destroyed:
            return None
        currentUpdateTimestamp = gametime.GetWallclockTime()
        self.updateScrollTimestamp = currentUpdateTimestamp
        self.scroll.ShowLoading()
        facilityID = self.GetDefaultFacilitySelection()
        blueprints, facilities = self.GetBlueprintsData(facilityID)
        if not self.IsLatestUpdateScroll(currentUpdateTimestamp):
            return None
        bpCountLimitReached = facilityID in FACILITY_NOT_SPECIFIC and len(blueprints) == 0 and len(facilities) != 0
        self.UpdateFacilityCombo(facilities, bpCountLimitReached)
        self.UpdateInvLocationCombo(blueprints)
        if not self.IsLatestUpdateScroll(currentUpdateTimestamp):
            return None
        if not len(blueprints):
            self.scroll.LoadContent(noContentHint=localization.GetByLabel('UI/Industry/NoBlueprintsFound'))
            self.scroll.HideLoading()
            return None
        scrollList = self.GetScrollList(blueprints, facilityID, currentUpdateTimestamp)
        if not self.IsLatestUpdateScroll(currentUpdateTimestamp):
            return None
        if len(scrollList) >= self.maxBlueprintCount:
            ShowQuickMessage(localization.GetByLabel('UI/Industry/MaximumEntryCountReached', count=self.maxBlueprintCount))
        self.scroll.sr.defaultColumnWidth = BlueprintEntry.GetDefaultColumnWidth()
        self.scroll.sr.fixedColumns = BlueprintEntry.GetFixedColumns(self.viewModeButtons.GetViewMode())
        showImpounded = not self.IsAvailableBlueprintsOnlyShown() or facilityID == FACILITY_NONE
        if not self.IsLatestUpdateScroll(currentUpdateTimestamp):
            return None
        self.scroll.LoadContent(contentList=scrollList, headers=BlueprintEntry.GetHeaders(showFacility=facilityID == FACILITY_ALL, showLocation=self.invLocationCombo.GetValue() == (None, None), showImpounded=showImpounded), noContentHint=localization.GetByLabel('UI/Industry/NoBlueprintsFound'))
        self.scroll.HideLoading()
        self.UpdateSelectedEntry()

    def IsLatestUpdateScroll(self, timestamp):
        return self.updateScrollTimestamp == timestamp

    @telemetry.ZONE_METHOD
    def GetFilteredBlueprints(self, blueprints, facilityID):
        jumpsCache = {}
        jumpsAndBlueprints = []
        for bpData in blueprints:
            if bpData.facilityID is None and facilityID != FACILITY_NONE:
                continue
            elif facilityID not in (bpData.facilityID if bpData.facilityID else FACILITY_NONE, FACILITY_ALL):
                continue
            if self.IsFilteredOut(bpData):
                continue
            jumpsAndBlueprints.append((jumpsCache.setdefault(bpData.facilityID, bpData.GetDistance()), bpData))
            blue.pyos.BeNice()

        self.UpdateCategoryGroupCombo([ bpData for _, bpData in jumpsAndBlueprints ])
        categoryID, groupID = self.categoryGroupCombo.GetValue()
        if (categoryID, groupID) == GROUPS_ALL:
            return jumpsAndBlueprints
        ret = []
        for jumps, bpData in jumpsAndBlueprints:
            typeID = bpData.GetProductOrBlueprintTypeID()
            if groupID:
                if evetypes.GetGroupID(typeID) == groupID:
                    ret.append((jumps, bpData))
            elif evetypes.GetCategoryID(typeID) == categoryID:
                ret.append((jumps, bpData))

        return ret

    @telemetry.ZONE_METHOD
    def GetScrollList(self, blueprints, facilityID, currentUpdateTimestamp):
        showFacility = facilityID == FACILITY_ALL
        showLocation = self.invLocationCombo.GetValue() == (None, None)
        scrollList = []
        for jumps, bpData in self.GetFilteredBlueprints(blueprints, facilityID):
            if not self.IsLatestUpdateScroll(currentUpdateTimestamp):
                return []
            node = Bunch(bpData=bpData, decoClass=BlueprintEntry, sortValues=BlueprintEntry.GetColumnSortValues(bpData, jumps, showFacility, showLocation), viewMode=self.viewModeButtons.GetViewMode(), jumps=jumps, activityCallback=self.SelectActivity, showFacility=showFacility, showLocation=showLocation, item=bpData.GetItem(), charIndex=bpData.GetLabel(), name=u'BlueprintEntry_{}'.format(bpData.blueprintTypeID))
            scrollList.append(node)
            blue.pyos.BeNice()

        return scrollList

    def GetBlueprintsData(self, facilityID):
        facilityID = facilityID if facilityID > 0 else None
        if self.IsCorpSelected():
            return sm.GetService('blueprintSvc').GetCorporationBlueprints(facilityID)
        else:
            return sm.GetService('blueprintSvc').GetCharacterBlueprints(facilityID)

    def IsFilteredOut(self, bpData):
        filterText = self.filterEdit.GetValue().strip().lower()
        if filterText:
            productTypeObj = bpData.GetProductGroupAndCategory()
            text = bpData.GetName()
            if bpData.facility:
                text += bpData.GetFacilityName()
            text += bpData.GetLocationName() + productTypeObj.groupName + productTypeObj.categoryName
            if text.lower().find(filterText) == -1:
                return True
        locationID, flagID = self.invLocationCombo.GetValue()
        if locationID:
            if bpData.locationID != locationID:
                return True
            if bpData.flagID != flagID and not self.IsContainerFlag(bpData.flagID):
                return True
        bpType = self.blueprintTypeCombo.GetValue()
        if bpType != BLUEPRINTS_ALL:
            if bpType in (BLUEPRINTS_ORIGINAL, BLUEPRINTS_COPY):
                if bpData.IsReactionBlueprint() or bpData.IsAncientRelic():
                    return True
                if bpData.original != (bpType == BLUEPRINTS_ORIGINAL):
                    return True
            elif bpType == BLUEPRINTS_FORMULAS:
                if not bpData.IsReactionBlueprint():
                    return True
            elif bpType == BLUEPRINTS_ANCIENT_RELICS:
                if not bpData.IsAncientRelic():
                    return True
        if not self.IsBlueprintsInUseShown():
            if bpData.jobID is not None:
                return True
        if self.IsAvailableBlueprintsOnlyShown() and bpData.IsImpounded():
            return True
        return False

    def IsBlueprintsInUseShown(self):
        return settings.user.ui.Get('industryShowBlueprintsInUse', True)

    def IsAvailableBlueprintsOnlyShown(self):
        return settings.user.ui.Get('industryShowAvailableBlueprintsOnly', True)

    def IsContainerFlag(self, flagID):
        return flagID in (const.flagLocked, const.flagUnlocked)

    def OnScrollSelectionChange(self, entries):
        entry = entries[0].bpData
        if uicore.uilib.Key(uiconst.VK_SHIFT) and uicore.uilib.Key(uiconst.VK_DOWN):
            entry = entries[-1].bpData
        self.SelectActivity(entry)

    def OnScrollKeyDown(self, key, flag):
        Scroll.OnKeyDown(self.scroll, key, flag)
        if key in (uiconst.VK_LEFT, uiconst.VK_RIGHT):
            sm.ScatterEvent('OnIndustryLeftOrRightKey', key)

    def OnScrollChar(self, key, flag):
        if key >= uiconst.VK_0 and key <= uiconst.VK_9 or key == uiconst.VK_BACK:
            sm.ScatterEvent('OnBlueprintBrowserNumericInput', key, flag)

    def SelectActivity(self, bpData, activityID = None):
        self.callback(bpData, activityID)

    def UpdateOwnerCombo(self):
        options = [(localization.GetByLabel('UI/Industry/OwnedByMe'), OWNER_ME)]
        if sm.GetService('blueprintSvc').CanSeeCorpBlueprints():
            options.append((localization.GetByLabel('UI/Industry/OwnedByCorp'),
             OWNER_CORP,
             None,
             'res:/UI/Texture/classes/Industry/iconCorp.png'))
        select = settings.user.ui.Get('IndustryBlueprintBrowserOwner', OWNER_ME)
        self.ownerCombo.LoadOptions(options, select=select)
