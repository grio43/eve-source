#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation_new\hexes.py
import carbonui.const as uiconst
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui.loggers.buttonLogger import log_button_clicked
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from eve.client.script.ui import eveColor

class CCHexButtonMedium(Container):
    texture_0 = 'res:/UI/Texture/CharacterCreation/hexes/bloodlines.dds'
    textureInv_0 = 'res:/UI/Texture/CharacterCreation/hexes/bloodlinesInverted.dds'
    frameTexture = 'res:/UI/Texture/CharacterCreation/hexes/mediumHexFrame.dds'
    bgTexture = 'res:/UI/Texture/CharacterCreation/hexes/mediumHexBg.dds'
    bevelTexture = 'res:/UI/Texture/CharacterCreation/hexes/mediumHexBevel.dds'
    shawdowTexture = 'res:/UI/Texture/CharacterCreation/hexes/mediumHexShadow.dds'
    numColumns = 4
    hexPadWidth = 0
    hexPadHeight = 0
    wInterval = 64
    hInterval = 64
    rectW = 64
    rectH = 64
    shadowOffset = 1
    default_analyticID = ''

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.hint = self.hexName = attributes.hexName or ''
        self.info = attributes.info
        self.func = attributes.func
        self.id = attributes.id
        self.iconNum = attributes.iconNum
        self.showIcon = attributes.get('showIcon', 1)
        self.clickable = attributes.get('clickable', 1)
        self.showBg = self.clickable
        self.analyticID = attributes.get('analyticID', self.default_analyticID)
        self.SetupHex()

    def SetupHex(self, *args):
        textureNum, logoLocation = self.GetLogoLocation()
        normalCont = Container(name='normal', parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED)
        if self.showBg:
            sprite = Sprite(name='normalBg', parent=normalCont, align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath=self.bgTexture, padding=(-self.hexPadWidth,
             -self.hexPadHeight,
             -self.hexPadWidth,
             -self.hexPadHeight))
            sprite.SetRGBA(0.35, 0.35, 0.35, 0.3)
            sprite = Sprite(name='normalBevel', parent=normalCont, align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath=self.bevelTexture, padding=(-self.hexPadWidth,
             -self.hexPadHeight,
             -self.hexPadWidth,
             -self.hexPadHeight))
            sprite.SetAlpha(0.2)
            self.bevel = sprite
        if self.showIcon:
            sprite = Sprite(name='normalIcon', parent=normalCont, align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath=getattr(self, 'texture_%s' % textureNum, ''))
            sprite.rectLeft, sprite.rectTop, sprite.rectWidth, sprite.rectHeight = logoLocation
            sprite.SetAlpha(1.0)
            self.logo = sprite
            shadowOffset = getattr(self, 'shadowOffset', 3)
            sprite = Sprite(name='normalShadow', parent=normalCont, align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath=getattr(self, 'texture_%s' % textureNum, ''), padding=(shadowOffset,
             shadowOffset,
             -shadowOffset,
             -shadowOffset))
            sprite.rectLeft, sprite.rectTop, sprite.rectWidth, sprite.rectHeight = logoLocation
            sprite.SetRGBA(0.0, 0.0, 0.0, 0.3)
        self.normalCont = normalCont
        name = '%sFrame' % self.hexName
        sprite = Sprite(name=name, parent=self, align=uiconst.TOALL, state=uiconst.UI_HIDDEN, texturePath=self.frameTexture, padding=(-self.hexPadWidth,
         -self.hexPadHeight,
         -self.hexPadWidth,
         -self.hexPadHeight))
        sprite.SetAlpha(0.2)
        self.frame = sprite
        name = '%sSelection' % self.hexName
        selectionCont = Container(name='selectionCont', parent=self, align=uiconst.TOALL, state=uiconst.UI_HIDDEN)
        sprite = Sprite(name=name, parent=selectionCont, align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath=getattr(self, 'textureInv_%s' % textureNum, ''))
        sprite.rectLeft, sprite.rectTop, sprite.rectWidth, sprite.rectHeight = logoLocation
        sprite = Sprite(name=name, parent=selectionCont, align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath=getattr(self, 'textureInv_%s' % textureNum, ''), padding=(2, 2, -2, -2))
        sprite.rectLeft, sprite.rectTop, sprite.rectWidth, sprite.rectHeight = logoLocation
        sprite.SetRGBA(0.0, 0.0, 0.0, 0.3)
        self.selection = selectionCont
        if self.showBg:
            sprite = Sprite(name='shadow', parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath=self.shawdowTexture, padding=(-self.hexPadWidth,
             -self.hexPadHeight,
             -self.hexPadWidth,
             -self.hexPadHeight))
            sprite.SetAlpha(0.5)

    def OnClick(self, *args):
        if not self.clickable:
            return
        log_button_clicked(self)
        if self.func:
            self.func(self)

    def OnMouseEnter(self, *args):
        if not self.clickable:
            return
        PlaySound('ui_icc_button_mouse_over_play')
        if getattr(self, 'frame', None) is not None:
            self.frame.state = uiconst.UI_DISABLED
        if getattr(self, 'bevel', None) is not None:
            self.bevel.SetAlpha(0.5)

    def OnMouseExit(self, *args):
        if not self.clickable:
            return
        if getattr(self, 'frame', None) is not None:
            self.frame.state = uiconst.UI_HIDDEN
        if getattr(self, 'bevel', None) is not None:
            self.bevel.SetAlpha(0.2)

    def SelectHex(self, allConts = []):
        PlaySound('ui_icc_button_mouse_down_play')
        for c in allConts:
            c.normalCont.state = uiconst.UI_DISABLED
            c.frame.state = uiconst.UI_HIDDEN
            c.selection.state = uiconst.UI_HIDDEN

        self.normalCont.state = uiconst.UI_HIDDEN
        self.selection.state = uiconst.UI_DISABLED

    def GetLogoLocation(self, *args):
        iconNum = self.iconNum
        numInFile = pow(self.numColumns, 2)
        textureNum = iconNum / numInFile
        newIconNum = iconNum - numInFile * textureNum
        j = newIconNum / self.numColumns
        i = newIconNum % self.numColumns
        leftOffset = getattr(self, 'leftOffset', 0)
        topOffset = getattr(self, 'topOffset', 0)
        top = topOffset + j * self.hInterval
        left = leftOffset + i * self.wInterval
        return (textureNum, (left,
          top,
          self.rectW,
          self.rectH))


class CCHexButtonRace2(CCHexButtonMedium):
    __guid__ = 'uicls.CCHexButtonRace2'
    texture_0 = 'res:/UI/Texture/CharacterCreation/hexes/smallRaceGenderHexes.dds'
    textureInv_0 = 'res:/UI/Texture/CharacterCreation/hexes/smallRaceGenderHexesInverted.dds'
    frameTexture = 'res:/UI/Texture/CharacterCreation/hexes/mediumHexFrame.dds'
    bgTexture = 'res:/UI/Texture/CharacterCreation/hexes/mediumHexBg.dds'
    topOffset = 64


class CCHexButtonGender2(CCHexButtonMedium):
    __guid__ = 'uicls.CCHexButtonGender2'
    texture_0 = 'res:/UI/Texture/CharacterCreation/hexes/smallRaceGenderHexes.dds'
    textureInv_0 = 'res:/UI/Texture/CharacterCreation/hexes/smallRaceGenderHexesInverted.dds'


class CCHexButtonAncestry(CCHexButtonMedium):
    __guid__ = 'uicls.CCHexButtonAncestry'
    texture_0 = 'res:/UI/Texture/CharacterCreation/hexes/ancestries1.dds'
    textureInv_0 = 'res:/UI/Texture/CharacterCreation/hexes/ancestriesInverted1.dds'
    texture_1 = 'res:/UI/Texture/CharacterCreation/hexes/ancestries2.dds'
    textureInv_1 = 'res:/UI/Texture/CharacterCreation/hexes/ancestriesInverted2.dds'
    texture_2 = 'res:/UI/Texture/CharacterCreation/hexes/ancestries3.dds'
    textureInv_2 = 'res:/UI/Texture/CharacterCreation/hexes/ancestriesInverted3.dds'


class CCHexButtonSchool(CCHexButtonMedium):
    __guid__ = 'uicls.CCHexButtonSchool'
    texture_0 = 'res:/UI/Texture/CharacterCreation/hexes/ancestries3.dds'
    textureInv_0 = 'res:/UI/Texture/CharacterCreation/hexes/ancestriesInverted3.dds'
    topOffset = 192
    leftOffset = 64


class CCHexButtonHead(CCHexButtonMedium):
    __guid__ = 'uicls.CCHexButtonHead'
    texture_0 = ''
    textureInv_0 = 'res:/UI/Texture/CharacterCreation/headPickerBG.dds'
    frameTexture = 'res:/UI/Texture/CharacterCreation/headPickerFrame.dds'
    bgTexture = 'res:/UI/Texture/CharacterCreation/headPickerBG.dds'
    bevelTexture = 'res:/UI/Texture/CharacterCreation/headPickerBevel.dds'
    shawdowTexture = 'res:/UI/Texture/CharacterCreation/headPickerShadow.dds'
    numColumns = 1
    shadowOffset = 0
    default_analyticID = 'CCHexButtonHead'


class CCHexButtonBody(CCHexButtonMedium):
    __guid__ = 'uicls.CCHexButtonBody'
    texture_0 = ''
    textureInv_0 = 'res:/UI/Texture/CharacterCreation/bodyPickerBG.dds'
    frameTexture = 'res:/UI/Texture/CharacterCreation/bodyPickerFrame.dds'
    bgTexture = 'res:/UI/Texture/CharacterCreation/bodyPickerBG.dds'
    bevelTexture = 'res:/UI/Texture/CharacterCreation/bodyPickerBevel.dds'
    shawdowTexture = 'res:/UI/Texture/CharacterCreation/bodyPickerShadow.dds'
    numColumns = 1
    shadowOffset = 0
    wInterval = 128
    hInterval = 128
    rectW = 128
    rectH = 128
    default_analyticID = 'CCHexButtonBody'


class CCHexButtonRandomize(CCHexButtonMedium):
    __guid__ = 'uicls.CCHexButtonRandomize'
    texture_0 = 'res:/UI/Texture/CharacterCreation/randomize_arrows.png'
    numColumns = 1
    default_analyticID = 'CCHexButtonRandomize'

    def ApplyAttributes(self, attributes):
        super(CCHexButtonRandomize, self).ApplyAttributes(attributes)
        self.logo.padding = 5
        self.logo.SetRGBA(*eveColor.PRIMARY_BLUE)

    def StartBlinking(self):
        animations.BlinkIn(self.logo, startVal=0.5, endVal=1.2, duration=1.2, loops=-1, curveType=uiconst.ANIM_WAVE)

    def StopBlinking(self):
        self.logo.StopAnimations()
        self.logo.opacity = 1.0
