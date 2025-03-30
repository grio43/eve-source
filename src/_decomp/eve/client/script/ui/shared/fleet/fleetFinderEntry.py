#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fleet\fleetFinderEntry.py
import evefleet.client
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.uiconst import defaultPadding
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.shared.stateFlag import AddAndSetFlagIconFromData
from eveservices.menu import GetMenuService
from localization import GetByLabel
from menu import MenuLabel
import blue

class FleetFinderEntry(Generic):
    __guid__ = 'listentry.FleetFinderEntry'
    isDragObject = True

    def Startup(self, *args):
        Generic.Startup(self, *args)
        self.picture = Container(name='picture', parent=self, pos=(defaultPadding,
         2,
         32,
         32), state=uiconst.UI_PICKCHILDREN, align=uiconst.TOPLEFT)
        self.portrait = Icon(name='portrait', parent=self.picture, size=32, align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)

    def Load(self, node):
        Generic.Load(self, node)
        Frame(parent=self.picture)
        sm.GetService('photo').GetPortrait(node.charID, 32, self.portrait)
        AddAndSetFlagIconFromData(parentCont=self.picture, data=node, top=23)
        self.portrait.OnClick = (sm.GetService('info').ShowInfo, cfg.eveowners.Get(node.charID).typeID, node.charID)
        self.sr.label.left = 40
        self.sr.label.text = node.label
        self.sr.label.Update()

    def GetHeight(self, *args):
        node, width = args
        node.height = 37
        return node.height

    def GetMenu(self, *args):
        menuSvc = GetMenuService()
        m = []
        fleet = self.sr.node.fleet
        fleetSvc = sm.GetService('fleet')
        if self.sr.node.fleetID != session.fleetid:
            m += [(MenuLabel('UI/Fleet/FleetRegistry/JoinFleet'), self.ApplyToJoinFleet)]
            m += [None]
        elif fleetSvc.IsBoss():
            m += [(MenuLabel('UI/Fleet/FleetWindow/EditAdvert'), fleetSvc.OpenRegisterFleetWindow)]
            if sm.GetService('fleet').GetCurrentAdvertForMyFleet() is not None:
                m += [(MenuLabel('UI/Fleet/FleetWindow/RemoveAdvert'), fleetSvc.UnregisterFleet)]
            m += [None]
        fleetbossMenu = menuSvc.CharacterMenu(fleet.leader.charID)
        m += [(MenuLabel('UI/Fleet/Ranks/Boss'), fleetbossMenu)]
        if fleet.solarSystemID:
            m += [(MenuLabel('UI/Fleet/FleetRegistry/BossLocationHeader'), menuSvc.CelestialMenu(itemID=fleet.solarSystemID))]
        return m

    def OnDblClick(self, *args):
        self.ApplyToJoinFleet()

    def ApplyToJoinFleet(self, *args):
        fleetID = self.sr.node.fleet.fleetID
        fleetSvc = sm.GetService('fleet')
        fleetSvc.ApplyToJoinFleet(fleetID)
        fleetSvc.LogFleetJoinAttempts(fleetID, evefleet.JOIN_SOURCE_FLEET_FINDER_ENTRY)

    def GetHint(self):
        fleetAd = self.sr.node.fleet
        hint = ''
        hint += GetByLabel('UI/Fleet/FleetRegistry/AdvertDetails/HintFleetName', fleetName=fleetAd.fleetName) + '<br>'
        hint += GetByLabel('UI/Fleet/FleetRegistry/AdvertDetails/HintFleetBoss', charID=fleetAd.leader.charID) + '<br>'
        if fleetAd.standing is not None:
            hint += GetByLabel('UI/Fleet/FleetRegistry/AdvertDetails/HintBossStanding', standing=fleetAd.standing) + '<br>'
        if fleetAd.solarSystemID:
            hint += GetByLabel('UI/Fleet/FleetRegistry/AdvertDetails/HintFleetLocation', location=fleetAd.solarSystemID) + '<br>'
        hint += GetByLabel('UI/Fleet/FleetRegistry/AdvertDetails/HintFleetAge', fleetAge=blue.os.GetWallclockTime() - fleetAd.dateCreated) + '<br>'
        if fleetAd.numMembers:
            hint += GetByLabel('UI/Fleet/FleetRegistry/AdvertDetails/HintFleetMemberCount', memberCount=fleetAd.numMembers) + '<br>'
            if fleetAd.advertJoinLimit and fleetAd.numMembers >= fleetAd.advertJoinLimit:
                txt = GetByLabel('UI/Fleet/FleetRegistry/AdvertDetails/HintFleetMemberCountMoreThanLimit', advertJoinLimit=fleetAd.advertJoinLimit)
                hint += '<color=0xffdd0000>%s</color>' % txt + '<br>'
        hint += GetByLabel('UI/Fleet/FleetRegistry/AdvertDetails/HintScope') + '<br>'
        if evefleet.IsOpenToCorp(fleetAd):
            hint += GetByLabel('UI/Common/Corporation') + '<br>'
        if evefleet.IsOpenToAlliance(fleetAd):
            hint += GetByLabel('UI/Common/Alliance') + '<br>'
        if evefleet.IsOpenToMilitia(fleetAd):
            hint += GetByLabel('UI/Common/Militia') + '<br>'
        if fleetAd.membergroups_minStanding is not None:
            hint += GetByLabel('UI/Fleet/FleetRegistry/AdvertDetails/HintMinimumStanding', standing=fleetAd.membergroups_minStanding) + '<br>'
        if fleetAd.membergroups_minSecurity is not None:
            hint += GetByLabel('UI/Fleet/FleetRegistry/AdvertDetails/HintMinimumSecurity', security=fleetAd.membergroups_minSecurity) + '<br>'
        if evefleet.IsOpenToPublic(fleetAd):
            hint += GetByLabel('UI/Fleet/FleetRegistry/AdvertDetails/PublicAccessScope') + '<br>'
        elif evefleet.IsOpenToAllPublic(fleetAd):
            hint += '<b>%s</b>' % GetByLabel('UI/Agency/Fleetup/Public Access') + '<br>'
        if fleetAd.public_minStanding is not None:
            hint += GetByLabel('UI/Fleet/FleetRegistry/AdvertDetails/HintMinimumStanding', standing=fleetAd.public_minStanding) + '<br>'
        if fleetAd.public_minSecurity is not None:
            hint += GetByLabel('UI/Fleet/FleetRegistry/AdvertDetails/HintMinimumSecurity', security=fleetAd.public_minSecurity) + '<br>'
        if fleetAd.joinNeedsApproval:
            hint += GetByLabel('UI/Fleet/FleetRegistry/AdvertDetails/NeedsApproval') + '<br>'
        if fleetAd.description:
            hint += GetByLabel('UI/Fleet/FleetRegistry/AdvertDetails/HintFleetDescription', description=fleetAd.description)
        return hint

    def GetDragData(self, *args):
        data = evefleet.client.FleetDragData(fleet_id=self.sr.node.fleet.fleetID, name=self.sr.node.fleet.fleetName)
        return [data]
