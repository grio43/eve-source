#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiSpriteTest.py
import blue
import trinity
from carbonui import uiconst
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.control.slider import Slider
from carbonui.primitives.container import Container
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control import eveLabel
from carbonui.control.button import Button
from carbonui.control.radioButton import RadioButton
from carbonui.control.window import Window
from eve.devtools.script.uiAnimationTest import TestAnimationsWnd
from eve.client.script.ui.control.fileDialog import FileDialog

class UISpriteTest(Window):
    __guid__ = 'form.UISpriteTest'
    __notifyevents__ = ['OnFileDialogSelection']
    default_width = 1000
    default_height = 800
    default_minSize = (default_width, default_height)
    default_windowID = 'UISpriteTest'
    COLUMN_WIDTH = 160

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.SetCaption('UI Sprite Test')
        self.textureSetFunc = None
        self.bottomCont = Container(name='bottomCont', parent=self.sr.main, align=uiconst.TOBOTTOM_PROP, padding=(5, 0, 5, 0), height=0.6)
        self.topCont = Container(name='topCont', parent=self.sr.main, align=uiconst.TOALL, padding=(3, 3, 3, 3))
        self.topLeftCont = Container(name='topLeftCont', parent=self.topCont, align=uiconst.TOLEFT, width=90)
        self.topRightCont = Container(name='topRightCont', parent=self.topCont, align=uiconst.TOALL)
        primaryCont = Container(parent=self.topLeftCont, align=uiconst.TOTOP, height=self.topLeftCont.width)
        Button(name='closePrimaryBtn', parent=primaryCont, label='<color=red>X', align=uiconst.TOPRIGHT, func=self.OnClosePrimaryBtnClick, fixedwidth=20, top=-3, left=-3)
        self.primaryTextureSprite = Sprite(name='primaryTextureSprite', parent=primaryCont, align=uiconst.TOALL)
        Button(name='loadPrimaryTextureBtn', parent=self.topLeftCont, label='Load primary', align=uiconst.TOTOP, func=self.OnLoadPrimaryTextureBtnClicked)
        Button(name='switchBtn', parent=self.topLeftCont, label='Switch', align=uiconst.TOTOP, func=self.OnSwitchBtnClick, padding=(0, 8, 0, 5))
        secondaryCont = Container(parent=self.topLeftCont, align=uiconst.TOTOP, height=self.topLeftCont.width, padTop=10)
        Button(name='closeSecondaryBtn', parent=secondaryCont, label='<color=red>X', align=uiconst.TOPRIGHT, func=self.OnCloseSecondaryBtnClick, fixedwidth=20, top=-3, left=-3)
        self.secondaryTextureSprite = Sprite(name='secondaryTextureSprite', parent=secondaryCont, align=uiconst.TOALL)
        Button(name='loadSecondaryTextureBtn', parent=self.topLeftCont, label='Load secondary', align=uiconst.TOTOP, func=self.OnLoadSecondaryTextureBtnClicked)
        self.mainSprite = Sprite(name='mainSprite', parent=self.topRightCont, align=uiconst.CENTER, width=128, height=128)
        sizeCont = Container(parent=self.topRightCont, align=uiconst.TOPRIGHT, pos=(5, 5, 60, 50))
        self.mainSpriteWidthEdit = SingleLineEditText(parent=sizeCont, name='mainSpriteWidthEdit', align=uiconst.TOTOP, label='width', ints=(1, 1024), setvalue=self.mainSprite.width, padTop=10, OnChange=self.OnMainSpriteWidthHeightChange)
        self.mainSpriteHeightEdit = SingleLineEditText(parent=sizeCont, name='mainSpriteHeightEdit', align=uiconst.TOTOP, label='height', ints=(1, 1024), setvalue=self.mainSprite.height, padTop=15, OnChange=self.OnMainSpriteWidthHeightChange)
        Button(parent=self.topRightCont, align=uiconst.BOTTOMRIGHT, label='Animate', func=self.OpenAnimationWindow, top=20)
        Button(parent=self.topRightCont, align=uiconst.BOTTOMRIGHT, label='Copy to clipboard', func=self.CopyCodeToClipboard, top=0)
        Line(parent=self.bottomCont, align=uiconst.TOTOP, padBottom=16)
        self.ConstructColorColumn()
        self.ConstructBlendModeColumn()
        self.ConstructSpriteEffectColumn()
        self.ConstructOutputModeColumn()
        self.ConstructShadowColumn()
        self.SetPrimaryPath(settings.user.ui.Get('UISpriteTestPrimaryTexturePath', None))
        self.SetSecondaryPath(settings.user.ui.Get('UISpriteTestSecondaryTexturePath', None))

    def ConstructOutputModeColumn(self):
        outputModeColumn = Container(name='outputModeColumn', parent=self.bottomCont, align=uiconst.TOLEFT, width=self.COLUMN_WIDTH, padLeft=32)
        eveLabel.Label(parent=outputModeColumn, text='outputMode', align=uiconst.TOTOP)
        options = (('OUTPUT_COLOR', uiconst.OUTPUT_COLOR), ('OUTPUT_GLOW', uiconst.OUTPUT_GLOW), ('OUTPUT_COLOR_AND_GLOW', uiconst.OUTPUT_COLOR_AND_GLOW))
        for modeName, value in options:
            RadioButton(parent=outputModeColumn, text=modeName, align=uiconst.TOTOP, groupname='outputModeRadioGroup', checked=value == Sprite.default_outputMode, callback=self.OnOutputModeRadioButton, retval=value)

        eveLabel.Label(parent=outputModeColumn, text='glowBrightness', align=uiconst.TOTOP, padTop=16)
        Slider(parent=outputModeColumn, align=uiconst.TOTOP, minValue=0, maxValue=10.0, value=Sprite.default_glowBrightness, on_dragging=self.OnGlowBrightnessSlider, increments=[1.0], snapToIncrements=False)
        eveLabel.Label(parent=outputModeColumn, text='effectOpacity', align=uiconst.TOTOP, padTop=16)
        Slider(parent=outputModeColumn, align=uiconst.TOTOP, minValue=0, maxValue=10.0, value=Sprite.default_effectOpacity, on_dragging=self.OnEffectOpacitySlider, increments=[1.0], snapToIncrements=False)
        eveLabel.Label(parent=outputModeColumn, text='saturation', align=uiconst.TOTOP, padTop=16)
        Slider(parent=outputModeColumn, align=uiconst.TOTOP, minValue=0, maxValue=10.0, value=Sprite.default_saturation, on_dragging=self.OnSaturationSlider, increments=[1.0], snapToIncrements=False)

    def OnSaturationSlider(self, slider):
        self.mainSprite.saturation = slider.GetValue()

    def OnEffectOpacitySlider(self, slider):
        self.mainSprite.effectOpacity = slider.GetValue()

    def OnGlowBrightnessSlider(self, slider):
        self.mainSprite.glowBrightness = slider.GetValue()

    def OnOutputModeRadioButton(self, radioButton):
        self.mainSprite.outputMode = radioButton.GetGroupValue()

    def ConstructColorColumn(self):
        colorCont = Container(parent=self.bottomCont, align=uiconst.TOLEFT, width=self.COLUMN_WIDTH)
        eveLabel.Label(parent=colorCont, text='color', align=uiconst.TOTOP)
        self.colorSliders = self.GetColorSliders(colorCont, self.OnColorValueChanged)

    def ConstructBlendModeColumn(self):
        blendModeCont = Container(parent=self.bottomCont, align=uiconst.TOLEFT, width=self.COLUMN_WIDTH, padLeft=32)
        eveLabel.Label(parent=blendModeCont, align=uiconst.TOTOP, text='blendMode')
        for constName in dir(trinity):
            if not constName.startswith('TR2_SBM_'):
                continue
            constVal = getattr(trinity, constName)
            RadioButton(parent=blendModeCont, text=constName, align=uiconst.TOTOP, settingsKey='blendModeGroup', groupname='blendModeGroup', checked=constVal == Sprite.default_blendMode, callback=self.OnBlendModeRadioChanged, retval=constVal)

    def ConstructSpriteEffectColumn(self):
        spriteEffectCont = Container(parent=self.bottomCont, align=uiconst.TOLEFT, width=self.COLUMN_WIDTH, padLeft=32)
        eveLabel.Label(parent=spriteEffectCont, text='spriteEffect', align=uiconst.TOTOP)
        for constName in dir(trinity):
            if not constName.startswith('TR2_SFX_'):
                continue
            constVal = getattr(trinity, constName)
            RadioButton(parent=spriteEffectCont, text=constName, align=uiconst.TOTOP, settingsKey='spriteEffectGroup', groupname='spriteEffectGroup', checked=constVal == Sprite.default_spriteEffect, callback=self.OnSpriteEffectRadioChanged, retval=constVal)

    def ConstructShadowColumn(self):
        shadowCont = Container(parent=self.bottomCont, align=uiconst.TOLEFT, width=self.COLUMN_WIDTH, padLeft=32)
        eveLabel.Label(parent=shadowCont, text='shadowOffset:', align=uiconst.TOTOP, padBottom=-5)
        defaultX, defaultY = Sprite.default_shadowOffset
        self.shadowOffsetXSlider = Slider(parent=shadowCont, label='x', align=uiconst.TOTOP, minValue=0, maxValue=50.0, value=defaultX, height=20, on_dragging=self.OnShadowOffsetSlider)
        self.shadowOffsetYSlider = Slider(parent=shadowCont, label='y', align=uiconst.TOTOP, minValue=0, maxValue=50.0, value=defaultY, height=20, on_dragging=self.OnShadowOffsetSlider)
        eveLabel.Label(parent=shadowCont, text='shadowColor:', align=uiconst.TOTOP, padTop=15, padBottom=-5)
        self.shadowColorSliders = self.GetColorSliders(shadowCont, self.OnShadowColorValueChanged)

    def OnSwitchBtnClick(self, *args):
        primary = self.mainSprite.GetTexturePath()
        secondary = self.mainSprite.GetSecondaryTexturePath()
        self.SetPrimaryPath(secondary)
        self.SetSecondaryPath(primary)

    def OnClosePrimaryBtnClick(self, *args):
        self.SetPrimaryPath(None)

    def OnCloseSecondaryBtnClick(self, *args):
        self.SetSecondaryPath(None)

    def OnMainSpriteWidthHeightChange(self, *args):
        self.mainSprite.width = self.mainSpriteWidthEdit.GetValue()
        self.mainSprite.height = self.mainSpriteHeightEdit.GetValue()

    def GetColorSliders(self, parent, callback):
        sliders = []
        for colName in ('R', 'G', 'B', 'A'):
            slider = Slider(parent=parent, label=colName, align=uiconst.TOTOP, minValue=0, maxValue=1.0, value=1.0, height=20, on_dragging=callback)
            sliders.append(slider)

        return sliders

    def OnColorValueChanged(self, *args):
        if not hasattr(self, 'colorSliders'):
            return
        self.mainSprite.SetRGBA(*[ slider.value for slider in self.colorSliders ])

    def OnBlurFactorSlider(self, slider):
        self.mainSprite.blurFactor = slider.value

    def OnShadowOffsetSlider(self, slider):
        try:
            self.mainSprite.shadowOffset = (self.shadowOffsetXSlider.value, self.shadowOffsetYSlider.value)
        except:
            pass

    def OnShadowColorValueChanged(self, *args):
        if not hasattr(self, 'shadowColorSliders'):
            return
        self.mainSprite.shadowColor = tuple([ slider.value for slider in self.shadowColorSliders ])

    def OnBlendModeRadioChanged(self, button):
        self.mainSprite.blendMode = button.GetGroupValue()

    def OnSpriteEffectRadioChanged(self, button):
        self.mainSprite.spriteEffect = button.GetGroupValue()

    def OnSpriteEffectCombo(self, combo, label, value):
        self.mainSprite.spriteEffect = value

    def OnLoadPrimaryTextureBtnClicked(self, *args):
        self.textureSetFunc = self.SetPrimaryPath
        resPath = self.GetFilePathThroughFileDialog()
        if resPath:
            self.SetPrimaryPath(resPath)

    def OnLoadSecondaryTextureBtnClicked(self, *args):
        self.textureSetFunc = self.SetSecondaryPath
        resPath = self.GetFilePathThroughFileDialog()
        if resPath:
            self.SetSecondaryPath(resPath)

    def SetPrimaryPath(self, resPath):
        self.primaryTextureSprite.SetTexturePath(resPath)
        self.mainSprite.SetTexturePath(resPath)
        settings.user.ui.Set('UISpriteTestPrimaryTexturePath', resPath)

    def SetSecondaryPath(self, resPath):
        self.secondaryTextureSprite.SetTexturePath(resPath)
        self.mainSprite.SetSecondaryTexturePath(resPath)
        settings.user.ui.Set('UISpriteTestSecondaryTexturePath', resPath)

    def GetFilePathThroughFileDialog(self):
        return FileDialog.SelectFiles(path=blue.paths.ResolvePath('res:/UI/Texture'), multiSelect=False)

    def OnFileDialogSelection(self, selected):
        if not selected:
            return
        entry = selected[0]
        if entry.isDir:
            return
        self.textureSetFunc(str(entry.filePath))

    def OpenAnimationWindow(self, *args):
        TestAnimationsWnd.Open(animObj=self.mainSprite)

    def CopyCodeToClipboard(self, *args):

        def AddArg(argName, value = None):
            value = value or repr(getattr(self.mainSprite, argName))
            return '%s=%s,\n\t' % (argName, value.replace("'", '"').replace('\\\\', '\\'))

        ret = 'Sprite(\n\t'
        ret += AddArg('parent', 'uicore.desktop')
        ret += AddArg('width')
        ret += AddArg('height')
        if self.mainSprite.GetTexturePath():
            _, path = self.mainSprite.GetTexturePath().split('res')
            ret += AddArg('texturePath', repr('res:%s' % path))
        if self.mainSprite.GetSecondaryTexturePath():
            _, path = self.mainSprite.GetSecondaryTexturePath().split('res')
            ret += AddArg('textureSecondaryPath', repr('res:%s' % path))
        ret += AddArg('color', repr(self.mainSprite.GetRGBA()))
        ret += AddArg('blendMode')
        ret += AddArg('glowBrigtness')
        ret += AddArg('shadowOffset')
        ret += AddArg('shadowColor')
        ret += AddArg('spriteEffect')
        ret += ')'
        blue.pyos.SetClipboardData(ret)
