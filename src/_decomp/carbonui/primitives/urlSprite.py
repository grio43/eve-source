#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\primitives\urlSprite.py
from carbonui.primitives.sprite import Sprite
from evephotosvc.const import NONE_PATH
DEFAULT_IMAGE = 'res:/UI/Texture/Vgs/missing_image.png'

class UrlSprite(Sprite):

    def ApplyAttributes(self, attributes):
        super(UrlSprite, self).ApplyAttributes(attributes)
        self.url = attributes.get('url')
        self._load_texture_from_url()

    def _load_texture_from_url(self):
        if not self.url:
            raise AttributeError('UrlSprite requires image URL as a parameter')
        photo_service = sm.GetService('photo')
        texture, width, height = photo_service.GetTextureFromURL(self.url, retry=False)
        if not self._is_valid_texture(texture):
            texture, width, height = sm.GetService('photo').GetTextureFromURL(DEFAULT_IMAGE, retry=False)
        self.texture = texture
        self.width = width
        self.height = height

    def _is_valid_texture(self, texture):
        return texture is not None and texture.resPath != NONE_PATH
