#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\pvpFilaments\client\activation_window\errorTooltipPanel.py
from eveui import EveLabelMedium
from eve.client.script.ui.shared.industry.views.errorFrame import ErrorFrame

class ErrorTooltipPanel(object):

    def __init__(self, panel, errors):
        if panel.destroyed or not errors:
            return
        self._panel = panel
        self._layout(errors)

    def _layout(self, errors):
        self._panel.margin = (8, 8, 8, 0)
        self._panel.columns = 2
        self._panel.Flush()
        self._panel.cellSpacing = (0, 4)
        for error in errors:
            self._add_error(error)

        self._panel.AddSpacer(width=0, height=4, colSpan=2)

    def _add_error(self, error):
        description = EveLabelMedium(text=error, maxWidth=320)
        cell = self._panel.AddCell(description, colSpan=2, cellPadding=(8, 4, 8, 4))
        frame = ErrorFrame(bgParent=cell, opacityLow=0.15, opacityHigh=0.25)
        frame.Show()
