#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation_new\colorPalette.py
import carbonui.const as uiconst
import uthread
import charactercreator.const as ccConst
import eve.client.script.ui.login.charcreation_new.ccUtil as ccUtil
import localization
from carbon.common.script.util import timerstuff
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.uicore import uicore
from carbonui.uianimations import animations
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.login.charcreation_new.charCreationUtils import CCLabel, GradientSlider, BitSlider
from eve.client.script.ui.login.charcreation_new.sceneManager import GetCharacterCreationSceneManager
from eve.client.script.ui.login.charcreation_new.dollManager import GetCharacterCreationDollManager
HAIRDARKNESS = 'hari_darkness'

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
        Container.ApplyAttributes(self, attributes)
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
        Container.Close(self)

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
            if not ccUtil.IsSlowMachine():
                sliders += [('lights', localization.GetByLabel('UI/Login/CharacterCreation/AssetMenu/Intensity'), GetCharacterCreationSceneManager().GetLightIntensity())]
        self.Flush()
        self.height = 0
        self.width = self.startingWidth
        self.currentColorSize = self.COLORSIZE
        self.PrepareTuckControls()
        for referenceName, label, currentValue in sliders:
            extraParameters = {}
            if referenceName == 'intensity':
                sliderClass = GradientSlider
                extraParameters = {'alphaValues': (0, 0)}
            elif referenceName == HAIRDARKNESS:
                sliderClass = GradientSlider
            else:
                sliderClass = BitSlider
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
        GetCharacterCreationDollManager().ValidateColors(self.modifier)
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
        GetCharacterCreationDollManager().SetColorValue(self.modifier, var1, var2)

    def SetSliderValue(self, slider):
        ccDollManager = GetCharacterCreationDollManager()
        value = slider.GetValue()
        if slider.sliderType == 'lights':
            intensity = slider.GetValue()
            GetCharacterCreationSceneManager().SetLightIntensity(intensity)
        elif slider.sliderType == 'intensity':
            info = uicore.layer.charactercreation.controller.GetInfo()
            value = sm.GetService('character').GetTrueWeight(info.charID, slider.modifier, value)
            ccDollManager.SetIntensity(slider.modifier, value)
        elif slider.sliderType == 'specularity':
            ccDollManager.SetColorSpecularity(slider.modifier, value)
        elif slider.sliderType == HAIRDARKNESS:
            uicore.layer.charactercreation.controller.SetHairDarkness(value)

    def OnMouseWheel(self, *args):
        pass

    def OnMouseEnterColor(self, colorPar, *args):
        colorPar.hiliteFrame.state = uiconst.UI_DISABLED

    def OnMouseExitColor(self, colorPar, *args):
        colorPar.hiliteFrame.state = uiconst.UI_HIDDEN
