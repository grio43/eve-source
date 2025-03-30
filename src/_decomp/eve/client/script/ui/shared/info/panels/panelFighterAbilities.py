#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\info\panels\panelFighterAbilities.py
from appConst import defaultPadding
from carbonui.primitives.container import Container
from dogma import units
from dogma.attributes.format import FormatValue, GetFormattedAttributeAndValue
import dogma.const as dogmaConst
from eve.client.script.ui.control.entries.header import Header
from eve.client.script.ui.control.entries.label_text import LabelTextSides, LabelTextSidesAttributes
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.shared.fitting.fittingUtil import ModifiedAttribute
from fighters import IterTypeAbilities
import fighters
from fighters.abilityAttributes import GetDogmaAttributeIDsForAbilityID, GetAbilityRangeAndFalloffAttributeIDs, GetAbilityDurationAttributeID, GetDamageMultiplierAttributeFromAbilityID, FIGHTER_DAMAGE_ATTRIBUTES
from localization import GetByLabel, GetByMessageID
from shipfitting.fittingDogmaLocationUtil import GetDamageForSquadron

class PanelFighterAbilities(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.itemID = attributes.get('itemID', None)
        self.typeID = attributes.typeID
        self.infoSvc = sm.GetService('info')
        self.dogmaStaticMgr = sm.GetService('clientDogmaStaticSvc')
        self.dogmaLocation = attributes.dogmaLocation

    def Load(self):
        self.Flush()
        self.scroll = Scroll(name='abilityScroll', parent=self, padding=defaultPadding)
        contentList = self._GetContentList()
        self.scroll.Load(contentList=contentList)

    def _GetContentList(self):
        contentList = []
        for slotID, typeAbility in IterTypeAbilities(self.typeID):
            if typeAbility is not None:
                abilityID = typeAbility.abilityID
                ability = fighters.AbilityStorage()[abilityID]
                self._AddAbilityHeader(contentList, ability)
                self._AddRestrictionEntries(contentList, ability)
                self._AddRangeEntries(contentList, abilityID)
                self._AddDurationEntry(contentList, abilityID)
                self._AddCooldownEntry(contentList, typeAbility)
                self._AddChargeCountEntry(contentList, typeAbility)
                self._AddAttributeEntries(contentList, abilityID)

        return contentList

    def _AddAbilityHeader(self, contentList, ability):
        contentList.append(GetFromClass(Header, {'label': GetByMessageID(ability.displayNameID)}))

    def _AddRestrictionEntries(self, contentList, ability):
        if ability.disallowInHighSec:
            contentList.append(GetFromClass(LabelTextSides, {'label': GetByLabel('UI/Fighters/AbilityDisallowedInHighSec'),
             'text': '',
             'iconID': '77_12'}))
        if ability.disallowInLowSec:
            contentList.append(GetFromClass(LabelTextSides, {'label': GetByLabel('UI/Fighters/AbilityDisallowedInLowSec'),
             'text': '',
             'iconID': '77_12'}))

    def _AddRangeEntries(self, contentList, abilityID):
        rangeAttributeID, falloffAttributeID = GetAbilityRangeAndFalloffAttributeIDs(self.dogmaStaticMgr, abilityID)
        contentList.extend(self.infoSvc.GetAttributeScrollListForItem(self.itemID, self.typeID, attrList=[rangeAttributeID, falloffAttributeID]))

    def _AddDurationEntry(self, contentList, abilityID):
        durationAttributeID = GetAbilityDurationAttributeID(self.dogmaStaticMgr, abilityID)
        contentList.extend(self.infoSvc.GetAttributeScrollListForItem(self.itemID, self.typeID, attrList=[durationAttributeID]))

    def _AddCooldownEntry(self, contentList, typeAbility):
        if typeAbility.cooldownSeconds:
            contentList.append(GetFromClass(LabelTextSides, {'label': GetByLabel('UI/Fighters/AbilityCooldown'),
             'text': FmtFSDTimeAttribute(typeAbility.cooldownSeconds),
             'iconID': '22_16'}))

    def _AddChargeCountEntry(self, contentList, typeAbility):
        if typeAbility.charges is not None:
            contentList.append(GetFromClass(LabelTextSides, {'label': GetByLabel('UI/Fighters/AbilityChargeCount'),
             'text': typeAbility.charges.chargeCount,
             'iconID': '22_21'}))
            contentList.append(GetFromClass(LabelTextSides, {'label': GetByLabel('UI/Fighters/RearmTimePerCharge'),
             'text': FmtFSDTimeAttribute(typeAbility.charges.rearmTimeSeconds),
             'iconID': '22_16'}))

    def _AddAttributeEntries(self, contentList, abilityID):
        abilityAttributeIDs = GetDogmaAttributeIDsForAbilityID(abilityID)
        dogmaLocation = self.infoSvc.GetDogmaLocation(self.itemID)
        damageFromAbility, dpsFromAbility = GetDamageForSquadron(dogmaLocation, self.itemID, 1, abilityID)
        if damageFromAbility:
            banAttrs = FIGHTER_DAMAGE_ATTRIBUTES
            entryList = self.TryGetDamageEntry(abilityAttributeIDs, abilityID, damageFromAbility)
        else:
            banAttrs = []
            entryList = []
        if abilityAttributeIDs:
            contentList.extend(self.infoSvc.GetAttributeScrollListForItem(self.itemID, self.typeID, attrList=abilityAttributeIDs, banAttrs=banAttrs))
        if entryList:
            contentList += entryList

    def TryGetDamageEntry(self, abilityAttributeIDs, abilityID, damageFromAbility):
        entryList = []
        damageMultiplierAttributeID = GetDamageMultiplierAttributeFromAbilityID(abilityID)
        if self.itemID and damageMultiplierAttributeID:
            dogmaLocation = self.infoSvc.GetDogmaLocation(self.itemID)
            damageAttributesForAbility = [ x for x in abilityAttributeIDs if x in FIGHTER_DAMAGE_ATTRIBUTES ]
            for eachDmgAttributeID in damageAttributesForAbility:
                dmgValue = dogmaLocation.GetAttributeValue(self.itemID, eachDmgAttributeID)
                if dmgValue == 0:
                    continue
                entry = self.GetCustomDamageEntry(damageFromAbility, eachDmgAttributeID, damageMultiplierAttributeID)
                entryList.append(entry)

        return entryList

    def GetCustomDamageEntry(self, value, attributeID, damageMultiplierAttributeID):
        formatInfo = GetFormattedAttributeAndValue(attributeID, value)
        if not formatInfo:
            return
        if self.itemID and formatInfo.infoTypeID and self.typeID != formatInfo.infoTypeID:
            itemID = None
        else:
            itemID = self.itemID
        baseValue = self.dogmaStaticMgr.GetTypeAttribute(self.typeID, attributeID)
        modifiedValue = ModifiedAttribute(value, oldValue=baseValue, attributeID=attributeID, higherIsBetter=True)
        return GetFromClass(LabelTextSidesAttributes, {'attributeID': attributeID,
         'line': 1,
         'label': formatInfo.displayName,
         'text': formatInfo.value,
         'iconID': formatInfo.iconID,
         'typeID': formatInfo.infoTypeID,
         'itemID': itemID,
         'modifiedAttribute': modifiedValue,
         'OnClick': (self.OnCustomDamageEntryClicked,
                     attributeID,
                     itemID,
                     damageMultiplierAttributeID)})

    def OnCustomDamageEntryClicked(self, attributeID, itemID, damageMultiplierAttributeID):
        self.infoSvc.OnAttributeClick(attributeID, itemID)
        self.infoSvc.OnAttributeClick(damageMultiplierAttributeID, itemID)


def FmtFSDTimeAttribute(valueSeconds):
    numberText = FormatValue(valueSeconds * 1000, dogmaConst.unitMilliseconds)
    return GetByLabel('UI/InfoWindow/ValueAndUnit', value=numberText, unit=units.get_display_name(dogmaConst.unitMilliseconds))
