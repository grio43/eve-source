#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPageInfoConts\resourceHarvestingInfoCont.py
from carbonui import uiconst
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.layoutGrid import LayoutGrid
from eve.client.script.ui.shared.agencyNew.ui.contentPageInfoConts.jobInfoContainer import JobContentPageInfoContainer
from eve.client.script.ui.shared.agencyNew.ui.controls.agencyScrollContEntry import AgencyScrollContEntry
from carbonui.control.section import SubSection
from eve.client.script.ui.shared.agencyNew.ui.controls.enemyInfoCont import EnemyInfoCont
from eve.client.script.ui.shared.agencyNew.ui.typeEntry import TypeEntry
from localization import GetByLabel

class ResourceHarvestingInfoContainer(JobContentPageInfoContainer):
    default_name = 'ResourceHarvestingInfoContainer'
    default_scroll_container_height = 100
    default_headerText = GetByLabel('UI/Agency/BeltsInSystem')

    def ConstructLayout(self):
        super(ResourceHarvestingInfoContainer, self).ConstructLayout()
        self.enemyInfoCont = EnemyInfoCont(name='enemyInfoContainer', parent=self, align=uiconst.TOBOTTOM, padTop=10)
        self.ConstructTypesInSystemContainer()

    def GetEntryContentPieces(self):
        return self.contentPiece.contentPieces

    def ConstructTypesInSystemContainer(self):
        typesInSystemContainer = SubSection(name='typesInSystemContainer', parent=self, align=uiconst.TOALL, headerText=self.GetTypesInSystemLabel(), padTop=10)
        self.typesInSiteScroll = ScrollContainer(name='typesInSystemScroll', parent=typesInSystemContainer, align=uiconst.TOALL, padding=(0, 5, 0, 5))
        self.typesInSiteLayoutGrid = LayoutGrid(name='typesInSystemLayoutGrid', parent=self.typesInSiteScroll, align=uiconst.TOTOP, cellSpacing=(60, 10), columns=2)

    def GetTypesInSystemLabel(self):
        return GetByLabel('UI/Agency/OreTypesInBelt')

    def UpdateTypesInSiteScroll(self):
        self.typesInSiteLayoutGrid.Flush()
        self.typesInSiteScroll.ScrollToVertical(0)
        typeIDs = self.clickedEntry.contentPiece.GetResourceTypeIDs()
        if typeIDs:
            self.ConstructTypeEntries(typeIDs)
            self.typesInSiteScroll.HideNoContentHint()
        else:
            self.typesInSiteScroll.ShowNoContentHint(GetByLabel('UI/Common/Unknown'))
        self.AnimateEnterAllTypesInSite()

    def ConstructTypeEntries(self, typeIDs):
        for typeID in typeIDs:
            TypeEntry(parent=self.typesInSiteLayoutGrid, typeID=typeID, opacity=0)

    def AnimateEnterAllTypesInSite(self):
        for i, cell in enumerate(self.typesInSiteLayoutGrid.children):
            entry = cell.GetCellObject()
            entry.AnimEnter(i)

    def OnScrollEntryClicked(self, clickedEntry):
        super(ResourceHarvestingInfoContainer, self).OnScrollEntryClicked(clickedEntry)
        self.UpdateTypesInSiteScroll()
        self.enemyInfoCont.Update(ownerID=self.contentPiece.GetEnemyOwnerID(), ownerTypeID=self.contentPiece.GetEnemyOwnerTypeID())

    def _GetScrollEntryClass(self):
        return AgencyScrollContEntryWithTooltip


class AgencyScrollContEntryWithTooltip(AgencyScrollContEntry):

    def LoadTooltipPanel(self, tooltipPanel, *args):
        if self.label.textwidth > self.displayWidth:
            tooltipPanel.AddLabelMedium(text=self.contentPiece.GetName())
