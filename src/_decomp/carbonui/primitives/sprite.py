#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\primitives\sprite.py
import logging
import weakref
from collections import Sequence
import audio2
import blue
import eveexceptions
import eveicon
import trinity
import uthread
import videoplayer
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui import uiconst
from carbonui.primitives.base import Base
from carbonui.primitives.message_bus.videoMessenger import VideoMessenger
from carbonui.uicore import uicore
from carbonui.util import colorblind
from carbonui.util.dpi import reverse_scale_dpi
GameWorld = None
DEFAULTCOLOR = (1.0,
 1.0,
 1.0,
 1.0)
logger = logging.getLogger(__name__)

class VisibleBase(Base):
    __renderObject__ = None
    default_left = 0
    default_top = 0
    default_color = DEFAULTCOLOR
    default_opacity = None
    default_blendMode = trinity.TR2_SBM_BLEND
    default_outputMode = trinity.Tr2SpriteTarget.COLOR
    default_glowBrightness = 1.0
    default_depth = 0.0
    default_ignoreColorBlindMode = False
    _blendMode = None
    _color = None
    _depth = None
    _glowBrightness = None
    _outputMode = None

    def ApplyAttributes(self, attributes):
        super(VisibleBase, self).ApplyAttributes(attributes)
        self.ignoreColorBlindMode = attributes.get('ignoreColorBlindMode', self.default_ignoreColorBlindMode)
        self.initialColor = attributes.get('color', self.default_color)
        if self.initialColor not in (None, DEFAULTCOLOR):
            self.SetRGBA(*self.initialColor)
        self.blendMode = attributes.get('blendMode', self.default_blendMode)
        self.outputMode = attributes.get('outputMode', self.default_outputMode)
        self.glowBrightness = attributes.get('glowBrightness', self.default_glowBrightness)
        self.depth = attributes.get('depth', self.default_depth)
        opacity = attributes.get('opacity', self.default_opacity)
        if opacity is not None:
            self.opacity = opacity

    def Close(self):
        self._color = None
        Base.Close(self)

    @property
    def blendMode(self):
        return self._blendMode

    @blendMode.setter
    def blendMode(self, value):
        self._blendMode = value
        ro = self.renderObject
        if ro:
            ro.blendMode = value

    @property
    def outputMode(self):
        return self._outputMode

    @outputMode.setter
    def outputMode(self, value):
        self._outputMode = value
        if self.renderObject:
            self.renderObject.spriteTarget = value

    @property
    def glowBrightness(self):
        return self._glowBrightness

    @glowBrightness.setter
    def glowBrightness(self, value):
        self._glowBrightness = value
        if self.renderObject:
            self.renderObject.glowBrightness = value

    @property
    def color(self):
        self._InitializeColor()
        return self._color

    @color.setter
    def color(self, value):
        if isinstance(value, Sequence):
            if len(value) == 3:
                self.SetRGB(*value)
            else:
                self.SetRGBA(*value)
        elif isinstance(value, PyColor):
            self._color = value
            self._ApplyColor()

    @color.deleter
    def color(self):
        self._color = None

    def _InitializeColor(self):
        if self._color is None:
            self._color = PyColor(self)
            self._ApplyColor()

    @property
    def rgb(self):
        self._InitializeColor()
        return self._color.GetRGB()

    @rgb.setter
    def rgb(self, value):
        try:
            self.color.SetRGB(*value)
        except Exception:
            logger.exception('Invalid color: %s' % repr(value))

    @property
    def rgba(self):
        self._InitializeColor()
        return self._color.GetRGBA()

    @rgba.setter
    def rgba(self, value):
        try:
            self.color.SetRGBA(*value)
        except Exception:
            logger.exception('Invalid color: %s' % repr(value))

    def _ApplyColor(self):
        ro = self.renderObject
        if ro and self._color:
            ro.color = self.CheckReplaceColor(self._color.GetRGBA())

    @property
    def opacity(self):
        return self.color.a

    @opacity.setter
    def opacity(self, value):
        self.color.a = value

    @property
    def depth(self):
        return self._depth

    @depth.setter
    def depth(self, value):
        self._depth = value
        ro = self.renderObject
        if ro:
            ro.depth = value

    def SetRGB(self, *color):
        try:
            self.color.SetRGB(*color)
        except Exception:
            logger.exception('Invalid color: %s' % repr(color))

    def SetRGBA(self, *color):
        try:
            self.color.SetRGBA(*color)
        except Exception:
            logger.exception('Invalid color: %s' % repr(color))

    def CheckReplaceColor(self, color):
        if not self.ignoreColorBlindMode:
            color = colorblind.CheckReplaceColor(color)
        return color

    def GetRGB(self):
        return self.color.GetRGB()

    def GetRGBA(self):
        return self.color.GetRGBA()

    def SetAlpha(self, alpha):
        self.color.SetAlpha(alpha)

    def GetAlpha(self):
        return self.color.GetAlpha()


class TexturedBase(VisibleBase):
    __renderObject__ = None
    default_noScale = 0
    default_texturePath = None
    default_textureSecondaryPath = None
    default_translationPrimary = (0.0, 0.0)
    default_translationSecodary = (0.0, 0.0)
    default_glowFactor = 0.0
    default_glowExpand = 0.0
    default_glowColor = (1, 1, 1, 1)
    default_shadowOffset = (0, 0)
    default_shadowColor = (0, 0, 0, 0.5)
    default_spriteEffect = trinity.TR2_SFX_COPY
    default_rotation = 0.0
    default_tileX = False
    default_tileY = False
    _glowColor = None
    _glowExpand = None
    _glowFactor = None
    _rectHeight = None
    _rectLeft = None
    _rectTop = None
    _rectWidth = None
    _shadowColor = None
    _shadowOffset = None
    _spriteEffect = None
    _texture = None
    _textureSecondary = None

    def ApplyAttributes(self, attributes):
        super(TexturedBase, self).ApplyAttributes(attributes)
        self.texture = trinity.Tr2Sprite2dTexture()
        texturePath = attributes.get('texturePath', self.default_texturePath)
        if texturePath:
            self.SetTexturePath(texturePath)
        secondaryPath = attributes.get('textureSecondaryPath', self.default_textureSecondaryPath)
        if secondaryPath:
            self.SetSecondaryTexturePath(secondaryPath)
        self.glowFactor = attributes.get('glowFactor', self.default_glowFactor)
        self.glowExpand = attributes.get('glowExpand', self.default_glowExpand)
        self.glowColor = attributes.get('glowColor', self.default_glowColor)
        self.shadowOffset = attributes.get('shadowOffset', self.default_shadowOffset)
        self.shadowColor = attributes.get('shadowColor', self.default_shadowColor)
        rectLeft = attributes.rectLeft
        if rectLeft:
            self.rectLeft = rectLeft
        rectTop = attributes.rectTop
        if rectTop:
            self.rectLeft = rectTop
        rectWidth = attributes.rectWidth
        if rectWidth:
            self.rectWidth = rectWidth
        rectHeight = attributes.rectHeight
        if rectHeight:
            self.rectHeight = rectHeight
        self.translationPrimary = attributes.get('translationPrimary', self.default_translationPrimary)
        self.translationSecondary = attributes.get('translationSecondary', self.default_translationSecodary)
        self.spriteEffect = attributes.get('spriteEffect', self.default_spriteEffect)
        self.rotation = attributes.get('rotation', self.default_rotation)
        self.tileX = attributes.get('tileX', self.default_tileX)
        self.tileY = attributes.get('tileY', self.default_tileY)

    def Close(self):
        self._texture = None
        self._textureSecondary = None
        super(TexturedBase, self).Close()

    @property
    def spriteEffect(self):
        return self._spriteEffect

    @spriteEffect.setter
    def spriteEffect(self, value):
        self._spriteEffect = value
        ro = self.renderObject
        if ro and hasattr(ro, 'spriteEffect'):
            ro.spriteEffect = value

    @property
    def texture(self):
        return self._texture

    @texture.setter
    def texture(self, value):
        self._texture = value
        ro = self.renderObject
        if ro:
            ro.texturePrimary = self._texture

    @property
    def textureSecondary(self):
        return self._textureSecondary

    @textureSecondary.setter
    def textureSecondary(self, value):
        self._textureSecondary = value
        ro = self.renderObject
        if ro and value is not None:
            ro.textureSecondary = value

    @property
    def rectLeft(self):
        return self._rectLeft

    @rectLeft.setter
    def rectLeft(self, value):
        self._rectLeft = value
        ro = self.renderObject
        if ro and ro.texturePrimary:
            ro.texturePrimary.srcX = value

    @property
    def rectTop(self):
        return self._rectTop

    @rectTop.setter
    def rectTop(self, value):
        self._rectTop = value
        ro = self.renderObject
        if ro and ro.texturePrimary:
            ro.texturePrimary.srcY = value

    @property
    def rectWidth(self):
        return self._rectWidth

    @rectWidth.setter
    def rectWidth(self, value):
        self._rectWidth = value
        ro = self.renderObject
        if ro and ro.texturePrimary:
            ro.texturePrimary.srcWidth = value

    @property
    def rectHeight(self):
        return self._rectHeight

    @rectHeight.setter
    def rectHeight(self, value):
        self._rectHeight = value
        ro = self.renderObject
        if ro and ro.texturePrimary:
            ro.texturePrimary.srcHeight = value

    @property
    def rectSecondary(self):
        if self.textureSecondary:
            return (self.textureSecondary.srcX,
             self.textureSecondary.srcY,
             self.textureSecondary.srcWidth,
             self.textureSecondary.srcHeight)

    @rectSecondary.setter
    def rectSecondary(self, value):
        if self.textureSecondary:
            self.textureSecondary.srcX, self.textureSecondary.srcY, self.textureSecondary.srcWidth, self.textureSecondary.srcHeight = value

    @property
    def translationPrimary(self):
        if self.texture:
            return self.texture.translation

    @translationPrimary.setter
    def translationPrimary(self, value):
        if self.texture:
            self.texture.translation = value
            if value != (0, 0):
                self.texture.useTransform = True
                self._EnableStandAloneTexture(self.texture)

    @property
    def translationSecondary(self):
        if self.textureSecondary:
            return self.textureSecondary.translation

    @translationSecondary.setter
    def translationSecondary(self, value):
        if self.textureSecondary:
            self.textureSecondary.translation = value
            if value != (0, 0):
                self.__EnableSecondaryTransform()

    @property
    def rotationSecondary(self):
        if self.textureSecondary:
            return self.textureSecondary.rotation

    @rotationSecondary.setter
    def rotationSecondary(self, value):
        if self.textureSecondary:
            self.textureSecondary.rotation = value
            if value != 0.0:
                self.__EnableSecondaryTransform()

    @property
    def scaleSecondary(self):
        if self.textureSecondary:
            return self.textureSecondary.scale

    @scaleSecondary.setter
    def scaleSecondary(self, value):
        if self.textureSecondary:
            self.textureSecondary.scale = value
            if value != (1.0, 1.0):
                self.__EnableSecondaryTransform()

    @property
    def scalingCenterSecondary(self):
        if self.textureSecondary:
            return self.textureSecondary.scalingCenter

    @scalingCenterSecondary.setter
    def scalingCenterSecondary(self, value):
        if self.textureSecondary:
            self.textureSecondary.scalingCenter = value

    @property
    def glowFactor(self):
        return self._glowFactor

    @glowFactor.setter
    def glowFactor(self, value):
        self._glowFactor = value
        ro = self.renderObject
        if ro:
            ro.glowFactor = value

    @property
    def glowExpand(self):
        return self._glowExpand

    @glowExpand.setter
    def glowExpand(self, value):
        self._glowExpand = value
        ro = self.renderObject
        if ro:
            ro.glowExpand = value

    @property
    def glowColor(self):
        return self._glowColor

    @glowColor.setter
    def glowColor(self, value):
        self._glowColor = value
        ro = self.renderObject
        if ro:
            ro.glowColor = value

    @property
    def shadowOffset(self):
        return self._shadowOffset

    @shadowOffset.setter
    def shadowOffset(self, value):
        self._shadowOffset = value
        ro = self.renderObject
        if ro:
            ro.shadowOffset = value

    @property
    def shadowColor(self):
        return self._shadowColor

    @shadowColor.setter
    def shadowColor(self, value):
        self._shadowColor = value
        ro = self.renderObject
        if ro:
            ro.shadowColor = value

    @property
    def rotation(self):
        if self.texture:
            return self.texture.rotation
        else:
            return 0

    @rotation.setter
    def rotation(self, value):
        if self.texture:
            self.texture.rotation = value
            if value != 0.0:
                self.texture.useTransform = True
                self._EnableStandAloneTexture(self.texture)

    @property
    def scale(self):
        if self.texture:
            return self.texture.scale

    @scale.setter
    def scale(self, value):
        if self.texture:
            self.texture.scale = value
            if value != (1.0, 1.0):
                self.texture.useTransform = True
                self._EnableStandAloneTexture(self.texture)

    @property
    def scalingCenter(self):
        if self.texture:
            return self.texture.scalingCenter

    @scalingCenter.setter
    def scalingCenter(self, value):
        if self.texture:
            self.texture.scalingCenter = value

    @property
    def tileX(self):
        if self.texture:
            return self.texture.tileX

    @tileX.setter
    def tileX(self, value):
        if self.texture:
            self.texture.tileX = value
            if value:
                self.texture.useTransform = True
                self._EnableStandAloneTexture(self.texture)

    @property
    def tileY(self):
        if self.texture:
            return self.texture.tileY

    @tileY.setter
    def tileY(self, value):
        if self.texture:
            self.texture.tileY = value
            if value:
                self.texture.useTransform = True
                self._EnableStandAloneTexture(self.texture)

    @property
    def tileXSecondary(self):
        if self.textureSecondary:
            return self.textureSecondary.tileX

    @tileXSecondary.setter
    def tileXSecondary(self, value):
        if self.textureSecondary:
            self.textureSecondary.tileX = value
            if value:
                self.textureSecondary.useTransform = True
                self._EnableStandAloneTexture(self.textureSecondary)

    @property
    def tileYSecondary(self):
        if self.textureSecondary:
            return self.textureSecondary.tileY

    @tileYSecondary.setter
    def tileYSecondary(self, value):
        if self.textureSecondary:
            self.textureSecondary.tileY = value
            if value:
                self.textureSecondary.useTransform = True
                self._EnableStandAloneTexture(self.textureSecondary)

    def _EnableStandAloneTexture(self, texture):
        if getattr(texture, 'atlasTexture', None) is not None:
            texture.atlasTexture.isStandAlone = True

    def __EnableSecondaryTransform(self):
        self.textureSecondary.useTransform = True
        self._EnableStandAloneTexture(self.textureSecondary)

    def ReloadTexture(self):
        if self.texture:
            if self.texture.atlasTexture:
                self.texture.atlasTexture.Reload()

    def ReloadSecondaryTexture(self):
        if self.textureSecondary:
            if self.textureSecondary.atlasTexture:
                self.textureSecondary.atlasTexture.Reload()

    def SetTexturePath(self, texturePath):
        if self.texture:
            newPath = str(texturePath or '')
            if newPath != self.texture.resPath:
                self.texture.resPath = newPath

    LoadTexture = SetTexturePath

    def GetTexturePath(self):
        if self.texture:
            return self.texture.resPath

    texturePath = property(GetTexturePath, SetTexturePath)

    def SetSecondaryTexturePath(self, texturePath):
        if not self.textureSecondary:
            self.textureSecondary = trinity.Tr2Sprite2dTexture()
        self.textureSecondary.resPath = str(texturePath or '')

    def GetSecondaryTexturePath(self):
        if self.textureSecondary:
            return self.textureSecondary.resPath

    def SetRect(self, rectLeft, rectTop, rectWidth, rectHeight):
        self.rectLeft = rectLeft
        self.rectTop = rectTop
        self.rectWidth = rectWidth
        self.rectHeight = rectHeight

    def LoadIcon(self, iconNo, ignoreSize = False):
        if self.destroyed:
            return
        if iconNo.startswith('res:') or iconNo.startswith('cache:'):
            self.SetTexturePath(iconNo)
            return
        if iconNo.startswith('ui_'):
            root, sheetNo, iconSize, icon = iconNo.split('_')
            resPath = 'res:/ui/texture/icons/%s_%s_%s.png' % (int(sheetNo), int(iconSize), int(icon))
            iconSize = int(iconSize)
            self.SetTexturePath(resPath)
            if not ignoreSize and self.GetAlign() != uiconst.TOALL and self.texture.atlasTexture:
                self.width = iconSize
                self.height = iconSize
            return
        return iconNo


class Sprite(TexturedBase):
    __guid__ = 'uiprimitives.Sprite'
    __renderObject__ = trinity.Tr2Sprite2d
    isDragObject = True
    default_noScale = 0
    default_left = 0
    default_top = 0
    default_width = 0
    default_height = 0
    default_pickRadius = 0
    default_saturation = 1.0
    default_effectOpacity = 1.0
    default_useSizeFromTexture = False
    _sprite = None
    _effectOpacity = None
    _pickRadius = None
    _saturation = None
    _texturePath = None
    _useSizeFromTexture = None

    def ApplyAttributes(self, attributes):
        super(Sprite, self).ApplyAttributes(attributes)
        self.pickRadius = attributes.get('pickRadius', self.default_pickRadius)
        self.saturation = attributes.get('saturation', self.default_saturation)
        self.effectOpacity = attributes.get('effectOpacity', self.default_effectOpacity)
        self.useSizeFromTexture = attributes.get('useSizeFromTexture', self.default_useSizeFromTexture)

    @property
    def pickRadius(self):
        return self._pickRadius

    @pickRadius.setter
    def pickRadius(self, value):
        self._pickRadius = value
        ro = self.renderObject
        if ro and hasattr(ro, 'pickRadius'):
            if value < 0:
                ro.pickRadius = value
            else:
                ro.pickRadius = uicore.ScaleDpi(value) or 0.0

    @property
    def useSizeFromTexture(self):
        return self._useSizeFromTexture

    @useSizeFromTexture.setter
    def useSizeFromTexture(self, value):
        self._useSizeFromTexture = value
        if self.renderObject:
            self.renderObject.useSizeFromTexture = value

    @property
    def saturation(self):
        return self._saturation

    @saturation.setter
    def saturation(self, value):
        self._saturation = value
        ro = self.renderObject
        if ro:
            ro.saturation = value or 0.0

    @property
    def effectOpacity(self):
        return self._effectOpacity

    @effectOpacity.setter
    def effectOpacity(self, value):
        self._effectOpacity = value
        ro = self.renderObject
        if ro:
            ro.effectOpacity = value or 0.0

    def SetTexturePath(self, texturePath):
        self._texturePath = texturePath
        if isinstance(texturePath, eveicon.IconData):
            texturePath = self._resolve_icon_data_texture(texturePath)
        super(Sprite, self).SetTexturePath(texturePath)

    LoadTexture = SetTexturePath
    texturePath = property(TexturedBase.GetTexturePath, SetTexturePath)

    def _resolve_icon_data_texture(self, icon_data):
        size = max(reverse_scale_dpi(self.displayWidth), reverse_scale_dpi(self.displayHeight))
        return icon_data.resolve(size)

    def UpdateAlignment(self, budgetLeft = 0, budgetTop = 0, budgetWidth = 0, budgetHeight = 0, updateChildrenOnly = False):
        result_budget_left, result_budget_top, result_budget_width, result_budget_height, size_changed = super(Sprite, self).UpdateAlignment(budgetLeft, budgetTop, budgetWidth, budgetHeight, updateChildrenOnly)
        if size_changed and isinstance(self._texturePath, eveicon.IconData):
            new_texture_path = self._resolve_icon_data_texture(self._texturePath)
            super(Sprite, self).SetTexturePath(new_texture_path)
        return (result_budget_left,
         result_budget_top,
         result_budget_width,
         result_budget_height,
         size_changed)


class RenderTargetSprite(Sprite):
    __guid__ = 'uiprimitives.RenderTargetSprite'
    __renderObject__ = trinity.Tr2Sprite2d
    default_spriteEffect = trinity.TR2_SFX_NOALPHA

    def ApplyAttributes(self, attributes):
        Sprite.ApplyAttributes(self, attributes)
        self._viewport_width = attributes.viewportWidth
        self._viewport_height = attributes.viewportHeight
        RO = self.GetRenderObject()
        self._construct_render_target()
        if 'pos' in attributes:
            default_pos = (self.default_left,
             self.default_top,
             self.default_width,
             self.default_height)
            pos = attributes.get('pos', default_pos)
            RO.displayX, RO.displayY, RO.displayWidth, RO.displayHeight = pos

    def _construct_render_target(self):
        self._texture_res = trinity.TriTextureRes()
        self.render_target = trinity.Tr2RenderTarget(self._viewport_width, self._viewport_height, 1, trinity.PIXEL_FORMAT.B8G8R8X8_UNORM)
        self._texture_res.CreateEmptyTexture(self.width, self.height, 1, trinity.PIXEL_FORMAT.B8G8R8A8_UNORM)
        self._texture_res.SetFromRenderTarget(self.render_target)
        self.texture.atlasTexture = trinity.Tr2AtlasTexture()
        self.texture.atlasTexture.textureRes = self._texture_res

    def Close(self, *args, **kwds):
        self._texture_res = None
        self.render_target = None
        super(RenderTargetSprite, self).Close()


class StreamingVideoSprite(Sprite):
    __guid__ = 'uiprimitives.StreamingVideoSprite'
    __renderObject__ = trinity.Tr2Sprite2d
    __notifyevents__ = ['OnAudioActivated', 'OnAudioDeactivated']
    default_disableAudio = False
    default_videoPath = ''
    default_videoLoop = False
    default_videoAutoPlay = True
    default_muteAudio = False
    default_spriteEffect = trinity.TR2_SFX_NOALPHA
    default_sendAnalytics = None

    def ApplyAttributes(self, attributes):
        Sprite.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self._sendAnalytics = attributes.get('sendAnalytics', self.default_sendAnalytics)
        self.textureRes = trinity.TriTextureRes()
        self.texture = trinity.Tr2Sprite2dTexture()
        self.player = None
        self.path = None
        self.audioTrack = 0
        self.videoLoop = False
        self.emitter = None
        self._oldPosition = 0
        self.loopChecker = None
        self._updateStep = None
        self._isFetchingFile = False
        RO = self.GetRenderObject()
        self.disableAudio = attributes.get('disableAudio', self.default_disableAudio)
        self._positionComponent = attributes.get('positionComponent', None)
        self.positionComponent = None
        self._auto_play = attributes.get('videoAutoPlay', self.default_videoAutoPlay)
        if 'videoPath' in attributes and attributes['videoPath']:
            self.SetVideoPath(attributes['videoPath'], attributes.get('audioTrack', 0), attributes.get('videoLoop', self.default_videoLoop))
        if 'pos' in attributes:
            default_pos = (self.default_left,
             self.default_top,
             self.default_width,
             self.default_height)
            pos = attributes.get('pos', default_pos)
            RO.displayX, RO.displayY, RO.displayWidth, RO.displayHeight = pos

    def Close(self, *args, **kwds):
        self._DestroyVideo()
        super(StreamingVideoSprite, self).Close()

    def OnVideoSizeAvailable(self, width, height):
        pass

    def OnVideoDurationAvailable(self):
        pass

    def OnVideoFinished(self):
        pass

    def _OnCreateTextures(self, player, width, height):
        if not self.texture:
            return
        try:
            self.textureRes = trinity.TriTextureRes()
            self.textureRes.CreateEmptyTexture(width, height, 1, trinity.PIXEL_FORMAT.B8G8R8A8_UNORM)
            player.bgra_texture = self.textureRes
            self.texture.atlasTexture = trinity.Tr2AtlasTexture()
            self.texture.atlasTexture.textureRes = self.textureRes
        except Exception:
            logging.exception('Exception in VideoPlayer.on_create_textures')

    def _OnVideoStateChange(self, player):
        try:
            logging.debug('Video player state changed to %s', videoplayer.State.GetNameFromValue(player.state))
            if player.state == videoplayer.State.INITIAL_BUFFERING:
                info = self.player.get_video_info()
                self.OnVideoSizeAvailable(info['width'], info['height'])
                self.OnVideoDurationAvailable()
                self.StartLoopChecker()
            elif player.state == videoplayer.State.DONE:
                self._LogVideoProtoEventStopped(played_to=int(self.GetPositionRatioInVideo() * 100))
                self.OnVideoFinished()
                self.StopLoopChecker()
        except Exception:
            logging.exception('Exception in VideoPlayer.on_state_change')

    def _OnVideoError(self, *args):
        try:
            self.player.validate()
        except RuntimeError:
            logging.exception('Video player error')

    def _DestroyVideo(self):
        self._LogVideoProtoEventStopped(played_to=int(self.GetPositionRatioInVideo() * 100))
        if self.positionComponent:
            self.positionComponent.UnRegisterPlacementObserverWrapper(self.positionObserver)
            self.positionComponent = None
            self.positionObserver = None
        self.emitter = None
        self.player = None
        self._updateStep = None
        self.textureRes = trinity.TriTextureRes()

    @eveexceptions.EatsExceptions('protoClientLogs')
    def _LogVideoProtoEvent(self, event_class, *args, **kwargs):
        if self._sendAnalytics and self.path:
            proto_event = event_class(hierarchy_path=self.analyticContext, video_path=self.path, *args, **kwargs)
            sm.GetService('publicGatewaySvc').publish_event(proto_event)

    @eveexceptions.EatsExceptions('protoClientLogs')
    def _LogVideoProtoEventStarted(self):
        if self._sendAnalytics and self.path:
            message_bus = VideoMessenger(sm.GetService('publicGatewaySvc'))
            message_bus.video_started(hierarchy_path=self.analyticContext, video_path=self.path)

    @eveexceptions.EatsExceptions('protoClientLogs')
    def _LogVideoProtoEventLooped(self):
        if self._sendAnalytics and self.path:
            message_bus = VideoMessenger(sm.GetService('publicGatewaySvc'))
            message_bus.video_looped(hierarchy_path=self.analyticContext, video_path=self.path)

    @eveexceptions.EatsExceptions('protoClientLogs')
    def _LogVideoProtoEventStopped(self, played_to):
        if self._sendAnalytics and self.path:
            message_bus = VideoMessenger(sm.GetService('publicGatewaySvc'))
            message_bus.video_stopped(hierarchy_path=self.analyticContext, video_path=self.path, played_to=played_to)

    @eveexceptions.EatsExceptions('protoClientLogs')
    def _LogVideoProtoEventSeeked(self, new_position):
        if self._sendAnalytics and self.path:
            message_bus = VideoMessenger(sm.GetService('publicGatewaySvc'))
            message_bus.video_seeked(hierarchy_path=self.analyticContext, video_path=self.path, new_position=new_position)

    def OnAudioActivated(self):
        if self.path and not self._isFetchingFile:
            self.SetVideoPath(self.path, self.audioTrack, self.videoLoop)

    def OnAudioDeactivated(self):
        if self.path and not self._isFetchingFile:
            self.SetVideoPath(self.path, self.audioTrack, self.videoLoop)

    def SetPositionComponent(self, positionComponent):
        if self.emitter and positionComponent and GameWorld:
            self.positionObserver = GameWorld.PlacementObserverWrapper(self.emitter)
            positionComponent.RegisterPlacementObserverWrapper(self.positionObserver)
            return positionComponent

    def GetVideoSize(self):
        try:
            info = self.player.get_video_info()
            return (info['width'], info['height'])
        except (AttributeError, videoplayer.VideoPlayerError):
            pass

    def SetVideoPath(self, path, audioTrack = 0, videoLoop = False):
        self._DestroyVideo()
        self.path = path
        self.audioTrack = audioTrack
        self.videoLoop = videoLoop

        def prefetch():
            blue.paths.GetFileContentsWithYield(path)
            if self._isFetchingFile and path == self.path:
                self._isFetchingFile = False
                self.SetVideoPath(path, audioTrack, videoLoop)

        if path.lower().startswith('res:/'):
            if blue.remoteFileCache.FileExists(path):
                if not blue.paths.FileExistsLocally(path):
                    self._isFetchingFile = True
                    uthread.new(prefetch)
                    return
        if not self.disableAudio:
            is3D = self._positionComponent is not None
            self.positionComponent = self.SetPositionComponent(self._positionComponent)
        if path.lower().startswith('res:/') or path.find(':') < 2:
            stream = blue.paths.open(path)
        else:
            stream = blue.BlueNetworkStream(unicode(path).encode('utf-8'))
        if uicore.audioHandler.active and not self.disableAudio:
            inputMgr = audio2.AudioInputMgr()
            sink = videoplayer.WwiseAudioSink(inputMgr)
        else:
            sink = None
        self.player = videoplayer.VideoPlayer(stream, sink, audioTrack, videoLoop)
        self.player.on_state_change = self._OnVideoStateChange
        self.player.on_create_textures = self._OnCreateTextures
        self.player.on_error = self._OnVideoError
        if not self._auto_play:
            self.player.pause()
            self.player.seek(0)
        self._LogVideoProtoEventStarted()

    def StartLoopChecker(self):
        self.loopChecker = AutoTimer(1, self.HasLooped)

    def StopLoopChecker(self):
        if not self.loopChecker:
            return
        self._oldPosition = 0
        self.loopChecker.KillTimer()

    def Play(self):
        if self.player:
            self.player.resume()
            self.StartLoopChecker()

    def Pause(self):
        if self.player:
            self.player.pause()
            self.StopLoopChecker()

    def MuteAudio(self):
        try:
            self.player.audio_sink.volume = 0
        except AttributeError:
            pass

    def UnmuteAudio(self):
        try:
            self.player.audio_sink.volume = 1.0
        except AttributeError:
            pass

    def GetVolume(self):
        try:
            return self.player.audio_sink.volume
        except AttributeError:
            return 1

    def SetVolume(self, volume):
        try:
            self.player.audio_sink.volume = volume
        except AttributeError:
            pass

    def Seek(self, nanoseconds):
        self.StopLoopChecker()
        try:
            self.player.seek(nanoseconds)
        except AttributeError:
            pass
        else:
            isMouseDown = uicore.uilib.leftbtn
            if not isMouseDown:
                self._LogVideoProtoEventSeeked(new_position=int(self.GetPositionRatioInVideo() * 100))
            self.StartLoopChecker()

    def GetPositionRatioInVideo(self):
        if not self.mediaTime or not self.duration:
            return 0
        secondsInNano = 1000000
        duration = float((self.duration or 1) / secondsInNano)
        if duration == 0:
            duration = 1
        try:
            new_position = min(float((self.mediaTime % self.duration or 0) / secondsInNano) / duration, 1)
        except TypeError:
            return 0

        return new_position

    def HasLooped(self):
        if self.player and self.player.duration:
            time = self.player.media_time % self.player.duration or 0
            if time and time < self._oldPosition:
                self._LogVideoProtoEventLooped()
            self._oldPosition = time
        return False

    @property
    def isMuted(self):
        try:
            return self.player.audio_sink.volume == 0
        except AttributeError:
            return None

    @property
    def isPaused(self):
        if self.player:
            return self.player.is_paused

    @property
    def isFinished(self):
        if self.destroyed:
            return True
        if self._isFetchingFile:
            return False
        if self.player:
            return self.player.state == videoplayer.State.DONE

    @property
    def mediaTime(self):
        if self.player:
            return self.player.media_time

    @property
    def duration(self):
        if self.player:
            return self.player.duration

    @property
    def downloadedTime(self):
        if self.player:
            return self.player.downloaded_media_time


class PyColor(object):

    def __init__(self, owner, r = 1.0, g = 1.0, b = 1.0, a = 1.0):
        self.owner = weakref.ref(owner)
        self._r = r
        self._g = g
        self._b = b
        self._a = a

    def UpdateOwner(self):
        owner = self.owner()
        owner._ApplyColor()

    @property
    def r(self):
        return self._r

    @r.setter
    def r(self, value):
        self._r = value
        self.UpdateOwner()

    @property
    def g(self):
        return self._g

    @g.setter
    def g(self, value):
        self._g = value
        self.UpdateOwner()

    @property
    def b(self):
        return self._b

    @b.setter
    def b(self, value):
        self._b = value
        self.UpdateOwner()

    @property
    def a(self):
        return self._a

    @a.setter
    def a(self, value):
        self._a = value
        self.UpdateOwner()

    def SetRGB(self, r, g, b):
        self._r = r
        self._g = g
        self._b = b
        self.UpdateOwner()

    def SetRGBA(self, r, g, b, a = 1.0):
        self._r = r
        self._g = g
        self._b = b
        self._a = a
        self.UpdateOwner()

    def GetRGB(self):
        return (self.r, self.g, self.b)

    def GetRGBA(self):
        return (self.r,
         self.g,
         self.b,
         self.a)

    def SetAlpha(self, a):
        self.a = a

    def GetAlpha(self):
        return self.a

    def GetHSV(self):
        return trinity.TriColor(*self.GetRGBA()).GetHSV()

    def SetHSV(self, h, s, v):
        c = trinity.TriColor()
        c.SetHSV(h, s, v)
        self.SetRGB(c.r, c.g, c.b)

    def GetBrightness(self):
        return (self.r + self.g + self.b) / 3.0
