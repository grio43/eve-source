#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\droneTooltip.py
import dogma.attributes.format as attributeFormat
import eveformat
import evetypes
import log
from carbon.common.script.util.timerstuff import AutoTimer
from dogma.data import get_attribute_display_name, get_attribute
from eve.client.script.ui import eveColor
from eve.client.script.ui.inflight.shipModuleButton.moduleButtonTooltip import ModuleButtonTooltip
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from eve.common.lib import appConst
from fsdBuiltData.common.iconIDs import GetIconFile
from localization import GetByLabel
from utillib import KeyVal

class DroneTooltipWrapper(TooltipBaseWrapper):

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = DroneTooltip(parent=parent, owner=owner, idx=idx)
        return self.tooltipPanel


class DroneFittingTooltipWrapper(TooltipBaseWrapper):

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = DroneFittingTooltip(parent=parent, owner=owner, idx=idx)
        return self.tooltipPanel


class DroneTooltip(ModuleButtonTooltip):
    infoFunctionNames = {appConst.groupMiningDrone: 'AddMiningDroneInfo'}

    def LoadTooltip(self):
        if not self.owner:
            return
        itemIDs = self.owner.sr.node.itemIDs
        if not itemIDs:
            return
        self.moduleItemID = list(itemIDs)[0]
        self.ownerGuid = 'Drones'
        if not self.moduleItemID:
            return
        self.dogmaLocation = self.GetDogmaLocation()
        self.moduleInfoItem = self.dogmaLocation.GetDogmaItem(self.moduleItemID)
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

    def GetDogmaLocation(self):
        return sm.GetService('clientDogmaIM').GetDogmaLocation()

    def GetNumberOfSlaves(self, *args):
        return 1

    def ShouldAddDps(self, *args):
        return True

    def GetDpsDamageTypeInfo(self, itemID, typeID, groupID, charge, numSlaves):
        shipID = self.dogmaLocation.GetCurrentShipID()
        drones = {itemID: 1}
        damage, _ = self.dogmaLocation.GetOptimalDroneDamage2(shipID, drones)
        texturePath = 'res:/UI/Texture/Icons/drones.png'
        return (damage,
         damage,
         texturePath,
         None,
         1)

    def AddActivityStatus(self):
        pass

    def AddCountDownTimes(self, itemID):
        pass

    def GetModuleDamage(self, ownerGuid, moduleItemID):
        return KeyVal(moduleDamage=None, repairingModuleDamage=None, repairTimeLeft=None)

    def AddMiningDroneInfo(self, itemID, chargeInfoItem):
        durationText = self.GetDuration(itemID)
        amount = self.GetEffectiveAttributeValue(itemID, appConst.attributeMiningAmount)
        durationInSec = self.GetEffectiveAttributeValue(itemID, appConst.attributeDuration) / 1000.0
        amountPerSec = amount / durationInSec
        text = GetByLabel('UI/Inflight/ModuleRacks/Tooltips/MiningAmountPerTime2', duration=durationText, amount=amount, amountPerSec=amountPerSec)
        self.AddRowWithIconAndText(text=text, texturePath='res:/ui/texture/icons/23_64_5.png')

    def UpdateToolTips(self):
        try:
            super(DroneTooltip, self).UpdateToolTips()
            self.AddDroneBandwidthUsed()
        except KeyError as e:
            log.LogWarn('Failed to display drone tooltip, keyError e = ', e)

    def GetTypeText(self):
        text = super(DroneTooltip, self).GetTypeText()
        activity = self.owner.GetDroneActivityDescription()
        if activity:
            text += u'<br>{}'.format(eveformat.color(activity, eveColor.SUCCESS_GREEN))
        state = self.owner.GetDroneStateDescription()
        if state:
            text += u'<br>{}'.format(state)
        return text

    def AddDroneBandwidthUsed(self):
        value = self.GetEffectiveAttributeValue(self.moduleItemID, appConst.attributeDroneBandwidthUsed)
        displayName = get_attribute_display_name(appConst.attributeDroneBandwidthUsed)
        text = '%s %s' % (displayName, attributeFormat.GetFormatAndValue(get_attribute(appConst.attributeDroneBandwidthUsed), value))
        texturePath = GetIconFile(attributeFormat.GetIconID(appConst.attributeDroneBandwidthUsed))
        self.AddRowWithIconAndText(text, texturePath)


class DroneFittingTooltip(DroneTooltip):

    def GetDogmaLocation(self):
        return sm.GetService('clientDogmaIM').GetFittingDogmaLocation()
