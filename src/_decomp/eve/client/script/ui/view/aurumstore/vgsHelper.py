#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\view\aurumstore\vgsHelper.py
import localization
from evephotosvc.const import NONE_PATH

def FormatAUR(amount):
    return localization.GetByLabel('UI/VirtualGoodsStore/FormatAUR', amount=amount)


def FormatPLEX(amount):
    return localization.GetByLabel('UI/VirtualGoodsStore/FormatPlex', amount=amount)


def LoadImageToSprite(sprite, imageUrl, defaultImageUrl = 'res:/UI/Texture/Vgs/missing_image.png'):
    texture, w, h = (None, 0, 0)
    if imageUrl:
        texture, w, h = sm.GetService('photo').GetTextureFromURL(imageUrl, retry=False)
    if texture is None or texture.resPath == NONE_PATH:
        texture, w, h = sm.GetService('photo').GetTextureFromURL(defaultImageUrl, retry=False)
    sprite.texture = texture
    sprite.width = w
    sprite.height = h
