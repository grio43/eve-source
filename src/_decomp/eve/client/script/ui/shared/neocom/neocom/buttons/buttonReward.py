#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\neocom\buttons\buttonReward.py
import localization
from carbonui import const as uiconst
from carbonui.uicore import uicore
from eve.client.script.ui.shared.neocom.neocom.buttons.baseNeocomButton import BaseNeocomButton
from eve.client.script.ui.shared.neocom.neocom.neocomUtil import IsBlinkingEnabled

class ButtonReward(BaseNeocomButton):

    def OnBadgeCountChanged(self):
        super(ButtonReward, self).OnBadgeCountChanged()
        if IsBlinkingEnabled():
            if sm.GetService('loginCampaignService').can_claim_now():
                self.btnData.SetBlinkingOn()

    def OnClickCommand(self):
        uicore.cmd.OpenLoginRewardWindow()

    def LoadTooltipPanel(self, tooltipPanel, owner):
        tooltipPanel.LoadGeneric3ColumnTemplate()
        description = localization.GetByLabel(self.btnData.descriptionPath)
        tooltipPanel.AddLabelShortcut(self.btnData.label, None)
        tooltipPanel.AddLabelMedium(text=description, align=uiconst.TOPLEFT, wrapWidth=200, colSpan=tooltipPanel.columns, color=(0.6, 0.6, 0.6, 1))
