#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\structure\components\durationSelector.py
from carbonui import const as uiconst
from carbonui import TextColor, TextAlign
from eve.client.script.ui import eveColor
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.primitives.frame import Frame
from carbonui.primitives.line import Line
from eve.client.script.ui.control.eveLabel import EveCaptionSmall, EveCaptionLarge, EveLabelMedium
from eve.client.script.ui.control.infoIcon import MoreInfoIcon
from eve.client.script.ui.cosmetics.structure import paintToolSelections, paintToolSignals
from localization import GetByLabel
from carbonui.uianimations import animations
from carbon.client.script.environment.AudioUtil import PlaySound
DURATION_CARD_WIDTH = 210
DURATION_CARD_HEIGHT = 87

class DurationSelector(ContainerAutoSize):

    def __init__(self, **kw):
        super(DurationSelector, self).__init__(**kw)
        self._duration_cards = {}
        self._construct_layout()

    def Close(self):
        super(DurationSelector, self).Close()

    def set_durations(self, durations):
        self._cards_cont.Flush()
        self._duration_cards.clear()
        for duration in durations:
            self._duration_cards[duration] = DurationCard(parent=self._cards_cont, name='durationCard_%s' % duration, align=uiconst.NOALIGN, duration=duration)

        if len(durations) > 0:
            default_selection = durations[0]
            paintToolSelections.set_selected_duration(default_selection)

    def _construct_layout(self):
        EveCaptionSmall(parent=self, name='topLabel', align=uiconst.TOTOP, text=GetByLabel('UI/Personalization/PaintTool/SelectDuration'), padBottom=16)
        self._cards_cont = FlowContainer(name='cardsLibraryCont', parent=self, align=uiconst.TOTOP, contentSpacing=(28, 28), padBottom=8)
        info_label_text = GetByLabel('UI/Personalization/PaintTool/DurationSelectionInfo')
        info_label_width, info_label_height = EveLabelMedium.MeasureTextSize(info_label_text)
        info_container = Container(name='info_container', parent=self, align=uiconst.TOTOP, height=info_label_height, padBottom=24)
        info_icon = MoreInfoIcon(name='info_icon', parent=info_container, align=uiconst.CENTERLEFT)
        info_icon.LoadTooltipPanel = self.LoadInfoTooltipPanel
        EveLabelMedium(name='infoLabel', parent=info_container, align=uiconst.TOTOP, text=GetByLabel('UI/Personalization/PaintTool/DurationSelectionInfo'), padLeft=24)
        Line(parent=self, align=uiconst.TOTOP, color=tuple(eveColor.WHITE[:3]) + (0.3,), weight=2)

    def LoadInfoTooltipPanel(self, tooltipPanel, *args):
        title_text = GetByLabel('UI/Personalization/PaintTool/DurationSelectionHintTitle')
        body_text = GetByLabel('UI/Personalization/PaintTool/DurationSelectionHintBody')
        wrap_width = 370
        tooltipPanel.state = uiconst.UI_NORMAL
        tooltipPanel.LoadGeneric1ColumnTemplate()
        tooltipPanel.AddCaptionSmall(text=title_text, state=uiconst.UI_NORMAL, wrapWidth=wrap_width)
        tooltipPanel.AddDivider()
        tooltipPanel.AddLabelMedium(text=body_text, state=uiconst.UI_NORMAL, wrapWidth=wrap_width)


class DurationCard(Container):
    default_width = DURATION_CARD_WIDTH
    default_height = DURATION_CARD_HEIGHT
    default_state = uiconst.UI_NORMAL

    def __init__(self, duration, **kw):
        super(DurationCard, self).__init__(**kw)
        self._duration = duration
        paintToolSignals.on_duration_selection_changed.connect(self._on_selected_duration_changed)
        self._construct_layout()
        self.set_selected(False)

    def Close(self):
        paintToolSignals.on_duration_selection_changed.disconnect(self._on_selected_duration_changed)
        super(DurationCard, self).Close()

    def OnClick(self, *args):
        if paintToolSelections.SELECTED_DURATION != self._duration:
            paintToolSelections.set_selected_duration(self._duration)
        PlaySound(uiconst.SOUND_BUTTON_CLICK)

    def OnMouseEnter(self, *args):
        if paintToolSelections.SELECTED_DURATION != self._duration:
            animations.MorphScalar(self._frame, 'glowBrightness', self._frame.glowBrightness, 1.0, duration=0.25)
        PlaySound(uiconst.SOUND_BUTTON_HOVER)

    def OnMouseExit(self, *args):
        if paintToolSelections.SELECTED_DURATION != self._duration:
            animations.MorphScalar(self._frame, 'glowBrightness', self._frame.glowBrightness, 0.0, duration=0.25)

    def _construct_layout(self):
        self._frame = Frame(bgParent=self, name='frame', outputMode=uiconst.OUTPUT_COLOR_AND_GLOW)
        label_cont = ContainerAutoSize(parent=self, name='labelCont', align=uiconst.CENTER, width=DURATION_CARD_WIDTH)
        self._duration_label = EveCaptionLarge(parent=label_cont, name='durationLabel', align=uiconst.TOTOP, textAlign=TextAlign.CENTER, text='%s' % (self._duration / 86400))
        self._bottom_label = EveCaptionSmall(parent=label_cont, name='bottomLabel', align=uiconst.TOTOP, textAlign=TextAlign.CENTER, text=GetByLabel('UI/Personalization/PaintTool/LicenseDuration'))

    def set_selected(self, selected):
        target_text_color = eveColor.LEAFY_GREEN if selected else TextColor.NORMAL
        animations.SpColorMorphTo(self._duration_label, self._duration_label.GetRGBA(), target_text_color, 0.25)
        animations.SpColorMorphTo(self._bottom_label, self._bottom_label.GetRGBA(), target_text_color, 0.25)
        animations.SpColorMorphTo(self._frame, self._frame.GetRGBA(), target_text_color, 0.25)
        target_brightness = 0.75 if selected else 0.0
        animations.MorphScalar(self._frame, 'glowBrightness', self._frame.glowBrightness, target_brightness, duration=0.25)

    def _on_selected_duration_changed(self):
        self.set_selected(self._duration == paintToolSelections.SELECTED_DURATION)
