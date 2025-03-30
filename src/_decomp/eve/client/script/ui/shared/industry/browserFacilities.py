#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\industry\browserFacilities.py
from carbonui.control.combo import Combo
from carbonui.primitives.container import Container
from carbonui.util.bunch import Bunch
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.quickFilter import QuickFilterEdit
from eve.client.script.ui.shared.industry import industryUIConst
from eve.client.script.ui.shared.industry.industryUIConst import ACTIVITY_NAMES
from eve.client.script.ui.shared.industry.facilityEntry import FacilityEntry
from eve.client.script.ui.shared.industry.viewModeButtons import ViewModeButtons
import industry
import localization
import carbonui.const as uiconst
import blue
from eve.common.script.sys import idCheckers
OWNER_ANY = 1
OWNER_NPC = 2
OWNER_CORP = 3
RANGE_MAX_SKILL = -2
RANGE_REGION = -1
RANGE_OPTIONS = [('UI/Generic/CurrentSystem', 0),
 ('UI/Industry/RangeWithin5Jumps', 5),
 ('UI/Industry/RangeWithin10Jumps', 10),
 ('UI/Generic/CurrentRegion', RANGE_REGION),
 ('UI/Industry/RangeMaxSkill', RANGE_MAX_SKILL)]

class BrowserFacilities(Container):
    default_name = 'BrowserFacilities'
    __notifyevents__ = ['OnFacilitiesReloaded']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.callback = attributes.callback
        self.isInitialized = False

    def _OnClose(self, *args):
        sm.UnregisterNotify(self)

    def OnTabSelect(self):
        if self.isInitialized:
            self.UpdateScroll()
            return
        self.isInitialized = True
        self.topPanel = Container(name='topPanel', parent=self, align=uiconst.TOTOP, height=32, padding=(0, 6, 0, 6))
        self.scroll = Scroll(parent=self, id='InstallationBrowser')
        self.scroll.OnSelectionChange = self.OnScrollSelectionChange
        self.ownerCombo = Combo(name='ownerCombo', parent=self.topPanel, align=uiconst.TOLEFT, callback=self.OnOwnerCombo, options=self.GetOwnerOptions(), select=settings.user.ui.Get('BrowserFacilitiesOwner', 0), width=120, padRight=4)
        self.activityCombo = Combo(name='activityCombo', parent=self.topPanel, align=uiconst.TOLEFT, callback=self.OnActivityCombo, options=self.GetActivityOptions(), select=settings.user.ui.Get('BrowserFacilitiesActivity', 0), width=120, padRight=4, maxVisibleEntries=7)
        self.rangeCombo = Combo(name='rangeCombo', parent=self.topPanel, align=uiconst.TOLEFT, callback=self.OnRangeCombo, options=self.GetRangeOptions(), select=settings.user.ui.Get('BrowserFacilitiesRange', 0), width=140, padRight=4)
        self.viewModeButtons = ViewModeButtons(parent=self.topPanel, align=uiconst.TORIGHT, controller=self, settingsID='IndustryBlueprintBrowserViewMode')
        self.filterEdit = QuickFilterEdit(name='searchField', parent=self.topPanel, maxLength=64, align=uiconst.TORIGHT, OnClearFilter=self.OnFilterEditCleared, padRight=4, width=144)
        self.filterEdit.ReloadFunction = self.OnFilterEdit
        self.UpdateScroll()

    def OnFacilitiesReloaded(self, *args):
        if self.isInitialized and self.display:
            self.UpdateScroll()

    def OnScrollSelectionChange(self, entries, activityID = None):
        self.callback(entries[0].facilityData)

    def OnFilterEdit(self):
        self.UpdateScroll()

    def OnFilterEditCleared(self):
        self.UpdateScroll()

    def UpdateScroll(self):
        self.scroll.ShowLoading()
        blue.pyos.synchro.Yield()
        installations = self.GetInstallationData()
        scrollList = self.GetScrollList(installations)
        self.scroll.sr.defaultColumnWidth = FacilityEntry.GetDefaultColumnWidth()
        self.scroll.sr.fixedColumns = FacilityEntry.GetFixedColumns(self.viewModeButtons.GetViewMode())
        self.scroll.LoadContent(contentList=scrollList, headers=FacilityEntry.GetHeaders(showTax=self.activityCombo.GetValue() in industry.ACTIVITIES), noContentHint=localization.GetByLabel('UI/Industry/NoFacilitiesFound'))
        self.scroll.HideLoading()

    def GetInstallationData(self):
        installations = sm.GetService('facilitySvc').GetFacilities()
        cfg.evelocations.Prime((facilityData.facilityID for facilityData in installations))
        cfg.eveowners.Prime((facilityData.ownerID for facilityData in installations))
        return installations

    def GetScrollList(self, installations):
        scrollList = []
        if installations:
            sm.GetService('facilitySvc').InitMaxActivityModifiers()
        showTax = self.activityCombo.GetValue() in industry.ACTIVITIES
        for facilityData in installations:
            blue.pyos.BeNice()
            jumps = self.GetJumpsTo(facilityData.solarSystemID)
            if self.IsFilteredOut(facilityData):
                continue
            activityID = self.activityCombo.GetValue()
            node = Bunch(facilityData=facilityData, decoClass=FacilityEntry, sortValues=FacilityEntry.GetColumnSortValues(facilityData, jumps, activityID, showTax), viewMode=self.viewModeButtons.GetViewMode(), jumps=jumps, charIndex=facilityData.GetName(), activityID=activityID)
            scrollList.append(node)

        return scrollList

    def IsFilteredOut(self, facilityData):
        if not facilityData.activities:
            return True
        filterText = self.filterEdit.GetValue().strip().lower()
        if filterText:
            text = facilityData.GetName() + facilityData.GetOwnerName() + facilityData.GetTypeName()
            if text.lower().find(filterText) == -1:
                return True
        activityValue = self.activityCombo.GetValue()
        if activityValue and activityValue not in facilityData.activities:
            return True
        ownerValue = self.ownerCombo.GetValue()
        if ownerValue != OWNER_ANY:
            isCorporation = facilityData.ownerID == session.corpid
            if not isCorporation and ownerValue != OWNER_NPC:
                return True
            if isCorporation and ownerValue != OWNER_CORP:
                return True
        solarSystemID = facilityData.solarSystemID
        if idCheckers.IsWormholeSystem(solarSystemID) and solarSystemID != session.solarsystemid2:
            return True
        rangeValue = self.rangeCombo.GetValue()
        if rangeValue != RANGE_MAX_SKILL:
            if rangeValue == RANGE_REGION and cfg.mapSystemCache.Get(solarSystemID).regionID != session.regionid:
                return True
            if 0 <= rangeValue < self.GetJumpsTo(solarSystemID):
                return True
        return False

    def GetJumpsTo(self, solarsystemID):
        return sm.GetService('clientPathfinderService').GetJumpCountFromCurrent(solarsystemID)

    def OnViewModeChanged(self, viewMode):
        self.UpdateScroll()

    def OnRangeCombo(self, combo, key, value):
        settings.user.ui.Set('BrowserFacilitiesRange', value)
        self.UpdateScroll()

    def GetRangeOptions(self):
        return [ (localization.GetByLabel(label), value) for label, value in RANGE_OPTIONS ]

    def OnActivityCombo(self, combo, key, value):
        settings.user.ui.Set('BrowserFacilitiesActivity', value)
        self.UpdateScroll()

    def GetActivityOptions(self):
        ret = [ (localization.GetByLabel(ACTIVITY_NAMES[activityID]),
         activityID,
         None,
         industryUIConst.ACTIVITY_ICONS_SMALL[activityID]) for activityID in industry.ACTIVITIES ]
        ret.insert(0, (localization.GetByLabel('UI/Industry/AllActivities'), 0))
        return ret

    def GetOwnerOptions(self):
        return [(localization.GetByLabel('UI/Industry/AllFacilities'), OWNER_ANY), (localization.GetByLabel('UI/Industry/PublicFacilities'),
          OWNER_NPC,
          None,
          'res:/UI/Texture/Classes/Inventory/readOnly.png'), (localization.GetByLabel('UI/Industry/CorpOwnedFacilities'),
          OWNER_CORP,
          None,
          'res:/UI/Texture/Classes/Industry/iconCorp.png')]

    def OnOwnerCombo(self, combo, key, value):
        settings.user.ui.Set('BrowserFacilitiesOwner', value)
        self.UpdateScroll()
