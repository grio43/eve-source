#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentCards\asteroidBeltContentCard.py
import sys
import evetypes
from carbonui import uiconst
from carbonui.primitives.sprite import Sprite
from carbonui.util.color import Color
from eve.client.script.ui.shared.agencyNew.ui.agencyUIConst import ICON_SIZE_RESOURCE
from eve.client.script.ui.shared.agencyNew.ui.contentCards.baseContentCard import BaseContentCard
from eve.common.script.util.eveFormat import FmtSystemSecStatus
from localization import GetByLabel
from carbonui.primitives.container import Container

class AsteroidBeltContentCard(BaseContentCard):
    default_name = 'AsteroidBeltContentCard'

    def ApplyAttributes(self, attributes):
        super(AsteroidBeltContentCard, self).ApplyAttributes(attributes)
        self.PopulateOreTypeContainer(self.contentPiece.GetResourceTypeIDs())

    def ConstructContent(self):
        self.ConstructTitleLabel()
        self.ConstructSubtitleLabel()
        self.ConstructBottomLabel()

    def ConstructOreTypeContainer(self):
        self.oreTypeContainer = Container(name='oreTypeContainer', parent=self.bottomCont, align=uiconst.TOTOP, height=ICON_SIZE_RESOURCE, padding=(2, -6, 0, 2))

    def PopulateOreTypeContainer(self, oreTypeIDList):
        if not oreTypeIDList:
            return
        self.ConstructOreTypeContainer()
        for oreTypeID in oreTypeIDList:
            oreTypeSprite = Sprite(name='%s_icon' % evetypes.GetName(oreTypeID).lower(), parent=self.oreTypeContainer, align=uiconst.TOLEFT, height=ICON_SIZE_RESOURCE, width=ICON_SIZE_RESOURCE)
            sm.GetService('photo').GetIconByType(oreTypeSprite, oreTypeID, size=ICON_SIZE_RESOURCE)

    def UpdateCardText(self):
        self.titleLabel.SetText(self.GetTitle())
        self.subtitleLabel.SetText(self.contentPiece.GetNumJumpsText())
        self.bottomLabel.SetText(GetByLabel('UI/Agency/NumberOfBeltsInSystem', amount=len(self.contentPiece.contentPieces)))

    def GetTitle(self):
        securityStatus, color = FmtSystemSecStatus(self.contentPiece.GetSystemSecurityStatus(), getColor=1)
        modifierIconText = self.contentPiece.GetSystemSecurityStatusModifierIconText()
        color = Color.RGBtoHex(*color)
        return '<color=%s>%s%s</color> %s' % (color,
         securityStatus,
         modifierIconText,
         self.contentPiece.GetName())
