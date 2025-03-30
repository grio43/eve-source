#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPageInfoConts\incursionSystemInfoContainer.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLabel import EveLabelMediumBold, EveLabelMedium
from eve.client.script.ui.shared.agencyNew.ui.contentPageInfoConts.baseContentPageInfoCont import BaseContentPageInfoContainer
from eve.client.script.ui.shared.agencyNew.ui.controls.agencyScrollContEntry import AgencyScrollContEntry
from localization import GetByLabel

class IncursionSystemInfoContainer(BaseContentPageInfoContainer):
    default_name = 'IncursionSystemInfoContainer'
    default_headerText = GetByLabel('UI/Agency/SitesInSystem')

    def ConstructLayout(self):
        self.ConstructSceneTypeInfoContainer()
        self.ConstructScroll()
        self.SetOpacity(1.0)

    def GetEntryContentPieces(self):
        return self.contentPiece.GetSiteContentPieces()

    def ConstructSceneTypeInfoContainer(self):
        iconSize = 32
        cont = ContainerAutoSize(parent=self, align=uiconst.TOTOP, height=iconSize, padBottom=10)
        iconCont = Container(name='iconCont', parent=cont, align=uiconst.CENTERLEFT, width=iconSize + 8, pos=(6,
         0,
         iconSize,
         iconSize))
        self.sceneTypeIcon = Sprite(parent=iconCont, align=uiconst.TOALL)
        textCont = ContainerAutoSize(parent=cont, align=uiconst.CENTERLEFT, width=250, left=iconSize + 14)
        self.sceneTypeTitle = EveLabelMediumBold(parent=textCont, align=uiconst.TOTOP)
        self.sceneTypeText = EveLabelMedium(parent=textCont, align=uiconst.TOTOP)

    def CheckShowEmptyState(self, contentPieces):
        return False

    def ConstructScrollEntry(self, contentPiece):
        entry = IncursionSiteScrollEntry(name=contentPiece.GetName(), parent=self.scrollCont, text=contentPiece.GetName(), contentPiece=contentPiece, texturePath=contentPiece.GetBracketIconTexturePath())
        self.scrollEntries.append(entry)
        entry.on_clicked.connect(self.OnScrollEntryClicked)
        return entry

    def _UpdateContentPiece(self, contentPiece):
        self.primaryActionButton.SetController(self.contentPiece)
        super(IncursionSystemInfoContainer, self)._UpdateContentPiece(contentPiece)
        self.sceneTypeIcon.texturePath = self.contentPiece.GetSceneTypeIcon()
        self.sceneTypeTitle.text = self.contentPiece.GetSceneTypeName()
        self.sceneTypeText.text = self.contentPiece.GetSceneTypeHint()

    def GetNoContentHint(self):
        return GetByLabel('UI/Incursion/HUD/SitePresenceUnknownHint')


class IncursionSiteScrollEntry(AgencyScrollContEntry):

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric1ColumnTemplate()
        tooltipPanel.AddLabelLarge(text=self.contentPiece.GetForcesRequiredLabel(), bold=True, wrapWidth=300)
        tooltipPanel.AddSpacer(height=20)
        tooltipPanel.AddLabelSmall(text=self.contentPiece.GetSiteDescription(), wrapWidth=300)

    def GetTooltipPointer(self):
        return uiconst.POINT_LEFT_2
