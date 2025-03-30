#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\skillPlanPanelWnd.py
from carbonui.control.window import Window
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.client.script.ui.skillPlan.selectedPlan.selectedSkillPlanContainer import LinkedSkillPlanContainer
from eve.client.script.ui.skillPlan import skillPlanUISignals
from carbonui import uiconst
from eveexceptions import UserError
from localization import GetByLabel
from skills.skillplan import skillPlanService
from carbonui.uicore import uicore
DEFAULT_WINDOWID = 'SkillPlanPanelWnd'

def OpenSkillPlanWnd(skillPlanID, ownerID = None):
    skillPlanSvc = skillPlanService.GetSkillPlanSvc()
    if not sm.GetService('publicGatewaySvc').is_available():
        return ShowQuickMessage(GetByLabel('UI/SkillPlan/ConnectionError'))
    try:
        skillPlan = skillPlanSvc.Get(skillPlanID)
        if not skillPlan:
            skillPlan = skillPlanSvc.GetOwnedByOther(skillPlanID, ownerID)
        if not skillPlan:
            raise UserError('SkillPlanNotFound')
    except UserError as e:
        raise e
    except Exception:
        raise UserError('SkillPlanGenericError')

    if uicore.uilib.Key(uiconst.VK_SHIFT):
        windowInstanceID = '%s_%s' % (DEFAULT_WINDOWID, skillPlanID)
    else:
        windowInstanceID = None
    wnd = SkillPlanPanelWnd.Open(windowInstanceID=windowInstanceID)
    wnd.LoadSkillPlan(skillPlan)


class SkillPlanPanelWnd(Window):
    default_minSize = [345, 650]
    default_height = 750
    default_width = 400
    default_windowID = DEFAULT_WINDOWID
    default_captionLabelPath = 'UI/SkillPlan/SkillPlan'

    def ApplyAttributes(self, attributes):
        self.selectedPlanCont = None
        skillPlanUISignals.on_skill_collapse_changing.connect(self.OnSkillCollapseChanged)
        super(SkillPlanPanelWnd, self).ApplyAttributes(attributes)

    def LoadSkillPlan(self, skillPlan):
        if self.selectedPlanCont and not self.selectedPlanCont.destroyed:
            showSkills = self.selectedPlanCont.skillsVisible
        else:
            showSkills = settings.char.ui.Get(self._GetSettingName(), False)
        overviewWidth = 0.5 if showSkills else 1.0
        self.sr.main.Flush()
        self.selectedPlanCont = LinkedSkillPlanContainer(parent=self.sr.main, align=uiconst.TOALL, skillPlan=skillPlan, showSkills=showSkills, overviewWidth=overviewWidth)
        self._SetMinSize(showSkills)
        captionText = '%s: %s' % (GetByLabel(self.default_captionLabelPath), skillPlan.GetName())
        self.SetCaption(captionText)

    def OnSkillCollapseChanged(self, skillPlan, isSkillPlanVisible, skillPlanContainer):
        if not self.selectedPlanCont or self.selectedPlanCont.destroyed or self.selectedPlanCont != skillPlanContainer:
            return
        mainWidth = self.selectedPlanCont.mainCont.GetAbsoluteSize()[0]
        self._SetMinSize(isSkillPlanVisible)
        if self.InStack():
            mainWidth = 0
        elif isSkillPlanVisible:
            mainWidth = max(2 * mainWidth, self.minsize[0])
        else:
            mainWidth = max(0.5 * mainWidth, self.minsize[0])
        self.width = mainWidth
        settings.char.ui.Set(self._GetSettingName(), isSkillPlanVisible)

    def _SetMinSize(self, isSkillPlanVisible):
        if isSkillPlanVisible:
            self.SetMinSize([600, 650])
        else:
            self.SetMinSize([345, 650])

    def _GetSettingName(self):
        settingName = '%s_ShowingSkills' % (self.windowInstanceID or self.windowID)
        return settingName
