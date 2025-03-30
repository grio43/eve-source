#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPageInfoConts\escalationInfoContainer.py
import blue
import uthread
from carbonui import uiconst
from eve.client.script.ui import eveColor
from eve.client.script.ui.shared.agencyNew.ui.contentPageInfoConts.combatAnomalyInfoContainer import CombatAnomalyInfoContainer
from eve.client.script.ui.shared.agencyNew.ui.controls.infoContAttribute import InfoContAttribute
from eve.client.script.ui.shared.agencyNew.ui.controls.warningContainer import WarningContainer
from localization import GetByLabel

class EscalationInfoContainer(CombatAnomalyInfoContainer):
    default_name = 'EscalationInfoContainer'
    default_headerText = GetByLabel('UI/Agency/EscalationsInSystem')
    default_scroll_container_height = 100

    def ConstructLayout(self):
        self.warningCont = WarningContainer(parent=self, align=uiconst.TOTOP, color=eveColor.WARNING_ORANGE, padBottom=10)
        super(EscalationInfoContainer, self).ConstructLayout()
        self.timeRemainingLabel = InfoContAttribute(parent=self, align=uiconst.TOTOP, headerText=GetByLabel('UI/Market/Marketbase/ExpiresIn'), padTop=12, idx=1)
        uthread.new(self.UpdateExpiryTimeThread)

    def UpdateExpiryTimeThread(self):
        while not self.destroyed:
            if self.clickedEntry:
                contentPiece = self.clickedEntry.contentPiece
                self.timeRemainingLabel.UpdateText(contentPiece.GetExpiryTimeShort())
            blue.synchro.SleepWallclock(100)

    def OnScrollEntryClicked(self, clickedEntry):
        super(EscalationInfoContainer, self).OnScrollEntryClicked(clickedEntry)
        text = GetByLabel('UI/Agency/EscalationDescription', systemName=clickedEntry.contentPiece.GetSolarSystemName())
        self.warningCont.SetText(text)
