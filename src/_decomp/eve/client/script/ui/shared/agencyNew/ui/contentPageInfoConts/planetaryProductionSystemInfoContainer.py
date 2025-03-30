#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPageInfoConts\planetaryProductionSystemInfoContainer.py
import evetypes
from carbonui.control.button import Button
from carbonui.primitives.flowcontainer import FlowContainer
from eve.client.script.ui import eveThemeColor
from eve.common.lib import appConst
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import AxisAlignment, uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.gridcontainer import GridContainer
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from dogma import const as dogmaConst
from eve.client.script.ui.control.statefulButton import StatefulButton
from eve.client.script.ui.control.eveLabel import EveLabelLarge
from eve.client.script.ui.control.gauge import Gauge
from eve.client.script.ui.shared.agencyNew import agencyFilters, agencyConst
from eve.client.script.ui.shared.agencyNew.ui.contentPageInfoConts.baseContentPageInfoCont import BaseContentPageInfoContainer
from carbonui.control.section import SubSection
from eve.client.script.ui.shared.agencyNew.ui.controls.planetScrollEntry import PlanetScrollEntry
from eve.client.script.ui.shared.planet import planetCommon
from fsdBuiltData.common.planet import get_resource_type_ids_for_planet_type_id
from inventorycommon import typeHelpers
from localization import GetByLabel

class PlanetaryProductionSystemInfoContainer(BaseContentPageInfoContainer):
    default_name = 'PlanetaryProductionSystemInfoContainer'
    default_scroll_container_height = 200
    default_headerText = GetByLabel('UI/Agency/PlanetaryProduction/planetsInSystem')

    def ApplyAttributes(self, attributes):
        super(PlanetaryProductionSystemInfoContainer, self).ApplyAttributes(attributes)
        agencyFilters.onFilterChanged.connect(self.OnAgencyFilterChanged)

    def OnAgencyFilterChanged(self, contentGroupID, filterType, value):
        if filterType == agencyConst.FILTERTYPE_PLANETTYPES:
            if all((filter is False for filter in value.values())):
                self.SetEmpty()

    def ConstructLayout(self):
        self.ConstructResourcesInPlanetContainer()
        self.ConstructScroll()
        self.scrollParent.SetAlign(uiconst.TOALL)
        self.scrollParent.height = 0

    def ConstructButtonContainer(self):
        self.buttonRowCont = FlowContainer(name='buttonRowContainer', parent=self, align=uiconst.TOBOTTOM, padTop=8, contentAlignment=AxisAlignment.END, contentSpacing=(4, 4), idx=0)
        self.primaryActionButton = StatefulButton(parent=self.buttonRowCont, align=uiconst.NOALIGN, iconAlign=uiconst.TORIGHT)
        self.buyCommandCenterButton = Button(name='buyCommandCenterButton', parent=self.buttonRowCont, align=uiconst.NOALIGN, iconAlign=uiconst.TORIGHT, label=GetByLabel('UI/Agency/PlanetaryProduction/buyCommandCenter'), texturePath='res:/ui/Texture/WindowIcons/market.png', padLeft=4)

    def GetEntryContentPieces(self):
        return self.contentPiece.planetContentPieces

    def ConstructScrollEntry(self, contentPiece):
        entry = PlanetScrollEntry(parent=self.scrollCont, contentPiece=contentPiece)
        self.scrollEntries.append(entry)
        entry.on_clicked.connect(self.OnScrollEntryClicked)
        return entry

    def ConstructResourcesInPlanetContainer(self):
        self.resourcesSection = SubSection(parent=self, align=uiconst.TOBOTTOM, height=150, padTop=10)
        self.resourcesInPlanetContainer = GridContainer(name='resourcesInPlanetContainer', parent=self.resourcesSection, columns=2, lines=3)

    def UpdateResourcesInPlanet(self, planetContentPiece):
        if planetContentPiece.isBlacklisted:
            return
        self.resourcesInPlanetContainer.Flush()
        if self.contentPiece.isSystemWithinScanRange:
            resourceInfo = planetContentPiece.GetPlanetResourceInfo()
        else:
            resourceInfo = [ (resourceTypeID, 0) for resourceTypeID in get_resource_type_ids_for_planet_type_id(planetContentPiece.typeID, []) ]
        for resourceTypeID, resourceDensity in resourceInfo:
            PlanetaryResourceContainer(parent=self.resourcesInPlanetContainer, resourceTypeID=resourceTypeID, resourceDensity=resourceDensity, padding=(4, 4, 10, 6))

    def UpdateBuyCommandCenterButton(self, planetContentPiece):
        requiredCommandCenterTypeID = None
        godmaSvc = sm.GetService('godma')
        for commandCenterTypeID in evetypes.GetTypeIDsByGroup(appConst.groupCommandPins):
            if not evetypes.IsPublished(commandCenterTypeID):
                continue
            planetRestriction = godmaSvc.GetTypeAttribute(commandCenterTypeID, dogmaConst.attributePlanetRestriction)
            if planetRestriction == planetContentPiece.typeID:
                requiredCommandCenterTypeID = commandCenterTypeID

        self.buyCommandCenterButton.SetFunc(lambda x: sm.GetService('marketutils').ShowMarketDetails(requiredCommandCenterTypeID))

    def UpdateResourcesInPlanetLabel(self, planetContentPiece):
        text = GetByLabel('UI/Agency/PlanetaryProduction/resourcesInPlanet', planetName=planetContentPiece.GetName())
        self.resourcesSection.SetText(text)

    def _UpdateContentPiece(self, contentPiece):
        self.systemInfoContainer.UpdateContentPiece(contentPiece)
        self.scrollCont.Flush()
        if not contentPiece.planetContentPieces:
            contentPiece.planetContentPiecesReadySignal.connect(self.UpdateScroll)
        else:
            self.UpdateScroll()

    def SetEmpty(self):
        self.mainCont.SetOpacity(0)

    def Update(self, planetContentPiece):
        self.mainCont.SetOpacity(1)
        self.UpdateResourcesInPlanetLabel(planetContentPiece)
        self.UpdateBuyCommandCenterButton(planetContentPiece)
        self.UpdateResourcesInPlanet(planetContentPiece)

    def OnScrollEntryClicked(self, clickedEntry):
        super(PlanetaryProductionSystemInfoContainer, self).OnScrollEntryClicked(clickedEntry)
        self.Update(clickedEntry.contentPiece)


class PlanetaryResourceContainer(Container):
    default_name = 'PlanetaryResourceContainer'
    default_state = uiconst.UI_NORMAL
    HOVER_FILL_COLOR = (1.0, 1.0, 1.0, 0.15)

    def ApplyAttributes(self, attributes):
        super(PlanetaryResourceContainer, self).ApplyAttributes(attributes)
        self.resourceTypeID = attributes.resourceTypeID
        self.resourceDensity = attributes.resourceDensity
        self.ConstructLayout()
        self.Update()

    def ConstructLayout(self):
        self._ConstructIcon()
        self._ConstructLabel()
        self._ConstructGauge()

    def _ConstructIcon(self):
        iconContainer = ContainerAutoSize(name='iconContainer', parent=self, align=uiconst.TOLEFT, padRight=4)
        self.resourceIcon = Sprite(name='resourceIcon', parent=iconContainer, align=uiconst.CENTER, width=32, height=32, state=uiconst.UI_DISABLED)

    def _ConstructLabel(self):
        cont = ContainerAutoSize(name='resourceNameLabelCont', parent=self, align=uiconst.TOTOP)
        self.resourceNameLabel = EveLabelLarge(name='resourceNameLabel', parent=cont, align=uiconst.TOPLEFT, autoFadeSides=10)

    def _ConstructGauge(self):
        self.resourceDensityGauge = Gauge(name='resourceDensityGauge', parent=self, align=uiconst.TOTOP, gaugeHeight=10, state=uiconst.UI_DISABLED, color=eveThemeColor.THEME_ACCENT)
        self.resourceDensityGauge.ShowMarkers([ i * 0.1 for i in xrange(1, 10) ], color=(0.0, 0.0, 0.0, 0.2))

    def Update(self):
        sm.GetService('photo').GetIconByType(self.resourceIcon, self.resourceTypeID)
        self.resourceNameLabel.SetText(evetypes.GetName(self.resourceTypeID))
        self.resourceDensityGauge.SetValueInstantly(max(0.0, min(1.0, self.resourceDensity)))

    def GetMenu(self):
        return sm.GetService('menu').GetMenuFromItemIDTypeID(None, self.resourceTypeID, includeMarketDetails=True)

    def OnMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_ENTRY_HOVER)
        animations.FadeTo(self.resourceNameLabel, self.resourceNameLabel.opacity, 1.5, duration=0.2)

    def OnMouseExit(self, *args):
        animations.FadeTo(self.resourceNameLabel, self.resourceNameLabel.opacity, 1.0, duration=0.2)

    def OnClick(self, *args):
        sm.GetService('info').ShowInfo(self.resourceTypeID)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        if not self.resourceTypeID:
            return
        tooltipPanel.LoadGeneric2ColumnTemplate()
        tooltipPanel.AddLabelMedium(colSpan=2, text=planetCommon.GetProductNameAndTier(self.resourceTypeID))
        text = GetByLabel('UI/PI/Common/ResourceDensity', density=int(100 * self.resourceDensity))
        tooltipPanel.AddLabelMedium(colSpan=2, text=text)
        tooltipPanel.AddLabelMedium(colSpan=2, cellPadding=(0, 10, 0, 2), text=GetByLabel('UI/InfoWindow/TabNames/RequiredFor'))
        for typeID in planetCommon.GetRequiredForItems(self.resourceTypeID):
            label = planetCommon.GetProductNameAndTier(typeID)
            icon = typeHelpers.GetIconFile(typeID)
            tooltipPanel.AddIconLabel(icon=icon, label=label, iconSize=28)

    def GetTooltipPointer(self):
        return uiconst.POINT_RIGHT_2
