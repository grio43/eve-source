#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation\assetMenu.py
import random
import types
import blue
import charactercreator.const as ccConst
import evegraphics.settings as gfxsettings
import localization
import uthread
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.sys import serviceConst
from carbon.common.script.util import timerstuff
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.util.various_unsorted import SortListOfTuples
from eve.client.script.ui import eveColor
from eve.client.script.ui.control import eveIcon, eveImagePicker
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.login.charcreation import ccUtil, charCreation, charCreationColorPicker
from eve.common.lib import appConst as appconst
from eve.client.script.ui.login.charcreation.label import CCLabel
from eveexceptions import UserError
from eveprefs import prefs
HAIRDARKNESS = 'hari_darkness'
HAIRSATURATION = 'hari_saturation'
GROUPNAMES = {ccConst.SKINGROUP: 'UI/Login/CharacterCreation/AssetMenu/Groups/Complexion',
 ccConst.HAIRGROUP: 'UI/Login/CharacterCreation/AssetMenu/Groups/Hair',
 ccConst.EYESGROUP: 'UI/Login/CharacterCreation/AssetMenu/Groups/Eyes',
 ccConst.MAKEUPGROUP: 'UI/Login/CharacterCreation/AssetMenu/Groups/Makeup',
 ccConst.SKINDETAILSGROUP: 'UI/Login/CharacterCreation/AssetMenu/Groups/SkinDetails',
 ccConst.CLOTHESGROUP: 'UI/Login/CharacterCreation/AssetMenu/Groups/Clothes',
 ccConst.BODYGROUP: 'UI/Login/CharacterCreation/AssetMenu/Groups/Shape',
 ccConst.BACKGROUNDGROUP: 'UI/Login/CharacterCreation/AssetMenu/Groups/Backgrounds',
 ccConst.POSESGROUP: 'UI/Login/CharacterCreation/AssetMenu/Groups/Poses',
 ccConst.LIGHTSGROUP: 'UI/Login/CharacterCreation/AssetMenu/Groups/Lights',
 ccConst.PIERCINGGROUP: 'UI/Login/CharacterCreation/AssetMenu/Groups/Piercings',
 ccConst.TATTOOGROUP: 'UI/Login/CharacterCreation/AssetMenu/Groups/Tattoos',
 ccConst.SCARSGROUP: 'UI/Login/CharacterCreation/AssetMenu/Groups/Scars',
 ccConst.PROSTHETICS: 'UI/Login/CharacterCreation/AssetMenu/Groups/Prosthetics',
 ccConst.AUGMENTATIONS: 'UI/Login/CharacterCreation/AssetMenu/Groups/Augmentations'}
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

class CharCreationAssetMenu(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.name = attributes.menuType or 'CharCreationAssetMenu'
        sm.GetService('cc').LogInfo('CharCreationAssetMenu::ApplyAttributes:: name = ', self.name)
        if attributes.genderID == 0:
            modifierNames = femaleModifierDisplayNames
        else:
            modifierNames = maleModifierDisplayNames
        self.mainContainter = Container(parent=self, name='mainAssetMenuCont', align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN)
        self.mainContainter.clipChildren = 1
        self.togglerIdx = None
        self.toggleFunc = attributes.toggleFunc
        self.bloodlineID = attributes.bloodlineID
        empireID = attributes.raceID
        if empireID == appconst.raceMinmatar:
            if self.bloodlineID not in [appconst.bloodlineBrutor, appconst.bloodlineVherokior, appconst.bloodlineSebiestor]:
                self.bloodlineID = appconst.bloodlineSebiestor
        elif empireID == appconst.raceAmarr:
            if self.bloodlineID not in [appconst.bloodlineAmarr, appconst.bloodlineKhanid, appconst.bloodlineNiKunni]:
                self.bloodlineID = appconst.bloodlineKhanid
        elif empireID == appconst.raceGallente:
            if self.bloodlineID not in [appconst.bloodlineGallente, appconst.bloodlineJinMei, appconst.bloodlineIntaki]:
                self.bloodlineID = appconst.bloodlineGallente
        elif empireID == appconst.raceCaldari:
            if self.bloodlineID not in [appconst.bloodlineAchura, appconst.bloodlineCivire, appconst.bloodlineDeteis]:
                self.bloodlineID = appconst.bloodlineCivire
        if self.toggleFunc:
            self.togglerIdx = idx = attributes.get('togglerIdx', -1)
            if idx == -1:
                padTop = 16
                padBottom = 4
            else:
                padTop = 4
                padBottom = 16
            self.menuToggler = CharCreationMenuToggler(parent=self.mainContainter, caption=localization.GetByLabel('UI/Login/CharacterCreation/AssetMenu/BodyModifications'), padTop=padTop, padBottom=padBottom, menuType=attributes.menuType, func=self.ToggleMenu, idx=idx)
        for groupID, modifiers in attributes.groups:
            if self._AreAllModifiersEmpty(modifiers):
                continue
            if type(groupID) == types.IntType:
                caption = localization.GetByLabel(GROUPNAMES.get(groupID, 'UI/Login/CharacterCreation/AssetMenu/MissingCaption'))
            else:
                caption = localization.GetByLabel(modifierNames.get(groupID, 'UI/Login/CharacterCreation/AssetMenu/MissingCaption'))
            CharCreationAssetPicker(parent=self.mainContainter, modifier=groupID, caption=caption, padTop=4, padBottom=4, genderID=attributes.genderID, bloodlineID=self.bloodlineID, charID=attributes.charID, isSubmenu=False, groupID=groupID)
            for modifier in modifiers:
                if self._IsModifierEmpty(modifier):
                    continue
                caption = localization.GetByLabel(modifierNames.get(modifier, 'UI/Login/CharacterCreation/AssetMenu/MissingCaption'))
                CharCreationAssetPicker(parent=self.mainContainter, modifier=modifier, caption=caption, padTop=-2, padBottom=4, genderID=attributes.genderID, bloodlineID=self.bloodlineID, isSubmenu=True, groupID=groupID)

        menuState = settings.user.ui.Get('assetMenuState', {ccConst.BODYGROUP: True})
        for pickerContainer in self.mainContainter.children:
            if isinstance(pickerContainer, CharCreationMenuToggler):
                continue
            key = pickerContainer.modifier or 'group_%s' % getattr(pickerContainer, 'groupID', '')
            if not pickerContainer.isSubmenu and menuState.get(key, 0):
                pickerContainer.Expand(initing=True)

        if self.togglerIdx and self.menuToggler:
            self.menuToggler.SetOrder(self.togglerIdx)

    def _AreAllModifiersEmpty(self, modifiers):
        return modifiers and not any([ not self._IsModifierEmpty(modifier) for modifier in modifiers ])

    def _IsModifierEmpty(self, modifier):
        if type(modifier) is types.IntType:
            return False
        itemTypes, _ = uicore.layer.charactercreation.controller.GetAvailableStyles(modifier)
        if itemTypes:
            return False
        return True

    def ToggleMenu(self, *args):
        if self.toggleFunc:
            self.toggleFunc()

    def CheckIfOversize(self, currentPicker = None):
        canCollapse = []
        totalExpandedHeight = 0
        for each in self.mainContainter.children:
            if not isinstance(each, CharCreationAssetPicker):
                continue
            if each.state == uiconst.UI_HIDDEN:
                continue
            if each.IsExpanded():
                if not each.isSubmenu:
                    subs = each.GetMySubmenus()
                    totalExpandedHeight += each.padTop + each.GetExpandedHeight() + each.padBottom
                    if each is not currentPicker and currentPicker not in each.GetMySubmenus():
                        canCollapse.append((each._expandTime, each))
                else:
                    totalExpandedHeight += each.padTop + each.GetExpandedHeight() + each.padBottom
                if each is not currentPicker and each.isSubmenu:
                    canCollapse.append((each._expandTime, each))
            else:
                totalExpandedHeight += each.padTop + each.GetCollapsedHeight() + each.padBottom

        canCollapse.sort()
        availableSpace = uicore.desktop.height - 150 - ccConst.BUTTON_AREA_HEIGHT
        if totalExpandedHeight > availableSpace:
            diff = totalExpandedHeight - availableSpace
            for expandTime, each in canCollapse:
                if each.IsExpanded():
                    uthread.new(each.Collapse)
                    diff -= each.GetExpandedHeight() - each.GetCollapsedHeight()
                if diff <= 0:
                    break


class CCColorPalette(ContainerAutoSize):
    default_state = uiconst.UI_NORMAL
    default_opacity = 0.0
    default_left = 6
    default_top = 22
    SIDEMARGIN = 6
    TOPMARGIN = 6
    COLORSIZE = 14
    MINCOLORSIZE = 10
    COLORGAP = 0
    COLORMARGIN = 1
    COLORPALETTEWIDTH = 124

    def ApplyAttributes(self, attributes):
        super(CCColorPalette, self).ApplyAttributes(attributes)
        self.modifier = attributes.modifier
        self.primaryColors = None
        self.secondaryColors = None
        self.OnSetValue = attributes.OnSetValue
        self.maxPaletteHeight = attributes.maxPaletteHeight or 200
        self.maxPaletteWidth = attributes.maxPaletteWidth
        self.startingWidth = self.width
        self.currentNumColorAreas = None
        self.browseFunction = attributes.browseFunction
        self.browseText = attributes.browseText
        self.isLights = attributes.isLights
        self._expanded = False
        self.fadeInThread = None
        self.fadeOutThread = None
        self.PrepareControls()

    def Close(self):
        if self.mouseOverTimer:
            self.mouseOverTimer.KillTimer()
        super(CCColorPalette, self).Close()

    def PrepareControls(self, reloading = None, *args):
        info = uicore.layer.charactercreation.controller.GetInfo()
        charSvc = sm.GetService('character')
        sliders = []
        if info.genderID == ccConst.GENDERID_FEMALE:
            facialHairText = localization.GetByLabel('UI/Login/CharacterCreation/AssetMenu/EyebrowsColor')
        else:
            facialHairText = localization.GetByLabel('UI/Login/CharacterCreation/AssetMenu/FacialHairColor')
        if ccUtil.HasUserDefinedWeight(self.modifier):
            sliders += [('intensity', localization.GetByLabel('UI/Login/CharacterCreation/AssetMenu/MakeupOpacity'), charSvc.GetWeightByCategory(info.charID, self.modifier))]
        if info.genderID == ccConst.GENDERID_FEMALE and ccUtil.HasUserDefinedSpecularity(self.modifier):
            sliders += [('specularity', localization.GetByLabel('UI/Login/CharacterCreation/AssetMenu/LipGloss'), charSvc.GetColorSpecularityByCategory(info.charID, self.modifier))]
        if self.modifier == ccConst.hair:
            sliders += [(HAIRDARKNESS, facialHairText, charSvc.GetHairDarkness(info.charID))]
        elif self.isLights:
            if not uicore.layer.charactercreation.controller.IsSlowMachine():
                sliders += [('lights', localization.GetByLabel('UI/Login/CharacterCreation/AssetMenu/Intensity'), uicore.layer.charactercreation.controller.GetLightIntensity())]
        self.Flush()
        self.height = 0
        self.width = self.startingWidth
        self.currentColorSize = self.COLORSIZE
        self.PrepareTuckControls()
        for referenceName, label, currentValue in sliders:
            extraParameters = {}
            if referenceName == 'intensity':
                sliderClass = charCreation.GradientSlider
                extraParameters = {'alphaValues': (0, 0)}
            elif referenceName == HAIRDARKNESS:
                sliderClass = charCreation.GradientSlider
            else:
                sliderClass = charCreation.BitSlider
            modifier = self.modifier or 'NotReallyModifier'
            slider = sliderClass(parent=self, name=(modifier + '_slider'), padTop=20, padLeft=0, align=uiconst.TOTOP, setvalue=currentValue, OnSetValue=self.SetSliderValue, sliderWidth=(self.COLORPALETTEWIDTH - self.SIDEMARGIN * 2 + 1), bitHeight=6, idx=0, left=self.SIDEMARGIN, **extraParameters)
            slider.modifier = modifier
            slider.sliderType = referenceName
            setattr(self, referenceName, slider)
            label = CCLabel(parent=slider, uppercase=1, shadowOffset=(0, 0), fontsize=9, letterspace=2, text=label, width=slider.width, color=ccConst.COLOR50)
            label.top = -label.textheight - 1

        self.previousWidth = self.width
        self.activePrimary = None
        self.activeSecondary = None
        if self.modifier in ccConst.COLORMAPPING:
            if reloading == 'oldColors':
                self.LoadColors(self.primaryColors, self.secondaryColors)
            else:
                self.PrepareCategoryColorOptions()
        self.SetGradientsColor()
        self.SetSizeAutomatically()
        self.mouseOverTimer = timerstuff.AutoTimer(50, self.CheckMouseOver)

    def SetSizeAutomatically(self):
        ContainerAutoSize.SetSizeAutomatically(self)
        if self.height > 0:
            self.padBottom = -8
        else:
            self.padBottom = 0

    def PrepareTuckControls(self, *args):
        self.tuckParent = Container(parent=self, name='tuckParent', align=uiconst.TOTOP, top=8, height=56, state=uiconst.UI_HIDDEN, padLeft=self.SIDEMARGIN, padRight=self.SIDEMARGIN)
        if self.isLights:
            browseText = localization.GetByLabel('UI/Login/CharacterCreation/AssetMenu/BrowseLightColors')
        else:
            browseText = localization.GetByLabel('UI/Login/CharacterCreation/AssetMenu/Tucking')
        CCLabel(parent=self.tuckParent, uppercase=1, shadowOffset=(0, 0), fontsize=9, letterspace=2, text=browseText, top=0, left=0, color=ccConst.COLOR50, idx=0)
        self.tuckParent.countLabel = CCLabel(parent=self.tuckParent, uppercase=1, shadowOffset=(0, 0), fontsize=9, letterspace=2, text='', top=16, left=0, color=ccConst.COLOR50, idx=0)
        self.tuckLeftBtn = ButtonIcon(parent=self.tuckParent, name='leftBtn', align=uiconst.TOPLEFT, pos=(0, 32, 20, 20), iconSize=32, func=self.OnTuckLeftButtonClicked, texturePath=ccConst.ICON_BACK)
        self.tuckRightBtn = ButtonIcon(parent=self.tuckParent, name='rightBtn', align=uiconst.TOPRIGHT, pos=(0, 32, 20, 20), iconSize=32, func=self.OnTuckRightButtonClicked, texturePath=ccConst.ICON_NEXT)

    def OnTuckRightButtonClicked(self):
        self.OnTuckButtonClicked(self.tuckRightBtn)

    def OnTuckLeftButtonClicked(self):
        self.OnTuckButtonClicked(self.tuckLeftBtn)

    def OnTuckButtonClicked(self, btn):
        if self.browseFunction is not None:
            self.browseFunction(btn)

    def SetTuckingCounter(self, current = 0, total = 0):
        self.tuckParent.countLabel.text = '%s/%s' % (current, total)

    def SetGradientsColor(self, displayColor = None):
        slidersToColor = []
        if self.activePrimary is None:
            return
        for slider in [getattr(self, HAIRDARKNESS, None), getattr(self.sr, 'intensity', None)]:
            if slider is None:
                continue
            if displayColor is None:
                displayColor = self.activePrimary.displayColor
            slidersToColor.append(slider)

        if displayColor is None:
            return
        gradientColor = (1.0, displayColor[:3])
        for slider in slidersToColor:
            slider.ChangeGradientColor(secondColor=gradientColor)

    def CheckMouseOver(self, *args):
        if uicore.uilib.leftbtn or uicore.uilib.rightbtn:
            return
        if self.parent is None:
            return
        grandParent = self.parent.parent
        if uicore.uilib.mouseOver is self or uicore.uilib.mouseOver is grandParent or uicore.uilib.mouseOver.IsUnder(grandParent):
            if grandParent.browser and grandParent.IsExpanded():
                activeData = grandParent.browser.GetActiveData()
                if not activeData:
                    return
                self.ExpandPalette()
                return
        if self._expanded:
            self.CollapsePalette()

    def ExpandPalette(self, *args):
        if self.fadeOutThread:
            self.fadeOutThread.kill()
            self.fadeOutThread = None
        if self.fadeInThread:
            return
        self._expanded = True
        self.left = 0
        self.fadeInThread = uthread.new(self.ShowPalette_thread)

    def ShowPalette_thread(self, *args):
        if self and not self.destroyed:
            self.state = uiconst.UI_NORMAL
        animations.FadeIn(self, duration=0.5, sleep=True)

    def CollapsePalette(self, push = False, *args):
        if self.fadeInThread:
            self.fadeInThread.kill()
            self.fadeInThread = None
        if self.fadeOutThread:
            return
        self._expanded = False
        if push:
            animations.MorphScalar(self, 'left', endVal=-self.COLORPALETTEWIDTH, duration=0.15)
            animations.FadeOut(self, duration=0.15)
        else:
            self.fadeOutThread = uthread.new(self.HidePalette_thread)

    def HidePalette_thread(self, *args):
        animations.FadeOut(self, duration=0.75, sleep=True)
        if self and not self.destroyed:
            self.state = uiconst.UI_HIDDEN

    def PrepareCategoryColorOptions(self):
        info = uicore.layer.charactercreation.controller.GetInfo()
        categoryColors = sm.GetService('character').GetAvailableColorsForCategory(self.modifier, info.genderID, info.raceID)
        if not categoryColors:
            return
        primary, secondary = categoryColors
        self.hasSecondary = bool(secondary)
        uicore.layer.charactercreation.controller.ValidateColors(self.modifier)
        self.LoadColors(primary, secondary)
        self.primaryColors = primary
        self.secondaryColors = secondary

    def UpdatePalette(self):
        self.HiliteActive()

    def HiliteActive(self):
        info = uicore.layer.charactercreation.controller.GetInfo()
        charSvc = sm.GetService('character')
        currentPrimaryName, currentSecondaryName = charSvc.GetTypeColors(info.charID, self.modifier)
        if not currentPrimaryName:
            return
        if getattr(self, 'colorControlsCont', None) is None:
            return
        for each in self.colorControlsCont.children:
            if not getattr(each, 'colorValue', None):
                continue
            each.activeFrame.state = uiconst.UI_HIDDEN
            if not self.hasSecondary:
                if each.colorName == currentPrimaryName:
                    each.activeFrame.state = uiconst.UI_DISABLED
                    self.activePrimary = each
                continue
            if each.colorName == currentPrimaryName:
                each.activeFrame.state = uiconst.UI_DISABLED
                self.activePrimary = each
            elif each.colorName == currentSecondaryName:
                each.activeFrame.state = uiconst.UI_DISABLED
                self.activeSecondary = each

    def GetNumColorAreas(self, *args):
        info = uicore.layer.charactercreation.controller.GetInfo()
        activeMod = sm.GetService('character').GetModifierByCategory(info.charID, self.modifier)
        if activeMod:
            return activeMod.metaData.numColorAreas

    def TryReloadColors(self, *args):
        numColorAreas = self.GetNumColorAreas()
        if numColorAreas is not None and self.currentNumColorAreas != numColorAreas:
            self.PrepareControls(reloading='oldColors')

    def LoadColors(self, primary, secondary):
        for each in self.children[:]:
            if each.name == 'colorPar':
                each.Close()

        if self.modifier == ccConst.hair:
            firstColourCaption = localization.GetByLabel('UI/Login/CharacterCreation/AssetMenu/HairRootColor')
            secondColourCaption = localization.GetByLabel('UI/Login/CharacterCreation/AssetMenu/HairColor')
        else:
            firstColourCaption = localization.GetByLabel('UI/Login/CharacterCreation/AssetMenu/NonHairColor')
            secondColourCaption = localization.GetByLabel('UI/Login/CharacterCreation/AssetMenu/NonHairSecondaryColor')
        numColorAreas = self.GetNumColorAreas()
        self.currentNumColorAreas = numColorAreas
        if numColorAreas is not None:
            if numColorAreas < 2:
                secondary = []
                if self.modifier == ccConst.hair:
                    firstColourCaption = localization.GetByLabel('UI/Login/CharacterCreation/AssetMenu/HairColor')
            if numColorAreas < 1:
                primary = []
        if not (primary or secondary):
            return
        top = 0
        left = self.SIDEMARGIN
        gapAndSize = self.currentColorSize + self.COLORGAP
        self.colorControlsCont = Container(parent=self, align=uiconst.TOTOP, idx=0)
        for colors in [primary, secondary]:
            if colors:
                top += 20
                inRow = self.width / gapAndSize
                rows = len(colors) / inRow + bool(len(colors) % inRow)
                colorHeight = top + rows * gapAndSize
                top = colorHeight
                self.SetSizeAutomatically()
                if self.height + colorHeight > self.maxPaletteHeight:
                    if self.width > self.maxPaletteWidth:
                        if self.currentColorSize > self.MINCOLORSIZE:
                            self.currentColorSize = self.currentColorSize - 1
                            self.width = self.startingWidth
                            return self.LoadColors(primary, secondary)
                    else:
                        self.width += gapAndSize
                        return self.LoadColors(primary, secondary)
                top += self.currentColorSize

        top = 0
        colorHeight = 0
        for colors, caption in ((primary, firstColourCaption), (secondary, secondColourCaption)):
            if not colors:
                continue
            left = self.SIDEMARGIN
            top += 4
            label = CCLabel(parent=self.colorControlsCont, uppercase=1, shadowOffset=(0, 0), fontsize=9, letterspace=2, text=caption, top=top, left=left, color=ccConst.COLOR50, idx=0)
            top += label.textheight + 3
            for data in colors:
                colorName, displayColor, colorValue = data
                colorPar = Container(parent=self.colorControlsCont, pos=(left,
                 top,
                 self.currentColorSize,
                 self.currentColorSize), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, name='colorPar', idx=0)
                colorPar.OnClick = (self.OnColorPicked, colorPar)
                colorPar.OnMouseEnter = (self.OnMouseEnterColor, colorPar)
                colorPar.OnMouseExit = (self.OnMouseExitColor, colorPar)
                colorPar.colorName = colorName
                colorPar.displayColor = displayColor
                colorPar.colorValue = colorValue
                colorPar.modifier = self.modifier
                colorPar.activeFrame = Frame(parent=colorPar, name='activeFrame', state=uiconst.UI_HIDDEN, frameConst=(ccConst.ICON_FOCUSFRAME, 15, -11), color=(1.0, 1.0, 1.0, 1.0))
                colorPar.hiliteFrame = Frame(parent=colorPar, name='hiliteFrame', state=uiconst.UI_HIDDEN, frameConst=(ccConst.ICON_FOCUSFRAME, 15, -11), color=(1.0, 1.0, 1.0, 0.25))
                f = Frame(parent=colorPar, color=(1.0, 1.0, 1.0, 0.05), padding=self.COLORMARGIN - 2)
                Fill(parent=colorPar, color=displayColor, padding=self.COLORMARGIN)
                colorHeight = top + self.currentColorSize
                left += self.currentColorSize + self.COLORGAP
                if left + self.currentColorSize > self.width:
                    top += self.currentColorSize + self.COLORGAP
                    left = self.SIDEMARGIN

            top += self.currentColorSize

        self.colorControlsCont.height = colorHeight
        self.HiliteActive()
        if self.width > self.previousWidth:
            sm.ScatterEvent('OnColorPaletteChanged', self.width)
        self.previousWidth = self.width

    def OnColorPicked(self, colorObj, *args):
        var1 = None
        var2 = None
        if self.hasSecondary:
            charID = uicore.layer.charactercreation.controller.GetInfo().charID
            currentPrimaryName, currentSecondaryName = sm.GetService('character').GetTypeColors(charID, self.modifier)
            if colorObj.colorName.lower().endswith('_bc'):
                var2 = (colorObj.colorName, colorObj.colorValue)
                for each in self.colorControlsCont.children:
                    if not getattr(each, 'colorValue', None):
                        continue
                    if each.colorName == currentPrimaryName:
                        var1 = (each.colorName, each.colorValue)

                if var1 is None:
                    return
            else:
                var1 = (colorObj.colorName, colorObj.colorValue)
                if currentSecondaryName:
                    for each in self.colorControlsCont.children:
                        if not getattr(each, 'colorValue', None):
                            continue
                        if each.colorName == currentSecondaryName:
                            var2 = (each.colorName, each.colorValue)

        else:
            var1 = (colorObj.colorName, colorObj.colorValue)
        if not colorObj.colorName.lower().endswith('_bc'):
            displayColor = colorObj.displayColor
            gradientColor = (1.0, displayColor[:3])
            self.SetGradientsColor(displayColor=displayColor)
        uicore.layer.charactercreation.controller.SetColorValue(self.modifier, var1, var2)

    def SetSliderValue(self, slider):
        value = slider.GetValue()
        if slider.sliderType == 'lights':
            intensity = slider.GetValue()
            uicore.layer.charactercreation.controller.SetLightIntensity(intensity)
        elif slider.sliderType == 'intensity':
            info = uicore.layer.charactercreation.controller.GetInfo()
            value = sm.GetService('character').GetTrueWeight(info.charID, slider.modifier, value)
            uicore.layer.charactercreation.controller.SetIntensity(slider.modifier, value)
        elif slider.sliderType == 'specularity':
            uicore.layer.charactercreation.controller.SetColorSpecularity(slider.modifier, value)
        elif slider.sliderType == HAIRDARKNESS:
            uicore.layer.charactercreation.controller.SetHairDarkness(value)

    def OnMouseWheel(self, *args):
        pass

    def OnMouseEnterColor(self, colorPar, *args):
        colorPar.hiliteFrame.state = uiconst.UI_DISABLED

    def OnMouseExitColor(self, colorPar, *args):
        colorPar.hiliteFrame.state = uiconst.UI_HIDDEN


class CharCreationAssetPicker(Container):
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

        self.bloodlineID = attributes.bloodlineID
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
        self._sliders = []
        self._colorPickers = []
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
                    path = self.GetAssetThumbnailPath(itemType, genderID, categoryName, self.bloodlineID)
                    assetData.append((path, itemType, ''))

                self.browser = eveImagePicker.ImagePicker(parent=self.assetParent, align=uiconst.CENTER, imageWidth=96, imageHeight=96, zoomFactor=3.0, radius=150.0, images=assetData, numSpecialItems=numSpecialItems, OnSetValue=self.OnStylePicked)
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

    def RandomizeGroup(self, groupID, *args):
        PlaySound('ui_icc_button_mouse_down_play')
        if uicore.layer.charactercreation.controller.doll.busyUpdating:
            raise UserError('uiwarning01')
        uicore.layer.charactercreation.controller.LockNavigation()
        svc = sm.GetService('character')
        info = uicore.layer.charactercreation.controller.GetInfo()
        if info.genderID == ccConst.GENDERID_FEMALE:
            itemDict = ccConst.femaleRandomizeItems
        else:
            itemDict = ccConst.maleRandomizeItems
        if groupID in (ccConst.BACKGROUNDGROUP, ccConst.POSESGROUP, ccConst.LIGHTSGROUP):
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
                    uicore.layer.charactercreation.controller.UpdateColorSelectionFromDoll(cat)

        if groupID == ccConst.CLOTHESGROUP:
            uicore.layer.charactercreation.controller.ToggleClothes(forcedValue=0)
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
        pickerType = getattr(self, 'pickerType', None)
        if pickerType is None:
            return
        if pickerType == 'backgrounds':
            activeBackdrop = uicore.layer.charactercreation.controller.GetBackdrop()
            if activeBackdrop:
                self.browser.SetActiveDataFromValue(activeBackdrop, focusOnSlot=True, doCallbacks=False, doYield=False)
        elif pickerType == 'poses':
            poseID = uicore.layer.charactercreation.controller.GetPoseId()
            self.browser.SetActiveDataFromValue(poseID, focusOnSlot=True, doCallbacks=False, doYield=False)
        elif pickerType == 'lights':
            currentLight = uicore.layer.charactercreation.controller.GetLight()
            self.browser.SetActiveDataFromValue(currentLight, focusOnSlot=True, doCallbacks=False, doYield=False)
            if uicore.layer.charactercreation.controller.IsSlowMachine():
                return
            self.BrowseLightColors(None)
            if self.colorPalette:
                intensitySlider = self.colorPalette.lights
                intensitySlider.SetValue(uicore.layer.charactercreation.controller.GetLightIntensity())

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
        uicore.layer.charactercreation.controller.SetStyle(self.colorPalette.tuckParent.tuckPath, self.colorPalette.tuckParent.tuckStyle, tuckOptions[currentIndex])

    def PrepareHair(self):
        self.FULLHEIGHT = 170
        svc = sm.GetService('character')
        info = uicore.layer.charactercreation.controller.GetInfo()
        itemTypes, activeIndex = uicore.layer.charactercreation.controller.GetAvailableStyles(ccConst.hair)
        assetData = []
        for itemType in itemTypes:
            path = self.GetAssetThumbnailPath(itemType, info.genderID, ccConst.hair, self.bloodlineID)
            assetData.append((path, itemType, ''))

        subPar = Container(parent=self.assetParent, align=uiconst.TOTOP, height=130)
        self.browser = eveImagePicker.ImagePicker(parent=subPar, align=uiconst.CENTER, imageWidth=96, imageHeight=96, zoomFactor=3.0, radius=150.0, images=assetData, OnSetValue=self.OnStylePicked)
        self.browser.assetCategory = ccConst.hair
        Line(parent=self.assetParent, align=uiconst.TOTOP, padding=(6, 0, 6, 0), color=(1.0, 1.0, 1.0, 0.1))
        itemTypes, activeIndex = uicore.layer.charactercreation.controller.GetAvailableStyles(ccConst.eyebrows)
        assetData = []
        for itemType in itemTypes:
            assetData.append(('res:/UI/Asset/%s_g%s_b%s.png' % ('_'.join(list(itemType[1])).replace('/', '_'), info.genderID, self.bloodlineID), itemType, ''))

        subPar = Container(parent=self.assetParent, align=uiconst.TOTOP, height=92)
        removeParent = Container(parent=subPar, align=uiconst.TOPRIGHT, name='removeParent', pickRadius=-1, state=uiconst.UI_NORMAL, hint=localization.GetByLabel('UI/Login/CharacterCreation/AssetMenu/RemoveCharacterPart'), pos=(2, 2, 20, 20), opacity=0.75, idx=0)
        removeParent.OnMouseEnter = (self.OnGenericMouseEnter, removeParent)
        removeParent.OnMouseExit = (self.OnGenericMouseExit, removeParent)
        removeParent.modifier = ccConst.eyebrows
        removeParent.icon = eveIcon.Icon(name='removeIcon', icon=ccConst.ICON_CLOSE, parent=removeParent, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT, color=ccConst.COLOR50, left=-9)
        self.altbrowser = eveImagePicker.ImagePicker(parent=subPar, align=uiconst.CENTER, imageWidth=64, imageHeight=64, zoomFactor=3.0, radius=150.0, images=assetData, OnSetValue=self.OnStylePicked)
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
                assetData.append(('res:/UI/Asset/%s_g%s_b%s.png' % ('_'.join(list(itemType[1])).replace('/', '_'), info.genderID, self.bloodlineID), itemType, ''))

            subPar = Container(parent=self.assetParent, align=uiconst.TOTOP, height=92)
            removeParent = Container(parent=subPar, align=uiconst.TOPRIGHT, name='removeParent', pickRadius=-1, state=uiconst.UI_NORMAL, hint=localization.GetByLabel('UI/Login/CharacterCreation/AssetMenu/RemoveCharacterPart'), pos=(2, 2, 20, 20), opacity=0.75, idx=0)
            removeParent.OnMouseEnter = (self.OnGenericMouseEnter, removeParent)
            removeParent.OnMouseExit = (self.OnGenericMouseExit, removeParent)
            removeParent.modifier = ccConst.beard
            removeParent.icon = eveIcon.Icon(name='removeIcon', icon=ccConst.ICON_CLOSE, parent=removeParent, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT, color=ccConst.COLOR50, left=-9)
            self.beardbrowser = eveImagePicker.ImagePicker(parent=subPar, align=uiconst.CENTER, imageWidth=64, imageHeight=64, zoomFactor=3.0, radius=150.0, images=assetData, OnSetValue=self.OnStylePicked)
            self.beardbrowser.removeParent = removeParent
            removeParent.OnClick = (self.RemoveHairAsset, removeParent, self.beardbrowser)
            self.beardbrowser.assetCategory = ccConst.beard
            self.FULLHEIGHT += 90

    def PrepareBodyShape(self):
        l, t, w, h = self.assetParent.GetAbsolute()
        sliderWidth = (w - 30) / 2
        left = 10
        for sModifier in (ccConst.muscle, ccConst.weight):
            slider = charCreation.BitSlider(parent=self.assetParent, name=sModifier + '_slider', align=uiconst.CENTERLEFT, OnSetValue=self.OnSetSliderValue, sliderWidth=sliderWidth, left=left, top=7)
            left += sliderWidth + 10
            label = CCLabel(parent=slider, text=localization.GetByLabel(maleModifierDisplayNames.get(sModifier, 'UI/Login/CharacterCreation/AssetMenu/MissingCaption')), top=-18, color=ccConst.COLOR50)
            slider.modifier = sModifier
            self._sliders.append(slider)

    def PrepareBackgrounds(self):
        self.modifier = None
        self.pickerType = 'backgrounds'
        images = []
        charSvc = sm.GetService('character')
        ccLayer = uicore.layer.charactercreation.controller
        activeBackdrop = ccLayer.GetBackdrop()
        if not gfxsettings.Get(gfxsettings.UI_NCC_GREEN_SCREEN):
            if activeBackdrop is not None and ccLayer.GetCurrentBackgroundID() < appconst.NCC_MIN_NORMAL_BACKGROUND_ID:
                activeBackdrop = None
        backgroundOptions = ccLayer.GetAvailableBackgroundsPaths()
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
        self.browser = eveImagePicker.ImagePicker(parent=self.assetParent, align=uiconst.CENTERTOP, top=-10, imageWidth=110, imageHeight=110, zoomFactor=3.0, radius=150.0, images=images, numSpecialItems=numSpecialItems, OnSetValue=self.OnAltSetAsset)
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

        self.browser = eveImagePicker.ImagePicker(parent=self.assetParent, align=uiconst.CENTERTOP, top=-10, imageWidth=110, imageHeight=110, zoomFactor=3.0, radius=150.0, images=posesData, OnSetValue=self.OnAltSetAsset)
        activePose = int(uicore.layer.charactercreation.controller.GetPoseId())
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
        currentLight = uicore.layer.charactercreation.controller.GetLight()
        currentLightColor = uicore.layer.charactercreation.controller.GetLightColor()
        lightingList = ccConst.LIGHT_SETTINGS_ID
        lightingColorList = ccConst.LIGHT_COLOR_SETTINGS_ID
        currentIndex = lightingColorList.index(currentLightColor)
        defaultThumbnailColor = lightingColorList[0]
        lightStyles = []
        assetBloodlineID = self.GetAssetBloodlineID(info.bloodlineID)
        for each in lightingList:
            lightStyles.append(('res:/UI/Asset/%s_g%s_b%s.png' % ('light_%s_%s' % (each, defaultThumbnailColor), info.genderID, assetBloodlineID), ('light', each), None))

        self.browser = eveImagePicker.ImagePicker(parent=self.assetParent, align=uiconst.CENTERTOP, top=-10, imageWidth=110, imageHeight=110, zoomFactor=3.0, radius=150.0, images=lightStyles, OnSetValue=self.OnAltSetAsset)
        if self.colorPalette is None:
            self.CreateColorPallette(isLights=True)
        self.colorPalette.tuckParent.display = True
        self.browser.SetActiveDataFromValue(currentLight, focusOnSlot=True, doCallbacks=False, doYield=False)
        self.colorPalette.SetTuckingCounter(currentIndex + 1, len(lightingColorList))

    def BrowseLightColors(self, btn, *args):
        currentLightColor = uicore.layer.charactercreation.controller.GetLightColor()
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
        uicore.layer.charactercreation.controller.SetLightColor(lightingColorList[currentIndex])
        self.colorPalette.SetTuckingCounter(currentIndex + 1, len(lightingColorList))

    def OnAltSetAsset(self, assetData, *args):
        if assetData:
            thumb, assetData, hiliteResPath = assetData
            k = assetData[0]
            v = assetData[1]
            if k == 'background':
                uicore.layer.charactercreation.controller.SetBackdrop(v)
                uicore.layer.charactercreation.controller.UpdateBackdrop()
            elif k == 'light':
                uicore.layer.charactercreation.controller.SetLights(v)
            elif k == 'pose':
                uicore.layer.charactercreation.controller.SetPoseID(assetData[1])
                info = uicore.layer.charactercreation.controller.GetInfo()
                sm.GetService('character').ChangePose(v, info.charID)
                if uicore.layer.charactercreation.controller.camera is not None:
                    uicore.layer.charactercreation.controller.camera.UpdatePortraitInfo()
            self.UpdateControls('OnAltSetAsset')

    def OnSetBackground(self, bgPath, *args):
        uicore.layer.charactercreation.controller.SetBackdrop(bgPath)
        uicore.layer.charactercreation.controller.UpdateBackdrop()

    def OnColorPaletteChanged(self, width):
        self.colorPaletteParent.width = width

    def PrepareSkinTone(self):
        itemTypes, activeIndex = uicore.layer.charactercreation.controller.GetAvailableStyles(ccConst.skintype)
        itemsWithDisplayColor = []
        for i, each in enumerate(itemTypes):
            itemsWithDisplayColor.append(('colorName', ccConst.SKINTYPECOLORS.get(str(each[1][2]), (1, 1, 1, 1)), each))

        colorPicker = charCreationColorPicker.CharCreationColorPicker(parent=self.assetParent, align=uiconst.CENTERLEFT, colors=itemsWithDisplayColor, OnSetValue=self.OnSkinTypePicked, activeColorIndex=activeIndex)
        colorPicker.modifier = ccConst.skintype
        self._colorPickers.append(colorPicker)
        l, t, w, h = self.assetParent.GetAbsolute()
        sliderWidth = w - 130 - 10
        left = 10
        top = -32
        for sModifier in (ccConst.skinaging, ccConst.freckles, ccConst.scarring):
            itemTypes, activeIdx = uicore.layer.charactercreation.controller.GetAvailableStyles(sModifier)
            bitAmount = len(itemTypes)
            slider = charCreation.BitSlider(parent=self.assetParent, name=sModifier + '_slider', align=uiconst.CENTERLEFT, OnSetValue=self.OnSetSliderValue, bitAmount=bitAmount, sliderWidth=sliderWidth, left=130, top=top)
            top += 32
            label = CCLabel(parent=slider, text=localization.GetByLabel(maleModifierDisplayNames.get(sModifier, 'UI/Login/CharacterCreation/AssetMenu/MissingCaption')), top=-18, color=ccConst.COLOR50)
            slider.modifier = sModifier
            self._sliders.append(slider)

    def OnSetSliderValue(self, slider):
        value = slider.GetValue()
        if slider.modifier in (ccConst.skinaging, ccConst.freckles, ccConst.scarring):
            itemTypes, activeIdx = uicore.layer.charactercreation.controller.GetAvailableStyles(slider.modifier)
            styleRange = 1.0 / len(itemTypes)
            portionalIndex = int(len(itemTypes) * (value + styleRange / 2))
            if portionalIndex == 0:
                uicore.layer.charactercreation.controller.ClearCategory(slider.modifier)
            else:
                uicore.layer.charactercreation.controller.SetItemType(itemTypes[portionalIndex - 1])
        else:
            uicore.layer.charactercreation.controller.SetIntensity(slider.modifier, value)

    def ShowActiveItem(self, *args):
        if self.browser:
            active = self.browser.GetActiveData()
            if active:
                self.browser.SetActiveData(active)

    def RemoveAsset(self, button, *args):
        uicore.layer.charactercreation.controller.ClearCategory(button.modifier)
        if self.browser:
            self.browser.SetActiveData(None, focusOnSlot=False)
            self.CollapseColorPalette()

    def RemoveHairAsset(self, button, browser, *args):
        info = uicore.layer.charactercreation.controller.GetInfo()
        modifiers = sm.GetService('character').GetModifierByCategory(info.charID, button.modifier, getAll=True)
        for each in modifiers:
            uicore.layer.charactercreation.controller.ClearCategory(button.modifier)

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
        subMenus = self.GetMySubmenus()
        if not self.IsExpanded() or subMenus:
            if subMenus and self._didRandomize and self.groupID in self._didRandomize:
                self._didRandomize = None
                for each in subMenus:
                    each.UpdateControls('UpdateControls', setFocusOnActive=True)

            return
        try:
            if self.colorPalette:
                uicore.layer.charactercreation.controller.ValidateColors(self.modifier)
                self.colorPalette.UpdatePalette()
        except Exception:
            if not self or self.destroyed:
                return
            raise

        info = uicore.layer.charactercreation.controller.GetInfo()
        charSvc = sm.GetService('character')
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
                    if not activeMod and modifier in uicore.layer.charactercreation.controller.clothesStorage:
                        activeMod = uicore.layer.charactercreation.controller.clothesStorage.get(modifier, None)
                if activeMod:
                    uthread.new(self.SetActiveData_thread, browser, activeMod, setFocusOnActive)
                else:
                    browser.SetActiveData(None, focusOnSlot=False, doCallbacks=False)

        self.LoadTuckOptions()
        self.LoadRemoveOptions()
        for colorPicker in self._colorPickers:
            if not getattr(colorPicker, 'modifier', None):
                continue
            itemTypes, activeIndex = uicore.layer.charactercreation.controller.GetAvailableStyles(colorPicker.modifier)
            if activeIndex is None:
                colorPicker.SetActiveColor(None, initing=True)
            else:
                activeColor = itemTypes[activeIndex]
                colorPicker.SetActiveColor(activeColor, initing=True)

        for slider in self._sliders:
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
        mask = serviceConst.ROLE_CONTENT | serviceConst.ROLE_QA | serviceConst.ROLE_PROGRAMMER | serviceConst.ROLE_GML
        if eve.session.role & mask and not prefs.GetValue('CCHideAssetDebugText', False):
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
            uicore.layer.charactercreation.controller.SetItemType(itemType, weight=weight)
            uthread.new(self.UpdateControls, 'OnStylePicked')

    def OnSkinTypePicked(self, itemType, *args):
        if itemType:
            info = uicore.layer.charactercreation.controller.GetInfo()
            uicore.layer.charactercreation.controller.ClearCategory(ccConst.skintone, doUpdate=False)
            sm.GetService('character').characterMetadata[info.charID].typeColors.pop(ccConst.skintone, None)
            uicore.layer.charactercreation.controller.SetItemType(itemType)
            uthread.new(self.UpdateControls, 'OnSkinTypePicked')

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
            if getattr(self, 'pickerType', None) == 'lights' and uicore.layer.charactercreation.controller.IsSlowMachine():
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
        uicore.layer.charactercreation.controller.SetColorValue(colorPicker.modifier, (name, tuple(color)))


class CharCreationMenuToggler(Container):
    __notifyevents__ = ['OnColorPaletteChanged']
    FULLHEIGHT = 22
    COLLAPSEHEIGHT = 22
    default_align = uiconst.TOTOP
    default_left = 0
    default_top = 0
    default_width = 0
    default_height = COLLAPSEHEIGHT
    default_pos = None
    default_name = 'CharCreationMenuToggler'
    default_state = uiconst.UI_PICKCHILDREN

    def ApplyAttributes(self, attributes):
        for each in uicore.layer.main.children:
            if each.name == self.default_name:
                each.Close()

        info = uicore.layer.charactercreation.controller.GetInfo()
        Container.ApplyAttributes(self, attributes)
        if attributes.parent is None:
            uicore.layer.main.children.append(self)
        self.colorPaletteParent = Container(parent=self, align=uiconst.TOLEFT, width=CCColorPalette.COLORPALETTEWIDTH, name='colorPaletteParent', state=uiconst.UI_DISABLED)
        self.captionParent = Container(parent=self, align=uiconst.TOTOP, height=self.COLLAPSEHEIGHT, name='captionParent', state=uiconst.UI_NORMAL)
        self.func = attributes.func
        self.captionParent.OnClick = self.Toggle
        self.captionParent.OnMouseEnter = self.OnCaptionEnter
        self.captionParent.OnMouseExit = self.OnCaptionExit
        self.menuType = attributes.menuType
        self.caption = CCLabel(parent=self.captionParent, align=uiconst.CENTERLEFT, left=10, letterspace=3, shadowOffset=(0, 0), text=attributes.caption, uppercase=1, color=ccConst.COLOR, fontsize=13)
        if self.menuType != 'tattooMenu':
            self.caption.SetAlpha(0.5)
        self.keepColor = 0
        self.AddRadioButton()
        Fill(parent=self.captionParent, color=(0.4, 0.4, 0.4, 0.5))
        self.bevel = bevel = Frame(parent=self.captionParent, color=(1.0, 1.0, 1.0, 0.2), frameConst=ccConst.FILL_BEVEL, state=uiconst.UI_HIDDEN)
        frame = Frame(parent=self.captionParent, frameConst=ccConst.FRAME_SOFTSHADE, color=(1.0, 1.0, 1.0, 0.5))
        frame.padding = (-12, -5, -12, -15)
        self.height = self.captionParent.height
        sm.RegisterNotify(self)

    def AddRadioButton(self, *args):
        self.shadowIcon = Sprite(parent=self.captionParent, name='shadowIcon', align=uiconst.CENTERRIGHT, state=uiconst.UI_DISABLED, pos=(0, 0, 32, 32), texturePath='res:/UI/Texture/CharacterCreation/radiobuttonShadow.dds', color=(0.4, 0.4, 0.4, 0.6))
        self.backIcon = Sprite(parent=self.captionParent, name='backIcon', align=uiconst.CENTERRIGHT, state=uiconst.UI_DISABLED, pos=(0, 0, 32, 32), texturePath='res:/UI/Texture/CharacterCreation/radiobuttonBack.dds')
        self.radioBtnFill = Container(parent=self.captionParent, state=uiconst.UI_HIDDEN, align=uiconst.CENTERRIGHT, pos=(0, 0, 32, 32), idx=0)
        self.radioBtnHilite = Sprite(parent=self.radioBtnFill, name='radioBtnHilite', align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, pos=(0, 0, 32, 32), texturePath='res:/UI/Texture/CharacterCreation/radiobuttonWhite.dds')
        self.radioBtnColor = Sprite(parent=self.radioBtnFill, name='radioBtnColor', align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, pos=(0, 0, 32, 32), texturePath='res:/UI/Texture/CharacterCreation/radiobuttonColor.dds')
        if self.menuType == 'tattooMenu':
            self.SetRadioBtnColor(color='green')

    def OnCaptionEnter(self, *args):
        uicore.layer.charactercreation.controller.SetHintText(None, localization.GetByLabel('UI/Login/CharacterCreation/AssetMenu/BodyModHelp'))
        sm.StartService('audio').SendUIEvent(unicode('ui_icc_menu_mouse_over_play'))
        if not self.keepColor:
            self.caption.SetAlpha(1.0)
            if self.menuType == 'tattooMenu':
                self.SetRadioBtnColor(color='red')
            elif self.menuType == 'assetMenu':
                self.SetRadioBtnColor(color='green')
        if self.bevel:
            self.bevel.state = uiconst.UI_DISABLED

    def OnCaptionExit(self, *args):
        uicore.layer.charactercreation.controller.SetHintText(None)
        if self.menuType != 'tattooMenu':
            self.caption.SetAlpha(0.5)
        if not self.keepColor:
            if self.menuType == 'tattooMenu':
                self.SetRadioBtnColor(color='green')
            else:
                self.radioBtnFill.state = uiconst.UI_HIDDEN
            if self.bevel:
                self.bevel.state = uiconst.UI_HIDDEN

    def Toggle(self, *args):
        sm.StartService('audio').SendUIEvent(unicode('ui_icc_button_mouse_down_play'))
        self.keepColor = 1
        if self.func:
            self.func()
            self.ResetRadioButton()

    def ResetRadioButton(self, *args):
        self.keepColor = 0
        if self.menuType != 'tattooMenu':
            self.caption.SetAlpha(0.5)
        if self.menuType == 'tattooMenu':
            self.SetRadioBtnColor(color='green')
        else:
            self.radioBtnFill.state = uiconst.UI_HIDDEN

    def OnColorPaletteChanged(self, width):
        self.colorPaletteParent.width = width

    def SetRadioBtnColor(self, color = 'green', *args):
        if color == 'green':
            self.radioBtnFill.state = uiconst.UI_DISABLED
            self.radioBtnColor.SetRGB(0, 1, 0)
            self.radioBtnHilite.SetAlpha(0.7)
        elif color == 'red':
            self.radioBtnFill.state = uiconst.UI_DISABLED
            self.radioBtnColor.SetRGB(1, 0, 0)
            self.radioBtnHilite.SetAlpha(0.3)
