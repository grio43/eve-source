#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation\empireui\empireThemedTooltip.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.primitives.gradientSprite import GradientSprite
from carbonui.primitives.sprite import Sprite
from charactercreator.client.scalingUtils import GetScaleFactor
from eve.client.script.ui.login.charcreation.label import CCLabel
from eve.client.script.ui.login.charcreation.technologyViewUtils import VerticalLineDecoration
from eve.client.script.ui.util.uix import GetTextHeight
from eve.common.lib.appConst import raceAmarr, raceCaldari, raceGallente, raceMinmatar
from math import pi
BOX_WIDTH_MIN_RES = 284
OUTER_BOX_PADDING_MIN_RES = 10
ICON_SIZE_MIN_RES = 23
ICON_PADDING_MIN_RES = 3
TEXT_PADDING_TOP_MIN_RES = 9
TEXT_PADDING_RIGHT_MIN_RES = 9
TEXT_PADDING_BOTTOM_MIN_RES = 11
TEXT_PADDING_INTERNAL_MIN_RES = 9
TEXT_WIDTH_MIN_RES = BOX_WIDTH_MIN_RES - 2 * ICON_PADDING_MIN_RES - ICON_SIZE_MIN_RES - TEXT_PADDING_RIGHT_MIN_RES
TITLE_FONTSIZE_MIN_RES = 11
TEXT_FONTSIZE_MIN_RES = 11
LINE_WIDTH = 4
LINE_DECO_HEIGHT_MIN_RES = 41
CURVED_GRADIENT_WIDTH_MIN_RES = 17
CURVED_GRADIENT_TEXTURE_BY_RACE = {raceAmarr: 'res:/UI/Texture/Classes/EmpireSelection/curvedGradientAmarr.png',
 raceCaldari: 'res:/UI/Texture/Classes/EmpireSelection/curvedGradientCaldari.png',
 raceGallente: 'res:/UI/Texture/Classes/EmpireSelection/curvedGradientGallente.png',
 raceMinmatar: 'res:/UI/Texture/Classes/EmpireSelection/curvedGradientMinmatar.png'}
BLURR_TEXTURE = 'res:/UI/Texture/Classes/EmpireSelection/shipTooltipBlur.png'
TITLE_OPACITY = 1.0
TEXT_OPACITY = 0.75
LINE_OPACITY = 1.0
CURVED_GRADIENT_OPACITY = 0.5
BACKGROUND_GRADIENT_OPACITY = 0.5
BLURR_BOX_OPACITY = 0.8
BACKGROUND_GRADIENT_TINT_BY_RACE = {raceAmarr: (0.51, 0.44, 0.32),
 raceCaldari: (0.29, 0.43, 0.5),
 raceGallente: (0.21, 0.4, 0.4),
 raceMinmatar: (0.4, 0.22, 0.2)}
BLURR_CORNERSIZE = 20

def get_tooltip_width():
    return BOX_WIDTH_MIN_RES * GetScaleFactor()


class EmpireThemedTooltip(object):
    default_state = uiconst.UI_DISABLED

    def __init__(self, raceID, icon, title, text, name, parent, left, top):
        self.raceID = raceID
        self.icon = icon
        self.title = title.upper()
        self.text = text
        self.name = name
        self.parent = parent
        self.left = left
        self.top = top
        self.calculate_sizes()
        self.add_tooltip_text()
        self.add_tooltip_box()

    def close(self):
        if self.is_box_available():
            self.tooltip_box_wrapper.Close()
        if self.is_text_available():
            self.tooltip_text_wrapper.Close()

    def is_box_available(self):
        return self.tooltip_box_wrapper and not self.tooltip_box_wrapper.destroyed

    def is_text_available(self):
        return self.tooltip_text_wrapper and not self.tooltip_text_wrapper.destroyed

    def calculate_sizes(self):
        self.label_width = TEXT_WIDTH_MIN_RES * GetScaleFactor()
        self.title_fontsize = TITLE_FONTSIZE_MIN_RES * GetScaleFactor()
        self.text_fontsize = TEXT_FONTSIZE_MIN_RES * GetScaleFactor()
        self.text_padding_top = TEXT_PADDING_TOP_MIN_RES * GetScaleFactor()
        self.text_padding_bottom = TEXT_PADDING_BOTTOM_MIN_RES * GetScaleFactor()
        self.text_padding_right = TEXT_PADDING_BOTTOM_MIN_RES * GetScaleFactor()
        self.text_padding_internal = TEXT_PADDING_INTERNAL_MIN_RES * GetScaleFactor()
        self.icon_size = ICON_SIZE_MIN_RES * GetScaleFactor()
        self.icon_padding = ICON_PADDING_MIN_RES * GetScaleFactor()
        self.title_height = self.calculate_title_height()
        self.text_height = self.calculate_text_height()
        self.label_height = self.title_height + self.text_padding_internal + self.text_height
        self.box_width = BOX_WIDTH_MIN_RES * GetScaleFactor()
        self.box_height = self.text_padding_top + self.label_height + self.text_padding_bottom
        self.outer_box_padding = OUTER_BOX_PADDING_MIN_RES * GetScaleFactor()

    def calculate_title_height(self):
        title_height = GetTextHeight(strng=self.title, fontsize=self.title_fontsize, hspace=1, uppercase=1, width=self.label_width)
        return title_height

    def calculate_text_height(self):
        text_height = GetTextHeight(strng=self.text, fontsize=self.text_fontsize, hspace=1, uppercase=0, width=self.label_width)
        return text_height

    def add_tooltip_text(self):
        self.tooltip_text_wrapper = Container(name='TooltipTextWrapper_%s' % self.name, parent=self.parent, align=uiconst.TOTOP_NOPUSH, width=self.box_width, height=self.box_height, top=self.top, left=self.left, opacity=0.0, state=uiconst.UI_DISABLED)
        self.tooltip_text_wrapper.SetOrder(0)
        tooltip_text_container = Container(name='TooltipTextContainer_%s' % self.name, parent=self.tooltip_text_wrapper, align=uiconst.TOLEFT, width=self.box_width, height=self.box_height)
        self.add_icon(tooltip_text_container)
        self.add_label(tooltip_text_container)

    def add_icon(self, parent_container):
        icon_container = Container(name='IconContainer_%s' % self.name, parent=parent_container, align=uiconst.TOLEFT, width=self.icon_size, height=self.icon_size, padding=self.icon_padding)
        Sprite(name='Icon_%s' % self.name, parent=icon_container, align=uiconst.CENTERTOP, width=self.icon_size, height=self.icon_size, texturePath=self.icon)

    def add_label(self, parent_container):
        label_wrapper = Container(name='LabelWrapper_%s' % self.name, parent=parent_container, align=uiconst.TOLEFT, width=self.label_width, height=self.label_height)
        label_container = Container(name='LabelContainer_%s' % self.name, parent=label_wrapper, align=uiconst.TOTOP, width=self.label_width, height=self.label_height, padTop=self.text_padding_top, padBottom=self.text_padding_bottom)
        self.add_title(label_container)
        self.add_text(label_container)

    def add_title(self, parent_container):
        title_container = Container(name='TitleContainer_%s' % self.name, parent=parent_container, align=uiconst.TOTOP, width=self.label_width, height=self.title_height)
        CCLabel(text=self.title, name='Title_%s' % self.name, parent=title_container, align=uiconst.TOALL, fontsize=self.title_fontsize, uppercase=1, letterspace=1, bold=True, opacity=TITLE_OPACITY)

    def add_text(self, parent_container):
        text_container = Container(name='TextContainer_%s' % self.name, parent=parent_container, align=uiconst.TOTOP, width=self.label_width, height=self.text_height, padTop=self.text_padding_internal)
        CCLabel(text=self.text, name='Text_%s' % self.name, parent=text_container, align=uiconst.TOALL, fontsize=self.text_fontsize, uppercase=0, letterspace=1, bold=False, opacity=TEXT_OPACITY)

    def add_tooltip_box(self):
        self.tooltip_box_wrapper = Container(name='TooltipBoxWrapper_%s' % self.name, parent=self.parent, align=uiconst.TOTOP_NOPUSH, width=self.box_width, height=self.box_height, top=self.top, left=self.left, opacity=0.0, state=uiconst.UI_DISABLED)
        tooltip_box_container = Container(name='TooltipBoxContainer_%s' % self.name, parent=self.tooltip_box_wrapper, align=uiconst.TOLEFT, width=self.box_width, height=self.box_height)
        self.add_line(tooltip_box_container)
        self.add_curved_gradient(tooltip_box_container)
        self.add_background_gradient(tooltip_box_container)
        self.add_tooltip_blurr(tooltip_box_container)

    def add_line(self, parent_container):
        VerticalLineDecoration(name='LineDecoration_%s' % self.name, parent=parent_container, align=uiconst.TOLEFT_NOPUSH, width=LINE_WIDTH, height=parent_container.height, lineHeight=parent_container.height, lineDecorationHeight=LINE_DECO_HEIGHT_MIN_RES * GetScaleFactor(), opacity=LINE_OPACITY)

    def add_curved_gradient(self, parent_container):
        Sprite(name='CurvedGradient_%s' % self.name, parent=parent_container, align=uiconst.TOLEFT_NOPUSH, width=CURVED_GRADIENT_WIDTH_MIN_RES * GetScaleFactor(), height=parent_container.height, texturePath=CURVED_GRADIENT_TEXTURE_BY_RACE[self.raceID], opacity=CURVED_GRADIENT_OPACITY, rotation=3 * pi / 2)

    def add_background_gradient(self, parent_container):
        GradientSprite(name='BackgroundGradient_%s' % self.name, parent=parent_container, align=uiconst.TOLEFT_NOPUSH, width=parent_container.width, height=parent_container.height, opacity=BACKGROUND_GRADIENT_OPACITY, rgbData=((0.0, BACKGROUND_GRADIENT_TINT_BY_RACE[self.raceID]),), alphaData=((0.0, 1.0), (1.0, 0.0)))

    def add_tooltip_blurr(self, parent_container):
        tooltip_blurr_wrapper = Container(name='TooltipBlurrWrapper_%s' % self.name, parent=parent_container, align=uiconst.TOTOP_NOPUSH, width=self.box_width + 2 * self.outer_box_padding, height=self.box_height + 2 * self.outer_box_padding, top=-self.outer_box_padding, left=-self.outer_box_padding)
        tooltip_blurr_container = Container(name='TooltipBlurrContainer_%s' % self.name, parent=tooltip_blurr_wrapper, align=uiconst.TOLEFT, width=self.box_width + 2 * self.outer_box_padding, height=self.box_height + 2 * self.outer_box_padding)
        Frame(name='TooltipBlurr_%s' % self.name, parent=tooltip_blurr_container, align=uiconst.TOTOP, width=self.box_width + 2 * self.outer_box_padding, height=self.box_height + 2 * self.outer_box_padding, cornerSize=BLURR_CORNERSIZE, texturePath=BLURR_TEXTURE, opacity=BLURR_BOX_OPACITY)

    def set_visibility(self, is_visible):
        opacity = 1.0 if is_visible else 0.0
        if self.is_box_available():
            self.tooltip_box_wrapper.SetOrder(0)
            self.tooltip_box_wrapper.opacity = opacity
        if self.is_text_available():
            self.tooltip_text_wrapper.SetOrder(0)
            self.tooltip_text_wrapper.opacity = opacity
