#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\browser\skillPlanEntry.py
import eveicon
import logging
import blue
import uthread2
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.sys.serviceConst import ROLE_PROGRAMMER
from carbonui import TextColor, uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.stretchspritehorizontal import StretchSpriteHorizontal
from carbonui.uianimations import animations
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveLabelLarge, EveCaptionLarge
from eve.client.script.ui.control.gauge import GaugeMultiValue
from eve.client.script.ui.skillPlan import skillPlanUISignals
from eve.client.script.ui.skillPlan.browser.skillPlanEntryTooltip import SkillPlanEntryTooltip
from eveui import Sprite
from localization import GetByLabel
from skills.skillplan import skillPlanSignals
from skills.skillplan.loggers.skillPlanLogger import log_certified_skill_plan_clicked
from skills.skillplan.skillPlanDragData import SkillPlanDragData
from skills.skillplan.skillPlanService import GetSkillPlanSvc
from uihighlighting.uniqueNameConst import GetUniqueSkillPlanName
logger = logging.getLogger(__name__)
TRACKED_ICON_SIZE = 20
OPACITY_BG_IDLE = 0.1
OPACITY_BG_HOVER = 0.3

class SkillPlanEntry(Container):
    default_name = 'SkillPlanEntry'
    default_state = uiconst.UI_NORMAL
    isDragObject = True
    __notifyevents__ = ['OnSkillQueueChanged']

    def ApplyAttributes(self, attributes):
        super(SkillPlanEntry, self).ApplyAttributes(attributes)
        sm.RegisterNotify(self)
        skillPlanSignals.on_tracked_plan_changed.connect(self.OnTrackedPlanChanged)
        self.skillPlan = attributes.skillPlan
        self.name = 'SkillPlanEntry_%s' % self.skillPlan.GetInternalName()
        if attributes.addUniqueName:
            self.AddUniqueName()
        self.gauge = None
        self.trackedIcon = None
        self.trainingTimeLabel = None
        self.updateTrainingTimeThread = None
        self.mainCont = Container(name='mainCont', parent=self, padding=(27, 53, 0, 0))
        self.ConstructTextCont()
        self.ConstructCompletionIndicators()
        self.underlay = StretchSpriteHorizontal(bgParent=self, texturePath='res:/UI/Texture/classes/SkillPlan/planEntryBG.png', opacity=OPACITY_BG_IDLE, leftEdgeSize=27)
        uthread2.start_tasklet(self.UpdateState)

    def ConstructTextCont(self):
        textCont = Container(name='textCont', parent=self.mainCont, align=uiconst.TOTOP, height=38, padRight=34)
        EveCaptionLarge(parent=textCont, align=uiconst.TOBOTTOM, padBottom=8, text=self.skillPlan.GetName(), autoFadeSides=True, maxLines=3)

    def UpdateState(self):
        self.CheckShowOmegaIndicator()
        self.UpdateProgressGauge()
        self.UpdateTrackedIcon()
        self.UpdateCompletedIcon()
        self.UpdateTrainingTimeLabel()

    def UpdateTrainingTimeLabel(self):
        self.trainingTimeLabel.text = self.skillPlan.GetTotalTrainingTimeLeftText()
        self.bottomCont.height = max(self.trainingTimeLabel.height, self.bottomCont.height)
        if self.skillPlan.IsCompleted():
            self.trainingTimeLabel.SetRGBA(*TextColor.SUCCESS)
            if self.updateTrainingTimeThread:
                self.updateTrainingTimeThread.kill()
        else:
            self.trainingTimeLabel.SetRGBA(*TextColor.NORMAL)

    def ConstructCompletionIndicators(self):
        self.trackedIcon = Sprite(name='trackedIcon', parent=self, state=uiconst.UI_HIDDEN, align=uiconst.TOPRIGHT, pos=(12,
         20,
         TRACKED_ICON_SIZE,
         TRACKED_ICON_SIZE), texturePath=eveicon.look_at.resolve(16), hint=GetByLabel('UI/SkillPlan/TrackedSkillPlan'))
        self.gauge = GaugeMultiValue(parent=self.mainCont, backgroundColor=(0, 0, 0, 0.4), colors=(eveColor.WHITE, eveColor.CRYO_BLUE), align=uiconst.TOTOP, gaugeHeight=4)
        self.bottomCont = Container(name='bottomCont', parent=self.mainCont, align=uiconst.TOTOP, height=20, padTop=10)
        self.trainingTimeLabel = EveLabelLarge(parent=self.bottomCont, align=uiconst.CENTERLEFT)
        rightIconCont = Container(name='rightIconCont', parent=self.bottomCont, align=uiconst.CENTERRIGHT, pos=(8, 0, 68, 34))
        self.omegaCont = Container(parent=rightIconCont, align=uiconst.TORIGHT, pos=(0, 0, 34, 34))
        Sprite(name='omegaIcon', parent=self.omegaCont, align=uiconst.CENTER, pos=(0, 0, 20, 20), texturePath='res:/UI/Texture/classes/Seasons/omega_32x32.png')
        self.omegaCont.display = False
        self.completedIcon = Sprite(name='completedIcon', parent=rightIconCont, align=uiconst.TORIGHT, pos=(0, 0, 34, 34), texturePath='res:/UI/Texture/classes/SkillPlan/completedIcon.png')
        self.completedIcon.display = False

    def CheckShowOmegaIndicator(self):
        if self.skillPlan.IsOmega() and not sm.GetService('cloneGradeSvc').IsOmega():
            self.omegaCont.display = True
        else:
            self.omegaCont.display = False

    def OnMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_HOVER)
        animations.FadeTo(self.underlay, self.underlay.opacity, OPACITY_BG_HOVER, duration=uiconst.TIME_ENTRY)

    def OnMouseExit(self, *args):
        animations.FadeTo(self.underlay, self.underlay.opacity, OPACITY_BG_IDLE, duration=uiconst.TIME_EXIT)

    def OnClick(self, *args):
        PlaySound('skills_planner_path_select_list_play')
        skillPlanUISignals.on_selected(self.skillPlan)
        if self.skillPlan.IsCertified():
            log_certified_skill_plan_clicked(self.skillPlan.GetID())

    def GetMenu(self):
        m = []
        if self.skillPlan.IsEditable():
            m.append((GetByLabel('UI/Neocom/Edit'), self.Edit))
            m.append((GetByLabel('UI/Common/Buttons/Delete'), self.Delete))
        if session.role & ROLE_PROGRAMMER:
            m.append(None)
            m.append((u'GM: Copy Skill Plan ID', blue.pyos.SetClipboardData, (str(self.skillPlan.GetID()),)))
        return m

    def Delete(self):
        GetSkillPlanSvc().Delete(self.skillPlan.GetID())

    def Edit(self):
        skillPlanUISignals.on_edit_button(self.skillPlan)

    def UpdateProgressGauge(self):
        progressRatio = self.skillPlan.GetProgressRatio()
        inTrainingRatio = self.skillPlan.GetInTrainingRatio()
        self.gauge.SetValue(0, progressRatio)
        self.gauge.SetValue(1, progressRatio + inTrainingRatio)
        if inTrainingRatio and not self.updateTrainingTimeThread:
            self.updateTrainingTimeThread = uthread2.start_tasklet(self._UpdateTrainingTimeThread)

    def _UpdateTrainingTimeThread(self):
        while not self.destroyed:
            self.UpdateState()
            uthread2.Sleep(1.0)

    def UpdateCompletedIcon(self):
        if self.skillPlan.IsCompleted():
            self.completedIcon.Show()
        else:
            self.completedIcon.Hide()

    def UpdateTrackedIcon(self):
        if GetSkillPlanSvc().IsSkillPlanTracked(self.skillPlan.GetID()):
            self.trackedIcon.Show()
        else:
            self.trackedIcon.Hide()

    def OnTrackedPlanChanged(self, oldPlan, newPlan):
        if self.skillPlan and self.skillPlan.GetID() in [oldPlan.GetID() if oldPlan else None, newPlan.GetID() if newPlan else None]:
            self.UpdateTrackedIcon()

    def LoadTooltipPanel(self, tooltipPanel, *args):
        SkillPlanEntryTooltip(skillPlan=self.skillPlan, tooltipPanel=tooltipPanel)

    def GetTooltipPointer(self):
        return uiconst.POINT_LEFT_2

    def GetDragData(self):
        return SkillPlanDragData(self.skillPlan.GetID(), self.skillPlan.GetName(), self.skillPlan.GetOwnerID())

    def OnSkillQueueChanged(self):
        self.UpdateProgressGauge()

    def AddUniqueName(self):
        try:
            skillPlanID = self.skillPlan.GetID().int
            self.uniqueUiName = GetUniqueSkillPlanName(skillPlanID)
        except StandardError as e:
            logger.exception('Failed to set unique name for skill plan, e: %s' % e)
