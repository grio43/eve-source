#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\sidePanelButtons.py
import math
import signals
import trinity
from carbonui.primitives.container import Container
from carbonui.primitives.gridcontainer import GridContainer
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from eve.client.script.ui.control.glowSprite import GlowSprite
from eve.client.script.ui.control.themeColored import FrameThemeColored
from eve.client.script.ui.util.uiComponents import Component, ButtonEffect
import carbonui.const as uiconst
from signals.signalUtil import ChangeSignalConnect
from carbonui.uicore import uicore
OPACITY_MOUSE_DOWN = 3.0
OPACITY_IDLE = 0.5

@Component(ButtonEffect(opacityIdle=OPACITY_IDLE, opacityHover=2.0, opacityMouseDown=OPACITY_IDLE, bgElementFunc=lambda parent, _: parent.hilite, audioOnEntry=uiconst.SOUND_BUTTON_HOVER, audioOnClick=uiconst.SOUND_BUTTON_CLICK))

class SidePanelButton(Container):
    default_state = uiconst.UI_NORMAL
    normalOpacity = 1.0
    disabledOpacity = 0.2
    hiliteTexture = 'res:/UI/Texture/Shared/sideButton_Over.png'
    selectedTexture = 'res:/UI/Texture/Shared/sideButton_Down.png'
    normalFrameTexture = 'res:/UI/Texture/Shared/sideButton_Up.png'

    def ApplyAttributes(self, attributes):
        super(SidePanelButton, self).ApplyAttributes(attributes)
        self.controller = attributes.controller
        self._isEnabled = True
        self.isOnRightOfContent = attributes.isOnRightOfContent
        self.onClick = attributes.onClick
        self.isSelected = False
        self.configName = attributes.configName
        self.iconSize = attributes.iconSize or 40
        self.tabText = attributes.tabText
        texturePath = attributes.texturePath
        frameRotation = self.GetRotations()
        self.icon = Sprite(parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=self.iconSize, height=self.iconSize, texturePath=texturePath, spriteEffect=trinity.TR2_SFX_COLOROVERLAY)
        frameCont = Transform(name='frameCont', parent=self, align=uiconst.TOALL, rotation=frameRotation)
        self.selectedFrame = FrameThemeColored(name='selectedFrame', parent=frameCont, state=uiconst.UI_DISABLED, texturePath=self.selectedTexture, colorType=uiconst.COLORTYPE_UIHILIGHT, opacity=1.0)
        self.selectedFrame.display = False
        self.hilite = FrameThemeColored(name='hilite', parent=frameCont, state=uiconst.UI_DISABLED, texturePath=self.hiliteTexture, colorType=uiconst.COLORTYPE_UIHILIGHT)
        frame = FrameThemeColored(parent=frameCont, state=uiconst.UI_DISABLED, texturePath=self.normalFrameTexture, colorType=uiconst.COLORTYPE_UIBASECONTRAST)
        self.SetSelectedBtnState(self.isSelected, animate=False)
        self.ChangeSignalConnection()

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.controller.on_selected_changed, self.OnSelectedChanged), (self.controller.on_btn_enabled, self.OnEnableBtn), (self.controller.on_btn_disabled, self.OnDisableBtn)]
        ChangeSignalConnect(signalAndCallback, connect)

    def GetRotations(self):
        if self.isOnRightOfContent:
            frameRotation = 0
        else:
            frameRotation = math.pi
        return frameRotation

    def OnClick(self, *args):
        if self._isEnabled:
            self.controller.OnBtnClicked(self.configName)

    def OnMouseDown(self, *args):
        if self._isEnabled:
            uicore.animations.FadeTo(self.hilite, self.hilite.opacity, OPACITY_MOUSE_DOWN, duration=0.1)

    def OnSelectedChanged(self, selectedBtnConfig):
        isSelected = selectedBtnConfig == self.configName
        self.SetSelectedBtnState(isSelected)

    def SetSelectedBtnState(self, isSelected, animate = True):
        self.isSelected = isSelected
        if self.isSelected:
            self.selectedFrame.display = True
        else:
            self.selectedFrame.display = False
            self.hilite.StopAnimations()
            self.hilite.opacity = OPACITY_IDLE
        if isSelected and animate:
            uicore.animations.MorphScalar(self.selectedFrame, 'opacity', 0, 1, duration=0.7, curveType=uiconst.ANIM_OVERSHOT)

    def OnEnableBtn(self, btnConfigName):
        if btnConfigName == self.configName:
            self.Enable()

    def Enable(self, *args):
        self.SetEnabled()
        self.SetOpacity(self.normalOpacity)

    def OnDisableBtn(self, btnConfigName):
        if btnConfigName == self.configName:
            self.Disable()

    def Disable(self, *args):
        self.SetDisabled()
        self.SetOpacity(self.disabledOpacity)

    def SetEnabled(self):
        self._isEnabled = True

    def SetDisabled(self):
        self._isEnabled = False

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric1ColumnTemplate()
        tooltipPanel.AddLabelLarge(text=self.tabText)


class SidePanelTabGroup(GridContainer):
    default_btnWidth = 45
    default_btnHeight = 40
    default_iconSize = 40
    default_height = 100
    default_width = default_btnWidth
    default_lines = 2
    default_columns = 1
    default_isOnRightOfContent = True
    default_isToggleBtn = True

    def ApplyAttributes(self, attributes):
        GridContainer.ApplyAttributes(self, attributes)
        self.isOnRightOfContent = attributes.get('isOnRightOfContent', self.default_isOnRightOfContent)
        isToggleBtn = attributes.get('isToggleBtn', self.default_isToggleBtn)
        selectedTab = attributes.selectedTab
        self.btnsDict = {}
        self.func = attributes.func
        settingName = attributes.settingName
        tabBtnData = attributes.tabBtnData
        self.btnWidth = attributes.get('btnWidth', self.default_btnWidth)
        self.btnHeight = attributes.get('btnHeight', self.default_btnHeight)
        self.iconSize = attributes.get('iconSize', self.default_iconSize)
        if isToggleBtn:
            self.controller = ToggleTabBtnController(onClickFunc=self.func, settingName=settingName)
        else:
            self.controller = TabBtnController(onClickFunc=self.func, settingName=settingName)
        self.AddBtns(tabBtnData, selectedTab)

    def AddBtns(self, btnData, selectedTab):
        self.Flush()
        self.btnsDict.clear()
        padTopBottom = 2
        for eachData in btnData:
            tabText, configName, texturePath, uniqueUiName = eachData
            btn = SidePanelButton(parent=self, name=configName, configName=configName, tabText=tabText, align=uiconst.TOALL, opacity=1.0, isOnRightOfContent=self.isOnRightOfContent, padTop=padTopBottom, padBottom=padTopBottom, controller=self.controller, iconSize=self.iconSize, texturePath=texturePath, uniqueUiName=uniqueUiName)
            self.btnsDict[configName] = btn

        self.controller.SetAsSelected(selectedTab)
        numBtns = len(self.btnsDict)
        self.height = numBtns * (self.btnHeight + 2 * padTopBottom)
        self.lines = numBtns

    def SetSelectedBtn(self, configName):
        self.controller.SetAsSelected(configName)

    def GetButton(self, configName):
        return self.btnsDict.get(configName, None)

    def GetButtons(self):
        return self.btnsDict

    def Enable(self):
        if self.controller:
            self.controller.Enable()

    def Disable(self):
        if self.controller:
            self.controller.Disable()

    def EnableBtns(self, btnNames):
        for eachBtnName in btnNames:
            self.controller.EnableBtn(eachBtnName)

    def DisableBtns(self, btnNames):
        selectedBtn = self.controller.GetSelectedBtn()
        disablingSelected = selectedBtn in btnNames
        for eachBtnName in btnNames:
            self.controller.DisableBtn(eachBtnName)

        if disablingSelected:
            for eachBtnName in self.btnsDict.iterkeys():
                if eachBtnName not in btnNames:
                    self.controller.OnBtnClicked(eachBtnName)
                    return

    def Close(self):
        self.controller = None
        Container.Close(self)


class SidePanelTabGroupSmall(SidePanelTabGroup):
    default_btnWidth = 36
    default_btnHeight = 32
    default_iconSize = 32


class TabBtnController(object):

    def __init__(self, onClickFunc, settingName):
        self.settingName = settingName
        self.btnSelected = self.GetSettingValue()
        self.onClickFunc = onClickFunc
        self.on_selected_changed = signals.Signal(signalName='on_selected_changed')
        self.on_btn_disabled = signals.Signal(signalName='on_btn_disabled')
        self.on_btn_enabled = signals.Signal(signalName='on_btn_enabled')
        self._isEnabled = True

    def OnBtnClicked(self, btnConfigName):
        if not self._isEnabled:
            return
        newSelected = btnConfigName
        self.ChangeSettingValue(newSelected)
        self.onClickFunc(newSelected)
        self.SetAsSelected(newSelected)

    def SetAsSelected(self, btnConfigName):
        self.btnSelected = btnConfigName
        self.on_selected_changed(btnConfigName)

    def EnableBtn(self, btnConfigName):
        self.on_btn_enabled(btnConfigName)

    def DisableBtn(self, btnConfigName):
        self.on_btn_disabled(btnConfigName)

    def GetSelectedBtn(self):
        return self.btnSelected

    def ResetSelected(self):
        self.btnSelected = ''

    def GetSettingValue(self):
        return settings.user.ui.Get(self.settingName, '')

    def ChangeSettingValue(self, newValue):
        settings.user.ui.Set(self.settingName, newValue)

    def Enable(self):
        self._isEnabled = True

    def Disable(self):
        self._isEnabled = False


class ToggleTabBtnController(TabBtnController):

    def OnBtnClicked(self, btnConfigName):
        if not self._isEnabled:
            return
        if self.btnSelected == btnConfigName:
            newSelected = ''
        else:
            newSelected = btnConfigName
        self.ChangeSettingValue(newSelected)
        self.onClickFunc(newSelected)
        self.SetAsSelected(newSelected)
