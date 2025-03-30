#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\scannerListEntries.py
import math
import geo2
from carbon.common.script.util.format import FmtDist
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.control.scrollentries import SE_BaseClassCore
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.util.color import Color
from eve.client.script.ui import eveColor, eveThemeColor
from eve.client.script.ui.control.baseListEntry import BaseListEntryCustomColumns, BaseListEntry
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelMediumBold, EveLabelMedium
from eve.client.script.ui.graphs.bargraph import BarGraphBarHorizontal
from eve.client.script.ui.shared.mapView.markers.mapMarkerUtil import GetResultTexturePath, GetResultColor
from eve.common.script.sys.eveCfg import InShipInSpace
from signals import Signal
import localization
import evetypes
import blue
from probescanning.tooltips.scanResultTooltip import ScanResultTooltip
from carbonui.uicore import uicore
from eveservices.menu import GetMenuService
from eve.common.lib import appConst as const

class NoScanProbesEntry(SE_BaseClassCore):

    def Startup(self, *args):
        self.label = EveLabelMedium(parent=self, text=localization.GetByLabel('UI/Inflight/Scanner/NoProbesDeployed'), bold=True, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, left=20)

    def Load(self, node):
        pass

    def GetHeight(self, *args):
        node, width = args
        node.height = 22
        return node.height


class ScanProbeEntryNew(SE_BaseClassCore):

    def Startup(self, *args):
        self.icon = Icon(parent=self, pos=(1, 0, 24, 24), align=uiconst.CENTERLEFT)
        self.labelLeft = EveLabelMedium(parent=self, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, left=26)
        self.probeExpiry = EveLabelMediumBold(parent=self, align=uiconst.CENTERRIGHT, state=uiconst.UI_DISABLED, left=66)
        self.probeScanRange = EveLabelMediumBold(parent=self, align=uiconst.CENTERRIGHT, state=uiconst.UI_DISABLED, left=6)

    def Load(self, node):
        if node.Get('selectable', 1) and node.Get('selected', 0):
            self.Select()
        else:
            self.Deselect()
        probeName = sm.GetService('scanSvc').GetProbeLabel(node.probe.probeID)
        self.labelLeft.text = probeName
        self.icon.LoadIconByTypeID(node.probe.typeID, ignoreSize=True)
        self.icon.hint = evetypes.GetName(node.probe.typeID)
        self.UpdateProbeState()
        self.updateStateTimer = AutoTimer(500, self.UpdateProbeState)

    def UpdateProbeState(self):
        if self.destroyed:
            self.updateStateTimer = None
            return
        probe = self.sr.node.probe
        if probe.expiry is None:
            expiryText = localization.GetByLabel('UI/Generic/None')
        else:
            expiry = max(0L, long(probe.expiry) - blue.os.GetSimTime())
            if expiry <= 0:
                expiryText = localization.GetByLabel('UI/Inflight/Scanner/Expired')
            elif expiry >= const.MIN:
                expiryText = localization.formatters.FormatTimeIntervalShortWritten(expiry, showFrom='day', showTo='minute')
            else:
                expiryText = localization.formatters.FormatTimeIntervalShortWritten(expiry, showFrom='day', showTo='second')
        self.probeExpiry.text = expiryText
        if probe.state == const.probeStateInactive:
            self.opacity = 0.5
        else:
            self.opacity = 1.0
        if probe.scanRange < const.AU:
            probeScanRangeText = FmtDist(probe.scanRange, maxdemicals=2)
        else:
            probeScanRangeText = FmtDist(probe.scanRange, maxdemicals=0)
        self.probeScanRange.text = probeScanRangeText

    def OnDblClick(self, *args):
        sm.ScatterEvent('OnProbeScanner_FocusOnProbe', self.sr.node.probeID)

    def GetHeight(self, *args):
        node, width = args
        node.height = 26
        return node.height

    def OnMouseEnter(self, *args):
        SE_BaseClassCore.OnMouseEnter(self, *args)
        sm.ScatterEvent('OnProbeScanner_ProbeEntryMouseEnter', self.sr.node.probeID)

    def OnMouseExit(self, *args):
        SE_BaseClassCore.OnMouseExit(self, *args)
        sm.ScatterEvent('OnProbeScanner_ProbeEntryMouseExit', self.sr.node.probeID)

    def OnClick(self, *args):
        if self.sr.node:
            if self.sr.node.Get('selectable', 1):
                self.sr.node.scroll.SelectNode(self.sr.node)
            eve.Message('ListEntryClick')
            if self.sr.node.Get('OnClick', None):
                self.sr.node.OnClick(self)

    def GetMenu(self):
        if self.sr.node and self.sr.node.Get('GetMenu', None):
            return self.sr.node.GetMenu(self)
        if getattr(self, 'itemID', None) or getattr(self, 'typeID', None):
            return GetMenuService().GetMenuFromItemIDTypeID(getattr(self, 'itemID', None), getattr(self, 'typeID', None))
        return []


class NoScanResult(BaseListEntry):
    BACKGROUND_COLOR = '#06465A'

    def ApplyAttributes(self, attributes):
        super(NoScanResult, self).ApplyAttributes(attributes)
        self.mainContainer = Container(name='MainContainer', parent=self, align=uiconst.TOALL, bgColor=Color.HextoRGBA(self.BACKGROUND_COLOR))

    def Load(self, node):
        if node.ignored and node.filtered:
            text = localization.GetByLabel('UI/Inflight/Scanner/FilteredAndIgnoredResults')
        elif node.ignored:
            text = localization.GetByLabel('UI/Inflight/Scanner/IgnoredResults')
        elif node.filtered:
            text = localization.GetByLabel('UI/Inflight/Scanner/FilteredResults')
        else:
            text = localization.GetByLabel('UI/Inflight/Scanner/NoScanResults')
        self.noScanResultsLabel = EveLabelMediumBold(name='NoScanResultsLabel', parent=self.mainContainer, align=uiconst.CENTER, text=text)

    def GetHeight(self, *args):
        node, width = args
        node.height = 24
        return node.height


class ScanResultNew(BaseListEntryCustomColumns):
    default_name = 'ScanResultNew'
    redHi = (0.8, 0.0, 0.0, 0.9)
    red = (0.5, 0.0, 0.0, 0.9)
    redLo = (0.3, 0.0, 0.0, 0.9)
    orangeHi = (0.8, 0.5, 0.0, 0.9)
    orange = (0.5, 0.3, 0.0, 0.9)
    orangeLo = (0.3, 0.2, 0.0, 0.9)
    greenHi = (0.0, 0.7, 0.0, 0.9)
    green = (0.0, 0.4, 0.0, 0.9)
    greenLo = (0.0, 0.2, 0.0, 0.9)
    warpButton = None

    def ApplyAttributes(self, attributes):
        BaseListEntryCustomColumns.ApplyAttributes(self, attributes)
        self.columnContainer = Container(align=uiconst.TOALL, parent=self)
        self.signalColumn = Container(align=uiconst.TORIGHT, parent=self.columnContainer, clipChildren=True, width=50)
        self.signalColumn.label = EveLabelMedium(parent=self.signalColumn, align=uiconst.CENTERRIGHT, left=6)
        self.pushColumnContainer = Container(align=uiconst.TOALL, parent=self.columnContainer, clipChildren=True)
        self.AddIconColumn()
        self.distanceColumn = self.AddColumn(textAlign=uiconst.CENTERRIGHT)
        self.idColumn = self.AddColumn()
        self.nameColumn = self.AddColumn()
        self.groupColumn = self.AddColumn()
        self.groupColumn.align = uiconst.TOALL
        self.columns.append(self.signalColumn)
        self.statusBar = BarGraphBarHorizontal(name='statusBar', parent=self, align=uiconst.TOBOTTOM_NOPUSH, pos=(0, 0, 0, 2), bgColor=(0, 0, 0, 0), state=uiconst.UI_DISABLED)
        self.onMouseExit = Signal()

    def AddIconColumn(self):
        column = Container(align=uiconst.TOLEFT, width=16, state=uiconst.UI_DISABLED, parent=self.pushColumnContainer)
        self.columns.append(column)
        self.icon = Sprite(parent=column, align=uiconst.CENTERLEFT, pos=(0, -1, 16, 16))
        return column

    def AddColumn(self, textAlign = None):
        column = Container(align=uiconst.TOLEFT, parent=self.pushColumnContainer, clipChildren=True, padRight=1)
        self.columns.append(column)
        textAlign = textAlign or uiconst.CENTERLEFT
        left = uiconst.LABELTABMARGIN + 8 if textAlign == uiconst.CENTERLEFT else 0
        column.label = EveLabelMedium(parent=column, align=textAlign, left=left)
        return column

    def Load(self, node):
        if node.selected:
            self.Select()
        else:
            self.Deselect()
        newResult = False
        if hasattr(node, 'newResult'):
            if node.newResult:
                newResult = True
        certainty = node.result.certainty
        newCert = certainty
        oldCert = node.result.prevCertainty
        certChange = newCert - oldCert
        signalText = ''
        from eve.client.script.ui.shared.mapView.markers.mapMarkerScanResult import IsResultWithinWarpDistance
        if node.result.isPerfect and IsResultWithinWarpDistance(node.result) and InShipInSpace():
            if not self.warpButton:
                self.warpButton = ButtonIcon(name='warpButton', func=self.WarpToAction, parent=self.signalColumn, align=uiconst.CENTERRIGHT, width=22, left=6, iconSize=22, texturePath='res:/UI/Texture/Icons/44_32_18.png', hint=localization.GetByLabel('UI/Commands/WarpTo'))
                if newResult:
                    self.warpButton.Blink(3)
        else:
            percentage = math.floor(newCert * 1000) / 10.0
            signalText = localization.GetByLabel('UI/Common/Percentage', percentage=percentage)
        hiColor, loColor, normalColor = self.GetColors(certainty)
        if newCert or oldCert:
            if certChange > 0:
                baseProportion = oldCert
                changeProportion = certChange
                changeColor = hiColor
            else:
                changeProportion = min(newCert, abs(certChange))
                baseProportion = max(0.0, newCert - changeProportion)
                changeColor = loColor
            graphData = []
            graphData.append(('base', baseProportion, normalColor))
            graphData.append(('change', changeProportion, changeColor))
            self.statusBar.LoadGraphData(graphData, animateIn=True)
        self.distanceColumn.label.text = FmtDist(node.distance)
        self.idColumn.label.text = node.result.id
        self.nameColumn.label.text = node.displayName
        self.groupColumn.label.text = node.groupName
        self.signalColumn.label.text = signalText
        texturePath = GetResultTexturePath(node.result)
        self.icon.texturePath = texturePath
        color = GetResultColor(certainty)
        self.icon.SetRGBA(*color)
        if newResult:
            node.newResult = False
        self.name = 'scan_result_{}'.format(node.result.id)
        self.OnColumnResize(node.columnWidths)
        self.tooltipPanelClassInfo = ScanResultTooltip(node)

    def UpdateDistanceText(self):
        if not self.distanceColumn or not self.distanceColumn.label:
            return
        self.distanceColumn.label.text = FmtDist(self.node.distance)

    def GetColors(self, certainty):
        col = GetResultColor(certainty)
        hiColor = Color(*col).SetBrightness(0.5).GetRGBA()
        color = Color(*col).SetBrightness(0.35).GetRGBA()
        loColor = Color(*col).SetBrightness(0.2).GetRGBA()
        return (hiColor, loColor, color)

    def WarpToAction(self, *args):
        GetMenuService().WarpToScanResult(self.sr.node.result.id)

    def GetHeight(self, *args):
        node, width = args
        node.height = 24
        return node.height

    def RegisterForMouseExit(self, callback):
        self.onMouseExit.connect(callback)

    def UnregisterForMouseExit(self, callback):
        self.onMouseExit.disconnect(callback)

    def OnMouseEnter(self, *args):
        BaseListEntryCustomColumns.OnMouseEnter(self, *args)
        sm.ScatterEvent('OnProbeScanner_ScanResultMouseEnter', self.sr.node.result)

    def OnMouseExit(self, *args):
        BaseListEntryCustomColumns.OnMouseExit(self, *args)
        if self._hiliteFill:
            self._hiliteFill.color_override = None
        result = self.sr.node.result
        sm.ScatterEvent('OnProbeScanner_ScanResultMouseExit', result)
        resultID = getattr(result, 'id', None)
        if resultID:
            self.onMouseExit(self, resultID)

    def OnDblClick(self, *args):
        BaseListEntryCustomColumns.OnDblClick(self, *args)
        sm.ScatterEvent('OnProbeScanner_ProbeEntryDblClick', self.sr.node.result)

    def OnClick(self, *args):
        BaseListEntryCustomColumns.OnClick(self, *args)
        doDScan = uicore.cmd.IsCombatCommandLoaded('CmdRefreshDirectionalScan')
        if doDScan:
            pos = self.sr.node.result.pos
            bp = sm.GetService('michelle').GetBallpark()
            pos = geo2.Vec3Subtract(pos, bp.GetCurrentEgoPos())
            uicore.cmd.GetCommandAndExecute('OpenDirectionalScanner', toggle=False)
            sm.GetService('directionalScanSvc').ScanTowardsItem(self.sr.node.itemID, mapPosition=pos)

    def GetMenu(self):
        if self.sr.node and self.sr.node.Get('GetMenu', None):
            self.DoSelectNode()
            return self.sr.node.GetMenu(self)
        return []

    def OnColumnResize(self, newCols):
        for i, width in enumerate(newCols):
            if self.columns[i].align != uiconst.TOALL:
                self.columns[i].width = width - 1

    def ShowNewResultHighlight(self):
        self.ConstructHiliteFill()
        self._hiliteFill.color_override = eveThemeColor.THEME_ALERT

    @classmethod
    def GetCopyData(cls, node):
        return '<t>'.join([node.result.id,
         node.scanGroupName,
         node.groupName,
         node.typeName,
         localization.GetByLabel('UI/Common/Percentage', percentage=node.result.certainty * 100),
         FmtDist(node.distance)])

    @staticmethod
    def GetDefaultColumnAndDirection():
        return (localization.GetByLabel('UI/Common/ID'), True)

    @staticmethod
    def GetFixedColumns():
        return {'': 16,
         localization.GetByLabel('UI/Inflight/Scanner/SignalStrength'): 60}

    @staticmethod
    def GetRightAlignedColumns():
        return [localization.GetByLabel('UI/Inflight/Scanner/SignalStrength')]

    @staticmethod
    def GetColumns():
        return ['',
         localization.GetByLabel('UI/Common/Distance'),
         localization.GetByLabel('UI/Common/ID'),
         localization.GetByLabel('UI/Common/Name'),
         localization.GetByLabel('UI/Common/Group'),
         localization.GetByLabel('UI/Inflight/Scanner/SignalStrength')]

    @staticmethod
    def GetStretchColumns():
        return [localization.GetByLabel('UI/Common/Group')]

    @staticmethod
    def GetColumnsMinSize():
        return {localization.GetByLabel('UI/Common/Distance'): 50,
         localization.GetByLabel('UI/Common/ID'): 30,
         localization.GetByLabel('UI/Common/Name'): 70,
         localization.GetByLabel('UI/Common/Group'): 70}

    @staticmethod
    def GetColumnsDefaultSize():
        return {localization.GetByLabel('UI/Common/Distance'): 70,
         localization.GetByLabel('UI/Common/ID'): 60,
         localization.GetByLabel('UI/Common/Name'): 100,
         localization.GetByLabel('UI/Common/Group'): 100}
