#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation_new\assetPicker.py
import os
import random
import types
import uthread
import charactercreator.const as ccConst
import blue
import localization
import evegraphics.settings as gfxsettings
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.sys.serviceConst import ROLE_CONTENT, ROLE_GML, ROLE_PROGRAMMER, ROLE_QA
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from carbonui.uianimations import animations
from carbonui.util.various_unsorted import SortListOfTuples
from eve.client.script.ui import eveColor
from eve.client.script.ui.control import eveIcon
from eve.client.script.ui.control.eveImagePicker import ImagePicker
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.login.charcreation_new.charCreationUtils import GradientSlider, BitSlider, CCLabel
from eve.client.script.ui.login.charcreation_new.charCreationColorPicker import CharCreationColorPicker
from eve.client.script.ui.login.charcreation_new.colorPalette import CCColorPalette
from eve.client.script.ui.login.charcreation_new.sceneManager import GetCharacterCreationSceneManager
from eve.client.script.ui.login.charcreation_new.portraitManager import GetCharacterCreationPortraitManager
from eve.client.script.ui.login.charcreation_new.dollManager import GetCharacterCreationDollManager
import eve.client.script.ui.login.charcreation_new.ccUtil as ccUtil
from eveexceptions import UserError
from eveprefs import prefs
commonModifiersDisplayNames = {ccConst.eyes: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Eyes',
 ccConst.hair: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/HairStyle',
 ccConst.eyebrows: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Eyebrows',
 ccConst.skintone: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/SkinTone',
 ccConst.skinaging: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Aging',
 ccConst.scarring: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Scarring',
 ccConst.freckles: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Freckles',
 ccConst.glasses: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Clothing/Glasses',
 ccConst.muscle: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Muscularity',
 ccConst.weight: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Weight',
 ccConst.topmiddle: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Clothing/TopMiddleLayer',
 ccConst.topouter: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Clothing/TopOuterLayer',
 ccConst.bottomouter: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Clothing/BottomOuterLayer',
 ccConst.outer: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Clothing/OuterLayer',
 ccConst.bottommiddle: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Clothing/BottomMiddleLayer',
 ccConst.feet: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Clothing/FeetLayer',
 ccConst.p_earslow: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Piercings/EarsLow',
 ccConst.p_earshigh: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Piercings/EarsHigh',
 ccConst.p_nose: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Piercings/Nose',
 ccConst.p_nostril: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Piercings/Nostril',
 ccConst.p_brow: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Piercings/Eyebrows',
 ccConst.p_lips: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Piercings/Lips',
 ccConst.p_chin: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Piercings/Chin',
 ccConst.t_head: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Tattoos/Head',
 ccConst.t_armleft: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Tattoos/ArmLeft',
 ccConst.t_armright: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Tattoos/ArmRight',
 ccConst.s_head: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Scars/Head',
 ccConst.skintype: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Skintype',
 ccConst.pr_armleft: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Prosthetics/ArmLeft',
 ccConst.pr_armright: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Prosthetics/ArmRight',
 ccConst.augm_face: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Augmentations/Face',
 ccConst.augm_body: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Augmentations/Body',
 ccConst.mask: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Clothing/Masks'}
maleModifierDisplayNames = {ccConst.eyeshadow: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/EyeDetails',
 ccConst.eyeliner: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/LashThickness',
 ccConst.lipstick: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/LipTone',
 ccConst.blush: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/CheekColor',
 ccConst.beard: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/FacialHair'}
maleModifierDisplayNames.update(commonModifiersDisplayNames)
femaleModifierDisplayNames = {ccConst.eyeshadow: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/EyeShadow',
 ccConst.eyeliner: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Eyeliner',
 ccConst.lipstick: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Lipstick',
 ccConst.blush: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Blush'}
femaleModifierDisplayNames.update(commonModifiersDisplayNames)

class CharCreationAssetPicker(Container):
    __guid__ = 'uicls.CharCreationAssetPicker'
    __notifyevents__ = ['OnDollUpdated', 'OnColorPaletteChanged', 'OnPortraitPicked']
    FULLHEIGHT = 190
    COLLAPSEHEIGHT = 22
    default_align = uiconst.TOTOP
    default_left = 0
    default_top = 0
    default_width = 0
    default_height = COLLAPSEHEIGHT
    default_name = 'CharCreationAssetPicker'
    default_state = uiconst.UI_PICKCHILDREN

    def ApplyAttributes(self, attributes):
        sm.GetService('cc').LogInfo('CharCreationAssetPicker::ApplyAttributes:: modifier = ', attributes.modifier)
        for each in uicore.layer.main.children:
            if each.name == self.default_name:
                each.Close()

        info = uicore.layer.charactercreation.controller.GetInfo()
        if attributes.isSubmenu:
            self.COLLAPSEHEIGHT = 18
            attributes.heght = 18
        Container.ApplyAttributes(self, attributes)
        if attributes.parent is None:
            uicore.layer.main.children.append(self)
        self._expandTime = None
        self._expanded = False
        self._didRandomize = None
        self.randomButton = None
        self.colorPalette = None
        self.browser = None
        self.colorIntensitySlider = None
        self.colorPaletteParent = Container(parent=self, align=uiconst.TOLEFT, width=CCColorPalette.COLORPALETTEWIDTH, name='colorPaletteParent', state=uiconst.UI_PICKCHILDREN)
        self.captionParent = Container(parent=self, align=uiconst.TOTOP, height=self.COLLAPSEHEIGHT, name='captionParent', state=uiconst.UI_NORMAL)
        self.captionParent.OnClick = self.Toggle
        self.captionParent.OnMouseEnter = self.OnCaptionEnter
        self.captionParent.OnMouseExit = self.OnCaptionExit
        self.captionParent.modifier = attributes.modifier
        self.caption = CCLabel(parent=self.captionParent, align=uiconst.CENTERLEFT, left=10, letterspace=3, shadowOffset=(0, 0), text=attributes.caption, uppercase=1, color=ccConst.COLOR, fontsize=13)
        self.caption.SetAlpha(0.5)
        self.expanderIcon = eveIcon.Icon(name='expanderIcon', icon=[ccConst.ICON_EXPANDED, ccConst.ICON_EXPANDEDSINGLE][attributes.isSubmenu], parent=self.captionParent, state=uiconst.UI_DISABLED, align=uiconst.CENTERRIGHT, color=ccConst.COLOR50)
        if attributes.isSubmenu:
            Fill(parent=self.captionParent, color=(0.2, 0.2, 0.2, 0.4))
            self.caption.fontsize = 12
            bevelAlpha = 0.1
        else:
            self.randomButton = ButtonIcon(parent=self.colorPaletteParent, name='randomizeButton', pos=(0, 0, 22, 22), iconSize=32, align=uiconst.TOPRIGHT, hint=localization.GetByLabel('UI/Login/CharacterCreation/AssetMenu/RandomizeGroup'), idx=0, func=lambda : self.RandomizeGroup(attributes.groupID), texturePath='res:/UI/Texture/CharacterCreation/randomize_arrows.png', state=uiconst.UI_HIDDEN, iconClass=Sprite)
            Frame(parent=self.captionParent, frameConst=ccConst.MAINFRAME_INV, color=(1.0, 1.0, 1.0, 0.5))
            Fill(parent=self.captionParent, color=(0.0, 0.0, 0.0, 0.5))
            bevelAlpha = 0.2
        self.bevel = Frame(parent=self.captionParent, color=(1.0,
         1.0,
         1.0,
         bevelAlpha), frameConst=ccConst.FILL_BEVEL, state=uiconst.UI_HIDDEN)
        frame = Frame(parent=self.captionParent, frameConst=ccConst.FRAME_SOFTSHADE, color=(1.0, 1.0, 1.0, 0.5))
        frame.padding = (-12, -5, -12, -15)
        self.mainParent = Container(parent=self, align=uiconst.TOALL, name='mainParent')
        if attributes.modifier in ccConst.REMOVEABLE:
            self.removeParent = Container(parent=self.mainParent, align=uiconst.TOPRIGHT, name='removeParent', pickRadius=-1, state=uiconst.UI_HIDDEN, hint=localization.GetByLabel('UI/Login/CharacterCreation/AssetMenu/RemoveCharacterPart'), pos=(2, 2, 20, 20), opacity=0.75, idx=0)
            self.removeParent.OnClick = (self.RemoveAsset, self.removeParent)
            self.removeParent.OnMouseEnter = (self.OnGenericMouseEnter, self.removeParent)
            self.removeParent.OnMouseExit = (self.OnGenericMouseExit, self.removeParent)
            self.removeParent.modifier = attributes.modifier
            self.removeParent.icon = eveIcon.Icon(name='removeIcon', icon=ccConst.ICON_CLOSE, parent=self.removeParent, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT, color=ccConst.COLOR50, left=-10)
        modifier = attributes.modifier
        if modifier == ccConst.EYESGROUP:
            modifier = ccConst.eyes
        elif modifier == ccConst.HAIRGROUP:
            modifier = ccConst.hair
        Frame(parent=self.mainParent, frameConst=ccConst.MAINFRAME, color=(1.0, 1.0, 1.0, 0.5))
        self.assetParent = Container(parent=self.mainParent, align=uiconst.TOALL, name='assetParent', clipChildren=True, padding=(1, 1, 1, 1))
        self.modifier = modifier
        self.isSubmenu = attributes.isSubmenu
        self.groupID = attributes.groupID
        genderID = attributes.genderID
        if modifier is not None:
            if modifier == ccConst.BACKGROUNDGROUP:
                self.FULLHEIGHT = 170
                self.PrepareBackgrounds()
            elif modifier == ccConst.POSESGROUP:
                self.FULLHEIGHT = 170
                self.PreparePoses()
            elif modifier == ccConst.LIGHTSGROUP:
                self.PrepareLights()
            elif modifier == ccConst.SKINGROUP:
                self.FULLHEIGHT = 150
                self.PrepareSkinTone()
            elif modifier == ccConst.BODYGROUP:
                self.FULLHEIGHT = 70
                self.PrepareBodyShape()
            elif modifier == ccConst.hair:
                self.PrepareHair()
            elif modifier == ccConst.ARCHETYPESGROUP:
                self.PrepareArchetypes()
            elif type(modifier) is not types.IntType:
                self.FULLHEIGHT = 150
                if modifier == ccConst.eyeshadow:
                    self.FULLHEIGHT = 180
                itemTypes, activeIndex = uicore.layer.charactercreation.controller.GetAvailableStyles(modifier)
                categoryName = modifier.replace('/', '_')
                assetData = []
                numSpecialItems = 0
                for itemType in itemTypes:
                    if itemType[2] is not None:
                        numSpecialItems += 1
                    path = self.GetAssetThumbnailPath(itemType, genderID, categoryName, info.bloodlineID)
                    assetData.append((path, itemType, ''))

                self.browser = ImagePicker(parent=self.assetParent, align=uiconst.CENTER, imageWidth=96, imageHeight=96, zoomFactor=3.0, radius=150.0, images=assetData, numSpecialItems=numSpecialItems, OnSetValue=self.OnStylePicked)
                self.browser.assetCategory = modifier
            else:
                self.FULLHEIGHT = self.COLLAPSEHEIGHT
        Fill(parent=self.mainParent, color=(0.25, 0.25, 0.25, 0.25))
        self.mainParent.SetOpacity(0.0)
        self.height = self.captionParent.height
        self.expanderIcon.LoadIcon([ccConst.ICON_COLLAPSED, ccConst.ICON_COLLAPSEDSINGLE][self.isSubmenu])
        if not attributes.isSubmenu:
            self.state = uiconst.UI_PICKCHILDREN
        else:
            self.state = uiconst.UI_HIDDEN
        sm.RegisterNotify(self)

    def OnMouseEnter(self, *args):
        if self.randomButton:
            self.randomButton.Show()
        self.caption.SetRGBA(*eveColor.PRIMARY_BLUE)
        super(CharCreationAssetPicker, self).OnMouseEnter(*args)

    def OnMouseExit(self, *args):
        if self.randomButton:
            self.randomButton.Hide()
        self.caption.SetRGBA(*ccConst.COLOR)
        super(CharCreationAssetPicker, self).OnMouseExit(*args)

    def GetAssetThumbnailPath(self, itemType, genderID, categoryName, bloodlineID):
        path = ''
        if itemType[2] is not None:
            if genderID == 0:
                genderText = 'Female'
            else:
                genderText = 'Male'
            assetResPath = cfg.paperdollResources.Get(itemType[0]).resPath
            assetResPath = assetResPath.replace('/', '_').replace('.type', '')
            tempPath = 'res:/UI/Asset/mannequin/%s/%s_%s_%s.png' % (categoryName,
             itemType[2],
             genderText,
             assetResPath)
            if blue.paths.exists(tempPath):
                path = tempPath
        if not path:
            path = 'res:/UI/Asset/%s_g%s_b%s.png' % ('_'.join(list(itemType[1])).replace('/', '_'), genderID, bloodlineID)
        return path

    def GetArchetypeThumbnailPath(self, genderID, bloodlineID):
        return 'res:/UI/Asset/bloodline_g%s_b%s.png' % (genderID, bloodlineID)

    def RandomizeGroup(self, groupID, *args):
        ccDollManager = GetCharacterCreationDollManager()
        info = uicore.layer.charactercreation.controller.GetInfo()
        PlaySound('ui_icc_button_mouse_down_play')
        if ccDollManager.GetDoll(info.charID).busyUpdating:
            raise UserError('uiwarning01')
        uicore.layer.charactercreation.controller.LockNavigation()
        svc = sm.GetService('character')
        if info.genderID == ccConst.GENDERID_FEMALE:
            itemDict = ccConst.femaleRandomizeItems
        else:
            itemDict = ccConst.maleRandomizeItems
        if groupID in (ccConst.BACKGROUNDGROUP,
         ccConst.POSESGROUP,
         ccConst.LIGHTSGROUP,
         ccConst.ARCHETYPESGROUP):
            randomPick = random.choice(self.browser.images)
            self.browser.SetActiveData(randomPick)
        elif groupID == ccConst.BODYGROUP:
            svc.RandomizeCharacterSculpting(info.charID, info.raceID, doUpdate=False)
            self.UpdateControls('OnDollUpdated', setFocusOnActive=True)
            svc.UpdateTattoos(info.charID, doUpdate=True)
            uicore.layer.charactercreation.controller.TryStoreDna(False, 'Sculpting', force=True)
        else:
            groupList = []
            for key, value in itemDict.iteritems():
                if value == groupID:
                    groupList.append(key)

            if len(groupList) > 0:
                svc.RandomizeCharacterGroups(info.charID, info.raceID, groupList, doUpdate=True)
            for cat in groupList:
                if cat in ccConst.COLORMAPPING:
                    ccDollManager.UpdateColorSelectionFromDoll(cat)

        if groupID == ccConst.CLOTHESGROUP:
            ccDollManager.ToggleClothes(forcedValue=0)
        self._didRandomize = [groupID]
        uicore.layer.charactercreation.controller.UnlockNavigation()

    def GetAssetBloodlineID(self, fromBloodlineID):
        if fromBloodlineID in (1, 8, 7, 3, 2, 5, 6):
            assetBloodlineID = 1
        elif fromBloodlineID in (4,):
            assetBloodlineID = 4
        elif fromBloodlineID in (14, 12, 11, 13):
            assetBloodlineID = 14
        else:
            assetBloodlineID = 1
        return assetBloodlineID

    def OnDollUpdated(self, charID, redundantUpdate, *args):
        info = uicore.layer.charactercreation.controller.GetInfo()
        if charID == info.charID and self and not self.destroyed:
            self.UpdateControls('OnDollUpdated', setFocusOnActive=True)

    def OnPortraitPicked(self, *args):
        ccPortraitManager = GetCharacterCreationPortraitManager()
        pickerType = getattr(self, 'pickerType', None)
        if pickerType is None:
            return
        if pickerType == 'backgrounds':
            activeBackdrop = ccPortraitManager.GetBackdrop()
            if activeBackdrop:
                self.browser.SetActiveDataFromValue(activeBackdrop, focusOnSlot=True, doCallbacks=False, doYield=False)
        elif pickerType == 'poses':
            poseID = ccPortraitManager.GetPoseID()
            self.browser.SetActiveDataFromValue(poseID, focusOnSlot=True, doCallbacks=False, doYield=False)
        elif pickerType == 'lights':
            ccSceneManager = GetCharacterCreationSceneManager()
            currentLight = ccSceneManager.GetLight()
            self.browser.SetActiveDataFromValue(currentLight, focusOnSlot=True, doCallbacks=False, doYield=False)
            if ccUtil.IsSlowMachine():
                return
            self.BrowseLightColors(None)
            if self.colorPalette:
                intensitySlider = self.colorPalette.lights
                intensitySlider.SetValue(ccSceneManager.GetLightIntensity())

    def OnGenericMouseEnter(self, btn, *args):
        PlaySound('ui_icc_button_mouse_over_play')
        btn.icon.SetAlpha(1.0)
        if btn.sr.label:
            btn.label.SetAlpha(1.0)

    def OnGenericMouseExit(self, btn, *args):
        btn.icon.SetAlpha(0.5)
        if btn.sr.label:
            btn.label.SetAlpha(0.5)

    def OnGenericMouseDown(self, btn, *args):
        btn.icon.top += 1

    def OnGenericMouseUp(self, btn, *args):
        btn.icon.top -= 1

    def OnTuckBrowse(self, btn, *args):
        if getattr(self.colorPalette.tuckParent, 'tuckOptions', None) is None:
            return
        tuckOptions = self.colorPalette.tuckParent.tuckOptions
        currentIndex = self.colorPalette.tuckParent.tuckIndex
        if btn.name == 'leftBtn':
            if currentIndex == 0:
                currentIndex = len(tuckOptions) - 1
            else:
                currentIndex = currentIndex - 1
        elif currentIndex == len(tuckOptions) - 1:
            currentIndex = 0
        else:
            currentIndex = currentIndex + 1
        GetCharacterCreationDollManager().SetStyle(self.colorPalette.tuckParent.tuckPath, self.colorPalette.tuckParent.tuckStyle, tuckOptions[currentIndex])

    def PrepareHair(self):
        self.FULLHEIGHT = 170
        svc = sm.GetService('character')
        info = uicore.layer.charactercreation.controller.GetInfo()
        itemTypes, activeIndex = uicore.layer.charactercreation.controller.GetAvailableStyles(ccConst.hair)
        assetData = []
        for itemType in itemTypes:
            path = self.GetAssetThumbnailPath(itemType, info.genderID, ccConst.hair, info.bloodlineID)
            assetData.append((path, itemType, ''))

        subPar = Container(parent=self.assetParent, align=uiconst.TOTOP, height=130)
        self.browser = ImagePicker(parent=subPar, align=uiconst.CENTER, imageWidth=96, imageHeight=96, zoomFactor=3.0, radius=150.0, images=assetData, OnSetValue=self.OnStylePicked)
        self.browser.assetCategory = ccConst.hair
        Line(parent=self.assetParent, align=uiconst.TOTOP, padding=(6, 0, 6, 0), color=(1.0, 1.0, 1.0, 0.1))
        itemTypes, activeIndex = uicore.layer.charactercreation.controller.GetAvailableStyles(ccConst.eyebrows)
        assetData = []
        for itemType in itemTypes:
            assetData.append(('res:/UI/Asset/%s_g%s_b%s.png' % ('_'.join(list(itemType[1])).replace('/', '_'), info.genderID, info.bloodlineID), itemType, ''))

        subPar = Container(parent=self.assetParent, align=uiconst.TOTOP, height=92)
        removeParent = Container(parent=subPar, align=uiconst.TOPRIGHT, name='removeParent', pickRadius=-1, state=uiconst.UI_NORMAL, hint=localization.GetByLabel('UI/Login/CharacterCreation/AssetMenu/RemoveCharacterPart'), pos=(2, 2, 20, 20), opacity=0.75, idx=0)
        removeParent.OnMouseEnter = (self.OnGenericMouseEnter, removeParent)
        removeParent.OnMouseExit = (self.OnGenericMouseExit, removeParent)
        removeParent.modifier = ccConst.eyebrows
        removeParent.icon = eveIcon.Icon(name='removeIcon', icon=ccConst.ICON_CLOSE, parent=removeParent, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT, color=ccConst.COLOR50, left=-9)
        self.altbrowser = ImagePicker(parent=subPar, align=uiconst.CENTER, imageWidth=64, imageHeight=64, zoomFactor=3.0, radius=150.0, images=assetData, OnSetValue=self.OnStylePicked)
        self.altbrowser.removeParent = removeParent
        removeParent.OnClick = (self.RemoveHairAsset, removeParent, self.altbrowser)
        self.altbrowser.assetCategory = ccConst.eyebrows
        self.FULLHEIGHT += 80
        self.beardbrowser = None
        if info.genderID == 1:
            Line(parent=self.assetParent, align=uiconst.TOTOP, padding=(6, 0, 6, 0), color=(1.0, 1.0, 1.0, 0.1))
            itemTypes, activeIndex = uicore.layer.charactercreation.controller.GetAvailableStyles(ccConst.beard)
            assetData = []
            for itemType in itemTypes:
                assetData.append(('res:/UI/Asset/%s_g%s_b%s.png' % ('_'.join(list(itemType[1])).replace('/', '_'), info.genderID, info.bloodlineID), itemType, ''))

            subPar = Container(parent=self.assetParent, align=uiconst.TOTOP, height=92)
            removeParent = Container(parent=subPar, align=uiconst.TOPRIGHT, name='removeParent', pickRadius=-1, state=uiconst.UI_NORMAL, hint=localization.GetByLabel('UI/Login/CharacterCreation/AssetMenu/RemoveCharacterPart'), pos=(2, 2, 20, 20), opacity=0.75, idx=0)
            removeParent.OnMouseEnter = (self.OnGenericMouseEnter, removeParent)
            removeParent.OnMouseExit = (self.OnGenericMouseExit, removeParent)
            removeParent.modifier = ccConst.beard
            removeParent.icon = eveIcon.Icon(name='removeIcon', icon=ccConst.ICON_CLOSE, parent=removeParent, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT, color=ccConst.COLOR50, left=-9)
            self.beardbrowser = ImagePicker(parent=subPar, align=uiconst.CENTER, imageWidth=64, imageHeight=64, zoomFactor=3.0, radius=150.0, images=assetData, OnSetValue=self.OnStylePicked)
            self.beardbrowser.removeParent = removeParent
            removeParent.OnClick = (self.RemoveHairAsset, removeParent, self.beardbrowser)
            self.beardbrowser.assetCategory = ccConst.beard
            self.FULLHEIGHT += 90

    def PrepareArchetypes(self):
        self.FULLHEIGHT = 170
        self.modifier = None
        info = uicore.layer.charactercreation.controller.GetInfo()
        activeArchetypePath = None
        assetData = []
        for archetype in ccConst.AVAILABLE_ARCHETYPES:
            path = self.GetArchetypeThumbnailPath(info.genderID, archetype)
            assetData.append((path, (archetype, os.path.basename(path), None), ''))
            if archetype == info.bloodlineID:
                activeArchetypePath = os.path.basename(path)

        subPar = Container(parent=self.assetParent, align=uiconst.TOTOP, height=130)
        self.browser = ImagePicker(parent=subPar, align=uiconst.CENTER, imageWidth=96, imageHeight=96, zoomFactor=3.0, radius=150.0, images=assetData, OnSetValue=self.OnArchetypePicked)
        self.browser.assetCategory = ccConst.AVAILABLE_ARCHETYPES
        self.browser.SetActiveDataFromValue(activeArchetypePath, focusOnSlot=True, doCallbacks=False, doYield=False)

    def PrepareBodyShape(self):
        l, t, w, h = self.assetParent.GetAbsolute()
        sliderWidth = (w - 30) / 2
        left = 10
        for sModifier in (ccConst.muscle, ccConst.weight):
            slider = BitSlider(parent=self.assetParent, name=sModifier + '_slider', align=uiconst.CENTERLEFT, OnSetValue=self.OnSetSliderValue, sliderWidth=sliderWidth, left=left, top=7)
            left += sliderWidth + 10
            label = CCLabel(parent=slider, text=localization.GetByLabel(maleModifierDisplayNames.get(sModifier, 'UI/Login/CharacterCreation/AssetMenu/MissingCaption')), top=-18, color=ccConst.COLOR50)
            slider.modifier = sModifier

    def PrepareBackgrounds(self):
        self.modifier = None
        self.pickerType = 'backgrounds'
        images = []
        charSvc = sm.GetService('character')
        ccPortraitManager = GetCharacterCreationPortraitManager()
        activeBackdrop = ccPortraitManager.GetBackdrop()
        if not gfxsettings.Get(gfxsettings.UI_NCC_GREEN_SCREEN):
            if activeBackdrop is not None and ccPortraitManager.GetCurrentBackgroundID() < const.NCC_MIN_NORMAL_BACKGROUND_ID:
                activeBackdrop = None
        backgroundOptions = ccPortraitManager.GetAvailableBackgroundsPaths()
        if activeBackdrop not in backgroundOptions:
            activeBackdrop = None
        numSpecialItems = 0
        for background in backgroundOptions:
            resource = charSvc.GetPortraitResourceByPath(background)
            typeID = resource.typeID if resource else None
            bgID = resource.portraitResourceID if resource else -1
            if typeID:
                numSpecialItems += 1
                bgID = -bgID
            images.append((bgID, (background.replace('.dds', '_thumb.dds'), ('background', background, typeID), None)))

        images = SortListOfTuples(images)
        if activeBackdrop is None:
            activeBackdrop = random.choice(images)
            self.OnSetBackground(activeBackdrop[1][1])
            activeBackdrop = activeBackdrop[0]
        self.browser = ImagePicker(parent=self.assetParent, align=uiconst.CENTERTOP, top=-10, imageWidth=110, imageHeight=110, zoomFactor=3.0, radius=150.0, images=images, numSpecialItems=numSpecialItems, OnSetValue=self.OnAltSetAsset)
        if activeBackdrop:
            self.browser.SetActiveDataFromValue(activeBackdrop, focusOnSlot=True, doCallbacks=False, doYield=False)

    def PreparePoses(self):
        info = uicore.layer.charactercreation.controller.GetInfo()
        self.modifier = None
        self.pickerType = 'poses'
        posesData = []
        assetBloodlineID = self.GetAssetBloodlineID(info.bloodlineID)
        for i in range(ccConst.POSERANGE):
            posesData.append(('res:/UI/Asset/%s_g%s_b%s.png' % ('pose_%s' % i, info.genderID, assetBloodlineID), ('pose', i), None))

        self.browser = ImagePicker(parent=self.assetParent, align=uiconst.CENTERTOP, top=-10, imageWidth=110, imageHeight=110, zoomFactor=3.0, radius=150.0, images=posesData, OnSetValue=self.OnAltSetAsset)
        activePose = int(GetCharacterCreationPortraitManager().GetPoseID())
        if activePose:
            pose = posesData[activePose]
        else:
            pose = random.choice(posesData)
        self.OnAltSetAsset(pose)
        self.browser.SetActiveDataFromValue(pose[1][1], focusOnSlot=True, doCallbacks=False, doYield=False)

    def PrepareLights(self):
        info = uicore.layer.charactercreation.controller.GetInfo()
        self.modifier = None
        self.pickerType = 'lights'
        ccSceneManager = GetCharacterCreationSceneManager()
        currentLight = ccSceneManager.GetLight()
        currentLightColor = ccSceneManager.GetLightColor()
        lightingList = ccConst.LIGHT_SETTINGS_ID
        lightingColorList = ccConst.LIGHT_COLOR_SETTINGS_ID
        currentIndex = lightingColorList.index(currentLightColor)
        defaultThumbnailColor = lightingColorList[0]
        lightStyles = []
        assetBloodlineID = self.GetAssetBloodlineID(info.bloodlineID)
        for each in lightingList:
            lightStyles.append(('res:/UI/Asset/%s_g%s_b%s.png' % ('light_%s_%s' % (each, defaultThumbnailColor), info.genderID, assetBloodlineID), ('light', each), None))

        self.browser = ImagePicker(parent=self.assetParent, align=uiconst.CENTERTOP, top=-10, imageWidth=110, imageHeight=110, zoomFactor=3.0, radius=150.0, images=lightStyles, OnSetValue=self.OnAltSetAsset)
        if self.colorPalette is None:
            self.CreateColorPallette(isLights=True)
        self.colorPalette.tuckParent.display = True
        self.browser.SetActiveDataFromValue(currentLight, focusOnSlot=True, doCallbacks=False, doYield=False)
        self.colorPalette.SetTuckingCounter(currentIndex + 1, len(lightingColorList))

    def BrowseLightColors(self, btn, *args):
        ccSceneManager = GetCharacterCreationSceneManager()
        currentLightColor = ccSceneManager.GetLightColor()
        lightingColorList = ccConst.LIGHT_COLOR_SETTINGS_ID
        currentIndex = lightingColorList.index(currentLightColor)
        if btn:
            if btn.name == 'leftBtn':
                currentIndex -= 1
                if currentIndex == -1:
                    currentIndex = len(lightingColorList) - 1
            else:
                currentIndex += 1
                if currentIndex == len(lightingColorList):
                    currentIndex = 0
        ccSceneManager.SetLightColor(lightingColorList[currentIndex])
        self.colorPalette.SetTuckingCounter(currentIndex + 1, len(lightingColorList))

    def OnAltSetAsset(self, assetData, *args):
        if assetData:
            ccSceneManager = GetCharacterCreationSceneManager()
            ccPortraitManager = GetCharacterCreationPortraitManager()
            thumb, assetData, hiliteResPath = assetData
            k = assetData[0]
            v = assetData[1]
            if k == 'background':
                ccPortraitManager.SetBackdrop(v)
                ccPortraitManager.UpdateBackdrop()
            elif k == 'light':
                ccSceneManager.SetLights(v)
            elif k == 'pose':
                ccPortraitManager.SetPoseID(assetData[1])
                info = uicore.layer.charactercreation.controller.GetInfo()
                sm.GetService('character').ChangePose(v, info.charID)
                if ccSceneManager.camera is not None:
                    ccSceneManager.camera.UpdatePortraitInfo()
            self.UpdateControls('OnAltSetAsset')

    def OnSetBackground(self, bgPath, *args):
        ccPortraitManager = GetCharacterCreationPortraitManager()
        ccPortraitManager.SetBackdrop(bgPath)
        ccPortraitManager.UpdateBackdrop()

    def OnColorPaletteChanged(self, width):
        self.colorPaletteParent.width = width

    def PrepareSkinTone(self):
        itemTypes, activeIndex = uicore.layer.charactercreation.controller.GetAvailableStyles(ccConst.skintype)
        itemsWithDisplayColor = []
        for i, each in enumerate(itemTypes):
            itemsWithDisplayColor.append(('colorName', ccConst.SKINTYPECOLORS.get(str(each[1][2]), (1, 1, 1, 1)), each))

        colorPicker = CharCreationColorPicker(parent=self.assetParent, colors=itemsWithDisplayColor, align=uiconst.CENTERLEFT, OnSetValue=self.OnSkinTypePicked, activeColorIndex=activeIndex)
        colorPicker.modifier = ccConst.skintype
        l, t, w, h = self.assetParent.GetAbsolute()
        sliderWidth = w - 130 - 10
        left = 10
        top = -32
        for sModifier in (ccConst.skinaging, ccConst.freckles, ccConst.scarring):
            itemTypes, activeIdx = uicore.layer.charactercreation.controller.GetAvailableStyles(sModifier)
            bitAmount = len(itemTypes)
            slider = BitSlider(parent=self.assetParent, name=sModifier + '_slider', align=uiconst.CENTERLEFT, OnSetValue=self.OnSetSliderValue, bitAmount=bitAmount, sliderWidth=sliderWidth, left=130, top=top)
            top += 32
            label = CCLabel(parent=slider, text=localization.GetByLabel(maleModifierDisplayNames.get(sModifier, 'UI/Login/CharacterCreation/AssetMenu/MissingCaption')), top=-18, color=ccConst.COLOR50)
            slider.modifier = sModifier

    def OnSetSliderValue(self, slider):
        value = slider.GetValue()
        ccDollManager = GetCharacterCreationDollManager()
        if slider.modifier in (ccConst.skinaging, ccConst.freckles, ccConst.scarring):
            itemTypes, activeIdx = uicore.layer.charactercreation.controller.GetAvailableStyles(slider.modifier)
            styleRange = 1.0 / len(itemTypes)
            portionalIndex = int(len(itemTypes) * (value + styleRange / 2))
            if portionalIndex == 0:
                ccDollManager.ClearCategory(slider.modifier)
            else:
                ccDollManager.SetItemType(itemTypes[portionalIndex - 1])
        else:
            ccDollManager.SetIntensity(slider.modifier, value)

    def ShowActiveItem(self, *args):
        if self.browser:
            active = self.browser.GetActiveData()
            if active:
                self.browser.SetActiveData(active)

    def RemoveAsset(self, button, *args):
        GetCharacterCreationDollManager().ClearCategory(button.modifier)
        if self.browser:
            self.browser.SetActiveData(None, focusOnSlot=False)
            self.CollapseColorPalette()

    def RemoveHairAsset(self, button, browser, *args):
        info = uicore.layer.charactercreation.controller.GetInfo()
        modifiers = sm.GetService('character').GetModifierByCategory(info.charID, button.modifier, getAll=True)
        for each in modifiers:
            GetCharacterCreationDollManager().ClearCategory(button.modifier)

    def OnCaptionEnter(self, *args):
        uicore.layer.charactercreation.controller.SetHintText(self.captionParent.modifier)
        sm.StartService('audio').SendUIEvent(unicode('ui_icc_menu_mouse_over_play'))
        self.caption.SetAlpha(1.0)
        self.expanderIcon.SetAlpha(1.0)
        if self.bevel:
            self.bevel.state = uiconst.UI_DISABLED

    def OnCaptionExit(self, *args):
        uicore.layer.charactercreation.controller.SetHintText(None)
        if not self.IsExpanded():
            self.caption.SetAlpha(0.5)
            self.expanderIcon.SetAlpha(0.5)
        if self.bevel:
            self.bevel.state = uiconst.UI_HIDDEN

    def Toggle(self, *args):
        sm.StartService('audio').SendUIEvent(unicode('ui_icc_button_mouse_down_play'))
        if self._expanded:
            self.Collapse()
        else:
            self.Expand()

    def IsExpanded(self):
        return self._expanded

    def UpdateControls(self, trigger = None, setFocusOnActive = False):
        ccDollManager = GetCharacterCreationDollManager()
        subMenus = self.GetMySubmenus()
        if not self.IsExpanded() or subMenus:
            if subMenus and self._didRandomize and self.groupID in self._didRandomize:
                self._didRandomize = None
                for each in subMenus:
                    each.UpdateControls('UpdateControls', setFocusOnActive=True)

            return
        try:
            if self.colorPalette:
                ccDollManager.ValidateColors(self.modifier)
                self.colorPalette.UpdatePalette()
        except Exception:
            if not self or self.destroyed:
                return
            raise

        info = uicore.layer.charactercreation.controller.GetInfo()
        charSvc = sm.GetService('character')
        containers = [ w for w in self.Find('trinity.Tr2Sprite2dContainer') ]
        browsersAndModifiers = [(self.browser, self.modifier)]
        if self.modifier == ccConst.hair:
            browsersAndModifiers.append((self.altbrowser, ccConst.eyebrows))
            if hasattr(self, 'beardbrowser'):
                browsersAndModifiers.append((self.beardbrowser, ccConst.beard))
        for browser, modifier in browsersAndModifiers:
            if browser and modifier is not None:
                if modifier == ccConst.beard:
                    activeMod = None
                    activeMods = charSvc.GetModifierByCategory(info.charID, modifier, getAll=True)
                    if activeMods:
                        if len(activeMods) == 1:
                            activeMod = activeMods[0]
                        else:
                            for a in activeMods:
                                if a.respath == ccConst.BASEBEARD:
                                    continue
                                activeMod = a
                                break
                            else:
                                activeMod = activeMods[0]

                else:
                    activeMod = charSvc.GetModifierByCategory(info.charID, modifier)
                    if activeMod and activeMod.name in ccConst.invisibleModifiers:
                        activeMod = None
                    if not activeMod and modifier in ccDollManager.clothesStorage:
                        activeMod = ccDollManager.clothesStorage.get(modifier, None)
                if activeMod:
                    uthread.new(self.SetActiveData_thread, browser, activeMod, setFocusOnActive)
                else:
                    browser.SetActiveData(None, focusOnSlot=False, doCallbacks=False)

        self.LoadTuckOptions()
        self.LoadRemoveOptions()
        colorPickers = [ each for each in containers if isinstance(each, CharCreationColorPicker) ]
        for colorPicker in colorPickers:
            if not getattr(colorPicker, 'modifier', None):
                continue
            itemTypes, activeIndex = uicore.layer.charactercreation.controller.GetAvailableStyles(colorPicker.modifier)
            if activeIndex is None:
                colorPicker.SetActiveColor(None, initing=True)
            else:
                activeColor = itemTypes[activeIndex]
                colorPicker.SetActiveColor(activeColor, initing=True)

        sliders = [ each for each in containers if isinstance(each, BitSlider) or isinstance(each, GradientSlider) ]
        for slider in sliders:
            if not getattr(slider, 'modifier', None):
                continue
            if slider.modifier in (ccConst.skinaging, ccConst.freckles, ccConst.scarring):
                itemTypes, activeIndex = uicore.layer.charactercreation.controller.GetAvailableStyles(slider.modifier)
                if not itemTypes:
                    continue
                if activeIndex is None:
                    activeIndex = 0
                else:
                    activeIndex = activeIndex + 1
                value = 1.0 / float(len(itemTypes)) * activeIndex
                slider.SetValue(value, doCallback=False)
            elif slider.modifier in ccConst.weight:
                weight = charSvc.GetCharacterWeight(info.charID)
                slider.SetValue(weight, doCallback=False)
            elif slider.modifier == ccConst.muscle:
                muscularity = charSvc.GetCharacterMuscularity(info.charID)
                slider.SetValue(muscularity, doCallback=False)
            elif slider.modifier == ccConst.hair:
                slider.SetValue(charSvc.GetHairDarkness(info.charID), doCallback=False)
                slider.parent.SetGradientsColor()
            else:
                activeMod = charSvc.GetModifierByCategory(info.charID, slider.modifier)
                if activeMod:
                    if slider.sliderType == 'intensity':
                        slider.SetValue(charSvc.GetWeightByCategory(info.charID, slider.modifier))
                        slider.parent.SetGradientsColor()
                    elif slider.sliderType == 'specularity':
                        slider.SetValue(charSvc.GetColorSpecularityByCategory(info.charID, slider.modifier))

    def SetActiveData_thread(self, browser, activeMod, setFocusOnActive):
        typeData = activeMod.GetTypeData()
        if typeData[0].startswith(('makeup', 'beard')) and typeData[2] in ('default', 'none'):
            typeData = (typeData[0], typeData[1], '')
        if browser and hasattr(browser, 'SetActiveDataFromValue'):
            browser.SetActiveDataFromValue(typeData, doCallbacks=False, focusOnSlot=setFocusOnActive, doYield=False)
            if self.colorPalette:
                self.colorPalette.TryReloadColors()
            self.LoadTuckOptions()
            self.LoadRemoveOptions()

    def DebugRoleCheck(self):
        mask = ROLE_CONTENT | ROLE_QA | ROLE_PROGRAMMER | ROLE_GML
        if session.role & mask and not prefs.GetValue('CCHideAssetDebugText', False):
            return True
        else:
            return False

    def UpdatePrefs(self, state):
        currentMenuState = settings.user.ui.Get('assetMenuState', {ccConst.BODYGROUP: 1})
        key = self.modifier or 'group_%s' % getattr(self, 'groupID', '')
        currentMenuState[key] = state
        settings.user.ui.Set('assetMenuState', currentMenuState)

    def Expand(self, initing = False):
        if self._expanded:
            return
        self._expanded = True
        self._expandTime = blue.os.GetWallclockTime()
        self.caption.SetAlpha(1.0)
        self.expanderIcon.SetAlpha(1.0)
        self.CheckIfOversize()
        if self.isSubmenu or not self.GetMySubmenus():
            self.height = self.GetCollapsedHeight()
            animations.FadeIn(self.mainParent, duration=0.05)
            uicore.effect.MorphUIMassSpringDamper(self, 'height', self.GetExpandedHeight(), newthread=True, float=False, frequency=15.0, dampRatio=0.75)
            self.Show()
        else:
            mySubs = self.GetMySubmenus()
            menuState = settings.user.ui.Get('assetMenuState', {ccConst.BODYGROUP: True})
            for subMenu in mySubs:
                key = subMenu.modifier or 'group_%s' % getattr(subMenu, 'groupID', '')
                if menuState.get(key, False):
                    subMenu.Expand(True)
                else:
                    subMenu.height = 0
                    subMenu.Show()
                    uicore.effect.MorphUIMassSpringDamper(subMenu, 'height', subMenu.GetCollapsedHeight(), newthread=True, float=False, frequency=15.0, dampRatio=0.75)

        self.CheckIfOversize()
        if self.modifier in ccConst.COLORMAPPING or self.modifier in ccConst.TUCKMAPPING:
            uthread.new(self.ExpandColorPalette)
        self.UpdateControls('Expand', setFocusOnActive=True)
        self.UpdatePrefs(True)
        self.expanderIcon.LoadIcon([ccConst.ICON_EXPANDED, ccConst.ICON_EXPANDEDSINGLE][self.isSubmenu])

    def ExpandColorPalette(self, initing = False, *args):
        blue.pyos.synchro.SleepWallclock(500)
        if hasattr(self, 'sr'):
            self.CreateColorPallette()
        if self.browser and self.IsExpanded():
            info = uicore.layer.charactercreation.controller.GetInfo()
            activeMod = sm.GetService('character').GetModifierByCategory(info.charID, self.modifier)
            if activeMod and (uicore.uilib.mouseOver is self or uicore.uilib.mouseOver.IsUnder(self)):
                self.colorPalette.ExpandPalette()

    def CreateColorPallette(self, isLights = False, *args):
        if self.colorPalette is None:
            maxPaletteWidth = int(uicore.desktop.width / 8)
            if isLights:
                browseFunction = self.BrowseLightColors
            else:
                browseFunction = self.OnTuckBrowse
            self.colorPalette = CCColorPalette(name='CCColorPalette', parent=self.colorPaletteParent, align=uiconst.TOPRIGHT, pos=(0,
             self.GetCollapsedHeight(),
             CCColorPalette.COLORPALETTEWIDTH,
             0), modifier=self.modifier, state=uiconst.UI_HIDDEN, maxPaletteHeight=self.GetExpandedHeight(), maxPaletteWidth=maxPaletteWidth, browseFunction=browseFunction, bgColor=(0.0, 0.0, 0.0, 0.25), isLights=isLights)

    def CheckIfOversize(self, *args):
        self.parent.parent.CheckIfOversize(currentPicker=self)

    def GetCollapsedHeight(self):
        return self.captionParent.height

    def GetExpandedHeight(self):
        return self.FULLHEIGHT

    def Collapse(self):
        self._expanded = False
        self.CollapseColorPalette()
        if self._expanded:
            return
        animations.FadeOut(self.mainParent, duration=0.15)
        if self.isSubmenu or not self.GetMySubmenus():
            uicore.effect.MorphUIMassSpringDamper(self, 'height', self.captionParent.height, newthread=1, float=False, frequency=15.0, dampRatio=1.0)
        else:
            mySubs = self.GetMySubmenus()
            hideHeight = 0
            for subMenu in mySubs:
                if subMenu.IsExpanded():
                    subMenu.Collapse()

            for subMenu in mySubs:
                subMenu.Hide()

        self.expanderIcon.LoadIcon([ccConst.ICON_COLLAPSED, ccConst.ICON_COLLAPSEDSINGLE][self.isSubmenu])
        if uicore.uilib.mouseOver is not self.captionParent:
            self.OnCaptionExit()
        self.UpdatePrefs(False)

    def CollapseColorPalette(self, *args):
        if self.colorPalette:
            self.colorPalette.CollapsePalette(push=True)

    def GetMySubmenus(self):
        ret = []
        if self.isSubmenu:
            return []
        for each in self.parent.children:
            if not hasattr(each, 'groupID'):
                continue
            if each is not self and each.groupID == self.groupID and getattr(each, 'isSubmenu', False):
                ret.append(each)

        return ret

    def GetCurrentModifierValue(self, modifierPath):
        info = uicore.layer.charactercreation.controller.GetInfo()
        modifier = sm.GetService('character').GetModifiersByCategory(info.charID, modifierPath)
        if modifier:
            return modifier[0].weight
        return 0.0

    def OnStylePicked(self, assetData, *args):
        if assetData:
            info = uicore.layer.charactercreation.controller.GetInfo()
            thumb, itemType, hiliteResPath = assetData
            weight = 1.0
            if self.colorIntensitySlider:
                weight = self.colorIntensitySlider.GetValue()
            GetCharacterCreationDollManager().SetItemType(itemType, weight=weight)
            uthread.new(self.UpdateControls, 'OnStylePicked')

    def OnSkinTypePicked(self, itemType, *args):
        if itemType:
            ccDollManager = GetCharacterCreationDollManager()
            info = uicore.layer.charactercreation.controller.GetInfo()
            ccDollManager.ClearCategory(ccConst.skintone, doUpdate=False)
            sm.GetService('character').characterMetadata[info.charID].typeColors.pop(ccConst.skintone, None)
            ccDollManager.SetItemType(itemType)
            uthread.new(self.UpdateControls, 'OnSkinTypePicked')

    def OnArchetypePicked(self, assetData, *args):
        if assetData:
            uicore.layer.charactercreation.controller.SelectBloodline(assetData[1][0])

    def LoadRemoveOptions(self, *args):
        if self.modifier == ccConst.hair:
            return self.LoadRemoveHairOptions()
        if not self.browser or not self.IsExpanded() or self.state == uiconst.UI_HIDDEN or self.modifier not in ccConst.REMOVEABLE:
            return
        self.SetRemoveIcon(self.modifier, self.removeParent)

    def SetRemoveIcon(self, modifier, icon):
        info = uicore.layer.charactercreation.controller.GetInfo()
        currentModifier = sm.GetService('character').GetModifierByCategory(info.charID, modifier)
        if not currentModifier or getattr(currentModifier, 'name', None) in ccConst.invisibleModifiers:
            if icon:
                icon.Hide()
        elif icon:
            icon.Show()

    def LoadRemoveHairOptions(self, *args):
        if not self.IsExpanded() or self.state == uiconst.UI_HIDDEN:
            return
        if self.altbrowser:
            self.SetRemoveIcon(ccConst.eyebrows, self.altbrowser.removeParent)
        if self.beardbrowser:
            self.SetRemoveIcon(ccConst.beard, self.beardbrowser.removeParent)

    def LoadTuckOptions(self, *args):
        if not self.browser or not self.IsExpanded() or self.state == uiconst.UI_HIDDEN or self.modifier not in ccConst.TUCKMAPPING:
            if getattr(self, 'pickerType', None) == 'lights' and ccUtil.IsSlowMachine():
                self.colorPalette.tuckParent.display = False
            return
        if self.colorPalette is None:
            self.CreateColorPallette()
        if self.colorPalette is None:
            return
        info = uicore.layer.charactercreation.controller.GetInfo()
        currentModifier = sm.GetService('character').GetModifierByCategory(info.charID, self.modifier)
        activeData = None
        if self.browser and self.IsExpanded():
            activeData = self.browser.GetActiveData()
        hideTuck = True
        if activeData and currentModifier:
            tuckPath, requiredModifiers, subKey = ccConst.TUCKMAPPING[self.modifier]
            if requiredModifiers:
                haveRequired = False
                for each in requiredModifiers:
                    haveRequired = bool(sm.GetService('character').GetModifierByCategory(info.charID, each))
                    if haveRequired:
                        break

            else:
                haveRequired = True
            resPath, itemType, hiliteResPath = activeData
            if haveRequired:
                tuckModifier = sm.GetService('character').GetModifierByCategory(info.charID, tuckPath)
                if tuckModifier:
                    tuckVariations = tuckModifier.GetVariations()
                    if tuckVariations:
                        currentTuckVariation = tuckModifier.currentVariation
                        tuckStyle = tuckModifier.GetResPath().split('/')[-1]
                        if currentTuckVariation in tuckVariations:
                            tuckIndex = tuckVariations.index(currentTuckVariation)
                        else:
                            tuckIndex = 0
                        tuckParent = self.colorPalette.tuckParent
                        tuckParent.tuckOptions = tuckVariations
                        tuckParent.tuckIndex = tuckIndex
                        tuckParent.tuckPath = tuckPath
                        tuckParent.tuckStyle = tuckStyle
                        tuckParent.tuckResPath = tuckModifier.GetResPath()
                        self.colorPalette.SetTuckingCounter(tuckIndex + 1, len(tuckVariations))
                        hideTuck = False
        if hideTuck:
            if self.colorPalette.tuckParent.display == True:
                self.colorPalette.tuckParent.display = False
                animations.FadeOut(self.colorPalette.tuckParent, duration=0.125)
        else:
            self.colorPalette.tuckParent.display = True
            animations.FadeIn(self.colorPalette.tuckParent, duration=0.125)

    def OnColorPickedFromWheel(self, colorPicker, color, name):
        GetCharacterCreationDollManager().SetColorValue(colorPicker.modifier, (name, tuple(color)))
