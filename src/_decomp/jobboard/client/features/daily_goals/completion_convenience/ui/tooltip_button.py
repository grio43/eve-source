#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\daily_goals\completion_convenience\ui\tooltip_button.py
from carbonui import Align, Density
from jobboard.client.features.daily_goals.completion_convenience.ui.button import CompletionConvenienceTooltipButton
from jobboard.client.features.daily_goals.completion_convenience.ui.tooltip import load_tooltip

def load_tooltip_with_button(tooltip_panel, job):
    load_tooltip(tooltip_panel)
    tooltip_panel.AddSpacer(colSpan=2, width=4, height=8)
    buy_button = CompletionConvenienceTooltipButton(align=Align.TOBOTTOM, density=Density.COMPACT, job=job)
    tooltip_panel.AddCell(buy_button, colSpan=2)
