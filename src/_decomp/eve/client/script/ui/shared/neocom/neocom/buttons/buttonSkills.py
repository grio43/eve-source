#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\neocom\buttons\buttonSkills.py
import trinity
import uthread2
from carbonui import const as uiconst
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.uianimations import animations
from carbonui.util.color import Color
from eve.client.script.ui import eveColor, eveThemeColor
from eve.client.script.ui.control.donutSegment import DonutSegment
from eve.client.script.ui.shared.neocom.neocom import neocomSignals
from eve.client.script.ui.shared.neocom.neocom.buttons.baseNeocomButton import BaseNeocomButton
from eve.client.script.ui.shared.neocom.neocom.buttons.buttonSkillsTooltipPanel import ButtonSkillsTooltipPanel
from eve.client.script.ui.shared.neocom.neocom.neocomUtil import IsBlinkingEnabled
from skills.client.skillController import SkillController
from skills.skillplan import skillPlanSignals
from skills.skillplan.skillPlanService import GetSkillPlanSvc
SCALE_SMALL = (0.7, 0.7)
LINE_WIDTH = 4.0

class BaseGauge(Transform):
    default_scalingCenter = (0.5, 0.5)

    def ApplyAttributes(self, attributes):
        super(BaseGauge, self).ApplyAttributes(attributes)
        self.color = attributes.color or eveColor.WHITE
        self.animationColor = attributes.animationColor
        self.isAnimating = False
        self.gauge = DonutSegment(name='skillGauge', parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, colorStart=self.color, colorEnd=self.color, lineWidth=LINE_WIDTH, value=0, blendMode=trinity.TR2_SBM_ADD, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.0)

    def PlayCompletionAnimation(self):
        self.isAnimating = True
        try:
            self._PlayCompletionAnimation()
        finally:
            self.isAnimating = False

    def _PlayCompletionAnimation(self):
        self._AnimScaleAndFadeOut()
        self._AnimGaugeFlashRotate()
        self._AnimScaleAndFadeIn()
        uthread2.Sleep(1.0)
        animations.FadeOut(self, duration=0.3, sleep=True)
        self.gauge.SetColor(self.color, self.color)
        animations.FadeIn(self, duration=0.6)

    def _AnimScaleAndFadeIn(self):
        duration = 0.4
        animations.Tr2DScaleTo(self, SCALE_SMALL, (1.0, 1.0), duration=duration, curveType=uiconst.ANIM_OVERSHOT)
        animations.FadeIn(self, 1.0, duration=duration, sleep=True)

    def _AnimGaugeFlashRotate(self):
        duration = 0.4
        self.StopAnimations()
        self.scale = (1.0, 1.0)
        self.opacity = 1.0
        self.gauge.SetColor(self.animationColor, self.animationColor)
        animations.MorphScalar(self.gauge, 'start', 1.0, 0.0, duration=duration)
        animations.MorphScalar(self.gauge, 'end', 1.0, 0.0, duration=duration, timeOffset=0.2, sleep=True)
        uthread2.Sleep(0.3)
        self.gauge.start = 0.0
        self.gauge.end = 1.0

    def _AnimScaleAndFadeOut(self):
        duration = 0.3
        animations.Tr2DScaleTo(self, (1.0, 1.0), SCALE_SMALL, duration=duration)
        animations.FadeIn(self, 0.0, duration=duration, sleep=True)
        return duration

    def SetValue(self, value):
        if self.isAnimating:
            return
        self.gauge.SetValue(value)

    def SetRadius(self, radius):
        self.gauge.SetRadius(radius)

    def SetColor(self, color):
        if self.isAnimating:
            return
        self.gauge.SetColor(color, color)

    def OnMouseEnter(self, *args):
        self.gauge.OnMouseEnter()

    def OnMouseExit(self, *args):
        self.gauge.OnMouseExit()


class SkillGauge(BaseGauge):

    def ApplyAttributes(self, attributes):
        super(SkillGauge, self).ApplyAttributes(attributes)
        self.checkmarkSprite = Sprite(name='checkmarkSprite', parent=self, align=uiconst.CENTER, texturePath='res:/UI/Texture/classes/Skills/checkmark.png', pos=(0, 0, 42, 37), opacity=0)

    def _PlayCompletionAnimation(self):
        self._AnimScaleAndFadeOut()
        self._AnimGaugeFlashRotate()
        self._AnimScaleAndFadeIn()
        self._AnimFadeCheckmarkIn()
        uthread2.Sleep(1.0)
        animations.FadeOut(self, duration=0.3, sleep=True)
        self.checkmarkSprite.opacity = 0.0
        self.gauge.SetColor(self.color, self.color)
        animations.FadeIn(self, duration=0.6)

    def _AnimFadeCheckmarkIn(self):
        animations.SpMaskIn(self.checkmarkSprite, duration=0.3)
        animations.FadeIn(self.checkmarkSprite, duration=0.3, sleep=True)


class SkillPlanGauge(BaseGauge):

    def _PlayCompletionAnimation(self):
        uthread2.Sleep(0.15)
        super(SkillPlanGauge, self)._PlayCompletionAnimation()


class ButtonSkills(BaseNeocomButton):
    __notifyevents__ = ['OnSkillQueueChanged', 'OnSkillQueuePaused', 'OnSkillLevelsTrained']
    default_state = uiconst.UI_NORMAL
    default_isDraggable = False

    def ApplyAttributes(self, attributes):
        self.skill = None
        self.skillPlan = None
        self.isInitialized = False
        super(ButtonSkills, self).ApplyAttributes(attributes)
        sm.RegisterNotify(self)
        skillPlanSignals.on_tracked_plan_changed.connect(self.OnSkillPlanTracked)
        skillPlanSignals.on_tracked_plan_completed.connect(self.OnTrackedSkillPlanCompleted)
        self.skillGauge = SkillGauge(name='skillGauge', parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, color=eveColor.CRYO_BLUE, animationColor=eveColor.LEAFY_GREEN)
        self.skillPlanGauge = SkillPlanGauge(name='skillPlanGauge', parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, animationColor=eveColor.COPPER_OXIDE_GREEN, lineWidth=LINE_WIDTH)
        self.bgGauge = DonutSegment(name='bgGauge', parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, colorStart=eveColor.BLACK, colorEnd=eveColor.BLACK, opacity=0.6, lineWidth=2 * LINE_WIDTH + 4)
        uthread2.start_tasklet(self._InitializeState)
        self.isInitialized = True

    def OnTrackedSkillPlanCompleted(self, skillPlanID):
        uthread2.start_tasklet(self._OnTrackedSkillPlanCompleted)

    def _OnTrackedSkillPlanCompleted(self):
        self.skillPlanGauge.PlayCompletionAnimation()
        self._UpdateGaugesAndIcon()

    def OnSkillLevelsTrained(self, skillLevels):
        self.skillGauge.PlayCompletionAnimation()
        self.UpdateSkill()

    def _InitializeState(self):
        self.UpdateSkillPlanData()
        self.UpdateSkillData()
        self.UpdateGaugeRadius()
        self._UpdateGaugesAndIcon()
        uthread2.StartTasklet(self.UpdateThread)

    def OnSkillPlanTracked(self, oldSkillPlan, skillPlan):
        self.skillPlan = skillPlan
        self._UpdateGaugesAndIcon()

    def UpdateSkillPlanData(self):
        self.skillPlan = GetSkillPlanSvc().GetTrackedSkillPlan()

    def OnSkillQueueChanged(self):
        self.UpdateSkill()

    def OnSkillQueuePaused(self):
        self.UpdateSkill()

    def UpdateSkill(self):
        self.UpdateSkillData()
        self._UpdateGaugesAndIcon()

    def UpdateSkillData(self):
        typeID = sm.GetService('skillqueue').GetActiveSkillTypeID()
        if typeID:
            self.skill = SkillController(typeID=typeID)
        else:
            self.skill = None

    def UpdateThread(self):
        while not self.destroyed:
            self._UpdateGaugesAndIcon()
            uthread2.Sleep(1.0)

    def _UpdateGaugesAndIcon(self):
        self._UpdateSkillPlanGauge()
        self._UpdateSkillGauge()
        self._UpdateBGGauge()
        self.UpdateIcon()

    def _UpdateBGGauge(self):
        if self.skill:
            self.bgGauge.Show()
        else:
            self.bgGauge.Hide()

    def _UpdateSkillGauge(self):
        if self.skill:
            value = self.skill.GetTrainingProgressForCurrLevel()
        else:
            value = 0.0
        self.skillGauge.SetValue(value)

    def _UpdateSkillPlanGauge(self):
        if self.skill and self.skillPlan:
            value = self.skillPlan.GetProgressRatio()
            color = eveColor.TUNGSTEN_GREY
            blendMode = trinity.TR2_SBM_ADD
        elif self.skill:
            value = 1.0
            color = Color(*eveColor.TUNGSTEN_GREY).SetOpacity(0.1).GetRGBA()
            blendMode = trinity.TR2_SBM_ADD
        else:
            value = 1.0
            color = Color(*eveThemeColor.THEME_ALERT).SetOpacity(0.6).GetRGBA()
            blendMode = trinity.TR2_SBM_BLEND
        self.skillPlanGauge.SetColor(color)
        self.skillPlanGauge.SetValue(value)
        self.skillPlanGauge.gauge.blendMode = blendMode

    def GetMenu(self):
        m = super(ButtonSkills, self).GetMenu()
        wnd = self.btnData.wndCls.GetIfOpen()
        if wnd:
            m += wnd.GetMenu()
        return m

    def _GetTexturePath(self):
        if not self.skill:
            if sm.GetService('skillqueue').IsAllCharacterTrainingSlotsUsed():
                texturePath = 'res:/UI/Texture/classes/Skills/pauseIcon.png'
            else:
                texturePath = 'res:/UI/Texture/classes/Skills/warningIcon.png'
        else:
            texturePath = None
        return texturePath

    def LoadTooltipPanel(self, tooltipPanel, *args):
        pass

    def ConstructTooltipPanel(self):
        return ButtonSkillsTooltipPanel(skill=self.skill, skillPlan=self.skillPlan)

    def _OnResize(self, *args):
        super(ButtonSkills, self)._OnResize(*args)
        if self.isInitialized:
            self.UpdateGaugeRadius()

    def UpdateGaugeRadius(self):
        width, _ = self.GetAbsoluteSize()
        radius = width / 2 - 5.0
        self.bgGauge.SetRadius(radius + 1.0)
        self.skillPlanGauge.SetRadius(radius + 1.0)
        self.skillGauge.SetRadius(radius - LINE_WIDTH - 2.0)

    def ShouldBlinkIcon(self):
        if not IsBlinkingEnabled() or not self.btnData.IsBlinkingEnabled():
            return False
        return not self.skill and not sm.GetService('skillqueue').IsAllCharacterTrainingSlotsUsed()

    def OnMouseEnter(self, *args):
        super(ButtonSkills, self).OnMouseEnter(*args)
        self.skillPlanGauge.OnMouseEnter()
        self.skillGauge.OnMouseEnter()

    def OnMouseExit(self, *args):
        super(ButtonSkills, self).OnMouseExit(*args)
        self.skillPlanGauge.OnMouseExit()
        self.skillGauge.OnMouseExit()
