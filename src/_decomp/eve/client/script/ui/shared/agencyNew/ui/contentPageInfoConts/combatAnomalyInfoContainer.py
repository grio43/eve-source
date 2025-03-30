#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPageInfoConts\combatAnomalyInfoContainer.py
from carbonui import uiconst
from eve.client.script.ui.shared.agencyNew.ui.contentPageInfoConts.jobInfoContainer import JobContentPageInfoContainer
from eve.client.script.ui.shared.agencyNew.ui.controls.enemyInfoCont import EnemyInfoCont
from eve.client.script.ui.shared.agencyNew.ui.controls.infoContAttribute import InfoContAttribute
from localization import GetByLabel
from jobboard.client import get_combat_anomaly_job

class CombatAnomalyInfoContainer(JobContentPageInfoContainer):
    default_name = 'CombatAnomalyInfoContainer'
    default_headerText = GetByLabel('UI/Agency/SitesInSystem')

    def ConstructLayout(self):
        super(CombatAnomalyInfoContainer, self).ConstructLayout()
        self.difficultyLabel = InfoContAttribute(parent=self, align=uiconst.TOTOP, headerText=GetByLabel('UI/Agency/ContentDifficulty'), padTop=12)
        self.enemyInfoCont = EnemyInfoCont(name='enemyInfoContainer', parent=self, align=uiconst.TOTOP, padTop=12)

    def _UpdateContentPiece(self, contentPiece):
        if not self.systemInfoContainer:
            return
        self.systemInfoContainer.UpdateContentPiece(contentPiece)
        if not self.primaryActionButton:
            return
        self.primaryActionButton.SetController(contentPiece)
        self.UpdateScroll()

    def OnScrollEntryClicked(self, clickedEntry):
        super(CombatAnomalyInfoContainer, self).OnScrollEntryClicked(clickedEntry)
        contentPiece = clickedEntry.contentPiece
        self.enemyInfoCont.Update(ownerID=contentPiece.GetEnemyOwnerID(), ownerTypeID=contentPiece.GetEnemyOwnerTypeID())
        self.difficultyLabel.UpdateText(contentPiece.GetSiteLevelText())

    def GetEntryContentPieces(self):
        return self.contentPiece.GetSiteContentPieces()

    def _GetJob(self, instanceID):
        return get_combat_anomaly_job(instanceID)
