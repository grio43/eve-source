#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\glow.py
import trinity
from carbonui import AxisAlignment, uiconst
from carbonui.control.singlelineedits.singleLineEditFloat import SingleLineEditFloat
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from eve.client.script.ui.control import eveLabel
from carbonui.control.window import Window
from eve.client.script.ui.control.infoIcon import MoreInfoIcon

class GlowTestWindow(Window):
    default_windowID = 'glow_test_window'
    default_caption = 'Glow Test'
    default_width = 520
    default_height = 320

    def __init__(self, **kwargs):
        super(GlowTestWindow, self).__init__(**kwargs)
        self.MakeUnResizeable()
        left_cont = Container(parent=self.GetMainArea(), align=uiconst.TOLEFT, width=200)
        grid = LayoutGrid(parent=ContainerAutoSize(parent=left_cont, align=uiconst.TOTOP), columns=2, cellSpacing=(4, 4))
        eveLabel.EveLabelMedium(parent=grid, align=uiconst.CENTERLEFT, text='Brightness')
        MoreInfoIcon(parent=grid, align=uiconst.CENTER, hint='A global glow brightness scale factor (uicore.desktop.glowBrightness).')
        grid.AddCell(SingleLineEditFloat(align=uiconst.TOPLEFT, maxValue=10.0, decimalPlaces=2, setvalue=uicore.desktop.glowBrightness, OnChange=self._on_brightness_changed), colSpan=2)
        grid = LayoutGrid(parent=ContainerAutoSize(parent=left_cont, align=uiconst.TOTOP, top=16), columns=2, cellSpacing=(4, 4))
        eveLabel.EveLabelMedium(parent=grid, align=uiconst.CENTERLEFT, text='Mouse highlight brightness')
        MoreInfoIcon(parent=grid, align=uiconst.CENTER, hint='A scale factor applied to the glow in a radius around the mouse cursor (uicore.desktop.glowHighlightBrightness).')
        grid.AddCell(SingleLineEditFloat(align=uiconst.TOPLEFT, maxValue=10.0, decimalPlaces=2, setvalue=uicore.desktop.glowHighlightBrightness, OnChange=self._on_highlight_brightness_changed), colSpan=2)
        grid = LayoutGrid(parent=ContainerAutoSize(parent=left_cont, align=uiconst.TOTOP, top=16), columns=2, cellSpacing=(4, 4))
        eveLabel.EveLabelMedium(parent=grid, align=uiconst.CENTERLEFT, text='Mouse highlight radius')
        MoreInfoIcon(parent=grid, align=uiconst.CENTER, hint='The radius (in pixels) around the mouse cursor where the glow is multiplied by the mouse highlight brightness factor (uicore.desktop.glowHighlightRadius).')
        grid.AddCell(SingleLineEditFloat(align=uiconst.TOPLEFT, maxValue=1000.0, decimalPlaces=0, setvalue=uicore.desktop.glowHighlightRadius, OnChange=self._on_highlight_radius_changed), colSpan=2)
        grid = LayoutGrid(parent=ContainerAutoSize(parent=left_cont, align=uiconst.TOTOP, top=16), columns=2, cellSpacing=(4, 4))
        eveLabel.EveLabelMedium(parent=grid, align=uiconst.CENTERLEFT, text='Pincushion distortion')
        MoreInfoIcon(parent=grid, align=uiconst.CENTER, hint='The amount of global distortion applied to the glow effect (uicore.desktop.glowDistortion).')
        grid.AddCell(SingleLineEditFloat(align=uiconst.TOTOP, maxValue=1.0, minValue=-1.0, decimalPlaces=3, setvalue=uicore.desktop.glowDistortion, OnChange=self._on_distortion_changed), colSpan=2)
        sprite_cont = FlowContainer(parent=self.GetMainArea(), align=uiconst.TOTOP, contentAlignment=AxisAlignment.CENTER, contentSpacing=(32, 32))
        color_and_glow_cont = ContainerAutoSize(parent=sprite_cont, align=uiconst.NOALIGN)
        Sprite(parent=color_and_glow_cont, align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED, width=64, height=64, texturePath='res:/UI/Texture/Icons/78_64_4.png', outputMode=trinity.Tr2SpriteTarget.COLOR_AND_GLOW)
        eveLabel.EveLabelMedium(parent=color_and_glow_cont, align=uiconst.CENTERTOP, top=72, text='Tr2SpriteTarget.COLOR_AND_GLOW')
        glow_cont = ContainerAutoSize(parent=sprite_cont, align=uiconst.NOALIGN)
        Sprite(parent=glow_cont, align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED, width=64, height=64, texturePath='res:/UI/Texture/Icons/78_64_4.png', outputMode=trinity.Tr2SpriteTarget.GLOW)
        eveLabel.EveLabelMedium(parent=glow_cont, align=uiconst.CENTERTOP, top=72, text='Tr2SpriteTarget.GLOW')

    def _on_brightness_changed(self, value):
        uicore.desktop.glowBrightness = float(value)

    def _on_highlight_brightness_changed(self, value):
        uicore.desktop.glowHighlightBrightness = float(value)

    def _on_highlight_radius_changed(self, value):
        uicore.desktop.glowHighlightRadius = float(value)

    def _on_distortion_changed(self, value):
        uicore.desktop.glowDistortion = float(value)
