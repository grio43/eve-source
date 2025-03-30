#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\ui\instructions.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.eveLabel import Label
from localization import GetByLabel
from math import pi
from projectdiscovery.client.projects.covid.ui.containerwithcorners import ContainerWithCorners
WIDTH = 322
BACKGROUND_COLOR = (0.2, 0.74, 0.95, 0.2)
PADDING_H_TITLE = 22
PADDING_H_TEXT = 24
PADDING_H_BULLET_POINTS = 22
PADDING_TOP_IF_TITLE = 20
PADDING_TOP_IF_NO_TITLE = 23
PADDING_BOT_IF_BULLET_POINTS = 23
PADDING_BOT_IF_NO_BULLET_POINTS = 23
PADDING_V_BETWEEN_CONTAINERS = 21
PADDING_V_BETWEEN_BULLET_POINTS = 13
BULLET_POINT_CONTAINER_SIZE = 24
BULLET_POINT_SIZE = 6
BULLET_POINT_LEFT = 1
BULLET_POINT_TOP = 6
BULLET_POINT_COLOR = (1.0, 1.0, 1.0, 1.0)
BULLET_POINT_GLOW_SIZE = 34
BULLET_POINT_GLOW_OPACITY = 0.5
BULLET_POINT_GLOW_TEXTURE = 'res:/UI/Texture/classes/ProjectDiscovery/covid/slot_glow.png'
FONTSIZE_TITLE = 24
FONTSIZE_TEXT = 14
FONTSIZE_BULLET_POINT_TEXT = 14
TEXT_COLOR = (1.0, 1.0, 1.0, 1.0)

class Instructions(Container):
    default_width = WIDTH

    def ApplyAttributes(self, attributes):
        super(Instructions, self).ApplyAttributes(attributes)
        self.title = attributes.get('title', None)
        self.text = attributes.get('text', None)
        self.bullet_points_text_list = attributes.get('bullet_points_text_list', [])
        pad_top = PADDING_TOP_IF_TITLE if self.title else PADDING_TOP_IF_NO_TITLE
        pad_bottom = PADDING_BOT_IF_BULLET_POINTS if self.bullet_points_text_list else PADDING_BOT_IF_NO_BULLET_POINTS
        box = ContainerAutoSize(name='box', parent=self, align=uiconst.TOTOP, bgColor=BACKGROUND_COLOR)
        self.content = ContainerAutoSize(name='content', parent=box, align=uiconst.TOTOP, padTop=pad_top, padBottom=pad_bottom)
        self.total_height = pad_top + pad_bottom
        self._add_title()
        self._add_text()
        self._add_bullet_points()
        self._add_corners()

    def _add_title(self):
        if self.title:
            title_label = Label(name='title', parent=self.content, align=uiconst.TOTOP, padLeft=PADDING_H_TITLE, padRight=PADDING_H_TITLE, fontsize=FONTSIZE_TITLE, maxWidth=WIDTH - 2 * PADDING_H_TITLE, text=GetByLabel(self.title), color=TEXT_COLOR)
            self.total_height += title_label.height

    def _add_text(self):
        if self.text:
            text_label = Label(name='text', parent=self.content, align=uiconst.TOTOP, padLeft=PADDING_H_TEXT, padRight=PADDING_H_TEXT, padTop=PADDING_V_BETWEEN_CONTAINERS if self.title else 0, fontsize=FONTSIZE_TEXT, maxWidth=WIDTH - 2 * PADDING_H_TEXT, text=self.text, color=TEXT_COLOR)
            self.total_height += text_label.height + text_label.padTop

    def _add_bullet_points(self):
        if self.bullet_points_text_list:
            bullet_points_container = ContainerAutoSize(name='bullet_points_container', parent=self.content, align=uiconst.TOTOP, padLeft=PADDING_H_BULLET_POINTS, padRight=PADDING_H_BULLET_POINTS, padTop=PADDING_V_BETWEEN_CONTAINERS if self.title or self.text else 0)
            for index, item_text in enumerate(self.bullet_points_text_list):
                item_container = ContainerAutoSize(name='item_container', parent=bullet_points_container, align=uiconst.TOTOP, padTop=PADDING_V_BETWEEN_BULLET_POINTS if index > 0 else 0)
                bullet_point_container = Container(name='item_bullet_point', parent=item_container, align=uiconst.TOPLEFT, width=BULLET_POINT_SIZE, height=BULLET_POINT_SIZE, left=BULLET_POINT_LEFT, top=BULLET_POINT_TOP)
                Fill(name='square', parent=bullet_point_container, align=uiconst.TOALL, color=BULLET_POINT_COLOR)
                Sprite(name='glow', parent=bullet_point_container, align=uiconst.CENTER, width=BULLET_POINT_GLOW_SIZE, height=BULLET_POINT_GLOW_SIZE, texturePath=BULLET_POINT_GLOW_TEXTURE, opacity=BULLET_POINT_GLOW_OPACITY)
                Label(name='item_text', parent=item_container, align=uiconst.TOPLEFT, padLeft=BULLET_POINT_CONTAINER_SIZE, fontsize=FONTSIZE_BULLET_POINT_TEXT, maxWidth=WIDTH - 2 * PADDING_H_BULLET_POINTS - BULLET_POINT_CONTAINER_SIZE, text=GetByLabel(item_text), color=TEXT_COLOR)
                item_container.UpdateAlignment()

            bullet_points_container.UpdateAlignment()
            self.total_height += bullet_points_container.height + bullet_points_container.padTop

    def _add_corners(self):
        ContainerWithCorners(name='corners', parent=self, align=uiconst.TOPLEFT, width=self.width, height=self.total_height)

    def get_content_height(self):
        return self.total_height
