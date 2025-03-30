#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\careerPortal\panels\detailsEntry.py
import eveicon
from carbonui import Align, TextColor
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.utilButtons.showInfoButton import ShowInfoButton
DEFAULT_PADDING = 4

class BaseDetailsEntry(Container):
    default_name = 'DetailsEntry'
    default_align = Align.TOTOP
    default_height = 32
    default_top = DEFAULT_PADDING
    icon_size = default_height
    icon_opacity = 1.0

    def __init__(self, texture_path, text, *args, **kwargs):
        super(BaseDetailsEntry, self).__init__(*args, **kwargs)
        self.texture_path = texture_path
        self.text = text
        self.construct_layout()

    def construct_layout(self):
        self.construct_background_fill()
        self.construct_icon()
        self.construct_name_label()

    def construct_background_fill(self):
        Fill(bgParent=self, opacity=0.03 if self.GetOrder() % 2 == 0 else 0, color=self.background_fill_color)

    def construct_icon(self):
        self.icon_container = Container(name='icon_container', parent=self, align=Align.TOLEFT, pos=(0,
         0,
         self.icon_size,
         self.icon_size))
        self.icon = Sprite(name='icon', parent=self.icon_container, align=Align.CENTER, texturePath=self.texture_path, opacity=self.icon_opacity, pos=(0,
         0,
         self.icon_size,
         self.icon_size))

    def construct_name_label(self):
        self.name_label_container = Container(name='name_label_container', parent=self, left=DEFAULT_PADDING * 2)
        self.name_label = EveLabelMedium(name='name_label', parent=self.name_label_container, align=Align.TOTOP, text=self.text, color=self.text_color)
        if self.name_label._numLines == 1:
            self.name_label.top = 8

    @property
    def background_fill_color(self):
        return Fill.default_color

    @property
    def text_color(self):
        return TextColor.NORMAL


class AlphaRewardDetailsEntry(BaseDetailsEntry):

    def __init__(self, type_id, *args, **kwargs):
        self.type_id = type_id
        super(AlphaRewardDetailsEntry, self).__init__(*args, **kwargs)

    def construct_layout(self):
        super(AlphaRewardDetailsEntry, self).construct_layout()
        self.construct_info_icon()

    def construct_info_icon(self):
        info_icon_container = Container(name='info_icon_container', parent=self, align=Align.TORIGHT, pos=(DEFAULT_PADDING,
         0,
         20,
         20))
        ShowInfoButton(name='info_icon', parent=info_icon_container, align=Align.CENTER, typeID=self.type_id)


class OmegaRewardDetailsEntry(AlphaRewardDetailsEntry):
    __notifyevents__ = ['OnSubscriptionChanged']

    def __init__(self, *args, **kwargs):
        super(OmegaRewardDetailsEntry, self).__init__(*args, **kwargs)
        sm.RegisterNotify(self)

    def Close(self):
        try:
            sm.UnregisterNotify(self)
        finally:
            super(OmegaRewardDetailsEntry, self).Close()

    def construct_layout(self):
        super(OmegaRewardDetailsEntry, self).construct_layout()
        self.construct_omega_icon()
        self.update()

    def construct_background_fill(self):
        if self.has_omega:
            super(OmegaRewardDetailsEntry, self).construct_background_fill()
        else:
            Sprite(bgParent=self, texturePath='res:/UI/Texture/Classes/Industry/Output/hatchPattern.png', tileX=True, tileY=True, color=self.background_fill_color, opacity=0.1)

    def construct_omega_icon(self):
        omega_icon_container = Container(name='omega_icon_container', parent=self, align=Align.TORIGHT, pos=(DEFAULT_PADDING,
         0,
         16,
         16))
        Sprite(name='omega_icon', parent=omega_icon_container, align=Align.CENTER, texturePath=eveicon.omega, pos=(0, 0, 16, 16))

    def update(self):
        if self.has_omega:
            self.icon_container.opacity = 1.0
            self.name_label_container.opacity = 1.0
        else:
            self.icon_container.opacity = 0.5
            self.name_label_container.opacity = 0.5

    def OnSubscriptionChanged(self):
        self.construct_background_fill()
        self.update()

    @property
    def background_fill_color(self):
        return eveColor.OMEGA_YELLOW

    @property
    def text_color(self):
        return eveColor.OMEGA_YELLOW

    @property
    def has_omega(self):
        return sm.GetService('cloneGradeSvc').IsOmega()


class GoalInfoDetailsEntry(BaseDetailsEntry):
    icon_size = 16

    def __init__(self, value, *args, **kwargs):
        self.value = value
        super(GoalInfoDetailsEntry, self).__init__(*args, **kwargs)

    def construct_layout(self):
        super(GoalInfoDetailsEntry, self).construct_layout()
        self.construct_value_label()

    def construct_value_label(self):
        value_label_container = ContainerAutoSize(name='value_label_container', parent=self, align=Align.TORIGHT, left=DEFAULT_PADDING)
        EveLabelMedium(name='value_label', parent=value_label_container, align=Align.CENTERLEFT, text=self.value, color=self.text_color)


class CareerPointsDetailsEntry(BaseDetailsEntry):
    icon_opacity = 0.5
