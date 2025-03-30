#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\ui\cells.py
import carbonui.const as uiconst
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from random import choice
import trinity
PADDING_TOP = 0
LITTLE_SQUARE_SIZE = 22
LITTLE_SQUARE_PADDING = 2
LITTLE_SQUARE_CONTENT_SIZE = 16
LITTLE_SQUARE_EMPTY_COLOR = (0.2, 0.73, 0.95, 0.1)
LITTLE_SQUARE_FULL_COLOR = (0.96, 0.96, 0.96, 1.0)
LITTLE_SQUARE_FULL_GLOW_TEXTURE = 'res:/UI/Texture/classes/ProjectDiscovery/covid/slot_glow.png'
LITTLE_SQUARE_FULL_QUADRANT_SIZE = 4
LITTLE_SQUARE_FULL_QUADRANT_PADDING = 3
VERTICAL_PADDING = 11
BIG_SQUARE_SIZE = 130
BIG_SQUARE_PADDING = 16
BIG_SQUARES_PADDING_R = 10
EMPTY_CELL_CROSS_IMAGE_TEXTURE = 'res:/UI/Texture/classes/ProjectDiscovery/covid/slot_cross.png'
EMPTY_CELL_CROSS_SIZE = 26
EMPTY_CELL_DECORATION_SIZE = 7
CELL_IMAGE_TEXTURES_FOLDER = 'res:/UI/Texture/classes/ProjectDiscovery/covid/cells/'
NUMBER_OF_CELL_IMAGES = 131
VALIDATION_SIZE = 20
COLOR_EMPTY = (0.16, 0.18, 0.22, 1.0)
COLOR_NORMAL = (1.0, 1.0, 1.0, 1.0)
COLOR_SELECTED = (0.2, 0.74, 0.95, 1.0)
COLOR_INVALID = (0.97, 0.09, 0.13, 1.0)
FRAME_EMPTY = uiconst.FRAME_BORDER1_CORNER0
FRAME_FULL = uiconst.FRAME_BORDER1_CORNER0
VALID_ICON_WIDTH = 15
VALID_ICON_HEIGHT = 12
VALID_ICON_TEXTURE = 'res:/UI/Texture/classes/ProjectDiscovery/covid/valid.png'
INVALID_ICON_WIDTH = 12
INVALID_ICON_HEIGHT = 12
INVALID_ICON_TEXTURE = 'res:/UI/Texture/classes/ProjectDiscovery/covid/x.png'
LINE_COLOR = (1.0, 1.0, 1.0, 1.0)
LINE_HEIGHT = 5
SCROLL_WIDTH = 7
SCROLL_COLOR = (0.063, 0.69, 0.937, 0.2)
SCROLL_BOTTOM_PADDING = 10
SCROLL_SHADOW_WIDTH = 140
SCROLL_SHADOW_HEIGHT = 12
SCROLL_SHADOW_TEXTURE = 'res:/UI/Texture/classes/ProjectDiscovery/covid/scroll_shadow.png'
CELLS_CONTAINER_WIDTH = LITTLE_SQUARE_SIZE + VERTICAL_PADDING + BIG_SQUARE_SIZE + BIG_SQUARES_PADDING_R + SCROLL_WIDTH

class LittleSquare(Container):

    def ApplyAttributes(self, attributes):
        super(LittleSquare, self).ApplyAttributes(attributes)
        self._add_quadrants()
        self._add_base()
        self._add_glow()
        self.set_empty()

    def _add_quadrants(self):
        self.quadrants = Container(name='quadrants', parent=self, align=uiconst.CENTER, width=LITTLE_SQUARE_CONTENT_SIZE, height=LITTLE_SQUARE_CONTENT_SIZE)
        padding = LITTLE_SQUARE_FULL_QUADRANT_PADDING
        size = LITTLE_SQUARE_FULL_QUADRANT_SIZE
        for left in [padding, padding + size + padding]:
            for top in [padding, padding + size + padding]:
                Fill(name='quadrant_(%s, %s)' % (left, top), parent=self.quadrants, align=uiconst.TOPLEFT, width=size, height=size, color=LITTLE_SQUARE_FULL_COLOR, left=left, top=top)

    def _add_base(self):
        self.base = Fill(name='base', parent=self, align=uiconst.CENTER, width=LITTLE_SQUARE_CONTENT_SIZE, height=LITTLE_SQUARE_CONTENT_SIZE, color=LITTLE_SQUARE_EMPTY_COLOR, state=uiconst.UI_DISABLED)

    def _add_glow(self):
        self.glow = Sprite(name='glow', parent=self, align=uiconst.TOALL, texturePath=LITTLE_SQUARE_FULL_GLOW_TEXTURE)

    def set_full(self):
        self.quadrants.SetState(uiconst.UI_DISABLED)
        self.glow.SetState(uiconst.UI_DISABLED)

    def set_empty(self):
        self.quadrants.Hide()
        self.glow.Hide()


class Cell(Container):

    def ApplyAttributes(self, attributes):
        super(Cell, self).ApplyAttributes(attributes)
        self.on_cell_clicked = attributes.get('on_cell_clicked')
        self.is_selected = False
        self.is_valid = True
        self._add_valid()
        self._add_frame()
        self._add_cell_image()
        self._add_empty_image()
        self.set_empty()

    def _add_frame(self):
        self.frame = Frame(name='frame', parent=self, frameConst=FRAME_EMPTY, color=COLOR_EMPTY)

    def _add_valid(self):
        self.valid = Container(name='valid', parent=self, align=uiconst.BOTTOMRIGHT, width=VALIDATION_SIZE, height=VALIDATION_SIZE, bgColor=COLOR_NORMAL, bgBlendMode=trinity.TR2_SBM_NONE, state=uiconst.UI_DISABLED)
        self.valid_icon = Sprite(name='valid_icon', parent=self.valid, align=uiconst.CENTER, width=VALID_ICON_WIDTH, height=VALID_ICON_HEIGHT, texturePath=VALID_ICON_TEXTURE)
        self.invalid_icon = Sprite(name='invalid_icon', parent=self.valid, align=uiconst.CENTER, width=INVALID_ICON_WIDTH, height=INVALID_ICON_HEIGHT, texturePath=INVALID_ICON_TEXTURE, state=uiconst.UI_HIDDEN)

    def _add_cell_image(self):
        self.cell_image = Sprite(name='cell_image', parent=self, align=uiconst.TOALL, state=uiconst.UI_NORMAL)
        self.cell_image.OnClick = self.on_image_clicked

    def _add_empty_image(self):
        self.empty_state = Container(name='empty_state', parent=self, align=uiconst.TOALL, bgColor=(0.0, 0.0, 0.0, 1.0), state=uiconst.UI_DISABLED)
        Sprite(name='empty_image', parent=self.empty_state, align=uiconst.CENTER, width=EMPTY_CELL_CROSS_SIZE, height=EMPTY_CELL_CROSS_SIZE, texturePath=EMPTY_CELL_CROSS_IMAGE_TEXTURE)
        Fill(name='empty_image_decoration', parent=self.empty_state, align=uiconst.BOTTOMRIGHT, width=EMPTY_CELL_DECORATION_SIZE, height=EMPTY_CELL_DECORATION_SIZE, color=COLOR_EMPTY, left=1, top=1)

    def is_polygon_set(self, order):
        return self.order == order

    def _display_normal(self):
        self.frame.color = COLOR_NORMAL
        self.valid.background_color = COLOR_NORMAL
        self.valid_icon.Show()
        self.invalid_icon.Hide()

    def _display_selected(self):
        self.frame.color = COLOR_SELECTED
        self.valid.background_color = COLOR_SELECTED
        self.valid_icon.Show()
        self.invalid_icon.Hide()

    def _display_invalid(self):
        self.frame.color = COLOR_INVALID
        self.valid.background_color = COLOR_INVALID
        self.valid_icon.Hide()
        self.invalid_icon.Show()

    def set_state_normal(self):
        self.is_selected = False
        if self.is_valid:
            self._display_normal()
        else:
            self._display_invalid()

    def set_state_selected(self):
        self.is_selected = True
        if self.is_valid:
            self._display_selected()
        else:
            self._display_invalid()

    def set_state_valid(self):
        self.is_valid = True
        if self.is_selected:
            self.set_state_selected()
        else:
            self.set_state_normal()

    def set_state_invalid(self):
        self.is_valid = False
        if self.is_selected:
            self.set_state_selected()
        else:
            self.set_state_normal()

    def set_polygon(self, order, cell_image_id):
        self.order = order
        self.empty_state.Hide()
        self.cell_image.SetTexturePath(CELL_IMAGE_TEXTURES_FOLDER + '%s.png' % cell_image_id)
        self.cell_image.Show()
        self.valid.SetState(uiconst.UI_DISABLED)
        self.frame.LoadFrame(FRAME_FULL)
        self.set_state_normal()

    def set_empty(self):
        self.order = None
        self.empty_state.SetState(uiconst.UI_DISABLED)
        self.cell_image.Hide()
        self.valid.Hide()
        self.frame.LoadFrame(FRAME_EMPTY)

    def on_image_clicked(self, *args):
        if self.order is not None:
            self.on_cell_clicked(self.order)


class Cells(Container):

    def ApplyAttributes(self, attributes):
        super(Cells, self).ApplyAttributes(attributes)
        self.max_cells = attributes.get('max_cells')
        self.number_of_polygons = 0
        self.cell_image_by_order = {}
        self.is_listening_to_changes = True
        self.toggle_polygon_selection = None
        self.little_squares_container = None
        self.cell_scroll = None
        self._add_bottom_line()
        self._add_little_squares()
        self._add_scroll_shadow()
        self._add_cell_images()

    def _add_bottom_line(self):
        self.bottom_line = Line(name='bottom_line', parent=self, align=uiconst.TOBOTTOM, height=LINE_HEIGHT, color=LINE_COLOR)

    def _add_little_squares(self):
        self.little_squares_container = Container(name='little_squares_container', parent=self, align=uiconst.TOLEFT, width=LITTLE_SQUARE_SIZE, padTop=PADDING_TOP, padRight=VERTICAL_PADDING)
        self.little_squares = {}
        for order in xrange(0, self.max_cells):
            self.little_squares[order] = LittleSquare(name='little_square_%s' % order, parent=self.little_squares_container, align=uiconst.TOTOP, width=LITTLE_SQUARE_SIZE, height=LITTLE_SQUARE_SIZE, padBottom=LITTLE_SQUARE_PADDING)

    def _add_scroll_shadow(self):
        scroll_shadow_container = Container(name='cell_scroll_shadow_container', parent=self, align=uiconst.TOLEFT_NOPUSH, width=BIG_SQUARE_SIZE + BIG_SQUARES_PADDING_R + SCROLL_WIDTH, padTop=PADDING_TOP, state=uiconst.UI_DISABLED)
        Sprite(name='cell_scroll_shadow', parent=scroll_shadow_container, align=uiconst.BOTTOMLEFT, width=SCROLL_SHADOW_WIDTH, height=SCROLL_SHADOW_HEIGHT, texturePath=SCROLL_SHADOW_TEXTURE)

    def _add_cell_images(self):
        self.cell_scroll = ScrollContainer(name='cell_scroll', parent=self, align=uiconst.TOLEFT, width=BIG_SQUARE_SIZE + BIG_SQUARES_PADDING_R + SCROLL_WIDTH, padTop=PADDING_TOP, state=uiconst.UI_PICKCHILDREN, scrollBarColor=SCROLL_COLOR)
        self.cell_scroll.mainCont.SetState(uiconst.UI_PICKCHILDREN)
        self.cells = {}
        for order in xrange(0, self.max_cells):
            bottom_padding = SCROLL_BOTTOM_PADDING if order == max(0, self.max_cells - 1) else 0
            top = order * (BIG_SQUARE_SIZE + BIG_SQUARE_PADDING)
            cell_container = Container(name='cell_container_%s' % order, parent=self.cell_scroll, align=uiconst.TOPLEFT, width=BIG_SQUARE_SIZE + BIG_SQUARES_PADDING_R, height=BIG_SQUARE_SIZE, top=top, padBottom=bottom_padding)
            self.cells[order] = Cell(name='cell_%s' % order, parent=cell_container, align=uiconst.TOPLEFT, width=BIG_SQUARE_SIZE, height=BIG_SQUARE_SIZE, on_cell_clicked=self.on_cell_clicked)

    def get_random_cell_image(self):
        available_ids = self.get_available_cell_ids()
        cell_image_id = choice(available_ids)
        return cell_image_id

    def get_available_cell_ids(self):
        all_cell_image_ids = set(xrange(1, NUMBER_OF_CELL_IMAGES + 1))
        used_cell_image_ids = set(self.cell_image_by_order.values())
        return list(all_cell_image_ids - used_cell_image_ids)

    def on_cell_clicked(self, index):
        if self.toggle_polygon_selection:
            self.toggle_polygon_selection(index)

    def on_polygon_added(self, index):
        if not self.is_listening_to_changes or index not in self.cells or self.cells[index].is_polygon_set(index):
            return
        cell_image_id = self.get_random_cell_image()
        self.cell_image_by_order[index] = cell_image_id
        self.cells[index].set_polygon(index, cell_image_id)
        self.little_squares[index].set_full()
        self.number_of_polygons += 1

    def _on_polygon_selected(self, index):
        if index in self.cells:
            cell = self.cells[index]
            if cell.is_polygon_set(index):
                cell.set_state_selected()

    def _on_polygon_deselected(self, index):
        if index in self.cells:
            cell = self.cells[index]
            if cell.is_polygon_set(index):
                cell.set_state_normal()

    def on_polygon_deleted(self, index):
        if not self.is_listening_to_changes or index not in self.cells or self.cells[index].is_polygon_set(None):
            return
        if index in self.cell_image_by_order:
            del self.cell_image_by_order[index]
        cell_image_ids = sorted(self.cell_image_by_order.items(), key=lambda x: x[0])
        self.number_of_polygons -= 1
        self.redraw_little_squares()
        self.redraw_cell_images()
        for order in xrange(0, self.number_of_polygons):
            try:
                cell_image_id = cell_image_ids[order][1]
            except (KeyError, IndexError):
                cell_image_id = None

            self.cell_image_by_order[order] = cell_image_id
            self.cells[order].set_polygon(order, cell_image_id)
            self.little_squares[order].set_full()

    def reset(self):
        self.number_of_polygons = 0
        self.cell_image_by_order = {}
        self.redraw_little_squares()
        self.redraw_cell_images()

    def redraw_little_squares(self):
        if self.little_squares_container and not self.little_squares_container.destroyed:
            self.little_squares_container.Close()
        self._add_little_squares()

    def redraw_cell_images(self):
        if self.cell_scroll and not self.cell_scroll.destroyed:
            self.cell_scroll.Close()
        self._add_cell_images()

    def Enable(self, *args):
        super(Cells, self).Enable(*args)
        self.is_listening_to_changes = True
        self.reset()

    def Disable(self, *args):
        super(Cells, self).Disable(*args)
        self.is_listening_to_changes = False

    def invalidate(self, invalid_polygons):
        for order, cell in self.cells.items():
            is_valid = order not in invalid_polygons
            if is_valid:
                cell.set_state_valid()
            else:
                cell.set_state_invalid()
