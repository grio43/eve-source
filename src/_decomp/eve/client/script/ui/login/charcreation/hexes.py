#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation\hexes.py
import math
import operator
import blue
import carbonui.const as uiconst
import charactercreator.const as ccConst
import localization
import uthread
import utillib
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from eve.client.script.ui import eveColor
from eve.client.script.ui.login.charcreation.label import CCLabel
FILL_MOUSEOVER = 0.1
FILL_SELECTION = 0.2
TEXT_MOUSEOVER = 0.6
TEXT_SELECTION = 1.0
TEXT_NORMAL = 0.8

class CCGenderPicker(Container):
    default_name = 'CCRacePicker'
    default_width = 145
    default_height = 90
    hexHeight = 64
    hexWidth = 64

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.isActive = 0
        self.cookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEUP, self._OnGlobalMouseUp)
        self.showText = attributes.showText
        self.genderID = attributes.genderID
        self.clickable = attributes.get('clickable', 1)
        self.disabledHex = attributes.get('disabledHex', [])
        self.padValue = -16
        self.padding2 = -int(math.sqrt(math.pow(self.padValue, 2) + math.pow(0.5 * self.padValue, 2))) - 2
        self.PrepareInfo()
        self.Setup()

    def Setup(self, *args):
        self.genderCont = Container(name='genderCont', parent=self, pos=(0,
         0,
         200,
         int(1.5 * self.hexHeight)), align=uiconst.TOPLEFT)
        self.CreateGenderHex()
        if self.showText:
            if self.genderID is not None:
                if self.genderID:
                    genderText = localization.GetByLabel('UI/Common/Gender/Male')
                else:
                    genderText = localization.GetByLabel('UI/Common/Gender/Female')
                text = localization.GetByLabel('UI/CharacterCreation/GenderAndGenderName', genderName=genderText)
                genderTextCont = Container(name='genderTextCont', parent=self.genderCont, text=text, pos=(0,
                 int(0.5 * (16 + self.hexHeight)),
                 0,
                 self.hexHeight), align=uiconst.TOTOP)
                CCLabel(parent=genderTextCont, fontsize=12, align=uiconst.CENTERLEFT, text=text, letterspace=1, left=self.hexWidth + 20, bold=0, color=ccConst.COLOR50)

    def CreateGenderHex(self, *args):
        offsetMap = {0: (0, int(0.5 * (self.hexHeight + self.padValue))),
         1: (self.hexWidth + self.padding2, 0)}
        self.AddGenderHex(offsetMap, self.hexWidth, self.hexHeight, self.currentGenderInfo)
        self.ChangeStateOfAlmostAllConts(self.genderConts, uiconst.UI_HIDDEN, [self.genderID])
        self.SelectHex(self.genderConts.get(self.genderID), [])

    def AddGenderHex(self, offsetMap, width, height, genderInfo, state = uiconst.UI_NORMAL, *args):
        self.genderConts = {}
        isClickable = self.clickable and 'gender' not in self.disabledHex
        for i, info in enumerate(genderInfo):
            id = info.get('genderID', 0)
            gender = info.get('text', 0)
            left, top = offsetMap.get(i, (0, 0))
            hex = CCHexButtonGender2(name='genderHex', parent=self.genderCont, align=uiconst.TOPLEFT, state=state, pos=(left,
             top,
             width,
             height), pickRadius=int(height / 2.0), info=info, id=id, hexName=gender, func=self.OnGenderClicked, iconNum=id, clickable=isClickable)
            self.genderConts[id] = hex

    def OnHexMouseOver(self, cont, *args):
        sm.StartService('audio').SendUIEvent(unicode('ui_icc_button_mouse_over_play'))
        if getattr(cont, 'frame', None) is not None:
            cont.frame.state = uiconst.UI_DISABLED

    def OnHexMouseExit(self, cont, *args):
        if getattr(cont, 'frame', None) is not None:
            cont.frame.state = uiconst.UI_HIDDEN

    def _AnimateHexList(self, containerList, time = 100.0, attribute = 'left'):
        containerList.sort(key=operator.attrgetter(attribute))
        for cont in containerList:
            cont.state = uiconst.UI_NORMAL
            blue.pyos.synchro.SleepWallclock(time)

    def SelectHex(self, cont, allConts):
        sm.StartService('audio').SendUIEvent(unicode('ui_icc_button_mouse_down_play'))
        for c in allConts:
            c.normalCont.state = uiconst.UI_DISABLED
            c.selection.state = uiconst.UI_HIDDEN

        self.SetSelectionState(cont, on=0)

    def PrepareInfo(self, *args):
        self.currentGenderInfo = [utillib.KeyVal(genderID=0, text=localization.GetByLabel('UI/Common/Gender/Female')), utillib.KeyVal(genderID=1, text=localization.GetByLabel('UI/Common/Gender/Male'))]
        self.RearrangeInfo(self.genderID, 'genderID', self.currentGenderInfo)

    def RearrangeInfo(self, id, what, info, *args):
        selectedIdx = None
        for i, each in enumerate(info):
            if getattr(each, what, '') == id:
                selectedIdx = i
                break

        if selectedIdx is not None:
            currentPick = info[selectedIdx]
            oldPick = info[0]
            info[selectedIdx] = oldPick
            info[0] = currentPick

    def OnGenderClicked(self, cont, *args):
        info = uicore.layer.charactercreation.controller.GetInfo()
        if info.charID or not self.clickable:
            return
        newGenderID = cont.info.get('genderID', 0)
        if newGenderID == self.genderID:
            self.ClickingOnCurrent(self.genderID, cont, self.genderConts, what=['gender'])
        else:
            dnaLog = uicore.layer.charactercreation.controller.GetDollDNAHistory()
            if dnaLog and len(dnaLog) > 1:
                if eve.Message('CharCreationLoseChangeGender', {}, uiconst.YESNO) != uiconst.ID_YES:
                    return
            self.isActive = 1
            self.Disable()
            self.SwitchGender(newGenderID)
            self.Enable()

    def SwitchGender(self, newGenderID, *args):
        uicore.layer.charactercreation.controller.FadeToBlack(why=localization.GetByLabel('UI/Common/Loading'))
        sm.GetService('character').StopEditing()
        self.genderID = newGenderID
        self.genderCont.Flush()
        self.RearrangeInfo(self.genderID, 'genderID', self.currentGenderInfo)
        self.CreateGenderHex()
        self.SelectHex(self.genderConts.get(self.genderID), [])
        info = uicore.layer.charactercreation.controller.GetInfo()
        sm.GetService('character').RemoveCharacter(info.charID)
        uicore.layer.charactercreation.controller.AddCharacter(info.charID, info.bloodlineID, info.raceID, newGenderID)
        uicore.layer.charactercreation.controller.SelectGender(self.genderID, check=0)
        uicore.layer.charactercreation.controller.StartEditMode(mode='sculpt', resetAll=True)
        if hasattr(uicore.layer.charactercreation.controller.step, 'LoadFaceMode'):
            uthread.new(uicore.layer.charactercreation.controller.step.LoadFaceMode)
        uicore.layer.charactercreation.controller.FadeFromBlack()

    def ClickingOnCurrent(self, id, cont, allConts, animate = False, what = [], *args):
        self.isActive = 1
        expanded = getattr(cont, 'expanded', 0)
        if expanded:
            opacity = 1.0
            selectionOn = 0
        else:
            opacity = 0.3
            selectionOn = 1
        cont.opacity = 1.0
        self.SetSelectionState(cont, on=selectionOn)
        self.ChangeHexOpacity(self.GetMainHexes(exceptWhat=what).values(), opacity=opacity)
        newState = [uiconst.UI_NORMAL, uiconst.UI_HIDDEN][expanded]
        self.ChangeStateOfAlmostAllConts(allConts, newState, [id], animate=True)
        cont.expanded = not expanded

    def GetMainHexes(self, exceptWhat = [], *args):
        mainHexes = {text:cont for text, cont in [('gender', self.genderConts.get(self.genderID, None))] if text not in exceptWhat}
        return mainHexes

    def ChangeStateOfAlmostAllConts(self, allConts, newState, exceptIDs = [], animate = False):
        changed = []
        doAnimation = animate and newState == uiconst.UI_NORMAL
        for id, cont in allConts.iteritems():
            if id in exceptIDs:
                if newState == uiconst.UI_HIDDEN:
                    cont.expanded = False
                continue
            if not doAnimation:
                cont.state = newState
            changed.append(cont)

        if doAnimation:
            self.AnimateHexes(changed)
        return changed

    def AnimateHexes(self, changedConts, *args):
        for cont in changedConts:
            cont.state = uiconst.UI_HIDDEN

        uthread.new(self._AnimateHexesThread, changedConts, attribute='top')

    def _AnimateHexesThread(self, changedConts, attribute, time = 100.0, *args):
        self._AnimateHexList(changedConts, time=time, attribute=attribute)

    def SetSelectionState(self, cont, on = 1):
        if not cont:
            return
        if on:
            cont.normalCont.state = uiconst.UI_HIDDEN
            cont.selection.state = uiconst.UI_DISABLED
        else:
            cont.normalCont.state = uiconst.UI_DISABLED
            cont.selection.state = uiconst.UI_HIDDEN

    def CloseAllExtraHexes(self, *args):
        self.ChangeStateOfAlmostAllConts(self.genderConts, uiconst.UI_HIDDEN, [self.genderID], animate=False)
        self.ChangeHexOpacity(self.GetMainHexes().values(), opacity=1.0)

    def Disable(self, *args):
        self.state = uiconst.UI_DISABLED
        self.opacity = 0.3

    def Enable(self, *args):
        self.state = uiconst.UI_PICKCHILDREN
        self.opacity = 1.0
        self.ChangeHexOpacity(self.GetMainHexes().values(), opacity=1.0)

    def ChangeHexOpacity(self, hexes, opacity = 1.0):
        for h in hexes:
            h.opacity = opacity
            self.SetSelectionState(h, 0)

    def _OnGlobalMouseUp(self, obj, *args):
        if self.isActive and not isinstance(obj, CCHexButtonMedium):
            self.CloseAllExtraHexes()
            self.isActive = False
        return 1

    def _OnClose(self, *args):
        uicore.event.UnregisterForTriuiEvents(self.cookie)


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
    texture_0 = 'res:/UI/Texture/CharacterCreation/hexes/smallRaceGenderHexes.dds'
    textureInv_0 = 'res:/UI/Texture/CharacterCreation/hexes/smallRaceGenderHexesInverted.dds'
    frameTexture = 'res:/UI/Texture/CharacterCreation/hexes/mediumHexFrame.dds'
    bgTexture = 'res:/UI/Texture/CharacterCreation/hexes/mediumHexBg.dds'
    topOffset = 64


class CCHexButtonGender2(CCHexButtonMedium):
    texture_0 = 'res:/UI/Texture/CharacterCreation/hexes/smallRaceGenderHexes.dds'
    textureInv_0 = 'res:/UI/Texture/CharacterCreation/hexes/smallRaceGenderHexesInverted.dds'


class CCHexButtonAncestry(CCHexButtonMedium):
    texture_0 = 'res:/UI/Texture/CharacterCreation/hexes/ancestries1.dds'
    textureInv_0 = 'res:/UI/Texture/CharacterCreation/hexes/ancestriesInverted1.dds'
    texture_1 = 'res:/UI/Texture/CharacterCreation/hexes/ancestries2.dds'
    textureInv_1 = 'res:/UI/Texture/CharacterCreation/hexes/ancestriesInverted2.dds'
    texture_2 = 'res:/UI/Texture/CharacterCreation/hexes/ancestries3.dds'
    textureInv_2 = 'res:/UI/Texture/CharacterCreation/hexes/ancestriesInverted3.dds'


class CCHexButtonSchool(CCHexButtonMedium):
    texture_0 = 'res:/UI/Texture/CharacterCreation/hexes/ancestries3.dds'
    textureInv_0 = 'res:/UI/Texture/CharacterCreation/hexes/ancestriesInverted3.dds'
    topOffset = 192
    leftOffset = 64


class CCHexButtonHead(CCHexButtonMedium):
    texture_0 = ''
    textureInv_0 = 'res:/UI/Texture/CharacterCreation/headPickerBG.dds'
    frameTexture = 'res:/UI/Texture/CharacterCreation/headPickerFrame.dds'
    bgTexture = 'res:/UI/Texture/CharacterCreation/headPickerBG.dds'
    bevelTexture = 'res:/UI/Texture/CharacterCreation/headPickerBevel.dds'
    shawdowTexture = 'res:/UI/Texture/CharacterCreation/headPickerShadow.dds'
    numColumns = 1
    shadowOffset = 0


class CCHexButtonBody(CCHexButtonMedium):
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


class CCHexButtonRandomize(CCHexButtonMedium):
    __guid__ = 'uicls.CCHexButtonRandomize'
    texture_0 = 'res:/UI/Texture/CharacterCreation/randomize_arrows.png'
    numColumns = 1

    def ApplyAttributes(self, attributes):
        super(CCHexButtonRandomize, self).ApplyAttributes(attributes)
        self.logo.padding = 5
        self.logo.SetRGBA(*eveColor.PRIMARY_BLUE)

    def StartBlinking(self):
        animations.BlinkIn(self.logo, startVal=0.5, endVal=1.2, duration=1.2, loops=-1, curveType=uiconst.ANIM_WAVE)

    def StopBlinking(self):
        self.logo.StopAnimations()
        self.logo.opacity = 1.0
