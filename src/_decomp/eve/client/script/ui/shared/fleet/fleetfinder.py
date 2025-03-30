#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fleet\fleetfinder.py
from carbonui.control.checkbox import Checkbox
from carbonui.control.combo import Combo
from carbonui.control.scrollContainer import ScrollContainer
from eve.client.script.ui.control.entries.util import GetFromClass
from carbonui.control.tabGroup import TabGroup
from eve.client.script.ui.shared.fleet.fleetFinderEntry import FleetFinderEntry
from eve.common.lib.appConst import contactGoodStanding, contactHighStanding
from carbon.common.script.util.commonutils import GetAttrs
from eve.client.script.ui.control.themeColored import FrameThemeColored
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
from eveexceptions import ExceptionEater
from inventorycommon.const import groupSolarSystem, typeCorporation, typeAlliance, typeFaction
import uthread
import blue
import carbonui.const as uiconst
import evefleet.client
import evefleet
from carbonui.primitives.container import Container
from carbonui.button.group import ButtonGroup
from carbonui.control.button import Button
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from eve.client.script.ui.control.eveLabel import EveLabelMediumBold, EveLabelMedium, EveCaptionMedium
from eve.client.script.ui.control.eveScroll import Scroll
from localization import GetByLabel
PANEL_FLEETFINDER = 'findfleets'
PANEL_ADVERT = 'myadvert'
GETFLEETS_THROTTLETIME = 2000
SIZE_FULLUI = (420, 250)

def GetFleetDetailsEntry(fleet):
    textList = []
    bossText = GetByLabel('UI/Fleet/FleetRegistry/AdvertDetails/Boss', boss=fleet.leader.charID, bossInfoData=('showinfo', 1376, fleet.leader.charID))
    textList.append(bossText)
    if fleet.solarSystemID:
        locationText = GetByLabel('UI/Fleet/FleetRegistry/AdvertDetails/Location', bossLocation=fleet.solarSystemID, locationData=('showinfo', groupSolarSystem, fleet.solarSystemID))
        textList.append(locationText)
    ageText = GetByLabel('UI/Fleet/FleetRegistry/AdvertDetails/Age', fleetAge=blue.os.GetWallclockTime() - fleet.dateCreated)
    textList.append(ageText)
    if fleet.numMembers:
        numMembersText = GetByLabel('UI/Fleet/FleetRegistry/AdvertDetails/MemberCount', memberCount=fleet.numMembers)
        textList.append(numMembersText)
    scopeLines = []
    if evefleet.IsOpenToCorp(fleet):
        scopeLines.append(GetByLabel('UI/Fleet/FleetRegistry/AdvertDetails/CorporationAccessScope', corpName=cfg.eveowners.Get(fleet.leader.corpID).name, corpInfo=('showinfo', typeCorporation, fleet.leader.corpID)))
    if evefleet.IsOpenToAlliance(fleet) and fleet.leader.allianceID:
        scopeLines.append(GetByLabel('UI/Fleet/FleetRegistry/AdvertDetails/AllianceAccessScope', allianceName=cfg.eveowners.Get(fleet.leader.allianceID).name, allianceInfo=('showinfo', typeAlliance, fleet.leader.allianceID)))
    if evefleet.IsOpenToMilitia(fleet) and fleet.leader.warFactionID:
        scopeLines.append(GetByLabel('UI/Fleet/FleetRegistry/AdvertDetails/MilitiaAccessScope', militiaName=cfg.eveowners.Get(fleet.leader.warFactionID).name, militiaInfo=('showinfo', typeFaction, fleet.leader.warFactionID)))
    if fleet.membergroups_minStanding is not None or fleet.membergroups_minSecurity is not None:
        if fleet.membergroups_minStanding is not None:
            if fleet.membergroups_minStanding == contactGoodStanding:
                standing = GetByLabel('UI/Standings/Good')
            elif fleet.membergroups_minStanding == contactHighStanding:
                standing = GetByLabel('UI/Standings/Excellent')
            else:
                standing = fleet.public_minStanding
            if fleet.membergroups_minSecurity is not None:
                scopeLines.append(GetByLabel('UI/Fleet/FleetRegistry/AdvertDetails/MinimumStandingAndSecurity', standing=standing, security=fleet.membergroups_minSecurity))
            else:
                scopeLines.append(GetByLabel('UI/Fleet/FleetRegistry/AdvertDetails/MinimumStanding', standing=standing))
        elif fleet.membergroups_minSecurity is not None:
            scopeLines.append(GetByLabel('UI/Fleet/FleetRegistry/AdvertDetails/MinimumSecurity', security=fleet.membergroups_minSecurity))
    if evefleet.IsOpenToPublic(fleet) or evefleet.IsOpenToAllPublic(fleet):
        if evefleet.IsOpenToPublic(fleet):
            scopeLines.append(GetByLabel('UI/Fleet/FleetRegistry/AdvertDetails/PublicAccessScope'))
        else:
            scopeLines.append(GetByLabel('UI/Agency/Fleetup/Public Access'))
        if fleet.public_minStanding is not None:
            if fleet.public_minStanding == contactGoodStanding:
                standing = GetByLabel('UI/Standings/Good')
            elif fleet.public_minStanding == contactHighStanding:
                standing = GetByLabel('UI/Standings/Excellent')
            else:
                standing = fleet.public_minStanding
            if fleet.public_minSecurity is not None:
                scopeLines.append(GetByLabel('UI/Fleet/FleetRegistry/AdvertDetails/MinimumStandingAndSecurity', standing=standing, security=fleet.public_minSecurity))
            else:
                scopeLines.append(GetByLabel('UI/Fleet/FleetRegistry/AdvertDetails/MinimumStanding', standing=standing))
        elif fleet.public_minSecurity is not None:
            scopeLines.append(GetByLabel('UI/Fleet/FleetRegistry/AdvertDetails/MinimumSecurity', security=fleet.public_minSecurity))
    if not scopeLines:
        scopeLines.append('-')
    scopeLinesText = GetByLabel('UI/Fleet/FleetRegistry/AdvertDetails/Scope', scope='<br><t>'.join(scopeLines))
    textList.append(scopeLinesText)
    if fleet.joinNeedsApproval:
        approvalText = GetByLabel('UI/Fleet/FleetRegistry/AdvertDetails/NeedsApproval')
        textList.append(approvalText)
    text = '<br>'.join(textList)
    return text


class AdvertDraggableIcon(Container):
    isDragObject = True

    def Startup(self, fleet):
        self.fleet = fleet

    def GetDragData(self, *args):
        data = evefleet.client.FleetDragData(fleet_id=self.fleet.fleetID, name=self.fleet.fleetName)
        return [data]


class PanelFleetFinderAndAdvert(Container):

    def ApplyAttributes(self, attributes):
        super(PanelFleetFinderAndAdvert, self).ApplyAttributes(attributes)
        self.tabs = TabGroup(name='fleetfindertabs', parent=self, idx=0)
        self.tabs.AddTab(GetByLabel('UI/Fleet/FleetRegistry/FindFleets'), PanelFleetFinder(parent=self), self, 'findfleets')
        self.tabs.AddTab(GetByLabel('UI/Fleet/FleetRegistry/MyAdvert'), PanelAdvert(parent=self), self, 'myadvert')
        uthread.new(self.tabs.ShowPanelByName, GetByLabel('UI/Fleet/FleetRegistry/FindFleets'))


class PanelAdvert(Container):
    __notifyevents__ = ['OnFleetFinderAdvertChanged']

    def ApplyAttributes(self, attributes):
        super(PanelAdvert, self).ApplyAttributes(attributes)
        sm.RegisterNotify(self)
        self.isLoaded = False
        self.myAdvertButtons = Container(name='myAdvertButtons', parent=self, align=uiconst.TOBOTTOM, height=35)
        self.myAdvertCont = ScrollContainer(name='myAdvertCont', parent=self, align=uiconst.TOALL, alignMode=uiconst.TOTOP)
        tabs = [130, 540]
        self.myAdvertButtonWnd = ButtonGroup(parent=self.myAdvertButtons)
        self.myAdvertButtonWnd.AddButton(GetByLabel('UI/Fleet/FleetWindow/EditAdvert'), sm.GetService('fleet').OpenRegisterFleetWindow, ())
        self.myAdvertButtonWnd.AddButton(GetByLabel('UI/Fleet/FleetWindow/RemoveAdvert'), sm.GetService('fleet').UnregisterFleet, ())
        self.myAdvertCaption = EveCaptionMedium(text='', parent=self.myAdvertCont, align=uiconst.TOTOP, state=uiconst.UI_DISABLED)
        self.myAdvertText = EveLabelMedium(name='myAdvertText', parent=self.myAdvertCont, top=uiconst.defaultPadding, tabs=tabs, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        self.myAdvertDesc = EveLabelMedium(name='myAdvertDesc', parent=self.myAdvertCont, padTop=8, state=uiconst.UI_NORMAL, align=uiconst.TOTOP)
        self.myAdvertButtonWnd_RegisterBtnGroup = ButtonGroup(parent=self.myAdvertButtons)
        self.myAdvertButtonWnd_RegisterBtnGroup.AddButton(GetByLabel('UI/Fleet/FleetWindow/CreateAdvert'), sm.GetService('fleet').OpenRegisterFleetWindow, ())
        self.myAdvertButtonWnd_RegisterBtnGroup.display = False
        self.dragIcon = None

    def LoadPanel(self):
        self.myAdvertText.text = ''
        self.myAdvertButtonWnd.display = False
        self.myAdvertButtonWnd_RegisterBtnGroup.display = False
        if session.fleetid is None:
            caption = GetByLabel('UI/Fleet/FleetRegistry/NotInAFleet')
            self.myAdvertCaption.text = caption
            self.myAdvertText.text = GetByLabel('UI/Fleet/FleetRegistry/NotInAFleetDetailed')
            self.myAdvertDesc.display = False
            return
        fleetAdvert = sm.GetService('fleet').GetCurrentAdvertForMyFleet()
        if fleetAdvert is None:
            caption = GetByLabel('UI/Fleet/FleetRegistry/DoNotHaveAnAdvert')
            self.myAdvertCaption.text = caption
            self.myAdvertText.text = GetByLabel('UI/Fleet/FleetRegistry/DoNotHaveAnAdvertDetailed')
            self.myAdvertDesc.display = False
            self.myAdvertButtonWnd_RegisterBtnGroup.display = True
            if self.dragIcon:
                self.dragIcon.Close()
                self.dragIcon = None
        else:
            self.myAdvertButtonWnd.display = True
            caption = fleetAdvert.fleetName or GetByLabel('UI/Fleet/FleetRegistry/UnnamedFleet')
            self.myAdvertCaption.text = caption
            self.dragIcon = AdvertDraggableIcon(name='theicon', align=uiconst.TOPLEFT, parent=self.myAdvertCont, pos=(uiconst.defaultPadding,
             uiconst.defaultPadding,
             64,
             64), state=uiconst.UI_NORMAL, idx=0)
            self.dragIcon.Startup(fleetAdvert)
            self.dragIcon.hint = GetByLabel('UI/Fleet/FleetRegistry/DragToShareAdvertHint')
            self.myAdvertText.text = GetFleetDetailsEntry(fleetAdvert)
            self.myAdvertDesc.SetText(fleetAdvert.description)

    def OnFleetFinderAdvertChanged(self):
        if self.display:
            self.LoadPanel()


class PanelFleetFinder(Container):
    default_clipChildren = True

    def ApplyAttributes(self, attributes):
        super(PanelFleetFinder, self).ApplyAttributes(attributes)
        self.inited = False
        self.gettingFleets = False
        self.fleets = {}
        self.infoCont = None
        self.ConstructLayout()
        self.inited = True

    def LoadPanel(self):
        if not self.inited:
            return
        if not self.gettingFleets:
            self.GetFleetsClick()

    def GetWndHeight(self):
        return self.height or self.absoluteBottom - self.absoluteTop

    def GetWndWidth(self):
        return self.width or self.absoluteRight - self.absoluteLeft

    def _OnResize(self, *args):
        if self.infoCont:
            if self.GetWndHeight() < SIZE_FULLUI[1]:
                self.infoCont.height = 190 - (SIZE_FULLUI[1] - self.GetWndHeight())
            else:
                self.infoCont.height = 190

    def ConstructLayout(self):
        self.filterCont = Container(name='filterCont', parent=self, align=uiconst.TOTOP, height=22, padTop=4, padBottom=2, uniqueUiName=pConst.UNIQUE_NAME_FLEET_FINDER_SETTINGS)
        self.infoCont = Container(name='infoCont', parent=self, align=uiconst.TOBOTTOM, height=155, state=uiconst.UI_PICKCHILDREN, padTop=4)
        self.infoCont.display = False
        self.topInfoCont = Container(name='topInfoCont', parent=self.infoCont, align=uiconst.TOTOP, height=20)
        self.descrCont = Container(name='descrCont', parent=self.infoCont, align=uiconst.TOALL, padRight=2, clipChildren=True)
        self.scrollCont = Container(name='scrollCont', parent=self, align=uiconst.TOALL)
        self._SetupFilterCont()
        self.showGroupAndHighStandingsFleets = Checkbox(text=GetByLabel('UI/Fleet/FleetRegistry/ShowGroupAndHighStandingsFleets'), parent=self.scrollCont, settingsKey='fleetfinder_showGroupAndHighStandingsFleets', checked=settings.char.ui.Get('fleetfinder_showGroupAndHighStandingsFleets', False), callback=self.OnShowPublicFleetsChanged, align=uiconst.TOTOP, settingsPath=('char', 'ui'), padding=(2, 4, 2, 4))
        self.scroll = Scroll(parent=self.scrollCont)
        self.scroll.sr.id = 'fleetfinderScroll'
        self.scroll.multiSelect = 0
        self.scroll.Load(contentList=[], headers=[], scrolltotop=0, noContentHint=GetByLabel('UI/Fleet/FleetRegistry/SearchHint'))
        self.captionLabel = EveLabelMediumBold(text='', parent=self.topInfoCont, align=uiconst.RELATIVE, left=4, top=2, state=uiconst.UI_NORMAL)
        self.detailsText = EditPlainText(name='detailsText', parent=self.descrCont, padTop=2, state=uiconst.UI_NORMAL, readonly=1)
        self.detailsText.HideBackground()
        self.detailsText.RemoveActiveFrame()
        FrameThemeColored(parent=self.detailsText, colorType=uiconst.COLORTYPE_UIHILIGHT)
        tabs = [110, 540]
        self.infoText = EveLabelMedium(name='infoText', text='', parent=self.descrCont, top=uiconst.defaultPadding, idx=0, tabs=tabs, state=uiconst.UI_NORMAL)
        self.joinBtn = Button(parent=self.topInfoCont, label=GetByLabel('UI/Fleet/FleetRegistry/JoinFleet'), pos=(0, 1, 0, 0), func=self.JoinFleet, align=uiconst.CENTERRIGHT)
        self.joinRequestBtn = Button(parent=self.topInfoCont, label=GetByLabel('UI/Fleet/FleetRegistry/RequestJoinFleet'), pos=(0, 1, 0, 0), func=self.JoinFleet, align=uiconst.CENTERRIGHT)

    def _SetupFilterCont(self):
        self.getFleetsBtn = Button(parent=self.filterCont, label=GetByLabel('UI/Fleet/FleetRegistry/FindFleets'), func=self.GetFleetsClick, align=uiconst.TORIGHT)
        comboCont = Container(name='comboCont', parent=self.filterCont)
        options, selected = self._GetScopeComboOptionsAndIsSelected()
        self.scopeCombo = Combo(parent=comboCont, options=options, name='fleetfinder_scopeFilter', select=selected, align=uiconst.TOLEFT_PROP, width=0.33, maxWidth=160, padLeft=2)
        self.scopeCombo.OnChange = self.OnComboChange
        options = [(GetByLabel('UI/Agency/ContentOfAnyDistance'), None),
         (GetByLabel('UI/Common/WithinJumps', numJumps=5), 5),
         (GetByLabel('UI/Common/WithinJumps', numJumps=10), 10),
         (GetByLabel('UI/Common/LocationTypes/Region'), -1)]
        self.rangeCombo = Combo(parent=comboCont, options=options, name='fleetfinder_rangeFilter', select=settings.user.ui.Get('fleetfinder_rangeFilter', None), align=uiconst.TOLEFT_PROP, width=0.33, maxWidth=130, padLeft=2)
        self.rangeCombo.OnChange = self.OnComboChange
        options = [(GetByLabel('UI/Standings/AnyStanding'), None), (GetByLabel('UI/Standings/GoodStanding'), contactGoodStanding), (GetByLabel('UI/Standings/ExcellentStanding'), contactHighStanding)]
        self.standingCombo = Combo(parent=comboCont, options=options, name='fleetfinder_standingFilter', select=settings.user.ui.Get('fleetfinder_standingFilter', None), align=uiconst.TOLEFT_PROP, width=0.33, maxWidth=130, padLeft=2)
        self.standingCombo.OnChange = self.OnComboChange

    def _GetScopeComboOptionsAndIsSelected(self):
        options = [(GetByLabel('UI/Fleet/FleetRegistry/MyAvailableFleets'), evefleet.INVITE_ALL), (GetByLabel('UI/Fleet/FleetRegistry/MyCorpFleets'), evefleet.INVITE_CORP)]
        selected = settings.user.ui.Get('fleetfinder_scopeFilter', None)
        if session.allianceid is not None:
            options.append((GetByLabel('UI/Fleet/FleetRegistry/MyAllianceFleets'), evefleet.INVITE_ALLIANCE))
        elif selected == evefleet.INVITE_ALLIANCE:
            selected = None
        if session.warfactionid is not None:
            options.append((GetByLabel('UI/Fleet/FleetRegistry/MyMilitiaFleets'), evefleet.INVITE_MILITIA))
        elif selected == evefleet.INVITE_MILITIA:
            selected = None
        options.append((GetByLabel('UI/Fleet/FleetRegistry/BasedOnStandings'), evefleet.INVITE_PUBLIC | evefleet.INVITE_PUBLIC_OPEN))
        return (options, selected)

    def SetInfoCont(self, entry):
        selected = GetAttrs(entry.sr.node, 'selected')
        if not selected:
            self.ClearInfoCont()
            return
        fleet = entry.sr.node.fleet
        self.infoCont.isOpen = True
        if self.GetWndHeight() >= SIZE_FULLUI[1]:
            self.infoCont.display = True
        caption = fleet.fleetName or GetByLabel('UI/Fleet/FleetRegistry/UnnamedFleet')
        self.captionLabel.text = caption
        text = GetFleetDetailsEntry(fleet)
        self.infoText.text = text
        self.detailsText.padTop = self.infoText.height + 2
        desc = fleet.description
        self.detailsText.display = bool(desc)
        self.detailsText.SetValue(desc)
        self.joinBtn.display = not bool(fleet.joinNeedsApproval)
        self.joinRequestBtn.display = bool(fleet.joinNeedsApproval)

    def ClearInfoCont(self):
        self.infoCont.display = False
        self.infoCont.isOpen = False
        self.detailsText.SetValue('')

    def OnComboChange(self, combo, header, value, *args):
        settings.user.ui.Set(combo.name, value)

    def GetFleetsClick(self, *args):
        self.gettingFleets = True
        try:
            self.getFleetsBtn.Disable()
            sm.GetService('fleet').GetFleetAdsForChar_Memoized.clear_memoized()
            self.Refresh()
        finally:
            uthread.new(self.EnableButtonTimer)
            self.gettingFleets = False

    def EnableButtonTimer(self):
        blue.pyos.synchro.SleepWallclock(GETFLEETS_THROTTLETIME)
        with ExceptionEater('fleetFinder.EnableButtonTimer'):
            self.getFleetsBtn.Enable()

    def OnShowPublicFleetsChanged(self, *args):
        self.Refresh()

    def Refresh(self):
        filterScope = self.scopeCombo.GetValue()
        filterRange = self.rangeCombo.GetValue()
        filterStanding = self.standingCombo.GetValue()
        onlyShowGroupAndHighStanding = self.showGroupAndHighStandingsFleets.checked
        self.GetFleets()
        self.DrawScrollList(filterScope, filterRange, filterStanding, onlyShowGroupAndHighStanding)
        self.ClearInfoCont()

    def JoinFleet(self, *args):
        fleetID = None
        selected = self.scroll.GetSelected()
        if len(selected) > 0:
            selected = selected[0]
            fleetID = getattr(selected, 'fleetID', None)
            if fleetID is None:
                return
        if fleetID:
            fleetSvc = sm.GetService('fleet')
            fleetSvc.ApplyToJoinFleet(fleetID)
            fleetSvc.LogFleetJoinAttempts(fleetID, evefleet.JOIN_SOURCE_FLEET_FINDER_BTN)

    def DrawScrollList(self, filterScope = None, filterRange = None, filterStanding = None, onlyShowGroupAndHighStanding = False):
        fleets = self.fleets
        self.PrimeStuff(fleets)
        scrolllist = []
        addressbookSvc = sm.GetService('addressbook')
        for fleet in fleets.itervalues():
            if addressbookSvc.IsBlocked(fleet.leader.charID):
                continue
            entry = self.GetFleetEntry(fleet, filterScope, filterRange, filterStanding, onlyShowGroupAndHighStanding)
            if entry:
                scrolllist.append(entry)

        headers = [GetByLabel('UI/Fleet/Ranks/Boss'),
         GetByLabel('UI/Fleet/FleetRegistry/BossLocationHeader'),
         GetByLabel('UI/Fleet/NameOfFleet'),
         GetByLabel('UI/Fleet/FleetRegistry/MemberCount'),
         GetByLabel('UI/Common/Description')]
        self.scroll.Load(contentList=scrolllist, headers=headers, scrolltotop=0, noContentHint=GetByLabel('UI/Fleet/FleetRegistry/SearchNoResult'))

    def IsOpenToMyGroups(self, fleetAd):
        if fleetAd.inviteScope & evefleet.INVITE_CORP and fleetAd.leader.corpID == session.corpid:
            return True
        if fleetAd.inviteScope & evefleet.INVITE_ALLIANCE and fleetAd.leader.allianceID == session.allianceid:
            return True
        if fleetAd.inviteScope & evefleet.INVITE_MILITIA and fleetAd.leader.warFactionID == session.warfactionid:
            return True
        return False

    def GetFleetEntry(self, fleet, filterScope, filterRange, filterStanding, onlyShowGroupAndHighStanding):
        if filterScope is not None:
            if fleet.inviteScope & filterScope == 0:
                return
            if filterScope == evefleet.INVITE_CORP and fleet.leader.corpID != session.corpid:
                return
            if filterScope == evefleet.INVITE_ALLIANCE and fleet.leader.allianceID != session.allianceid:
                return
            if filterScope == evefleet.INVITE_MILITIA and fleet.leader.warFactionID != session.warfactionid:
                return
        if filterRange is not None:
            if not hasattr(fleet, 'numJumps'):
                return
            if 0 < filterRange < fleet.numJumps:
                return
            if filterRange == -1 and fleet.regionID != session.regionid:
                return
        if filterStanding is not None:
            if filterStanding > fleet.standing:
                return
        if onlyShowGroupAndHighStanding and fleet.inviteScope & evefleet.INVITE_PUBLIC_OPEN:
            if fleet.leader.charID != session.charid and not self.IsOpenToMyGroups(fleet):
                if fleet.public_minStanding is None or fleet.public_minStanding <= 0:
                    return
        bossName = GetByLabel('UI/Common/CharacterNameLabel', charID=fleet.leader.charID)
        if fleet.hideInfo:
            numMembers = '<color=0x7f888888>%s</color>' % GetByLabel('UI/Generic/Private')
            systemString = '<color=0x7f888888>%s</color>' % GetByLabel('UI/Generic/Private')
        else:
            if fleet.advertJoinLimit and fleet.numMembers >= fleet.advertJoinLimit:
                numMembers = '<color=0xffdd0000>%s</color>' % fleet.numMembers
            else:
                numMembers = fleet.numMembers
            systemString = GetByLabel('UI/Common/LocationDynamic', location=fleet.solarSystemID)
        return GetFromClass(FleetFinderEntry, {'label': '%s<t>%s<t>%s<t>%s<t>%s' % (bossName,
                   systemString,
                   fleet.fleetName,
                   numMembers,
                   fleet.description),
         'fleetID': fleet.fleetID,
         'charID': fleet.leader.charID,
         'fleet': fleet,
         'OnClick': self.SetInfoCont,
         'corpID': fleet.leader.corpID,
         'allianceID': fleet.leader.allianceID,
         'warFactionID': fleet.leader.warFactionID,
         'securityStatus': fleet.leader.securityStatus})

    def PrimeStuff(self, fleets):
        pathfinderSvc = sm.GetService('clientPathfinderService')
        mapSvc = sm.GetService('map')
        standingSvc = sm.GetService('standing')
        namesForPriming = set()
        locationsForPriming = set()
        for fleet in fleets.itervalues():
            for itemID in [fleet.leader.charID, fleet.leader.corpID, fleet.leader.allianceID]:
                if itemID is not None:
                    namesForPriming.add(itemID)

            fleet.regionID = None
            fleet.standing = standingSvc.GetStanding(session.charid, fleet.leader.charID)
            if fleet.Get('solarSystemID', 0):
                locationsForPriming.add(fleet.solarSystemID)
                numJumps = int(pathfinderSvc.GetJumpCountFromCurrent(fleet.solarSystemID))
                fleet.numJumps = numJumps
                constellationID = mapSvc.GetParent(fleet.solarSystemID)
                fleet.regionID = mapSvc.GetParent(constellationID)
                fleet.standing = standingSvc.GetStanding(session.charid, fleet.leader.charID)

        if len(namesForPriming) > 0:
            cfg.eveowners.Prime(namesForPriming)
        if len(locationsForPriming) > 0:
            cfg.evelocations.Prime(locationsForPriming)

    def GetFleets(self):
        self.fleets = sm.GetService('fleet').GetFleetAdsForChar_Memoized()
        return self.fleets
