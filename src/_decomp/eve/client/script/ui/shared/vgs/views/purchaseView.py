#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\vgs\views\purchaseView.py
import logging
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.uianimations import animations
from eve.client.script.ui.control.eveLabel import Label
from gametime import SEC
from localization import GetByLabel
log = logging.getLogger(__name__)
MINIMUM_PROGRESS_DISPLAY_TIME = 1.2 * SEC

class BasePanel(Container):
    default_align = uiconst.TOLEFT
    default_opacity = 0.0
    TRANSITION_TIME = 0.5

    def AnimEntry(self):
        animations.FadeIn(self, duration=self.TRANSITION_TIME, timeOffset=self.TRANSITION_TIME)

    def AnimExit(self):
        animations.FadeOut(self, duration=self.TRANSITION_TIME)


class PurchaseSuccessPanel(BasePanel):
    ICON_FOREGROUND = 'res:/UI/Texture/vgs/purchase_success_fg.png'
    ICON_BACKGROUND = 'res:/UI/Texture/vgs/purchase_success_bg.png'
    AUDIO_EVENT = 'store_purchase_success'
    ICON_WIDTH = 72
    ICON_HEIGHT = 64
    ICON_HEIGHT_TRANSFORM = 78
    PADDING_ICON_LEFT = 10
    PADDING_ICON_TO_TEXT = 20
    PADDING_TOP_TO_TEXT = 12
    PADDING_TEXT_TO_SUBTEXT = 12
    FONTSIZE_TEXT = 14
    FONTSIZE_SUBTEXT = 12
    default_name = 'PurchaseSuccessPanel'
    default_text = 'UI/VirtualGoodsStore/Purchase/Completed'
    default_subtext = 'UI/VirtualGoodsStore/Purchase/NewPurchaseInstruction'

    def ApplyAttributes(self, attributes):
        super(PurchaseSuccessPanel, self).ApplyAttributes(attributes)
        default_text = GetByLabel(self.default_text)
        default_subtext = GetByLabel(self.default_subtext) if self.default_subtext is not None else None
        self.text = attributes.pop('text', default_text)
        self.subtext = attributes.pop('subText', default_subtext)
        self.subtext_time_offset = attributes.get('subTextTimeOffset', 2)
        self._add_icon()
        self._add_text()

    def _add_icon(self):
        icon_container = Container(name='icon_container', parent=self, align=uiconst.TOLEFT, width=self.ICON_WIDTH, padLeft=self.PADDING_ICON_LEFT)
        self.icon_foreground_transform = Transform(name='icon_foreground_transform', parent=icon_container, align=uiconst.CENTERTOP, width=self.ICON_WIDTH, height=self.ICON_HEIGHT_TRANSFORM, scalingCenter=(0.5, 0.5))
        self.icon_foreground = Sprite(name='icon_foreground_sprite', parent=self.icon_foreground_transform, align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath=self.ICON_FOREGROUND, width=self.ICON_WIDTH, height=self.ICON_HEIGHT, opacity=0)
        self.icon_background_transform = Transform(name='icon_background_transform', parent=icon_container, align=uiconst.CENTERTOP, width=self.ICON_WIDTH, height=self.ICON_HEIGHT_TRANSFORM, scalingCenter=(0.5, 0.5))
        self.icon_background = Sprite(name='icon_background', parent=self.icon_background_transform, align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath=self.ICON_BACKGROUND, width=self.ICON_WIDTH, height=self.ICON_HEIGHT, opacity=0)

    def _add_text(self):
        text_container = Container(name='text_container', parent=self, align=uiconst.TOALL, padLeft=self.PADDING_ICON_TO_TEXT, padTop=self.PADDING_TOP_TO_TEXT)
        text_width = self.width - self.PADDING_ICON_LEFT - self.ICON_WIDTH - self.PADDING_ICON_TO_TEXT
        label_container = ContainerAutoSize(name='label_container', parent=text_container, align=uiconst.TOTOP)
        Label(name='label', parent=label_container, align=uiconst.CENTER, text=self.text, bold=True, fontsize=self.FONTSIZE_TEXT, width=text_width)
        if self.subtext:
            self.subtext_container = ContainerAutoSize(name='subtext_container', parent=text_container, align=uiconst.TOTOP, top=self.PADDING_TEXT_TO_SUBTEXT, opacity=0)
            Label(name='subtext_label', parent=self.subtext_container, align=uiconst.CENTER, text=self.subtext, fontsize=self.FONTSIZE_SUBTEXT, width=text_width)

    def AnimEntry(self):
        super(PurchaseSuccessPanel, self).AnimEntry()
        sm.GetService('audio').SendUIEvent(self.AUDIO_EVENT)
        animations.FadeIn(self.icon_background, duration=0.5, timeOffset=self.TRANSITION_TIME)
        animations.FadeIn(self.icon_foreground, duration=0.5, timeOffset=self.TRANSITION_TIME + 0.5)
        animations.Tr2DScaleTo(self.icon_background_transform, startScale=(2.0, 2.0), endScale=(1.0, 1.0), duration=0.25, timeOffset=self.TRANSITION_TIME)
        animations.Tr2DScaleTo(self.icon_foreground_transform, startScale=(2.0, 2.0), endScale=(1.0, 1.0), duration=0.25, timeOffset=self.TRANSITION_TIME + 0.5)
        if hasattr(self, 'subtext_container'):
            animations.FadeTo(self.subtext_container, timeOffset=self.subtext_time_offset)


class PurchaseFailedPanel(PurchaseSuccessPanel):
    ICON_FOREGROUND = 'res:/UI/Texture/vgs/purchase_fail_fg.png'
    ICON_BACKGROUND = 'res:/UI/Texture/vgs/purchase_fail_bg.png'
    AUDIO_EVENT = 'store_purchase_failure'
    default_text = 'UI/VirtualGoodsStore/Purchase/Failed'
    default_subtext = None


class ConfirmPurchasePanel(PurchaseSuccessPanel):
    ICON_FOREGROUND = 'res:/UI/Texture/WindowIcons/attention.png'
    ICON_BACKGROUND = 'res:/UI/Texture/Vgs/loading-track.png'
    AUDIO_EVENT = 'store_purchase_failure'
    default_text = 'UI/VirtualGoodsStore/Purchase/ConfirmationRequired'
    default_subtext = 'UI/VirtualGoodsStore/Purchase/ConfirmationInstructions'
