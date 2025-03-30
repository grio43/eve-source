#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation_new\steps\characterCustomization.py
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.sys import serviceConst
from carbonui import uiconst
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from charactercreator import const as ccConst
from eve.client.script.ui import eveColor
from eve.client.script.ui.control import eveLabel
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.button import Button
from eve.client.script.ui.control.eveLabel import EveLabelMedium, Label, EveHeaderLarge
from eve.client.script.ui.login.charcreation_new import ccUtil, soundConst
from eve.client.script.ui.login.charcreation_new.charCreation import BaseCharacterCreationStep, MAXMENUSIZE
from eve.client.script.ui.login.charcreation_new.charCreationBodyPicker import CCHeadBodyPicker
from eve.client.script.ui.login.charcreation_new.hexes import CCHexButtonRandomize
from eve.client.script.ui.login.charcreation_new.assetMenu import CharCreationAssetMenu
from eve.client.script.ui.login.charcreation_new.colorPalette import CCColorPalette
from eve.client.script.ui.login.charcreation_new.historySlider import CharacterCreationHistorySlider
from eve.client.script.ui.login.charcreation_new.sceneManager import GetCharacterCreationSceneManager
from eve.client.script.ui.login.charcreation_new.dollManager import GetCharacterCreationDollManager
from eveexceptions import UserError
from evegraphics import settings as gfxsettings
import localization
import trinity
import uthread
import blue
import geo2
from carbonui.uicore import uicore
from eveprefs import prefs
from itertoolsext.Enum import Enum
TOGGLE_CLOTHES_BUTTON_ANALYTIC_ID = 'ToggleClothesButton'

class CharacterCustomization(BaseCharacterCreationStep):
    __guid__ = 'uicls.CharacterCustomization'
    __notifyevents__ = ['OnColorPaletteChanged', 'OnHideUI', 'OnShowUI']
    stepID = ccConst.CUSTOMIZATIONSTEP
    ASSETMENU = 1
    TATTOOMENU = 2

    def ApplyAttributes(self, attributes):
        uicore.event.RegisterForTriuiEvents(uiconst.UI_ACTIVE, self.CheckAppFocus)
        BaseCharacterCreationStep.ApplyAttributes(self, attributes)
        self.menuMode = self.ASSETMENU
        self.colorPaletteWidth = CCColorPalette.COLORPALETTEWIDTH
        self.tattooChangeMade = 0
        self.menusInitialized = 0
        self.tattoMenu = None
        self.assetMenu = None
        self.loadingWheelThread = None
        self.historySlider = None
        self.debugReloadBtn = None
        customizationOptionsContainer = ContainerAutoSize(name='customizationOptionsContainer', parent=self.leftSide, align=uiconst.TOLEFT, top=90, width=200)
        self.randomizeButton = CCHexButtonRandomize(name='randomizeButton', parent=Container(parent=customizationOptionsContainer, align=uiconst.TOTOP, height=64), align=uiconst.CENTER, state=uiconst.UI_NORMAL, width=64, height=64, pickRadius=32, iconNum=0, func=self.RandomizeCharacter, hexName=localization.GetByLabel('UI/CharacterCreation/RandomizeDollTooltip'))
        EveLabelMedium(name='randomizeLabel', parent=customizationOptionsContainer, align=uiconst.TOTOP, text='<center>%s</center>' % localization.GetByLabel('UI/CharacterCreation/RandomizeAll'), top=-4)
        CCHeadBodyPicker(parent=customizationOptionsContainer, align=uiconst.TOTOP, headCallback=self.LoadFaceMode, bodyCallback=self.LoadBodyMode, top=10)
        EveLabelMedium(name='toggleClothesLabel', parent=customizationOptionsContainer, align=uiconst.TOTOP, text='<center>%s</center>' % localization.GetByLabel('UI/CharacterCreation/Zoom'))
        ButtonIcon(name='toggleClothesButton', parent=Container(parent=customizationOptionsContainer, align=uiconst.TOTOP, height=64, top=5), align=uiconst.CENTER, width=64, height=64, iconSize=64, texturePath='res:/UI/Texture/WindowIcons/charcustomization.png', func=self.ToggleClothes, useThemeColor=False, iconClass=Sprite, iconBlendMode=trinity.TR2_SBM_BLEND, hint=localization.GetByLabel('UI/CharacterCreation/ToggleClothes'), analyticID=TOGGLE_CLOTHES_BUTTON_ANALYTIC_ID)
        EveLabelMedium(name='toggleClothesLabel', parent=customizationOptionsContainer, align=uiconst.TOTOP, text='<center>%s</center>' % localization.GetByLabel('UI/CharacterCreation/ToggleClothes'))
        self.assetMenuParent = Container(parent=self.rightSide, name='assetMenuParent', pos=(20, 115, 500, 0), state=uiconst.UI_PICKCHILDREN, align=uiconst.TORIGHT)
        assetMenuWidth = min(MAXMENUSIZE, self.rightSide.width - 22)
        Label(name='assetMenuLabel', parent=Container(parent=self.assetMenuParent, align=uiconst.TOPRIGHT, width=assetMenuWidth, height=25), align=uiconst.CENTERLEFT, text=localization.GetByLabel('UI/CharacterCreation/CustomizeAppearance'), color=eveColor.PRIMARY_BLUE, fontsize=22, uppercase=True)
        self.hintBox = Container(name='hintBox', parent=self.assetMenuParent, pos=(-96, 30, 200, 150), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED)
        self.hintText = eveLabel.EveLabelMedium(parent=self.hintBox, align=uiconst.TOTOP)
        self.characterCustomizationInfoPanel = CharacterCustomizationInfoPanel(name='characterCustomizationInfoPanel', parent=self.uiContainer, align=uiconst.CENTERTOP, top=80, width=300)
        self.UpdateLayout()
        if uicore.layer.charactercreation.controller.needSculptingTutorial:
            self.ShowSculptingInfoPanel()
        elif uicore.layer.charactercreation.controller.needNavigationTutorial:
            self.ShowNavigationInfoPanel()
        GetCharacterCreationSceneManager().camera.cameraModeChanged.connect(self._OnCameraModeChanged)
        self.StartLoadingThread()
        PlaySound(soundConst.EDIT_CHARACTER_LOOP)

    def StartLoadingThread(self, *args):
        if self.loadingWheelThread:
            self.loadingWheelThread.kill()
            self.loadingWheelThread = None
        self.loadingWheelThread = uthread.new(self.ShowLoadingWheel_thread)

    def SetHintText(self, modifier, hintText = ''):
        text = hintText
        if modifier in ccConst.HELPTEXTS:
            labelPath = ccConst.HELPTEXTS[modifier]
            text = localization.GetByLabel(labelPath)
        elif modifier == ccConst.eyes:
            labelPath = ccConst.HELPTEXTS[ccConst.EYESGROUP]
            text = localization.GetByLabel(labelPath)
        if text != self.hintText.text:
            self.hintText.text = text

    def ToggleClothes(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        info = self.GetInfo()
        ccDollManager = GetCharacterCreationDollManager()
        if ccDollManager.GetDoll(info.charID).busyUpdating:
            raise UserError('uiwarning01')
        ccDollManager.ToggleClothes()

    def UpdateLayout(self, *args):
        self.colorPaletteWidth = CCColorPalette.COLORPALETTEWIDTH
        sm.GetService('cc').LogInfo('CharacterCustomization::UpdateLayout')
        if not self.menusInitialized:
            self.tattoMenu = self.ReloadTattooMenu()
            self.assetMenu = self.ReloadAssetMenu()
            self.menusInitialized = 1
        self.LoadMenu()

    def OnColorPaletteChanged(self, width, *args):
        if width > self.colorPaletteWidth:
            self.colorPaletteWidth = width

    def RandomizeCharacter(self, *args):
        self.randomizeButton.StartBlinking()
        PlaySound('ui_icc_button_mouse_down_play')
        uicore.layer.charactercreation.controller.RandomizeCharacter()
        self.randomizeButton.StopBlinking()

    def InitAvatarPositions(self):
        info = self.GetInfo()
        avatar = sm.GetService('character').GetSingleCharactersAvatar(info.charID)
        avatar.translation = (0.0, 0.0, 0.0)
        avatar.rotation = geo2.QuaternionRotationSetYawPitchRoll(0.0, 0.0, 0.0)
        sm.GetService('character').UpdateDoll(info.charID, fromWhere='InitAvatarPositions')

    def LoadMenu(self, animate = 0, forcedMode = 0, *arg):
        sm.GetService('cc').LogInfo('CharacterCustomization::LoadMenu')
        menu = None
        if self.menuMode == self.ASSETMENU:
            menu = self.GetAssetMenu(forcedMode)
        elif self.menuMode == self.TATTOOMENU:
            menu = self.GetTattooMenu(forcedMode)
        if menu is None:
            return
        if animate:
            mainCont = menu.mainContainter
            if self.menuMode == self.TATTOOMENU:
                menu.state = uiconst.UI_PICKCHILDREN
            else:
                menu.state = uiconst.UI_DISABLED
                uicore.effect.MorphUIMassSpringDamper(mainCont, 'top', 0, newthread=False, float=False, frequency=15.0, dampRatio=0.85)
                menu.state = uiconst.UI_PICKCHILDREN
        else:
            menu.state = uiconst.UI_PICKCHILDREN
        menu.CheckIfOversize()

    def GetTattooMenu(self, forcedMode = 0, *args):
        sm.GetService('cc').LogInfo('CharacterCustomization::GetTattooMenu')
        if not forcedMode and self.tattoMenu and not self.tattoMenu.destroyed:
            if self.assetMenu:
                self.assetMenu.state = uiconst.UI_HIDDEN
            return self.tattoMenu
        else:
            return self.ReloadTattooMenu()

    def ReloadTattooMenu(self, *args):
        sm.GetService('cc').LogInfo('CharacterCustomization::ReloadTattooMenu')
        self.StartLoadingThread()
        if self.assetMenu:
            self.assetMenu.state = uiconst.UI_HIDDEN
        if self.tattoMenu:
            self.tattoMenu.Close()
        info = self.GetInfo()
        piercingSub = (ccConst.p_brow,
         ccConst.p_nose,
         ccConst.p_nostril,
         ccConst.p_earshigh,
         ccConst.p_earslow,
         ccConst.p_lips,
         ccConst.p_chin)
        scarSub = (ccConst.s_head,)
        tattooSub = (ccConst.t_head, ccConst.t_armleft, ccConst.t_armright)
        augmentations = (ccConst.pr_armleft,
         ccConst.pr_armright,
         ccConst.augm_face,
         ccConst.augm_body)
        groups = []
        groups += [(ccConst.PIERCINGGROUP, piercingSub)]
        groups += [(ccConst.TATTOOGROUP, tattooSub)]
        groups += [(ccConst.SCARSGROUP, scarSub)]
        groups += [(ccConst.AUGMENTATIONS, augmentations)]
        self.tattoMenu = CharCreationAssetMenu(menuType='tattooMenu', parent=self.assetMenuParent, bloodlineID=info.bloodlineID, state=uiconst.UI_PICKCHILDREN, genderID=info.genderID, charID=info.charID, groups=groups, align=uiconst.TOALL, toggleFunc=self.GoToAssetMode, togglerIdx=0, top=26)
        return self.tattoMenu

    def GetAssetMenu(self, forcedMode = 0, *args):
        sm.GetService('cc').LogInfo('CharacterCustomization::GetAssetMenu')
        if not forcedMode and self.assetMenu and not self.assetMenu.destroyed:
            if self.tattoMenu and not self.tattoMenu.destroyed:
                self.tattoMenu.state = uiconst.UI_HIDDEN
            return self.assetMenu
        else:
            return self.ReloadAssetMenu()

    def ReloadAssetMenu(self, *args):
        sm.GetService('cc').LogInfo('CharacterCustomization::ReloadAssetMenu')
        self.StartLoadingThread()
        if self.assetMenu:
            self.assetMenu.Close()
        if self.tattoMenu:
            self.tattoMenu.state = uiconst.UI_HIDDEN
        info = self.GetInfo()
        makeup = ccConst.MAKEUPGROUP
        if info.genderID == 1:
            makeup = ccConst.SKINDETAILSGROUP
        clothesSub = (ccConst.outer,
         ccConst.topouter,
         ccConst.topmiddle,
         ccConst.bottomouter,
         ccConst.bottommiddle,
         ccConst.feet,
         ccConst.glasses,
         ccConst.mask)
        groups = []
        if uicore.layer.charactercreation.controller.CanChangeBaseAppearance():
            groups += [(ccConst.ARCHETYPESGROUP, ())]
            groups += [(ccConst.BODYGROUP, ())]
            groups += [(ccConst.SKINGROUP, ())]
        groups += [(ccConst.EYESGROUP, ())]
        groups += [(ccConst.HAIRGROUP, ())]
        groups += [(makeup, (ccConst.eyeshadow,
           ccConst.eyeliner,
           ccConst.blush,
           ccConst.lipstick))]
        groups += [(ccConst.CLOTHESGROUP, clothesSub)]
        assetMenuWidth = min(MAXMENUSIZE + CCColorPalette.COLORPALETTEWIDTH, self.rightSide.width - 20)
        self.assetMenuMainWidth = assetMenuWidth - CCColorPalette.COLORPALETTEWIDTH
        self.assetMenu = CharCreationAssetMenu(menuType='assetMenu', parent=self.assetMenuParent, bloodlineID=info.bloodlineID, state=uiconst.UI_PICKCHILDREN, genderID=info.genderID, charID=info.charID, groups=groups, align=uiconst.TOALL, toggleFunc=self.GoToTattooMode, clipChildren=True, top=26)
        if self.historySlider:
            self.historySlider.Close()
        self.historySlider = CharacterCreationHistorySlider(parent=self.uiContainer, align=uiconst.CENTERBOTTOM, top=-45, width=400, opacity=0.0, bitChangeCheck=self.IsDollReady, lastLitHistoryBit=GetCharacterCreationDollManager().lastLitHistoryBit)
        mask = serviceConst.ROLE_CONTENT | serviceConst.ROLE_QA | serviceConst.ROLE_PROGRAMMER | serviceConst.ROLE_GML
        if eve.session.role & mask:
            if self.debugReloadBtn:
                self.debugReloadBtn.Close()
                self.tattooModeBtn.Close()
                self.typeAddEdit.Close()
                self.validationToggle.Close()
                self.typeAddBtn.Close()
            self.debugReloadBtn = Button(parent=self.uiContainer, func=self.GoToAssetMode, args=(1,), label='Reload Menu (debug)', align=uiconst.TOPRIGHT, left=self.randomizeButton.left + 30, top=16)
            self.tattooModeBtn = Button(parent=self.uiContainer, func=self.GoToTattooMode, args=(0, 1), label='Go to Tattoo mode (debug)', align=uiconst.TOPRIGHT, left=250, top=16)
            self.typeAddEdit = SingleLineEditInteger(parent=self.uiContainer, name='typeAdd', maxValue=100000, align=uiconst.TOPRIGHT, left=650, top=16, maxLength=10)
            self.validationToggle = Button(parent=self.uiContainer, name='validationToggle', func=self.ToggleValidation, label='Validation On', align=uiconst.TOPRIGHT, left=430, top=16)
            self.typeAddBtn = Button(parent=self.uiContainer, func=self.AddTypeButton, label='Add Type (debug)', align=uiconst.TOPRIGHT, left=530, top=16)
            self.addBlankDoll = Button(parent=self.uiContainer, func=self.AddBlankDrifterDoll, label='Add Blank Drifter Doll (debug)', align=uiconst.TOPRIGHT, left=530, top=35)
        animations.MorphScalar(self.historySlider, 'top', endVal=55, duration=0.125)
        animations.FadeIn(self.historySlider, duration=0.125)
        return self.assetMenu

    def AddBlankDrifterDoll(self, *args):
        from eve.common.script.paperDoll.paperDollDefinitions import LOD_SKIN
        info = self.GetInfo()
        self.charSvc.RemoveCharacter(info.charID)
        self.charSvc.AddCharacterToScene(info.charID, uicore.layer.charactercreation.controller.scene, ccUtil.GenderIDToPaperDollGender(info.genderID), bloodlineID=19, raceID=None, noRandomize=True, updateDoll=False)
        doll = self.charSvc.GetSingleCharactersDoll(info.charID)
        GetCharacterCreationDollManager().SetDoll(info.charID, doll)
        while doll.IsBusyUpdating():
            blue.synchro.Yield()

        doll.overrideLod = LOD_SKIN
        textureQuality = gfxsettings.Get(gfxsettings.GFX_CHAR_TEXTURE_QUALITY)
        doll.textureResolution = ccConst.TEXTURE_RESOLUTIONS[textureQuality]
        if ccUtil.IsSlowMachine():
            doll.useFastShader = True
        else:
            doll.useFastShader = False
        self.charSvc.SetDollBloodline(info.charID, 19)
        self.charSvc.UpdateDoll(info.charID, fromWhere='AddCharacter')

    def ToggleValidation(self, *args):
        validating = sm.RemoteSvc('charUnboundMgr').ToggleValidation()
        if validating:
            self.validationToggle.SetLabel('Validation On')
        else:
            self.validationToggle.SetLabel('Validation Off')

    def AddTypeButton(self, *args):
        resourceID = self.typeAddEdit.GetValue()
        paperdollResource = cfg.paperdollResources.Get(resourceID)
        if paperdollResource:
            info = self.GetInfo()
            itemRelativeResPath = self.charSvc.GetRelativePath(paperdollResource.resPath).lower()
            itemTypeData = self.charSvc.factory.GetItemType(itemRelativeResPath, gender=ccUtil.GenderIDToPaperDollGender(info.genderID))
            itemInfo = (resourceID, itemTypeData[:3], paperdollResource.typeID)
            GetCharacterCreationDollManager().SetItemType(itemInfo)

    def GoToTattooMode(self, animate = 1, forcedMode = 0, *args):
        self.menuMode = self.TATTOOMENU
        self.tattooChangeMade = 0
        self.charSvc.StopEditing()
        if self.historySlider:
            self.historySlider.state = uiconst.UI_HIDDEN
        if self.assetMenu and not self.assetMenu.destroyed:
            mainCont = self.assetMenu.mainContainter
            h = mainCont.displayHeight - self.assetMenu.menuToggler.height - 4
            uicore.effect.MorphUIMassSpringDamper(mainCont, 'top', -h, newthread=False, float=False, frequency=15.0, dampRatio=0.85)
        self.LoadMenu(animate=animate, forcedMode=forcedMode)

    def GoToAssetMode(self, forcedMode = 0, *args):
        self.menuMode = self.ASSETMENU
        if self.tattoMenu and not self.tattoMenu.destroyed:
            if self.tattooChangeMade:
                uicore.layer.charactercreation.controller.TryStoreDna(False, 'GoToAssetMode', sculpting=False, force=1, allowReduntant=0)
            mainCont = self.tattoMenu.mainContainter
            h = self.tattoMenu.menuToggler.height + self.tattoMenu.menuToggler.padTop + self.tattoMenu.menuToggler.padBottom
            animations.MorphScalar(mainCont, 'top', endVal=0, duration=0.01)
            animations.MorphScalar(mainCont, 'height', endVal=h, duration=0.25, sleep=True)
        self.tattooChangeMade = 0
        if uicore.layer.charactercreation.controller.CanChangeBaseAppearance():
            uicore.layer.charactercreation.controller.StartEditMode()
        if self.historySlider:
            self.historySlider.state = uiconst.UI_PICKCHILDREN
        self.LoadMenu(animate=1, forcedMode=forcedMode)

    def OnGenericMouseEnter(self, btn, *args):
        PlaySound('ui_icc_button_mouse_over_play')
        btn.icon.SetAlpha(1.0)

    def OnGenericMouseExit(self, btn, *args):
        btn.icon.SetAlpha(0.5)

    def LoadFaceMode(self, *args):
        info = self.GetInfo()
        avatar = self.charSvc.GetSingleCharactersAvatar(info.charID)
        GetCharacterCreationSceneManager().camera.ToggleMode(ccConst.CAMERA_MODE_FACE, avatar=avatar, transformTime=500.0)

    def LoadBodyMode(self, *args):
        info = self.GetInfo()
        avatar = self.charSvc.GetSingleCharactersAvatar(info.charID)
        GetCharacterCreationSceneManager().camera.ToggleMode(ccConst.CAMERA_MODE_BODY, avatar=avatar, transformTime=500.0)

    def ValidateStepComplete(self):
        info = self.GetInfo()
        if prefs.GetValue('ignoreCCValidation', False):
            return True
        if self.menuMode == self.TATTOOMENU:
            uicore.layer.charactercreation.controller.TryStoreDna(False, 'ValidateStepComplete', force=1, allowReduntant=0)
        while not self.IsDollReady():
            blue.synchro.Yield()

        return self.charSvc.ValidateDollCustomizationComplete(info.charID)

    def ShowLoadingWheel_thread(self, *args):
        layer = uicore.layer.charactercreation.controller
        info = self.GetInfo()
        doll = GetCharacterCreationDollManager().GetDoll(info.charID)
        while doll and not self.destroyed:
            if layer.step and getattr(layer.step, '_activeSculptZone', None) is not None:
                layer.HideLoading()
            elif doll.busyUpdating:
                layer.ShowLoading(why=localization.GetByLabel('UI/CharacterCreation/UpdatingCharacter'))
            else:
                layer.HideLoading()
            blue.pyos.synchro.SleepWallclock(100)

    def CheckAppFocus(self, wnd, msgID, vkey):
        focused = vkey[0]
        if not focused:
            uicore.layer.charactercreation.controller.PassMouseEventToSculpt('LeftDown', uicore.uilib.x, uicore.uilib.y)
            uicore.layer.charactercreation.controller.PassMouseEventToSculpt('LeftUp', uicore.uilib.x, uicore.uilib.y)
            self.ChangeSculptingCursor(-1, 0, 0)
            uicore.layer.charactercreation.controller.UnfreezeAnimationIfNeeded()
        return 1

    def Close(self):
        PlaySound(soundConst.EDIT_CHARACTER_LOOP_STOP)
        super(CharacterCustomization, self).Close()

    def StoreHistorySliderPosition(self, *args):
        if self.historySlider:
            currentIndex, maxIndex = self.historySlider.GetCurrentIndexAndMaxIndex()
        else:
            currentIndex = None
        GetCharacterCreationDollManager().lastLitHistoryBit = currentIndex

    def _SetActiveSculptZone(self, sculptZone):
        super(CharacterCustomization, self)._SetActiveSculptZone(sculptZone)
        if sculptZone:
            self.HideSculptingInfoPanel()

    def _OnCameraModeChanged(self, previousMode, newMode):
        if previousMode is not None and newMode in [ccConst.CAMERA_MODE_FACE, ccConst.CAMERA_MODE_BODY]:
            uicore.layer.charactercreation.controller.needNavigationTutorial = False
            self.HideNavigationInfoPanel()
            GetCharacterCreationSceneManager().camera.cameraModeChanged.disconnect(self._OnCameraModeChanged)

    def IsNavigationInfoPanelVisible(self):
        return self.characterCustomizationInfoPanel.IsVisible() and self.characterCustomizationInfoPanel.GetMode() == CharacterCustomizationInfoPanel.Modes.NAVIGATION

    def IsSculptingInfoPanelVisible(self):
        return self.characterCustomizationInfoPanel.IsVisible() and self.characterCustomizationInfoPanel.GetMode() == CharacterCustomizationInfoPanel.Modes.SCULPTING

    def ShowSculptingInfoPanel(self):
        if uicore.layer.charactercreation.controller.needSculptingTutorial:
            self.characterCustomizationInfoPanel.SetMode(CharacterCustomizationInfoPanel.Modes.SCULPTING)
            self.characterCustomizationInfoPanel.Show()

    def HideSculptingInfoPanel(self):
        if self.IsSculptingInfoPanelVisible():
            self.characterCustomizationInfoPanel.Hide(callback=lambda : self.ShowNavigationInfoPanel(timeOffset=1.0))
            uicore.layer.charactercreation.controller.needSculptingTutorial = False

    def ShowNavigationInfoPanel(self, timeOffset = 0.0):
        if uicore.layer.charactercreation.controller.needNavigationTutorial:
            self.characterCustomizationInfoPanel.SetMode(CharacterCustomizationInfoPanel.Modes.NAVIGATION)
            self.characterCustomizationInfoPanel.Show(timeOffset=timeOffset)

    def HideNavigationInfoPanel(self):
        if self.IsNavigationInfoPanelVisible():
            self.characterCustomizationInfoPanel.Hide()
            uicore.layer.charactercreation.controller.needNavigationTutorial = False


class CharacterCustomizationInfoPanel(ContainerAutoSize):

    @Enum

    class Modes(object):
        NONE = 'NONE'
        NAVIGATION = 'NAVIGATION'
        SCULPTING = 'SCULPTING'

    def ApplyAttributes(self, attributes):
        super(CharacterCustomizationInfoPanel, self).ApplyAttributes(attributes)
        Frame(bgParent=self, color=(0.15, 0.15, 0.15, 1.0))
        self.background_color = (0.04, 0.04, 0.04, 1.0)
        self._mode = CharacterCustomizationInfoPanel.Modes.NONE
        self._title = EveHeaderLarge(name='sculptingInfoTitle', parent=self, align=uiconst.TOTOP, top=10)
        self._title.SetTextColor(eveColor.PRIMARY_BLUE)
        self._text = EveLabelMedium(name='sculptingInfoText', parent=self, align=uiconst.TOTOP, padding=(10, 10, 10, 10))
        self.opacity = 0

    def SetMode(self, mode):
        self._mode = mode
        if self._mode == CharacterCustomizationInfoPanel.Modes.NONE:
            self._SetTitle('')
            self._SetText('')
            self.opacity = 0
            return
        if self._mode == CharacterCustomizationInfoPanel.Modes.SCULPTING:
            self._SetTitle(localization.GetByLabel('UI/CharacterCreation/SculptingTool'))
            self._SetText(localization.GetByLabel('UI/CharacterCreation/SculptingToolHelp'))
        elif self._mode == CharacterCustomizationInfoPanel.Modes.NAVIGATION:
            self._SetTitle(localization.GetByLabel('UI/CharacterCreation/Navigation'))
            self._SetText(localization.GetByLabel('UI/CharacterCreation/NavigationHelp'))

    def GetMode(self):
        return self._mode

    def IsVisible(self):
        return self.opacity > 0

    def _SetTitle(self, title):
        self._title.SetText('<center>%s</center>' % title)

    def _SetText(self, text):
        self._text.SetText(text)

    def Show(self, timeOffset = 0.0, callback = None):
        uicore.animations.FadeTo(self, startVal=self.opacity, endVal=1.0, duration=0.25 * (1.0 - self.opacity), timeOffset=timeOffset, callback=callback)

    def Hide(self, timeOffset = 0.0, callback = None):
        uicore.animations.FadeTo(self, startVal=self.opacity, endVal=0.0, duration=0.25 * self.opacity, timeOffset=timeOffset, callback=callback)
