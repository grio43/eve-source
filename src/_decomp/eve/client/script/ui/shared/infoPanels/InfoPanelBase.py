#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\infoPanels\InfoPanelBase.py
import math
import localization
import signals
import uthread2
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.control import utilMenu
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.shared.infoPanels import infoPanelSettingsController
from eve.client.script.ui.shared.infoPanels.const import infoPanelConst
from eve.client.script.ui.shared.infoPanels.const import infoPanelUIConst

class InfoPanelBase(ContainerAutoSize):
    default_iconTexturePath = 'res:/UI/texture/icons/77_32_30.png'
    default_align = uiconst.TOTOP
    default_isModeFixed = False
    default_mode = infoPanelConst.MODE_NORMAL
    label = ''
    panelTypeID = None
    hasSettings = True
    isCollapsable = True
    headerCls = eveLabel.EveCaptionSmall
    MAINPADBOTTOM = 10
    MAINPADTOP = 0
    HEADER_FADE_WIDTH = 20
    __notifyevents__ = ['ProcessUpdateInfoPanel']

    def __init__(self, **kwargs):
        super(InfoPanelBase, self).__init__(**kwargs)
        sm.RegisterNotify(self)
        self.Update(None)

    def ApplyAttributes(self, attributes):
        super(InfoPanelBase, self).ApplyAttributes(attributes)
        self.onModeTransitionToNormalSignal = signals.Signal(signalName='onModeTransitionToNormalSignal')
        self.isInModeTransition = False
        self.expandButton = None
        self._mode = attributes.get('mode', self.default_mode)
        self.isModeFixed = attributes.get('isModeFixed', self.default_isModeFixed)
        self.__settingsID = attributes.get('settingsID', None)
        self.ConstructLayout()

    def ConstructLayout(self):
        self.topCont = Container(name='topCont', parent=self, align=uiconst.TOTOP, height=28)
        self.headerBtnCont = Container(name='headerBtnCont', parent=self.topCont, align=uiconst.TOLEFT, width=infoPanelUIConst.LEFTPAD)
        self.headerCont = Container(name='headerCont', parent=self.topCont)
        self.headerCompactCont = Container(name='headerCompactCont', parent=self.topCont, opacity=0.0)
        self.headerButton = self.ConstructHeaderButton()
        if not self.isModeFixed:
            self.expandButton = ExpandButton(parent=self.headerBtnCont, align=uiconst.TOLEFT, width=self.topCont.height, expanded=self.mode == infoPanelConst.MODE_NORMAL, on_click=self.ToggleMode)
        self.mainCont = ContainerAutoSize(name='mainCont', parent=self, align=uiconst.TOTOP, padLeft=infoPanelUIConst.LEFTPAD, padTop=self.MAINPADTOP, padBottom=self.MAINPADBOTTOM if self.mode == infoPanelConst.MODE_NORMAL else 0)

    @property
    def settingsID(self):
        if not self.__settingsID:
            self.__settingsID = sm.GetService('viewState').GetCurrentView().name
        return self.__settingsID

    @classmethod
    def GetTexturePath(cls):
        return cls.default_iconTexturePath

    def ConstructHeaderButton(self):
        return utilMenu.UtilMenu(name='headerButton', parent=self.headerBtnCont, align=uiconst.CENTERRIGHT, state=uiconst.UI_NORMAL if self.hasSettings else uiconst.UI_DISABLED, menuAlign=uiconst.TOPLEFT, pos=(0,
         0,
         self.topCont.height,
         self.topCont.height), iconSize=18, texturePath=self.GetTexturePath(), GetUtilMenu=self.GetSettingsMenu)

    def ConstructSimpleHeaderButton(self):
        return ButtonIcon(name='headerButton', parent=self.headerBtnCont, align=uiconst.CENTERRIGHT, pos=(0,
         0,
         self.topCont.height,
         self.topCont.height), iconSize=18, texturePath=self.GetTexturePath())

    @staticmethod
    def IsAvailable():
        return True

    @property
    def mode(self):
        if not self._mode:
            self._mode = self.default_mode
        return self._mode

    @mode.setter
    def mode(self, mode):
        if mode == infoPanelConst.MODE_HIDDEN and not self.isCollapsable:
            return
        if self.mode is not None and mode == self.mode:
            return
        infoPanelSettingsController.save_mode_for_panel_in_setting(self.settingsID, self.panelTypeID, mode)
        oldMode = self._mode
        self._mode = mode
        self.Update(oldMode)

    def ProcessUpdateInfoPanel(self, panelTypeID):
        if panelTypeID is None or panelTypeID == self.panelTypeID:
            self.Update()

    def Update(self, oldMode = None):
        if not self.IsAvailable():
            self.Hide()
            return
        self.Show()
        self.isInModeTransition = True
        self.OnBeforeModeChanged(oldMode)
        try:
            if self.expandButton:
                self.expandButton.expanded = self.mode == infoPanelConst.MODE_NORMAL
            if self.mode == infoPanelConst.MODE_NORMAL:
                if oldMode == infoPanelConst.MODE_COMPACT:
                    self.mainCont.opacity = 0.0
                    self.mainCont.height = 0
                    self.mainCont.padBottom = 0
                    self.EnableAutoSize()
                    self.mainCont.DisableAutoSize()
                    self.mainCont.Show()
                self.ConstructNormal()
            elif self.mode == infoPanelConst.MODE_COMPACT:
                self.ConstructCompact()
            elif self.mode == infoPanelConst.MODE_HIDDEN:
                self.ConstructCollapsed()
            else:
                raise RuntimeError('Invalid infoPanel mode: %s' % self.mode)
            self.ModeTransition(oldMode)
        finally:
            self.isInModeTransition = False

    def ModeTransition(self, oldMode = None):
        self.OnStartModeChanged(oldMode)
        if self.mode == infoPanelConst.MODE_HIDDEN:
            if oldMode:
                self.AnimFadeOut()
            self._SetCollapsedState()
        elif self.mode == infoPanelConst.MODE_NORMAL:
            self.Show()
            if oldMode == infoPanelConst.MODE_HIDDEN:
                self.AnimFadeIn()
            elif oldMode == infoPanelConst.MODE_COMPACT:
                self.AnimFadeInMainCont()
            self._SetNormalState()
            self.onModeTransitionToNormalSignal(self.panelTypeID)
        elif self.mode == infoPanelConst.MODE_COMPACT:
            self.Show()
            if oldMode == infoPanelConst.MODE_HIDDEN:
                self.AnimFadeIn()
            elif oldMode == infoPanelConst.MODE_NORMAL:
                self.AnimFadeOutMainCont()
            self._SetCompactState()
        self.OnEndModeChanged(oldMode)

    def OnBeforeModeChanged(self, oldMode):
        pass

    def OnStartModeChanged(self, oldMode):
        pass

    def OnEndModeChanged(self, oldMode):
        pass

    def _SetNormalState(self):
        self.mainCont.opacity = 1.0
        self.mainCont.EnableAutoSize()
        self.mainCont.Show()

    def _SetCollapsedState(self):
        self.Hide()
        self.mainCont.Show()
        self.mainCont.EnableAutoSize()
        self.mainCont.opacity = 1.0
        self.mainCont.padBottom = self.MAINPADBOTTOM
        self.mainCont.left = 0

    def _SetCompactState(self):
        self.mainCont.Hide()
        self.mainCont.DisableAutoSize()

    def AnimFadeIn(self):
        duration = 0.3
        self.mainCont.Show()
        _, height = self.mainCont.GetAutoSize()
        height += self.MAINPADBOTTOM
        height += self.topCont.height
        self.left = 5
        self.opacity = 0.0
        animations.MorphScalar(self, 'height', 0, height, duration=duration)
        uthread2.sleep(0.1)
        animations.MorphScalar(self, 'left', 5, 0, duration=duration)
        animations.MorphScalar(self, 'padBottom', 0, self.default_padBottom, duration=duration)
        self._AnimFadeInSelf(duration)

    def _AnimFadeInSelf(self, duration):
        animations.FadeIn(self, duration=duration, sleep=True)

    def AnimFadeOut(self):
        duration = 0.3
        animations.FadeOut(self, duration=duration)
        uthread2.sleep(0.1)
        animations.MorphScalar(self, 'left', 0, 5, duration=duration)
        animations.MorphScalar(self, 'height', self.height, 0, duration=duration)
        animations.MorphScalar(self, 'padBottom', self.padBottom, 0, duration=duration, sleep=True)

    def AnimFadeInMainCont(self):
        duration = 0.3
        _, height = self.mainCont.GetAutoSize()
        animations.MorphScalar(self.mainCont, 'height', 0, height, duration=duration)
        animations.MorphScalar(self.mainCont, 'padBottom', 0, self.MAINPADBOTTOM, duration=duration)
        uthread2.sleep(0.1)
        animations.MorphScalar(self.mainCont, 'left', 5, 0, duration=duration)
        animations.FadeTo(self.mainCont, 0.0, 1.0, duration=duration, sleep=True)

    def AnimFadeOutMainCont(self):
        duration = 0.3
        self.mainCont.DisableAutoSize()
        animations.MorphScalar(self.mainCont, 'left', 0, 5, duration=duration)
        animations.FadeOut(self.mainCont, duration=duration)
        uthread2.sleep(0.1)
        animations.MorphScalar(self.mainCont, 'height', self.mainCont.height, 0, duration=duration)
        animations.MorphScalar(self.mainCont, 'padBottom', self.mainCont.padBottom, 0, duration=duration, sleep=True)

    def GetSettingsMenu(self, menuParent):
        pass

    def ToggleMode(self, *args):
        if self.isInModeTransition:
            return
        if self.mode == infoPanelConst.MODE_NORMAL:
            PlaySound(uiconst.SOUND_COLLAPSE)
            self.mode = infoPanelConst.MODE_COMPACT
        else:
            PlaySound(uiconst.SOUND_EXPAND)
            self.mode = infoPanelConst.MODE_NORMAL

    @classmethod
    def GetClassHint(cls):
        if cls.mode != infoPanelConst.MODE_HIDDEN:
            return localization.GetByLabel(cls.label)

    def ConstructNormal(self):
        pass

    def ConstructCompact(self):
        pass

    def ConstructCollapsed(self):
        pass


class ExpandButton(Container):
    default_state = uiconst.UI_NORMAL

    def __init__(self, expanded, on_click = None, **kwargs):
        super(ExpandButton, self).__init__(**kwargs)
        self._expanded = expanded
        self._icon = None
        self._fill = None
        self.on_click = signals.Signal(signalName='on_click')
        self.layout()
        if on_click:
            self.on_click.connect(on_click)

    @property
    def expanded(self):
        return self._expanded

    @expanded.setter
    def expanded(self, expanded):
        if expanded != self._expanded:
            self._expanded = expanded
            self.anim_update()

    @property
    def _icon_rotation(self):
        if self._expanded:
            return 0.0
        return math.pi / 2.0

    def layout(self):
        self._fill = Fill(bgParent=self, color=(1.0, 1.0, 1.0), opacity=0.0)
        self._icon = Sprite(parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Neocom/arrowDown.png', width=7, height=7, rotation=self._icon_rotation)

    def anim_update(self):
        animations.MorphScalar(self._icon, 'rotation', startVal=self._icon.rotation, endVal=self._icon_rotation, duration=0.3)

    def OnClick(self, *args):
        self.on_click()

    def OnMouseEnter(self):
        PlaySound(uiconst.SOUND_ENTRY_HOVER)
        animations.FadeIn(self._fill, endVal=0.1, duration=0.1)

    def OnMouseExit(self):
        animations.FadeOut(self._fill, duration=0.3)
