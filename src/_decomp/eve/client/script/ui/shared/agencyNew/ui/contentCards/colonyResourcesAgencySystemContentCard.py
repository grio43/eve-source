#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentCards\colonyResourcesAgencySystemContentCard.py
from carbon.common.script.util.format import FmtAmt
from eve.client.script.ui.shared.agencyNew.ui.contentCards.baseContentCard import BaseContentCard
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.shared.agencyNew.ui import agencyUIConst
from eve.client.script.ui.eveColor import PLATINUM_GREY
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.frame import Frame
from carbonui import TextColor, uiconst
from inventorycommon.const import typeColonyReagentIce, typeColonyReagentLava
from localization import GetByLabel
from orbitalSkyhook.resourceRichness import GetSystemPowerRichnessTexturePath, GetSystemWorkforceRichnessTexturePath, GetSystemReagentRichnessTexturePathAndHint

class ColonyResourcesAgencySystemContentCard(BaseContentCard):

    def ApplyAttributes(self, attributes):
        super(ColonyResourcesAgencySystemContentCard, self).ApplyAttributes(attributes)

    def ConstructContent(self):
        self.ConstructTitleLabel()
        self.ConstructSubtitleLabel()
        self.ConstructBottomLabel()

    def ConstructIcon(self):
        self.leftCont.width = 8
        self.ConstructBackgroundTexture()

    def ConstructBottomCont(self):
        solarSystemValues = self.contentPiece.solarSystemValues
        self.bottomCont = ContainerAutoSize(name='bottomCont', parent=self, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, minHeight=20, padding=(4, 6, 6, 6))
        Frame(bgParent=self.bottomCont, texturePath='res:/UI/Texture/Shared/DarkStyle/panel1Corner_Solid.png', cornerSize=9, color=agencyUIConst.COLOR_BG)
        self.powerWorkforceContainer = Container(name='powerWorkforceContainer', parent=self.bottomCont, align=uiconst.TOTOP, height=20)
        self.powerOutputInfoContainer = Container(name='powerOutputInfoContainer', parent=self.powerWorkforceContainer, align=uiconst.TOLEFT, width=60)
        texturePath, hintPath = GetSystemPowerRichnessTexturePath(solarSystemValues.powerOutput)
        self.powerOutputInfoSprite = Sprite(parent=self.powerOutputInfoContainer, width=18, height=18, texturePath=texturePath, align=uiconst.CENTERLEFT, color=PLATINUM_GREY)
        self.powerOutputInfoSprite.hint = GetByLabel(hintPath)
        self.powerOutputInfoLabel = Label(parent=self.powerOutputInfoContainer, algin=uiconst.TOLEFT, padLeft=20, padTop=1, text=FmtAmt(solarSystemValues.powerOutput))
        self.workforceOutputInfoContainer = Container(name='workforceOutputInfoGridContainer', parent=self.powerWorkforceContainer, align=uiconst.TOLEFT, width=60)
        if solarSystemValues.workforceOutput:
            texturePath, hintPath = GetSystemWorkforceRichnessTexturePath(solarSystemValues.workforceOutput)
            workforceOutputInfoSprite = Sprite(parent=self.workforceOutputInfoContainer, width=18, height=18, texturePath=texturePath, align=uiconst.CENTERLEFT, color=PLATINUM_GREY)
            workforceOutputInfoSprite.hint = GetByLabel(hintPath)
            workforceOutputInfoLabel = Label(parent=self.workforceOutputInfoContainer, algin=uiconst.TOLEFT, padLeft=22, padTop=1, text=FmtAmt(solarSystemValues.workforceOutput))
        self.reagentsFirstContainer = Container(name='reagentsFirstContainer', parent=self.powerWorkforceContainer, align=uiconst.TOLEFT, width=25, padLeft=8)
        self.reagentsFirstSprite = Sprite(parent=self.reagentsFirstContainer, width=18, height=18, align=uiconst.CENTERLEFT, color=PLATINUM_GREY)
        self.reagentsSecondContainer = Container(name='reagentsSecondContainer', parent=self.powerWorkforceContainer, align=uiconst.TOLEFT, width=25)
        self.reagentsSecondSprite = Sprite(parent=self.reagentsSecondContainer, width=18, height=18, align=uiconst.CENTERLEFT, color=PLATINUM_GREY)
        reagentsTypes = solarSystemValues.reagentsTypes
        hasSuperionicIce = reagentsTypes.hasSuperionicIce
        hasMagmaticGas = reagentsTypes.hasMagmaticGas
        spriteLists = [self.reagentsFirstSprite, self.reagentsSecondSprite]
        if hasSuperionicIce:
            sprite = spriteLists.pop(0)
            self._SetTexturePathAndHint(sprite, typeColonyReagentIce, reagentsTypes.superionicIceAmount)
        if hasMagmaticGas:
            sprite = spriteLists.pop(0)
            self._SetTexturePathAndHint(sprite, typeColonyReagentLava, reagentsTypes.magmaticGasAmount)

    def _SetTexturePathAndHint(self, sprite, reagentTypeID, amount):
        texturePath, hintPath = GetSystemReagentRichnessTexturePathAndHint(amount, reagentTypeID)
        sprite.SetTexturePath(texturePath)
        sprite.hint = GetByLabel(hintPath)

    def ConstructTitleLabel(self):
        self.titleLabel = EveLabelMedium(name='cardTitleLabel', parent=self.mainCont, align=uiconst.TOTOP, maxLines=1, color=TextColor.NORMAL)
