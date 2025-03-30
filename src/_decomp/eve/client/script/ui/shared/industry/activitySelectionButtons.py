#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\industry\activitySelectionButtons.py
from carbonui.primitives.container import Container
from carbonui.util.color import Color
from eve.client.script.ui.control.toggleButtonGroupButton import ToggleButtonGroupButtonIcon
from eve.client.script.ui.shared.industry import industryUIConst
from eve.client.script.ui.control.toggleButtonGroup import ToggleButtonGroup
from eve.client.script.ui.shared.industry.views.errorFrame import ErrorFrame
import localization
import carbonui.const as uiconst
import industry

class ActivitySelectionButtons(Container):
    default_name = 'ActivityTabs'
    default_height = 32

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.callback = attributes.callback
        self.jobData = None
        self.btnGroup = None
        self.ReconstructButtons()

    def ReconstructButtons(self):
        if self.btnGroup:
            self.btnGroup.Close()
        self.btnGroup = ToggleButtonGroup(name='myToggleBtnGroup', parent=self, align=uiconst.TOTOP, callback=self.OnActivitySelected)
        for activityID in industry.ACTIVITIES:
            isDisabled = not self._EnabledActivity(activityID)
            color = industryUIConst.GetActivityColor(activityID)
            color = Color(*color).SetBrightness(0.5).GetRGBA()
            btn = self.btnGroup.AddButton(activityID, iconPath=industryUIConst.ACTIVITY_ICONS_LARGE[activityID], iconSize=26, colorSelected=color, isDisabled=isDisabled, btnClass=ActivityToggleButtonGroupButton, activityID=activityID)
            btn.uniqueUiName = industryUIConst.ACTIVITY_HELP_POINTERS.get(activityID, None)

    def _EnabledActivity(self, activityID):
        if self.jobData is None:
            return False
        if self.jobData.blueprint is None:
            return False
        if activityID not in self.jobData.blueprint.activities:
            return False
        return True

    def OnNewJobData(self, jobData):
        oldJobData = self.jobData
        self.jobData = jobData
        if jobData:
            jobData.on_updated.connect(self.OnJobDataUpdated)
        blueprint = oldJobData.blueprint if oldJobData else None
        if jobData and jobData.blueprint.IsSameBlueprint(blueprint):
            self.UpdateSelectedBtn()
            return
        self.ReconstructButtons()
        self.UpdateState()

    def OnJobDataUpdated(self, jobData):
        self.UpdateState()

    def UpdateState(self):
        if self.jobData and self.jobData.IsInstalled():
            self.btnGroup.Disable()
            self.btnGroup.opacity = 0.5
        else:
            self.btnGroup.Enable()
            self.btnGroup.opacity = 1.0
        if not self.jobData:
            return
        self.UpdateSelectedBtn()
        for btn in self.btnGroup.buttons:
            activityID = btn.btnID
            if self.jobData.facility and activityID not in self.jobData.facility.activities:
                btn.ShowErrorFrame()
            else:
                btn.HideErrorFrame()

    def UpdateSelectedBtn(self):
        if self.btnGroup and self._EnabledActivity(self.jobData.activityID):
            self.btnGroup.SetSelectedByID(self.jobData.activityID, animate=False)

    def OnActivitySelected(self, activityID, *args):
        self.callback(self.jobData.blueprint, activityID)


class ActivityToggleButtonGroupButton(ToggleButtonGroupButtonIcon):

    def ApplyAttributes(self, attributes):
        super(ActivityToggleButtonGroupButton, self).ApplyAttributes(attributes)
        self.activityID = attributes.activityID
        color = Color(*self.colorSelected).SetBrightness(0.75).GetRGBA()
        self.errorFrame = ErrorFrame(bgParent=self, state=uiconst.UI_HIDDEN, color=color, padding=(2, 2, 2, 2), idx=0)

    def ShowErrorFrame(self):
        if not self.isDisabled:
            self.errorFrame.Show()

    def HideErrorFrame(self):
        self.errorFrame.Hide()

    def GetHint(self, *args):
        hint = '<b>%s</b><br>%s' % (localization.GetByLabel(industryUIConst.ACTIVITY_NAMES[self.activityID]), localization.GetByLabel(industryUIConst.ACTIVITY_HINTS[self.activityID]))
        if self.errorFrame.display:
            colorHex = Color.RGBtoHex(*industryUIConst.COLOR_NOTREADY)
            hint += '<br><b><color=%s>%s</color></b>' % (colorHex, localization.GetByLabel('UI/Industry/ActivityNotSupported'))
        return hint
