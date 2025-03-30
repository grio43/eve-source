#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fleet\fleetCompositionWnd.py
from collections import defaultdict
import evetypes
import localization
from carbonui import uiconst, TextColor
from carbonui.control.button import Button
from carbonui.control.dragResizeCont import DragResizeCont
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control import eveLabel, eveScroll
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from carbonui.control.window import Window
from carbonui.control.tabGroup import TabGroup
from eve.client.script.ui.quickFilter import QuickFilterEdit
from eve.client.script.ui.shared.fleet import fleetbroadcastexports
from eve.client.script.ui.shared.fleet.entries import FleetCompositionEntry, FleetCompSummaryEntry
from eveexceptions import UserError
from eveservices.menu import GetMenuService
from menu import MenuLabel
from utillib import KeyVal
import blue

class FleetComposition(Window):
    default_windowID = 'FleetComposition'
    default_captionLabelPath = 'UI/Fleet/FleetComposition/FleetComposition'
    default_iconNum = 'res:/ui/Texture/WindowIcons/fleet.png'
    default_minSize = (390, 300)

    def ApplyAttributes(self, attributes):
        super(FleetComposition, self).ApplyAttributes(attributes)
        self.ConstructTop()
        self.tabGroup = TabGroup(name='tabGroup', parent=self.sr.main, settingsID='fleetComp')
        fleetComp = self.ConstructFleetComp()
        fleetSummary = self.ConstructFleetSummary()
        self.tabGroup.AddTab(localization.GetByLabel('UI/Fleet/FleetComposition/FleetComposition'), fleetComp, self, 'fleetComp')
        self.tabGroup.AddTab(localization.GetByLabel('UI/Fleet/FleetComposition/FleetSummary'), fleetSummary, self, 'fleetSummary')
        self.tabGroup.AutoSelect()

    def ConstructTop(self):
        self.sr.top = ContainerAutoSize(name='topCont', parent=self.sr.main, align=uiconst.TOTOP, alignMode=uiconst.TOTOP)
        refreshButtCont = Container(name='refreshButtCont', parent=self.sr.top, align=uiconst.TORIGHT, width=80)
        self.sr.refreshBtn = Button(parent=refreshButtCont, label=localization.GetByLabel('UI/Commands/Refresh'), left=2, func=self.RefreshClick, align=uiconst.TOPRIGHT)
        eveLabel.EveLabelMedium(text=localization.GetByLabel('UI/Fleet/FleetComposition/FleetCompositionHelp'), parent=self.sr.top, align=uiconst.TOTOP, color=TextColor.SECONDARY, padding=(0, 0, 0, 8))

    def ConstructFleetComp(self):
        fleetComp = Container(name='fleetComp', parent=self.sr.main)
        self.topCont = Container(name='topCont', parent=fleetComp, align=uiconst.TOTOP)
        self.filterEdit = QuickFilterEdit(name='filterEdit', parent=self.topCont, hintText=localization.GetByLabel('UI/Inventory/Filter'), maxLength=64, left=4, align=uiconst.TOPRIGHT, OnClearFilter=self.OnFilterEditCleared, width=120)
        self.topCont.height = self.filterEdit.height + 4
        self.filterEdit.ReloadFunction = self.OnFilterEdit
        self.sr.bottom = Container(name='bottomCont', parent=fleetComp, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        self.counterLabel = eveLabel.EveLabelMedium(text='', parent=self.sr.bottom, align=uiconst.TOBOTTOM, padRight=4, padTop=4)
        self.sr.fleetCompScroll = eveScroll.Scroll(name='scrollComposition', parent=self.sr.bottom)
        self.sr.fleetCompScroll.OnSelectionChange = self.OnScrollSelectionChange
        self.sr.fleetCompScroll.sr.id = 'scrollComposition'
        return fleetComp

    def ConstructFleetSummary(self):
        fleetSummary = Container(name='fleetSummary', parent=self.sr.main)
        bytGroupCont = DragResizeCont(name='bytGroupCont', parent=fleetSummary, align=uiconst.TOBOTTOM, settingsID='fleetcompsummary_ContProporations', minSize=0.2, maxSize=0.8)
        byTypeCont = Container(name='bytGroupCont', parent=fleetSummary)
        self.fleetSummaryTypeScroll = eveScroll.Scroll(name='fleeSummaryTypeScroll', parent=byTypeCont)
        self.fleetSummaryTypeScroll.sr.id = 'fleeSummaryTypeScroll'
        self.fleetSummaryGroupScroll = eveScroll.Scroll(name='fleeSummaryGroupScroll', parent=bytGroupCont)
        self.fleetSummaryGroupScroll.sr.id = 'fleeSummaryGroupScroll'
        return fleetSummary

    def Load(self, key):
        if key == 'fleetComp':
            self.LoadComposition()
        elif key == 'fleetSummary':
            self.LoadSummary()

    def LoadComposition(self):
        fleetSvc = sm.GetService('fleet')
        if not fleetSvc.IsCommanderOrBoss():
            raise UserError('FleetNotCommanderOrBoss')
        filterText = self.filterEdit.GetValue()
        scrolllist = []
        composition = fleetSvc.GetFleetComposition()
        fleetHierarchy = fleetSvc.GetFleetHierarchy()
        fleetPositionText = localization.GetByLabel('UI/Fleet/FleetWindow/FleetPosition')
        for kv in composition:
            blue.pyos.BeNice()
            member = fleetSvc.GetMemberInfo(kv.characterID, fleetHierarchy)
            if member is None:
                continue
            if not fleetSvc.IsMySubordinate(kv.characterID) and not fleetSvc.IsBoss():
                continue
            data = KeyVal()
            charName = localization.GetByLabel('UI/Common/CharacterNameLabel', charID=kv.characterID)
            locationName = localization.GetByLabel('UI/Common/LocationDynamic', location=kv.solarSystemID)
            if kv.stationID:
                locationName = '%s %s' % (locationName, localization.GetByLabel('UI/Fleet/FleetComposition/Docked'))
            if kv.shipTypeID is not None:
                shipTypeName = evetypes.GetName(kv.shipTypeID)
                shipGroupName = evetypes.GetGroupName(kv.shipTypeID)
            else:
                shipTypeName = ''
                shipGroupName = ''
            if kv.skills:
                skillLevels = localization.GetByLabel('UI/Fleet/FleetComposition/SkillLevels', skillLevelA=kv.skills[2], skillLevelB=kv.skills[1], skillLevelC=kv.skills[0])
                data.hint = localization.GetByLabel('UI/Fleet/FleetComposition/SkillsHint', skillTypeA=kv.skillIDs[2], skillLevelA=kv.skills[2], skillTypeB=kv.skillIDs[1], skillLevelB=kv.skills[1], skillTypeC=kv.skillIDs[0], skillLevelC=kv.skills[0])
            else:
                skillLevels = ''
            if not member.wingName:
                fleetPosition = ''
                positionSortValue = (None, None)
            elif not member.squadName:
                fleetPosition = member.wingName
                positionSortValue = (fleetPosition, None)
            else:
                fleetPosition = '%s / %s ' % (member.wingName, member.squadName)
                positionSortValue = (member.wingName, member.squadName)
            data.label = '<t>'.join([charName,
             locationName,
             shipTypeName,
             shipGroupName,
             member.roleName,
             skillLevels,
             fleetPosition])
            if filterText and data.label.lower().find(filterText) < 0:
                continue
            data.GetMenu = self.OnCompositionEntryMenu
            data.cfgname = charName
            data.retval = None
            data.charID = kv.characterID
            data.shipTypeID = kv.shipTypeID
            data.solarSystemID = kv.solarSystemID
            data.info = cfg.eveowners.Get(kv.characterID)
            data.Set('sort_%s' % fleetPositionText, positionSortValue)
            scrolllist.append(GetFromClass(FleetCompositionEntry, data))

        self.counterLabel.text = localization.GetByLabel('UI/Fleet/FleetComposition/PilotsSelected', numSelected=0, numTotalPilots=len(scrolllist))
        headers = [localization.GetByLabel('UI/Common/Name'),
         localization.GetByLabel('UI/Common/Location'),
         localization.GetByLabel('UI/Fleet/FleetComposition/ShipType'),
         localization.GetByLabel('UI/Fleet/FleetComposition/ShipGroup'),
         localization.GetByLabel('UI/Fleet/FleetComposition/FleetRole'),
         localization.GetByLabel('UI/Fleet/FleetComposition/FleetSkills'),
         fleetPositionText]
        self.sr.fleetCompScroll.Load(headers=headers, contentList=scrolllist, noContentHint=localization.GetByLabel('UI/Common/NothingFound'))

    def OnScrollSelectionChange(self, selectedList, *args):
        totalPilots = len(self.sr.fleetCompScroll.GetNodes())
        selectedPilots = len(selectedList)
        self.counterLabel.text = localization.GetByLabel('UI/Fleet/FleetComposition/PilotsSelected', numSelected=selectedPilots, numTotalPilots=totalPilots)

    def OnCompositionEntryMenu(self, entry):
        m = []
        data = entry.sr.node
        m += fleetbroadcastexports.GetMenu_Member(data.charID)
        if data.solarSystemID:
            m += [(MenuLabel('UI/Common/SolarSystem'), GetMenuService().CelestialMenu(data.solarSystemID))]
        if data.shipTypeID:
            m += [(MenuLabel('UI/Common/Ship'), GetMenuService().GetMenuFromItemIDTypeID(None, data.shipTypeID, includeMarketDetails=True))]
        return m

    def RefreshClick(self, *args):
        self.LoadComposition()

    def OnFilterEditCleared(self):
        self.LoadComposition()

    def OnFilterEdit(self):
        self.LoadComposition()

    def LoadSummary(self):
        composition = sm.GetService('fleet').GetFleetComposition()
        unknownNum = 0
        numByShipTypeID = defaultdict(int)
        numByShipGroupID = defaultdict(int)
        for kv in composition:
            if kv.shipTypeID is None:
                unknownNum += 1
            else:
                numByShipTypeID[kv.shipTypeID] += 1
                numByShipGroupID[evetypes.GetGroupID(kv.shipTypeID)] += 1

        byTypeScrollList = []
        for shipTypeID, numShip in numByShipTypeID.iteritems():
            sort_key = 'sort_%s' % localization.GetByLabel('UI/Fleet/FleetComposition/NumShips')
            entry = GetFromClass(FleetCompSummaryEntry, {'typeID': shipTypeID,
             'label': '<t>'.join([evetypes.GetName(shipTypeID), evetypes.GetGroupName(shipTypeID), '<right>%s</right>' % numShip]),
             sort_key: numShip})
            byTypeScrollList.append(entry)

        byGroupScrollList = []
        for groupID, numShip in numByShipGroupID.iteritems():
            entry = GetFromClass(Generic, {'label': '<t>'.join([evetypes.GetGroupNameByGroup(groupID), '<right>%s</right>' % numShip]),
             'sort_%s' % localization.GetByLabel('UI/Fleet/FleetComposition/NumShips'): numShip})
            byGroupScrollList.append(entry)

        if unknownNum:
            entry = GetFromClass(Generic, {'label': '<t>'.join([localization.GetByLabel('UI/Fleet/FleetComposition/UnknownShipTypeID'), '', '<right>%s</right>' % unknownNum]),
             'sort_%s' % localization.GetByLabel('UI/Fleet/FleetComposition/NumShips'): unknownNum})
            byTypeScrollList.append(entry)
            entry = GetFromClass(Generic, {'label': '<t>'.join([localization.GetByLabel('UI/Fleet/FleetComposition/UnknownShipTypeID'), '<right>%s</right>' % unknownNum]),
             'sort_%s' % localization.GetByLabel('UI/Fleet/FleetComposition/NumShips'): unknownNum})
            byGroupScrollList.append(entry)
        headers = [localization.GetByLabel('UI/Fleet/FleetComposition/ShipType'), localization.GetByLabel('UI/Fleet/FleetComposition/ShipGroup'), localization.GetByLabel('UI/Fleet/FleetComposition/NumShips')]
        self.fleetSummaryTypeScroll.Load(headers=headers, contentList=byTypeScrollList)
        headers = [localization.GetByLabel('UI/Fleet/FleetComposition/ShipGroup'), localization.GetByLabel('UI/Fleet/FleetComposition/NumShips')]
        self.fleetSummaryGroupScroll.Load(headers=headers, contentList=byGroupScrollList)
