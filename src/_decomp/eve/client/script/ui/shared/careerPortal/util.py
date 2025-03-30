#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\careerPortal\util.py
from eve.client.script.ui.skillPlan.skillPlanDockablePanel import SkillPlanDockablePanel
from carbonui.uicore import uicore

def OpenSkillPlanWindow(careerID):
    wnd = SkillPlanDockablePanel.ToggleOpenClose()
    wnd.ShowCertifiedPlans(careerID)
    uicore.registry.SetFocus(wnd)
