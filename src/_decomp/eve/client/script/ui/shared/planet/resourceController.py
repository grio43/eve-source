#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\planet\resourceController.py
import blue
import carbonui.const as uiconst
import evetypes
import localization
import uthread
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.sys.serviceConst import ROLE_GML
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.uicore import uicore
from carbonui.util.various_unsorted import SortListOfTuples
from eve.client.script.ui.control import eveIcon, eveLabel
from eve.client.script.ui.control.gauge import Gauge
from eve.client.script.ui.shared.planet import planetCommon
from eve.common.lib import appConst as const
from inventorycommon import typeHelpers
from localization import GetByLabel

class ResourceController(ContainerAutoSize):
    __notifyevents__ = []
    default_name = 'ResourceController'
    default_align = uiconst.TOTOP
    default_state = uiconst.UI_HIDDEN

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        self.CreateLayout()
        sm.RegisterNotify(self)

    def CreateLayout(self):
        legend = ResourceLegend(parent=self)
        planetUI = sm.GetService('planetUI')
        self.resourceList = ResourceList(parent=self)
        planetObject = sm.GetService('planetSvc').GetPlanet(planetUI.planetID)
        resourceInfo = planetObject.remoteHandler.GetPlanetResourceInfo()
        sortedList = []
        for typeID, quality in resourceInfo.iteritems():
            name = evetypes.GetName(typeID)
            sortedList.append((name, (typeID, quality)))

        sortedList = SortListOfTuples(sortedList)
        for typeID, quality in sortedList:
            qualityRemapped = quality / const.MAX_DISPLAY_QUALITY
            self.resourceList.AddItem(typeID, quality=max(0, min(1.0, qualityRemapped)))

    def StopLoadingResources(self, resourceTypeID):
        self.resourceList.StopLoading(resourceTypeID)

    def StartLoadingResources(self):
        self.resourceList.StartLoading()

    def ResourceSelected(self, resourceTypeID):
        for item in self.resourceList.children:
            if item.typeID == resourceTypeID:
                self.resourceList.SelectItem(item)

    def EnterSurveyMode(self):
        self.resourceList.SetOpacity(0.5)
        self.resourceList.state = uiconst.UI_DISABLED

    def ExitSurveyMode(self):
        self.resourceList.SetOpacity(1)
        self.resourceList.state = uiconst.UI_PICKCHILDREN


class ResourceLegend(Container):
    default_name = 'ResourceLegend'
    default_align = uiconst.TOTOP
    default_height = 30
    default_state = uiconst.UI_PICKCHILDREN
    LINE_COLOR = (1, 1, 1, 0.5)
    RAMP_HEIGHT = 8
    HEIGHT = 4
    ADJUSTER_WIDTH = 16
    MIN_COLOR_RANGE = 26
    LEGENDWIDTH = 240

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.leftSpacerMaxWidth = self.ADJUSTER_WIDTH + self.LEGENDWIDTH - self.MIN_COLOR_RANGE
        self.CreateLayout()

    def CreateLayout(self):
        scale = Container(name='scale', parent=self, align=uiconst.TOTOP, pos=(0,
         0,
         0,
         self.HEIGHT), padding=(4, 2, 4, -4))
        Line(name='scaleBase', parent=scale, align=uiconst.TOTOP, color=self.LINE_COLOR)
        Line(name='leftTick', parent=scale, align=uiconst.TOLEFT, color=self.LINE_COLOR)
        Line(name='rightTick', parent=scale, align=uiconst.TORIGHT, color=self.LINE_COLOR)
        Line(name='centerTick', parent=scale, align=uiconst.RELATIVE, color=self.LINE_COLOR, pos=(self.LEGENDWIDTH / 2,
         1,
         1,
         self.HEIGHT))
        for x in (0.1, 0.2, 0.3, 0.4, 0.6, 0.7, 0.8, 0.9):
            left = int(self.LEGENDWIDTH * x)
            Line(name='miniorTick_%f' % x, parent=scale, align=uiconst.RELATIVE, color=self.LINE_COLOR, pos=(left,
             1,
             1,
             self.HEIGHT / 2))

        self.legendContainer = Container(parent=self, name='colorFilterContainer', align=uiconst.TOTOP, statestate=uiconst.UI_PICKCHILDREN, pos=(0,
         8,
         self.LEGENDWIDTH + 2 * self.ADJUSTER_WIDTH,
         self.ADJUSTER_WIDTH))
        self.leftSpacer = Container(parent=self.legendContainer, name='leftSpacer', align=uiconst.TOLEFT, pos=(0,
         0,
         self.ADJUSTER_WIDTH,
         self.ADJUSTER_WIDTH), state=uiconst.UI_PICKCHILDREN)
        self.centerSpacer = Container(parent=self.legendContainer, name='centerSpacer', align=uiconst.TOLEFT, pos=(0,
         0,
         self.LEGENDWIDTH,
         self.ADJUSTER_WIDTH), state=uiconst.UI_PICKCHILDREN)
        self.rightSpacer = Container(parent=self.legendContainer, name='rightSpacer', align=uiconst.TOLEFT, pos=(0,
         0,
         self.ADJUSTER_WIDTH,
         self.ADJUSTER_WIDTH), state=uiconst.UI_PICKCHILDREN)
        adjusterMin = eveIcon.Icon(iname='leftAdjuster', icon='ui_73_16_185', parent=self.leftSpacer, align=uiconst.TORIGHT, pos=(0,
         0,
         self.ADJUSTER_WIDTH - 2,
         self.ADJUSTER_WIDTH), state=uiconst.UI_NORMAL, hint=localization.GetByLabel('UI/PI/Common/ResourcesMinimumVisibleHint'), color=(1, 1, 1, 0.5))
        adjusterMax = eveIcon.Icon(name='rightAdjuster', icon='ui_73_16_186', parent=self.rightSpacer, align=uiconst.TOLEFT, pos=(0,
         0,
         self.ADJUSTER_WIDTH - 2,
         self.ADJUSTER_WIDTH), state=uiconst.UI_NORMAL, hint=localization.GetByLabel('UI/PI/Common/ResourcesMaximumVisibleHint'), color=(1, 1, 1, 0.5))
        adjusterMin.OnMouseDown = (self.OnAdjustMouseDown, adjusterMin)
        adjusterMin.OnMouseUp = (self.OnAdjustMouseUp, adjusterMin)
        adjusterMin.OnMouseMove = (self.OnAdjustMouseMove, adjusterMin)
        adjusterMin.OnMouseEnter = (self.OnAdjusterMouseEnter, adjusterMin)
        adjusterMin.OnMouseExit = (self.OnAdjusterMouseExit, adjusterMin)
        adjusterMax.OnMouseDown = (self.OnAdjustMouseDown, adjusterMax)
        adjusterMax.OnMouseUp = (self.OnAdjustMouseUp, adjusterMax)
        adjusterMax.OnMouseMove = (self.OnAdjustMouseMove, adjusterMax)
        adjusterMax.OnMouseEnter = (self.OnAdjusterMouseEnter, adjusterMax)
        adjusterMax.OnMouseExit = (self.OnAdjusterMouseExit, adjusterMax)
        colorRamp = Sprite(name='ColorRamp', parent=self.centerSpacer, texturePath='res:/dx9/model/worldobject/planet/resource_colorramp.dds', color=(1, 1, 1, 0.75), padding=(0, 4, 0, 4), state=uiconst.UI_NORMAL, align=uiconst.TOALL)
        colorRamp.OnMouseDown = (self.OnAdjustMouseDown, colorRamp)
        colorRamp.OnMouseUp = (self.OnAdjustMouseUp, colorRamp)
        colorRamp.OnMouseMove = (self.OnMoveRange, colorRamp)
        low, hi = sm.GetService('planetUI').GetResourceDisplayRange()
        scalar = self.LEGENDWIDTH - 1
        self.leftSpacer.width = int(low * scalar) + self.ADJUSTER_WIDTH
        self.centerSpacer.width = int((hi - low) * scalar)

    def OnAdjusterMouseEnter(self, adjuster, *args):
        adjuster.SetRGBA(1, 1, 1, 0.75)
        PlaySound(uiconst.SOUND_ENTRY_HOVER)

    def OnAdjusterMouseExit(self, adjuster, *args):
        adjuster.SetRGBA(1, 1, 1, 0.5)

    def OnAdjustMouseDown(self, adjuster, button):
        if button == 0:
            adjuster.dragging = True

    def OnAdjustMouseUp(self, adjuster, button):
        if button == 0:
            adjuster.dragging = False

    def OnAdjustMouseMove(self, adjuster, *args):
        if getattr(adjuster, 'dragging', False) and uicore.uilib.leftbtn:
            if adjuster.name.startswith('right'):
                self.centerSpacer.width += uicore.uilib.dx
                position = self.centerSpacer.width + self.leftSpacer.width - self.ADJUSTER_WIDTH
                if position > self.LEGENDWIDTH - self.ADJUSTER_WIDTH:
                    self.centerSpacer.width = self.LEGENDWIDTH - self.leftSpacer.width
                elif position > self.LEGENDWIDTH:
                    self.centerSpacer.width = self.LEGENDWIDTH - (self.leftSpacer.width - self.ADJUSTER_WIDTH)
                elif self.centerSpacer.width < self.MIN_COLOR_RANGE:
                    self.centerSpacer.width = self.MIN_COLOR_RANGE
            else:
                width = self.leftSpacer.width
                dx = uicore.uilib.dx
                if self.centerSpacer.width - uicore.uilib.dx < self.MIN_COLOR_RANGE:
                    dx = self.centerSpacer.width - self.MIN_COLOR_RANGE
                width += dx
                if width < self.ADJUSTER_WIDTH:
                    width = self.ADJUSTER_WIDTH
                elif width > self.leftSpacerMaxWidth:
                    width = self.leftSpacerMaxWidth
                dx = width - self.leftSpacer.width
                self.leftSpacer.width = width
                self.centerSpacer.width -= dx
            self.UpdateColorRamp()

    def OnMoveRange(self, adjuster, *args):
        if getattr(adjuster, 'dragging', False):
            self.leftSpacer.width += uicore.uilib.dx
            position = self.centerSpacer.width + self.leftSpacer.width - self.ADJUSTER_WIDTH
            if position > self.LEGENDWIDTH - self.ADJUSTER_WIDTH:
                self.leftSpacer.width = self.LEGENDWIDTH - self.centerSpacer.width
            elif position > self.LEGENDWIDTH:
                self.leftSpacer.width = self.LEGENDWIDTH - (self.centerSpacer.width - self.ADJUSTER_WIDTH)
            elif self.leftSpacer.width < self.ADJUSTER_WIDTH:
                self.leftSpacer.width = self.ADJUSTER_WIDTH
            self.UpdateColorRamp()

    def UpdateColorRamp(self):
        low = self.leftSpacer.width - self.ADJUSTER_WIDTH
        hi = low + self.centerSpacer.width
        sm.GetService('planetUI').SetResourceDisplayRange(low / float(self.LEGENDWIDTH - 1), hi / float(self.LEGENDWIDTH - 1))


class ResourceNameLabel(eveLabel.EveLabelMedium):

    def ApplyAttributes(self, attributes):
        eveLabel.EveLabelMedium.ApplyAttributes(self, attributes)
        self.toolTipTextWidthThreshold = attributes.get('toolTipTextWidthThreshold', 0)
        self.SetRightAlphaFade(self.toolTipTextWidthThreshold, maxFadeWidth=10)


class ResourceList(ContainerAutoSize):
    default_name = 'ResourceList'
    default_align = uiconst.TOTOP
    default_state = uiconst.UI_PICKCHILDREN

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        self.AddItem(None)

    def AddItem(self, typeID, quality = None):
        ResourceListItem(parent=self, typeID=typeID, quality=quality)

    def ClearItems(self):
        self.children.Clear()

    def SelectItem(self, selectedItem):
        for item in self.children:
            if item != selectedItem:
                item.Deselect()
            else:
                item.Select()

    def StopLoading(self, typeID):
        item = self.GetItemByType(typeID)
        item.StopLoading()

    def GetItemByType(self, typeID):
        for item in self.children:
            if item.typeID == typeID:
                return item

    def GetSelected(self):
        for item in self.children:
            if item.selected:
                return item


class ResourceListItem(Container):
    ITEM_HEIGHT = 28
    SELECT_BLOCK_PADDING = 1
    LEVEL_COLOR = (0.85, 0.85, 0.85, 1)
    LEVEL_BG_COLOR = (0.85, 0.85, 0.85, 0.25)
    LEVEL_WIDTH = 112
    LEVEL_HEIGHT = 10
    LEVEL_LEFT = 150
    SELECT_FILL_COLOR = (1.0, 1.0, 1.0, 0.25)
    HOVER_FILL_COLOR = (1.0, 1.0, 1.0, 0.25)
    EMPTY_COLOR = (1, 1, 1, 0)
    ICON_SIZE = 24
    ICON_LEFT = 0
    default_name = 'ResourceListItem'
    default_left = 0
    default_top = 0
    default_width = 0
    default_height = ITEM_HEIGHT
    default_align = uiconst.TOTOP
    default_state = uiconst.UI_NORMAL
    default_typeID = None
    default_selected = False
    default_quality = None

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.typeID = attributes.get('typeID', self.default_typeID)
        self.quality = attributes.get('quality', self.default_quality)
        if self.typeID is None:
            self.selected = True
        else:
            self.selected = False
        self.CreateLayout()

    def CreateLayout(self):
        if self.typeID is None:
            text = localization.GetByLabel('UI/PI/Common/NoFilter')
            self.icon = None
            self.loadingIcon = None
        else:
            self.icon = eveIcon.Icon(parent=self, align=uiconst.CENTERLEFT, pos=(0,
             0,
             self.ICON_SIZE,
             self.ICON_SIZE), state=uiconst.UI_DISABLED, ignoreSize=True, typeID=self.typeID, size=self.ICON_SIZE)
            text = evetypes.GetName(self.typeID)
            self.loadingIcon = Transform(parent=self, align=uiconst.CENTERLEFT, pos=(0,
             0,
             self.ICON_SIZE,
             self.ICON_SIZE), state=uiconst.UI_HIDDEN)
            load = eveIcon.Icon(icon='ui_77_32_13', parent=self.loadingIcon, IgnoreSize=True, pos=(0,
             0,
             self.ICON_SIZE,
             self.ICON_SIZE), align=uiconst.CENTER)
        self.container = Container(parent=self, name='mainContainer', align=uiconst.TOALL, state=uiconst.UI_DISABLED)
        self.resourceName = ResourceNameLabel(text=text, parent=self, left=6 + (self.ICON_SIZE if self.typeID is not None else 0), top=0, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, toolTipTextWidthThreshold=105)
        if self.typeID is not None:
            self.ConstructQualityGauge()
        self.selectBlock = Fill(parent=self, name='selectBlock', state=uiconst.UI_DISABLED, align=uiconst.TOALL, padding=(0,
         self.SELECT_BLOCK_PADDING,
         0,
         self.SELECT_BLOCK_PADDING), color=self.SELECT_FILL_COLOR if self.selected else self.EMPTY_COLOR)

    def ConstructQualityGauge(self):
        if self.quality is not None:
            gauge = Gauge(parent=self, pos=(0,
             0,
             self.LEVEL_WIDTH,
             self.LEVEL_HEIGHT), align=uiconst.CENTERRIGHT, state=uiconst.UI_DISABLED, gaugeHeight=self.LEVEL_HEIGHT, value=self.quality)
            gauge.ShowMarkers([ i * 0.1 for i in xrange(1, 10) ], color=(0.0, 0.0, 0.0, 0.2))

    def OnMouseEnter(self, *args):
        if not self.selected:
            PlaySound(uiconst.SOUND_ENTRY_HOVER)
            self.selectBlock.SetRGBA(*self.HOVER_FILL_COLOR)

    def OnMouseExit(self, *args):
        if not self.selected:
            self.selectBlock.SetRGBA(*self.EMPTY_COLOR)

    def OnClick(self, *args):
        sm.GetService('audio').SendUIEvent('msg_pi_scanning_switch_play')
        selected = self.parent.GetSelected()
        if selected == self:
            return
        PlaySound(uiconst.SOUND_ENTRY_SELECT)
        self.parent.SelectItem(self)
        sm.GetService('planetUI').ShowResource(self.typeID)

    def Select(self):
        self.selectBlock.SetRGBA(*self.SELECT_FILL_COLOR)
        if self.loadingIcon:
            self.loadingIcon.state = uiconst.UI_DISABLED
            self.icon.state = uiconst.UI_HIDDEN
            uthread.new(self.loadingIcon.StartRotationCycle, 1.0, 4000.0)
        self.selected = True

    def Deselect(self):
        self.selectBlock.SetRGBA(*self.EMPTY_COLOR)
        self.selected = False

    def StopLoading(self):
        if self.loadingIcon:
            self.loadingIcon.StopRotationCycle()
            self.loadingIcon.state = uiconst.UI_HIDDEN
            self.icon.state = uiconst.UI_DISABLED

    def GetMenu(self):
        if self.typeID is None:
            return []
        ret = sm.GetService('menu').GetMenuFromItemIDTypeID(None, self.typeID, includeMarketDetails=True)
        if session.role & ROLE_GML == ROLE_GML:
            ret.append(('PI: GM / WM Extras', self.GetGMMenu()))
        return ret

    def LoadTooltipPanel(self, tooltipPanel, *args):
        if not self.typeID:
            return
        tooltipPanel.LoadGeneric2ColumnTemplate()
        tooltipPanel.AddLabelMedium(colSpan=2, text=planetCommon.GetProductNameAndTier(self.typeID))
        text = GetByLabel('UI/PI/Common/ResourceDensity', density=int(100 * self.quality))
        tooltipPanel.AddLabelMedium(colSpan=2, text=text)
        tooltipPanel.AddLabelMedium(colSpan=2, cellPadding=(0, 10, 0, 2), text=GetByLabel('UI/InfoWindow/TabNames/RequiredFor'))
        for typeID in planetCommon.GetRequiredForItems(self.typeID):
            label = planetCommon.GetProductNameAndTier(typeID)
            icon = typeHelpers.GetIconFile(typeID)
            tooltipPanel.AddIconLabel(icon=icon, label=label, iconSize=28)

    def GetTooltipPointer(self):
        return uiconst.POINT_LEFT_2

    def GetGMMenu(self):
        ret = []
        ret.append(('Copy typeID', self.CopyTypeID))
        ret.append(('Show resource details: current server version', sm.GetService('planetUI').GMShowResource, (self.typeID, 'current')))
        ret.append(('Show resource details: current player version', sm.GetService('planetUI').GMShowResource, (self.typeID, 'player')))
        ret.append(('Show resource details: base layer', sm.GetService('planetUI').GMShowResource, (self.typeID, 'base')))
        ret.append(('Show resource details: depletion layer', sm.GetService('planetUI').GMShowResource, (self.typeID, 'depletion')))
        ret.append(('Show resource details: Nugget layer', sm.GetService('planetUI').GMShowResource, (self.typeID, 'nuggets')))
        ret.append(None)
        ret.append(('Create nugget layer', sm.GetService('planetUI').GMCreateNuggetLayer, (self.typeID,)))
        return ret

    def CopyTypeID(self):
        blue.pyos.SetClipboardData(str(self.typeID))
