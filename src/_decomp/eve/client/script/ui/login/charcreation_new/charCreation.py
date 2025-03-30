#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation_new\charCreation.py
import carbonui.const as uiconst
import uthread
import log
import charactercreator.const as ccConst
import blue
import trinity
import eve.common.lib.appConst as const
from carbonui.primitives.container import Container
from carbonui.uicore import uicore
from eve.client.script.ui.login.charcreation_new.assetPicker import CharCreationAssetPicker
from eve.client.script.ui.login.charcreation_new.sceneManager import GetCharacterCreationSceneManager
from eve.client.script.ui.login.charcreation_new.dollManager import GetCharacterCreationDollManager
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
    __guid__ = 'uicls.BaseCharacterCreationStep'
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
        if self.stepID in (ccConst.CUSTOMIZATIONSTEP, ccConst.PORTRAITSTEP):
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
        if self.stepID in (ccConst.CUSTOMIZATIONSTEP, ccConst.PORTRAITSTEP):
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
        ccSceneManager = GetCharacterCreationSceneManager()
        if self._cameraActive:
            if uicore.uilib.leftbtn and uicore.uilib.rightbtn:
                modifier = uicore.mouseInputHandler.GetCameraZoomModifier()
                ccSceneManager.camera.Dolly(modifier * uicore.uilib.dy)
            if uicore.uilib.leftbtn:
                ccSceneManager.camera.AdjustYaw(uicore.uilib.dx)
                if not uicore.uilib.rightbtn:
                    ccSceneManager.camera.AdjustPitch(uicore.uilib.dy)
            elif uicore.uilib.rightbtn:
                ccSceneManager.camera.Pan(uicore.uilib.dx, uicore.uilib.dy)
        else:
            if self._activeSculptZone is not None and self.stepID == ccConst.CUSTOMIZATIONSTEP:
                GetCharacterCreationDollManager().CheckDnaLog()
                self._didSculptMotion = True
            uicore.layer.charactercreation.controller.PassMouseEventToSculpt('Motion', *pos)

    def OnMouseWheel(self, *args):
        ccSceneManager = GetCharacterCreationSceneManager()
        if not ccSceneManager.camera:
            return
        modifier = uicore.mouseInputHandler.GetCameraZoomModifier()
        ccSceneManager.camera.Dolly(modifier * -uicore.uilib.dz)

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
        info = self.GetInfo()
        ccDollManager = GetCharacterCreationDollManager()
        if ccDollManager.GetDoll(info.charID) is None:
            return False
        return not ccDollManager.GetDoll(info.charID).busyUpdating

    def GetViewportForPicking(self):
        return trinity.device.viewport

    def _SetActiveSculptZone(self, sculptZone):
        self._activeSculptZone = sculptZone
