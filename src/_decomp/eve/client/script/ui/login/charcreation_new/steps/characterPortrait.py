#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation_new\steps\characterPortrait.py
from carbon.common.script.util import timerstuff
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.util.various_unsorted import MapIcon
from charactercreator import const as ccConst
from eve.client.script.ui.control import eveIcon, eveLabel
from carbonui.control.button import Button
from eve.client.script.ui.login.charcreation_new.charCreation import BaseCharacterCreationStep, MAXMENUSIZE
from eve.client.script.ui.login.charcreation_new.assetMenu import CharCreationAssetMenu
from eve.client.script.ui.login.charcreation_new.colorPalette import CCColorPalette
from eve.client.script.ui.login.charcreation_new.portraitManager import GetCharacterCreationPortraitManager
from evegraphics import settings as gfxsettings
import localization
from carbonui.uicore import uicore

class CharacterPortrait(BaseCharacterCreationStep):
    __notifyevents__ = BaseCharacterCreationStep.__notifyevents__
    __notifyevents__ += ['OnGraphicSettingsChanged']
    stepID = ccConst.PORTRAITSTEP

    def ApplyAttributes(self, attributes):
        BaseCharacterCreationStep.ApplyAttributes(self, attributes)
        self.colorPaletteWidth = CCColorPalette.COLORPALETTEWIDTH
        self.portraitSize = 128
        self.selectedPortrait = 0
        self.portraitAssetMenu = None
        self.portraitCont = None
        self.assetMenuPar = Container(parent=self.rightSide, pos=(20,
         115,
         MAXMENUSIZE,
         uicore.desktop.height), state=uiconst.UI_PICKCHILDREN, align=uiconst.TORIGHT)
        self.hintBox = Container(parent=self.assetMenuPar, pos=(MAXMENUSIZE,
         40,
         200,
         150), align=uiconst.TOPRIGHT, state=uiconst.UI_DISABLED)
        self.hintText = eveLabel.EveLabelMedium(text='', parent=self.hintBox, align=uiconst.TOTOP)
        self.UpdateLayout()

    def UpdateLayout(self):
        self.ReloadPortraitAssetMenu()
        self.ReloadPortraits()
        self.hintBox.left = self.assetMenuMainWidth + 20

    def ReloadPortraitAssetMenu(self):
        sm.GetService('cc').LogInfo('CharacterPortrait::ReloadPortraitAssetMenu')
        if self.portraitAssetMenu:
            self.portraitAssetMenu.Close()
        groups = [(ccConst.BACKGROUNDGROUP, ()), (ccConst.POSESGROUP, ()), (ccConst.LIGHTSGROUP, ())]
        rightSideWidth = self.rightSide.GetAbsoluteSize()[1]
        assetMenuWidth = max(min(MAXMENUSIZE + CCColorPalette.COLORPALETTEWIDTH, rightSideWidth - 32), 0)
        self.assetMenuMainWidth = assetMenuWidth - CCColorPalette.COLORPALETTEWIDTH
        self.portraitAssetMenu = CharCreationAssetMenu(parent=self.assetMenuPar, groups=groups, align=uiconst.CENTERTOP, width=assetMenuWidth, height=uicore.desktop.height)
        self.assetMenuPar.width = assetMenuWidth

    def SetHintText(self, modifier, hintText = ''):
        text = hintText
        if modifier in ccConst.HELPTEXTS:
            labelPath = ccConst.HELPTEXTS[modifier]
            text = localization.GetByLabel(labelPath)
        if text != self.hintText.text:
            self.hintText.text = text

    def ReloadPortraits(self):
        if self.portraitCont:
            self.portraitCont.Close()
        self.portraitCont = Container(name='portraitCont', parent=self.leftSide, align=uiconst.TOPLEFT, pos=(25,
         128,
         128,
         134 * ccConst.NUM_PORTRAITS - 6 + 44))
        self.facePortraits = [None] * ccConst.NUM_PORTRAITS
        for i in xrange(ccConst.NUM_PORTRAITS):
            if i == 0:
                frameAlpha = 0.8
            else:
                frameAlpha = 0.2
            portraitCont = Container(name='portraitCont1', parent=self.portraitCont, align=uiconst.TOTOP, pos=(0,
             0,
             0,
             self.portraitSize), padBottom=6, state=uiconst.UI_NORMAL)
            portraitCont.OnClick = (self.PickPortrait, i)
            portraitCont.OnDblClick = self.OnPortraitDblClick
            portraitCont.OnMouseEnter = (self.OnPortraitEnter, portraitCont)
            button = eveIcon.Icon(parent=portraitCont, icon=ccConst.ICON_CAM_IDLE, state=uiconst.UI_NORMAL, align=uiconst.TOPRIGHT, color=ccConst.COLOR75, left=6, top=6)
            button._idleIcon = ccConst.ICON_CAM_IDLE
            button._pressedIcon = ccConst.ICON_CAM_PRESSED
            button._imageIndex = i
            button.OnClick = (self.CameraButtonClick, button)
            button.OnMouseEnter = (self.GenericButtonEnter, button)
            button.OnMouseExit = (self.GenericButtonExit, button)
            button.OnMouseDown = (self.GenericButtonDown, button)
            button.OnMouseUp = (self.GenericButtonUp, button)
            frame = Frame(parent=portraitCont, color=ccConst.COLOR + (frameAlpha,))
            facePortrait = eveIcon.Icon(parent=portraitCont, align=uiconst.TOALL, state=uiconst.UI_DISABLED)
            Fill(parent=portraitCont, color=(0.0, 0.0, 0.0, 0.35))
            portraitCont.button = button
            portraitCont.frame = frame
            portraitCont.facePortrait = facePortrait
            portraitCont.hasPhoto = False
            self.facePortraits[i] = portraitCont

        for i in xrange(ccConst.NUM_PORTRAITS):
            ccPortraitManager = GetCharacterCreationPortraitManager()
            if ccPortraitManager.facePortraits[i] is not None:
                photo = ccPortraitManager.facePortraits[i]
                cont = self.facePortraits[i]
                cont.facePortrait.texture.atlasTexture = photo
                cont.facePortrait.texture.atlasTexture.Reload()
                cont.hasPhoto = True
                cont.button.state = uiconst.UI_HIDDEN
                if hasattr(uicore.layer.charactercreation.controller, 'activePortrait') and photo == uicore.layer.charactercreation.controller.activePortrait:
                    self.SetPortraitFocus(i)

        Button(parent=self.portraitCont, label=localization.GetByLabel('UI/CharacterCreation/ResetExpression'), align=uiconst.CENTERBOTTOM, func=self.ResetFacePose)

    def ResetFacePose(self, *args):
        info = self.GetInfo()
        self.charSvc.ResetFacePose(info.charID)

    def OnPortraitDblClick(self, *args):
        uicore.layer.charactercreation.controller.Approve()

    def PickPortrait(self, selectedNo):
        uicore.layer.charactercreation.controller.AnimateToStoredPortrait(selectedNo)
        self.SetPortraitFocus(selectedNo)

    def SetPortraitFocus(self, selectedNo, *args):
        self.selectedPortrait = selectedNo
        for portraitContainer in self.facePortraits:
            portraitContainer.frame.SetAlpha(0.2)
            portraitContainer.facePortrait.SetAlpha(0.3)

        frame = self.facePortraits[selectedNo].frame
        frame.SetAlpha(0.8)
        portrait = self.facePortraits[selectedNo].facePortrait
        portrait.SetAlpha(1.0)
        GetCharacterCreationPortraitManager().SetActivePortrait(selectedNo)

    def ValidateStepComplete(self):
        if not self.IsDollReady:
            return False
        if GetCharacterCreationPortraitManager().GetPortraitInfo(self.selectedPortrait) is None:
            self.CapturePortrait(self.selectedPortrait)
        return True

    def CapturePortrait(self, idx, *args):
        photo = uicore.layer.charactercreation.controller.CapturePortrait(idx)
        if photo:
            self.SetPortrait(photo)
            GetCharacterCreationPortraitManager().SetFacePortrait(photo, idx)

    def SetPortrait(self, photo, *args):
        if self.destroyed:
            return
        facePortraitCont = self.facePortraits[self.selectedPortrait]
        facePortraitCont.facePortrait.texture.atlasTexture = photo
        facePortraitCont.facePortrait.texture.atlasTexture.Reload()
        facePortraitCont.hasPhoto = True

    def OnPortraitEnter(self, portrait, *args):
        portrait.button.state = uiconst.UI_NORMAL
        portrait.mouseOverTimer = timerstuff.AutoTimer(33.0, self.CheckPortraitMouseOver, portrait)

    def CheckPortraitMouseOver(self, portrait, *args):
        if uicore.uilib.mouseOver is portrait or uicore.uilib.mouseOver.IsUnder(portrait):
            return
        portrait.mouseOverTimer = None
        if portrait.hasPhoto:
            portrait.button.state = uiconst.UI_HIDDEN

    def CameraButtonClick(self, button, *args):
        sm.StartService('audio').SendUIEvent(unicode('ui_icc_portrait_snapshot_play'))
        self.SetPortraitFocus(button._imageIndex)
        self.CapturePortrait(button._imageIndex)

    def GenericButtonDown(self, button, mouseBtn, *args):
        if mouseBtn == uiconst.MOUSELEFT:
            MapIcon(button, button._pressedIcon)

    def GenericButtonUp(self, button, *args):
        MapIcon(button, button._idleIcon)

    def GenericButtonEnter(self, button, *args):
        MapIcon(button, button._idleIcon)

    def GenericButtonExit(self, button, *args):
        MapIcon(button, button._idleIcon)

    def OnGraphicSettingsChanged(self, changes):
        if gfxsettings.UI_NCC_GREEN_SCREEN in changes:
            self.UpdateLayout()
        self.ReloadPortraitAssetMenu()
