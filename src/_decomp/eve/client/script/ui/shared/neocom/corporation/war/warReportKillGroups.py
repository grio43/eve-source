#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\war\warReportKillGroups.py
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from carbonui.primitives.gridcontainer import GridContainer
from carbonui.primitives.line import Line
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from eve.client.script.ui.shared.neocom.corporation.war.warReportKillBarContainer import KillsBarContainer
from eve.common.script.util.eveFormat import FmtISK
from localization import GetByLabel
from carbonui.util.color import Color

class WarReportKillsByGroupParent(Container):
    default_align = uiconst.TOTOP
    default_name = 'killsByGroupParent'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.getKillFunc = attributes.getKillFunc
        self.loadFunc = attributes.loadFunc
        self.groupLabels = []
        killGroupsCont = Container(name='killsFilterCont', parent=self, align=uiconst.TOALL)
        self.killGroupsTextCont = Container(name='killGroupsTextCont', parent=killGroupsCont, align=uiconst.TOLEFT, width=90)
        self.killGroupsLegendCont = Container(name='killGroupsLegendCont', parent=killGroupsCont, align=uiconst.TOBOTTOM, height=20)
        self.killGroupsDataCont = Container(name='killGroupsDataCont', parent=killGroupsCont, align=uiconst.TOALL, padding=(const.defaultPadding,
         0,
         0,
         const.defaultPadding), bgColor=Color.GetGrayRGBA(0.4, 0.2))

    def FlushContainers(self):
        self.killGroupsTextCont.Flush()
        self.killGroupsDataCont.Flush()
        self.killGroupsLegendCont.Flush()

    def DrawKillsByGroup(self, killsByShipGroup, warReportController, maxKills = 10):
        self.FlushContainers()
        groupCont = Container(name='groupCont', parent=self.killGroupsDataCont)
        parentLineCont = GridContainer(name='parentLineCont', parent=self.killGroupsDataCont, lines=1, columns=10)
        top = 2
        self.groupLabels = []
        for shipGroup in self.GetShipGroupList():
            shipGroupKills = killsByShipGroup[shipGroup]
            labelText = self.GetShipGroupName(shipGroup)
            groupLabel = EveLabelSmall(text=GetByLabel(labelText), parent=self.killGroupsTextCont, top=top, left=const.defaultPadding, state=uiconst.UI_NORMAL, align=uiconst.TOPRIGHT)
            groupLabel.OnClick = (self.GetBarAndClick, shipGroup)
            if shipGroupKills.attackerKills == 0 and shipGroupKills.defenderKills == 0:
                groupLabel.SetAlpha(0.5)
            top += 18
            self.groupLabels.append(groupLabel)
            self.CreateBarContainer(groupCont, shipGroup, shipGroupKills, warReportController, maxKills)

        w, h = self.killGroupsDataCont.GetAbsoluteSize()
        legendmin = EveLabelSmall(parent=self.killGroupsLegendCont, text=GetByLabel('UI/Corporations/Wars/Legend', legend=FmtISK(0)), align=uiconst.TOPLEFT)
        legendmax = EveLabelSmall(parent=self.killGroupsLegendCont, text=GetByLabel('UI/Corporations/Wars/Legend', legend=FmtISK(maxKills)), align=uiconst.TOPRIGHT, left=4)
        for x in xrange(parentLineCont.columns):
            Line(parent=parentLineCont, align=uiconst.TORIGHT, color=(1.0, 1.0, 1.0, 0.1))

        self.displayGroup = settings.user.ui.Get('killGroupDisplayed', None)
        maxWidth = self.GetGroupLabelWidth()
        self.killGroupsTextCont.width = maxWidth + 10
        if self.displayGroup is not None:
            selectedBar = self._GetBarForGroupID(self.displayGroup)
            self._SetBarDisplayStateAsSelected(selectedBar)

    def CreateBarContainer(self, parent, groupID, killsByShipGroup, warReportController, maxKills):
        attackerKills = killsByShipGroup.attackerKills
        defenderKills = killsByShipGroup.defenderKills
        attackerKillsIsk = killsByShipGroup.attackerKillsIsk
        defenderKillsIsk = killsByShipGroup.defenderKillsIsk
        contName = 'group_%d' % groupID
        barCont = KillsBarContainer(name=contName, parent=parent, attackerID=warReportController.GetAttackerID(), defenderID=warReportController.GetDefenderID(), attackerKills=attackerKills, defenderKills=defenderKills, attackerKillsIsk=attackerKillsIsk, defenderKillsIsk=defenderKillsIsk, groupID=groupID, maxKills=maxKills)
        setattr(self.sr, contName, barCont)
        barCont.OnClick = (self.BarOnClick, groupID, barCont)

    def GetBarAndClick(self, groupID, *args):
        bar = self._GetBarForGroupID(groupID)
        self.BarOnClick(groupID, bar)

    def _GetBarForGroupID(self, groupID):
        groupName = 'group_%d' % groupID
        bar = getattr(self.sr, groupName, None)
        return bar

    def BarOnClick(self, groupID, container, *args):
        if self.displayGroup == groupID:
            groupID = None
        settings.user.ui.Set('killGroupDisplayed', groupID)
        self.displayGroup = groupID
        self._UnselectBars()
        if groupID is not None:
            self._SetBarDisplayStateAsSelected(container)
        self.loadFunc(groupID)

    def _SetBarDisplayStateAsSelected(self, container):
        container.selected.display = True

    def _UnselectBars(self):
        for i in xrange(len(self.GetShipGroupList())):
            cont = self.sr.Get('group_%d' % i)
            cont.selected.display = False

    def GetShipGroupList(self):
        return [const.GROUP_CAPSULES,
         const.GROUP_FRIGATES,
         const.GROUP_DESTROYERS,
         const.GROUP_CRUISERS,
         const.GROUP_BATTLECRUISERS,
         const.GROUP_BATTLESHIPS,
         const.GROUP_INDUSTRIALS,
         const.GROUP_CAPITALSHIPS,
         const.GROUP_STRUCTURES,
         const.GROUP_POS]

    def GetShipGroupName(self, shipGroup):
        return self.GetShipGroupNamesByGroupID()[shipGroup]

    def GetShipGroupNamesByGroupID(self):
        return {const.GROUP_CAPSULES: 'UI/Corporations/Wars/ShipGroups/Capsules',
         const.GROUP_FRIGATES: 'UI/Corporations/Wars/ShipGroups/Frigate',
         const.GROUP_DESTROYERS: 'UI/Corporations/Wars/ShipGroups/Destroyers',
         const.GROUP_CRUISERS: 'UI/Corporations/Wars/ShipGroups/Cruisers',
         const.GROUP_BATTLECRUISERS: 'UI/Corporations/Wars/ShipGroups/Battlecruisers',
         const.GROUP_BATTLESHIPS: 'UI/Corporations/Wars/ShipGroups/Battleships',
         const.GROUP_CAPITALSHIPS: 'UI/Corporations/Wars/ShipGroups/CapitalShips',
         const.GROUP_INDUSTRIALS: 'UI/Corporations/Wars/ShipGroups/IndustrialShips',
         const.GROUP_POS: 'UI/Corporations/Wars/ShipGroups/POS',
         const.GROUP_STRUCTURES: 'UI/Corporations/Wars/ShipGroups/Structures'}

    def GetGroupLabelWidth(self):
        maxWidth = 0
        for label in self.groupLabels:
            maxWidth = max(maxWidth, label.textwidth)

        return maxWidth
