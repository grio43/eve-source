#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPages\contentPageAbyssalFilaments.py
import random
from abyss.client.constants import WEATHER_NAMES_BY_ID, WEATHER_TEXTURE_PATHS_BY_ID, NAME_LABEL_PATH_BY_TIER, DIFFICULTY_LABEL_PATH_BY_TIER, TIER_TEXTURE_PATH_BY_TIER, KEY_TYPE_BY_TIER_AND_WEATHER, WEATHER_HINTS_BY_ID
from abyss.common.constants import DIFFICULTY_TIERS, WEATHER_TYPE_IDS
from carbonui import Density, TextColor, uiconst
from carbonui.control.button import Button
from carbonui.control.combo import Combo
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from carbonui.control.scrollContainer import ScrollContainer
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelLarge
from eve.client.script.ui.shared.agencyNew.contentGroups.contentGroupConst import contentGroupSignatures
from eve.client.script.ui.shared.agencyNew.ui import agencyUIConst
from eve.client.script.ui.shared.agencyNew.ui.common.descriptionIcon import DescriptionIconLabel
from eve.client.script.ui.shared.agencyNew.ui.contentPages.baseContentPage import BaseContentPage
from carbonui.control.section import SectionAutoSize
from eve.client.script.ui.shared.agencyNew.ui.tooltips.abyssalDeadspaceRewardsTooltip import AbyssalDeadspaceRewardsTooltip
from localization import GetByLabel

class ContentPageAbyssalFilaments(BaseContentPage):
    default_name = 'ContentPageAbyssalFilaments'

    def ApplyAttributes(self, attributes):
        self.sortedWeatherNamesAndTypes = sorted({(weatherType, GetByLabel(namePath)) for weatherType, namePath in WEATHER_NAMES_BY_ID.iteritems()}, key=lambda x: x[1])
        super(ContentPageAbyssalFilaments, self).ApplyAttributes(attributes)

    def ConstructLayout(self):
        self._ConstructScrollContainer()
        self.ConstructLeftContainer()
        self.ConstructRightContainer()

    def ConstructRightContainer(self):
        self.rightContainer = Container(name='rightContainer', parent=self, align=uiconst.TOLEFT, width=agencyUIConst.CONTENT_PAGE_WIDTH / 1.65, padLeft=10)
        self.ConstructFilamentContainer()
        self.ConstructInfoContainer()

    def ConstructInfoContainer(self):
        infoContainer = SectionAutoSize(name='infoContainer', parent=self.leftContainer, align=uiconst.TOTOP, top=6, headerText=GetByLabel('UI/InfoWindow/Information'))
        descriptionIconLabelContainer = Container(name='descriptionIconLabelContainer', parent=infoContainer, align=uiconst.TOTOP, height=35)
        DescriptionIconLabel(name='rewardInfoIcon', parent=descriptionIconLabelContainer, align=uiconst.CENTERLEFT, text=GetByLabel('UI/Agency/AbyssalDeadspace/rewards'), tooltipPanelClassInfo=AbyssalDeadspaceRewardsTooltip())

    def ConstructFilamentContainer(self):
        filamentSearchContainer = SectionAutoSize(name='filamentSearchContainer', parent=self.rightContainer, align=uiconst.TOTOP, headerText=GetByLabel('UI/Agency/AbyssalDeadspace/filamentSearch'))
        filamentsContainer = ContainerAutoSize(name='filamentsContainer', parent=filamentSearchContainer, align=uiconst.TOTOP, padBottom=20)
        headerLabelContainer = Container(name='headerLabelContainer', parent=filamentsContainer, align=uiconst.TOTOP, height=22, padding=(10, 10, 0, 0))
        EveLabelLarge(parent=headerLabelContainer, align=uiconst.TOLEFT, text=GetByLabel('UI/Agency/AbyssalDeadspace/filamentType'), color=TextColor.NORMAL)
        EveLabelLarge(parent=headerLabelContainer, align=uiconst.TOLEFT, text=GetByLabel('UI/Agency/AbyssalDeadspace/weatherEffect'), left=130, color=TextColor.NORMAL)
        filamentEntriesContainer = ContainerAutoSize(name='filamentEntriesContainer', parent=filamentsContainer, align=uiconst.TOTOP, padBottom=20)
        for difficultyTier in DIFFICULTY_TIERS:
            AbyssalFilamentEntry(parent=filamentEntriesContainer, difficultyTier=difficultyTier, sortedWeatherNamesAndTypes=self.sortedWeatherNamesAndTypes)

    def ConstructLeftContainer(self):
        self.leftContainer = Container(name='leftContainer', parent=self, align=uiconst.TOLEFT, width=agencyUIConst.CONTENT_PAGE_WIDTH / 2)
        self.ConstructDescriptionContainer()
        self.ConstructWeatherInfoContainer()

    def ConstructWeatherInfoContainer(self):
        weatherInfoContainer = SectionAutoSize(name='weatherInfoContainer', parent=self.leftContainer, align=uiconst.TOTOP, top=6, headerText=GetByLabel('UI/Agency/AbyssalDeadspace/weatherTypes'))
        weatherTypesContainer = FlowContainer(name='weatherTypesContainer', parent=weatherInfoContainer, align=uiconst.TOTOP, contentSpacing=(20, 10))
        for weatherTypeID, weatherName in self.sortedWeatherNamesAndTypes:
            AbyssalWeatherTypeContainer(parent=weatherTypesContainer, typeID=weatherTypeID, weatherName=weatherName)

    def ConstructDescriptionContainer(self):
        filamentsContainer = SectionAutoSize(name='filamentsContainerLeft', parent=self.leftContainer, align=uiconst.TOTOP, headerText=GetByLabel('UI/Agency/AbyssalDeadspace/abyssalFilaments'))
        descriptionScrollContainer = ScrollContainer(name='descriptionScrollContainer', parent=filamentsContainer, align=uiconst.TOTOP, height=175)
        descriptionContainer = ContainerAutoSize(name='descriptionContainer', parent=descriptionScrollContainer, align=uiconst.TOTOP, height=64, alignMode=uiconst.TOTOP)
        Sprite(name='filamentExampleSprite', parent=Container(parent=descriptionContainer, align=uiconst.TOLEFT, width=64), align=uiconst.CENTERTOP, width=64, height=64, texturePath='res:/UI/Texture/Icons/Inventory/abyssalFilamentL3.png')
        EveLabelMedium(name='descriptionLabel', parent=descriptionContainer, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/AbyssalDeadspace/filamentsDescription'), opacity=0.75)
        obtainingFilamentsContainer = ContainerAutoSize(name='obtainingFilamentsContainer', parent=descriptionScrollContainer, align=uiconst.TOTOP, top=6)
        EveLabelMedium(parent=obtainingFilamentsContainer, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/AbyssalDeadspace/howToGetFilaments'), opacity=0.75)
        EveLabelMedium(parent=obtainingFilamentsContainer, align=uiconst.TOTOP, top=4, left=5, text=GetByLabel('UI/Agency/AbyssalDeadspace/filamentsAtDataSites'), opacity=0.75)
        buttonContainer = LayoutGrid(parent=ContainerAutoSize(parent=obtainingFilamentsContainer, align=uiconst.TOTOP, top=5, left=25), align=uiconst.TOPLEFT, columns=2)
        EveLabelMedium(parent=buttonContainer, align=uiconst.CENTERLEFT, text=GetByLabel('UI/Agency/jumpTo'))
        Button(name='signaturesButton', parent=buttonContainer, align=uiconst.TOPLEFT, label=GetByLabel('UI/Agency/ContentGroups/ContentGroupSignatures'), func=self.OpenExplorationContentGroup, left=8, density=Density.COMPACT)
        EveLabelMedium(parent=obtainingFilamentsContainer, align=uiconst.TOTOP, top=4, left=5, text=GetByLabel('UI/Agency/AbyssalDeadspace/filamentsInCaches'), opacity=0.75)
        EveLabelMedium(parent=obtainingFilamentsContainer, align=uiconst.TOTOP, top=4, left=5, text=GetByLabel('UI/Agency/AbyssalDeadspace/filamentsInMarket'), opacity=0.75, padBottom=10)

    @staticmethod
    def OpenExplorationContentGroup(*args):
        sm.GetService('agencyNew').OpenWindow(contentGroupID=contentGroupSignatures)


class AbyssalWeatherTypeContainer(Container):
    default_name = 'AbyssalWeatherTypeContainer'
    default_align = uiconst.NOALIGN
    default_width = 195
    default_height = 40

    def ApplyAttributes(self, attributes):
        super(AbyssalWeatherTypeContainer, self).ApplyAttributes(attributes)
        self.weatherName = attributes.weatherName
        self.typeID = attributes.typeID
        self.ConstructLayout()

    def ConstructLayout(self):
        weatherIconContainer = Container(name='weatherIconContainer', parent=self, align=uiconst.TOLEFT, width=40, height=40)
        Sprite(name='weatherIcon', parent=weatherIconContainer, align=uiconst.TOALL, texturePath=WEATHER_TEXTURE_PATHS_BY_ID.get(self.typeID, ''))
        DescriptionIconLabel(name='weatherInfoIconLabel', parent=ContainerAutoSize(parent=self, align=uiconst.TOLEFT, left=10), align=uiconst.CENTERLEFT, hint=GetByLabel(WEATHER_HINTS_BY_ID.get(self.typeID, '')), text=self.weatherName)


class AbyssalFilamentEntry(Container):
    default_name = 'AbyssalFilamentEntry'
    default_align = uiconst.TOTOP
    default_height = 40
    default_top = 10
    default_padLeft = 10

    def ApplyAttributes(self, attributes):
        super(AbyssalFilamentEntry, self).ApplyAttributes(attributes)
        self.difficultyTier = attributes.difficultyTier
        self.sortedWeatherNamesAndTypes = attributes.sortedWeatherNamesAndTypes
        self.ConstructLayout()

    def ConstructLayout(self):
        Sprite(name='tierIcon', parent=Container(parent=self, align=uiconst.TOLEFT, width=40), align=uiconst.TOALL, texturePath=TIER_TEXTURE_PATH_BY_TIER.get(self.difficultyTier, ''))
        textContainer = Container(name='textContainer', parent=self, align=uiconst.TOLEFT, width=100, left=10)
        EveLabelLarge(parent=ContainerAutoSize(parent=textContainer, align=uiconst.TOTOP), align=uiconst.CENTERLEFT, text=GetByLabel(NAME_LABEL_PATH_BY_TIER.get(self.difficultyTier, '')), color=TextColor.NORMAL)
        EveLabelMedium(parent=ContainerAutoSize(parent=textContainer, align=uiconst.TOTOP), align=uiconst.CENTERLEFT, text=GetByLabel(DIFFICULTY_LABEL_PATH_BY_TIER.get(self.difficultyTier, '')), color=TextColor.SECONDARY)
        Button(parent=ContainerAutoSize(parent=self, align=uiconst.TORIGHT, left=10), align=uiconst.CENTER, label=GetByLabel('UI/Agency/AbyssalDeadspace/marketSearch'), func=self.OpenMarketOnSelectedFilamentType)
        self.weatherTypeCombo = Combo(name='weatherTypeCombo', parent=ContainerAutoSize(parent=self, align=uiconst.TORIGHT, left=10), align=uiconst.CENTER, options=self.GetWeatherTypeComboOptions(), height=25, width=115, callback=self.SetSelectedWeather, select=random.choice(WEATHER_TYPE_IDS))
        self.weatherTypeSprite = Sprite(name='weatherTypeSprite', parent=ContainerAutoSize(parent=self, align=uiconst.TORIGHT, left=10), align=uiconst.CENTER, width=40, height=40, texturePath=self.GetSelectedWeatherTexturePath())

    def OpenMarketOnSelectedFilamentType(self, *args):
        keyTypeID = KEY_TYPE_BY_TIER_AND_WEATHER.get((self.difficultyTier, self.weatherTypeCombo.GetValue()))
        sm.GetService('marketutils').ShowMarketDetails(keyTypeID)

    def SetSelectedWeather(self, *args):
        self.weatherTypeSprite.SetTexturePath(self.GetSelectedWeatherTexturePath())

    def GetSelectedWeatherTexturePath(self):
        return WEATHER_TEXTURE_PATHS_BY_ID.get(self.weatherTypeCombo.GetValue(), '')

    def GetWeatherTypeComboOptions(self):
        options = []
        for weatherType, weatherName in self.sortedWeatherNamesAndTypes:
            options.append((weatherName, weatherType))

        return options
