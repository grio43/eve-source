#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation\empireTechnologyViews\shipsView.py
import blue
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from charactercreator.client.scalingUtils import GetScaleFactor, SMALL_PANEL_WIDTH, SMALL_PANEL_HEIGHT, GetMainPanelWidth, GetMainPanelHeight, GetTopNavHeight, PANEL_HEADER_HEIGHT, GetBannerHeaderHeight
from eve.client.script.ui.login.charcreation.empireTechnologyViews.shipsViewData import ShipData
from eve.client.script.ui.login.charcreation.empireTechnologyViews.technologyView import TechnologyViewWithCentralPic
from eve.client.script.ui.login.charcreation.empireui.empireThemedTooltip import EmpireThemedTooltip, get_tooltip_width
from eve.common.lib.appConst import raceAmarr, raceCaldari, raceGallente, raceMinmatar
COLOR_CODE_MAP_BY_RACE = {raceAmarr: 'res:/UI/Texture/classes/EmpireSelection/Ships/fleetAmarr_colormap.png',
 raceCaldari: 'res:/UI/Texture/classes/EmpireSelection/Ships/fleetCaldari_colormap.png',
 raceGallente: 'res:/UI/Texture/classes/EmpireSelection/Ships/fleetGallente_colormap.png',
 raceMinmatar: 'res:/UI/Texture/classes/EmpireSelection/Ships/fleetMinmatar_colormap.png'}
NO_COLOR = (0.0, 0.0, 0.0, 0.0)
COLOR_MAP_WIDTH = 1280
COLOR_MAP_HEIGHT = 800
HOVER_FREQUENCY = 250
X_SCALE_FACTOR_COLOR_MAP = float(COLOR_MAP_WIDTH) / float(SMALL_PANEL_WIDTH)
Y_SCALE_FACTOR_COLOR_MAP = float(COLOR_MAP_HEIGHT) / float(SMALL_PANEL_HEIGHT - PANEL_HEADER_HEIGHT)
TOOLTIP_MARGIN = 5
MOUSE_OVER_SHIP_SOUND = 'ui_es_ship_mouse_over_play'
MOUSE_EXIT_SHIP_SOUND = 'ui_es_ship_mouse_over_stop'
CENTRAL_VIEW_FADE_IN_DURATION = 2.0

class ShipsView(TechnologyViewWithCentralPic):
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        self.is_ready = False
        TechnologyViewWithCentralPic.ApplyAttributes(self, attributes)
        self.tooltips = {}
        self.hovered_ship_order_current = None
        self.hover_x_new = None
        self.hover_y_new = None
        self.hover_thread = None
        self.audio_svc = sm.GetService('audio')
        self.ship_data = ShipData(self.technology, self.raceID).get_ship_data()
        self.calculate_static_offsets()
        self.calculate_proportions()
        self.build_tooltips()
        self.color_code_map = blue.resMan.GetResource(COLOR_CODE_MAP_BY_RACE[self.raceID], 'raw')
        self.build_ship_by_color_code()
        TechnologyViewWithCentralPic.ShowMainView(self)
        self.is_ready = True

    def Close(self):
        self.hover_thread = None
        TechnologyViewWithCentralPic.Close(self)

    def clear_tooltips(self):
        for tooltip in self.tooltips.values():
            tooltip.close()

        self.tooltips = {}

    def build_tooltips(self):
        self.clear_tooltips()
        for ship_order, ship_info in self.ship_data.iteritems():
            panel_width = GetMainPanelWidth()
            margin = (uicore.desktop.width - panel_width) / 2
            tooltip_left = ship_info['tooltip_left'] * self.scale_factor
            tooltip_top = ship_info['tooltip_top'] * self.scale_factor
            tooltip_width = get_tooltip_width()
            if tooltip_left - TOOLTIP_MARGIN < -margin:
                tooltip_left = -margin + TOOLTIP_MARGIN
            elif tooltip_left + TOOLTIP_MARGIN + tooltip_width > panel_width + margin:
                tooltip_left = panel_width + margin - tooltip_width - TOOLTIP_MARGIN
            self.tooltips[ship_order] = EmpireThemedTooltip(name='Ship%d_%s' % (ship_order, ship_info['title']), parent=self, raceID=self.raceID, icon=ship_info['icon'], title=ship_info['title'], text=ship_info['subtitle'], left=tooltip_left, top=tooltip_top)

    def build_ship_by_color_code(self):
        self.ship_by_color_code = {}
        for ship_order, ship_info in self.ship_data.iteritems():
            color_code = ship_info['color_code']
            self.ship_by_color_code[color_code] = ship_order

    def calculate_static_offsets(self):
        self.x_scale_factor_map = float(COLOR_MAP_WIDTH) / float(SMALL_PANEL_WIDTH)
        self.y_scale_factor_map = float(COLOR_MAP_HEIGHT) / float(SMALL_PANEL_HEIGHT - PANEL_HEADER_HEIGHT)

    def calculate_proportions(self):
        self.x_offset = self.displayX + int(round((uicore.desktop.width - GetMainPanelWidth()) / 2))
        self.y_offset = self.displayY + int(round(GetTopNavHeight()))
        self.scale_factor = GetScaleFactor()
        viewWidthMinRes = SMALL_PANEL_WIDTH
        viewWidth = GetMainPanelWidth()
        viewHeightMinRes = SMALL_PANEL_HEIGHT - PANEL_HEADER_HEIGHT
        viewHeight = GetMainPanelHeight() - GetBannerHeaderHeight()
        self.scale_x = float(viewWidthMinRes) / float(viewWidth)
        self.scale_y = float(viewHeightMinRes) / float(viewHeight)

    def find_ship_from_color_map(self, x, y):
        if self.hover_x_new is None or self.hover_y_new is None:
            return
        x_in_view = x - self.x_offset
        y_in_view = y - self.y_offset
        min_res_x_in_view = int(round(x_in_view * self.scale_x))
        min_res_y_in_view = int(round(y_in_view * self.scale_y))
        map_x = int(round(min_res_x_in_view * self.x_scale_factor_map))
        map_y = int(round(min_res_y_in_view * self.y_scale_factor_map))
        color_code = self.color_code_map.GetPixelColor(map_x, map_y)
        ship_order = self.ship_by_color_code.get(color_code, None)
        return ship_order

    def OnMouseMove(self, *args):
        if not self.is_ready:
            return
        self.hover_x_new = uicore.uilib.x
        self.hover_y_new = uicore.uilib.y
        self.show_ship_hover()

    def OnMouseExit(self, *args):
        if not self.is_ready:
            return
        self.hover_x_new = None
        self.hover_y_new = None
        self.show_ship_hover()

    def show_ship_hover(self):
        if not self.hover_thread:
            self.hover_thread = AutoTimer(HOVER_FREQUENCY, self.show_ship_hover_timed)

    def show_ship_hover_timed(self):
        try:
            if self.destroyed:
                return
            hovered_ship_order = self.find_ship_from_color_map(x=self.hover_x_new, y=self.hover_y_new)
            if self.hovered_ship_order_current == hovered_ship_order:
                return
            if self.hovered_ship_order_current is not None:
                self.tooltips[self.hovered_ship_order_current].set_visibility(False)
                self.audio_svc.SendUIEvent(MOUSE_EXIT_SHIP_SOUND)
            self.hovered_ship_order_current = hovered_ship_order
            if self.hovered_ship_order_current is None:
                return
            self.tooltips[self.hovered_ship_order_current].set_visibility(True)
            self.audio_svc.SendUIEvent(MOUSE_OVER_SHIP_SOUND)
        finally:
            self.hover_thread = None

    def _OnResize(self, *args):
        self.is_ready = False
        self.calculate_proportions()
        self.build_tooltips()
        self.is_ready = True
