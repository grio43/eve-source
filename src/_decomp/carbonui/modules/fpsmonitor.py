#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\modules\fpsmonitor.py
import blue
import trinity
import uthread
import carbonui.const as uiconst
from carbonui.control.window import Window
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.primitives.gridcontainer import GridContainer
from carbonui.primitives.base import Base
from carbonui.primitives.container import Container
from carbonui.primitives.line import Line
from carbonui.text.custom import TextCustom
from carbonui.text.styles import TextHeader, TextDetail
from eve.client.script.ui import eveColor
import evegraphics.settings as gfxsettings
from carbonui.uiconst import PickState
COLOR = eveColor.LIME_GREEN
COLOR_HEX = eveColor.LIME_GREEN_HEX
COLOR_SECONDARY = eveColor.LEAFY_GREEN
COLOR_SECONDARY_HEX = eveColor.LEAFY_GREEN_HEX
COLOR_TERTIARY = eveColor.COPPER_OXIDE_GREEN
COLOR_TERTIARY_HEX = eveColor.COPPER_OXIDE_GREEN_HEX

class GraphRenderer(Base):
    __renderObject__ = trinity.Tr2Sprite2dRenderJob
    default_state = uiconst.UI_PICKCHILDREN
    default_pickState = PickState.CHILDREN

    def ApplyAttributes(self, attributes):
        Base.ApplyAttributes(self, attributes)
        self.viewport = trinity.TriViewport()
        self.linegraph = trinity.Tr2LineGraph()
        self.linegraphSize = 0
        self.linegraph.name = 'FPS'
        self.linegraph.color = COLOR
        blue.statistics.SetAccumulator(self.linegraph.name, self.linegraph)
        self.generatedLinegraph = trinity.Tr2LineGraph()
        self.generatedLinegraph.name = 'Trinity/smoothedGeneratedFrames'
        self.generatedLinegraph.color = COLOR_TERTIARY
        blue.statistics.SetAccumulator(self.generatedLinegraph.name, self.generatedLinegraph)
        self.renderJob = trinity.CreateRenderJob('Graphs')
        self.renderObject.renderJob = self.renderJob
        self.renderJob.PythonCB(self.AdjustViewport)
        self.renderJob.SetViewport(self.viewport)
        self.renderJob.SetStdRndStates(trinity.RM_SPRITE2D)
        self.renderer = self.renderJob.RenderLineGraph()
        self.renderer.showLegend = False
        self.renderer.lineGraphs.append(self.linegraph)

    def Close(self):
        Base.Close(self)
        self.renderer.scaleChangeCallback = None

    def AdjustViewport(self):
        l, t = self.displayX, self.displayY
        parent = self.GetParent()
        while parent:
            l += parent.displayX
            t += parent.displayY
            parent = parent.GetParent()

        self.viewport.x = l
        self.viewport.y = t
        self.viewport.width = self._displayWidth
        self.viewport.height = self._displayHeight
        if self.linegraphSize != self._displayWidth:
            self.linegraph.SetSize(self._displayWidth)
            self.generatedLinegraph.SetSize(self._displayWidth)
            self.linegraphSize = self._displayWidth

    def SetShowGeneratedFrames(self, show):
        if not show:
            self.renderer.lineGraphs.remove(self.generatedLinegraph)
        elif show:
            self.renderer.lineGraphs.append(self.generatedLinegraph)


class ExtraInfoLabel(ContainerAutoSize):
    default_align = uiconst.NOALIGN

    def ApplyAttributes(self, attributes):
        super(ExtraInfoLabel, self).ApplyAttributes(attributes)
        self.isAutoSizeEnabled = 'width' not in attributes
        self.label = TextCustom(parent=self, align=uiconst.TOPLEFT)
        self.caption = attributes.caption
        self.value = attributes.value
        self.ApplyText()

    def ApplyText(self):
        text = "<fontsize=12><color='{}'>{}: </color></fontsize><color='{}'>{}</color>".format(COLOR_SECONDARY_HEX, self.caption, COLOR_HEX, self.value)
        self.label.SetText(text)

    def SetValue(self, value):
        self.value = value
        self.ApplyText()


class FpsMonitor(Window):
    default_caption = 'FPS Monitor'
    default_windowID = 'fpsMonitor2'
    default_width = 360
    default_height = 180
    __notifyevents__ = ['OnGraphicSettingsChanged']

    def ApplyAttributes(self, attributes):
        super(FpsMonitor, self).ApplyAttributes(attributes)
        self.fpsStat = blue.statistics.Find('FPS')
        self.gfpsStat = blue.statistics.Find('Trinity/smoothedGeneratedFrames')
        self.frameTimeStat = blue.statistics.Find('Trinity/SmoothedFrameTime')
        self.upscalingLabel = None
        self.hasUpscaling = False
        self.hasFrameGen = False
        self.gr = None
        self.extraInfoCont = FlowContainer(name='extraInfoCont', parent=self.sr.main, align=uiconst.TOBOTTOM, state=uiconst.UI_NORMAL, contentSpacing=(12, 2), padding=4)
        self.graphContainer = Container(parent=self.sr.main, align=uiconst.TOALL, padding=(4, 9, 4, 0))
        self.legendContainer = GridContainer(parent=self.graphContainer, align=uiconst.TORIGHT, width=24, columns=1, padLeft=4, top=-7)
        self.ConstructLegend()
        self.ConstructGraphRenderer()
        self.labelContainer = Container(parent=self.graphContainer, align=uiconst.TOBOTTOM, height=20)
        self.fpsLabel = TextCustom(name='fpsLabel', parent=self.labelContainer, bold=True, color=COLOR, pickState=PickState.ON, align=uiconst.TOLEFT)
        self.fpsLabel.hint = 'FPS'
        self.msLabel = TextCustom(name='fpsLabel', parent=self.labelContainer, color=COLOR_SECONDARY, pickState=PickState.ON, align=uiconst.TOLEFT)
        self.msLabel.hint = 'Frame time (ms)'
        self.genFpsLabel = TextCustom(name='genFpsLabel', parent=self.labelContainer, bold=True, color=COLOR_TERTIARY, align=uiconst.TORIGHT, pickState=PickState.ON)
        self.genFpsLabel.display = False
        self.genFpsLabel.hint = 'Generated FPS'
        self.ConstructExtraInfoLabels()
        uthread.new(self.UpdateLabelsThread)

    def ConstructExtraInfoLabels(self):
        adapterInfo = trinity.adapters.GetAdapterInfo(trinity.device.adapter)
        ExtraInfoLabel(parent=self.extraInfoCont, caption='Shader Model', value=trinity.GetShaderModel())
        ExtraInfoLabel(parent=self.extraInfoCont, caption='Platform', value=trinity.platform)
        ExtraInfoLabel(parent=self.extraInfoCont, caption='GPU', value=adapterInfo.description)
        self.throttlingLabel = ExtraInfoLabel(parent=self.extraInfoCont, caption='FPS Throttling')
        self.RefreshUpscalingLabel()

    def RefreshUpscalingLabel(self):
        upscalingInfo = trinity.device.GetUpscalingInfo()
        if self.hasUpscaling != upscalingInfo['technique'] == trinity.UPSCALING_TECHNIQUE.NONE or self.hasFrameGen == upscalingInfo['frameGeneration']:
            return
        self.hasUpscaling = upscalingInfo['technique'] != trinity.UPSCALING_TECHNIQUE.NONE
        self.hasFrameGen = upscalingInfo['frameGeneration']
        if self.upscalingLabel is None:
            self.upscalingLabel = ExtraInfoLabel(parent=self.extraInfoCont, caption='Upscaling', value='')
        techniqueName = upscalingInfo['techniqueName']
        settingName = upscalingInfo['settingName']
        labelText = '%s (%s) %s' % (techniqueName, settingName, 'Frame Gen' if self.hasFrameGen else '')
        self.upscalingLabel.SetValue(labelText)
        self.upscalingLabel.display = self.hasUpscaling
        self.upscalingLabel.AutoFitToContent()
        self.genFpsLabel.display = self.hasFrameGen
        self.gr.SetShowGeneratedFrames(self.hasFrameGen)

    def ConstructGraphRenderer(self):
        self.gr = GraphRenderer(parent=self.graphContainer, align=uiconst.TOALL)
        self.renderer = self.gr.renderer
        self.renderer.scaleChangeCallback = self.ScaleChangeHandler
        for i in xrange(4):
            cont = Container(parent=self.graphContainer, align=uiconst.TOTOP_PROP, height=0.25)
            Line(parent=cont, align=uiconst.TOTOP, color=COLOR, opacity=0.05)
            if i == 3:
                Line(parent=cont, align=uiconst.TOBOTTOM, color=COLOR, opacity=0.075)

    def ConstructLegend(self):
        self.legendLabels = []
        for i in xrange(4):
            label = TextDetail(parent=self.legendContainer, align=uiconst.TOTOP, width=20, color=COLOR_SECONDARY)
            self.legendLabels.append(label)

    def ScaleChangeHandler(self):
        numLabels = len(self.legendLabels)
        label = 1.0
        labelStep = 1.0 / float(numLabels)
        for i in xrange(numLabels):
            labelValue = int((label / self.renderer.scale * self.renderer.legendScale + 0.5) / 100)
            self.legendLabels[i].SetText(str(labelValue))
            label -= labelStep

    def UpdateLabelsThread(self):
        while not self.destroyed:
            self.RefreshUpscalingLabel()
            if self.hasFrameGen:
                self.genFpsLabel.text = '%.2f' % (self.gfpsStat.value / 100.0)
            self.fpsLabel.text = '%.2f' % (self.fpsStat.value / 100.0)
            self.msLabel.text = '(%.1fms)' % (self.frameTimeStat.value * 1000.0)
            value = self._GetThrottlingLabelText()
            self.throttlingLabel.SetValue(value)
            blue.synchro.SleepWallclock(500)

    def _GetThrottlingLabelText(self):
        if trinity.device.allowThrottling:
            t = trinity.device.throttlingState
        else:
            t = 0
        reasons = {1: 'Not focused',
         2: 'Window hidden',
         4: 'Thermal',
         -8: 'Other'}
        if t == 0:
            value = 'None'
        else:
            value = ' + '.join((v for k, v in reasons.items() if t & k != 0))
        return value

    def OnGraphicSettingsChanged(self, changes):
        if gfxsettings.GFX_UPSCALING_TECHNIQUE in changes or gfxsettings.GFX_UPSCALING_SETTING in changes or gfxsettings.GFX_FRAMEGENERATION_ENABLED in changes:
            self.RefreshUpscalingLabel()
