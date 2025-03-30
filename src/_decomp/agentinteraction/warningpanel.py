#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\agentinteraction\warningpanel.py
from agentinteraction.textutils import get_menu_for_item
from carbonui.control.scrollContainer import ScrollContainer
from agentinteraction.constUI import HEADER_SIZE_MEDIUM, PADDING_XSMALL, PADDING_SMALL
from agentinteraction.reward import RewardType, Reward, typeCredits
import carbonui
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.util.color import Color
from eve.client.script.ui import eveColor
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.infoIcon import InfoGlyphIcon
from eve.common.script.util.eveFormat import FmtISK
from evelink.client import blueprint_link, type_link
from localization import GetByLabel
import trinity
ICON_SIZE = 64

class WarningPanel(ContainerAutoSize):
    USE_TEST_REWARDS = False
    default_padTop = PADDING_SMALL
    default_alignMode = uiconst.TOTOP
    CONTENT_BACKGROUND_COLOR = None
    CONTENT_COLOR = None
    TITLE_PATH = None
    HAS_UPPERCASE_TITLE = False
    TITLE_COLOR = None
    TEXT_PATH = None
    TEXT_COLOR = Color.GRAY6
    TEXTS_PADDING_H = 10
    TEXTS_PADDING_TOP_BOTTOM = 10
    TEXTS_PADDING_BOTTOM = 17
    LINE_WIDTH = 6
    CONTENT_LEFT_PAD = 5
    SUBTEXT_FONTSIZE = 14
    SUBTEXT_COLOR = None
    PADDING_TEXT_TO_SUBTEXT = 2

    def ApplyAttributes(self, attributes):
        self.line_container = None
        self.title = None
        self.title_cont = None
        self.text = None
        super(WarningPanel, self).ApplyAttributes(attributes)
        self._build_content()

    def _build_content(self):
        self._add_content()

    def _add_content(self):
        self.content_container = ContainerAutoSize(name='content_container', parent=self, align=uiconst.TOTOP, height=self.height, alignMode=uiconst.TOTOP)
        self._add_icon()
        Frame(name='warning_panel_background', bgParent=self.content_container, texturePath='res:/UI/Texture/Shared/bg_cutoff.png', textureSecondaryPath='res:/UI/Texture/Shared/DarkStyle/solid.png', spriteEffect=trinity.TR2_SFX_MODULATE, color=self.CONTENT_BACKGROUND_COLOR, cornerSize=6)
        self._add_texts()

    def _add_icon(self):
        self.icon_container = Container(name='icon_container', parent=self.content_container, align=uiconst.TOLEFT, width=ICON_SIZE, state=uiconst.UI_NORMAL, padLeft=PADDING_XSMALL)
        self.icon_container.Hide()
        self.icon = Icon(name='icon', parent=self.icon_container, align=uiconst.CENTER, width=ICON_SIZE, height=ICON_SIZE, state=uiconst.UI_DISABLED)

    def _add_texts(self):
        self.texts_container = ContainerAutoSize(name='texts_container', parent=self.content_container, align=uiconst.TOTOP, padding=(self.TEXTS_PADDING_H,
         self.TEXTS_PADDING_TOP_BOTTOM,
         self.TEXTS_PADDING_H,
         self.TEXTS_PADDING_TOP_BOTTOM), alignMode=uiconst.TOTOP)
        self._add_title()
        self._add_text()

    def _add_title(self):
        if self.TITLE_PATH:
            title = GetByLabel(self.TITLE_PATH)
            if self.HAS_UPPERCASE_TITLE:
                title = title.upper()
            self.title_cont = ContainerAutoSize(parent=self.texts_container, align=uiconst.TOTOP, alignMode=uiconst.TOTOP)
            self.title = carbonui.TextHeader(name='title', parent=self.title_cont, align=uiconst.TOTOP, text=title, color=self.TITLE_COLOR)

    def _add_text(self):
        if self.TEXT_PATH:
            self.text = carbonui.TextBody(name='text', parent=self.texts_container, align=uiconst.TOTOP, color=self.TEXT_COLOR)
            self._update_text()

    def _add_subtext(self):
        self.subtext = Label(name='subtext', parent=self.texts_container, align=uiconst.TOTOP, fontsize=self.SUBTEXT_FONTSIZE, color=self.SUBTEXT_COLOR, padTop=self.PADDING_TEXT_TO_SUBTEXT)

    def _update_text(self):
        if self.TEXT_PATH:
            text = self._get_text()
            self.text.SetText(text)

    def _get_text(self):
        return GetByLabel(self.TEXT_PATH)

    def update_items(self, items):
        if self.USE_TEST_REWARDS:
            items = [Reward(RewardType.NORMAL, typeCredits, quantity=1000)]
        self.icon_container.Hide()
        for item in items:
            self._load_item(item)
            self.icon_container.Show()
            return

    def _load_item(self, item):
        hint = item.get_hint()
        self.icon_container.SetHint(hint)
        type_id = item.type_id
        is_blueprint_copy = item.is_blueprint_copy()
        self.icon.LoadIconByTypeID(type_id, ignoreSize=True, isCopy=is_blueprint_copy)
        if item.is_normal_type():
            self.icon_container.GetMenu = lambda *args: self._get_menu_for_item(item)

    def _get_menu_for_item(self, item):
        return get_menu_for_item(item)


class ShipRequirementsPanel(WarningPanel):
    CONTENT_BACKGROUND_COLOR = eveColor.CHERRY_RED[:3] + (0.4,)
    CONTENT_COLOR = eveColor.DANGER_RED
    TITLE_COLOR = eveColor.DANGER_RED
    TEXT_COLOR = Color.WHITE
    TITLE_PATH = 'UI/Generic/Warning'
    TEXT_PATH = 'UI/Agents/StandardMission/ShipRequirementsText'
    HAS_UPPERCASE_TITLE = True

    def __init__(self, dungeon_id = None, in_valid_ship = False, ship_window_header = '', *args, **kwargs):
        self.in_valid_ship = in_valid_ship
        self.dungeon_id = dungeon_id
        self.ship_window_header = ship_window_header
        super(ShipRequirementsPanel, self).__init__(*args, **kwargs)

    def _build_content(self):
        container = ContainerAutoSize(parent=self, align=carbonui.Align.TOTOP, alignMode=carbonui.Align.TOLEFT, height=20, padBottom=8)
        carbonui.TextBody(parent=container, align=carbonui.Align.TOLEFT, text=GetByLabel('UI/Dungeons/ShipRestrictionsLabel'), padRight=8)
        InfoGlyphIcon(parent=container, align=carbonui.Align.TOLEFT, width=16, height=16, func=self._open_ship_restrictions)
        self._add_line()
        self._add_content()
        if self.in_valid_ship:
            self.title_cont.Hide()
            self.content_container.Hide()

    def _open_ship_restrictions(self, *args, **kwargs):
        from evedungeons.client.ship_restrictions_window import ShipRestrictionsWindow
        ShipRestrictionsWindow.Open(dungeon_id=self.dungeon_id, header_text=self.ship_window_header)

    def _add_line(self):
        self.line_container = Container(name='line_container', parent=self, align=uiconst.TOLEFT, width=self.LINE_WIDTH, clipChildren=True, padRight=5)
        Sprite(name='line', parent=self.line_container, align=uiconst.TOALL, texturePath='res:/UI/Texture/Classes/AgentInteraction/HazardLine_6px.png', color=self.CONTENT_COLOR, tileY=True, state=uiconst.UI_DISABLED)

    def set_restrictions_info(self, dungeon_id, in_valid_ship, ship_window_header = ''):
        self.in_valid_ship = in_valid_ship
        self.dungeon_id = dungeon_id
        self.ship_window_header = ship_window_header
        if self.in_valid_ship:
            self.title_cont.Hide()
            self.content_container.Hide()
        else:
            self.title_cont.Show()
            self.content_container.Show()

    def _get_text(self):
        return GetByLabel(self.TEXT_PATH, startLink='', endLink='')


class GrantedItemsPanel(WarningPanel):
    CONTENT_BACKGROUND_COLOR = eveColor.COPPER_OXIDE_GREEN[:3] + (0.4,)
    CONTENT_COLOR = eveColor.SUCCESS_GREEN
    TITLE_COLOR = Color.WHITE
    SUBTEXT_COLOR = CONTENT_COLOR
    TITLE_PATH = 'UI/Agents/StandardMission/GrantedItems'
    TEXT_PATH = 'UI/Agents/StandardMission/GrantedItemText'
    TEXTS_PADDING_TOP_BOTTOM = 14

    def _add_texts(self):
        super(GrantedItemsPanel, self)._add_texts()
        self._add_subtext()

    def update_items(self, items):
        super(GrantedItemsPanel, self).update_items(items)
        if self.USE_TEST_REWARDS:
            items += [Reward(RewardType.NORMAL, typeCredits, quantity=1000)]
            items += [Reward(RewardType.NORMAL, 1230, quantity=1000)]
        textList = []
        for item in items:
            details = item.get_text_details()
            if item.is_blueprint_copy():
                text = blueprint_link(item.type_id, runs=item.get_runs_remaining(), isCopy=item.is_blueprint_copy(), te=item.get_productivity_level(), me=item.get_material_level())
            elif item.is_normal_type():
                text = type_link(item.type_id, link_text=details)
            else:
                text = details
            textList.append(text)

        if textList:
            text = ', '.join(textList)
            self.subtext.SetText(text=text)
            self.subtext.state = uiconst.UI_NORMAL


class CollateralPanel(WarningPanel):
    CONTENT_BACKGROUND_COLOR = eveColor.DUSKY_ORANGE[:3] + (0.4,)
    CONTENT_COLOR = eveColor.WARNING_ORANGE
    TITLE_PATH = 'UI/Agents/StandardMission/CollateralTitle'
    TEXT_PATH = 'UI/Agents/StandardMission/CollateralText'
    TITLE_COLOR = Color.WHITE
    SUBTEXT_COLOR = CONTENT_COLOR

    def ApplyAttributes(self, attributes):
        self.subtext = None
        super(CollateralPanel, self).ApplyAttributes(attributes)

    def _add_texts(self):
        super(CollateralPanel, self)._add_texts()
        self._add_subtext()

    def _load_item(self, item):
        super(CollateralPanel, self)._load_item(item)
        self.subtext.SetText(text=FmtISK(item.quantity))


class DisclaimerPanel(WarningPanel):
    CONTENT_BACKGROUND_COLOR = eveColor.SMOKE_BLUE[:3] + (0.4,)
    TEXT_COLOR = Color.WHITE
    TEXTS_PADDING_TOP_BOTTOM = 14

    def set_text(self, text):
        if self.text is None:
            self.text = eveLabel.EveLabelMedium(name='text', parent=self.texts_container, align=uiconst.TOTOP, color=self.TEXT_COLOR)
        self.text.SetText(text)
