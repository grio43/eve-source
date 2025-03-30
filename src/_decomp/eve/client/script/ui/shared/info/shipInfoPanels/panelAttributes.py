#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\info\shipInfoPanels\panelAttributes.py
import eveicon
import localization
from collections import OrderedDict
import uthread2
from carbonui import Align, TextBody, uiconst, TextColor, TextHeader
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from dogma import const
from dogma.attributes.format import GetFormattedAttributeAndValue
from eve.client.script.ui.control.eveWindowUnderlay import ListEntryUnderlay
from eve.client.script.ui.inflight.shipModuleButton.attributeValueRowContainer import AttributeValueRowContainer
from eve.client.script.ui.shared.info.attribute import Attribute
from eve.client.script.ui.shared.info.shipInfoCollapsibleGroup import CollapsibleGaugeGroup, CollapsibleGroup
from eve.client.script.ui.shared.info.shipInfoListEntries import ListEntryStatusBarAttribute, ListEntryAttribute, ListEntryTypeAttribute
from eve.client.script.ui.shared.info.shipInfoPanels.panelBase import PanelBase
from eve.client.script.ui.shared.info.shipInfoConst import TOP_DOWN_NOSE_UP, TAB_ATTRIBUTES
from eve.common.script.util.eveFormat import FmtDist2
from fsdBuiltData.common.iconIDs import GetIconFile
from localization import GetByLabel
from shipfitting.fittingDogmaLocationUtil import GetAlignTimeFromAgilityAndMass
DAMAGE_TYPE_ICONS = {'em': 'res:/ui/texture/icons/22_32_12.png',
 'thermal': 'res:/ui/texture/icons/22_32_10.png',
 'kinetic': 'res:/ui/texture/icons/22_32_9.png',
 'explosive': 'res:/ui/texture/icons/22_32_11.png'}
DAMAGE_TYPE_COLORS = {'em': (0.1,
        0.37,
        0.55,
        1.0),
 'thermal': (0.55,
             0.1,
             0.1,
             1.0),
 'kinetic': (0.45,
             0.45,
             0.45,
             1.0),
 'explosive': (0.55,
               0.37,
               0.1,
               1.0)}
MIN_IN_MS = 60 * 1000
ATTRIBUTE_GROUP_ICONS = {'structure': eveicon.inventory,
 'armor': eveicon.armor,
 'shield': eveicon.shields,
 'ewar': eveicon.capacitor_warfare,
 'capacitor': eveicon.capacitor_plus,
 'targeting': eveicon.target,
 'sharedFacilities': eveicon.shared_folder,
 'fighterFacilities': eveicon.drones,
 'onDeath': eveicon.inventory,
 'jumpDrive': eveicon.broadcast_warp_to_jump_beacon,
 'propulsion': eveicon.warp_to,
 'navigation': eveicon.warp_to,
 'drones': eveicon.drones,
 'inventory': eveicon.inventory}

class PanelAttributes(PanelBase):

    def ApplyAttributes(self, attributes):
        self.fitting_controller = None
        super(PanelAttributes, self).ApplyAttributes(attributes)

    def _construct_content(self):
        self.scrollContainer = ScrollContainer(name='abilityScroll', parent=self.rightCont, align=Align.TOALL)
        self.attributeCont = ContainerAutoSize(name='abilityCont', parent=self.scrollContainer, align=Align.TOTOP)
        self._construct_attributes()
        uthread2.start_tasklet(self._construct_size)

    def _construct_attributes(self):
        attrDict = self.infoSvc.GetAttributeDictForType(self.typeID)
        for group_id, attribGroup in self.attributesByCaption.iteritems():
            group_icon = ATTRIBUTE_GROUP_ICONS[group_id]
            group_name = attribGroup['groupName']
            normalAttributes = attribGroup['normalAttributes']
            groupedAttributes = attribGroup.get('groupedAttributes', [])
            constructedAttributes = attribGroup.get('constructedAttributes', None)
            derivedHeaderAttribute = attribGroup.get('derivedHeaderAttribute', None)
            derivedHeaderAttributeLabel = None
            derivedHeaderAttributeValue = None
            derivedHeaderAttributeTooltip = None
            derivedHeaderAttributeFormat = None
            if derivedHeaderAttribute:
                derivedHeaderAttributeLabel = derivedHeaderAttribute['name']
                derivedHeaderAttributeTooltip = derivedHeaderAttribute['tooltip']
                derivedHeaderAttributeFormat = derivedHeaderAttribute['format']
                valueFunc = derivedHeaderAttribute['valueFunc']
                parameterAttribs = derivedHeaderAttribute['parameterAttributes']
                params = {}
                for name, attributeID in parameterAttribs.iteritems():
                    params[name] = self.attributes[attributeID].value

                derivedHeaderAttributeValue = valueFunc(**params)
            if groupedAttributes:
                groupedAttribs = {}
                layerHpAttributeID = attribGroup['hpAttribute']
                hpDescriptionPath = attribGroup['hpDescriptionPath']
                layerHp = self.attributes[layerHpAttributeID].value
                for damageType, attributeID in groupedAttributes:
                    attrib = self.attributes[attributeID]
                    modifiedAttrib = self.modifiedAttributesDict.get(attributeID, None)
                    groupedAttribs[damageType] = (attrib, modifiedAttrib)

                groupContainer = CollapsibleGaugeGroup(parent=self.attributeCont, name=group_id, align=Align.TOTOP, groupIcon=group_icon, groupName=group_name, iconID=eveicon.armor, itemID=self.itemID, layerHp=layerHp, groupedAttributes=groupedAttribs, padBottom=8, damageTypeIcons=DAMAGE_TYPE_ICONS, damageTypeColors=DAMAGE_TYPE_COLORS, ehpDescriptionPath=hpDescriptionPath)
            else:
                groupContainer = CollapsibleGroupWithHeaderAttribute(parent=self.attributeCont, name=group_id, align=Align.TOTOP, groupIcon=group_icon, groupName=group_name, padBottom=8, headerAttributeLabel=derivedHeaderAttributeLabel, headerAttributeValue=derivedHeaderAttributeValue, headerAttributeTooltip=derivedHeaderAttributeTooltip, headerAttributeFormat=derivedHeaderAttributeFormat)
            groupedEntries, attribsAdded = self.infoSvc.GetAttributeRowData(normalAttributes, attrDict, self.itemID, self.modifiedAttributesDict)
            shipAttr = [ each for each in normalAttributes if each in attrDict ]
            for attributeID in shipAttr:
                if attributeID in attribsAdded:
                    continue
                attrib = self.attributes[attributeID]
                modifiedAttrib = self.modifiedAttributesDict.get(attributeID, None)
                if attrib.unitID == const.unitMilliseconds and attrib.value >= 5 * MIN_IN_MS:
                    formatInfo = GetFormattedAttributeAndValue(attributeID, attrib.value / MIN_IN_MS / 60, const.unitHour)
                else:
                    formatInfo = GetFormattedAttributeAndValue(attributeID, attrib.value)
                if not formatInfo:
                    continue
                statusBarData = self.infoSvc.GetStatusBarDataForAttribute(attributeID, self.itemID, self.typeID, modifiedAttrib)
                if statusBarData:
                    texturePath = GetIconFile(statusBarData['iconID'])
                    ListEntryStatusBarAttribute(label=statusBarData['label'], text=statusBarData['text'], texturePath=texturePath, itemID=self.itemID, attributeID=statusBarData['attributeID'], modifiedAttribute=statusBarData['modifiedAttribute'], color=statusBarData['color'], value=statusBarData['value'], parent=groupContainer.mainCont)
                    continue
                attributeData = self.infoSvc.GetDataForAttribute(attributeID, attrib.value, self.itemID, self.typeID, modifiedAttrib)
                if attributeData:
                    texturePath = GetIconFile(attributeData['iconID'])
                    if attributeData['typeID']:
                        ListEntryTypeAttribute(label=attributeData['label'], text=attributeData['text'], texturePath=texturePath, typeID=attributeData['typeID'], itemID=self.itemID, attributeID=attributeData['attributeID'], modifiedAttribute=attributeData['modifiedAttribute'], parent=groupContainer.mainCont)
                    else:
                        ListEntryAttribute(label=attributeData['label'], text=attributeData['text'], texturePath=texturePath, itemID=self.itemID, attributeID=attributeData['attributeID'], modifiedAttribute=attributeData['modifiedAttribute'], parent=groupContainer.mainCont)

            if constructedAttributes:
                for attributeID, dataFunc in constructedAttributes:
                    data = dataFunc(self.typeID, self.itemID)
                    texturePath = GetIconFile(data['iconID'])
                    if data:
                        ListEntryAttribute(parent=groupContainer.mainCont, label=data['label'], text=data['text'], texturePath=texturePath, itemID=self.itemID, attributeID=data['attributeID'], modifiedAttribute=data.get('modifiedAttribute', None))

            for dataEntry in groupedEntries:
                ListEntryAttributeGroup(parent=groupContainer.mainCont, padLeft=4, **dataEntry)

            if len(groupContainer.mainCont.children) == 0:
                groupContainer.Hide()
                continue

    def _construct_size(self):
        bottomCont = Container(name='bottomCont', parent=self.leftCont, align=Align.TOBOTTOM, height=84, padLeft=32, opacity=0)
        long_axis_length = self._controller.long_axis_length
        while long_axis_length == 0:
            uthread2.sleep(0.01)
            long_axis_length = self._controller.long_axis_length

        length = FmtDist2(long_axis_length, maxDecimals=0)
        labelCont = Container(name='labelCont', parent=bottomCont, align=Align.TOTOP, height=12)
        TextBody(name='label', parent=labelCont, align=Align.CENTERLEFT, text=localization.GetByLabel('UI/InfoWindow/LongAxis'), color=TextColor.SECONDARY)
        valueCont = Container(name='valueCont', parent=bottomCont, align=Align.TOTOP, height=24)
        TextHeader(name='value', parent=valueCont, align=Align.CENTERLEFT, text=length, bold=True)
        animations.FadeIn(bottomCont, duration=1.2)

    def _gather_data(self):
        self.infoSvc = sm.GetService('info')
        self.attributesByCaption = self.get_ship_attributes()
        self.attributeDictForType, self.attributeDict = self.infoSvc.GetAttributeDictForItem(self.itemID, self.typeID)
        self.modifiedAttributesDict = self.infoSvc.FindAttributesThatHaveBeenModified(self.attributeDictForType, self.attributeDict)
        if not self.attributeDict:
            self.attributeDict = self.attributeDictForType
        self.attributes = {}
        for attributeID, value in self.attributeDict.iteritems():
            self.attributes[attributeID] = Attribute(attributeID, value)

    def _enable_expanded_view(self):
        self.attributeCont.SetParent(self.scrollContainer)

    def _enable_minimized_view(self):
        self.attributeCont.SetParent(self.content_scroll_minimized)

    @classmethod
    def get_name(cls):
        return localization.GetByLabel('UI/InfoWindow/TabNames/Attributes')

    @classmethod
    def get_icon(cls):
        return eveicon.attributes

    def get_camera_position(self):
        return TOP_DOWN_NOSE_UP

    def get_tab_type(self):
        return TAB_ATTRIBUTES

    @classmethod
    def is_visible(cls, typeID, itemID = None, rec = None):
        return True

    def _get_group_icon(self, group_id):
        return None

    def get_ship_attributes(self):
        shipAttributes = OrderedDict()
        shipAttributes['shield'] = {'groupName': GetByLabel('UI/Common/Shield'),
         'hpAttribute': const.attributeShieldCapacity,
         'hpDescriptionPath': 'UI/InfoWindow/EffectiveHpDescriptionShield',
         'groupedAttributes': [('em', const.attributeShieldEmDamageResonance),
                               ('thermal', const.attributeShieldThermalDamageResonance),
                               ('kinetic', const.attributeShieldKineticDamageResonance),
                               ('explosive', const.attributeShieldExplosiveDamageResonance)],
         'normalAttributes': [const.attributeShieldCapacity, const.attributeShieldRechargeRate, const.attributeShieldDamageLimit]}
        shipAttributes['armor'] = {'groupName': GetByLabel('UI/Common/Armor'),
         'hpAttribute': const.attributeArmorHP,
         'hpDescriptionPath': 'UI/InfoWindow/EffectiveHpDescriptionArmor',
         'groupedAttributes': [('em', const.attributeArmorEmDamageResonance),
                               ('thermal', const.attributeArmorThermalDamageResonance),
                               ('kinetic', const.attributeArmorKineticDamageResonance),
                               ('explosive', const.attributeArmorExplosiveDamageResonance)],
         'normalAttributes': [const.attributeArmorHP, const.attributeArmorDamageLimit]}
        shipAttributes['structure'] = {'groupName': GetByLabel('UI/Fitting/Structure'),
         'hpAttribute': const.attributeHp,
         'hpDescriptionPath': 'UI/InfoWindow/EffectiveHpDescriptionStructure',
         'groupedAttributes': [('em', const.attributeEmDamageResonance),
                               ('thermal', const.attributeThermalDamageResonance),
                               ('kinetic', const.attributeKineticDamageResonance),
                               ('explosive', const.attributeExplosiveDamageResonance)],
         'normalAttributes': [const.attributeHp, const.attributeStructureDamageLimit]}
        shipAttributes['capacitor'] = {'groupName': GetByLabel('UI/Fitting/FittingWindow/Capacitor'),
         'normalAttributes': [const.attributeCapacitorCapacity, const.attributeRechargeRate]}
        shipAttributes['navigation'] = {'groupName': GetByLabel('UI/Fitting/Navigation'),
         'derivedHeaderAttribute': {'name': 'Tooltips/FittingWindow/AlignTime',
                                    'format': 'UI/Fitting/FittingWindow/AlignTime',
                                    'tooltip': 'Tooltips/FittingWindow/AlignTime_description',
                                    'hint': '',
                                    'valueFunc': GetAlignTimeFromAgilityAndMass,
                                    'parameterAttributes': {'agility': const.attributeAgility,
                                                            'mass': const.attributeMass}},
         'normalAttributes': [const.attributeMaxVelocity, const.attributeMass, const.attributeAgility],
         'constructedAttributes': [(const.attributeBaseWarpSpeed, lambda typeID, itemID: sm.GetService('info').GetWarpSpeedData(typeID, itemID))]}
        shipAttributes['targeting'] = {'groupName': GetByLabel('UI/Fitting/FittingWindow/Targeting'),
         'normalAttributes': [const.attributeMaxTargetRange,
                              const.attributeMaxRange,
                              const.attributeMaxLockedTargets,
                              const.attributeSignatureRadius,
                              const.attributeSignatureResolution,
                              const.attributeScanResolution,
                              const.attributeScanLadarStrength,
                              const.attributeScanMagnetometricStrength,
                              const.attributeScanRadarStrength,
                              const.attributeScanGravimetricStrength,
                              const.attributeProximityRange,
                              const.attributeFalloff,
                              const.attributeTrackingSpeed]}
        shipAttributes['drones'] = {'groupName': GetByLabel('UI/Drones/Drones'),
         'normalAttributes': [const.attributeDroneCapacity, const.attributeDroneBandwidth]}
        shipAttributes['inventory'] = {'groupName': GetByLabel('UI/Neocom/InventoryBtn'),
         'normalAttributes': [const.attributeVolume,
                              const.attributeCapacity,
                              const.attributeFrigateEscapeBayCapacity,
                              const.attributeSpecialAmmoHoldCapacity,
                              const.attributeSpecialGasHoldCapacity,
                              const.attributeSpecialIceHoldCapacity,
                              const.attributeSpecialIndustrialShipHoldCapacity,
                              const.attributeSpecialLargeShipHoldCapacity,
                              const.attributeSpecialMediumShipHoldCapacity,
                              const.attributeSpecialMineralHoldCapacity,
                              const.attributeGeneralMiningHoldCapacity,
                              const.attributeSpecialAsteroidHoldCapacity,
                              const.attributeSpecialSalvageHoldCapacity,
                              const.attributeSpecialShipHoldCapacity,
                              const.attributeSpecialSmallShipHoldCapacity,
                              const.attributeSpecialCommandCenterHoldCapacity,
                              const.attributeSpecialPlanetaryCommoditiesHoldCapacity,
                              const.attributeSpecialSubsystemHoldCapacity,
                              const.attributeSpecialCorpseHoldCapacity,
                              const.attributeSpecialBoosterHoldCapacity,
                              const.attributeSpecialMobileDepotHoldCapacity,
                              const.attributeSpecialColonyResourcesHoldCapacity]}
        shipAttributes['ewar'] = {'groupName': GetByLabel('UI/Common/EWarResistances'),
         'normalAttributes': [const.attributeECMResistance,
                              const.attributeRemoteAssistanceImpedance,
                              const.attributeRemoteRepairImpedance,
                              const.attributeEnergyWarfareResistance,
                              const.attributeSensorDampenerResistance,
                              const.attributeStasisWebifierResistance,
                              const.attributeTargetPainterResistance,
                              const.attributeWeaponDisruptionResistance]}
        shipAttributes['sharedFacilities'] = {'groupName': GetByLabel('UI/InfoWindow/SharedFacilities'),
         'normalAttributes': [const.attributeFleetHangarCapacity,
                              const.attributeShipMaintenanceBayCapacity,
                              const.attributeMaxJumpClones,
                              const.attributeReclonerFuelType]}
        shipAttributes['fighterFacilities'] = {'groupName': GetByLabel('UI/InfoWindow/FighterFacilities'),
         'normalAttributes': [const.attributeFighterCapacity,
                              const.attributeFighterTubes,
                              const.attributeFighterLightSlots,
                              const.attributeFighterSupportSlots,
                              const.attributeFighterHeavySlots,
                              const.attributeFighterStandupLightSlots,
                              const.attributeFighterStandupSupportSlots,
                              const.attributeFighterStandupHeavySlots]}
        shipAttributes['onDeath'] = {'groupName': GetByLabel('UI/InfoWindow/OnDeath'),
         'normalAttributes': [const.attributeOnDeathAOERadius,
                              const.attributeOnDeathSignatureRadius,
                              const.attributeOnDeathDamageEM,
                              const.attributeOnDeathDamageTherm,
                              const.attributeOnDeathDamageKin,
                              const.attributeOnDeathDamageExp]}
        shipAttributes['jumpDrive'] = {'groupName': GetByLabel('UI/InfoWindow/JumpDriveSystems'),
         'normalAttributes': [const.attributeJumpDriveCapacitorNeed,
                              const.attributeJumpDriveRange,
                              const.attributeJumpDriveConsumptionType,
                              const.attributeJumpDriveConsumptionAmount,
                              const.attributeJumpDriveDuration,
                              const.attributeJumpPortalCapacitorNeed,
                              const.attributeJumpPortalConsumptionMassFactor,
                              const.attributeJumpPortalDuration,
                              const.attributeSpecialFuelBayCapacity,
                              const.attributeGroupJumpDriveConsumptionAmount,
                              const.attributeConduitJumpPassengerCount]}
        return shipAttributes


class CollapsibleGroupWithHeaderAttribute(CollapsibleGroup):

    def ApplyAttributes(self, attributes):
        self.headerAttributeLabel = attributes.get('headerAttributeLabel', None)
        self.headerAttributeTooltip = attributes.get('headerAttributeTooltip', None)
        self.headerAttributeValue = attributes.get('headerAttributeValue', None)
        self.headerAttributeFormat = attributes.get('headerAttributeFormat', None)
        super(CollapsibleGroupWithHeaderAttribute, self).ApplyAttributes(attributes)

    def _construct_label(self):
        super(CollapsibleGroupWithHeaderAttribute, self)._construct_label()
        if not self.headerAttributeLabel:
            return
        headerAttributeCont = ContainerAutoSize(name='headerAttribContainer', parent=self.headerLabelWrapper, align=Align.TOLEFT, state=uiconst.UI_NORMAL, padLeft=8, hint=GetByLabel(self.headerAttributeTooltip))
        headerAttributeCont.OnClick = self.headerCont.OnClick
        headerAttributeLabel = TextBody(parent=headerAttributeCont, align=Align.CENTERLEFT, state=uiconst.UI_DISABLED, color=TextColor.SECONDARY, text=u'{}:'.format(GetByLabel(self.headerAttributeLabel)))
        headerValueLabel = TextBody(parent=headerAttributeCont, align=Align.CENTERLEFT, state=uiconst.UI_DISABLED, padLeft=headerAttributeLabel.width + 4, text=GetByLabel(self.headerAttributeFormat, value=self.headerAttributeValue))


class ListEntryAttributeGroup(ContainerAutoSize):

    def ApplyAttributes(self, attributes):
        self.default_state = uiconst.UI_NORMAL
        self.default_align = Align.TOTOP
        self.default_padBottom = 2
        self._hiliteFill = None
        super(ListEntryAttributeGroup, self).ApplyAttributes(attributes)
        self.itemID = attributes.itemID
        self.attributeValues = attributes.attributeValues
        self.modifiedAttributesDict = attributes.modifiedAttributesDict
        self.labelCont = ContainerAutoSize(name='labelCont', parent=self, align=Align.TOTOP, padTop=8, padLeft=8)
        self.label = TextBody(parent=self.labelCont, text=GetByLabel(attributes.labelPath))
        self.valueContainer = AttributeValueRowContainer(parent=self, align=Align.TOTOP, padding=(2, 2, 0, 2), doWidthAdjustments=True, loadOnStartup=False)
        self.valueContainer.Load(self.attributeValues, mouseExitFunc=self.OnMouseExit, modifiedAttributesDict=self.modifiedAttributesDict, itemID=self.itemID)

    def ConstructHiliteFill(self):
        if not self._hiliteFill:
            self._hiliteFill = ListEntryUnderlay(name='selectionHighlight', bgParent=self)

    def ShowHilite(self, animate = True):
        self.ConstructHiliteFill()
        self._hiliteFill.set_hovered(True, animate)

    def HideHilite(self, animate = True):
        if self._hiliteFill:
            self._hiliteFill.set_hovered(False, animate)

    def OnMouseEnter(self, *args):
        self.ShowHilite()

    def OnMouseExit(self, *args):
        self.HideHilite()
