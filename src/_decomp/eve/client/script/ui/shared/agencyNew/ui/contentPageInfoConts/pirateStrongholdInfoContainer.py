#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPageInfoConts\pirateStrongholdInfoContainer.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveIcon import OwnerIcon
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.shared.agencyNew.ui.contentPageInfoConts.baseContentPageInfoCont import BaseContentPageInfoContainer
from eve.client.script.ui.shared.agencyNew.ui.controls.warningContainer import WarningContainer
from localization import GetByLabel

class PirateStrongholdInfoContainer(BaseContentPageInfoContainer):
    default_headerText = GetByLabel('UI/Agency/PirateStrongholdsInSystem')

    def ConstructLayout(self):
        self.ConstructFactionIconAndText()
        self.ConstructScroll()
        WarningContainer(parent=self, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/PirateStrongholdNote'), color=eveColor.WARNING_ORANGE, padTop=10)

    def ConstructFactionIconAndText(self):
        iconSize = 60
        cont = ContainerAutoSize(parent=self, align=uiconst.TOTOP, height=iconSize, alignMode=uiconst.TOTOP, padBottom=10)
        iconCont = Container(name='iconCont', parent=cont, align=uiconst.TOLEFT, width=iconSize)
        self.factionIcon = OwnerIcon(parent=iconCont, align=uiconst.TOPLEFT, pos=(0,
         0,
         iconSize,
         iconSize))
        self.factionText = Label(parent=cont, align=uiconst.TOTOP, padLeft=4)

    def GetEntryContentPieces(self):
        return self.contentPiece.GetContentPieces()

    def _UpdateContentPiece(self, contentPiece):
        super(PirateStrongholdInfoContainer, self)._UpdateContentPiece(contentPiece)
        factionID = self.contentPiece.GetEnemyFactionID()
        self.factionIcon.SetOwnerID(factionID)
        text = GetByLabel('UI/Agency/PirateStrongholdFactionText', factionID=factionID)
        self.factionText.SetText(text)
