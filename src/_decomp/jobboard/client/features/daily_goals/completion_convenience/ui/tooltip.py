#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\daily_goals\completion_convenience\ui\tooltip.py
from carbonui import uiconst, TextColor, Align
from chroma import Color
from jobboard.client.features.daily_goals.completion_convenience.const import TEXT_COLOR_EVERMARK_GREEN
from jobboard.client.features.daily_goals.completion_convenience.util import get_price_of_completion, can_afford_completion_convenience
from localization import GetByLabel

def load_tooltip(tooltip_panel):
    tooltip_panel.LoadGeneric1ColumnTemplate()
    tooltip_panel.SetState(uiconst.UI_NORMAL)
    tooltip_panel.margin = 16
    tooltip_panel.cellSpacing = (12, 4)
    price = get_price_of_completion()
    tooltip_panel.AddLabelMedium(color=TextColor.SECONDARY, text=GetByLabel('UI/DailyGoals/CompletionConvenienceExplanation', highlightColor=TextColor.NORMAL, rewardColor=Color(*TEXT_COLOR_EVERMARK_GREEN), amount=price), align=Align.CENTERLEFT)
    tooltip_panel.AddSpacer(colSpan=2, width=4, height=8)
    tooltip_panel.AddLabelMedium(color=TextColor.SECONDARY, text=GetByLabel('UI/DailyGoals/CompletionConvenienceMaxRepetitions', highlightColor=TextColor.NORMAL))
    if not can_afford_completion_convenience():
        tooltip_panel.AddSpacer(colSpan=2, width=4, height=8)
        tooltip_panel.AddLabelMedium(align=Align.CENTER, text=GetByLabel('UI/DailyGoals/CompletionConvenienceInsufficientFunds'), color=TextColor.DANGER)
