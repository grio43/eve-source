#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPageInfoConts\signatureInfoContainer.py
from carbonui import uiconst
from eve.client.script.ui import eveColor
from eve.client.script.ui.shared.agencyNew.ui.contentPageInfoConts.baseContentPageInfoCont import BaseContentPageInfoContainer
from eve.client.script.ui.shared.agencyNew.ui.controls.agencyScrollContEntry import AgencyScrollContEntry
from eve.client.script.ui.shared.agencyNew.ui.controls.warningContainer import WarningContainer
from localization import GetByLabel

class SignatureInfoContainer(BaseContentPageInfoContainer):
    default_name = 'SignatureInfoContainer'
    default_headerText = GetByLabel('UI/Agency/SignaturesInSystem')

    def ConstructLayout(self):
        super(SignatureInfoContainer, self).ConstructLayout()
        WarningContainer(parent=self, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/SignaturesNote'), padding=(0, 10, 0, 0), color=eveColor.WARNING_ORANGE)

    def GetEntryContentPieces(self):
        return self.contentPiece.GetSiteContentPieces()

    def _GetScrollEntryClass(self):
        return SignatureScrollEntry


class SignatureScrollEntry(AgencyScrollContEntry):

    def UpdateIcon(self):
        super(SignatureScrollEntry, self).UpdateIcon()
        self.icon.SetRGBA(*self.contentPiece.GetColor())
