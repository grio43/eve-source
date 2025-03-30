#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\infoIcon.py
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui import eveColor, eveThemeColor
from eve.client.script.ui.control.glowSprite import GlowSprite

class InfoIcon(GlowSprite):
    default_abstractinfo = None
    default_texturePath = 'res:/ui/Texture/Icons/38_16_208.png'
    default_name = 'InfoIcon'
    default_typeID = None
    default_itemID = None
    default_width = 16
    default_height = 16

    def ApplyAttributes(self, attributes):
        GlowSprite.ApplyAttributes(self, attributes)
        self.itemID = attributes.get('itemID', self.default_itemID)
        self.typeID = attributes.get('typeID', self.default_typeID)
        self.abstractinfo = attributes.get('abstractinfo', self.default_abstractinfo)

    def OnClick(self, *args):
        if not self.typeID:
            return
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        self.ShowInfo(self.typeID, self.itemID, self.abstractinfo)

    def ShowInfo(self, typeID, itemID, abstractinfo, *_args):
        sm.GetService('info').ShowInfo(typeID=typeID, itemID=itemID, abstractinfo=abstractinfo)

    def UpdateInfoLink(self, typeID, itemID, abstractinfo = None):
        self.typeID = typeID
        self.itemID = itemID
        self.abstractinfo = abstractinfo

    def SetTypeID(self, typeID):
        self.typeID = typeID

    def SetItemID(self, itemID):
        self.itemID = itemID

    def SetAbstractInfo(self, abstractInfo):
        self.abstractinfo = abstractInfo

    def OnMouseEnter(self, *args):
        GlowSprite.OnMouseEnter(self, *args)
        PlaySound(uiconst.SOUND_BUTTON_HOVER)


class MoreInfoIcon(Sprite):
    default_width = 16
    default_height = 16
    default_texturePath = 'res:/ui/Texture/Shared/moreIcon.png'

    def GetTooltipDelay(self):
        return 0

    def OnMouseDown(self, *args):
        pass

    def OnMouseUp(self, *args):
        pass

    def OnMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_HOVER)


class MoreInfoIconBeta(Container):
    default_width = 16
    default_height = 16
    default_texturePath_circle = 'res:/ui/Texture/Shared/questionMarkCircle.png'
    default_texturePath_questionMark = 'res:/ui/Texture/Shared/questionMark.png'
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL
    default_circle_color = eveColor.CRYO_BLUE

    def ApplyAttributes(self, attributes):
        super(MoreInfoIconBeta, self).ApplyAttributes(attributes)
        self.circleTexturePath = attributes.get('circleTexturePath', self.default_texturePath_circle)
        self.circleColor = attributes.get('circleColor', self.default_circle_color)
        self.questionMarkTexturePath = attributes.get('questionMarkTexturePath', self.default_texturePath_questionMark)
        self.circle = GlowSprite(name='circle', parent=self, align=uiconst.CENTER, pos=(0,
         0,
         self.height,
         self.width), texturePath=self.circleTexturePath, state=uiconst.UI_DISABLED, color=self.circleColor)
        self.questionMark = Sprite(name='questionMark', parent=self, align=uiconst.CENTER, pos=(0,
         0,
         self.height,
         self.width), texturePath=self.questionMarkTexturePath, state=uiconst.UI_DISABLED)

    def GetTooltipDelay(self):
        return 0

    def OnMouseEnter(self, *args):
        super(MoreInfoIconBeta, self).OnMouseEnter(*args)
        self.circle.OnMouseEnter()
        PlaySound(uiconst.SOUND_BUTTON_HOVER)

    def OnMouseExit(self, *args):
        super(MoreInfoIconBeta, self).OnMouseExit(*args)
        self.circle.OnMouseExit()


class MoreExtraInfoInTooltip(MoreInfoIcon):
    default_width = 11
    default_height = 11
    default_texturePath = 'res:/ui/Texture/Icons/generic/extraInfoInTooltip.png'


class GlyphIcon(Container):
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL
    default_width = 16
    default_height = 16
    default_frameTexture = None
    default_glyphTexture = None
    default_frameColor = eveColor.WHITE
    default_glyphColor = eveColor.WHITE
    default_glowAmount = 0.5

    def ApplyAttributes(self, attributes):
        super(GlyphIcon, self).ApplyAttributes(attributes)
        self.frameTexture = attributes.get('frameTexture', self.default_frameTexture)
        self.glyphTexture = attributes.get('glyphTexture', self.default_glyphTexture)
        self.frameColor = attributes.get('frameColor', self.default_frameColor)
        self.glyphColor = attributes.get('glyphColor', self.default_glyphColor)
        self.func = attributes.get('func', None)
        self.ConstructLayout()

    def ConstructLayout(self):
        self.frame = GlowSprite(name='frame', parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath=self.frameTexture, color=self.frameColor, pos=(0,
         0,
         self.height,
         self.width), glowAmount=self.default_glowAmount)
        self.glyph = Sprite(name='glyph', parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath=self.glyphTexture, color=self.glyphColor, pos=(0,
         0,
         self.height,
         self.width))

    def OnClick(self, *args):
        if self.func:
            self.func()


class ThemedGlyphIcon(GlyphIcon):
    default_frameColor = eveThemeColor.THEME_FOCUS

    def OnColorThemeChanged(self):
        super(ThemedGlyphIcon, self).OnColorThemeChanged()
        self.frameColor = eveThemeColor.THEME_FOCUS
        self.frame.color = self.frameColor


class CheckMarkGlyphIcon(GlyphIcon):
    default_frameTexture = 'res:/ui/Texture/classes/Menu/Icons/circleBG.png'
    default_glyphTexture = 'res:/ui/Texture/classes/Menu/Icons/checkmark.png'
    default_frameColor = eveColor.SUCCESS_GREEN


class ExclamationMarkGlyphIcon(GlyphIcon):
    default_frameTexture = 'res:/ui/Texture/classes/Menu/Icons/circleBG.png'
    default_glyphTexture = 'res:/ui/Texture/classes/Menu/Icons/exclamationMark.png'
    default_frameColor = eveColor.WARNING_ORANGE


class WarningGlyphIcon(GlyphIcon):
    default_frameTexture = 'res:/ui/Texture/classes/Menu/Icons/triangleBG.png'
    default_glyphTexture = 'res:/ui/Texture/classes/Menu/Icons/exclamationMark.png'
    default_frameColor = eveColor.DANGER_RED


class InfoGlyphIcon(ThemedGlyphIcon):
    default_frameTexture = 'res:/ui/Texture/classes/Menu/Icons/circleBG.png'
    default_glyphTexture = 'res:/ui/Texture/classes/Menu/Icons/info.png'


class PlayGlyphIcon(ThemedGlyphIcon):
    default_frameTexture = 'res:/ui/Texture/classes/Menu/Icons/circleBG.png'
    default_glyphTexture = 'res:/ui/Texture/classes/Menu/Icons/play.png'


class QuestionMarkGlyphIcon(ThemedGlyphIcon):
    default_frameTexture = 'res:/ui/Texture/classes/Menu/Icons/circleBG.png'
    default_glyphTexture = 'res:/ui/Texture/classes/Menu/Icons/questionMark.png'
