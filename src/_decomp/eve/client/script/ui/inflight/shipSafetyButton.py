#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\shipSafetyButton.py
from math import pi, sqrt
import blue
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import fontconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.primitives.vectorlinetrace import VectorLineTrace
from carbonui.util.color import Color
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.control.themeColored import FillThemeColored
from eve.client.script.ui.crimewatch import crimewatchConst
from eve.client.script.ui.inflight.shipSafetyConst import OPACITY_BG, TEXT_PADDING, DOCK_POINTER_LENGTH, DOCK_MARGIN, DESELECTED_BUTTON_OPACITY, HINT_DELAY, SAFETY_LEVEL_DATA_MAP
import carbonui.const as uiconst
from eve.client.script.util.settings import IsShipHudTopAligned
import trinity
import uthread
import localization
from carbonui.uicore import uicore
from eve.common.lib import appConst as const

class LightEmittingDiode(Container):
    __guid__ = 'shipSafetyButton.LightEmittingDiode'
    default_color = (1, 0, 0, 1)
    default_align = uiconst.TOPLEFT
    default_width = 32
    default_height = 32

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.isAnimating = False
        self.colorSprite = Sprite(bgParent=self, texturePath='res:/UI/Texture/CharacterCreation/radiobuttonColor.dds')
        Sprite(bgParent=self, texturePath='res:/UI/Texture/CharacterCreation/radiobuttonBack.dds', opacity=0.4)
        Sprite(bgParent=self, texturePath='res:/UI/Texture/CharacterCreation/radiobuttonShadow.dds', color=(0.4, 0.4, 0.4, 0.4))
        self.SetColor(attributes.get('color', self.default_color))

    def SetColor(self, color):
        self._color = color
        self.colorSprite.SetRGBA(*color)

    def Blink(self, cycles = 2, audioAlert = True):
        if not self.isAnimating:
            self.isAnimating = True
            self.blinkCurve = uicore.animations.SpColorMorphTo(self.colorSprite, Color.BLACK, self._color, duration=0.5, loops=cycles, curveType=uiconst.ANIM_BOUNCE, callback=self._EndBlink, sleep=False)
            if audioAlert:
                sm.GetService('audio').SendUIEvent('crimewatch_locked_play')

    def _EndBlink(self):
        self.isAnimating = False
        self.blinkCurve.Stop()
        self.blinkCurve = None
        self.SetColor(self._color)


class SafetyButton(Container):
    __guid__ = 'shipSafetyButton.SafetyButton'
    default_align = uiconst.TOPLEFT
    default_width = 24
    default_height = 24
    default_state = uiconst.UI_NORMAL
    default_hintDelay = HINT_DELAY
    __notifyevents__ = ['OnSafetyLevelChanged', 'OnCrimewatchSafetyCheckFailed', 'OnReCheckAlphaLock']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        cwsvc = sm.GetService('crimewatchSvc')
        self.canBeModified = not cwsvc.IsSafetyLockedToFullLevel()
        self.isAlphaLocked = cwsvc.IsSafetyAlphaLocked()
        sm.RegisterNotify(self)
        self.safetyLevel = None
        self.selector = None
        self.content = Container(parent=self, name='content', align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, pos=(0, 0, 24, 24))
        self.hilite = Sprite(parent=self.content, name='hilite', align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/utilBtnBaseAndShadow.png', color=(0.63, 0.63, 0.63, 1.0), blendMode=trinity.TR2_SBM_ADD, scale=(0.75, 0.75), display=False)
        Sprite(parent=self.content, name='baseButton', align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/utilBtnBaseAndShadow.png', scale=(0.75, 0.75))
        Sprite(parent=self, name='busy', align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/utilBtnGlow.png', color=(0, 0, 0, 0.8))
        self.led = LightEmittingDiode(parent=self.content, align=uiconst.CENTER)
        safetyLevel = cwsvc.GetSafetyLevel()
        self.SetSafetyLevel(safetyLevel, doAlert=False)

    def OnReCheckAlphaLock(self):
        self.isAlphaLocked = sm.GetService('crimewatchSvc').IsSafetyAlphaLocked()
        if self.selector:
            self.selector.SetIsAlphaLocked(self.isAlphaLocked)

    def SetSafetyLevel(self, safetyLevel, doAlert = True):
        self.safetyLevel = safetyLevel
        self.OnReCheckAlphaLock()
        data = SAFETY_LEVEL_DATA_MAP[safetyLevel]
        self.led.SetColor(data.color.GetRGBA())
        if doAlert:
            sm.GetService('audio').SendUIEvent(data.audioEvent)

    def GetHint(self):
        data = SAFETY_LEVEL_DATA_MAP[self.safetyLevel]
        if self.canBeModified:
            hintText = localization.GetByLabel(data.GetSafetySelectionHint(), color=data.color.GetHex())
        else:
            hintText = localization.GetByLabel('UI/Crimewatch/SafetyLevel/SafetyButtonFullHintLocked', color=data.color.GetHex())
        return hintText

    def OnMouseEnter(self):
        PlaySound(uiconst.SOUND_BUTTON_HOVER)
        self.hilite.display = True

    def OnMouseExit(self):
        self.hilite.display = False

    def OnClick(self):
        if self.selector is None or self.selector.destroyed:
            PlaySound(uiconst.SOUND_EXPAND)
            self.selector = SafetyLevelSelector(parent=uicore.layer.hint, safetyLevel=self.safetyLevel, anchor=self, canBeModified=self.canBeModified, width=270 * fontconst.fontSizeFactor, isAlphaLocked=self.isAlphaLocked)

    def OnMouseDown(self, btn, *args):
        self.content.top = 1

    def OnMouseUp(self, *args):
        self.content.top = 0

    def OnSafetyLevelChanged(self, safetyLevel):
        self.SetSafetyLevel(safetyLevel)
        if self.selector is None or self.selector.destroyed:
            return
        self.selector.state = uiconst.UI_DISABLED
        while self.selector.confirmationButton and not self.selector.confirmationButton.destroyed:
            blue.pyos.synchro.SleepSim(25)

        self.selector.SetSafetyLevel(safetyLevel)
        blue.pyos.synchro.SleepSim(500)
        self.selector.CloseSelector()
        self.led.Blink(audioAlert=False)

    def OnCrimewatchSafetyCheckFailed(self):
        self.led.Blink()


class SafetyLevelSelector(Container):
    __guid__ = 'shipSafetyButton.SafetyLevelSelector'
    default_width = 230
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.TOPLEFT
    default_name = 'SafetyLevelSelector'

    def SetIsAlphaLocked(self, isAlphaLocked):
        for btn in self.securityButtons:
            btn.SetIsAlphaLocked(isAlphaLocked)

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        currentSafetyLevel = attributes.get('safetyLevel')
        isAlphaLocked = attributes.get('isAlphaLocked')
        self.isTabStop = True
        self.confirmationButton = None
        self.anchor = attributes.get('anchor')
        self.canBeModified = attributes.get('canBeModified', True)
        FillThemeColored(bgParent=self, opacity=OPACITY_BG)
        self.lineTrace = None
        bodyText = '<center>%s</center>' % localization.GetByLabel('UI/Crimewatch/SafetyLevel/SafetyLevelSelectionBody', suspectColor=crimewatchConst.Colors.Yellow.GetHex(), criminalColor=crimewatchConst.Colors.Red.GetHex())
        captionCont = Container(parent=self, align=uiconst.TOTOP, name='captionCont', height=24)
        eveLabel.EveLabelMedium(parent=captionCont, align=uiconst.CENTERTOP, text='<center>%s</center>' % localization.GetByLabel('UI/Crimewatch/SafetyLevel/SafetySettingsCaption'), width=self.width - 2 * TEXT_PADDING, padTop=TEXT_PADDING, color=Color.WHITE)
        textCont = Container(parent=self, align=uiconst.TOTOP, name='textCont')
        text = eveLabel.EveLabelSmall(parent=textCont, align=uiconst.CENTERTOP, text=bodyText, width=self.width - 2 * TEXT_PADDING, padTop=TEXT_PADDING)
        textCont.height = text.textheight + 2 * TEXT_PADDING
        Container(parent=self, align=uiconst.TOTOP, name='padding', height=TEXT_PADDING)
        self.securityButtons = []
        for safetyLevel in (const.shipSafetyLevelNone, const.shipSafetyLevelPartial, const.shipSafetyLevelFull):
            cont = Container(parent=self, name='SecButtonCont', align=uiconst.TOTOP, height=44)
            securityButton = SecurityButton(parent=cont, safetyLevel=safetyLevel, align=uiconst.CENTERTOP, canBeModified=self.canBeModified, width=140 * fontconst.fontSizeFactor, isAlphaLocked=isAlphaLocked)
            securityButton.SetSelected(safetyLevel == currentSafetyLevel)
            securityButton.OnClick = (self.OnSecurityButtonClick, securityButton)
            self.securityButtons.append(securityButton)

        height = 0
        for container in self.children:
            if container.GetAlign() == uiconst.TOTOP:
                height += container.height

        self.height = height
        alignToTop = IsShipHudTopAligned()
        self.DrawFrame(alignToTop)
        self.DrawPointer(alignToTop)
        self.SetPosition(alignToTop)
        self.opacity = 0.0
        uicore.animations.FadeIn(self, duration=0.1, loops=1)
        uicore.registry.SetFocus(self)

    def DrawPointer(self, alignToTop):
        pointerWidth = DOCK_POINTER_LENGTH * 2
        pointerSideWidth = int(DOCK_POINTER_LENGTH * 2 / sqrt(2))
        pointerSideWidthHalf = pointerSideWidth / 2
        if alignToTop:
            clipperAlign = uiconst.CENTERTOP
            transformAlign = uiconst.CENTERBOTTOM
        else:
            clipperAlign = uiconst.CENTERBOTTOM
            transformAlign = uiconst.CENTERTOP
        clipperCont = Container(name='clipper', parent=self, width=pointerWidth, height=DOCK_POINTER_LENGTH, clipChildren=True, align=clipperAlign, top=-DOCK_POINTER_LENGTH)
        transform = Transform(name='transform', parent=clipperCont, align=transformAlign, rotation=pi / 4, width=pointerSideWidth, height=pointerSideWidth, top=-pointerSideWidthHalf)
        FillThemeColored(bgParent=transform, opacity=OPACITY_BG)

    def SetPosition(self, alignToTop):
        left, top, width, height = self.anchor.GetAbsolute()
        if alignToTop:
            self.top = top + (self.anchor.height + DOCK_POINTER_LENGTH + DOCK_MARGIN)
        else:
            self.top = top - (self.height + DOCK_POINTER_LENGTH + DOCK_MARGIN)
        self.left = left + (self.anchor.width - self.width) * 0.5

    def DrawFrame(self, alignToTop):
        if alignToTop:
            pointList = ((0, 0),
             ((self.width - DOCK_POINTER_LENGTH * 2) * 0.5, 0),
             (self.width * 0.5, -DOCK_POINTER_LENGTH),
             ((self.width + DOCK_POINTER_LENGTH * 2) * 0.5, 0),
             (self.width, 0),
             (self.width, self.height),
             (0, self.height))
        else:
            pointList = ((0, 0),
             (self.width, 0),
             (self.width, self.height),
             ((self.width + DOCK_POINTER_LENGTH * 2) * 0.5, self.height),
             (self.width * 0.5, self.height + DOCK_POINTER_LENGTH),
             ((self.width - DOCK_POINTER_LENGTH * 2) * 0.5, self.height),
             (0, self.height))
        if self.lineTrace is not None:
            self.lineTrace.Close()
        self.lineTrace = VectorLineTrace(name='Frame', parent=self, lineWidth=1.0, spriteEffect=trinity.TR2_SFX_FILL)
        self.lineTrace.isLoop = True
        for point in pointList:
            x, y = point
            color = sm.GetService('uiColor').GetUIColor(uiconst.COLORTYPE_UIHILIGHT)
            color = color[:3] + (0.25,)
            self.lineTrace.AddPoint((x, y), color)

    def OnKillFocus(self):
        if not self.confirmationButton or self.confirmationButton.destroyed:
            uthread.new(self.Close)

    def CloseSelector(self):
        uicore.animations.FadeOut(self, sleep=True)
        self.Close()

    def OnSecurityButtonClick(self, securityButton):
        if securityButton.IsLocked():
            return
        if self.confirmationButton and not self.confirmationButton.destroyed:
            return
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        currentSafetyLevel = sm.GetService('crimewatchSvc').GetSafetyLevel()
        for button in self.securityButtons:
            if button.safetyLevel == securityButton.safetyLevel:
                button.Blink()
                if securityButton.safetyLevel < currentSafetyLevel:
                    self.confirmationButton = SafetyConfirmButton(parent=button.parent, left=5, top=1, color=securityButton.data.color.GetRGBA(), idx=0, align=uiconst.TOPRIGHT, safetyButton=button, canBeModified=self.canBeModified)
                    button.Highlight(False)
                    button.Pin()
                    uicore.registry.SetFocus(self.confirmationButton)
                else:
                    sm.GetService('crimewatchSvc').SetSafetyLevel(securityButton.safetyLevel)

    def SetSafetyLevel(self, safetyLevel):
        selected = None
        for button in self.securityButtons:
            if button.safetyLevel == safetyLevel:
                selected = button
            else:
                button.SetSelected(False)

        selected.SetSelected(True, sleep=True)


class SecurityButton(Container):
    __guid__ = 'shipSafetyButton.SecurityButton'
    default_height = 29
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL
    default_hintDelay = HINT_DELAY
    lineWidth = 5.0
    lineSeperation = 14.0

    def SetIsAlphaLocked(self, isAlphaLocked):
        self.isAlphaLocked = isAlphaLocked

    def IsLocked(self):
        if not self.canBeModified:
            return True
        return self.IsAlphaLockedAndRed()

    def IsAlphaLockedAndRed(self):
        if self.canBeModified:
            if self.isAlphaLocked:
                return self.safetyLevel == const.shipSafetyLevelNone
        return False

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.pinned = False
        self.isSelected = False
        self.canBeModified = attributes.get('canBeModified', True)
        self.isAlphaLocked = attributes.get('isAlphaLocked', False)
        self.safetyLevel = attributes.get('safetyLevel')
        self.data = SAFETY_LEVEL_DATA_MAP[self.safetyLevel]
        cont = Container(name='content', parent=self, padding=3)
        self.text = eveLabel.EveHeaderSmall(name='buttonLabel', parent=cont, color=self.data.color.GetRGBA(), text=localization.GetByLabel(self.data.buttonText), align=uiconst.CENTER, opacity=DESELECTED_BUTTON_OPACITY)
        self.defaultSprite = Sprite(parent=self, name='default', texturePath='res:/UI/Texture/Crimewatch/SafetyButton_Default.png', align=uiconst.TOALL, state=uiconst.UI_DISABLED, color=self.data.color.GetRGBA(), opacity=DESELECTED_BUTTON_OPACITY)
        self.highlightSprite = Sprite(parent=self, name='highlight', texturePath='res:/UI/Texture/Crimewatch/SafetyButton_Highlight.png', align=uiconst.TOALL, state=uiconst.UI_DISABLED, color=self.data.color.GetRGBA())
        self.highlightSprite.Hide()
        self.leftArrowSprite = Sprite(parent=self, name='leftArrows', texturePath='res:/UI/Texture/Crimewatch/Safety_Selection.png', align=uiconst.CENTERLEFT, pos=(-24, 0, 16, 13), state=uiconst.UI_DISABLED, color=self.data.color.GetRGBA(), opacity=0.0)
        self.rightArrows = Transform(parent=self, name='rightArrowsTranform', align=uiconst.CENTERRIGHT, pos=(-24, 0, 16, 13), state=uiconst.UI_DISABLED, rotation=pi)
        self.rightArrowSprite = Sprite(parent=self.rightArrows, name='rightArrows', texturePath='res:/UI/Texture/Crimewatch/Safety_Selection.png', align=uiconst.CENTERRIGHT, pos=(0, 0, 16, 13), state=uiconst.UI_DISABLED, color=self.data.color.GetRGBA(), opacity=0.0)

    def GetHint(self):
        if self.canBeModified:
            if self.IsAlphaLockedAndRed():
                return localization.GetByLabel('UI/Crimewatch/SafetyLevel/SafetyButtonNoneOptionHintAlphaLocked')
            return localization.GetByLabel(self.data.GetSafetySelectionHint())
        else:
            return localization.GetByLabel(self.data.GetSafetySelectionHintLocked())

    def Pin(self):
        self.pinned = True
        self.text.opacity = 1.0
        self.defaultSprite.opacity = 1.0

    def Unpin(self):
        self.pinned = False
        self.text.opacity = DESELECTED_BUTTON_OPACITY
        self.defaultSprite.opacity = DESELECTED_BUTTON_OPACITY

    def SetSelected(self, selected, sleep = False):
        if selected:
            self.isSelected = True
            self.text.opacity = 1.0
            self.defaultSprite.opacity = 1.0
            self.leftArrowSprite.opacity = 1.0
            self.rightArrowSprite.opacity = 1.0
            curveSet = uicore.animations.MoveInFromLeft(self.leftArrowSprite, loops=1, duration=0.4, amount=20)
            uicore.animations.MoveInFromRight(self.rightArrowSprite, loops=1, duration=0.4, amount=20, curveSet=curveSet, sleep=sleep)
        else:
            self.isSelected = False
            self.text.opacity = DESELECTED_BUTTON_OPACITY
            self.defaultSprite.opacity = DESELECTED_BUTTON_OPACITY
            if self.leftArrowSprite.opacity > 0.0 or self.rightArrowSprite.opacity > 0.0:
                curveSet = uicore.animations.FadeOut(self.leftArrowSprite, duration=0.25)
                uicore.animations.FadeOut(self.rightArrowSprite, duration=0.25, curveSet=curveSet)

    def Highlight(self, enable):
        if self.IsLocked():
            return
        if enable and not self.IsConfirmButtonActive():
            self.defaultSprite.Hide()
            self.highlightSprite.Show()
            self.text.opacity = 1.0
        else:
            self.defaultSprite.Show()
            self.highlightSprite.Hide()
            if self.isSelected or self.pinned:
                self.text.opacity = 1.0
            else:
                self.text.opacity = DESELECTED_BUTTON_OPACITY

    def OnMouseEnter(self):
        if not self.IsLocked():
            PlaySound(uiconst.SOUND_BUTTON_HOVER)
            self.Highlight(True)

    def OnMouseExit(self):
        if not self.IsLocked():
            self.Highlight(False)

    def IsConfirmButtonActive(self):
        return not (self.parent.parent.confirmationButton is None or self.parent.parent.confirmationButton.destroyed)

    def Blink(self, sleep = True):
        curveSet = uicore.animations.SpGlowFadeTo(self.highlightSprite, startColor=self.data.color.GetRGBA(), glowExpand=0.0)
        uicore.animations.SpGlowFadeTo(self.defaultSprite, startColor=self.data.color.GetRGBA(), glowExpand=0.0, curveSet=curveSet)


class SafetyConfirmButton(Container):
    default_width = 50
    default_height = 27
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.TOPRIGHT
    default_name = 'SafetyConfirmButton'
    default_hintDelay = HINT_DELAY

    def ApplyAttributes(self, attributes):
        super(SafetyConfirmButton, self).ApplyAttributes(attributes)
        self.isTabStop = True
        self.canBeModified = attributes.get('canBeModified', True)
        self.safetyButton = attributes.get('safetyButton')
        self.color = attributes.get('color', (1, 1, 1, 1))
        self.bgColor = (self.color[0] * 0.3,
         self.color[1] * 0.3,
         self.color[2] * 0.3,
         1.0)
        self.label = eveLabel.EveLabelSmall(parent=self, text=localization.GetByLabel('UI/Common/Confirm'), color=self.color, align=uiconst.CENTER)
        self.frame = Frame(parent=self, frameConst=('ui_105_32_1', 8, -4), color=self.color, opacity=0.5)
        self.fill = Fill(parent=self, color=self.bgColor)
        self.SetHint(localization.GetByLabel('UI/Crimewatch/SafetyLevel/SafetyConfirmHint', color=self.safetyButton.data.color.GetHex()))
        width, _ = self.label.GetAbsoluteSize()
        self.width = max(self.width, width + 4)

    def OnMouseEnter(self):
        if self.canBeModified:
            PlaySound(uiconst.SOUND_BUTTON_HOVER)
            self.label.SetTextColor(Color.WHITE)

    def OnMouseExit(self):
        if self.canBeModified:
            self.label.SetTextColor(self.color)

    def OnClick(self):
        if not self.canBeModified:
            return
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        self.state = uiconst.UI_DISABLED
        self.safetyButton.Blink()
        self.Blink()
        sm.GetService('crimewatchSvc').SetSafetyLevel(self.safetyButton.safetyLevel)
        uthread.new(self._CloseButton)

    def OnKillFocus(self):
        uthread.new(self._CloseButton)

    def _CloseButton(self):
        if not self or self.destroyed:
            return
        self.safetyButton.Unpin()
        uicore.registry.SetFocus(self.parent.parent)
        uicore.animations.FadeOut(self, duration=0.1, sleep=True)
        self.Close()

    def Blink(self):
        curveSet = uicore.animations.SpGlowFadeTo(self.frame, startColor=self.color, glowExpand=0.0)
        uicore.animations.SpGlowFadeTo(self.fill, glowExpand=0.0, startColor=self.bgColor, curveSet=curveSet, sleep=True)
