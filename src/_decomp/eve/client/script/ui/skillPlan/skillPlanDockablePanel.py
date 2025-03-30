#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\skillPlanDockablePanel.py
import logging
from carbon.common.script.sys.serviceConst import ROLE_PROGRAMMER, ROLE_QA
from carbonui import uiconst
from eve.client.script.ui.shared.mapView.dockPanel import DockablePanel
from eve.client.script.ui.skillPlan.skillPlanPanel import SkillPlanPanel
from eve.client.script.ui.view.viewStateConst import ViewState
from skills.skillplan.skillPlanService import GetSkillPlanSvc
PADDING_WINDOWED = (16, 40, 16, 16)
PADDING_FULLSCREEN = (32, 60, 32, 32)
logger = logging.getLogger(__name__)

class SkillPlanDockablePanel(DockablePanel):
    default_captionLabelPath = 'Tooltips/CharacterSheet/Skills'
    default_windowID = 'SkillPlanner'
    default_iconNum = 'res:/ui/texture/windowIcons/skills.png'
    default_minSize = (1024, 768)
    panelID = default_windowID
    default_clipChildren = True
    viewState = ViewState.SkillPlan
    hasImmersiveAudioOverlay = True

    def ApplyAttributes(self, attributes):
        super(SkillPlanDockablePanel, self).ApplyAttributes(attributes)
        skillPlanTemplate = attributes.get('skillPlanTemplate', None)
        self.skillPlanPanel = SkillPlanPanel(parent=self.sr.main, state=uiconst.UI_NORMAL, padding=PADDING_FULLSCREEN, skillPlanTemplate=skillPlanTemplate)

    def FinalizeModeChange(self, registerSettings = True):
        super(SkillPlanDockablePanel, self).FinalizeModeChange(registerSettings)
        if self.IsFullscreen():
            self.skillPlanPanel.padding = PADDING_FULLSCREEN
        else:
            self.skillPlanPanel.padding = PADDING_WINDOWED

    def OnBack(self, *args):
        self.skillPlanPanel.OnBack()

    def IsClosable(self):
        try:
            if self.skillPlanPanel and not self.skillPlanPanel.destroyed:
                editor = self.skillPlanPanel.skillPlanEditor
                if editor and not editor.destroyed:
                    if not editor.ShouldContinueAfterAskingAboutLeavingEditor():
                        return False
        except Exception as e:
            logger.exception(e.message)

        return True

    def DeactivateUnderlay(self):
        if not self.IsFullscreen():
            self.sr.underlay.AnimExit()

    def GetMenu(self, *args):
        m = super(SkillPlanDockablePanel, self).GetMenu(*args)
        if session.role & (ROLE_PROGRAMMER | ROLE_QA):
            m.append(('Flush Skill Plan cache', GetSkillPlanSvc().FlushCache))
        return m

    def ShowCertifiedPlans(self, careerID):
        self.skillPlanPanel.ShowCertifiedPlans(careerID)
