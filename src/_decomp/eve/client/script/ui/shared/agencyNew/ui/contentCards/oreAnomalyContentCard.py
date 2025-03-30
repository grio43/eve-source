#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentCards\oreAnomalyContentCard.py
import evetypes
import eveicon
import log
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.gridcontainer import GridContainer
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui import eveColor
from eve.client.script.ui.shared.agencyNew.ui.agencyUIConst import ICON_SIZE_RESOURCE
from eve.client.script.ui.shared.agencyNew.ui.contentCards.baseContentCard import BaseContentCard
from eve.client.script.ui.shared.agencyNew.ui.tooltips.oreAvailabilityTooltip import ExtraOreTooltip
from localization import GetByLabel

class OreAnomalyContentCard(BaseContentCard):
    default_name = 'OreAnomalyContentCard'

    def ApplyAttributes(self, attributes):
        super(OreAnomalyContentCard, self).ApplyAttributes(attributes)
        self.PopulateOreTypeContainer(self.contentPiece.GetResourceTypeIDs())

    def ConstructContent(self):
        self.ConstructTitleLabel()
        self.ConstructSubtitleLabel()
        self.ConstructBottomLabel()

    def ConstructOreTypeContainer(self):
        self.oreTypeContainer = Container(name='oreTypeContainer', parent=self.bottomCont, align=uiconst.TOTOP, height=ICON_SIZE_RESOURCE, padding=(2, -6, 0, 2))

    def PopulateOreTypeContainer(self, typeIDs):
        if not typeIDs:
            return None
        self.ConstructOreTypeContainer()
        fst, rst = (None, None)
        if len(typeIDs) > 8:
            fst = typeIDs[:8]
            rst = typeIDs[8:]
            log.LogInfo('PopulateOreTypeContainer:: fst = ' + str(fst) + ', rst = ' + str(rst))
        else:
            fst = typeIDs
        for typeID in fst:
            sprite = Sprite(name='%s_icon' % evetypes.GetName(typeID).lower(), parent=self.oreTypeContainer, align=uiconst.TOLEFT, height=ICON_SIZE_RESOURCE, width=ICON_SIZE_RESOURCE, hint=evetypes.GetName(typeID))
            sm.GetService('photo').GetIconByType(sprite, typeID, size=ICON_SIZE_RESOURCE)

        if rst:
            sprite = Sprite(name='ore_icon_plus', parent=self.oreTypeContainer, align=uiconst.TOLEFT, height=ICON_SIZE_RESOURCE, width=ICON_SIZE_RESOURCE, texturePath=eveicon.add, color=eveColor.PLATINUM_GREY)
            sprite.LoadTooltipPanel = lambda tooltipPanel, *args: ExtraOreTooltip(tooltipPanel, rst)

    def UpdateCardText(self):
        self.titleLabel.SetText(self.contentPiece.GetSystemAndSecurityText())
        self.subtitleLabel.SetText(self.contentPiece.GetNumJumpsText())
        self.bottomLabel.SetText(GetByLabel('UI/Agency/NumberOfBeltsInSystem', amount=len(self.contentPiece.contentPieces)))
