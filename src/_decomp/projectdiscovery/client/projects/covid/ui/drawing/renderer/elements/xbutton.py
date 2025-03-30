#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\ui\drawing\renderer\elements\xbutton.py
import carbonui.const as uiconst
from carbonui.primitives import container
from carbonui.primitives import sprite
from carbonui.uicore import uicore
from projectdiscovery.client.projects.covid.ui.drawing.renderer.elements import colors
TEXTURES_FOLDER = 'res:/UI/Texture/classes/DrawingTool/x_button/'
TEXTURE_X = TEXTURES_FOLDER + 'x.png'
TEXTURE_BLACK_CIRCLE = TEXTURES_FOLDER + 'black_circle.png'
TEXTURE_BLUE_CIRCLE = TEXTURES_FOLDER + 'blue_circle.png'
TEXTURE_WHITE_RING = TEXTURES_FOLDER + 'white_ring.png'
TEXTURE_CLEAR = TEXTURES_FOLDER + 'clear.png'
BLUE_COLOR = (0.2, 0.74, 0.95, 1.0)
WHITE_COLOR = (1.0, 1.0, 1.0, 1.0)
ICON_SIZE = 32
LARGE_X_SIZE = 44
CLEAR_WIDTH = 42
CLEAR_HEIGHT = 18
PADDING_ICON_TO_CLEAR = 8
ANIMATION_CLICK_SECONDS = 0.2
ANIMATION_HOVER_SECONDS = 0.5

class XButton(container.Container):
    default_state = uiconst.UI_NORMAL
    default_width = ICON_SIZE
    default_height = ICON_SIZE

    def __init__(self, mouse_enter_callback, **attributes):
        self.polygon_uuid = None
        self.mouse_enter_callback = mouse_enter_callback
        super(XButton, self).__init__(**attributes)

    def ApplyAttributes(self, attributes):
        super(XButton, self).ApplyAttributes(attributes)
        self.button_function = attributes.get('button_function')
        self.setup_x_area()
        self.setup_tooltip_area()

    def setup_x_area(self):
        x_area = container.Container(name='x_area', parent=self, align=uiconst.TOLEFT, width=ICON_SIZE, state=uiconst.UI_DISABLED)
        self.x_sprite = sprite.Sprite(name='x_sprite', parent=x_area, align=uiconst.CENTER, width=ICON_SIZE, height=ICON_SIZE, texturePath=TEXTURE_X, color=BLUE_COLOR)
        self.black_circle = sprite.Sprite(name='black_circle', parent=x_area, align=uiconst.CENTER, width=ICON_SIZE, height=ICON_SIZE, texturePath=TEXTURE_BLACK_CIRCLE)
        self.blue_circle = sprite.Sprite(name='blue_circle', parent=x_area, align=uiconst.CENTER, width=ICON_SIZE, height=ICON_SIZE, texturePath=TEXTURE_BLUE_CIRCLE)
        self.white_ring = sprite.Sprite(name='white_ring', parent=x_area, align=uiconst.CENTER, width=ICON_SIZE, height=ICON_SIZE, texturePath=TEXTURE_WHITE_RING, opacity=0.0)

    def setup_tooltip_area(self):
        tooltip_area = container.Container(name='tooltip_area', parent=self, align=uiconst.TOLEFT, width=CLEAR_WIDTH, state=uiconst.UI_DISABLED, padLeft=PADDING_ICON_TO_CLEAR)
        self.clear_tooltip = sprite.Sprite(name='clear_tooltip', parent=tooltip_area, align=uiconst.CENTER, width=CLEAR_WIDTH, height=CLEAR_HEIGHT, texturePath=TEXTURE_CLEAR, opacity=0.0)

    def OnClick(self, *args):
        super(XButton, self).OnClick(*args)
        self.button_function(polygon_uuid=self.polygon_uuid)

    def OnMouseDown(self, *args):
        super(XButton, self).OnMouseDown(*args)
        self._restore_ring()
        self._restore_black_circle_to_hovered()
        self._restore_x_to_hovered()
        self._restore_tooltip_to_normal()
        self._animate_ring_on_click()
        self._animate_x_on_click()

    def OnMouseUp(self, *args):
        super(XButton, self).OnMouseUp(*args)
        self._restore_ring()
        self._restore_black_circle_to_normal()
        self._restore_x_to_normal()

    def OnMouseEnter(self, *args):
        super(XButton, self).OnMouseEnter(*args)
        self.mouse_enter_callback(polygon_uuid=self.polygon_uuid)
        self._restore_black_circle_to_normal()
        self._restore_x_to_normal()
        self._restore_tooltip_to_normal()
        self._animate_black_circle_on_hover()
        self._animate_x_on_hover()
        self._animate_tooltip_on_hover()

    def OnMouseExit(self, *args):
        super(XButton, self).OnMouseExit(*args)
        self.mouse_enter_callback(polygon_uuid=self.polygon_uuid, is_exit=True)
        self._restore_black_circle_to_normal()
        self._restore_x_to_normal()
        self._restore_tooltip_to_normal()

    def _animate_ring_on_click(self):
        animate = uicore.animations.FadeIn
        animate(self.white_ring, duration=ANIMATION_CLICK_SECONDS)

    def _animate_x_on_click(self):
        animate = uicore.animations.MorphScalar
        duration = ANIMATION_CLICK_SECONDS
        start_width, start_height = self.x_sprite.width, self.x_sprite.height
        end_width, end_height = ICON_SIZE, ICON_SIZE
        animate(self.x_sprite, 'width', start_width, end_width, duration)
        animate(self.x_sprite, 'height', start_height, end_height, duration)

    def _animate_x_on_hover(self):
        animate = uicore.animations.MorphScalar
        duration = ANIMATION_HOVER_SECONDS
        start_width, start_height = self.x_sprite.width, self.x_sprite.height
        end_width, end_height = LARGE_X_SIZE, LARGE_X_SIZE
        animate(self.x_sprite, 'width', start_width, end_width, duration)
        animate(self.x_sprite, 'height', start_height, end_height, duration)
        animate = uicore.animations.SpColorMorphToWhite
        duration = ANIMATION_HOVER_SECONDS
        animate(self.x_sprite, duration)

    def _animate_black_circle_on_hover(self):
        animate = uicore.animations.MorphScalar
        duration = ANIMATION_HOVER_SECONDS
        start_width, start_height = self.black_circle.width, self.black_circle.height
        end_width, end_height = (0, 0)
        animate(self.black_circle, 'width', start_width, end_width, duration)
        animate(self.black_circle, 'height', start_height, end_height, duration)

    def _animate_tooltip_on_hover(self):
        animate = uicore.animations.FadeIn
        animate(self.clear_tooltip, duration=ANIMATION_HOVER_SECONDS)

    def _restore_ring(self):
        self.white_ring.StopAnimations()
        self.white_ring.opacity = 0.0

    def _restore_black_circle_to_normal(self):
        self.black_circle.StopAnimations()
        self.black_circle.width, self.black_circle.height = ICON_SIZE, ICON_SIZE

    def _restore_x_to_normal(self):
        self.x_sprite.StopAnimations()
        self.x_sprite.width, self.x_sprite.height = ICON_SIZE, ICON_SIZE
        self.x_sprite.SetRGBA(*BLUE_COLOR)

    def _restore_tooltip_to_normal(self):
        self.clear_tooltip.StopAnimations()
        self.clear_tooltip.opacity = 0.0

    def _restore_black_circle_to_hovered(self):
        self.black_circle.StopAnimations()
        self.black_circle.width, self.black_circle.height = (0, 0)

    def _restore_x_to_hovered(self):
        self.x_sprite.StopAnimations()
        self.x_sprite.width, self.x_sprite.height = LARGE_X_SIZE, LARGE_X_SIZE
        self.x_sprite.SetRGBA(*WHITE_COLOR)
