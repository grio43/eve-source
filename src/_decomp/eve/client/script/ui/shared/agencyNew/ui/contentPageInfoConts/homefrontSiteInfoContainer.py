#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPageInfoConts\homefrontSiteInfoContainer.py
from carbonui import uiconst, TextColor
from carbonui.control.scrollContainer import ScrollContainer
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveHeaderLarge
from eve.client.script.ui.shared.agencyNew.ui.common.descriptionIcon import DescriptionIconLabel
from eve.client.script.ui.shared.agencyNew.ui.contentPageInfoConts.jobInfoContainer import JobContentPageInfoContainer
from localization import GetByLabel
from jobboard.client import get_homefront_operation_job

class HomefrontSiteInfoContainer(JobContentPageInfoContainer):
    default_name = 'CombatAnomalyInfoContainer'
    default_headerText = GetByLabel('UI/Agency/SitesInSystem')
    __notifyevents__ = ['OnClientEvent_DestinationSet']

    def __init__(self, *args, **kwargs):
        super(HomefrontSiteInfoContainer, self).__init__(*args, **kwargs)
        sm.RegisterNotify(self)

    def Close(self):
        sm.UnregisterNotify(self)
        super(HomefrontSiteInfoContainer, self).Close()

    def OnClientEvent_DestinationSet(self, *args, **kwargs):
        self.OnScrollEntryClicked(self.clickedEntry)

    def ConstructLayout(self):
        super(HomefrontSiteInfoContainer, self).ConstructLayout()
        self.gameplayDescription = DescriptionIconLabel(parent=self, state=uiconst.UI_HIDDEN, align=uiconst.TOTOP, text=GetByLabel('UI/Dungeons/GameplayDescriptionHeader'), padTop=16)
        self.bottomCont = ScrollContainer(parent=self, align=uiconst.TOALL, padTop=16)
        self.loreDescriptionHeader = EveHeaderLarge(parent=self.bottomCont, state=uiconst.UI_HIDDEN, align=uiconst.TOTOP, text=GetByLabel('UI/Common/Description'), color=TextColor.SECONDARY)
        self.loreDescriptionBody = EveLabelMedium(parent=self.bottomCont, align=uiconst.TOTOP, state=uiconst.UI_HIDDEN)

    def OnScrollEntryClicked(self, clickedEntry):
        super(HomefrontSiteInfoContainer, self).OnScrollEntryClicked(clickedEntry)
        contentPiece = clickedEntry.contentPiece
        loreDescription = contentPiece.GetSiteDescription()
        if loreDescription:
            self.loreDescriptionBody.text = loreDescription
            self.loreDescriptionHeader.Show()
            self.loreDescriptionBody.Show()
        else:
            self.loreDescriptionHeader.Hide()
            self.loreDescriptionBody.Hide()
        gameplayDescription = contentPiece.GetSiteGameplayDescription()
        if gameplayDescription:
            self.gameplayDescription.SetHint(gameplayDescription)
            self.gameplayDescription.Show()
        else:
            self.gameplayDescription.Hide()

    def GetEntryContentPieces(self):
        return self.contentPiece.GetSiteContentPieces()

    def _GetJob(self, instanceID):
        return get_homefront_operation_job(instanceID)
