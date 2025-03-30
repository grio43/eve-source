#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\liveIconRenderer.py
import logging
from carbonui import Align, SpriteEffect, PickState
from cosmetics.client.liveIconRendererQueue import LiveIconRenderQueue
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import RenderTargetSprite, Sprite
import trinity
from signals import Signal
from liveIconCacheUtils import cached_render_available, get_unique_filename, is_low_spec
log = logging.getLogger(__name__)

class LiveIconSprite(Container):
    __guid__ = 'form.LiveIconSprite'
    default_glow = True
    default_mask_texture_path = 'res:/UI/Texture/classes/Cosmetics/Ship/cards/skin_design/mask.png'

    def ApplyAttributes(self, attributes):
        super(LiveIconSprite, self).ApplyAttributes(attributes)
        self._viewport_width = attributes.viewportWidth
        self._viewport_height = attributes.viewportHeight
        self.bg_texture_path = attributes.bg_texture_path
        self._glow = attributes.get('glow', self.default_glow)
        mask_texture_path = attributes.get('mask_texture_path', self.default_mask_texture_path)
        self.queued_function_call = None
        self.on_rendered = Signal('on_rendered')
        self.last_skin_design = None
        self.space_object = None
        self.sprite = Sprite(name='LiveIconSprite_Cached', parent=self, align=Align.CENTER, width=self._viewport_width, height=self._viewport_height, spriteEffect=trinity.TR2_SFX_MASK, texturePath=None, textureSecondaryPath=mask_texture_path)

    def _construct_fallback_sprite(self):
        self.sprite = Sprite(name='LiveIconSprite_Backup', parent=self, align=Align.CENTER, width=32, height=32, texturePath='res:/UI/Texture/WindowIcons/paint_tool.png')

    def apply_skin_design(self, skin_design, bg_texture_path = None, skip_queue = False):
        if bg_texture_path:
            self.bg_texture_path = bg_texture_path
        log.info('LIVE ICONS - Apply SKIN design {name}, skip_queue={skip_queue}'.format(name=skin_design.name.encode('utf-8'), skip_queue=skip_queue))
        if cached_render_available(skin_design, self.bg_texture_path):
            skip_queue = True
        self.queued_function_call = lambda : self._apply_skin_design(skin_design, self.bg_texture_path)
        if skip_queue:
            self.queued_function_call()
        else:
            LiveIconRenderQueue.get_instance().add_to_queue(self.queued_function_call)

    def Close(self):
        self.space_object = None
        try:
            if self.queued_function_call:
                LiveIconRenderQueue.get_instance().remove_from_queue(self.queued_function_call)
        finally:
            super(LiveIconSprite, self).Close()

    def _apply_skin_design(self, skin_design, bg_texture_path):
        self.bg_texture_path = bg_texture_path
        design_name = skin_design.name.encode('utf-8')
        icon_generator = LiveIconRenderQueue.get_instance().get_icon_generator(self._viewport_width, self._viewport_height, skin_design, bg_texture_path)
        if cached_render_available(skin_design, bg_texture_path):
            texturePath = get_unique_filename(skin_design, bg_texture_path)
            self.sprite.LoadTexture(texturePath)
            self.on_rendered()
            return
        icon_generator.construct_render_job()
        icon_generator.set_skin_design(skin_design)
        log.info('LIVE ICONS - Rendering SKIN design {name}: icon generator created'.format(name=design_name))
        log.info('LIVE ICONS - Rendering SKIN design {name}: started'.format(name=design_name))
        self.queued_function_call = None
        if not self.IsVisible():
            return
        if self.last_skin_design != skin_design or not self.space_object:
            log.info('LIVE ICONS - Rendering SKIN design {name}: DNA update required'.format(name=design_name))
            log.info('LIVE ICONS - Rendering SKIN design {name}: DNA update done'.format(name=design_name))
        self.last_skin_design = skin_design
        cachedTexturePath = icon_generator.render_icon(skin_design, bg_texture_path, self._glow)
        self.sprite.texturePath = cachedTexturePath
        log.info('LIVE ICONS - Rendering SKIN design {name}: icon rendering done'.format(name=design_name))
        self.on_rendered()
        log.info('LIVE ICONS - Rendering SKIN design {name}: finished'.format(name=design_name))
