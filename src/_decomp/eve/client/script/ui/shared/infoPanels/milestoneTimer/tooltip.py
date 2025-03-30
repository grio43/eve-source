#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\infoPanels\milestoneTimer\tooltip.py
from carbonui import uiconst
from carbonui.control.button import Button
from eve.client.script.ui.control.tooltips import TooltipPanel
from eve.client.script.ui.control import tooltipConst
from eve.client.script.ui.shared.infoPanels.milestoneTimer.milestoneTimerMessenger import MilestoneTimerMessenger
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from localization import GetByLabel

class MilestoneTooltip(TooltipBaseWrapper):

    def __init__(self, milestoneID, totalSeconds, secondsLeftFunc, *args, **kwargs):
        super(MilestoneTooltip, self).__init__(*args, **kwargs)
        self.milestoneID = milestoneID
        self.totalSeconds = totalSeconds
        self.secondsLeftFunc = secondsLeftFunc

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.LoadGeneric1ColumnTemplate()
        self.tooltipPanel.SetState(uiconst.UI_NORMAL)
        self.tooltipPanel.margin = tooltipConst.TOOLTIP_MARGIN
        self.ConstructEncouragementSection()
        MilestoneTimerMessenger(sm.GetService('publicGatewaySvc')).tooltip_displayed(self.milestoneID)
        return self.tooltipPanel

    def ConstructEncouragementSection(self):
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Crimewatch/Timers/milestoneRewardTooltip', minutes=self.totalSeconds / 60.0), wrapWidth=200)
        self.tooltipPanel.AddSpacer(height=10)
        self.tooltipPanel.AddCaptionMedium(text=GetByLabel('UI/Milestones/MinutesLoggedIn', minutesPassed=self.secondsLeftFunc() / 60.0, totalMinutes=self.totalSeconds / 60.0), wrapWidth=200)


class MilestoneRewardTooltip(TooltipBaseWrapper):

    def __init__(self, milestoneID, iskAmount, claimFunc, milestoneMinutes, *args, **kwargs):
        super(MilestoneRewardTooltip, self).__init__(*args, **kwargs)
        self.milestoneID = milestoneID
        self.iskAmount = iskAmount
        self.claimFunc = claimFunc
        self.milestoneMinutes = milestoneMinutes

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.LoadGeneric1ColumnTemplate()
        self.tooltipPanel.SetState(uiconst.UI_NORMAL)
        self.tooltipPanel.margin = tooltipConst.TOOLTIP_MARGIN
        self.ConstructRewardClaimSection()
        MilestoneTimerMessenger(sm.GetService('publicGatewaySvc')).tooltip_displayed(self.milestoneID)
        return self.tooltipPanel

    def ConstructRewardClaimSection(self):
        self.tooltipPanel.AddCaptionLarge(text=GetByLabel('UI/Agency/Rewards'), wrapWidth=200, textAlign=uiconst.CENTER)
        self.tooltipPanel.AddSpacer(height=10)
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Milestones/Congratulations', minutesPlayed=self.milestoneMinutes), wrapWidth=200)
        self.tooltipPanel.AddSpacer(height=10)
        self.tooltipPanel.AddCaptionSmall(text=GetByLabel('UI/Milestones/ClaimISK', amount=self.iskAmount), wrapWidth=200)
        self.tooltipPanel.AddSpacer(height=5)
        button = Button(name='claimMilestoneRewardButton', align=uiconst.CENTERLEFT, label=GetByLabel('UI/Seasons/ClaimReward'), func=self.claimFunc, analyticID='claimMilestoneRewardButton')
        self.tooltipPanel.AddCell(button, cellPadding=(0, 10, 0, 10))
