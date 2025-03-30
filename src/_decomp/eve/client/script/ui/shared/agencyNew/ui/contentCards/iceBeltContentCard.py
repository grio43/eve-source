#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentCards\iceBeltContentCard.py
import evetypes
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.shared.agencyNew.ui.agencyUIConst import ICON_SIZE_RESOURCE
from eve.client.script.ui.shared.agencyNew.ui.contentCards.baseContentCard import BaseContentCard
from localization import GetByLabel

class IceBeltContentCard(BaseContentCard):
    default_name = 'IceBeltContentCard'

    def ApplyAttributes(self, attributes):
        super(IceBeltContentCard, self).ApplyAttributes(attributes)
        self.PopulateIceTypeContainer(self.contentPiece.iceTypesInSystem)

    def ConstructContent(self):
        self.ConstructTitleLabel()
        self.ConstructSubtitleLabel()
        self.ConstructBottomLabel()

    def ConstructIceTypeContainer(self):
        self.iceTypeContainer = Container(name='iceTypeContainer', parent=self.bottomCont, align=uiconst.TOTOP, height=ICON_SIZE_RESOURCE, padding=(2, -6, 0, 2))

    def PopulateIceTypeContainer(self, iceTypeIDs):
        if not iceTypeIDs:
            return
        self.ConstructIceTypeContainer()
        for iceTypeID in iceTypeIDs:
            iceTypeSprite = Sprite(name='%s_icon' % evetypes.GetName(iceTypeID).lower(), parent=self.iceTypeContainer, align=uiconst.TOLEFT, height=ICON_SIZE_RESOURCE, width=ICON_SIZE_RESOURCE, hint=evetypes.GetName(iceTypeID))
            sm.GetService('photo').GetIconByType(iceTypeSprite, iceTypeID, size=ICON_SIZE_RESOURCE)

    def UpdateCardText(self):
        self.titleLabel.SetText(self.contentPiece.GetSystemAndSecurityText())
        self.subtitleLabel.SetText(self.contentPiece.GetNumJumpsText())
        self.bottomLabel.SetText(GetByLabel('UI/Agency/NumberOfBeltsInSystem', amount=len(self.contentPiece.contentPieces)))
