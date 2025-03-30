#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveclientqatools\textureViewer.py
import blue
import eveicon
import logging
import trinity
import math
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui import uiconst
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.checkbox import Checkbox
from carbonui.control.combo import Combo
from carbonui.control.window import Window
from carbonui.control.slider import Slider
from carbonui.primitives.base import Base
from carbonui.primitives.container import Container
from carbonui.util.various_unsorted import GetWindowAbove
from eve.client.script.ui.control.eveLabel import EveLabelSmall, EveLabelLarge
from evegraphics.graphicEffects.texture import TextureInfo
log = logging.getLogger(__name__)

class EffectContainer(Base):
    __guid__ = 'form.EffectContainer'
    __renderObject__ = trinity.Tr2Sprite2dRenderJob

    def ApplyAttributes(self, attributes):
        Base.ApplyAttributes(self, attributes)
        self.vpw = attributes.get('viewportWidth', 0)
        self.vph = attributes.get('viewportHeight', 0)
        self.viewport = trinity.TriViewport()
        self.pushRenderTargetStep = trinity.TriStepPushRenderTarget()
        self.setViewPortStep = trinity.TriStepSetViewport()
        self.setEffectStep = trinity.TriStepRenderEffect(attributes.effect)
        self.renderJob = trinity.TriRenderJob()
        self.renderJob.steps.append(trinity.TriStepSetStdRndStates(trinity.RM_FULLSCREEN))
        self.renderJob.steps.append(trinity.TriStepPushDepthStencil(None))
        self.renderJob.steps.append(self.pushRenderTargetStep)
        self.renderJob.steps.append(self.setViewPortStep)
        self.renderJob.steps.append(self.setEffectStep)
        self.renderJob.steps.append(trinity.TriStepPopRenderTarget())
        self.renderJob.steps.append(trinity.TriStepPopDepthStencil())
        self.renderJob.status = trinity.RJ_INIT
        self.renderObject.renderJob = self.renderJob

    def Close(self, *args, **kwargs):
        self.renderJob = None
        self.viewport = None
        self.pushRenderTargetStep = None
        self.setViewPortStep = None
        self.setEffectStep = None
        super(EffectContainer, self).Close(*args, **kwargs)

    def SetParent(self, parent, idx = None):
        Base.SetParent(self, parent, idx)
        wnd = GetWindowAbove(self)
        if wnd:
            stack = wnd.GetStack()
            if stack:
                stack.RegisterSceneContainer(self)
            else:
                wnd.RegisterSceneContainer(self)

    def UpdateAlignment(self, *args):
        ret = Base.UpdateAlignment(self, *args)
        self.UpdateViewPort()
        return ret

    def _OnResize(self):
        self.UpdateViewPort()

    def UpdateViewPort(self, *args):
        l, t, w, h = self.GetAbsoluteViewport()
        if not h:
            return
        if not self.vpw or not self.viewport.height:
            return
        zoom = float(w) / self.vpw
        if zoom * self.vph > h:
            zoom = float(h) / self.vph
        self.viewport.width = int(math.ceil(zoom * self.vpw))
        self.viewport.height = int(math.ceil(zoom * self.vph))
        self.viewport.x = l + (w - self.viewport.width) / 2
        self.viewport.y = t + (h - self.viewport.height) / 2
        self.setViewPortStep.viewport = self.viewport

    def SetViewport(self, width, height):
        self.vpw = width
        self.vph = height
        self.UpdateViewPort()

    def SetEffect(self, effect):
        self.setEffectStep.effect = effect


class TexturePanel(Container):
    default_caption = 'TexturePanel'
    default_windowID = 'TexturePanel'
    default_minSize = (512, 512)
    default_opacity = 1.0
    default_showHeader = True

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.textureInfo = attributes.get('textureInfo')
        self.showHeader = attributes.get('showHeader', TexturePanel.default_showHeader)
        header = attributes.get('customLabel', '')
        if header:
            header = header + '(' + self.textureInfo.path + ')'
        else:
            header = self.textureInfo.path
        if self.showHeader:
            nameContainer = Container(align=uiconst.TOTOP, parent=self, height=16, padBottom=4)
            EveLabelLarge(parent=nameContainer, align=uiconst.CENTER, text=header)
        self.infoContainer = Container(name='infoContainer', align=uiconst.TOLEFT, parent=self, width=175, padRight=12, padLeft=12)
        self.typeText = self._MakeLabelPair('Type', self.textureInfo.textureTypeName)
        self.formatText = self._MakeLabelPair('Format', self.textureInfo.format)
        self.colorSpaceText = self._MakeLabelPair('Color Space', self.textureInfo.colorSpace)
        self.sizeText = self._MakeLabelPair('Size', self._GetTextureSize())
        self.memoryText = self._MakeLabelPair('Memory', self.textureInfo.memory)
        self.msaaText = self._MakeLabelPair('MSAA', self.textureInfo.msaa)
        self.lodEnabledText = self._MakeLabelPair('Lod Enabled', 'Yes' if self.textureInfo.lodEnabled else 'No')
        self.cpuMip = self._MakeLabelPair('CPU Mip', self.textureInfo.cpuMip)
        self.gpuMip = self._MakeLabelPair('GPU Mip', self.textureInfo.gpuMip)
        self.colorSpace = self._MakeCombo('Color Space', [ (cs, i) for i, cs in enumerate(self.textureInfo.GetColorSpaceOptions()) ], self._OnSetColorSpace)
        self.colorCombo = self._MakeCombo('Colors', [('RGB', 1),
         ('R', 2),
         ('G', 3),
         ('B', 4),
         ('A', 5)], self._OnColorChanged)
        self.cubeViewCombo = self._MakeCombo('View', [('View', 0),
         ('Cross', 1),
         ('Rows', 2),
         ('Forward', 3),
         ('Backward', 4),
         ('Right', 5),
         ('Left', 6),
         ('Up', 7),
         ('Down', 8)], self._OnViewChanged)
        if not self.textureInfo.IsCube():
            self.cubeViewCombo.Disable()
        self.mipCombo = self._MakeCombo('Mip', [('None', -1)] + [ ('%s' % mip, mip) for mip in range(0, self.textureInfo.mips) ], self._OnMipChanged)
        self.minSlider = self._MakeSlider('Min', self._OnMinValueChanged, value=0.0)
        self.maxSlider = self._MakeSlider('Max', self._OnMaxValueChanged, value=1.0)
        self.sliceSlider = self._MakeSlider('Slice', self._OnSliceValueChanged, value=0, minValue=0, maxValue=max(self.textureInfo.arraySize, 1), step=1)
        if not self.textureInfo.isArray:
            self.sliceSlider.Disable()
        self.effectContainer = EffectContainer(name='effectContainer', align=uiconst.TOALL, parent=self, effect=self.textureInfo.effect, viewportHeight=self.textureInfo.height, viewportWidth=self.textureInfo.width)
        self.timer = AutoTimer(500, self.UpdateMipLabels)

    def Close(self, *args, **kwargs):
        self.textureInfo = None
        super(TexturePanel, self).Close(*args, **kwargs)

    def _MakeCheckBox(self, label, toggled, callback):
        cont = Container(align=uiconst.TOTOP, parent=self.infoContainer, height=24, padBottom=4)
        EveLabelSmall(parent=cont, align=uiconst.CENTERLEFT, text=label + ': ')
        return Checkbox(parent=cont, align=uiconst.CENTERRIGHT, checked=toggled, callback=callback)

    def _MakeLabelPair(self, label, info):
        cont = Container(align=uiconst.TOTOP, parent=self.infoContainer, height=24, padBottom=4)
        EveLabelSmall(parent=cont, align=uiconst.CENTERLEFT, text=label + ': ')
        l = EveLabelSmall(parent=cont, align=uiconst.CENTERRIGHT, text=info)
        return l

    def _MakeCombo(self, label, options, callback):
        cont = Container(align=uiconst.TOTOP, parent=self.infoContainer, height=20, padBottom=4)
        EveLabelSmall(parent=cont, align=uiconst.CENTERLEFT, text=label + ': ')
        return Combo(parent=cont, align=uiconst.TORIGHT, options=options, callback=callback, height=20)

    def _MakeSlider(self, label, callback, minValue = 0.0, maxValue = 1.0, value = 0.0, step = 0.001):
        cont = Container(align=uiconst.TOTOP, parent=self.infoContainer, height=24, padBottom=4)
        EveLabelSmall(parent=cont, align=uiconst.CENTERLEFT, text=label + ': ')
        return Slider(parent=cont, align=uiconst.CENTERRIGHT, width=100, minValue=minValue, maxValue=maxValue, value=value, step=step, on_dragging=callback)

    def UpdateMipLabels(self):
        if self.textureInfo:
            self.textureInfo.RefreshInfo()
            self.cpuMip.SetText(self.textureInfo.cpuMip)
            self.gpuMip.SetText(self.textureInfo.gpuMip)

    def _OnPanelToggled(self):
        self.split_view.expanded = not self.split_view.expanded
        if self.split_view.expanded:
            self.panelToggler.SetTexturePath(eveicon.navigate_back)
        else:
            self.panelToggler.SetTexturePath(eveicon.navigate_forward)

    def _OnColorChanged(self, combo, key, value):
        if value == 1:
            self.textureInfo.ShowAllChannels()
        elif value == 2:
            self.textureInfo.ShowRedChannel()
        elif value == 3:
            self.textureInfo.ShowGreenChannel()
        elif value == 4:
            self.textureInfo.ShowBlueChannel()
        elif value == 5:
            self.textureInfo.ShowAlphaChannel()

    def _OnViewChanged(self, combo, key, value):
        self.textureInfo.SetViewMode(key.upper())

    def _OnMipChanged(self, combo, key, value):
        self.textureInfo.SetMipLevel(value)

    def _OnMinValueChanged(self, slider):
        self.textureInfo.SetMinValue(slider.GetValue())

    def _OnMaxValueChanged(self, slider):
        self.textureInfo.SetMaxValue(slider.GetValue())

    def _OnSetColorSpace(self, combo, key, value):
        self.textureInfo.SetColorSpace(key)

    def _OnSliceValueChanged(self, slider):
        self.textureInfo.SetSlice(slider.GetValue())

    def _OnClose(self, *args, **kw):
        self.textureInfo = None

    def OnResizeUpdate(self, *args):
        self.effectContainer.UpdateViewPort()

    def _GetTextureSize(self):
        size = '%dx%d' % (self.textureInfo.width, self.textureInfo.height)
        if self.textureInfo.depth > 1:
            size += 'x%d' % self.textureInfo.depth
        return size

    def SetTextureInfo(self, ti):
        self.timer.KillTimer()
        self.textureInfo = ti
        self.typeText.text = self.textureInfo.textureTypeName
        self.formatText.text = self.textureInfo.format
        self.colorSpaceText.text = self.textureInfo.colorSpace
        self.sizeText.text = self._GetTextureSize()
        self.msaaText.text = self.textureInfo.msaa
        self.lodEnabledText.text = 'Yes' if self.textureInfo.lodEnabled else 'No'
        self.cpuMip.text = self.textureInfo.cpuMip
        self.gpuMip.text = self.textureInfo.gpuMip
        self.colorSpace.SelectItemByIndex(self.textureInfo.GetColorSpaceOptions().index(self.textureInfo.colorSpace))
        self.colorCombo.SelectItemByIndex(0)
        self.cubeViewCombo.SelectItemByIndex(0)
        if not self.textureInfo.IsCube():
            self.cubeViewCombo.Disable()
        else:
            self.cubeViewCombo.Enable()
        self.mipCombo.LoadOptions([ ('%s' % mip, mip) for mip in range(0, self.textureInfo.mips) ])
        self.minSlider.SetValue(0.0)
        self.maxSlider.SetValue(1.0)
        self.effectContainer.SetEffect(self.textureInfo.effect)
        self.effectContainer.SetViewport(self.textureInfo.width, self.textureInfo.height)
        self.timer = AutoTimer(500, self.UpdateMipLabels)


class TextureWindow(Window):
    default_caption = 'TextureWindow'
    default_windowID = 'TextureWindow'
    default_minSize = (512, 512)

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        o = attributes.get('object', None)
        texture = attributes.get('texture', None)
        label = attributes.get('label', None)
        self.textureInfos = {}
        if texture:
            self.textureInfos[None] = TextureInfo(texture)
        elif o:
            references = blue.FindAllReferences(o)
            textures = [ TextureInfo(r) for r in references.keys() if isinstance(r, trinity.TriTextureRes) ]
            self.textureInfos = {t.path:t for t in textures}
        self.sortedPaths = sorted(list(set(self.textureInfos.keys())))
        if len(self.textureInfos) > 1:
            cont = Container(name='textureHeader', align=uiconst.TOTOP, parent=self.content, height=24, padBottom=4, padLeft=12)
            EveLabelSmall(parent=cont, align=uiconst.TOLEFT, text='Textures: ')
            ButtonIcon(parent=cont, align=uiconst.TORIGHT, width=24, height=24, iconSize=16, texturePath=eveicon.navigate_forward, func=lambda : self.MoveToTexture(1))
            ButtonIcon(parent=cont, align=uiconst.TORIGHT, width=24, height=24, iconSize=16, texturePath=eveicon.navigate_back, func=lambda : self.MoveToTexture(-1))
            self.selection = Combo(parent=cont, align=uiconst.TOALL, options=[ (s, s) for s in self.sortedPaths ], select=self.sortedPaths[0], callback=self._OnSelectTexture, height=24)
        if len(self.sortedPaths) != 0:
            self.view = TexturePanel(parent=self.content, textureInfo=self.textureInfos[self.sortedPaths[0]], showHeader=len(self.sortedPaths) == 1, customLabel=label)
        else:
            EveLabelLarge(parent=self.content, text='No Textures Found')

    def Close(self, *args, **kwargs):
        self.textureInfos = []
        super(TextureWindow, self).Close(*args, **kwargs)

    def _OnSelectTexture(self, combo, key, value):
        self.view.SetTextureInfo(self.textureInfos[key])

    def MoveToTexture(self, offset):
        selectedIndex = self.selection.GetIndex()
        newSelection = (selectedIndex + offset) % len(self.sortedPaths)
        if newSelection < 0:
            newSelection += len(self.sortedPaths)
        self.selection.SelectItemByIndex(newSelection)
        self.view.SetTextureInfo(self.textureInfos[self.sortedPaths[newSelection]])
