#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\regionalui\addictionwarningcontainer.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLabel import EveLabelSmall, EveLabelMediumBold
from math import pi
from notifications.client.notificationUIConst import NOTIFICATION_BACKGROUND_UP, NOTIFICATION_BACKGROUND_CORNER_SIZE, NOTIFICATION_BACKGROUND_OFFSET, NOTIFICATION_CENTER_PADDING_H
from regionalui.const import RATING_ICONS, get_icon_path
from regionalui.utils import get_addiction_warning_text, get_playtime_text

class AddictionWarningContainer(ContainerAutoSize):
    default_name = 'AddictionWarning'
    default_state = uiconst.UI_DISABLED
    default_should_add_frame = False
    default_should_add_icons = True
    default_should_add_text = False
    LABEL_PATH = 'UI/RegionalUI/AddictionWarning'
    POPUP_PADDING_H = NOTIFICATION_CENTER_PADDING_H
    POPUP_PADDING_V = 4
    PADDING_RATINGS_TOP = 4
    PADDING_RATINGS_BOTTOM = 3
    PADDING_BETWEEN_RATINGS = 4
    PADDING_TEXT_H = 12
    PADDING_TEXT_TOP = 10
    PADDING_TEXT_BOTTOM = 10
    PADDING_TEXT_BETWEEN_LINES = 5

    def ApplyAttributes(self, attributes):
        super(AddictionWarningContainer, self).ApplyAttributes(attributes)
        self.should_add_frame = attributes.get('should_add_frame', self.default_should_add_frame)
        self.should_add_icons = attributes.get('should_add_icons', self.default_should_add_icons)
        self.should_add_text = attributes.get('should_add_text', self.default_should_add_text)
        self.content = ContainerAutoSize(name='AddictionWarning_Content', parent=self, align=uiconst.TOTOP, width=self.width - 2 * self.POPUP_PADDING_H, padding=(self.POPUP_PADDING_H,
         self.POPUP_PADDING_V,
         self.POPUP_PADDING_H,
         self.POPUP_PADDING_V))
        self.add_frame()
        self.add_icons()
        self.add_text()

    def add_frame(self):
        if not self.should_add_frame:
            return
        Frame(name='AddictionWarning_Frame', bgParent=self, texturePath=NOTIFICATION_BACKGROUND_UP, cornerSize=NOTIFICATION_BACKGROUND_CORNER_SIZE, offset=NOTIFICATION_BACKGROUND_OFFSET)

    def add_icons(self):
        if not self.should_add_icons or not RATING_ICONS:
            return
        ratings_padding_width = self.PADDING_BETWEEN_RATINGS * max(0, len(RATING_ICONS) - 1)
        ratings_width = sum([ icon.width for icon in RATING_ICONS.values() ]) + ratings_padding_width
        ratings_height = max([ icon.height for icon in RATING_ICONS.values() ])
        scale = float(self.content.width) / ratings_width if ratings_width > self.content.width else 1.0
        ratings_container = Container(name='AddictionWarning_RatingsContainer', parent=self.content, align=uiconst.TOTOP, height=ratings_height * scale, padding=(0,
         self.PADDING_RATINGS_TOP,
         0,
         self.PADDING_RATINGS_BOTTOM))
        ratings_centered = Container(name='AddictionWarning_RatingsContainerCentered', parent=ratings_container, align=uiconst.CENTER, width=ratings_width * scale, height=ratings_height * scale)
        left_padding = 0
        for icon_key in sorted(RATING_ICONS.keys()):
            icon = RATING_ICONS[icon_key]
            Sprite(name='AddictionWarning_RatingIcon%s' % icon.name, parent=ratings_centered, align=uiconst.CENTERLEFT, width=icon.width * scale, height=icon.height * scale, texturePath=get_icon_path(icon.name), left=left_padding, state=uiconst.UI_DISABLED)
            left_padding += (icon.width + self.PADDING_BETWEEN_RATINGS) * scale

    def add_text(self):
        if not self.should_add_text:
            return
        text_container = ContainerAutoSize(name='AddictionWarning_TextContainer', parent=self.content, align=uiconst.TOTOP, width=self.width)
        padding_h = self.PADDING_TEXT_H
        padding_top = self.PADDING_TEXT_TOP
        padding_bottom = self.PADDING_TEXT_BOTTOM
        padding_between_lines = self.PADDING_TEXT_BETWEEN_LINES
        disclaimer_container = ContainerAutoSize(name='AddictionWarning_DisclaimerContainer', parent=text_container, align=uiconst.TOTOP, width=text_container.width - 2 * padding_h, padding=(padding_h,
         padding_top,
         padding_h,
         padding_between_lines))
        EveLabelSmall(name='AddictionWarning_DisclaimerLabel', parent=disclaimer_container, align=uiconst.CENTER, text=get_addiction_warning_text())
        playtime_container = ContainerAutoSize(name='AddictionWarning_PlaytimeContainer', parent=text_container, align=uiconst.TOTOP, width=text_container.width - 2 * padding_h, padding=(padding_h,
         0,
         padding_h,
         padding_bottom))
        EveLabelMediumBold(name='AddictionWarning_PlaytimeLabel', parent=playtime_container, align=uiconst.CENTER, text=get_playtime_text())

    def get_total_height(self):
        _, content_height = self.content.GetAutoSize()
        return content_height + 2 * self.POPUP_PADDING_V


class FramedAddictionWarningContainer(AddictionWarningContainer):
    default_should_add_frame = True


class AddictionWarningExpander(ContainerAutoSize):
    EXPANDER_ICON_PATH = 'res:/UI/Texture/Icons/105_32_13.png'
    EXPANDER_ICON_WIDTH = 7
    EXPANDER_ICON_HEIGHT = 7

    def ApplyAttributes(self, attributes):
        super(AddictionWarningExpander, self).ApplyAttributes(attributes)
        scale = float(self.height) / self.EXPANDER_ICON_HEIGHT
        expander_width = self.EXPANDER_ICON_WIDTH * scale
        expander_height = self.EXPANDER_ICON_HEIGHT * scale
        Sprite(parent=self, name='AddictionWarningExpander_Sprite', texturePath=self.EXPANDER_ICON_PATH, align=uiconst.TOPRIGHT, width=expander_width, height=expander_height, rotation=pi / 2, state=uiconst.UI_DISABLED)
