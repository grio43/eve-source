#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\fighterTooltip.py
import dogma.data as dogma_data
import evetypes
from carbon.common.script.util.format import FmtDist
from carbon.common.script.util.timerstuff import AutoTimer
from eve.client.script.ui.inflight.shipModuleButton.moduleButtonTooltip import ModuleButtonTooltip
from eve.client.script.ui.inflight.squadrons.squadronController import SquadronController
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from eve.common.script.mgt.fighterConst import TUBE_STATES_INSPACE
from fighters import ABILITY_SLOT_0, ABILITY_SLOT_2, GetAbilityNameID
from fighters import GetMaxSquadronSize
from localization import GetByLabel, GetByMessageID
from shipfitting.fittingDogmaLocationUtil import GetRangesForAbilitySlot, GetDamageForAbilitySlot
import carbonui.const as uiconst
from utillib import KeyVal

class TooltipFighterWrapper(TooltipBaseWrapper):

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = FighterTooltip(parent=parent, owner=owner, idx=idx)
        return self.tooltipPanel


class FighterTooltip(ModuleButtonTooltip):
    infoFunctionNamesForCategories = {const.categoryFighter: 'AddFighterInfo'}
    infoFunctionNames = {}

    def LoadTooltip(self):
        if not self.owner:
            return
        itemID = self.owner.GetFighterItemID()
        if not itemID:
            return
        self.tubeFlagID = self.owner.tubeFlagID
        self.moduleItemID = itemID
        self.itemID = itemID
        self.ownerGuid = 'Fighters'
        if not self.moduleItemID:
            return
        if getattr(self.owner, 'tooltipIdentifier', '') == 'SimulatedFighterTooltip':
            self.dogmaLocation = sm.GetService('fittingSvc').GetCurrentDogmaLocation()
            self.isSimulated = True
        else:
            self.dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
            self.isSimulated = False
        self.moduleInfoItem = self.dogmaLocation.GetDogmaItem(self.itemID)
        self.moduleGroupID = evetypes.GetGroupID(self.moduleInfoItem.typeID)
        self.moduleCategoryID = evetypes.GetCategoryID(self.moduleInfoItem.typeID)
        self.numSlaves = 0
        if self.stateManager.GetDefaultEffect(self.moduleInfoItem.typeID):
            self.moduleShortcut = self.GetModuleShortcut(self.moduleInfoItem)
        else:
            self.moduleShortcut = None
        self.typeName = evetypes.GetName(self.moduleInfoItem.typeID)
        self.onHUDModuleButton = False
        self.UpdateToolTips()
        self._toolTooltipUpdateTimer = AutoTimer(1000, self.UpdateToolTips)

    def UpdateToolTips(self):
        if self.destroyed or self.beingDestroyed or self.owner is None:
            self._toolTooltipUpdateTimer = None
            return
        self.Flush()
        typeText = self.GetTypeText()
        self.AddTypeAndIcon(label=typeText, typeID=self.moduleInfoItem.typeID, moduleShortcut=self.moduleShortcut)
        self.AddDamageInfo()
        chargeInfoItem = None
        if self.ShouldAddDps(chargeInfoItem):
            self.AddDpsAndDamgeTypeInfo(self.moduleItemID, self.moduleInfoItem.typeID, self.moduleGroupID, chargeInfoItem, self.numSlaves)
        self.AddGroupAndCategoryExtraInfo(chargeInfoItem)

    def GetTypeText(self):
        numInSquadron = self._GetNumInSquadron()
        if numInSquadron > 1:
            typeText = GetByLabel('UI/Inflight/ModuleRacks/TypeNameWithNumInGroup', numInGroup=numInSquadron, typeName=self.typeName)
        else:
            typeText = self.typeName
        typeText = '<b>%s</b>' % typeText
        return typeText

    def _GetFightersForTube(self):
        return self.dogmaLocation.GetFightersForTube(self.tubeFlagID)

    def _GetNumInSquadron(self):
        fighters = self._GetFightersForTube()
        if fighters:
            return fighters.squadronSize
        else:
            return 0

    def AddFighterInfo(self, *args):
        self.AddVelocity()
        self.AddTargetingRange()
        self.AddScanRes()
        self.AddSignatureRadius()

    def GetRanges(self, chargeInfoItem):
        return (None, None, None, None)

    def GetNumberOfSlaves(self, *args):
        return 1

    def ShouldAddDps(self, *args):
        return True

    def AddDpsAndDamgeTypeInfo(self, itemID, typeID, groupID, charge, numSlaves):
        fighters = self.dogmaLocation.GetFightersForTube(self.tubeFlagID)
        if fighters is None:
            return
        texturePath = 'res:/UI/Texture/Icons/drones.png'
        for eachSlotID in (ABILITY_SLOT_0, ABILITY_SLOT_2):
            dps, damage, abilityID = GetDamageForAbilitySlot(self.dogmaLocation, itemID, typeID, fighters.squadronSize, eachSlotID)
            if dps:
                abilityName = GetByMessageID(GetAbilityNameID(abilityID))
                text = GetByLabel('UI/Inflight/ModuleRacks/Tooltips/DamagePerSecondAbility', abilityName=abilityName, dps=dps)
                self.AddRowWithIconAndText(text=text, texturePath=texturePath)
            self.AddRangesForAbilitySlot(eachSlotID)

    def AddActivityStatus(self):
        pass

    def GetModuleDamage(self, ownerGuid, moduleItemID):
        return KeyVal(moduleDamage=None, repairingModuleDamage=None, repairTimeLeft=None)

    def AddVelocity(self):
        controller = SquadronController()
        velocity = controller.GetSquadronVelocity(self.tubeFlagID)
        if velocity is None:
            return
        text = GetByLabel('UI/Inflight/MetersPerSecond', speed=int(velocity))
        self.AddRowWithIconAndText(text=text, iconID=1389)

    def AddTargetingRange(self):
        iconID = dogma_data.get_attribute_icon_id(const.attributeMaxTargetRange)
        attributeName = dogma_data.get_attribute_display_name(const.attributeMaxTargetRange)
        targetingRange = self.GetEffectiveAttributeValue(self.itemID, const.attributeMaxTargetRange)
        if targetingRange != 0:
            formattedOptimalRange = FmtDist(targetingRange)
            text = '%s: %s' % (attributeName, formattedOptimalRange)
            self.AddRowWithIconAndText(text, iconID=iconID)

    def AddRangesForAbilitySlot(self, abilitySlotID):
        maxRange, falloff, abilityID = GetRangesForAbilitySlot(self.dogmaLocation, self.moduleItemID, self.moduleInfoItem.typeID, abilitySlotID)
        if maxRange > 0:
            self.AddRangeInfo(self.moduleInfoItem.typeID, optimalRange=maxRange, falloff=falloff)

    def AddScanRes(self):
        self.AddAttributeInfoWithAttributeName(itemID=self.itemID, attributeID=const.attributeScanResolution, labelPath='UI/Inflight/ModuleRacks/Tooltips/ScanResolution')

    def AddSignatureRadius(self):
        self.AddAttributeInfoWithAttributeName(itemID=self.itemID, attributeID=const.attributeSignatureRadius, labelPath='UI/Inflight/ModuleRacks/Tooltips/SignatureRadius')

    def AddDamageInfo(self, damage = None):
        numHealthyFighters, damage = self._GetNumHealthyFightersAndDamage()
        if damage and damage < 0.99:
            damageNumber = round((1.0 - damage) * 100)
            hintText = GetByLabel('UI/Inventory/Fighters/SquadronModuleTooltipWitDamage', numFighters=int(numHealthyFighters), damagePercentage=damageNumber)
            self.AddSpacer(height=0, width=0, colSpan=2)
            self.AddLabelMedium(text=hintText, colSpan=self.columns, align=uiconst.CENTERLEFT, cellPadding=self.labelPadding)

    def _GetNumHealthyFightersAndDamage(self):
        if not self.moduleInfoItem.typeID:
            return 0
        damage = self._GetFighterDamage()
        numHealthyFighters = 0
        squadronMaxSize = GetMaxSquadronSize(self.moduleInfoItem.typeID)
        squadronSize = self._GetNumInSquadron()
        for i in xrange(1, squadronMaxSize + 1):
            if i <= squadronSize:
                if i == squadronSize and damage and damage < 0.99:
                    continue
                else:
                    numHealthyFighters += 1

        return (numHealthyFighters, damage)

    def _GetFighterDamage(self):
        if self.tubeFlagID is not None:
            shipFighterState = sm.GetService('fighters').shipFighterState
            tubeStatus = shipFighterState.GetTubeStatus(self.tubeFlagID)
            if tubeStatus.statusID not in TUBE_STATES_INSPACE:
                return
        bp = sm.GetService('michelle').GetBallpark()
        if bp is None:
            return
        damageState = bp.GetDamageState(self.itemID)
        if damageState:
            return damageState[0]
