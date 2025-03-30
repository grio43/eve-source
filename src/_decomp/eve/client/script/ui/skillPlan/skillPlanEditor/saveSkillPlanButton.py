#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\skillPlanEditor\saveSkillPlanButton.py
from carbonui import ButtonVariant, uiconst
from carbonui.control.button import Button
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from localization import GetByLabel

class SkillPlanEditorSaveButton(Button):
    default_variant = ButtonVariant.PRIMARY

    def ApplyAttributes(self, attributes):
        super(SkillPlanEditorSaveButton, self).ApplyAttributes(attributes)
        self.loadingWheel = LoadingWheel(parent=self, align=uiconst.CENTERLEFT, pos=(-8, 0, 50, 50), state=uiconst.UI_HIDDEN)

    def UpdateState(self, skillPlan, name):
        if skillPlan:
            noSkills = len(skillPlan.GetSkillRequirements()) == 0
            noName = len(name) == 0
            if noSkills or noName:
                self.Disable()
            else:
                self.Enable()
        else:
            self.Enable()

    def GetHint(self):
        if self.disabled:
            return GetByLabel('Tooltips/SkillPlanner/CantSaveTooltip')

    def _CallFunction(self):
        self.Disable()
        self.loadingWheel.Show()
        try:
            super(SkillPlanEditorSaveButton, self)._CallFunction()
        finally:
            self.Enable()
            self.loadingWheel.Hide()
