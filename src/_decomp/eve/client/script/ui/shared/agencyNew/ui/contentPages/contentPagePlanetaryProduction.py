#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPages\contentPagePlanetaryProduction.py
import evetypes
import inventorycommon.const as invConst
from carbonui import uiconst
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from eve.client.script.ui.shared.agencyNew.ui.common.descriptionIcon import DescriptionIconLabel
from eve.client.script.ui.shared.agencyNew.ui.contentPageInfoConts.planetaryProductionSystemInfoContainer import PlanetaryProductionSystemInfoContainer
from eve.client.script.ui.shared.agencyNew.ui.contentPages.singleColumnContentPage import SingleColumnContentPage
from eve.client.script.ui.shared.agencyNew.ui.tooltips.planetaryResourcesTooltip import PlanetaryResourcesTooltip
from eve.client.script.ui.control.simpleTextTooltip import SimpleTextTooltip
from localization import GetByLabel

class ContentPagePlanetaryProduction(SingleColumnContentPage):
    default_name = 'ContentPagePlanetaryProduction'
    default_height = 505

    def ConstructInfoContainer(self):
        self.infoContainer = PlanetaryProductionSystemInfoContainer(parent=self)

    def ConstructTooltips(self):
        DescriptionIconLabel(parent=self.informationContainer, align=uiconst.TOTOP, text=evetypes.GetName(invConst.typeRemoteSensing), tooltipPanelClassInfo=SimpleTextTooltip(text=GetByLabel('UI/Agency/Tooltips/ResourceHarvesting/PlanetaryProduction/RemoteSensing')), top=5)
        DescriptionIconLabel(parent=self.informationContainer, align=uiconst.TOTOP, text=GetByLabel('UI/PI/Common/PlanetaryResources'), tooltipPanelClassInfo=PlanetaryResourcesTooltip(text=GetByLabel('UI/Agency/Tooltips/ResourceHarvesting/PlanetaryProduction/RemoteSensing')), top=5)

    def _ConstructBaseLayout(self):
        super(ContentPagePlanetaryProduction, self)._ConstructBaseLayout()
        self.ConstructOpenPlanetsButton()

    def ConstructOpenPlanetsButton(self):
        Button(name='openPlanetsButton', parent=Container(parent=self.informationContainer, align=uiconst.TOTOP, height=25, idx=0), align=uiconst.CENTERLEFT, texturePath='res:/UI/Texture/WindowIcons/planets.png', label=GetByLabel('UI/InfoWindow/TabNames/PlanetaryProduction'), func=sm.GetService('cmd').OpenPlanets)
