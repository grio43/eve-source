#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPageInfoConts\colonyResourcesAgencyInfoContainer.py
import carbonui
import datetimeutils
import gametime
import log
import eveicon
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.gridcontainer import GridContainer
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from carbonui.control.section import SubSection
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import Label, EveLabelMedium
from eve.client.script.ui.shared.agencyNew.ui.controls.colonyResourcesAgencyPlanetScrollEntry import ColonyResourcesAgencyPlanetScrollEntry
from eve.client.script.ui.shared.agencyNew.ui.contentPageInfoConts.baseContentPageInfoCont import BaseContentPageInfoContainer
from eve.client.script.ui.shared.agencyNew.ui.contentPageInfoConts.colonyResourcesAgencySystemInfoContainer import ColonyResourcesAgencySystemInfoContainer
from inventorycommon.const import typeColonyReagentLava, typeColonyReagentIce
from localization import GetByLabel
from localization.formatters import FormatTimeIntervalShortWritten
from orbitalSkyhook.resourceRichness import GetPlanetWorkforceRichnessTexturePath, GetPlanetPowerRichnessTexturePath, GetPlanetReagentRichnessTexturePathAndHint

class ColonyResourceAgencyInfoContainer(BaseContentPageInfoContainer):
    default_name = 'ColonyResourceAgencyInfoContainer'
    default_scroll_container_height = 230
    default_headerText = GetByLabel('UI/Agency/PlanetaryProduction/planetsInSystem')

    def ApplyAttributes(self, attributes):
        super(ColonyResourceAgencyInfoContainer, self).ApplyAttributes(attributes)

    def ConstructLayout(self):
        self.ConstructCelestialDetailsContainer()
        super(ColonyResourceAgencyInfoContainer, self).ConstructLayout()

    def ConstructSystemInfoContainer(self):
        self.systemInfoContainer = ColonyResourcesAgencySystemInfoContainer(name='systemInfoContainer', parent=self, align=uiconst.TOTOP, height=48, padBottom=10)
        self.systemInfoContainer.Hide()

    def ConstructScrollEntry(self, contentPiece):
        entry = ColonyResourcesAgencyPlanetScrollEntry(parent=self.scrollCont, contentPiece=contentPiece)
        self.scrollEntries.append(entry)
        entry.on_clicked.connect(self.OnScrollEntryClicked)
        return entry

    def ConstructCelestialDetailsContainer(self):
        self.celestialDetailsSection = SubSection(name='celestialDetailsSection', parent=self, align=uiconst.TOBOTTOM, height=90, padding=(0, 0, 0, 0))
        self.celestialDetailsSection.SetText(GetByLabel('UI/Agency/ColonyResourcesAgency/CelestialDetails'))
        self.resourcesInPlanetContainer = Container(name='resourcesInPlanetContainer', parent=self.celestialDetailsSection, padding=(4, -4.5, 4, 4))
        self.resourcesStaticTitle = EveLabelMedium(parent=self.resourcesInPlanetContainer, text=GetByLabel('UI/Agency/ColonyResourcesAgency/Resources'), align=uiconst.TOTOP)
        self.resourcesInPlanetInnerContainer = GridContainer(parent=self.resourcesInPlanetContainer, align=carbonui.Align.TOALL, alignMode=carbonui.Align.TOTOP, pickState=carbonui.PickState.CHILDREN, contentSpacing=(1, 1), columns=2)

    def ConstructResourcesInfo(self, label, icon, value, tooltipText):
        resourcesInfo = Container(name='celestialDetailsInfo' + label, parent=self.resourcesInPlanetInnerContainer, height=40, align=uiconst.TOTOP)
        resourcesIcon = Sprite(parent=resourcesInfo, align=uiconst.CENTERLEFT, width=25, height=25, texturePath=icon, color=eveColor.PLATINUM_GREY)
        resourcesIcon.hint = tooltipText
        resourcesTextContainer = Container(parent=resourcesInfo, align=uiconst.TOTOP, height=35, padTop=4, padLeft=30)
        resourcesTitle = Label(parent=resourcesTextContainer, height=18, text=label, align=uiconst.TOTOP, color=eveColor.GUNMETAL_GREY)
        resourcesValue = Label(parent=resourcesTextContainer, height=18, text=value, align=uiconst.TOTOP)

    def GetEntryContentPieces(self):
        return self.contentPiece.GetPlanetContentPieces()

    def GetSolarSystemValues(self):
        return self.contentPiece.solarSystemValues

    def _UpdateContentPiece(self, contentPiece):
        self.systemInfoContainer.UpdateContentPiece(contentPiece)
        self.scrollCont.Flush()
        self.UpdateScroll()

    def UpdateCelestialDetails(self, planetContentPiece):
        self.resourcesInPlanetInnerContainer.Flush()
        values = planetContentPiece.planetColonyResourcesValues
        workforceLabel = GetByLabel('UI/Agency/ColonyResourcesAgency/Workforce')
        powerLabel = GetByLabel('UI/Agency/ColonyResourcesAgency/Power')
        magmaticGasLabel = GetByLabel('UI/Agency/ColonyResourcesAgency/MagmaticGas')
        superionicIceLabel = GetByLabel('UI/Agency/ColonyResourcesAgency/SuperionicIce')
        if values.powerOutput:
            texturePath, hint = GetPlanetPowerRichnessTexturePath(values.powerOutput)
            self.ConstructResourcesInfo(powerLabel, texturePath, values.powerOutput, GetByLabel(hint))
        if values.workforceOutput:
            texturePath, hint = GetPlanetWorkforceRichnessTexturePath(values.workforceOutput)
            self.ConstructResourcesInfo(workforceLabel, texturePath, values.workforceOutput, GetByLabel(hint))
        if values.reagentsTypes:
            if values.reagentsTypes.superionicIceAmount:
                texturePath, hint = GetPlanetReagentRichnessTexturePathAndHint(values.reagentsTypes.superionicIceAmount, typeColonyReagentIce)
                self.ConstructResourcesInfo(superionicIceLabel, texturePath, str(values.reagentsTypes.superionicIceAmount) + '/hour', GetByLabel(hint))
            if values.reagentsTypes.magmaticGasAmount:
                texturePath, hint = GetPlanetReagentRichnessTexturePathAndHint(values.reagentsTypes.magmaticGasAmount, typeColonyReagentLava)
                self.ConstructResourcesInfo(magmaticGasLabel, texturePath, str(values.reagentsTypes.magmaticGasAmount) + '/hour', GetByLabel(hint))
            if planetContentPiece.hasVulnerableSkyhook and planetContentPiece.expiry is not None:
                self.ConstructTheftInfo(planetContentPiece.expiry)

    def OnScrollEntryClicked(self, clickedEntry):
        super(ColonyResourceAgencyInfoContainer, self).OnScrollEntryClicked(clickedEntry)
        self.UpdateCelestialDetails(clickedEntry.contentPiece)

    def ConstructTheftInfo(self, expiry):
        theftInfo = Container(name='celestialDetailsInfoSkyhookTheft', parent=self.resourcesInPlanetInnerContainer, height=40, align=uiconst.TOTOP)
        theftIcon = Sprite(parent=theftInfo, align=uiconst.CENTERLEFT, width=25, height=25, texturePath=eveicon.reagents_skyhook, color=eveColor.PLATINUM_GREY)
        theftTextContainer = Container(parent=theftInfo, align=uiconst.TOTOP, height=35, padTop=4, padLeft=30)
        theftTitle = Label(parent=theftTextContainer, height=18, text=GetByLabel('UI/Agency/ColonyResourcesAgency/SkyhookTheftVulnerability'), align=uiconst.TOTOP, color=eveColor.GUNMETAL_GREY)
        countdown = FormatTimeIntervalShortWritten(datetimeutils.datetime_to_filetime(expiry) - gametime.GetWallclockTime(), 'day', 'minute')
        theftValue = Label(parent=theftTextContainer, height=18, text=countdown, align=uiconst.TOTOP)
