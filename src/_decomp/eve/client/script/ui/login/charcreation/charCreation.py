#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation\charCreation.py
import carbonui.const as uiconst
import uthread
import log
import localization
import charactercreator.const as ccConst
import blue
import trinity
import eve.common.lib.appConst as const
from carbon.common.script.util import timerstuff
from carbonui.primitives.container import Container
from carbonui.primitives.gradientSprite import GradientConst, GradientSprite
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from eve.client.script.ui.login.charcreation.hexes import CCHexButtonBody, CCHexButtonHead
FILL_SELECTION = 0.2
TEXT_NORMAL = 0.8
MINSIDESIZE = 280
MAXMENUSIZE = 380
CC_LEFT_SIZE = 180
ZONEMAP = {-1: uiconst.UICURSOR_DEFAULT,
 0: uiconst.UICURSOR_CCALLDIRECTIONS,
 1: uiconst.UICURSOR_CCALLDIRECTIONS,
 2: uiconst.UICURSOR_CCALLDIRECTIONS,
 3: uiconst.UICURSOR_CCALLDIRECTIONS,
 4: uiconst.UICURSOR_CCALLDIRECTIONS,
 5: uiconst.UICURSOR_CCALLDIRECTIONS,
 6: uiconst.UICURSOR_CCALLDIRECTIONS,
 7: uiconst.UICURSOR_CCALLDIRECTIONS,
 8: uiconst.UICURSOR_CCALLDIRECTIONS,
 9: uiconst.UICURSOR_CCALLDIRECTIONS,
 10: uiconst.UICURSOR_CCALLDIRECTIONS,
 11: uiconst.UICURSOR_CCALLDIRECTIONS,
 12: uiconst.UICURSOR_CCALLDIRECTIONS,
 13: uiconst.UICURSOR_CCALLDIRECTIONS,
 14: uiconst.UICURSOR_CCUPDOWN,
 15: uiconst.UICURSOR_CCALLDIRECTIONS,
 16: uiconst.UICURSOR_CCALLDIRECTIONS,
 17: uiconst.UICURSOR_CCLEFTRIGHT}
ZONEMAP_SIDE = {-1: uiconst.UICURSOR_DEFAULT,
 0: uiconst.UICURSOR_CCALLDIRECTIONS,
 1: uiconst.UICURSOR_CCALLDIRECTIONS,
 2: uiconst.UICURSOR_CCALLDIRECTIONS,
 3: uiconst.UICURSOR_CCALLDIRECTIONS,
 4: uiconst.UICURSOR_CCALLDIRECTIONS,
 5: uiconst.UICURSOR_CCALLDIRECTIONS,
 6: uiconst.UICURSOR_CCALLDIRECTIONS,
 7: uiconst.UICURSOR_CCALLDIRECTIONS,
 8: uiconst.UICURSOR_CCALLDIRECTIONS,
 9: uiconst.UICURSOR_CCALLDIRECTIONS,
 10: uiconst.UICURSOR_CCALLDIRECTIONS,
 11: uiconst.UICURSOR_CCALLDIRECTIONS,
 12: uiconst.UICURSOR_CCALLDIRECTIONS,
 13: uiconst.UICURSOR_CCALLDIRECTIONS,
 14: uiconst.UICURSOR_CCUPDOWN,
 15: uiconst.UICURSOR_CCALLDIRECTIONS,
 16: uiconst.UICURSOR_CCALLDIRECTIONS,
 17: uiconst.UICURSOR_DEFAULT}
ZONEMAP_ANIM = {-1: uiconst.UICURSOR_DEFAULT,
 0: uiconst.UICURSOR_CCHEADALL,
 1: uiconst.UICURSOR_CCHEADALL,
 2: uiconst.UICURSOR_CCHEADALL,
 3: uiconst.UICURSOR_CCALLDIRECTIONS,
 4: uiconst.UICURSOR_CCHEADTILT,
 5: uiconst.UICURSOR_CCALLDIRECTIONS,
 6: uiconst.UICURSOR_CCALLDIRECTIONS,
 7: uiconst.UICURSOR_CCHEADALL,
 8: uiconst.UICURSOR_CCHEADALL,
 9: uiconst.UICURSOR_CCALLDIRECTIONS,
 10: uiconst.UICURSOR_CCALLDIRECTIONS,
 11: uiconst.UICURSOR_CCHEADTILT,
 12: uiconst.UICURSOR_CCHEADALL,
 13: uiconst.UICURSOR_CCHEADALL,
 14: uiconst.UICURSOR_CCHEADALL,
 15: uiconst.UICURSOR_CCALLDIRECTIONS,
 16: uiconst.UICURSOR_CCALLDIRECTIONS,
 17: uiconst.UICURSOR_CCALLDIRECTIONS}
ZONEMAP_ANIMBODY = {-1: uiconst.UICURSOR_DEFAULT,
 3: uiconst.UICURSOR_CCSHOULDERTWIST,
 4: uiconst.UICURSOR_CCSHOULDERTWIST,
 5: uiconst.UICURSOR_CCSHOULDERTWIST,
 6: uiconst.UICURSOR_CCSHOULDERTWIST}
GHOST_TEXTURE_PATH = 'res:/UI/Texture/CharacterCreation/silhuette_ghost.dds'

class BaseCharacterCreationStep(Container):
    __notifyevents__ = ['OnHideUI', 'OnShowUI', 'OnUIScalingChange']
    default_align = uiconst.TOALL
    default_state = uiconst.UI_NORMAL
    racialHeader = {const.raceCaldari: 384,
     const.raceMinmatar: 128,
     const.raceAmarr: 256,
     const.raceGallente: 0}
    raceHeaderPath = 'res:/UI/Texture/CharacterCreation/RACE_Titletext.dds'
    raceFontColor = {const.raceCaldari: (0.93, 0.94, 0.99, 1.0),
     const.raceMinmatar: (0.99, 0.95, 0.95, 1.0),
     const.raceAmarr: (0.99, 0.95, 0.92, 1.0),
     const.raceGallente: (0.99, 0.99, 0.92, 1.0)}

    def ApplyAttributes(self, attributes):
        sm.RegisterNotify(self)
        Container.ApplyAttributes(self, attributes)
        self.charSvc = sm.GetService('character')
        self._cameraActive = False
        self._activeSculptZone = None
        self._didSculptMotion = False
        self._latestPickTime = None
        self.uiContainer = Container(name='uiContainer', parent=self, align=uiconst.TOALL)
        self.leftSide = Container(name='leftSide', parent=self.uiContainer, align=uiconst.TOLEFT_PROP, width=0.5)
        self.rightSide = Container(name='rightSide', parent=self.uiContainer, align=uiconst.TORIGHT_PROP, width=0.5)
        settings.user.ui.Get('assetMenuState', {ccConst.BODYGROUP: True})

    def GetInfo(self):
        return uicore.layer.charactercreation.controller.GetInfo()

    def ValidateStepComplete(self):
        return True

    def GetPickInfo(self, pos):
        layer = uicore.layer.charactercreation.controller
        layer.StartEditMode(mode='makeup', skipPickSceneReset=True, useThread=0)
        pickedMakeup = layer.PassMouseEventToSculpt('LeftDown', *pos)
        layer.StartEditMode(mode='hair', skipPickSceneReset=True, useThread=0)
        pickedHair = layer.PassMouseEventToSculpt('LeftDown', *pos)
        layer.StartEditMode(mode='bodyselect', skipPickSceneReset=True, useThread=0)
        pickedBody = layer.PassMouseEventToSculpt('LeftDown', *pos)
        layer.StartEditMode(mode='sculpt', skipPickSceneReset=True, useThread=0)
        pickedSculpt = layer.PassMouseEventToSculpt('LeftDown', *pos)
        reset = layer.PassMouseEventToSculpt('LeftUp', *pos)
        return (pickedMakeup,
         pickedHair,
         pickedBody,
         pickedSculpt)

    def OnMouseDown(self, btn, *args):
        if self.stepID not in (ccConst.CUSTOMIZATIONSTEP, ccConst.PORTRAITSTEP):
            return
        self.storedMousePos = None
        pos = (int(uicore.uilib.x * uicore.desktop.dpiScaling), int(uicore.uilib.y * uicore.desktop.dpiScaling))
        layer = uicore.layer.charactercreation.controller
        if btn == uiconst.MOUSERIGHT:
            self._cameraActive = True
            self._SetActiveSculptZone(None)
        elif btn == uiconst.MOUSELEFT and not self._cameraActive and self.charSvc.IsSculptingReady():
            self._didSculptMotion = False
            self._latestPickTime = blue.os.GetWallclockTime()
            if self.CanSculpt():
                layer.StartEditMode(mode='sculpt', callback=self.ChangeSculptingCursor)
                pickedSculpt = layer.PassMouseEventToSculpt('LeftDown', *pos)
                if pickedSculpt >= 0:
                    uicore.layer.charactercreation.controller.TryFreezeAnimation()
                    self.storedMousePos = (uicore.uilib.x, uicore.uilib.y)
                    self.cursor = uiconst.UICURSOR_NONE
                    self._cameraActive = False
                    self._SetActiveSculptZone(pickedSculpt)
                else:
                    self._cameraActive = True
                    self._SetActiveSculptZone(None)
            elif self.stepID == ccConst.PORTRAITSTEP:
                info = self.GetInfo()
                self.charSvc.StartPosing(info.charID, callback=self.ChangeSculptingCursor)
                pickedSculpt = layer.PassMouseEventToSculpt('LeftDown', *pos)
                if pickedSculpt >= 0:
                    self._cameraActive = False
                    self._SetActiveSculptZone(pickedSculpt)
                else:
                    self._cameraActive = True
                    self._SetActiveSculptZone(None)
            else:
                self._cameraActive = True
                self._SetActiveSculptZone(None)
        elif btn == uiconst.MOUSELEFT and self.stepID == ccConst.CUSTOMIZATIONSTEP and not layer.CanChangeBaseAppearance():
            self._cameraActive = True
        else:
            return
        uicore.uilib.ClipCursor(0, 0, uicore.desktop.width, uicore.desktop.height)
        uicore.uilib.SetCapture(self)

    def OnMouseUp(self, btn, *args):
        if self.stepID not in (ccConst.CUSTOMIZATIONSTEP, ccConst.PORTRAITSTEP):
            return
        uicore.layer.charactercreation.controller.UnfreezeAnimationIfNeeded()
        if getattr(self, 'storedMousePos', None) is not None:
            uicore.uilib.SetCursorPos(*self.storedMousePos)
            self.storedMousePos = None
        if btn == uiconst.MOUSELEFT:
            uicore.layer.charactercreation.controller.PassMouseEventToSculpt('LeftUp', uicore.uilib.x, uicore.uilib.y)
            if self.CanSculpt():
                if self._activeSculptZone is not None and self._didSculptMotion:
                    uicore.layer.charactercreation.controller.TryStoreDna(False, 'Sculpting', sculpting=True)
                    charID = uicore.layer.charactercreation.controller.GetInfo().charID
                    sm.ScatterEvent('OnDollUpdated', charID, False, 'sculpting')
                    self.charSvc.UpdateTattoos(charID)
                elif self._latestPickTime:
                    if blue.os.TimeDiffInMs(self._latestPickTime, blue.os.GetWallclockTime()) < 250.0:
                        pickedMakeup, pickedHair, pickedBody, pickedSculpt = self.GetPickInfo((uicore.uilib.x, uicore.uilib.y))
                        log.LogInfo('Pickinfo: makeup, hair, bodyselect, sculpt = ', pickedMakeup, pickedHair, pickedBody, pickedSculpt)
                        for each in (('hair', pickedHair),
                         ('makeup', pickedMakeup),
                         ('clothes', pickedBody),
                         ('sculpt', pickedSculpt)):
                            if each in ccConst.PICKMAPPING:
                                pickedModifier = ccConst.PICKMAPPING[each]
                                self.ExpandMenuByModifier(pickedModifier)
                                break

            self._SetActiveSculptZone(None)
        if not uicore.uilib.rightbtn and not uicore.uilib.leftbtn:
            uicore.layer.charactercreation.controller.PassMouseEventToSculpt('Motion', uicore.uilib.x, uicore.uilib.y)
            self._cameraActive = False
            self._SetActiveSculptZone(None)
            self.cursor = uiconst.UICURSOR_DEFAULT
            uicore.uilib.UnclipCursor()
            if uicore.uilib.GetCapture() is self:
                uicore.uilib.ReleaseCapture()

    def OnMouseMove(self, *args):
        if self.stepID not in (ccConst.CUSTOMIZATIONSTEP, ccConst.PORTRAITSTEP):
            return
        pos = (int(uicore.uilib.x * uicore.desktop.dpiScaling), int(uicore.uilib.y * uicore.desktop.dpiScaling))
        if self._cameraActive:
            if uicore.uilib.leftbtn and uicore.uilib.rightbtn:
                modifier = uicore.mouseInputHandler.GetCameraZoomModifier()
                uicore.layer.charactercreation.controller.camera.Dolly(modifier * uicore.uilib.dy)
            if uicore.uilib.leftbtn:
                uicore.layer.charactercreation.controller.camera.AdjustYaw(uicore.uilib.dx)
                if not uicore.uilib.rightbtn:
                    uicore.layer.charactercreation.controller.camera.AdjustPitch(uicore.uilib.dy)
            elif uicore.uilib.rightbtn:
                uicore.layer.charactercreation.controller.camera.Pan(uicore.uilib.dx, uicore.uilib.dy)
        else:
            if self._activeSculptZone is not None and self.stepID == ccConst.CUSTOMIZATIONSTEP:
                uicore.layer.charactercreation.controller.CheckDnaLog('OnMouseMove')
                self._didSculptMotion = True
            uicore.layer.charactercreation.controller.PassMouseEventToSculpt('Motion', *pos)

    def OnMouseWheel(self, *args):
        if not uicore.layer.charactercreation.controller.camera:
            return
        modifier = uicore.mouseInputHandler.GetCameraZoomModifier()
        uicore.layer.charactercreation.controller.camera.Dolly(modifier * -uicore.uilib.dz)

    def ChangeSculptingCursor(self, zone, isFront, isHead):
        if self.destroyed:
            return
        if self.stepID == ccConst.CUSTOMIZATIONSTEP:
            if isFront:
                cursor = ZONEMAP.get(zone, uiconst.UICURSOR_DEFAULT)
            else:
                cursor = ZONEMAP_SIDE.get(zone, uiconst.UICURSOR_DEFAULT)
            self.cursor = cursor
        elif self.stepID == ccConst.PORTRAITSTEP:
            if isHead:
                cursor = ZONEMAP_ANIM.get(zone, uiconst.UICURSOR_DEFAULT)
            else:
                cursor = ZONEMAP_ANIMBODY.get(zone, uiconst.UICURSOR_DEFAULT)
            self.cursor = cursor
        lastZone = getattr(self, '_lastZone', None)
        if lastZone != zone:
            sm.StartService('audio').SendUIEvent(unicode('ui_icc_sculpting_mouse_over_loop_play'))
            self._lastZone = zone
            if self._lastZone == -1:
                sm.StartService('audio').SendUIEvent(unicode('ui_icc_sculpting_mouse_over_loop_stop'))

    def ExpandMenuByModifier(self, modifier):
        from eve.client.script.ui.login.charcreation.assetMenu import CharCreationAssetPicker
        if not self.assetMenu:
            return
        lastParentGroup = None
        allMenus = [ each for each in self.assetMenu.mainContainter.children if isinstance(each, CharCreationAssetPicker) ]
        for menu in allMenus:
            if not menu.isSubmenu:
                lastParentGroup = menu
            if getattr(menu, 'modifier', None) == modifier:
                if lastParentGroup and not lastParentGroup.IsExpanded():
                    uthread.new(lastParentGroup.Expand)
                uthread.new(menu.Expand)

    def OnHideUI(self, *args):
        self.uiContainer.state = uiconst.UI_HIDDEN

    def OnShowUI(self, *args):
        self.uiContainer.state = uiconst.UI_PICKCHILDREN

    def CanSculpt(self, *args):
        return self.stepID == ccConst.CUSTOMIZATIONSTEP and uicore.layer.charactercreation.controller.CanChangeBaseAppearance() and getattr(self, 'menuMode', None) != getattr(self, 'TATTOOMENU', None)

    def IsDollReady(self, *args):
        if uicore.layer.charactercreation.controller.doll is None:
            return False
        return not uicore.layer.charactercreation.controller.doll.busyUpdating

    def GetViewportForPicking(self):
        return trinity.device.viewport

    def _SetActiveSculptZone(self, sculptZone):
        self._activeSculptZone = sculptZone


class CCHeadBodyPicker(Container):
    default_name = 'CCHeadBodyPicker'
    default_opacity = 0
    default_width = 130
    default_height = 130

    def ApplyAttributes(self, attributes):
        super(CCHeadBodyPicker, self).ApplyAttributes(attributes)
        self.headCallback = attributes.headCallback
        self.bodyCallback = attributes.bodyCallback
        self.ConstructLayout()
        self.updateTimer = timerstuff.AutoTimer(33, self.UpdatePosition)
        animations.FadeIn(self, duration=0.25)

    def ConstructLayout(self, *args):
        self.headHex = CCHexButtonHead(name='headHex', parent=self, align=uiconst.CENTERTOP, state=uiconst.UI_NORMAL, pos=(0, 0, 64, 64), pickRadius=21, info=None, id=0, hexName=localization.GetByLabel('UI/CharacterCreation/ZoomIn'), func=self.HeadClicked, iconNum=0, showIcon=False)
        self.headSolid = self.headHex.selection
        self.headSolid.SetState(uiconst.UI_DISABLED)
        self.headFrame = self.headHex.frame
        self.bodyHex = CCHexButtonBody(name='bodyHex', parent=self, align=uiconst.CENTERTOP, state=uiconst.UI_NORMAL, pos=(0, 16, 128, 128), pickRadius=42, info=None, id=0, hexName=localization.GetByLabel('UI/CharacterCreation/ZoomOut'), func=self.BodyClicked, iconNum=0, showIcon=False)
        self.bodySolid = self.bodyHex.selection
        self.bodySolid.SetState(uiconst.UI_DISABLED)
        self.bodyFrame = self.bodyHex.frame
        sprite = Sprite(name='ghostSprite', parent=self, align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED, pos=(0, 7, 128, 128), idx=0, texturePath=GHOST_TEXTURE_PATH)
        sprite.SetRect(0, 0, 0, 0)

    def UpdatePosition(self, *args):
        if self.destroyed:
            return
        camera = getattr(uicore.layer.charactercreation.controller, 'camera', None)
        if camera is not None:
            portion = camera.GetPortionFromDistance()
            self.headSolid.SetOpacity(max(0.2, 1.0 - portion))
            self.bodySolid.SetOpacity(max(0.2, portion))
            for hex in (self.headHex, self.bodyHex):
                if hex.selection.opacity >= 0.5 and len(self.children) and hex == self.children[-1]:
                    toSwap = self.children[-2]
                    self.children.remove(toSwap)
                    self.children.append(toSwap)
                    break

    def MouseOverPart(self, frameName, *args):
        sm.StartService('audio').SendUIEvent(unicode('ui_icc_button_mouse_over_play'))
        frame = self.get(frameName, None)
        if frame:
            frame.state = uiconst.UI_DISABLED

    def MouseExitPart(self, frameName, *args):
        frame = self.get(frameName, None)
        if frame:
            frame.state = uiconst.UI_HIDDEN

    def HeadClicked(self, *args):
        sm.StartService('audio').SendUIEvent(unicode('ui_icc_button_mouse_down_play'))
        self.headFrame.state = uiconst.UI_HIDDEN
        self.bodyFrame.state = uiconst.UI_HIDDEN
        if self.headCallback:
            self.headCallback()

    def BodyClicked(self, *args):
        sm.StartService('audio').SendUIEvent(unicode('ui_icc_button_mouse_down_play'))
        self.headFrame.state = uiconst.UI_HIDDEN
        self.bodyFrame.state = uiconst.UI_HIDDEN
        if self.bodyCallback:
            self.bodyCallback()


class BitSlider(Container):
    default_name = 'BitSlider'
    default_align = uiconst.RELATIVE
    default_bitWidth = 3
    default_bitHeight = 8
    default_bitGap = 1
    default_state = uiconst.UI_NORMAL
    default_left = 0
    default_top = 0
    default_width = 128
    default_height = 12
    cursor = uiconst.UICURSOR_SELECT

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.onSetValueCallback = None
        targetWidth = attributes.get('sliderWidth', 100)
        bitGap = attributes.get('bitGap', self.default_bitGap)
        bitAmount = attributes.bitAmount
        self.bitHeight = attributes.bitHeight or self.default_bitHeight
        self.height = self.bitHeight + 4
        if bitAmount:
            self.bitWidth = int(targetWidth / float(bitAmount))
        else:
            self.bitWidth = attributes.bitWidth or self.default_bitWidth
        self._value = 0.0
        self.bitParent = Container(parent=self, pos=(0,
         0,
         targetWidth,
         self.height), align=uiconst.TOPLEFT)
        self.handle = Container(parent=self.bitParent, align=uiconst.RELATIVE, state=uiconst.UI_DISABLED, pos=(0,
         0,
         3,
         self.height), bgColor=ccConst.COLOR + (1.0,))
        i = 0
        while True:
            if bitAmount is None and i >= 3 and i * (self.bitWidth + bitGap) + self.bitWidth > targetWidth:
                break
            bit = Container(parent=self.bitParent, pos=(i * (self.bitWidth + bitGap),
             2,
             self.bitWidth,
             self.bitHeight), align=uiconst.RELATIVE, state=uiconst.UI_DISABLED, bgColor=ccConst.COLOR + (1.0,))
            bit.isBit = True
            i += 1
            if bitAmount is not None and i == bitAmount:
                break

        self._numBits = i
        if targetWidth != bit.left + bit.width:
            diff = targetWidth - (bit.left + bit.width)
            bit.width += diff
        self.bitParent.width = targetWidth
        self.width = targetWidth
        if attributes.setvalue is not None:
            self.SetValue(attributes.setvalue)
        self.onSetValueCallback = attributes.OnSetValue

    def OnMouseDown(self, mouseBtn, *args):
        if mouseBtn != uiconst.MOUSELEFT:
            return
        self.softSlideTimer = None
        self.slideTimer = timerstuff.AutoTimer(33, self.UpdateSliderPortion)

    def OnMouseEnter(self, *args):
        self.softSlideTimer = timerstuff.AutoTimer(33, self.UpdateSoftSliderPortion)

    def OnMouseExit(self, *args):
        pass

    def OnMouseWheel(self, *args):
        if uicore.uilib.dz > 0:
            self.SetValue(self.GetValue() + 1.0 / self._numBits)
        else:
            self.SetValue(self.GetValue() - 1.0 / self._numBits)

    def UpdateSoftSliderPortion(self, *args):
        if uicore.uilib.mouseOver is self or uicore.uilib.mouseOver.IsUnder(self):
            l, t, w, h = self.bitParent.GetAbsolute()
            portion = max(0.0, min(1.0, (uicore.uilib.x - l) / float(w)))
            self.ShowSoftLit(portion)
        else:
            self.softSlideTimer = None
            self.ShowSoftLit(0.0)

    def UpdateSliderPortion(self, *args):
        l, t, w, h = self.bitParent.GetAbsolute()
        portion = max(0.0, min(1.0, (uicore.uilib.x - l) / float(w)))
        self.handle.left = int((w - self.bitWidth) * portion)
        self.ShowLit(portion)

    def OnMouseUp(self, mouseBtn, *args):
        if mouseBtn != uiconst.MOUSELEFT:
            return
        self.slideTimer = None
        l, t, w, h = self.bitParent.GetAbsolute()
        portion = max(0.0, min(1.0, (uicore.uilib.x - l) / float(w)))
        self.handle.left = int((w - self.handle.width) * portion)
        self.SetValue(portion)

    def ShowLit(self, portion):
        l, t, w, h = self.bitParent.GetAbsolute()
        if not w:
            return
        self.handle.left = int((w - self.handle.width) * portion)
        for each in self.bitParent.children:
            if not hasattr(each, 'isBit'):
                continue
            mportion = max(0.0, min(1.0, (each.left + each.width / 2) / float(w)))
            if portion > mportion:
                each.SetOpacity(1.0)
            else:
                each.SetOpacity(0.333)

    def ShowSoftLit(self, portion):
        l, t, w, h = self.bitParent.GetAbsolute()
        for each in self.bitParent.children:
            if not hasattr(each, 'isBit'):
                continue
            if each.opacity == 1.0:
                continue
            mportion = max(0.0, min(1.0, (each.left + each.width / 2) / float(w)))
            if portion > mportion:
                each.SetOpacity(0.5)
            else:
                each.SetOpacity(0.333)

    def SetValue(self, value, doCallback = True):
        callback = value != self._value
        self._value = max(0.0, min(1.0, value))
        self.ShowLit(self._value)
        if callback and doCallback and self.onSetValueCallback:
            self.onSetValueCallback(self)

    def GetValue(self):
        return self._value


class GradientSlider(Container):
    default_name = 'GradientSlider'
    default_align = uiconst.RELATIVE
    default_bitWidth = 3
    default_bitHeight = 8
    default_bitGap = 1
    default_state = uiconst.UI_NORMAL
    default_left = 0
    default_top = 0
    default_width = 128
    default_height = 12
    cursor = uiconst.UICURSOR_SELECT

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.onSetValueCallback = None
        targetWidth = attributes.get('sliderWidth', 100)
        bitHeight = attributes.bitHeight or self.default_bitHeight
        self.height = bitHeight + 4
        self._value = 0.0
        self.handle = Container(parent=self, align=uiconst.RELATIVE, state=uiconst.UI_DISABLED, pos=(0,
         -2,
         3,
         self.height + 4), bgColor=ccConst.COLOR + (1.0,))
        if attributes.get('alphaValues'):
            alphaValues = attributes.get('alphaValues')
            rgbValues = [(0, (0, 0, 0))]
        else:
            alphaValues = (1, 1)
            rgbValues = [(0, (0, 0, 0)), (1.0, (1, 1, 1))]
        self.gradientSprite = GradientSprite(parent=self, pos=(0,
         0,
         targetWidth,
         self.height), rgbData=rgbValues, alphaData=[alphaValues, (1.0, 1.0)], alphaInterp=GradientConst.INTERP_LINEAR, colorInterp=GradientConst.INTERP_LINEAR, state=uiconst.UI_DISABLED)
        self.gradientSprite.width = targetWidth
        if attributes.setvalue is not None:
            self.SetValue(attributes.setvalue)
        self.onSetValueCallback = attributes.OnSetValue
        self.ChangeGradientColor(secondColor=(1.0, (1, 1, 0)))

    def OnMouseDown(self, mouseBtn, *args):
        if mouseBtn != uiconst.MOUSELEFT:
            return
        self.slideTimer = timerstuff.AutoTimer(33, self.UpdateSliderPortion)

    def UpdateSliderPortion(self, *args):
        l, t, w, h = self.gradientSprite.GetAbsolute()
        portion = max(0.0, min(1.0, (uicore.uilib.x - l) / float(w)))
        self.handle.left = int(w * portion)

    def OnMouseUp(self, mouseBtn, *args):
        if mouseBtn != uiconst.MOUSELEFT:
            return
        self.slideTimer = None
        l, t, w, h = self.gradientSprite.GetAbsolute()
        portion = max(0.0, min(1.0, (uicore.uilib.x - l) / float(w)))
        self.handle.left = int(w * portion)
        self.SetValue(portion)

    def SetValue(self, value, doCallback = True):
        callback = value != self._value
        self._value = max(0.0, min(1.0, value))
        self.SetHandle(self._value)
        if callback and doCallback and self.onSetValueCallback:
            self.onSetValueCallback(self)

    def SetHandle(self, portion):
        l, t, w, h = self.gradientSprite.GetAbsolute()
        if not w:
            return
        self.handle.left = int((w - self.handle.width) * portion)

    def GetValue(self):
        return self._value

    def ChangeGradientColor(self, firstColor = None, secondColor = None):
        colorData = self.gradientSprite.colorData
        if len(colorData) < 2:
            firstColor = secondColor
        if firstColor is not None:
            colorData[0] = firstColor
        if secondColor is not None and len(colorData) > 1:
            colorData[1] = secondColor
        self.gradientSprite.SetGradient()
