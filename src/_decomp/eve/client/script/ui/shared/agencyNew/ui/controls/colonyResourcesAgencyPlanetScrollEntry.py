#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\controls\colonyResourcesAgencyPlanetScrollEntry.py
import eveicon
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.eveColor import PLATINUM_GREY
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.shared.agencyNew.ui.controls.agencyScrollContEntry import AgencyScrollContEntry
from inventorycommon.const import typeColonyReagentLava, typeColonyReagentIce
from localization import GetByLabel
from orbitalSkyhook.resourceRichness import GetPlanetWorkforceRichnessTexturePath, GetPlanetPowerRichnessTexturePath, GetPlanetReagentRichnessTexturePathAndHint
ICON_SIZE = 36

class ColonyResourcesAgencyPlanetScrollEntry(AgencyScrollContEntry):
    default_name = 'ColonyResourcesAgencyPlanetScrollEntry'
    default_height = 40

    def ApplyAttributes(self, attributes):
        super(ColonyResourcesAgencyPlanetScrollEntry, self).ApplyAttributes(attributes)
        self.powerText = GetByLabel('UI/Agency/ColonyResourcesAgency/Power')
        self.workforceText = GetByLabel('UI/Agency/ColonyResourcesAgency/Workforce')
        self.superionicIceText = GetByLabel('UI/Agency/ColonyResourcesAgency/SuperionicIce')
        self.magmaticGasText = GetByLabel('UI/Agency/ColonyResourcesAgency/MagmaticGas')

    def ConstructIcon(self):
        iconContainer = Container(name='iconContainer', parent=self, align=uiconst.TOLEFT, width=ICON_SIZE, padding=(2, 2, 4, 2))
        self.icon = Sprite(name='planetIcon', bgParent=iconContainer)

    def ConstructLabel(self):
        labelContainer = Container(name='labelContainer', parent=self, align=uiconst.TOALL)
        self.label = EveLabelMedium(name='planetNameLabel', parent=labelContainer, align=uiconst.CENTERLEFT, left=4)
        celestialIcons = []
        celestialValues = self.contentPiece.planetColonyResourcesValues
        if celestialValues.powerOutput:
            texturePath, hint = GetPlanetPowerRichnessTexturePath(celestialValues.powerOutput)
            celestialIcons.append((texturePath, hint))
        if celestialValues.workforceOutput:
            texturePath, hint = GetPlanetWorkforceRichnessTexturePath(celestialValues.workforceOutput)
            celestialIcons.append((texturePath, hint))
        if celestialValues.reagentsTypes:
            if celestialValues.reagentsTypes.hasSuperionicIce:
                texturePath, hint = GetPlanetReagentRichnessTexturePathAndHint(celestialValues.reagentsTypes.superionicIceAmount, typeColonyReagentIce)
                celestialIcons.append((texturePath, hint))
            if celestialValues.reagentsTypes.hasMagmaticGas:
                texturePath, hint = GetPlanetReagentRichnessTexturePathAndHint(celestialValues.reagentsTypes.magmaticGasAmount, typeColonyReagentLava)
                celestialIcons.append((texturePath, hint))
        if self.contentPiece.hasVulnerableSkyhook:
            texturePath = eveicon.reagents_skyhook
            hint = 'UI/Agency/ColonyResourcesAgency/SkyhooksIsTheftVulnerable'
            celestialIcons.append((texturePath, hint))
        for icon, hint in celestialIcons:
            cont = Container(parent=self, name='celestialIconContainer', align=uiconst.TORIGHT, width=20, padRight=8)
            sprite = Sprite(name='celestialIcon', parent=cont, width=20, height=20, texturePath=icon, align=uiconst.CENTER, color=PLATINUM_GREY)
            sprite.hint = GetByLabel(hint)

    def UpdateIcon(self):
        sm.GetService('photo').GetIconByType(self.icon, self.contentPiece.typeID)
