#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\industry\submitButton.py
import math
from carbonui import uiconst
from carbonui.primitives.sprite import Sprite
from carbonui.util.color import Color
from eve.client.script.ui.control.buttons import OPACITY_LABEL_IDLE
from carbonui.control.button import Button
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.shared.industry import industryUIConst
from eve.client.script.ui.shared.industry.views.errorFrame import ErrorFrame
from eve.client.script.ui.shared.industry.views.industryTooltips import SubmitButtonTooltipPanel
import industry
import trinity
import uthread
from eveexceptions import UserError
from localization import GetByLabel
from carbonui.uicore import uicore

class PrimaryButton(Button):

    def ApplyAttributes(self, attributes):
        Button.ApplyAttributes(self, attributes)
        self.tooltipErrors = None
        self.isStopPending = False
        self.isArrowsAnimating = False
        self.func = self.ClickFunc
        self._incoming_label = None

    def GetTranslation(self):
        return self.width / 120.0 / 6.0

    def GetColor(self):
        if self.IsErrorPresent() or self.isStopPending:
            return industryUIConst.COLOR_RED
        else:
            return Color.GRAY2

    def IsErrorPresent(self):
        return False

    def AnimateArrows(self):
        self.busy = True

    def StopAnimateArrows(self):
        self.busy = False

    def HideArrows(self):
        self.StopAnimateArrows()

    def UpdateState(self):
        self.UpdateLabel()
        self.UpdateArrowsByState()
        self.UpdateBlinkByState()
        self.UpdateIsEnabledByState()

    def UpdateBlinkByState(self):
        if self.IsBlinking():
            self.Blink(time=3000)
        else:
            self.Blink(False)

    def IsBlinking(self):
        return False

    def UpdateIsEnabledByState(self):
        pass

    def UpdateArrowsByState(self):
        if self.IsErrorPresent():
            self.Disable()
        else:
            self.Enable()

    def IsActive(self):
        return True

    def UpdateLabel(self):
        self.label = self.GetText()

    def GetText(self):
        return GetByLabel('UI/Industry/Start')

    def SetLabelAnimated(self, text):
        uthread.new(self._SetLabelAnimated, text)

    def _SetLabelAnimated(self, text):
        self._incoming_label = text
        uicore.animations.FadeOut(self.sr.label, duration=0.15, sleep=True)
        self.SetLabel(self._incoming_label)
        uicore.animations.FadeIn(self.sr.label, duration=0.3)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        pass

    def ClickFunc(self, *args):
        pass

    def OnMouseEnter(self, *args):
        Button.OnMouseEnter(self, *args)


class SubmitButton(PrimaryButton):

    def ApplyAttributes(self, attributes):
        PrimaryButton.ApplyAttributes(self, attributes)
        self.jobData = attributes.jobData

    def OnNewJobData(self, jobData):
        self.oldJobData = self.jobData
        self.jobData = jobData
        self.isStopPending = False
        if self.jobData:
            self.jobData.on_updated.connect(self.OnJobUpdated)
            self.jobData.on_errors.connect(self.OnJobUpdated)
        self.UpdateState()

    def OnJobUpdated(self, *args):
        self.UpdateState()

    def GetColor(self):
        if not self.jobData or self.jobData.status == industry.STATUS_DELIVERED:
            return Color.GRAY2
        if self.jobData.errors or self.isStopPending:
            return industryUIConst.COLOR_RED
        color = industryUIConst.GetJobColor(self.jobData)
        if self.jobData and self.jobData.status == industry.STATUS_UNSUBMITTED:
            color = Color(*color).SetAlpha(0.5).GetRGBA()
        return color

    def IsErrorPresent(self):
        return self.jobData.errors

    def UpdateState(self):
        self.UpdateLabel()
        if not self.jobData:
            return
        self.UpdateArrowsByState()
        self.UpdateBlinkByState()
        self.UpdateIsEnabledByState()

    def UpdateBlinkByState(self):
        if self.jobData.status == industry.STATUS_READY:
            self.Blink(time=3000)
        else:
            self.Blink(False)

    def UpdateIsEnabledByState(self):
        if self.jobData and self.IsErrorPresent():
            self.Disable()
        else:
            self.Enable()

    def IsBlinking(self):
        return self.jobData.status == industry.STATUS_READY

    def UpdateArrowsByState(self):
        if self.jobData.status == industry.STATUS_INSTALLED:
            if not self.oldJobData or self.oldJobData.status != industry.STATUS_INSTALLED:
                self.AnimateArrows()
        elif self.jobData.status == industry.STATUS_DELIVERED:
            self.HideArrows()
        else:
            self.StopAnimateArrows()

    def GetText(self):
        if not self.jobData or self.jobData.status == industry.STATUS_UNSUBMITTED:
            return GetByLabel('UI/Industry/Start')
        if self.jobData.status in (industry.STATUS_INSTALLED, industry.STATUS_PAUSED):
            if self.isStopPending:
                return GetByLabel('UI/Common/Confirm')
            else:
                return GetByLabel('UI/Industry/Stop')
        elif self.jobData.status == industry.STATUS_READY:
            return GetByLabel('UI/Industry/Deliver')

    def ClickFunc(self, *args):
        if self.jobData.IsInstalled():
            if self.jobData.status == industry.STATUS_READY:
                sm.GetService('industrySvc').CompleteJob(self.jobData.jobID, self.jobData.solarSystemID)
                sm.GetService('audio').SendUIEvent('ind_jobDelivered')
            elif self.isStopPending:
                try:
                    sm.GetService('industrySvc').CancelJob(self.jobData.jobID, self.jobData.solarSystemID)
                finally:
                    self.isStopPending = False
                    self.UpdateState()

            else:
                self.isStopPending = True
                self.UpdateState()
        else:
            try:
                self.Disable()
                if not self.IsErrorPresent():
                    self.AnimateArrows()
                sm.GetService('industrySvc').InstallJob(self.jobData)
                sm.GetService('audio').SendUIEvent('ind_jobStarted')
            except UserError as exception:
                if getattr(exception, 'msg', None) == 'IndustryValidationError':
                    self.tooltipErrors = exception.args[1]['errors']
                    uicore.uilib.tooltipHandler.RefreshTooltipForOwner(self)
                raise
            finally:
                self.Enable()
                self.StopAnimateArrows()

    def LoadTooltipPanel(self, tooltipPanel, *args):
        if self.tooltipErrors is not None:
            errors = self.tooltipErrors
            self.tooltipErrors = None
        else:
            errors = self.jobData.errors
        SubmitButtonTooltipPanel(status=self.jobData.status, errors=errors, tooltipPanel=tooltipPanel)
