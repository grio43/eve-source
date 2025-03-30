#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\agentinteraction\npccharacterview.py
import blue
import eveformat
import eveformat.client
from agentinteraction.constUI import PADDING_SMALL, HEADER_SIZE_XLARGE
from carbonui import TextColor, uiconst
from carbonui.fontconst import STYLE_SMALLTEXT
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite, StreamingVideoSprite
from carbonui.util.color import Color
from carbonui.util.dpi import reverse_scale_dpi
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import Label, EveLabelMedium
from eve.common.lib.appConst import agentDivisionHeraldry
import evegraphics.settings as gfxsettings
from evelink.client.handlers.show_info.link import location_link
from localization import GetByLabel, GetByMessageID
from npcs.divisions import get_division_name
from uthread2 import StartTasklet
import evelink.client
import trinity
PORTRAIT_WIDTH = 800
PORTRAIT_HEIGHT = 1080
PORTRAIT_WIDTH_EXTRA = 2.0
PORTRAIT_PROPS = float(PORTRAIT_WIDTH) / PORTRAIT_HEIGHT
BACKGROUND_WIDTH = 800
BACKGROUND_HEIGHT = 1400
BACKGROUND_PROPS = float(BACKGROUND_WIDTH) / BACKGROUND_HEIGHT
BACKGROUND_BY_DIVISION = {agentDivisionHeraldry: 'res:/UI/Texture/classes/Agents/heraldry.png'}
BACKGROUND_FALLBACK = None

class NpcCharacterView(Container):
    default_name = 'NpcCharacterView'
    show_background_for_character = True
    PORTRAITS_FOLDER_2D = None
    PORTRAIT_FALLBACK_2D = 'res:/UI/Texture/classes/Agents/3019471.png'
    PORTRAITS_FOLDER_VIDEO = None
    PORTRAIT_FALLBACK_VIDEO = None
    H_PADDING_CONTENT = PADDING_SMALL
    V_PADDING_BETWEEN_AGENT_INFO_AND_STANDINGS = 64
    V_PADDING_TEXT_TO_BOTTOM = 12
    V_PADDING_LINES_LEVEL_TO_NAME = 11
    V_PADDING_LINES_NAME_TO_LOCATION = 2
    H_PADDING_LINE_LEVEL_BITS = 6
    HEIGHT_LINE_LEVEL = 16
    HEIGHT_LINE_NAME = 58
    HEIGHT_LINE_LOCATION = 17

    def __init__(self, npc_character, inner_padding = (0, 0, 0, 0), **kwargs):
        self._inner_padding = inner_padding
        self.background_sprite = None
        self.container_npc_character_text = None
        self.gradient_text = None
        self.inner_cont = None
        self.npc_character = npc_character
        self.portrait = None
        super(NpcCharacterView, self).__init__(**kwargs)
        self.inner_cont = Container(name='inner_cont', parent=self, align=uiconst.TOALL, padding=self._inner_padding)
        StartTasklet(self._build_content)

    @property
    def inner_padding(self):
        return self._inner_padding

    @inner_padding.setter
    def inner_padding(self, value):
        if isinstance(value, (int, float)):
            value = (value,
             value,
             value,
             value)
        if self._inner_padding != value:
            self._inner_padding = value
            if self.inner_cont:
                self.inner_cont.padding = self._inner_padding

    def _build_content(self):
        self._build_npc_character_text()
        self._build_gradient()
        self._build_portrait()
        self._build_background()
        self._update_sizes()
        self._load_npc_character_location()

    def _build_npc_character_text(self):
        self.container_npc_character_text = ContainerAutoSize(name='container_npc_character_text', parent=self.inner_cont, align=uiconst.TOBOTTOM_NOPUSH, padRight=self.H_PADDING_CONTENT, padLeft=self.H_PADDING_CONTENT)
        self._build_npc_character_level()
        self._build_npc_character_name()
        self._build_npc_character_location()

    def _build_npc_character_level(self):
        level = self.npc_character.get_level()
        division_id = self.npc_character.get_division_id()
        division_name = get_division_name(division_id)
        container_level_line = Container(name='container_level_line', parent=self.container_npc_character_text, align=uiconst.TOTOP, height=self.HEIGHT_LINE_LEVEL)
        container_level = ContainerAutoSize(name='container_level', parent=container_level_line, align=uiconst.TOLEFT)
        EveLabelMedium(name='label_level', parent=container_level, align=uiconst.CENTERLEFT, text=GetByLabel('UI/Agents/AgentLevel').upper(), color=Color.WHITE)
        container_level_number = ContainerAutoSize(name='container_level_number', parent=container_level_line, align=uiconst.TOLEFT, padLeft=self.H_PADDING_LINE_LEVEL_BITS, bgColor=Color.WHITE)
        EveLabelMedium(name='number_level', parent=container_level_number, align=uiconst.CENTER, text=int(level), padLeft=self.H_PADDING_LINE_LEVEL_BITS, padRight=self.H_PADDING_LINE_LEVEL_BITS, color=Color.BLACK)
        container_division = ContainerAutoSize(name='container_division', parent=container_level_line, align=uiconst.TOLEFT, padLeft=self.H_PADDING_LINE_LEVEL_BITS)
        EveLabelMedium(name='division', parent=container_division, align=uiconst.CENTERLEFT, text=division_name, color=Color.WHITE)

    def _build_npc_character_name(self):
        name = GetByMessageID(self.npc_character.get_name())
        name_link = evelink.character_link(self.npc_character.get_id(), name)
        container_name_line = ContainerAutoSize(name='container_name_line', parent=self.container_npc_character_text, align=uiconst.TOTOP, height=self.HEIGHT_LINE_NAME, padTop=self.V_PADDING_LINES_LEVEL_TO_NAME)
        Label(name='label_name', parent=container_name_line, align=uiconst.TOTOP, text=name_link, fontsize=HEADER_SIZE_XLARGE, fontStyle=STYLE_SMALLTEXT, color=TextColor.HIGHLIGHT, bold=True, letterspace=1, state=uiconst.UI_NORMAL)

    def _build_npc_character_location(self):
        self.npc_character_location_label = EveLabelMedium(name='label_location', parent=self.container_npc_character_text, align=uiconst.TOTOP, state=uiconst.UI_ACTIVE, padTop=self.V_PADDING_LINES_NAME_TO_LOCATION)

    def _load_npc_character_location(self):
        text = self._get_location_text()
        self.npc_character_location_label.text = text

    def _build_gradient(self):
        self.gradient_text = Sprite(name='gradient_text', parent=self, align=uiconst.TOBOTTOM_NOPUSH, texturePath='res:/UI/Texture/classes/AgentInteraction/Gradient_CareerAgent.png', state=uiconst.UI_DISABLED, height=600, color=eveColor.BLACK)

    def _build_portrait(self):
        portait_cont = Container(name='portrait_cont', parent=self, clipChildren=True)
        if self._should_show_video():
            portrait_video_path = self._get_video_portrait_path()
            if portrait_video_path:
                self.portrait = StreamingVideoSprite(parent=portait_cont, name='sprite_video_portrait', videoPath=portrait_video_path, videoLoop=True, disableAudio=True, blendMode=trinity.TR2_SBM_NONE, spriteEffect=trinity.TR2_SFX_COPY, align=uiconst.CENTERBOTTOM, state=uiconst.UI_DISABLED)
                self.portrait.Play()
                return
        portrait_2d_path = self._get_2d_portrait_path()
        self.portrait = Sprite(name='sprite_2d_portrait', parent=portait_cont, align=uiconst.CENTERBOTTOM, texturePath=portrait_2d_path, state=uiconst.UI_DISABLED)

    def _build_background(self):
        if not self.show_background_for_character:
            return
        background_path = self._get_background_path()
        if not background_path:
            return
        background_container = Container(name='background_container', parent=self, state=uiconst.UI_DISABLED, align=uiconst.TOALL, clipChildren=True)
        self.background_sprite = Sprite(name='background_npc_character', parent=background_container, align=uiconst.TOLEFT, texturePath=background_path)

    def _get_background_path(self):
        division_id = self.npc_character.get_division_id()
        texture_path = BACKGROUND_BY_DIVISION.get(division_id, BACKGROUND_FALLBACK)
        return texture_path

    def _get_2d_portrait_path(self):
        if self.PORTRAITS_FOLDER_2D:
            npc_character_id = self.npc_character.get_id()
            path = '{path}/{character_id}.png'.format(path=self.PORTRAITS_FOLDER_2D, character_id=npc_character_id)
            if blue.paths.FileExistsLocally(path):
                return path
        return self.PORTRAIT_FALLBACK_2D

    def _get_video_portrait_path(self):
        if self.PORTRAITS_FOLDER_VIDEO:
            npc_character_id = self.npc_character.get_id()
            path = '{path}/{character_id}.webm'.format(path=self.PORTRAITS_FOLDER_VIDEO, character_id=npc_character_id)
            if blue.paths.FileExistsLocally(path):
                return path
        return self.PORTRAIT_FALLBACK_VIDEO

    def _should_show_video(self):
        return gfxsettings.Get(gfxsettings.GFX_SHADER_QUALITY) >= gfxsettings.SHADER_MODEL_MEDIUM

    def _get_location_text(self):
        station_id = self.npc_character.get_station_id()
        solar_system_id = sm.GetService('ui').GetStationSolarSystem(station_id)
        return u'{security} {location}'.format(security=eveformat.client.solar_system_security_status(solar_system_id), location=location_link(station_id))

    def _update_sizes(self):
        available_width = reverse_scale_dpi(self.displayWidth)
        available_height = reverse_scale_dpi(self.displayHeight)
        if not available_width or not available_height:
            return
        self._update_portrait_size(available_width, available_height)
        self._update_portrait_background_size(available_width, available_height)

    def _update_portrait_size(self, available_width, available_height):
        needed_width = PORTRAIT_PROPS * available_height
        needed_vs_actual = float(needed_width) / available_width
        if needed_vs_actual > PORTRAIT_WIDTH_EXTRA:
            width = available_width * PORTRAIT_WIDTH_EXTRA
        else:
            width = needed_width
        height = width / PORTRAIT_PROPS
        if self.portrait and not self.portrait.destroyed:
            self.portrait.SetSize(width, height)
        if self.gradient_text and not self.gradient_text.destroyed:
            self.gradient_text.height = height * 0.7

    def _update_portrait_background_size(self, available_width, available_height):
        width = BACKGROUND_PROPS * available_height
        height = width / BACKGROUND_PROPS
        if self.background_sprite and not self.background_sprite.destroyed:
            if available_width > width:
                self.background_sprite.align = uiconst.CENTER
                self.background_sprite.width = available_width
                self.background_sprite.height = float(available_width * height) / width
            else:
                self.background_sprite.align = uiconst.TOLEFT
                self.background_sprite.left = -(width - available_width) / 2
                self.background_sprite.width = width

    def _OnResize(self, *args):
        self._update_sizes()
