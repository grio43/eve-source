#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\tournamentRefereeTools.py
from collections import namedtuple
import blue
import carbonui.const as uiconst
import evetypes
import localization
import telemetry
import tournamentmanagement.const as tourneyConst
import uthread
import utillib
from carbon.common.script.sys.service import Service
from carbon.common.script.util import timerstuff
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.control.button import Button
from carbonui.control.combo import Combo
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.uicore import uicore
from carbonui.util.various_unsorted import MapIcon, SortListOfTuples, Transplant
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveIcon import Icon
from carbonui.control.window import Window
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.util import uix
from eve.client.script.ui.control import eveIcon, eveLabel, eveScroll
from eve.common.lib import appConst as const
from eve.common.script.net import eveMoniker
from eveexceptions import UserError
from eveservices.menu import GetMenuService
EntryRow = namedtuple('EntryRow', 'character groupName typeName maxDistance distance')
EntryRow.__guid__ = 'at.EntryRow'
WINDOW_WIDTH = 525
MINCOLWIDTH = 16

class ColumnLine(SE_BaseClassCore):
    __guid__ = 'listentry.ColumnLine'

    def __init__(self, **kwargs):
        self.overlay = None
        super(ColumnLine, self).__init__(**kwargs)

    @telemetry.ZONE_METHOD
    def Startup(self, args):
        self._clicks = 0
        self.clickTimer = None
        self.columns = []
        self.cursor = uiconst.UICURSOR_DEFAULT

    @telemetry.ZONE_METHOD
    def Load(self, node):
        self.LoadLite(node)
        node.needReload = 0
        if node.Get('selectable', 1) and node.Get('selected', 0):
            self.Select()
        else:
            self.Deselect()
        if self.overlay is not None:
            if self.overlay.parent == self:
                self.overlay.SetParent(None)
            self.overlay = None
        if node.Get('overlay', None) is not None:
            node.overlay.SetParent(self, idx=0)
            self.overlay = node.overlay
        self.UpdateOverlay()
        self.UpdateTriangles()

    def _OnSizeChange_NoBlock(self, *args):
        self.UpdateOverlay()

    def UpdateOverlay(self):
        if self.overlay is not None:
            customTabstops = GetCustomTabstops(self.sr.node.columnID)
            if customTabstops:
                totalColWidth = sum(customTabstops)
            else:
                totalColWidth = sum([ each.width for each in self.columns ])
            self.overlay.left = max(totalColWidth, self.width - self.overlay.width)

    def LoadLite(self, node):
        i = 0
        for each in node.texts:
            self.LoadColumn(i, each)
            i += 1

        for each in self.columns[i:]:
            each.Close()

        self.columns = self.columns[:i]
        self.UpdateColumnOrder(0)

    @telemetry.ZONE_METHOD
    def UpdateColumnOrder(self, updateEntries = 1, onlyVisible = False):
        displayOrder = settings.user.ui.Get('columnDisplayOrder_%s' % self.sr.node.columnID, None) or [ i for i in xrange(len(self.columns)) ]
        customTabstops = GetCustomTabstops(self.sr.node.columnID)
        if displayOrder is not None and len(displayOrder) == len(self.columns):
            left = 0
            for columnIdx in displayOrder:
                colWidth = customTabstops[columnIdx]
                col = self.columns[columnIdx]
                col.left = left
                col.width = colWidth
                if not self.sr.node.Get('editable', 0):
                    col.width -= 2
                left += colWidth

        self.sr.node.customTabstops = customTabstops
        if updateEntries:
            associates = self.FindAssociatingEntries()
            for node in associates:
                if node.panel and (not onlyVisible or onlyVisible and node.panel.state != uiconst.UI_HIDDEN):
                    node.panel.UpdateColumnOrder(0)
                    node.panel.UpdateOverlay()

    def OnMouseEnter(self, *args):
        SE_BaseClassCore.OnMouseEnter(self, *args)
        if self.sr.node:
            if self.sr.node.Get('OnMouseEnter', None):
                self.sr.node.OnMouseEnter(self)

    def OnMouseExit(self, *args):
        SE_BaseClassCore.OnMouseExit(self, *args)
        if self.sr.node:
            if self.sr.node.Get('OnMouseExit', None):
                self.sr.node.OnMouseExit(self)

    def OnClick(self, *args):
        if self.sr.node:
            if self.sr.node.Get('selectable', 1):
                self.sr.node.scroll.SelectNode(self.sr.node)
            eve.Message('ListEntryClick')
            if self.sr.node.Get('OnClick', None):
                self.sr.node.OnClick(self)

    def GetMenu(self):
        if self.sr.node and self.sr.node.Get('scroll', None) and getattr(self.sr.node.scroll, 'GetSelectedNodes', None):
            self.sr.node.scroll.GetSelectedNodes(self.sr.node)
        if self.sr.node and self.sr.node.Get('GetMenu', None):
            return self.sr.node.GetMenu(self)
        if getattr(self, 'itemID', None) or getattr(self, 'typeID', None):
            return GetMenuService().GetMenuFromItemIDTypeID(getattr(self, 'itemID', None), getattr(self, 'typeID', None))
        return []

    def LoadColumn(self, idx, textOrObject):
        node = self.sr.node
        if len(self.columns) > idx:
            col = self.columns[idx]
            col.height = self.height
        else:
            col = Container(name='column_%s' % idx, parent=self, align=uiconst.TOPLEFT, height=self.height, clipChildren=1, state=uiconst.UI_PICKCHILDREN, idx=0)
            col.textCtrl = eveLabel.Label(text='', parent=col, fontsize=self.sr.node.Get('fontsize', 12), letterspace=self.sr.node.Get('letterspace', 0), uppercase=self.sr.node.Get('uppercase', 0), state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT, maxLines=1)
            col.textCtrl.left = self.sr.node.Get('padLeft', 6)
            col.editHandle = None
            col.triangle = None
            col.columnIdx = idx
            col.OnDblClick = (self.OnHeaderDblClick, col)
            col.OnClick = (self.OnHeaderClick, col)
            col.GetMenu = lambda *args: self.OnHeaderGetMenu(col)
            col.cursor = uiconst.UICURSOR_DEFAULT
            self.columns.append(col)
        for each in col.children[:]:
            if each not in (col.textCtrl,
             col.editHandle,
             col.triangle,
             textOrObject):
                each.Close()

        if isinstance(textOrObject, basestring):
            col.textCtrl.state = uiconst.UI_DISABLED
            col.textCtrl.text = textOrObject
        else:
            col.textCtrl.state = uiconst.UI_HIDDEN
            if textOrObject not in col.children:
                Transplant(textOrObject, col, 0)
        if self.sr.node.Get('editable', 0):
            col.state = uiconst.UI_NORMAL
            if col.editHandle:
                col.editHandle.state = uiconst.UI_NORMAL
            else:
                par = Container(name='scaleHandle_%s' % idx, parent=col, align=uiconst.TOPRIGHT, height=self.height - 2, width=5, idx=0, state=uiconst.UI_NORMAL)
                par.OnMouseDown = (self.StartScaleCol, par)
                par.OnMouseUp = (self.EndScaleCol, par)
                par.OnMouseMove = (self.ScalingCol, par)
                par.cursor = uiconst.UICORSOR_HORIZONTAL_RESIZE
                par.columnIdx = idx
                col.editHandle = par
        else:
            col.state = uiconst.UI_PICKCHILDREN
            if col.editHandle:
                col.editHandle.state = uiconst.UI_HIDDEN

    def FindAssociatingEntries(self):
        ret = []
        for node in self.sr.node.scroll.GetNodes()[self.sr.node.idx + 1:]:
            if node.Get('columnID', None) == self.sr.node.columnID:
                ret.append(node)

        return ret

    def GetHeight(self, *args):
        node, _ = args
        node.height = uix.GetTextHeight(''.join([ text for text in node.texts if isinstance(text, basestring) ]), maxLines=1) + 1
        return node.height

    def StartScaleCol(self, sender, *args):
        if uicore.uilib.rightbtn:
            return
        l, t, w, h = sender.parent.GetAbsolute()
        sl, st, sw, sh = sender.GetAbsolute()
        associates = self.FindAssociatingEntries()
        self._startScalePosition = uicore.uilib.x
        self._startScalePositionDiff = sl - uicore.uilib.x
        self._scaleColumnIdx = sender.columnIdx
        self._scaleColumnInitialWidth = sender.parent.width
        self._minLeft = l + MINCOLWIDTH
        self.scaleEntries = associates
        self.ScalingCol(sender)

    def ScalingCol(self, sender, *args):
        if getattr(self, '_startScalePosition', None):
            diff = uicore.uilib.x - self._startScalePosition
            sender.parent.width = max(MINCOLWIDTH, self._scaleColumnInitialWidth + diff)
            self.sr.node.customTabstops[self._scaleColumnIdx] = sender.parent.width
            self.UpdateColumnOrder(onlyVisible=True)

    def EndScaleCol(self, sender, *args):
        prefsID = self.sr.node.Get('columnID', None)
        if prefsID:
            current = settings.user.ui.Get('listentryColumns_%s' % prefsID, self.sr.node.customTabstops)
            current[self._scaleColumnIdx] = sender.parent.width
            settings.user.ui.Set('listentryColumns_%s' % prefsID, current)
        self.sr.node.customTabstops[self._scaleColumnIdx] = sender.parent.width
        self.scaleEntries = None
        self._startScalePosition = 0

    def ChangeSort(self, sender, *args):
        columnID = self.sr.node.Get('columnID', None)
        if columnID:
            current = settings.user.ui.Get('columnSorts_%s' % columnID, {})
            if sender.columnIdx in current:
                direction = not current[sender.columnIdx]
            else:
                direction = False
            current[sender.columnIdx] = direction
            settings.user.ui.Set('columnSorts_%s' % columnID, current)
            current = settings.user.ui.Get('activeSortColumns', {})
            current[columnID] = sender.columnIdx
            settings.user.ui.Set('activeSortColumns', current)
        self.UpdateTriangles()
        self.UpdateColumnOrder()
        associates = self.FindAssociatingEntries()
        self.UpdateColumnSort(associates, columnID)
        callback = self.sr.node.Get('OnSortChange', None)
        if callback:
            callback()

    def UpdateColumnSort(self, entries, columnID):
        if not entries:
            return
        startIdx = entries[0].idx
        endIdx = entries[-1].idx
        entries = SortColumnEntries(entries, columnID)
        self.sr.node.scroll.sr.nodes = self.sr.node.scroll.sr.nodes[:startIdx] + entries + self.sr.node.scroll.sr.nodes[endIdx + 1:]
        idx = 0
        for entry in self.sr.node.scroll.GetNodes()[startIdx:]:
            if entry.Get('needReload', 0) and entry.panel:
                entry.panel.LoadLite(entry)
            idx += 1

        self.sr.node.scroll.UpdatePosition()

    def GetSortDirections(self):
        prefsID = self.sr.node.Get('columnID', None)
        if prefsID:
            return settings.user.ui.Get('columnSorts_%s' % prefsID, {})
        return {}

    def OnHeaderDblClick(self, sender, *args):
        self._clicks += 1
        self.ExecClick(sender)

    def OnHeaderClick(self, sender, *args):
        self._clicks += 1
        self.clickTimer = AutoTimer(250, self.ExecClick, sender)

    def OnHeaderGetMenu(self, sender, *args):
        m = [(localization.GetByLabel('UI/Control/Entries/ColumnMoveForward'), self.ChangeColumnOrder, (sender, -1)), (localization.GetByLabel('UI/Control/Entries/ColumnMoveBackward'), self.ChangeColumnOrder, (sender, 1))]
        return m

    def ChangeColumnOrder(self, column, direction):
        currentDisplayOrder = settings.user.ui.Get('columnDisplayOrder_%s' % self.sr.node.columnID, None) or [ i for i in xrange(len(self.sr.node.texts)) ]
        newDisplayOrder = currentDisplayOrder[:]
        currentlyInDisplayOrder = currentDisplayOrder.index(column.columnIdx)
        newDisplayOrder.pop(currentlyInDisplayOrder)
        newDisplayOrder.insert(max(0, direction + currentlyInDisplayOrder), column.columnIdx)
        settings.user.ui.Set('columnDisplayOrder_%s' % self.sr.node.columnID, newDisplayOrder)
        self.UpdateColumnOrder()

    def ExecClick(self, sender, *args):
        if self._clicks > 1:
            self.ResetColumn(sender)
        elif self._clicks == 1:
            self.ChangeSort(sender)
        if not self.destroyed:
            self._clicks = 0
            self.clickTimer = None

    def ResetColumn(self, sender, *args):
        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        if shift:
            idxs = []
            for i in xrange(len(self.sr.node.texts)):
                idxs.append(i)

        else:
            idxs = [sender.columnIdx]
        associates = self.FindAssociatingEntries()
        for columnIdx in idxs:
            textsInColumn = []
            columnWidths = []
            for node in [self.sr.node] + associates:
                text = node.texts[columnIdx]
                textsInColumn.append(text)
                padLeft = node.Get('padLeft', 6)
                padRight = node.Get('padRight', 6)
                fontsize = node.Get('fontsize', 12)
                hspace = node.Get('letterspace', 0)
                uppercase = node.Get('uppercase', 0)
                extraSpace = 0
                if node is self.sr.node and self.sr.node.Get('editable', 0):
                    extraSpace = 10
                if isinstance(text, basestring):
                    textWidth = uix.GetTextWidth(text, fontsize, hspace, uppercase)
                    if text:
                        columnWidths.append(padLeft + textWidth + padRight + 3 + extraSpace)
                    else:
                        columnWidths.append(3 + extraSpace)
                else:
                    textWidth = text.width
                    columnWidths.append(text.width)

            self.sr.node.customTabstops[columnIdx] = newWidth = max(columnWidths)
            self.UpdateColumnOrder()

    def UpdateTriangles(self):
        activeColumn = settings.user.ui.Get('activeSortColumns', {}).get(self.sr.node.columnID, 0)
        sortDirections = self.GetSortDirections()
        for column in self.columns:
            direction = sortDirections.get(column.columnIdx, True)
            if column.columnIdx == activeColumn and self.sr.node.Get('editable', 0):
                if not column.triangle:
                    column.triangle = Icon(align=uiconst.CENTERRIGHT, pos=(3, 0, 16, 16), parent=column, idx=0, name='directionIcon', icon='ui_1_16_16')
                column.triangle.state = uiconst.UI_DISABLED
                if direction == 1:
                    MapIcon(column.triangle, 'ui_1_16_16')
                else:
                    MapIcon(column.triangle, 'ui_1_16_15')
            elif column.triangle:
                column.triangle.state = uiconst.UI_HIDDEN

    @classmethod
    def GetCopyData(cls, node):
        displayOrder = settings.user.ui.Get('columnDisplayOrder_%s' % node.columnID, None) or [ i for i in xrange(len(node.texts)) ]
        retString = []
        for i in displayOrder:
            if i <= len(node.texts) - 1:
                retString.append(node.texts[i])

        return '<t>'.join(retString)


def GetCustomTabstops(columnID):
    return settings.user.ui.Get('listentryColumns_%s' % columnID, None)


def SortColumnEntries(nodes, columnID):
    if not nodes:
        return nodes
    displayOrder = settings.user.ui.Get('columnDisplayOrder_%s' % columnID, None) or [ i for i in xrange(len(nodes[0].sortData)) ]
    c = 0
    sortData = []
    for node in nodes:
        if not c:
            c = len(node.sortData)
        elif c != len(node.sortData):
            raise RuntimeError('Mismatch in column sizes')
        sortData.append((ReorderSortData(node.sortData[:], columnID, displayOrder), node))

    sortDirections = settings.user.ui.Get('columnSorts_%s' % columnID, [0, {}])
    sortData = SortListOfTuples(sortData)
    activeColumn = settings.user.ui.Get('activeSortColumns', {}).get(columnID, 0)
    if activeColumn in sortDirections and sortDirections[activeColumn] is False:
        sortData.reverse()
    return sortData


def ReorderSortData(sortData, columnID, displayOrder):
    if not sortData:
        return sortData
    if len(displayOrder) != len(sortData):
        return sortData
    ret = []
    activeColumn = settings.user.ui.Get('activeSortColumns', {}).get(columnID, 0)
    if activeColumn in displayOrder:
        di = displayOrder.index(activeColumn)
    else:
        di = 0
    for columnIdx in displayOrder[di:]:
        ret.append(sortData[columnIdx])

    return ret


def InitCustomTabstops(columnID, entries):
    idxs = []
    for i in xrange(len(entries[0].texts)):
        idxs.append(i)

    if not len(idxs):
        return
    current = GetCustomTabstops(columnID)
    if current is not None:
        if len(current) == len(idxs):
            return
    retval = []
    for columnIdx in idxs:
        textsInColumn = []
        columnWidths = []
        for node in entries:
            text = node.texts[columnIdx]
            textsInColumn.append(text)
            padLeft = node.Get('padLeft', 6)
            padRight = node.Get('padRight', 6)
            fontsize = node.Get('fontsize', 12)
            hspace = node.Get('letterspace', 0)
            uppercase = node.Get('uppercase', 0)
            if isinstance(text, basestring):
                textWidth = uix.GetTextWidth(text, fontsize, hspace, uppercase)
            else:
                textWidth = text.width
            extraSpace = 0
            if node.Get('editable', 0):
                extraSpace = 10
            columnWidths.append(padLeft + textWidth + padRight + 3 + extraSpace)

        retval.append(max(columnWidths))

    settings.user.ui.Set('listentryColumns_%s' % columnID, retval)


class AtCompetitorEntry(ColumnLine):
    __guid__ = 'listentry.AtCompetitorEntry'

    def Startup(self, args):
        super(AtCompetitorEntry, self).Startup(args)
        self.warn = Fill(name='warn', parent=self, padTop=1, color=(1.0, 0.0, 0.0, 0.125), state=uiconst.UI_HIDDEN)


class TournamentRefereeTool(Window):
    __guid__ = 'form.TournamentRefereeTool'
    __notifyevents__ = ['OnCompetitorTrackingUpdate', 'OnCompetitorTrackingStart', 'OnRemovalAsRef']
    default_arenaRadius = 125
    default_windowID = 'TournamentRefereeTool'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.SetCaption('Tournament Referee Tool')
        self.SetMinSize((WINDOW_WIDTH, 550))
        self.centerItemID = None
        self.arenaRadius = 125000
        self.isToggling = False
        self.playersCanLock = True
        self.playersCanWarp = True
        self.matchDetails = [None,
         None,
         None,
         None]
        self.ConstructLayout()
        sm.RegisterForNotifyEvent(self, 'ProcessTournamentMatchUpdate')
        self.solarsystemID = None
        self.pregameRangeTimer = None
        self.countdownTimer = None

    def ConstructLayout(self):
        localTournamentService = sm.GetService('allianceTournamentSvc')
        tourneyMgr = sm.RemoteSvc('tourneyMgr')
        tournaments, tourneySystems, activeSystems = tourneyMgr.GetTourneySetup()
        locations = []
        for systemID, (_combatBeacons, _warpBubbles) in tourneySystems.iteritems():
            locations.append(systemID)

        uthread.new(cfg.evelocations.Prime, locations)
        self.beaconOptions = {'red': [('1A', 0),
                 ('1B', 1),
                 ('1C', 2),
                 ('1D', 3)],
         'blue': [('2A', 0),
                  ('2B', 1),
                  ('2C', 2),
                  ('2D', 3)]}
        self.resetButton = Button(label='Reset Match', parent=self.content, align=uiconst.TOBOTTOM, func=self.ResetMatch, state=uiconst.UI_HIDDEN, padding=(0, 4, 0, 0))
        tourneyOptions = []
        for tourneyID, name in tournaments.iteritems():
            if len(tourneyMgr.GetPotentialMatches(tourneyID)) > 0:
                tourneyOptions.append((name, tourneyID))

        systemOptions = []
        defaultSelectSolarSystem = '__random__'
        for systemID in tourneySystems:
            systemName = cfg.evelocations.Get(systemID).locationName
            if systemID in activeSystems:
                systemName = '!' + systemName + ' - IN USE!'
            systemOptions.append((systemName, systemID))
            if systemID == session.solarsystemid:
                defaultSelectSolarSystem = systemID

        self.allianceSelections = ContainerAutoSize(name='aliSelect', parent=self.content, align=uiconst.TOTOP)
        self.pointOptions = []
        self.banOptions = []

        def TourneySelChanged(_combo, _tName, tourneyID):
            if tourneyID is None:
                self.matchSelect.options = []
            else:
                possibleMatches = tourneyMgr.GetPotentialMatches(tourneyID)
                menuOptions = []
                allDetails = tourneyMgr.GetAllCurrentSeriesMatchDetails(tourneyID)
                for seriesID, details in possibleMatches.iteritems():
                    seriesText = '[S%d M%d/%d] %s vs %s' % (seriesID + 1,
                     allDetails[seriesID][0] + 1,
                     allDetails[seriesID][1],
                     details['redTeam'],
                     details['blueTeam'])
                    if details['system'] > 0:
                        seriesText += ' - {}'.format(cfg.evelocations.Get(details['system']).locationName)
                    menuOptions.append((seriesText, (seriesID, details['redTeam'], details['blueTeam'])))

                self.matchSelect.LoadOptions(menuOptions)
                tournamentDetails = tourneyMgr.QueryTournamentDetails(tourneyID)
                ships = tournamentDetails['allowedShipList']
                self.banOptions = sorted(ships)
                maxPoints = tournamentDetails['maximumPointsMatch']
                self.pointOptions = [(str(maxPoints), maxPoints)]
                self.pointsSelect.LoadOptions(self.pointOptions)

        self.tourneySelect = Combo(label='Select Tournament:', parent=self.allianceSelections, align=uiconst.TOTOP, padding=(0, 16, 0, 24), name='tourneySel', options=[('Select Tourney', None)] + tourneyOptions, callback=TourneySelChanged)
        self.matchSelect = Combo(label='Select Match:', parent=self.allianceSelections, align=uiconst.TOTOP, padding=(0, 0, 0, 24), name='matchSel', options=[('Pick Tourney First', None)])
        self.solSystemSelect = Combo(label='Select Solar System', parent=self.allianceSelections, align=uiconst.TOTOP, options=systemOptions, pos=(0, 0, 0, 0), padding=(0, 0, 0, 24), select=defaultSelectSolarSystem)
        self.pointsSelect = Combo(label='Points Allowed', parent=self.allianceSelections, align=uiconst.TOTOP, name='pointSel', options=self.pointOptions, padding=(0, 0, 0, 24))
        self.timeSelect = Combo(label='Match Length', parent=self.allianceSelections, align=uiconst.TOTOP, name='timeSel', options=(('10:00', 600),
         ('7:00', 420),
         ('5:00', 300),
         ('2:00', 120)), select='10:00', padding=(0, 0, 0, 24))
        self.overtimeSelect = Combo(label='Overtime Length', parent=self.allianceSelections, align=uiconst.TOTOP, name='timeSel', options=(('5:00', 300),
         ('3:00', 180),
         ('2:00', 120),
         ('1:00', 60),
         ('None', 0)), select='5:00', padding=(0, 0, 0, 8))
        self.startButton = Button(label='Start Match', parent=self.allianceSelections, align=uiconst.TOTOP, pos=(0, 0, 0, 0), padding=(0, 0, 0, 8), func=self.StartMatch)
        self.teleportButtonSystem = Button(label='Teleport Self to System', parent=self.allianceSelections, align=uiconst.TOTOP, pos=(0, 0, 0, 0), padding=(0, 0, 0, 8), func=self.TeleportRef)
        self.teleportButtonHome = Button(label='Teleport Self Home', parent=self.allianceSelections, align=uiconst.TOTOP, pos=(0, 0, 0, 0), padding=(0, 0, 0, 8), func=self.TeleportRefHome)
        self.shipPilotCheck = Container(name='shipPilotCheck', parent=self.content, state=uiconst.UI_HIDDEN, align=uiconst.TOALL)
        Button(label="LET'S DO THIS", parent=self.shipPilotCheck, align=uiconst.TORIGHT, func=self.CompleteShipPilotCheck)
        boxes = Container(name='boxContainer', parent=self.shipPilotCheck, align=uiconst.TOALL)
        redTeamBox = Container(name='redTeamBox', parent=boxes, align=uiconst.TOTOP_PROP, height=0.5)
        blueTeamBox = Container(name='blueTeamBox', parent=boxes, align=uiconst.TOTOP_PROP, height=0.5)
        blueButtons = FlowContainer(name='shipPilotCheckButtons', parent=blueTeamBox, align=uiconst.TOBOTTOM, padding=(0, 16, 4, 4))
        redButtons = FlowContainer(name='shipPilotCheckButtons', parent=redTeamBox, align=uiconst.TOBOTTOM, padding=(0, 16, 4, 4))
        Button(label='Refresh Info', parent=blueButtons, align=uiconst.TOLEFT, func=self.RefreshShipPilotCheck, args=(1,))
        self.blueLockBtn = Button(label='Lock Member List', parent=blueButtons, align=uiconst.TOLEFT, func=self.LockMemberList, args=(1,))
        self.blueUnlockBtn = Button(label='Unlock Member List', parent=blueButtons, align=uiconst.TOLEFT, func=self.UnlockMemberList, args=(1,), state=uiconst.UI_HIDDEN)
        self.blueTeleportBtn = Button(label='Teleport Players', parent=blueButtons, align=uiconst.TOLEFT, func=self.TeleportPlayers, args=(1,), state=uiconst.UI_HIDDEN)
        self.blueTeleportBeacon = Combo(label='Beacon select', parent=blueButtons, align=uiconst.TOLEFT, state=uiconst.UI_HIDDEN, options=[])
        self.blueOverFleetBtn = Button(label='Override Fleet Boss charID', parent=blueButtons, align=uiconst.TOLEFT, func=self.OverrideFleetBossID, args=(1,))
        self.blueAddPlayerBtn = Button(label='Add Player', parent=blueButtons, align=uiconst.TOLEFT, func=self.AddPlayer, args=(1,), state=uiconst.UI_HIDDEN)
        self.blueReturnBtn = Button(label='Return Players', parent=blueButtons, align=uiconst.TOLEFT, func=self.ReturnTeamPlayers, args=(1,), state=uiconst.UI_HIDDEN)
        Button(label='Refresh Info', parent=redButtons, align=uiconst.TOLEFT, func=self.RefreshShipPilotCheck, args=(0,))
        self.redLockBtn = Button(label='Lock Member List', parent=redButtons, align=uiconst.TOLEFT, func=self.LockMemberList, args=(0,))
        self.redUnlockBtn = Button(label='Unlock Member List', parent=redButtons, align=uiconst.TOLEFT, func=self.UnlockMemberList, args=(0,), state=uiconst.UI_HIDDEN)
        self.redTeleportBtn = Button(label='Teleport Players', parent=redButtons, align=uiconst.TOLEFT, func=self.TeleportPlayers, args=(0,), state=uiconst.UI_HIDDEN)
        self.redTeleportBeacon = Combo(label='Beacon select', parent=redButtons, align=uiconst.TOLEFT, state=uiconst.UI_HIDDEN, options=[])
        self.redOverFleetBtn = Button(label='Override Fleet Boss charID', parent=redButtons, align=uiconst.TOLEFT, func=self.OverrideFleetBossID, args=(0,))
        self.redAddPlayerBtn = Button(label='Add Player', parent=redButtons, align=uiconst.TOLEFT, func=self.AddPlayer, args=(0,), state=uiconst.UI_HIDDEN)
        self.redReturnBtn = Button(label='Return Players', parent=redButtons, align=uiconst.TOLEFT, func=self.ReturnTeamPlayers, args=(0,), state=uiconst.UI_HIDDEN)
        self.shipcheckBlueTeamLabel = eveLabel.Label(text='Blue Team', parent=blueTeamBox, color=(0.5, 0.5, 1, 1), align=uiconst.TOTOP)
        self.shipcheckRedTeamLabel = eveLabel.Label(text='Red Team', parent=redTeamBox, color=(1, 0.3, 0.3, 1), align=uiconst.TOTOP)
        self.shipcheckRedScroll = eveScroll.Scroll(parent=redTeamBox, id='atRedTeamScroll')
        self.shipcheckBlueScroll = eveScroll.Scroll(parent=blueTeamBox, id='atBlueTeamScroll')
        self.pregameList = Container(name='pregameList', parent=self.content, state=uiconst.UI_HIDDEN, align=uiconst.TOALL)
        pregameRangeContainer = Container(name='rangeCont', parent=self.pregameList, align=uiconst.TORIGHT, width=110)
        for idx in xrange(26):
            label = eveLabel.Label(text='', parent=pregameRangeContainer, align=uiconst.TOTOP, padTop=5, padLeft=4, maxLines=1)
            setattr(self, 'pregameDistance%d' % (idx,), label)

        lockCont = Container(name='locks', parent=self.pregameList, align=uiconst.TOBOTTOM, height=50)
        self.pregameLockStatus = eveLabel.EveLabelLarge(text="Player locking: <color='green'>Allowed</color>", parent=lockCont, align=uiconst.TOLEFT_PROP, width=0.5, padTop=10)
        tempContainer = Container(parent=lockCont, align=uiconst.TORIGHT_PROP, width=0.5)
        Button(label='Toggle Locking', parent=tempContainer, func=self.ToggleLocks, align=uiconst.TORIGHT, padTop=5, padBottom=5)
        warpCont = Container(name='warps', parent=self.pregameList, align=uiconst.TOBOTTOM, height=50)
        self.pregameWarpStatus = eveLabel.EveLabelLarge(text="Player warping: <color='red'>Disallowed</color>", parent=warpCont, align=uiconst.TOLEFT_PROP, width=0.5, padTop=10)
        tempContainer = Container(parent=warpCont, align=uiconst.TORIGHT_PROP, width=0.5)
        Button(label='Toggle Warping', parent=tempContainer, func=self.ToggleWarping, align=uiconst.TORIGHT, padTop=5, padBottom=5)
        moveCont = Container(name='move', parent=self.pregameList, align=uiconst.TOBOTTOM, height=50)
        self.pregameMoveStatus = eveLabel.EveLabelLarge(text="Player movement: <color='red'>Disallowed</color>", parent=moveCont, align=uiconst.TOLEFT_PROP, width=0.5, padTop=10)
        tempContainer = Container(parent=moveCont, align=uiconst.TORIGHT_PROP, width=0.5)
        Button(label='Toggle Movement', parent=tempContainer, func=self.ToggleMovement, align=uiconst.TORIGHT, padTop=5, padBottom=5)
        stepOne = Container(name='stepOne', parent=self.pregameList, align=uiconst.TOTOP, height=50)
        self.pregameStepOneText = eveLabel.EveLabelLarge(text="Step 1 - Let them warp, don't let them lock", parent=stepOne, align=uiconst.TOLEFT_PROP, width=0.5, padTop=10)
        tempContainer = Container(parent=stepOne, align=uiconst.TORIGHT_PROP, width=0.5)
        Button(label='Do Step 1', parent=tempContainer, func=self.PreGameStepOne, align=uiconst.TORIGHT, padTop=5, padBottom=5)
        stepThree = Container(name='stepThree', parent=self.pregameList, align=uiconst.TOTOP, height=50)
        self.pregameStepThreeText = eveLabel.EveLabelLarge(text='Step 2 - Lock warping again', parent=stepThree, align=uiconst.TOLEFT_PROP, width=0.5, padTop=10)
        tempContainer = Container(parent=stepThree, align=uiconst.TORIGHT_PROP, width=0.5)
        Button(label='Do Step 2', parent=tempContainer, func=self.PreGameStepThree, align=uiconst.TORIGHT, padTop=5, padBottom=5)
        stepFour = Container(name='stepFour', parent=self.pregameList, align=uiconst.TOTOP, height=50)
        self.pregameStepFourText = eveLabel.EveLabelLarge(text='Step 3 - Start Countdown', parent=stepFour, align=uiconst.TOLEFT_PROP, width=0.5, padTop=10)
        tempContainer = Container(parent=stepFour, align=uiconst.TORIGHT_PROP, width=0.5)
        Button(label='Do Step 3', parent=tempContainer, func=self.PreGameStepFour, align=uiconst.TORIGHT, padTop=5, padBottom=5)
        self.countdownCont = Container(name='Countdown', parent=self.pregameList, align=uiconst.TOALL, state=uiconst.UI_HIDDEN)
        self.countdownText = eveLabel.Label(parent=self.countdownCont, align=uiconst.CENTERTOP, fontsize=48, color=(1, 0, 0, 1))
        self.countdownAbort = Button(label='Abort!', parent=self.countdownCont, align=uiconst.TOALL, func=self.AbortCountdown, padTop=65, padBottom=28)
        self.countdownAbort.width = self.countdownAbort.height = 0
        self.countdownAbort.sr.label.fontsize = 32
        self.ConstructRangeCheckLayout(localTournamentService)
        self.postgameList = Container(name='postgameList', parent=self.content, state=uiconst.UI_HIDDEN, align=uiconst.TOALL)
        stepOne = Container(name='stepOne', parent=self.postgameList, align=uiconst.TOTOP, height=50)
        self.postgameStepOneText = eveLabel.EveLabelLarge(text='Step 1 - Send everyone back home', parent=stepOne, align=uiconst.TOLEFT_PROP, width=0.75, padTop=10)
        tempContainer = Container(parent=stepOne, align=uiconst.TORIGHT_PROP, width=0.2)
        stepOneBtn = Button(label='Do Step 1', parent=tempContainer, func=self.PostGameStepOne, align=uiconst.TOLEFT, padTop=5, padBottom=5, state=uiconst.UI_HIDDEN)
        stepTwo = Container(name='stepTwo', parent=self.postgameList, align=uiconst.TOTOP, height=50)
        self.postgameStepTwoText = eveLabel.EveLabelLarge(text='Step 2 - Clean up the grid', parent=stepTwo, align=uiconst.TOLEFT_PROP, width=0.75, padTop=10)
        tempContainer = Container(parent=stepTwo, align=uiconst.TORIGHT_PROP, width=0.2)
        stepTwoBtn = Button(label='Do Step 2', parent=tempContainer, func=self.PostGameStepTwo, align=uiconst.TOLEFT, padTop=5, padBottom=5, state=uiconst.UI_HIDDEN)
        stepThree = Container(name='stepThree', parent=self.postgameList, align=uiconst.TOBOTTOM, height=50)
        self.postgameStepThreeText = eveLabel.EveLabelLarge(text='Step 3 (optional) - Teleport home', parent=stepThree, align=uiconst.TOLEFT_PROP, width=0.75, padTop=10)
        tempContainer = Container(parent=stepThree, align=uiconst.TORIGHT_PROP, width=0.2)
        stepThreeBtn = Button(label='Do Step 3', parent=tempContainer, func=self.PostGameStepThree, align=uiconst.TOLEFT, padTop=5, padBottom=5, state=uiconst.UI_HIDDEN)
        self.postGameButtons = [stepOneBtn, stepTwoBtn, stepThreeBtn]
        self.OnCompetitorTrackingStart(localTournamentService.competitorsByShipID)

    def ConstructRangeCheckLayout(self, localTournamentService):
        self.rangeCheck = Container(name='range check', state=uiconst.UI_HIDDEN, parent=self.content, align=uiconst.TOALL)
        self.layout_grid = LayoutGrid(parent=self.rangeCheck, align=uiconst.TOTOP, columns=3, cellSpacing=(8, 8))
        EveLabelMedium(text='Center Item ID', parent=self.layout_grid, align=uiconst.CENTERLEFT)
        self.centerItemIDEdit = SingleLineEditText(name='centerItemIDEdit', setvalue=str(session.shipid), width=120)
        self.layout_grid.AddCell(self.centerItemIDEdit, colSpan=2)
        EveLabelMedium(text='Arena Radius km', parent=self.layout_grid, align=uiconst.CENTERLEFT)
        self.arenaRadiusEdit = SingleLineEditText(name='arenaRadiusEdit', setvalue=self.default_arenaRadius, parent=self.layout_grid, ints=(1, 250))
        Button(label='Match Completed', parent=self.layout_grid, func=self.MatchCompleted)
        startButtonText = 'Stop' if localTournamentService.isCompetitorsTrackingActive else 'Start'
        self.startButton = Button(label=startButtonText)
        self.startButton.OnClick = self.OnToggleStart
        self.layout_grid.AddCell(self.startButton, colSpan=3)
        self.scroll = eveScroll.Scroll(name='competitorsList', parent=self.rangeCheck, align=uiconst.TOALL, padTop=8)

    def WaitForSessionChanges(self, buttons):
        blue.synchro.SleepWallclock(11000)
        for button in buttons:
            button.state = uiconst.UI_NORMAL

    def StartMatch(self, *args):
        if session.solarsystemid != self.solSystemSelect.GetValue():
            raise UserError('You must be in the selected system to start a match')
        self.banningScreen = Container(name='banningScreen', parent=self.content, state=uiconst.UI_HIDDEN, align=uiconst.TOALL, width=5)
        self.redTeamBanningHeader = eveLabel.EveLabelLarge(text='RedTeam', parent=self.banningScreen, align=uiconst.TOTOP, color=(1, 0.3, 0.3, 1))
        self.redBanBox = ContainerAutoSize(name='redBanBox', parent=self.banningScreen, align=uiconst.TOTOP, top=4, _only_use_callback_when_size_changes=True, callback=self.StartMatchWindowSize)
        self.redBans = {}
        self.redBanChoice = Combo(label='Red Team Ban:', parent=self.banningScreen, options=self.banOptions, top=20, align=uiconst.TOTOP)
        Button(label="Perform Red's Ban", parent=self.banningScreen, func=self.SendBan, args=(0, self.redBanChoice), align=uiconst.TOTOP)
        self.blueTeamBanningHeader = eveLabel.EveLabelLarge(text='BlueTeam', parent=self.banningScreen, align=uiconst.TOTOP, top=30, color=(0.5, 0.5, 1, 1))
        self.blueBanBox = ContainerAutoSize(name='blueBanBox', parent=self.banningScreen, align=uiconst.TOTOP, top=4, _only_use_callback_when_size_changes=True, callback=self.StartMatchWindowSize)
        self.blueBans = {}
        self.blueBanChoice = Combo(label='Blue Team Ban:', parent=self.banningScreen, options=self.banOptions, top=20, align=uiconst.TOTOP)
        Button(label="Perform Blue's Ban", parent=self.banningScreen, func=self.SendBan, args=(1, self.blueBanChoice), align=uiconst.TOTOP)
        autoBanBox = Container(name='autoBanBox', parent=self.banningScreen, align=uiconst.TOTOP, height=200, top=10)
        autoBanOverrides = Container(name='autoBanOverrides', parent=autoBanBox, align=uiconst.TOLEFT, width=200)
        autoBanOutput = Container(name='autoBanOutput', parent=autoBanBox)
        autoBanRedCapt = ContainerAutoSize(name='redCapt', parent=autoBanOverrides, align=uiconst.TOTOP, top=4)
        eveLabel.Label(text='Red Captain:', parent=autoBanRedCapt, top=4)
        self.autoBanRedCharName = eveLabel.Label(text='?', parent=autoBanRedCapt, top=4, left=100)
        self.autoBanRedCharID = SingleLineEditText(name='redCaptID', setvalue='', OnFocusLost=self.LookupBanChars, align=uiconst.TOTOP, parent=autoBanOverrides, top=4)
        autoBanBlueCapt = ContainerAutoSize(name='blueCapt', parent=autoBanOverrides, align=uiconst.TOTOP, top=4)
        eveLabel.Label(text='Blue Captain:', parent=autoBanBlueCapt, top=4)
        self.autoBanBlueCharName = eveLabel.Label(text='?', parent=autoBanBlueCapt, top=4, left=100)
        self.autoBanBlueCharID = SingleLineEditText(name='blueCaptID', setvalue='', OnFocusLost=self.LookupBanChars, align=uiconst.TOTOP, parent=autoBanOverrides, top=4)
        autoBanNumberBox = Container(name='autoBanNumberBox', parent=autoBanOverrides, align=uiconst.TOTOP, top=4, height=SingleLineEditText.default_height)
        eveLabel.Label(text='Number of AutoBans: ', parent=Container(parent=autoBanNumberBox), align=uiconst.CENTERLEFT)
        self.autoBanQty = SingleLineEditText(parent=autoBanNumberBox, name='autoBanQty', setvalue='3', align=uiconst.TORIGHT, width=50)
        Button(label='Initiate Autobans', parent=autoBanOverrides, func=self.Autobans, align=uiconst.TOTOP, top=4)
        eveLabel.Label(text='Auto Ban Output:', parent=autoBanOutput, align=uiconst.TOTOP, top=4, padLeft=125)
        self.autoBanText = eveLabel.Label(text='', parent=autoBanOutput, align=uiconst.TOTOP, height=100, top=4, padLeft=125)
        Button(label='Finalize Bans', parent=self.banningScreen, func=self.FinalizeBans, top=5, align=uiconst.TOTOP)
        selectedMatch = self.matchSelect.GetValue()
        self.redTeam = selectedMatch[1]
        self.blueTeam = selectedMatch[2]
        self.matchMoniker = eveMoniker.Moniker('tourneyMgr', self.solSystemSelect.GetValue())
        self.matchDetails = [-1,
         None,
         None,
         None]
        matchID, beaconIDs, captainIDs = self.matchMoniker.CreateMatch(self.tourneySelect.GetValue(), selectedMatch[0], self.pointsSelect.GetValue(), self.timeSelect.GetValue(), self.overtimeSelect.GetValue())
        self.SetCaption('Tournament Match: ' + self.matchSelect.GetKey())
        self.matchDetails[0] = matchID
        self.matchDetails[3] = beaconIDs
        self.autoBanRedCharID.SetValue(str(captainIDs[0]))
        self.redTeamBanningHeader.text = 'Red Team - %s' % (self.redTeam,)
        self.autoBanBlueCharID.SetValue(str(captainIDs[1]))
        self.blueTeamBanningHeader.text = 'Blue Team - %s' % (self.blueTeam,)
        self.LookupBanChars()
        self.StartMatchWindowSize()

    def StartMatchWindowSize(self):
        width, height = self.GetWindowSizeForContentSize(height=self.blueBanBox.height + self.redBanBox.height, width=self.blueBanBox.width + self.redBanBox.width)
        self.SetMinSize(size=(WINDOW_WIDTH, 500 + height), refresh=True)

    def ProcessTournamentMatchUpdate(self, matchState):
        myMatchID = self.matchDetails[0]
        if matchState['matchID'] != myMatchID:
            if myMatchID != -1:
                return
        uiScreenPerState = {tourneyConst.tournamentStateBanning: [self.banningScreen],
         tourneyConst.tournamentStatePregame: [self.shipPilotCheck],
         tourneyConst.tournamentStateWarpin: [self.pregameList],
         tourneyConst.tournamentStateCountdown: [self.pregameList, self.countdownCont, self.countdownAbort],
         tourneyConst.tournamentStateStarting: [self.pregameList, self.countdownCont],
         tourneyConst.tournamentStateInProgress: [self.rangeCheck],
         tourneyConst.tournamentStateComplete: [self.postgameList],
         tourneyConst.tournamentStateClosed: [self.allianceSelections]}
        allScreens = (self.allianceSelections,
         self.banningScreen,
         self.shipPilotCheck,
         self.pregameList,
         self.rangeCheck,
         self.postgameList,
         self.countdownCont,
         self.countdownAbort)
        for screen in allScreens:
            if screen in uiScreenPerState[matchState['state']]:
                screen.state = uiconst.UI_NORMAL
            else:
                screen.state = uiconst.UI_HIDDEN

        if matchState['state'] == tourneyConst.tournamentStateWarpin:
            if self.pregameRangeTimer is None:
                self.pregameRangeTimer = timerstuff.AutoTimer(1000, self.UpdatePregameRanges)
        else:
            self.pregameRangeTimer = None
        if 'matchStartTime' in matchState:
            self.matchStartTime = matchState['matchStartTime']
        if matchState['state'] in (tourneyConst.tournamentStateCountdown, tourneyConst.tournamentStateStarting):
            if self.countdownTimer is None:
                self.UpdateTimer()
                self.countdownTimer = timerstuff.AutoTimer(100, self.UpdateTimer)
        else:
            self.countdownTimer = None
        if matchState['state'] == tourneyConst.tournamentStateInProgress:
            if self.centerItemID is None:
                self.startButton.SetLabel('Stop')
                closestBeacon = None
                ballpark = sm.GetService('michelle').GetBallpark()
                for beaconID in self.matchDetails[3]:
                    try:
                        distance = ballpark.GetBall(beaconID).surfaceDist
                        if not closestBeacon or distance < closestBeacon[1]:
                            closestBeacon = (beaconID, distance)
                    except AttributeError:
                        pass

                self.centerItemIDEdit.SetValue(str(closestBeacon[0]))
                self.centerItemID = closestBeacon[0]
                self.arenaRadius = 125000
                self.arenaRadiusEdit.SetValue('125')
                localTournamentService = sm.GetService('allianceTournamentSvc')
                localTournamentService.StartTracking(self.centerItemID, self.arenaRadius)
        elif self.centerItemID is not None:
            localTournamentService = sm.GetService('allianceTournamentSvc')
            localTournamentService.StopTracking()
            self.centerItemID = None
            uthread.new(self.WaitForSessionChanges, self.postGameButtons)
        if 'solarsystemID' in matchState:
            if self.solarsystemID != matchState['solarsystemID']:
                self.solarsystemID = matchState['solarsystemID']
                self.redTeleportBeacon.LoadOptions(self.beaconOptions['red'])
                self.blueTeleportBeacon.LoadOptions(self.beaconOptions['blue'])

        def CreateBanElement(typeID, parent, teamIdx):

            def RemoveBan(*args):
                self.matchMoniker.UnBanShipType(self.matchDetails[0], typeID, teamIdx)

            banContainer = Container(name='banEle', parent=parent, align=uiconst.TOTOP, height=16)
            Button(label='X', parent=banContainer, func=RemoveBan, align=uiconst.TOLEFT)
            eveLabel.Label(text=evetypes.GetName(typeID), parent=banContainer, align=uiconst.TOLEFT)
            return banContainer

        if 'redTeamBans' in matchState:
            redBans = matchState['redTeamBans']
            keysToRemove = set(self.redBans.keys())
            for typeID in redBans:
                if typeID in keysToRemove:
                    keysToRemove.remove(typeID)
                if typeID not in self.redBans:
                    self.redBans[typeID] = CreateBanElement(typeID, self.redBanBox, 0)

            for typeID in keysToRemove:
                self.redBans[typeID].Close()
                del self.redBans[typeID]

        if 'blueTeamBans' in matchState:
            blueBans = matchState['blueTeamBans']
            keysToRemove = set(self.blueBans.keys())
            for typeID in blueBans:
                if typeID in keysToRemove:
                    keysToRemove.remove(typeID)
                if typeID not in self.blueBans:
                    self.blueBans[typeID] = CreateBanElement(typeID, self.blueBanBox, 1)

            for typeID in keysToRemove:
                self.blueBans[typeID].Close()
                del self.blueBans[typeID]

        if 'autoBanText' in matchState:
            autoBanText = matchState['autoBanText']
            self.autoBanText.text = autoBanText
        updatePilotDisplay = False
        if 'redTeamDetails' in matchState:
            self.matchDetails[1] = matchState['redTeamDetails']
            updatePilotDisplay = True
        if 'blueTeamDetails' in matchState:
            self.matchDetails[2] = matchState['blueTeamDetails']
            updatePilotDisplay = True
        if updatePilotDisplay:
            self.UpdateShipPilotDisplay()
        if 'redTeamLocked' in matchState:
            if matchState['redTeamLocked']:
                self.redLockBtn.state = uiconst.UI_HIDDEN
                self.redUnlockBtn.state = uiconst.UI_NORMAL
                self.redOverFleetBtn.state = uiconst.UI_HIDDEN
                self.redAddPlayerBtn.state = uiconst.UI_NORMAL
                self.redTeleportBtn.state = uiconst.UI_NORMAL
                self.redTeleportBeacon.state = uiconst.UI_NORMAL
            else:
                self.redLockBtn.state = uiconst.UI_NORMAL
                self.redUnlockBtn.state = uiconst.UI_HIDDEN
                self.redOverFleetBtn.state = uiconst.UI_NORMAL
                self.redAddPlayerBtn.state = uiconst.UI_HIDDEN
                self.redTeleportBtn.state = uiconst.UI_HIDDEN
                self.redTeleportBeacon.state = uiconst.UI_HIDDEN
        if 'blueTeamLocked' in matchState:
            if matchState['blueTeamLocked']:
                self.blueLockBtn.state = uiconst.UI_HIDDEN
                self.blueUnlockBtn.state = uiconst.UI_NORMAL
                self.blueOverFleetBtn.state = uiconst.UI_HIDDEN
                self.blueAddPlayerBtn.state = uiconst.UI_NORMAL
                self.blueTeleportBtn.state = uiconst.UI_NORMAL
                self.blueTeleportBeacon.state = uiconst.UI_NORMAL
            else:
                self.blueLockBtn.state = uiconst.UI_NORMAL
                self.blueUnlockBtn.state = uiconst.UI_HIDDEN
                self.blueOverFleetBtn.state = uiconst.UI_NORMAL
                self.blueAddPlayerBtn.state = uiconst.UI_HIDDEN
                self.blueTeleportBtn.state = uiconst.UI_HIDDEN
                self.blueTeleportBeacon.state = uiconst.UI_HIDDEN
        if 'warpRestrict' in matchState:
            self.playersCanWarp = not matchState['warpRestrict']
            if self.playersCanWarp:
                self.pregameWarpStatus.text = "Player warping: <color='green'>Allowed</color>"
            else:
                self.pregameWarpStatus.text = "Player warping: <color='red'>Disallowed</color>"
        if 'moveRestrict' in matchState:
            self.playersCanMove = not matchState['moveRestrict']
            if self.playersCanMove:
                self.pregameMoveStatus.text = "Player movement: <color='green'>Allowed</color>"
            else:
                self.pregameMoveStatus.text = "Player movement: <color='red'>Disallowed</color>"
        if 'lockRestrict' in matchState:
            self.playersCanLock = not matchState['lockRestrict']
            if self.playersCanLock:
                self.pregameLockStatus.text = "Player locking: <color='green'>Allowed</color>"
            else:
                self.pregameLockStatus.text = "Player locking: <color='red'>Disallowed</color>"
        if matchState['state'] in (tourneyConst.tournamentStatePregame, tourneyConst.tournamentStateWarpin):
            self.resetButton.state = uiconst.UI_NORMAL
        else:
            self.resetButton.state = uiconst.UI_HIDDEN

    def LookupBanChars(self, *args):
        try:
            self.autoBanRedCharName.text = cfg.eveowners.Get(int(self.autoBanRedCharID.GetValue())).ownerName
        except Exception:
            self.autoBanRedCharName.text = '?'

        try:
            self.autoBanBlueCharName.text = cfg.eveowners.Get(int(self.autoBanBlueCharID.GetValue())).ownerName
        except Exception:
            self.autoBanRedCharName.text = '?'

    def Autobans(self, *args):
        tourneyID = self.tourneySelect.GetValue()
        self.matchMoniker.StartAutobanning(self.matchDetails[0], tourneyID, redCharID=int(self.autoBanRedCharID.GetValue()), blueCharID=int(self.autoBanBlueCharID.GetValue()), totalNumBans=int(self.autoBanQty.GetValue()))

    def FinalizeBans(self, *args):
        self.matchMoniker.FinalizeBans(self.matchDetails[0])
        self.MakeUnKillable()

    def SendBan(self, teamIdx, comboBox, *args):
        curBans = self.matchMoniker.BanShipType(self.matchDetails[0], comboBox.GetValue(), teamIdx)

    def ToggleLocks(self, *args):
        self.matchMoniker.OverrideLockRestrict(self.matchDetails[0], self.playersCanLock)

    def ToggleWarping(self, *args):
        self.matchMoniker.OverrideWarpRestrict(self.matchDetails[0], self.playersCanWarp)

    def ToggleMovement(self, *args):
        self.matchMoniker.OverrideMoveRestrict(self.matchDetails[0], self.playersCanMove)

    def CompleteShipPilotCheck(self, *args):
        if self.matchMoniker.IsOtherMatchInProgress():
            raise UserError('TournamentOtherMatchInSystemInProgress')
        problems = []
        tharWereErrors = False
        if self.redLockBtn.state != uiconst.UI_HIDDEN:
            problems.append('Red team membership not locked')
        if self.blueLockBtn.state != uiconst.UI_HIDDEN:
            problems.append('Blue team membership not locked')
        for teamIdx in (1, 2):
            for charID, shipType, shipID, locationID, pointVal, errors in self.matchDetails[teamIdx]:
                if errors:
                    tharWereErrors = True
                if locationID != self.solarsystemID:
                    problems.append("%s doesn't look like they're here" % (cfg.eveowners[charID].ownerName,))

        if tharWereErrors:
            problems.append('Errors remain')
        if problems:
            ret = eve.Message('CustomQuestion', {'header': "This doesn't seem right",
             'question': 'The following problems remain:<br><br>' + '<br>'.join(problems) + '<br><br>Ignore and get this party started?'}, uiconst.YESNO)
            if ret != uiconst.ID_YES:
                return
        self.pregameStepOneText.text = "Step 1 - Let them warp, don't let them lock"
        self.pregameStepThreeText.text = 'Step 2 - Lock warping again'
        self.pregameStepFourText.text = 'Step 3 - Start Countdown'
        self.matchMoniker.CompletePregameChecks(self.matchDetails[0])

    def UpdatePregameRanges(self):
        bp = sm.GetService('michelle').GetBallpark()
        metersInKM = 1000.0
        maximumDistance = 55
        lines = ["<color='red'>" + self.redTeam]
        for charID, shipType, shipID, locationID, pointVal, errors in self.matchDetails[1]:
            try:
                dist = bp.GetBall(shipID).surfaceDist
                if dist / metersInKM > maximumDistance:
                    color = 'yellow'
                else:
                    color = 'red'
                lines.append("<color='%s'> %.1fkm %s" % (color, dist / metersInKM, cfg.eveowners.Get(charID).ownerName))
            except StandardError:
                lines.append("<color='red'> -- %s" % (cfg.eveowners.Get(charID).ownerName,))

        lines.append("<color='blue'>" + self.blueTeam)
        for charID, shipType, shipID, locationID, pointVal, errors in self.matchDetails[2]:
            try:
                dist = bp.GetBall(shipID).surfaceDist
                if dist / metersInKM > maximumDistance:
                    color = 'yellow'
                else:
                    color = 'blue'
                lines.append("<color='%s'> %.1fkm %s" % (color, dist / metersInKM, cfg.eveowners.Get(charID).ownerName))
            except:
                lines.append("<color='blue'> -- %s" % (cfg.eveowners.Get(charID).ownerName,))

        lines += [''] * (26 - len(lines))
        for idx, line in enumerate(lines):
            getattr(self, 'pregameDistance%d' % (idx,)).text = line

    def PreGameStepOne(self, *args):
        self.matchMoniker.OverrideLockRestrict(self.matchDetails[0], True)
        self.matchMoniker.OverrideWarpRestrict(self.matchDetails[0], False)
        self.pregameStepOneText.text = "<color='green'>%s</color>" % (self.pregameStepOneText.text,)

    def PreGameStepThree(self, *args):
        self.matchMoniker.OverrideWarpRestrict(self.matchDetails[0], True)
        self.pregameStepThreeText.text = "<color='green'>%s</color>" % (self.pregameStepThreeText.text,)

    def PreGameStepFour(self, *args):
        self.matchMoniker.StartCountdown(self.matchDetails[0])
        self.pregameStepFourText.text = "<color='green'>%s</color>" % (self.pregameStepFourText.text,)

    def UpdateTimer(self):
        timeDiffMS = max(0, -blue.os.TimeDiffInMs(self.matchStartTime, blue.os.GetWallclockTime()))
        self.countdownText.text = '%.1f' % (float(timeDiffMS) / 1000.0,)

    def AbortCountdown(self, *args):
        stopped = self.matchMoniker.AbortCountdown(self.matchDetails[0])
        if stopped:
            self.pregameStepFourText.text = 'Step 4 - Start Countdown'

    def MatchCompleted(self, *args):
        ret = eve.Message('CustomQuestion', {'header': 'Is it really over?',
         'question': 'Are you certain you want to prematurely end the match?'}, uiconst.YESNO)
        if ret != uiconst.ID_YES:
            return
        self.matchMoniker.MatchCompleted(self.matchDetails[0])
        self.postgameStepOneText.text = 'Step 1 - Send everyone back home'
        self.postgameStepTwoText.text = 'Step 2 - Clean up the grid'
        self.postgameStepThreeText.text = 'Step 3 (optional) - Teleport home'

    def PostGameStepOne(self, *args):
        self.matchMoniker.ReturnAllPlayers(self.matchDetails[0])
        self.postgameStepOneText.text = "<color='green'>%s</color>" % (self.postgameStepOneText.text,)
        self.MakeKillable()

    def PostGameStepTwo(self, *args):
        self.matchMoniker.CleanupGrid(self.matchDetails[0])
        self.postgameStepTwoText.text = "<color='green'>%s</color>" % (self.postgameStepTwoText.text,)

    def PostGameStepThree(self, *args):
        self.matchMoniker.TeleportRefHome(self.matchDetails[0])
        self.postgameStepThreeText.text = "<color='green'>%s</color>" % (self.postgameStepThreeText.text,)

    def OverrideFleetBossID(self, teamIdx, *args):
        format = [{'type': 'edit',
          'key': 'fleetbossid',
          'setfocus': True,
          'label': u'New Fleet Boss Char ID'}]
        retVal = uix.HybridWnd(format, caption=u'Specify new fleet boss charID', windowID='overrideFleetBoss', minW=410, minH=100)
        if retVal:
            newFleetBossID = int(retVal['fleetbossid'])
            if newFleetBossID:
                self.matchMoniker.OverrideFleetBossID(self.matchDetails[0], teamIdx, newFleetBossID)

    def OverrideError(self, teamIdx, charID, errorString):
        ret = eve.Message('CustomQuestion', {'header': 'YOU FUCKING SURE DUDE?!?',
         'question': 'Override<br>%s<br>for pilot %s?' % (errorString, cfg.eveowners.Get(charID).ownerName)}, uiconst.YESNO)
        if ret != uiconst.ID_YES:
            return
        self.matchMoniker.OverrideError(self.matchDetails[0], charID, errorString)

    def OverrideAllErrors(self, teamIdx, charID, errorStrings):
        errorList = ''
        for errorString in errorStrings:
            errorList += '<br>' + errorString

        ret = eve.Message('CustomQuestion', {'header': 'YOU ABSOLUTELY FUCKING SURE DUDE?!?',
         'question': 'Override ALL ERRORS for pilot %s?<br><br>Errors are: %s' % (cfg.eveowners.Get(charID).ownerName, errorList)}, uiconst.YESNO)
        if ret != uiconst.ID_YES:
            return
        for errorString in errorStrings:
            self.matchMoniker.OverrideError(self.matchDetails[0], charID, errorString)

    def RemovePlayer(self, teamIdx, charID):
        ret = eve.Message('CustomQuestion', {'header': "JUST CHECKIN'",
         'question': 'Remove %s from their team?' % cfg.eveowners.Get(charID).ownerName}, uiconst.YESNO)
        if ret != uiconst.ID_YES:
            return
        self.matchMoniker.RemovePlayer(self.matchDetails[0], teamIdx, charID)

    def GetPrematchPilotMenu(self, node):
        basePilotMenu = GetMenuService().GetMenuFromItemIDTypeID(node.sr.node.id[1], const.typeCharacter)
        errorMenu = []
        for error in node.sr.node.errors:
            errorMenu.append(('Override: %s' % (error,), self.OverrideError, (node.sr.node.id[0], node.sr.node.id[1], error)))

        if errorMenu:
            errorMenu.append(None)
        errorMenu.append(('Remove Player', self.RemovePlayer, (node.sr.node.id[0], node.sr.node.id[1])))
        errorMenu.append(None)
        errorMenu.append(('Override all errors (!!!)', self.OverrideAllErrors, (node.sr.node.id[0], node.sr.node.id[1], node.sr.node.errors)))
        return errorMenu + basePilotMenu

    def UpdateShipPilotDisplay(self):
        redTeam = []
        pointTotal = 0
        for charID, shipType, shipID, locationID, pointVal, errors in self.matchDetails[1]:
            data = utillib.KeyVal(id=(0, charID), errors=errors, label='%s<t>%s<t>%s<t>%s<t><color=red>%s</color>' % (cfg.eveowners.Get(charID).ownerName,
             evetypes.GetName(shipType),
             cfg.evelocations.Get(locationID).locationName,
             pointVal,
             ' - '.join(errors)), GetMenu=self.GetPrematchPilotMenu, hint='\n'.join(errors) if errors else 'No errors')
            listEntry = GetFromClass(Generic, data)
            redTeam.append(listEntry)
            pointTotal += pointVal

        self.shipcheckRedScroll.Load(contentList=redTeam, headers=['Name',
         'Ship Type',
         'Location',
         'Point Value',
         'Errors'], noContentHint='No pilots found')
        self.shipcheckRedTeamLabel.text = 'Red Team - %s - %d points' % (self.redTeam, pointTotal)
        blueTeam = []
        pointTotal = 0
        for charID, shipType, shipID, locationID, pointVal, errors in self.matchDetails[2]:
            data = utillib.KeyVal(id=(1, charID), errors=errors, label='%s<t>%s<t>%s<t>%s<t><color=red>%s</color>' % (cfg.eveowners.Get(charID).ownerName,
             evetypes.GetName(shipType),
             cfg.evelocations.Get(locationID).locationName,
             pointVal,
             ' - '.join(errors)), GetMenu=self.GetPrematchPilotMenu, hint='\n'.join(errors) if errors else 'No errors')
            listEntry = GetFromClass(Generic, data)
            blueTeam.append(listEntry)
            pointTotal += pointVal

        self.shipcheckBlueScroll.Load(contentList=blueTeam, headers=['Name',
         'Ship Type',
         'Location',
         'Point Value',
         'Errors'], noContentHint='No pilots found')
        self.shipcheckBlueTeamLabel.text = 'Blue Team - %s - %d points' % (self.blueTeam, pointTotal)

    def RefreshShipPilotCheck(self, whichTeam, *args):
        self.matchMoniker.UpdateFleetDetails(self.matchDetails[0], whichTeam)

    def LockMemberList(self, whichTeam, *args):
        memberList = [ x[0] for x in self.matchDetails[whichTeam + 1] ]
        self.matchMoniker.LockMemberList(self.matchDetails[0], whichTeam, memberList)

    def UnlockMemberList(self, whichTeam, *args):
        self.matchMoniker.UnlockMemberList(self.matchDetails[0], whichTeam)

    def AddPlayer(self, whichTeam):
        format = [{'type': 'edit',
          'key': 'charid',
          'setfocus': True,
          'label': u'Char ID to add'}]
        retVal = uix.HybridWnd(format, caption=u'Gimme a dude', windowID='addPlayerToTournament', minW=250, minH=100)
        if retVal:
            newCharID = int(retVal['charid'])
            if newCharID:
                self.matchMoniker.AddPlayer(self.matchDetails[0], whichTeam, newCharID)

    def TeleportPlayers(self, whichTeam, *args):
        if whichTeam == 0:
            beaconIdx = self.redTeleportBeacon.GetValue()
            self.redReturnBtn.state = uiconst.UI_NORMAL
        else:
            beaconIdx = self.blueTeleportBeacon.GetValue()
            self.blueReturnBtn.state = uiconst.UI_NORMAL
        self.matchMoniker.TeleportPlayers(self.matchDetails[0], whichTeam, beaconIdx)

    def ReturnTeamPlayers(self, whichTeam, *args):
        self.matchMoniker.ReturnTeamPlayers(self.matchDetails[0], whichTeam)

    def TeleportRef(self, *args):
        teleportMoniker = eveMoniker.Moniker('tourneyMgr', self.solSystemSelect.GetValue())
        teleportMoniker.TeleportToArena()

    def TeleportRefHome(self, *args):
        teleportMoniker = eveMoniker.Moniker('tourneyMgr', self.solSystemSelect.GetValue())
        teleportMoniker.TeleportToStation()

    def ResetMatch(self, *args):
        ret = eve.Message('CustomQuestion', {'header': 'Mildly Annoying',
         'question': 'Reseting is a moderate inconveniance, you sure you want that?'}, uiconst.YESNO)
        if ret != uiconst.ID_YES:
            return
        self.matchMoniker.ResetMatch(self.matchDetails[0])
        self.MakeKillable()

    def Close(self, *args, **kwds):
        matchID = getattr(self, 'matchDetails[0]', 0)
        if matchID > 0:
            self.matchMoniker.RemoveSelfFromReferees(matchID)
        Window.Close(self, *args, **kwds)

    def OnRemovalAsRef(self, matchID, *args):
        if matchID == self.matchDetails[0]:
            Window.Close(self)

    def OnToggleStart(self, *args):
        if self.isToggling:
            return
        try:
            self.isToggling = True
            self.centerItemID = int(self.centerItemIDEdit.GetValue())
            self.arenaRadius = int(self.arenaRadiusEdit.GetValue()) * 1000
            localTournamentService = sm.GetService('allianceTournamentSvc')
            if localTournamentService.isCompetitorsTrackingActive:
                localTournamentService.StopTracking()
                self.startButton.SetLabel('Start')
            else:
                localTournamentService.StartTracking(self.centerItemID, self.arenaRadius)
                self.startButton.SetLabel('Stop')
        finally:
            self.isToggling = False

    def UpdateColumnSort(self, scroll, entries, columnID):
        if not entries:
            return
        startIdx = entries[0].idx
        endIdx = entries[-1].idx
        entries = SortColumnEntries(entries, columnID)
        scroll.sr.nodes = scroll.sr.nodes[:startIdx] + entries + scroll.sr.nodes[endIdx + 1:]
        idx = 0
        for entry in scroll.GetNodes()[startIdx:]:
            if entry.panel:
                entry.panel.SetOrder(-1)
            entry.idx = startIdx + idx
            if entry.Get('needReload', 0) and entry.panel:
                entry.panel.LoadLite(entry)
            idx += 1

    def OnCompetitorTrackingUpdate(self, competitorsByShipID):
        scrolllist = []
        for node in self.scroll.GetNodes():
            data = competitorsByShipID.get(node.shipID, None)
            if data:
                distance = '%0.1f km' % (data.distance * 0.001)
                maxDistance = '%0.1f km' % (data.maxDistance * 0.001)
                if distance != node.texts.distance:
                    node.needReload = True
                    node.texts = node.texts._replace(distance=distance, maxDistance=maxDistance)
                    node.sortData = node.sortData._replace(distance=data.distance, maxDistance=data.maxDistance)
                if data.maxDistance > self.arenaRadius:
                    node.panel.warn.state = uiconst.UI_DISABLED
                    if data.shipLost:
                        node.overlay.state = uiconst.UI_HIDDEN
                    else:
                        node.overlay.state = uiconst.UI_PICKCHILDREN
                scrolllist.append(node)

        self.UpdateColumnSort(self.scroll, scrolllist, 'AtCompetitorsScroll')

    def OnCompetitorTrackingStart(self, competitorsByShipID):
        scrolllist = []
        for shipData in competitorsByShipID.values():
            data = utillib.KeyVal()
            data.shipID = shipData.shipID
            data.texts = EntryRow(character=shipData.ownerName, groupName=shipData.groupName, typeName=shipData.typeName, maxDistance='%.1f km' % (shipData.maxDistance * 0.001), distance='%.1f km' % (shipData.distance * 0.001))
            data.sortData = EntryRow(character=shipData.ownerName, groupName=shipData.groupName, typeName=shipData.typeName, maxDistance=shipData.maxDistance, distance=shipData.distance)
            data.columnID = 'AtCompetitorsScroll'
            data.isSelected = False
            data.GetMenu = lambda x: GetMenuService().GetMenuFromItemIDTypeID(shipData.shipID, shipData.typeID)
            iconPar = Container(name='iconParent', parent=None, align=uiconst.TOPLEFT, width=16, height=16, state=uiconst.UI_HIDDEN)
            icon = eveIcon.Icon(parent=iconPar, icon='ui_38_16_182', pos=(0, 0, 16, 16), align=uiconst.RELATIVE)
            icon.hint = 'Destroy Ship'
            icon.shipID = shipData.shipID
            icon.OnClick = (self.DestroyShip, icon)
            data.overlay = iconPar
            entry = GetFromClass(AtCompetitorEntry, data)
            scrolllist.append(entry)

        scrolllist = SortColumnEntries(scrolllist, 'AtCompetitorsScroll')
        data = utillib.KeyVal()
        data.texts = ('Character', 'Group', 'Type', 'Max Distance', 'Distance')
        data.columnID = 'AtCompetitorsScroll'
        data.editable = True
        data.showBottomLine = True
        data.selectable = False
        data.hilightable = False
        scrolllist.insert(0, GetFromClass(AtCompetitorEntry, data))
        if scrolllist:
            InitCustomTabstops('AtCompetitorsScroll', scrolllist)
            self.scroll.LoadContent(contentList=scrolllist)

    def DestroyShip(self, button):
        localTournamentService = sm.GetService('allianceTournamentSvc')
        shipData = localTournamentService.competitorsByShipID[button.shipID]
        header = 'Destroy Ship'
        warning = 'Are you sure you want to destroy this ship?<br /><br />Character: <b>%s</b><br />Type: <b>%s</b>' % (shipData.ownerName, shipData.typeName)
        if eve.Message('CustomWarning', {'header': header,
         'warning': warning}, uiconst.YESNO) == uiconst.ID_YES:
            sm.GetService('slash').SlashCmd('/heal %d 0' % button.shipID)
            channelID = (('solarsystemid2', session.solarsystemid2),)
            message = u'<url=showinfo:%d>%s</url> piloted by <url=showinfo:1377//%s>%s</url> has been disqualified for boundary violations.' % (shipData.typeID,
             shipData.typeName,
             shipData.charID,
             shipData.ownerName)
            c = sm.StartService('LSC').GetChannelWindow(channelID[0])
            c.Speak(message, eve.session.charid, localEcho=True)
            sm.StartService('LSC').SendMessage(channelID, message)


class RefWindowSpawningWindow(Window):
    __guid__ = 'form.RefWindowSpawningWindow'
    default_windowID = 'tournament'
    default_fixedWidth = 280
    default_fixedHeight = 110

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.SetScope(uiconst.SCOPE_ALL)
        self.SetCaption('Match Starter')
        self.SetMinSize([self.width, self.height])
        self.MakeUnResizeable()
        self.ConstructLayout()
        self.nextWndIDNum = 0

    def ConstructLayout(self):
        Button(label='Create New Match', parent=self.content, padding=(5, 5, 5, 5), func=self.NewMatch, align=uiconst.TOTOP)

    def NewMatch(self, *args):
        TournamentRefereeTool.Open(windowID='TournamentRefereeTool%d' % (self.nextWndIDNum,))
        self.nextWndIDNum += 1


class AllianceTournamentSvc(Service):
    __guid__ = 'svc.allianceTournamentSvc'
    __dependencies__ = ['michelle']

    def Run(self, *args):
        self.isCompetitorsTrackingActive = False
        self.competitorsByShipID = {}

    def Show(self):
        RefWindowSpawningWindow.Open()

    def StartTracking(self, centerItemID, arenaRadius):
        self.LogInfo('Start tracking arena center item', centerItemID, 'using a radius of', arenaRadius, 'meters')
        self.centerItemID = centerItemID
        self.arenaRadius = arenaRadius
        uthread.new(self._MonitorCompetitorsTask).context = 'at::competitortracking'

    def StopTracking(self):
        self.LogInfo('Stop tracking competitors')
        self.isCompetitorsTrackingActive = False
        self.competitorsByShipID = {}
        sm.ScatterEvent('OnCompetitorTrackingStart', {})

    def _RegisterCompetitors(self):
        self.competitorsByShipID = {}
        ballpark = self.michelle.GetBallpark()
        for ball, slim in ballpark.GetBallsAndItems():
            if ball.id != session.shipid and slim.categoryID == const.categoryShip and slim.groupID != const.groupCapsule and slim.charID:
                distance = ballpark.DistanceBetween(self.centerItemID, ball.id)
                if distance is None or distance >= self.arenaRadius:
                    continue
                data = utillib.KeyVal(charID=slim.ownerID, shipID=ball.id, typeID=slim.typeID, groupID=slim.groupID, ownerName=cfg.eveowners.Get(slim.ownerID).ownerName, typeName=evetypes.GetName(slim.typeID), groupName=evetypes.GetGroupNameByGroup(slim.groupID), distance=distance, maxDistance=distance, shipLost=False)
                self.competitorsByShipID[ball.id] = data

        sm.ScatterEvent('OnCompetitorTrackingStart', self.competitorsByShipID)

    def _MonitorCompetitorsTask(self):
        if self.isCompetitorsTrackingActive:
            return
        try:
            self._RegisterCompetitors()
            self.isCompetitorsTrackingActive = True
            self.LogInfo('Starting monitoring task')
            while self.isCompetitorsTrackingActive:
                blue.pyos.synchro.SleepWallclock(500)
                ballpark = sm.GetService('michelle').GetBallpark()
                ball = ballpark.GetBall(self.centerItemID)
                if not ball:
                    self.LogInfo('We lost the center ball.  Must abort tracking')
                    self.StopTracking()
                for shipID, data in self.competitorsByShipID.iteritems():
                    ball = ballpark.GetBall(shipID)
                    if ball:
                        data.distance = ballpark.DistanceBetween(self.centerItemID, shipID)
                        data.maxDistance = max(data.maxDistance, data.distance)
                    else:
                        data.shipLost = True

                sm.ScatterEvent('OnCompetitorTrackingUpdate', self.competitorsByShipID)

        finally:
            self.isCompetitorsTrackingActive = False
            self.LogInfo('Stopping monitoring task')
