#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentCards\planetaryProductionSystemContentCard.py
import telemetry
from carbonui import uiconst
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.shared.agencyNew.ui.contentCards.baseContentCard import BaseContentCard
from inventorycommon import const as invConst
from localization import GetByLabel

class PlanetaryProductionSystemContentCard(BaseContentCard):
    default_name = 'PlanetaryProductionSystemContentCard'

    @telemetry.ZONE_METHOD
    def ConstructContent(self):
        self.ConstructTitleLabel()
        self.ConstructSubtitleLabel()
        self.ConstructBottomLabel()
        self.ConstructColonyIndicatorSprite()
        self.ConstructScanRangeSprite()

    def ConstructScanRangeSprite(self):
        self.scanRangeSprite = Sprite(name='scanRangeSprite', parent=self.mainCont, align=uiconst.TOPRIGHT, width=32, height=32, state=uiconst.UI_NORMAL)

    def ConstructColonyIndicatorSprite(self):
        self.colonyIndicatorSprite = Sprite(name='colonyIndicatorSprite', parent=self.bottomCont, align=uiconst.CENTERRIGHT, state=uiconst.UI_NORMAL, texturePath='res:/UI/Texture/classes/agency/iconPlanetaryStructure.png', hint=GetByLabel('UI/Agency/PlanetaryProduction/systemHasColonies'), pos=(5, 0, 16, 16))

    @telemetry.ZONE_METHOD
    def Update(self):
        super(PlanetaryProductionSystemContentCard, self).Update()
        self.UpdateColonyIndicatorSprite()
        self.UpdateScanRangeSprite()

    def UpdateScanRangeSprite(self):
        self.scanRangeSprite.SetTexturePath(self._GetIsScannableTexturePath())
        self.scanRangeSprite.SetHint(self._GetIsScannableHint())

    def _GetIsScannableHint(self):
        if self.contentPiece.isSystemUnscannable:
            return GetByLabel('UI/Agency/PlanetaryProduction/systemUnscannable')
        if self.contentPiece.isSystemWithinScanRange:
            hintPath = 'UI/Agency/PlanetaryProduction/systemWithinScanRange'
        else:
            hintPath = 'UI/Agency/PlanetaryProduction/systemOutOfScanRange'
        return GetByLabel(hintPath, skillTypeID=invConst.typeRemoteSensing)

    def _GetIsScannableTexturePath(self):
        if self.contentPiece.isSystemWithinScanRange:
            return 'res:/UI/Texture/classes/Agency/iconScannable.png'
        else:
            return 'res:/UI/Texture/classes/Agency/iconNotScannable.png'

    def UpdateColonyIndicatorSprite(self):
        if self.contentPiece.IsSystemColonizedByMe():
            self.colonyIndicatorSprite.Show()
        else:
            self.colonyIndicatorSprite.Hide()

    def UpdateCardText(self):
        self.titleLabel.SetText(self.contentPiece.GetSystemAndSecurityText())
        self.subtitleLabel.SetText(self.contentPiece.GetNumJumpsText())
        self.bottomLabel.SetText(GetByLabel('UI/Agency/PlanetaryProduction/numPlanetsInSystem', numPlanets=len(self.contentPiece.planetContentPieces)))
