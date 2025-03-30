#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPageInfoConts\colonyResourcesAgencySystemInfoContainer.py
import log
import eveicon
from carbonui import uiconst, TextDetail
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.uianimations import animations
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.gridcontainer import GridContainer
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLabel import EveCaptionMedium
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.infoIcon import InfoIcon
from eve.client.script.ui.eveColor import PLATINUM_GREY
from eve.common.lib import appConst
from evelink.client import owner_link
from inventorycommon.const import typeColonyReagentIce, typeColonyReagentLava
from orbitalSkyhook.resourceRichness import GetSystemPowerRichnessTexturePath, GetSystemWorkforceRichnessTexturePath, GetSystemReagentRichnessTexturePathAndHint
from localization import GetByLabel

class ColonyResourcesAgencySystemInfoContainer(Container):

    def ApplyAttributes(self, attributes):
        super(ColonyResourcesAgencySystemInfoContainer, self).ApplyAttributes(attributes)
        self.powerText = GetByLabel('UI/Agency/ColonyResourcesAgency/Power')
        self.workforceText = GetByLabel('UI/Agency/ColonyResourcesAgency/Workforce')
        self.superionicIceText = GetByLabel('UI/Agency/ColonyResourcesAgency/SuperionicIce')
        self.magmaticGasText = GetByLabel('UI/Agency/ColonyResourcesAgency/MagmaticGas')
        self.infoPanelSvc = sm.GetService('infoPanel')
        self.contentPiece = None
        statsWidth = 160
        nameAndAllianceCont = Container(name='nameAndAllianceCont', parent=self, align=uiconst.TOALL, padRight=statsWidth)
        nameCont = ContainerAutoSize(name='nameCont', parent=nameAndAllianceCont, align=uiconst.TOTOP)
        nameGrid = LayoutGrid(name='nameGrid', parent=nameCont, align=uiconst.TOPLEFT, cellSpacing=4, columns=2)
        self.systemNameLabel = EveCaptionMedium(name='systemNameLabel', parent=nameGrid, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL)
        iconCont = Container(parent=nameGrid, align=uiconst.CENTERLEFT, pos=(-1, 0, 16, 16))
        self.systemInfoIcon = InfoIcon(name='systemInfoIcon', parent=iconCont, align=uiconst.CENTER, typeID=appConst.typeSolarSystem)
        self.allianceLabel = TextDetail(name='allianceLabel', parent=nameAndAllianceCont, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        systemCelestialStatsContainer = GridContainer(name='systemCelestialStatsContainer', parent=self, align=uiconst.CENTERRIGHT, height=48, width=statsWidth, columns=2)
        self.powerOutputInfoContainer = Container(name='powerOutputInfoContainer', parent=systemCelestialStatsContainer)
        self.powerOutputInfoSprite = Sprite(parent=self.powerOutputInfoContainer, width=18, height=18, texturePath=eveicon.power, align=uiconst.CENTERLEFT, color=PLATINUM_GREY)
        self.powerOutputInfoLabel = Label(parent=self.powerOutputInfoContainer, align=uiconst.CENTERLEFT, padLeft=22, height=18)
        self.workforceOutputInfoContainer = Container(name='workforceOutputInfoGridContainer', parent=systemCelestialStatsContainer)
        self.workforceOutputInfoSprite = Sprite(parent=self.workforceOutputInfoContainer, width=18, height=18, texturePath=eveicon.workforce, align=uiconst.CENTERLEFT, color=PLATINUM_GREY)
        self.workforceOutputInfoLabel = Label(parent=self.workforceOutputInfoContainer, align=uiconst.CENTERLEFT, padLeft=22, height=18)
        self.superionicIceContainer = Container(name='superionicIceContainer', parent=systemCelestialStatsContainer)
        self.superIonicIceSprite = Sprite(parent=self.superionicIceContainer, width=18, height=18, texturePath=eveicon.superionic_ice, align=uiconst.CENTERLEFT, color=PLATINUM_GREY)
        self.superIonicIceLabel = Label(parent=self.superionicIceContainer, align=uiconst.CENTERLEFT, padLeft=22, height=18)
        self.magmaticGasContainer = Container(name='magmaticGasContainer', parent=systemCelestialStatsContainer)
        self.magmaticGasSprite = Sprite(parent=self.magmaticGasContainer, width=18, height=18, texturePath=eveicon.magmatic_gas, align=uiconst.CENTERLEFT, color=PLATINUM_GREY)
        self.magmaticGasLabel = Label(parent=self.magmaticGasContainer, align=uiconst.CENTERLEFT, padLeft=22, height=18)

    def UpdateContentPiece(self, contentPiece):
        self.Show()
        self.contentPiece = contentPiece
        hasSuperionicIce = self.contentPiece.solarSystemValues.reagentsTypes.hasSuperionicIce
        hasMagmaticGas = self.contentPiece.solarSystemValues.reagentsTypes.hasMagmaticGas
        superionicIceAmount = self.contentPiece.solarSystemValues.reagentsTypes.superionicIceAmount
        magmaticGasAmount = self.contentPiece.solarSystemValues.reagentsTypes.magmaticGasAmount
        powerOutput = self.contentPiece.solarSystemValues.powerOutput
        workforceOutput = self.contentPiece.solarSystemValues.workforceOutput
        sovAllianceID = self.contentPiece.sovAllianceID
        systemText = self.infoPanelSvc.GetSolarSystemText(contentPiece.solarSystemID, solarSystemAlt='')
        self.systemNameLabel.SetText(systemText)
        self.systemInfoIcon.SetItemID(contentPiece.solarSystemID)
        if sovAllianceID:
            self.allianceLabel.text = owner_link(sovAllianceID)
        else:
            self.allianceLabel.text = ''
        if powerOutput:
            texturePath, hint = GetSystemPowerRichnessTexturePath(powerOutput)
            self.powerOutputInfoSprite.SetTexturePath(texturePath)
            self.powerOutputInfoSprite.hint = GetByLabel(hint)
            self.powerOutputInfoContainer.Show()
            self.powerOutputInfoLabel.SetText(str(powerOutput))
        else:
            self.powerOutputInfoContainer.Hide()
        if workforceOutput:
            texturePath, hint = GetSystemWorkforceRichnessTexturePath(workforceOutput)
            self.workforceOutputInfoSprite.SetTexturePath(texturePath)
            self.workforceOutputInfoSprite.hint = GetByLabel(hint)
            self.workforceOutputInfoContainer.Show()
            self.workforceOutputInfoLabel.SetText(str(workforceOutput))
        else:
            self.workforceOutputInfoContainer.Hide()
        if hasSuperionicIce:
            texturePath, hint = GetSystemReagentRichnessTexturePathAndHint(superionicIceAmount, typeColonyReagentIce)
            self.superIonicIceSprite.SetTexturePath(texturePath)
            self.superIonicIceSprite.hint = GetByLabel(hint)
            self.superionicIceContainer.Show()
            self.superIonicIceLabel.SetText(str(superionicIceAmount) + '/h')
        else:
            self.superionicIceContainer.Hide()
        if hasMagmaticGas:
            texturePath, hint = GetSystemReagentRichnessTexturePathAndHint(magmaticGasAmount, typeColonyReagentLava)
            if not hasSuperionicIce:
                self.magmaticGasContainer.Hide()
                self.superIonicIceSprite.SetTexturePath(texturePath)
                self.superIonicIceLabel.SetText(str(magmaticGasAmount) + '/h')
                self.superIonicIceSprite.hint = GetByLabel(hint)
                self.superionicIceContainer.Show()
            else:
                self.magmaticGasSprite.SetTexturePath(texturePath)
                self.magmaticGasSprite.hint = GetByLabel(hint)
                self.magmaticGasContainer.Show()
                self.magmaticGasLabel.SetText(str(magmaticGasAmount) + '/h')
        else:
            self.magmaticGasContainer.Hide()
        animations.FadeTo(self, 0.0, 1.0, duration=0.2)
