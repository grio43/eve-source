#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPages\contentPageIncursion.py
from carbon.common.script.util.format import FmtAmt
from carbonui import uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveIcon import OwnerIcon
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveCaptionMedium
from eve.client.script.ui.shared.agencyNew.ui.common.descriptionIcon import DescriptionIconLabel
from eve.client.script.ui.shared.agencyNew.ui.contentCards.incursionSystemContentCard import IncursionSystemContentCard
from eve.client.script.ui.shared.agencyNew.ui.contentPageInfoConts.incursionSystemInfoContainer import IncursionSystemInfoContainer
from eve.client.script.ui.shared.agencyNew.ui.contentPages.singleColumnContentPage import SingleColumnContentPage
from carbonui.control.section import Section, SubSectionAutoSize
from eve.client.script.ui.control.simpleTextTooltip import SimpleTextTooltip
from eve.client.script.ui.shared.incursions.taleSystemEffectCont import TaleSystemEffectCont
from eve.client.script.ui.shared.infoPanels.infoPanelIncursions import SystemInfluenceBar
from localization import GetByLabel

class ContentPageIncursion(SingleColumnContentPage):
    default_name = 'ContentPageIncursion'

    def _InitVariables(self):
        super(ContentPageIncursion, self)._InitVariables()
        self.contentPiece = self.contentGroup.GetIncursionContentPiece()

    def ConstructInfoContainer(self):
        self.infoContainer = IncursionSystemInfoContainer(parent=self, padding=(10, 0, 10, 0), contentPiece=self.contentPiece)

    def ConstructFilterContainer(self):
        pass

    def ConstructTooltips(self):
        DescriptionIconLabel(parent=self.informationContainer, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/ConstellationInfluence'), tooltipPanelClassInfo=SimpleTextTooltip(text=GetByLabel('UI/Agency/Tooltips/Encounters/Incursions/ConstellationInfluence')))
        DescriptionIconLabel(parent=self.informationContainer, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/AccumulatedPayout'), tooltipPanelClassInfo=SimpleTextTooltip(text=GetByLabel('UI/Agency/Tooltips/Encounters/Incursions/AccumulatedPayout')), top=5)

    def GetContentPieces(self):
        return self.contentPiece.GetSystemContentPieces()

    def GetContentCardClass(self):
        return IncursionSystemContentCard

    def ConstructLeftCont(self):
        self.leftCont = Section(name='leftCont', parent=self, align=uiconst.TOLEFT, width=300, padRight=10, headerText=GetByLabel('UI/Agency/ConstellationInfo'))
        self.ConstructIconAndStateHint()
        self.ConstructConstellationEffectIcons()
        self.ConstructInfluenceBar()
        self.ConstructLPPoolLabel()

    def ConstructIconAndStateHint(self):
        iconSize = 64
        cont = Container(parent=self.leftCont, align=uiconst.TOTOP, height=iconSize, alignMode=uiconst.TOTOP)
        OwnerIcon(parent=cont, align=uiconst.CENTERLEFT, pos=(0,
         0,
         iconSize,
         iconSize), ownerID=self.contentPiece.GetEnemyOwnerID())
        EveLabelMedium(parent=cont, align=uiconst.TOTOP, text=self.contentPiece.GetStateHint(), padLeft=iconSize + 6)

    def ConstructInfluenceBar(self):
        subSection = SubSectionAutoSize(parent=self.leftCont, align=uiconst.TOTOP, headerText=GetByLabel('UI/Incursion/HUD/PirateInfluence'), padTop=16)
        statusBar = SystemInfluenceBar(parent=subSection, height=10, align=uiconst.TOTOP, padRight=4)
        statusBar.SetInfluence(self.contentPiece.GetInfluence(), None, animate=False)

    def ConstructLPPoolLabel(self):
        subSection = SubSectionAutoSize(parent=self.leftCont, align=uiconst.TOTOP, headerText=GetByLabel('UI/Incursion/HUD/CurrentAccumulatedPayout'), padTop=16)
        EveCaptionMedium(parent=subSection, align=uiconst.TOTOP, text=GetByLabel('UI/LPStore/AmountLP', lpAmount=str(FmtAmt(self.contentPiece.GetLPPayoutPool()))))

    def ConstructConstellationEffectIcons(self):
        subSection = SubSectionAutoSize(parent=self.leftCont, align=uiconst.TOTOP, headerText=GetByLabel('UI/Incursion/HUD/ConstellationWidePenalties'), padTop=16)
        TaleSystemEffectCont(parent=subSection, align=uiconst.TOTOP, effects=self.contentPiece.GetConstellationEffects(), influence=self.contentPiece.GetInfluence())
