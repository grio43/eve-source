#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\abyss\activateButton.py
import abyss
from carbonui import uiconst
from carbonui.uicore import uicore
from carbonui.util.color import Color
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.shared.industry.submitButton import PrimaryButton
from eve.client.script.ui.shared.industry.views.errorFrame import ErrorFrame
import localization

class ActivateButton(PrimaryButton):

    def ApplyAttributes(self, attributes):
        super(ActivateButton, self).ApplyAttributes(attributes)
        self.controller = attributes.controller
        self.UpdateState()
        self.controller.onChange.connect(self.UpdateState)

    def IsActive(self):
        return self.controller.isReady or self.controller.isActivating

    def IsBlinking(self):
        return self.controller.isActivating

    def IsErrorPresent(self):
        return bool(self.controller.errors) and not self.controller.isReady

    def GetColor(self):
        if self.IsErrorPresent():
            return Color.RED
        else:
            return sm.GetService('uiColor').GetUIColor(uiconst.COLORTYPE_UIHILIGHT)

    def UpdateBlinkByState(self):
        pass

    def UpdateIsEnabledByState(self):
        if self.controller.isReady:
            self.Enable()
        else:
            self.Disable()

    def UpdateState(self):
        super(ActivateButton, self).UpdateState()
        super(ActivateButton, self).UpdateBlinkByState()
        uicore.uilib.tooltipHandler.RefreshTooltipForOwner(self)

    def ClickFunc(self, *args):
        self.controller.Activate()

    def LoadTooltipPanel(self, panel, *args):
        errors = self.controller.errors
        ActivateButtonTooltipPanel(errors=errors, panel=panel)

    def GetText(self):
        return self.controller.GetText()


class ActivateButtonTooltipPanel(object):

    def __init__(self, errors, panel):
        self.panel = panel
        self.Reconstruct(errors)

    def Reconstruct(self, errors):
        if self.panel.destroyed:
            return
        self.panel.margin = (8, 8, 8, 0)
        self.panel.columns = 2
        self.panel.Flush()
        if not errors:
            return
        self.panel.cellSpacing = (0, 4)
        for error, errorArgs in errors:
            self.AddErrorRow(error, errorArgs)

        self.panel.AddSpacer(width=0, height=4, colSpan=2)

    def AddErrorRow(self, error, args):
        text = abyss.get_error_label(localization.GetByLabel, error, *args)
        description = eveLabel.EveLabelMedium(text=text, align=uiconst.TOPLEFT)
        description.width = min(description.textwidth, 320)
        cell = self.panel.AddCell(description, colSpan=2, cellPadding=(8, 4, 8, 4))
        frame = ErrorFrame(bgParent=cell, opacityLow=0.15, opacityHigh=0.25)
        frame.Show()
