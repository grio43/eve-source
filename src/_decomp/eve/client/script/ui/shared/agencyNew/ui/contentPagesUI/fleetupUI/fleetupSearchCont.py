#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPagesUI\fleetupUI\fleetupSearchCont.py
import random
import evefleet
import gametime
from caching import Memoize
from carbon.common.script.util.format import FmtDate
from carbonui import ButtonVariant, uiconst
from carbonui.control.button import Button
from carbonui.control.checkbox import Checkbox
from carbonui.control.combo import Combo
from carbonui.control.dragResizeCont import DragResizeCont
from carbonui.control.scroll import Scroll
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.warningContainer import WarningContainer
from carbonui.util.bunch import Bunch
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from eve.common.lib import appConst as const
from eve.client.script.parklife import states as stateConst
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.shared.agencyNew import agencySignals
from eve.client.script.ui.shared.agencyNew.agencyUtil import GetNumberOfJumps, GetNoRouteFoundText
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.ui.contentPagesUI.fleetupUI.fleetupFleetEntries import FleetUpFleetEntry
from eve.client.script.ui.shared.fleet.fleet import FleetSvc, GetAllFleetActivities, GetFleetActivityName
from eve.client.script.ui.shared.stateFlag import GetStateFlagFromData
from eve.client.script.ui.shared.agencyNew.ui.contentPagesUI.fleetupUI.joinFleetConfirmation import RequestToJoinFleet
from evefleet.fleetAdvertObject import FleetAdvertObject
from localization import GetByLabel
from utillib import KeyVal
LAST_FLEET_ID_SETTING = 'fleetup_selectedFleetID'
STANDING_SORT_ORDER = [stateConst.flagStandingHorrible,
 stateConst.flagStandingBad,
 stateConst.flagStandingNeutral,
 stateConst.flagStandingGood,
 stateConst.flagStandingHigh,
 stateConst.flagSameMilitia,
 stateConst.flagSameAlliance,
 stateConst.flagSamePlayerCorp,
 stateConst.flagSameNpcCorp,
 stateConst.flagSameFleet]

class FleetupSearchCont(Container):
    __guid__ = 'FleetupSearchCont'
    __notifyevents__ = ['OnFleetJoin_Local',
     'OnFleetLeave_Local',
     'OnFleetFinderAdvertChanged',
     'OnOwnAdvertUpdated']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.ConstructUI()
        self.LoadUI()
        sm.RegisterNotify(self)

    def ConstructUI(self):
        topCont = ContainerAutoSize(name='topCont', parent=self, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, padding=(0, 20, 0, 20))
        self.bottomCont = Container(name='bottomCont', parent=self, align=uiconst.TOBOTTOM, padTop=40, height=40, padBottom=37)
        centerCont = Container(name='centerCont', parent=self)
        self.filterCont = Container(name='filterCont', parent=topCont, align=uiconst.TOTOP, height=48)
        self.AddFilters()
        self.createAndRegisterBtn = Button(name='registerBtn', parent=topCont, align=uiconst.CENTERRIGHT, label=GetByLabel('UI/Agency/Fleetup/RegisterFleetCommandBtn'), variant=ButtonVariant.PRIMARY, func=self.OnRegistrationClicked, hint=GetByLabel('UI/Agency/Fleetup/RegisterFleetCommandBtnHint'))
        self.ConstructCreateAd()
        self.requestToJoinBtn = Button(name='requestToJoinBtn', parent=self.bottomCont, align=uiconst.CENTERRIGHT, label=GetByLabel('UI/Agency/Fleetup/RequestToJoin'), func=self.RequestToJoin, analyticID=evefleet.REQUEST_TO_JOIN_BTN_ANALYTIC_ID)
        self.createAndRegisterBtn.width = self.requestToJoinBtn.width = max(self.createAndRegisterBtn.width, self.requestToJoinBtn.width)
        self.rightSide = DragResizeCont(name='rightSideResizeCont', parent=centerCont, align=uiconst.TORIGHT, maxSize=350, minSize=150, defaultSize=250)
        self.scroll = Scroll(parent=centerCont, hasUnderlay=False, id='fleetAdvertScroll')
        self.scroll.multiSelect = False
        self.scroll.tabMargin = 14
        self.scroll.ChangeSortBy = self.ScrollSortBy
        self.ConstructRightSide()

    def OnRegistrationClicked(self, *args):
        agencySignals.on_content_group_selected(contentGroupConst.contentGroupFleetUpRegister)

    def ConstructRightSide(self):
        innnerRightCont = Container(name='innnerRightCont', parent=self.rightSide, padLeft=10)
        contHeight = self.scroll.sr.scrollHeaders.height
        self.fleetDescLabelCont = Container(parent=innnerRightCont, align=uiconst.TOTOP, height=contHeight, top=1)
        EveLabelMedium(parent=self.fleetDescLabelCont, align=uiconst.CENTERLEFT, text=GetByLabel('UI/Agency/Fleetup/DescriptionForSelectedAd').upper(), left=20)
        self.fleetDescEdit = EditPlainText(parent=innnerRightCont, readonly=True, hasUnderlay=False)

    def ConstructCreateAd(self):
        self.createAdCont = LayoutGrid(name='createAdCont', parent=self.bottomCont, align=uiconst.CENTERLEFT, columns=2, cellSpacing=(10, 0))
        WarningContainer(parent=self.createAdCont, align=uiconst.CENTERLEFT, left=2, text=GetByLabel('UI/Agency/Fleetup/FleetNotListedWarning'))
        self.createAdBtn = Button(name='createAdBtn', parent=self.createAdCont, align=uiconst.CENTERLEFT, label=GetByLabel('UI/Agency/Fleetup/CreateAdBtn'), func=self.CreateAd)
        self.createAdCont.display = False

    def LoadUI(self):
        self.LoadFleetAdverts()
        self.LoadRightSide()
        self.UpdateButtons()

    def LoadFleetAdverts(self):
        scrollList = self.GetFleetAdsToLoad()
        headers = [GetByLabel('UI/Agency/Fleetup/ActivityHeader'),
         GetByLabel('UI/Agency/Fleetup/FleetLeaderHeader'),
         GetByLabel('UI/Agency/Fleetup/FleetNameHeader'),
         GetByLabel('UI/Agency/Fleetup/TimeActiveHeader'),
         GetByLabel('UI/Agency/Fleetup/MembersHeader'),
         GetByLabel('UI/Agency/Fleetup/JumpsAwayHeader')]
        ignoreSort = self.scroll.GetSortBy() is None
        self.scroll.Load(contentList=scrollList, headers=headers, noContentHint=GetByLabel('UI/Agency/Fleetup/NoSearchResults'), ignoreSort=ignoreSort)
        self.scroll.ScrollToSelectedNode()

    def GetFleetAdsToLoad(self):
        fleetAds = sm.GetService('fleet').GetFleetAdsForChar_Memoized()
        activityValue = self.activityCombo.GetValue()
        jumpFilter = self.distancePickerCombo.GetValue()
        npFilter = self.newPlayerFriendlyCb.checked
        scrollList = []
        realAndFakeFleetAds = fleetAds.copy()
        fleetLeaders = set()
        for x in realAndFakeFleetAds.itervalues():
            fleetLeaders.add(x.leader.charID)

        cfg.eveowners.Prime(fleetLeaders)
        lastSelectedFleetID = settings.char.ui.Get(LAST_FLEET_ID_SETTING, None)
        privateText = '<color=0x7f888888>%s</color>' % GetByLabel('UI/Generic/Private')
        for eachFleetID, eachFleetAd in realAndFakeFleetAds.iteritems():
            if activityValue and activityValue != eachFleetAd.activityValue:
                continue
            if npFilter and not eachFleetAd.newPlayerFriendly:
                continue
            jumps = GetNumberOfJumps(eachFleetAd.solarSystemID)
            jumpsText = jumps
            numMembersSortValue = eachFleetAd.numMembers
            numMembersText = numMembersSortValue
            if eachFleetAd.hideInfo:
                jumps = const.maxInt - 1
                jumpsText = privateText
                numMembersText = privateText
                numMembersSortValue = const.maxInt
            elif jumpFilter > 0:
                if jumps > jumpFilter:
                    continue
            elif jumps == const.maxInt:
                jumpsText = GetNoRouteFoundText(eachFleetAd.solarSystemID)
            charIndexValues, label = FleetUpFleetEntry.GetCharIndexValuesAndLabel(eachFleetAd, jumps)
            leaderName = cfg.eveowners.Get(eachFleetAd.leader.charID).name
            leaderFlag = GetStateFlagFromData(eachFleetAd.leader)
            node = Bunch(decoClass=FleetUpFleetEntry, label=label, fleetActivityID=eachFleetAd.activityValue, fleetActivityName=GetFleetActivityName(eachFleetAd.activityValue), fleetName=eachFleetAd.fleetName, fleetLeaderName=leaderName, leaderFlag=leaderFlag, dateText=FmtDate(gametime.GetWallclockTime() - eachFleetAd.dateCreated, 'ns'), numMembersText=numMembersText, jumpsText=jumpsText, tabMargin=14, fleetID=eachFleetID, fleetAd=eachFleetAd, isMyFleet=eachFleetID == session.fleetid, isSelected=eachFleetID == lastSelectedFleetID, OnClick=self.SelectFleetEntry, charIndexValues=charIndexValues)
            flagSortValue = -STANDING_SORT_ORDER.index(leaderFlag) if leaderFlag in STANDING_SORT_ORDER else leaderFlag
            leaderSortValue = (flagSortValue, leaderName.lower())
            node['sort_%s' % GetByLabel('UI/Agency/Fleetup/FleetLeaderHeader')] = leaderSortValue
            node['sort_%s' % GetByLabel('UI/Agency/Fleetup/TimeActiveHeader')] = -eachFleetAd.dateCreated
            node['sort_%s' % GetByLabel('UI/Agency/Fleetup/JumpsAwayHeader')] = jumps
            node['sort_%s' % GetByLabel('UI/Agency/Fleetup/MembersHeader')] = numMembersSortValue
            scrollList.append(node)

        return scrollList

    def SelectFleetEntry(self, fleetEntry):
        node = fleetEntry.sr.node
        settings.char.ui.Set(LAST_FLEET_ID_SETTING, node.fleetID)
        self.LoadRightSide()

    def LoadRightSide(self, *args):
        selected = self.scroll.GetSelected()
        self.fleetDescLabelCont.display = bool(selected)
        if not selected:
            self.requestToJoinBtn.display = False
            self.fleetDescEdit.SetValue('')
            self.fleetDescEdit.ShowHint(GetByLabel('UI/Agency/Fleetup/NoFleetSelected'))
            return
        self.fleetDescEdit.ShowHint(None)
        self.fleetDescLabelCont.height = self.scroll.sr.scrollHeaders.height
        self.requestToJoinBtn.display = True
        node = selected[0]
        fleetAd = node.fleetAd
        self.fleetDescEdit.SetValue(fleetAd.description or GetByLabel('UI/Agency/Fleetup/NoDescriptionSet'))
        self.UpdateButtons()

    def UpdateButtons(self):
        selected = self.scroll.GetSelected()
        fleetID = selected[0].fleetID if selected else None
        if selected:
            self.requestToJoinBtn.display = True
            if fleetID == session.fleetid:
                self.requestToJoinBtn.Disable()
                self.requestToJoinBtn.hint = GetByLabel('UI/Agency/Fleetup/AlreadyInThisFleetHint')
            else:
                self.requestToJoinBtn.Enable()
                self.requestToJoinBtn.hint = ''
        else:
            self.requestToJoinBtn.display = False
        self.createAndRegisterBtn.label = GetByLabel('UI/Agency/Fleetup/RegisterFleetCommandBtn')
        self.createAndRegisterBtn.hint = GetByLabel('UI/Agency/Fleetup/RegisterFleetCommandBtnHint')
        self.createAndRegisterBtn.analyticID = evefleet.REGISTER_BTN_ANALYTIC_ID
        self.createAndRegisterBtn.Enable()
        self.createAdCont.display = False
        if session.fleetid:
            self.createAndRegisterBtn.Disable()
            self.createAndRegisterBtn.hint = GetByLabel('UI/Agency/Fleetup/AlreadyInFleetHint')
            fleetSvc = FleetSvc()
            if fleetSvc.IsBoss() and not fleetSvc.IsFleetRegistered():
                self.createAdCont.display = True
            elif fleetSvc.CanUpdateAdvert():
                self.createAndRegisterBtn.analyticID = evefleet.UPDATE_BTN_ANALYTIC_ID
                self.createAndRegisterBtn.Enable()
                self.createAndRegisterBtn.label = GetByLabel('UI/Agency/Fleetup/UpdateFleetAdvertBtn')
                self.createAndRegisterBtn.hint = GetByLabel('UI/Agency/Fleetup/UpdateFleetAdvertBtnHint')

    def CreateAd(self, *args):
        sm.GetService('agencyNew').OpenWindow(contentGroupConst.contentGroupFleetUpRegister)

    def RequestToJoin(self, *args):
        selected = self.scroll.GetSelected()
        if not selected:
            return
        node = selected[0]
        RequestToJoinFleet(node.fleetID, node.fleetAd)

    def AddFilters(self):
        options = [ (v, k) for k, v in GetAllFleetActivities().iteritems() ]
        options.sort(key=lambda x: x[0].lower())
        options.insert(0, (GetByLabel('UI/Agency/Fleetup/AllActivity'), 0))
        activityConfigName = 'fleetup_activityPicker'
        self.activityCombo = Combo(parent=self.filterCont, options=options, name='fleetup_activityFilter', align=uiconst.TOPLEFT, callback=self.OnActivityPickerChanged, label=GetByLabel('UI/Agency/Fleetup/Fleet ActivityFilter'), prefskey=('char', 'ui', activityConfigName), select=settings.char.ui.Get(activityConfigName, 0))
        distanceOptions = [ (GetByLabel('UI/Agency/Fleetup/WithinJumps', jumpCount=x), x) for x in (1, 5, 10, 20) ]
        distanceOptions.insert(0, (GetByLabel('UI/Agency/ContentOfAnyDistance'), -1))
        distanceConfigName = 'fleetup_distanceFilter'
        self.distancePickerCombo = Combo(parent=self.filterCont, options=distanceOptions, name='distancePickerCombo', align=uiconst.TOPLEFT, left=self.activityCombo.left + self.activityCombo.width + 20, callback=self.OnDistancePickerChanged, label=GetByLabel('UI/Agency/Fleetup/JumpsAwayFilter'), prefskey=('char', 'ui', distanceConfigName), select=settings.char.ui.Get(distanceConfigName, 0))
        self.newPlayerFriendlyCb = Checkbox(parent=self.filterCont, name='newPlayerFriendlyCb', align=uiconst.CENTERLEFT, text=GetByLabel('UI/Agency/Fleetup/NewPlayerFriendlyFilter'), left=self.distancePickerCombo.left + self.distancePickerCombo.width + 20, hint=GetByLabel('UI/Agency/Fleetup/NewPlayerFriendlyFilterHint'), prefstype=('char', 'ui'), configName='fleetup_newPlayerFriendlyCb', callback=lambda *args: self.LoadUI(), checked=settings.char.ui.Get('fleetup_newPlayerFriendlyCb', False))
        self.activityCombo.top = -self.activityCombo.sr.label.top
        self.distancePickerCombo.top = self.activityCombo.top
        self.newPlayerFriendlyCb.top = self.activityCombo.top / 2
        self.filterCont.height = self.activityCombo.top + self.activityCombo.height

    def OnActivityPickerChanged(self, *args):
        self.activityCombo.UpdateSettings()
        self.LoadUI()

    def OnDistancePickerChanged(self, *args):
        self.distancePickerCombo.UpdateSettings()
        self.LoadUI()

    def OnFleetJoin_Local(self, member, *args):
        if session.charid == member.charID:
            self.LoadUI()

    def OnFleetLeave_Local(self, member, *args):
        if session.charid == member.charID:
            self.LoadUI()

    def OnOwnAdvertUpdated(self, *args):
        self.LoadUI()

    def OnFleetFinderAdvertChanged(self):
        self.UpdateButtons()

    def ScrollSortBy(self, by, *args):
        idx = None
        headers = self.scroll.GetColumns()
        if by in headers:
            idx = headers.index(by)
        if idx is not None:
            self.UpdateCharIdx(idx)
        Scroll.ChangeSortBy(self.scroll, by, *args)

    def UpdateCharIdx(self, sortIdx):
        for eachNode in self.scroll.GetNodes():
            eachNode.charIndex = eachNode.charIndexValues[sortIdx]


@Memoize
def GetFakeAds():
    fleetData = [(evefleet.ACTIVITY_PVP,
      'Wormholers Inc',
      23,
      '- Small gang to medium gang Wh PvP.<br><br>- Access to a strong WH infrastructure with good refining and manufacturing stations.<br><br>- A relaxed environment to learn the ropes of WH space.<br><br>- Pathfinder for easy navigation and travel in WH space.<br><br>- Ratting and home wormhole defence fleets.<br><br>- Exciting and experience full PvP encounters together with friends.'),
     (evefleet.ACTIVITY_PVP,
      'Foxhole Null Roamers',
      7,
      'Experienced wormhole and tournament FC<br>PvP focused, especially small gang. In Low, Null and WH space!<br>C2 & C3 statics. Leading to almost limitless content such as PvP, PvE and easy logistics.'),
     (evefleet.ACTIVITY_PVP,
      'Newbie Fighting Fleet',
      32,
      'PVP<br><br>> A very social group to have fun and talk with<br><br>> Training and advice for new pilots<br><br>>Newbie Friendly!'),
     (evefleet.ACTIVITY_PVP,
      'Fast Fun Fleetups!!!',
      56,
      'Tired of 40+ jumps lookingfor content? Tired of those darned huuge battles were it takes 5minutes to activate a module? U just wonna have fun? Find new pplz to talk and chill with? Learn to pvp? Come fly with us and have instan fun!!!'),
     (evefleet.ACTIVITY_PVP,
      'Hardcore Muthas',
      18,
      'PvP Fleet for Veteran players with min of 20M Skillpoints<br>Null roams<br>Structure bashing<br>Wormhole Evictions<br>Git gud or die trying!'),
     (evefleet.ACTIVITY_PVP,
      'Rookie Pilot Fleet',
      65,
      "New Players Wanted!<br><br>Want to learn how to fly in a fleet but were too afraid to ask?<br>Want to learn how to PvP but don't have the experience?<br>Want to team up with people and have pew pew fun?<br>This is the fleet for you!"),
     (evefleet.ACTIVITY_INCURSIONS,
      "Sansha's Little Helpers",
      12,
      'Incursion running fleet<br>Must be able to run LvL 4 missions<br>Logistics always needed<br>Fleet size limited<br>Experienced players only'),
     (evefleet.ACTIVITY_INCURSIONS,
      'Mothership Hunters',
      9,
      'Lo and null sec Incursion fleet<br>Experienced FC<br>Electronic Warfare  Skills preferred<br>Shield Tank preferred<br>12M Skill Point minimum'),
     (evefleet.ACTIVITY_INCURSIONS,
      'The Flying Chieftans',
      11,
      'Armor Tank ships needed to run Incursions in Null<br>FC has 2 years experience running Incursions<br>Experienced players preferred but will accept unexperienced players with the right skills (just ping me in chat to let me know you need help)<br>Casual group putting fun over profit'),
     (evefleet.ACTIVITY_INCURSIONS,
      'Kuvakei Must Die!',
      3,
      'Experienced player new to Incursions looking for like minded people to fly with<br>All welcome<br>Kuvakei must die or we die trying<br>Be nice.'),
     (evefleet.ACTIVITY_FW,
      'Trust in Rust',
      8,
      'Pilots needed to fight for the minmatar in FW<br>All welcome<br>No experience necessary<br>Help given to new players<br>Trust in Rust!'),
     (evefleet.ACTIVITY_FW,
      'The Divine',
      2,
      'Blessed are those that fight for Amarr<br>Faction Warfare our speciality<br>Experienced players wanted<br>No Minmatar'),
     (evefleet.ACTIVITY_FW,
      'Missile Command',
      7,
      'The Caldari Navy needs you!<br>Enlist now to defeat the Gallente<br>No experience required<br>Good FC willing to teach newbies'),
     (evefleet.ACTIVITY_FW,
      'Freedom Fries',
      5,
      'Freedom Fighters needed for the Gallente<br>Daily FW fleets<br>Join in the fun<br>Casual players welcome'),
     (evefleet.ACTIVITY_PIRATE_STRONGHOLD,
      "Dodixie's Midnight Runners",
      9,
      'Pirate Hunters needed!<br>Patrolling Asteroid Fields and attacking Bases<br>Any experience welcome<br>If you die, you die<br>80s music may be played on comms'),
     (evefleet.ACTIVITY_PIRATE_STRONGHOLD,
      'The Corsairs',
      7,
      "Looking to complete Pirate Strongholds in High and Lo-Sec<br>No experience needed but don't fly what you can't afford to lose<br>Be polite <br>Fly safe"),
     (evefleet.ACTIVITY_PIRATE_STRONGHOLD,
      'Morris and the Miners',
      11,
      'Defence fleet needed to protect miners from Pirates<br><br>Share of loot and mineral profits for all players<br><br>Save the Crabs!'),
     (evefleet.ACTIVITY_ABYSS,
      'Tranquil Waters',
      4,
      '- Newbie friendly Abyssal fleet<br>- No experience necessary<br>- Mostly Tranquil sites but may attempt harder - based on experience and fleet composition<br>- Friendly players welcome'),
     (evefleet.ACTIVITY_ABYSS,
      'Deeper Down The Spiral',
      3,
      'Players wanted for Abyssal sites<br>New players welcome if skilled up enough<br>Agitated, Fierce and maybe Raging sites<br>Loot shared'),
     (evefleet.ACTIVITY_ABYSS,
      'Chaotic Neutrals',
      5,
      '-Experienced Abyss pilots wanted<br>-Chaotic Abyss content only<br>-Filament donations welcome'),
     (evefleet.ACTIVITY_ABYSS,
      'Skillers in the Abyss',
      3,
      'Fierce content and upwards<br>Experts not needed but some experience necessary<br>Logi always needed<br>Please have dischord for comms'),
     (evefleet.ACTIVITY_COMBAT_ANOMALIES,
      'Angels Must Fall',
      15,
      '*Small/medium fleet looking for pilots for *Angel Cartel combat anomalies (please fit your ships correctly)<br>*High-sec only<br>*Level 3-4 difficulty<br>*No experience necessary as long as you can follow instructions'),
     (evefleet.ACTIVITY_COMBAT_ANOMALIES,
      'Lo-sec Blood Raider Raiders',
      21,
      'Level 4 Missions only<br>Lo-sec Only<br>No newbs<br>Mostly Blood Raider content<br>Cruisers and above only'),
     (evefleet.ACTIVITY_COMBAT_ANOMALIES,
      'Haven is a Place on Earth',
      7,
      'Elite players needed to run Havens in null<br>No scrubs needed<br>Dichord required<br>Take no prisoners!'),
     (evefleet.ACTIVITY_COMBAT_ANOMALIES,
      'Any Port in a Storm',
      11,
      'Experienced players wanted for low and null sec Combat Anomalies<br><br>Must be able to complete Port level combat sites<br><br>All requests to join will be reviewed <br><br>Fly safe!'),
     (evefleet.ACTIVITY_COMBAT_ANOMALIES,
      'Yard Dogs',
      18,
      "Good FC looking for players with some experience of running combat sites<br>Looking mostly for Gurista Yard sites but may run other factions or difficulties depending on fleet<br>Good attitude more important than good skill<br>Let's have some fun."),
     (evefleet.ACTIVITY_ESCALATIONS,
      'Expedite Espeditions',
      6,
      'Players needed to help complete Following the Blood escalation in high sec<br>Bloodraider NPCs<br>Damage/Resists EM & Th'),
     (evefleet.ACTIVITY_ESCALATIONS,
      'Scandalous!',
      9,
      'Experienced players wanted for Toxic Waszte Scadal! Escalation<br>Only apply if you have completed similar escalations<br>Cruiser minimum ship type<br>Null sec v Angel Cartel<br>Fit accordigly'),
     (evefleet.ACTIVITY_ESCALATIONS,
      'That Escalated Quickly',
      15,
      'All welcome!<br>Looking for pilots to clear Unrated Complexes and any Escaltions<br>Rookies welcome<br>Mostly hi-sec encounters'),
     (evefleet.ACTIVITY_ESCALATIONS,
      'Trigger Happy',
      16,
      'High sec Fleet looking to trigger escalations<br>All player experience welcome<br>Prefer Gurista content<br>Only apply if you can spare at least an hour<br>Discord preferred'),
     (evefleet.ACTIVITY_MINING,
      'Crabbers Delight',
      15,
      'High sec Mining Fleet<br>Will buy all minerals at good prices<br>Fleet boosts available<br>Rookies welcome<br>Happy are the crabbers!'),
     (evefleet.ACTIVITY_MINING,
      'Gas Huffers United',
      11,
      'Looking for people to help with gas harvesting<br>Sites already scanned down<br>Defence ships welcome<br>Share in profits!!!'),
     (evefleet.ACTIVITY_MINING,
      'Ice Ice Baby',
      7,
      'Ice Harvesting Fleet<br>Looking for Enriched Faction asteroids<br>Can refine with good yields if needed<br>All welcome'),
     (evefleet.ACTIVITY_MINING,
      'There is no Moon',
      4,
      'Want to learn how to moon mine?<br>Join my fleet<br>Moon ore chunks ready to go<br>Mining Crystals provided<br>Buyback at good prices'),
     (evefleet.ACTIVITY_MINING,
      'Nothing Ventured',
      25,
      'Newbie Friendly Mining Fleet<br>Ventures only<br>Safe mining in high sec<br>Come chill with us!'),
     (evefleet.ACTIVITY_MINING,
      'Deep Core, You Know The Score',
      14,
      'Miners with Deep Core Mining skills needed to help mine Mercoxit in Null<br>Haulers welcome<br>Scouts welcome<br>All profits shared'),
     (evefleet.ACTIVITY_MINING,
      'Spod U Like',
      12,
      'Spodumain mining in Null<br>Barges and Exhumers needed<br>Profit share<br>Hauling provided<br>Or join our defence fleet - Spod Podders'),
     (evefleet.ACTIVITY_EXPLORATION,
      'To Boldly Go...',
      3,
      'Wormhole Explration<br>C2 and C3 class<br>Pirate Relic Sites<br>Good hacking skills needed'),
     (evefleet.ACTIVITY_EXPLORATION,
      'Forget Me Not',
      4,
      'Experienced explorers needed for Sleeper sites<br>Good combat as well as hacking skills requires<br>All loot must be shared!'),
     (evefleet.ACTIVITY_EXPLORATION,
      'Ghostbusters',
      6,
      'Experienced players needed for Ghost Sites<br>Level 5 Hacking required<br>Serious players only'),
     (evefleet.ACTIVITY_EXPLORATION,
      'A Scanner Darkly',
      13,
      'Want to learn how to scan?<br>Want to learn how to complete data and relic sites?<br>Experienced player happy to show new players the ropes in hi-sec'),
     (evefleet.ACTIVITY_FREE_ROAM,
      'Whatever Wherever',
      26,
      'Looking to roam Null looking for action<br>PvE, PvP, Structure bashing, mission running<br>All levels welcome'),
     (evefleet.ACTIVITY_FREE_ROAM,
      'Lone Wolves United',
      19,
      'Bored of solo content?<br>Want to find new activities?<br>Join my fleet as we roam low and null<br>Fun guaranteed*<br><br>*not an actual guarantee<br>'),
     (evefleet.ACTIVITY_FREE_ROAM,
      'Fresh Blood',
      31,
      '* New players needed!<br>* Experiened Fleet Commanded willing to teach new players <br>* Variety of activities<br>* Join up and take your next steps in being a pilot'),
     (evefleet.ACTIVITY_MISC,
      'Spod Podders',
      5,
      'Defence fleet needed to protect Spod U Like mining fleet in Null<br>Share of mining profits<br>Cruisers and up'),
     (evefleet.ACTIVITY_MISC,
      'My Fleet',
      3,
      'Just doing some stuff with friends'),
     (evefleet.ACTIVITY_MISC,
      'Whatever, Whereever ',
      7,
      "Just looking for fellow capsuleers to join up with<br>No planned activity<br>Let's see what happens<br>o7"),
     (evefleet.ACTIVITY_MISC,
      'Mine, Haul, Repeat',
      21,
      'Miners, haulers and combat pilots needed<br>Want to create a fleet to mine in Null<br>Need haulers to transport minerals to trade hubs<br>Need combat pilots and scouts to protect from pirates and other players<br>Message me for more info<br>'),
     (evefleet.ACTIVITY_MISC,
      'Road to Nowhere',
      2,
      'Looking to explore wormholes<br>Looking to do relic and data sites<br>Looking to complete combat sites<br>Looking to do wahtever we find in WH space'),
     (evefleet.ACTIVITY_MISC,
      'Pew Pew Die!',
      16,
      'looking for PvE and PvP action in Null<br>Experienced players preferred<br>No minimum skill requirements but be good with what you fly<br>No moaning<br>The FC is always right!')]
    charIDs = {x for x in xrange(3019473, 3019973)}
    cfg.eveowners.Prime(charIDs)
    solarSystemOptions = cfg.mapRegionCache[session.regionid].solarSystemIDs
    fakeAdsByFleetID = {}
    for activity, fleetName, numMembers, fleetDesc in fleetData:
        validCharID = None
        while validCharID is None and charIDs:
            testCharID = charIDs.pop()
            charInfo = cfg.eveowners.GetIfExists(testCharID)
            if charInfo and charInfo.name != 'Aura':
                validCharID = testCharID

        if validCharID is None:
            continue
        leader = KeyVal(charID=validCharID, corpID=None, allianceID=None, warFactionID=None, securityStatus=0)
        solarSystemID = random.choice(solarSystemOptions)
        advertTime = random.randint(gametime.GetWallclockTime() - 12 * const.HOUR, gametime.GetWallclockTime() - 3 * const.MIN)
        fleetAd = FleetAdvertObject(leader=leader, solarSystemID=solarSystemID, advertTime=advertTime, dateCreated=advertTime, numMembers=numMembers, fleetName=fleetName, description=fleetDesc, activityValue=activity)
        fakeAdsByFleetID[-validCharID] = fleetAd

    return fakeAdsByFleetID
