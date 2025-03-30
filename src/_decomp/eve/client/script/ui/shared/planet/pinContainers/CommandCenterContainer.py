#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\planet\pinContainers\CommandCenterContainer.py
import evetypes
import blue
import localization
from carbon.common.script.util.format import FmtTime, IntToRoman
from carbonui import TextAlign, uiconst
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.util.color import Color
from carbonui.util.various_unsorted import SortListOfTuples
from eve.client.script.ui.control import eveLabel, eveScroll
from carbonui.button.group import ButtonGroup
from eve.client.script.ui.control.clickableboxbar import ClickableBoxBar
from eve.client.script.ui.control.entries.item import Item
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from eve.client.script.ui.control.gauge import Gauge, GaugeMultiValue
from eve.client.script.ui.shared.planet import planetCommon as planetCommonUI
from eve.client.script.ui.shared.planet.pinContainers.BasePinContainer import CaptionAndSubtext
from eve.client.script.ui.shared.planet.pinContainers.StorageFacilityContainer import StorageFacilityContainer
from eve.common.lib import appConst as const
from eve.common.script.util import planetCommon
from eve.common.script.util.eveFormat import FmtISK
from eveexceptions import UserError

class CommandCenterContainer(StorageFacilityContainer):
    default_name = 'CommandCenterContainer'
    INFO_CONT_HEIGHT = 110
    panelIDs = [planetCommonUI.PANEL_UPGRADE, planetCommonUI.PANEL_LAUNCH] + StorageFacilityContainer.panelIDs

    def _GetInfoCont(self):
        self.storageGauge = Gauge(parent=self.infoContLeft, value=0.0, color=planetCommonUI.PLANET_COLOR_STORAGE, label=localization.GetByLabel('UI/PI/Common/Capacity'), align=uiconst.TOTOP, padding=(0, 0, 10, 4))
        self.launchTimeTxt = CaptionAndSubtext(parent=self.infoContLeft, caption=localization.GetByLabel('UI/PI/Common/NextLaunchTime'), align=uiconst.TOTOP)
        self.cooldownTimer = CaptionAndSubtext(parent=self.infoContLeft, caption=localization.GetByLabel('UI/PI/Common/NextTransferAvailable'), align=uiconst.TOTOP)
        self.cpuGauge = Gauge(parent=self.infoContRight, value=0.0, color=planetCommonUI.PLANET_COLOR_CPU, align=uiconst.TOTOP, padding=(0, 0, 10, 4))
        self.powerGauge = Gauge(parent=self.infoContRight, value=0.0, color=planetCommonUI.PLANET_COLOR_POWER, align=uiconst.TOTOP, padding=(0, 0, 10, 4))
        self.upgradeLevelGauge = Gauge(parent=self.infoContRight, value=self._GetUpgradeLevelGaugeValue(), color=planetCommonUI.PLANET_COLOR_CURRLEVEL, backgroundColor=Color.GetGrayRGBA(0.5, 0.5), label=localization.GetByLabel('UI/PI/Common/UpgradeLevel'), align=uiconst.TOTOP, padding=(0, 0, 10, 4))
        self.upgradeLevelGauge.ShowMarkers([0.167,
         0.333,
         0.5,
         0.667,
         0.833], color=Color.BLACK)

    def _UpdateInfoCont(self):
        nextLaunchTime = self.pin.GetNextLaunchTime()
        if nextLaunchTime is not None and nextLaunchTime > blue.os.GetWallclockTime():
            nextLaunchTime = FmtTime(nextLaunchTime - blue.os.GetWallclockTime())
        else:
            nextLaunchTime = localization.GetByLabel('UI/Common/Now')
        self.launchTimeTxt.SetSubtext(nextLaunchTime)
        self.storageGauge.SetValue(float(self.pin.capacityUsed) / self.pin.GetCapacity())
        text = localization.GetByLabel('UI/PI/Common/StorageUsed', capacityUsed=self.pin.capacityUsed, capacityMax=self.pin.GetCapacity())
        if not self.pin.GetCapacityRemaining():
            text = '<color=red>%s</color>' % text
        self.storageGauge.SetSubText(text)
        colony = sm.GetService('planetUI').GetCurrentPlanet().GetColony(self.pin.ownerID)
        if colony is None or colony.colonyData is None:
            raise RuntimeError('Unable to find colony to update info container')
        cpuUsage = colony.colonyData.GetColonyCpuUsage()
        cpuSupply = colony.colonyData.GetColonyCpuSupply()
        if cpuSupply > 0:
            percentage = min(1.0, float(cpuUsage) / cpuSupply)
        else:
            percentage = 0.0
        self.cpuGauge.SetValue(percentage)
        self.cpuGauge.SetText(localization.GetByLabel('UI/PI/Common/CPUPercentage', usedPercentage=percentage * 100))
        self.cpuGauge.SetSubText(localization.GetByLabel('UI/PI/Common/CPUUsed', teraFlopsUsed=int(cpuUsage), teraFlopsMax=cpuSupply))
        powerUsage = colony.colonyData.GetColonyPowerUsage()
        powerSupply = colony.colonyData.GetColonyPowerSupply()
        if powerSupply > 0:
            percentage = min(1.0, float(powerUsage) / powerSupply)
        else:
            percentage = 0.0
        self.powerGauge.SetValue(percentage)
        self.powerGauge.SetText(localization.GetByLabel('UI/PI/Common/PowerPercentage', usedPercentage=percentage * 100))
        self.powerGauge.SetSubText(localization.GetByLabel('UI/PI/Common/PowerUsed', megaWattsUsed=int(powerUsage), megaWattsMax=powerSupply))
        self.upgradeLevelGauge.SetValue(self._GetUpgradeLevelGaugeValue())
        if self.pin.lastRunTime is None or self.pin.lastRunTime <= blue.os.GetWallclockTime():
            self.cooldownTimer.SetSubtext(localization.GetByLabel('UI/Common/Now'))
        else:
            self.cooldownTimer.SetSubtext(FmtTime(self.pin.lastRunTime - blue.os.GetWallclockTime()))

    def _GetUpgradeLevelGaugeValue(self):
        currLevel = self.planetUISvc.planet.GetCommandCenterLevel(session.charid)
        return float(currLevel + 1) / (planetCommonUI.PLANET_COMMANDCENTERMAXLEVEL + 1)

    def PanelLaunch(self):
        self.ResetPayloadContents()
        cont = Container(name='panelLaunch', parent=self.actionCont, state=uiconst.UI_HIDDEN)
        topCont = Container(name='topCont', align=uiconst.TOTOP_PROP, height=0.5, parent=cont, padBottom=8)
        bottomCont = Container(name='bottomCont', align=uiconst.TOTOP_PROP, height=0.5, parent=cont, padTop=8)
        self.contentsScroll = eveScroll.Scroll(parent=topCont, name='contentsScroll', hasUnderlay=True)
        manipBtns = [[localization.GetByLabel('UI/PI/Common/Add'), self._AddCommodities, None], [localization.GetByLabel('UI/PI/Common/Remove'), self._RemCommodities, None]]
        self.manipBtns = ButtonGroup(btns=manipBtns, parent=topCont, idx=0, padTop=4)
        self.payloadScroll = eveScroll.Scroll(name='payloadScroll', parent=bottomCont, hasUnderlay=True)
        btns = [[localization.GetByLabel('UI/PI/Common/Launch'), self._DoLaunch, None]]
        self.launchBtns = ButtonGroup(btns=btns, parent=bottomCont, idx=0, padTop=4)
        self.launchCostText = eveLabel.EveLabelMedium(name='launchCostText', parent=bottomCont, align=uiconst.TOBOTTOM, state=uiconst.UI_DISABLED, textAlign=TextAlign.CENTER, padTop=4, idx=0)
        self._ReloadScrolls()
        return cont

    def _ReloadScrolls(self):
        scrolllist = []
        for typeID, amount in self.contentsCommodities.iteritems():
            sortBy = amount
            scrolllist.append((sortBy, GetFromClass(Item, {'label': '<t>%s<t>%s' % (evetypes.GetName(typeID), amount),
              'typeID': typeID,
              'itemID': None,
              'getIcon': True})))

        scrolllist = SortListOfTuples(scrolllist)
        self.contentsScroll.Load(contentList=scrolllist, noContentHint=localization.GetByLabel('UI/PI/Common/StorehouseIsEmpty'), headers=['', localization.GetByLabel('UI/PI/Common/Type'), localization.GetByLabel('UI/Common/Quantity')])
        scrolllist = []
        for typeID, amount in self.payloadCommodities.iteritems():
            sortBy = amount
            scrolllist.append((sortBy, GetFromClass(Item, {'label': '<t>%s<t>%s' % (evetypes.GetName(typeID), amount),
              'typeID': typeID,
              'itemID': None,
              'getIcon': True})))

        scrolllist = SortListOfTuples(scrolllist)
        self.payloadScroll.Load(contentList=scrolllist, noContentHint=localization.GetByLabel('UI/PI/Common/PayloadIsEmpty'), headers=['', localization.GetByLabel('UI/PI/Common/Type'), localization.GetByLabel('UI/Common/Quantity')])
        if self.payloadCommodities:
            self.launchCostText.text = localization.GetByLabel('UI/PI/Common/LaunchCost', iskAmount=FmtISK(self.pin.GetExportTax(self.payloadCommodities)))
            self.launchCostText.Show()
        else:
            self.launchCostText.Hide()

    def _DoLaunch(self, *args):
        if len(self.payloadCommodities) < 1:
            raise UserError('PleaseSelectCommoditiesToLaunch')
        if not self.pin.CanLaunch(self.payloadCommodities):
            raise UserError('CannotLaunchCommandPinNotReady')
        if sm.GetService('planetUI').GetCurrentPlanet().IsInEditMode():
            raise UserError('CannotLaunchInEditMode')
        if len(self.payloadCommodities) == 0:
            return
        sm.GetService('audio').SendUIEvent('msg_pi_spaceports_launch_play')
        try:
            self.planetUISvc.myPinManager.LaunchCommodities(self.pin.id, self.payloadCommodities)
        except UserError:
            self.ResetPayloadContents()
            self._ReloadScrolls()
            raise
        finally:
            self._ToggleButtons()

        self._CancelLaunch()

    def _CancelLaunch(self, *args):
        self.ShowPanel(planetCommonUI.PANEL_LAUNCH)

    def _ToggleButtons(self):
        if self.launchBtns.state == uiconst.UI_HIDDEN:
            self.launchBtns.state = uiconst.UI_PICKCHILDREN
        else:
            self.launchBtns.state = uiconst.UI_HIDDEN
        if self.manipBtns.state == uiconst.UI_HIDDEN:
            self.manipBtns.state = uiconst.UI_PICKCHILDREN
        else:
            self.manipBtns.state = uiconst.UI_HIDDEN

    def ResetPayloadContents(self):
        self.contentsCommodities = self.pin.GetContents()
        self.payloadCommodities = {}

    def _AddCommodities(self, *args):
        selected = self.contentsScroll.GetSelected()
        toMove = {}
        for entry in selected:
            toMove[entry.typeID] = self.contentsCommodities[entry.typeID]

        for typeID, qty in toMove.iteritems():
            self.contentsCommodities[typeID] -= qty
            if self.contentsCommodities[typeID] <= 0:
                del self.contentsCommodities[typeID]
            if typeID not in self.payloadCommodities:
                self.payloadCommodities[typeID] = 0
            self.payloadCommodities[typeID] += qty

        self._ReloadScrolls()

    def _RemCommodities(self, *args):
        selected = self.payloadScroll.GetSelected()
        toMove = {}
        for entry in selected:
            toMove[entry.typeID] = self.payloadCommodities[entry.typeID]

        for typeID, qty in toMove.iteritems():
            self.payloadCommodities[typeID] -= qty
            if self.payloadCommodities[typeID] <= 0:
                del self.payloadCommodities[typeID]
            if typeID not in self.contentsCommodities:
                self.contentsCommodities[typeID] = 0
            self.contentsCommodities[typeID] += qty

        self._ReloadScrolls()

    def _DrawStoredCommoditiesIcons(self):
        pass

    def PanelUpgrade(self):
        cont = Container(parent=self.actionCont, state=uiconst.UI_HIDDEN)
        self.currLevel = self.planetUISvc.planet.GetCommandCenterLevel(session.charid)
        self.newLevel = self.currLevel
        self.currPowerOutput = self.pin.GetPowerOutput()
        self.maxPowerOutput = float(planetCommon.GetPowerOutput(level=planetCommonUI.PLANET_COMMANDCENTERMAXLEVEL))
        self.currCPUOutput = self.pin.GetCpuOutput()
        self.maxCPUOutput = float(planetCommon.GetCPUOutput(level=planetCommonUI.PLANET_COMMANDCENTERMAXLEVEL))
        colorDict = {ClickableBoxBar.COLOR_BELOWMINIMUM: planetCommonUI.PLANET_COLOR_CURRLEVEL,
         ClickableBoxBar.COLOR_SELECTED: planetCommonUI.PLANET_COLOR_UPGRADELEVEL,
         ClickableBoxBar.COLOR_UNSELECTED: Color.GetGrayRGBA(0.4, alpha=0.7),
         ClickableBoxBar.COLOR_ABOVEMAXIMUM: (1.0, 0.0, 0.0, 0.25)}
        boxBarCont = Container(parent=cont, align=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN, height=33)
        upgradeSkill = sm.GetService('skills').GetSkill(const.typeCommandCenterUpgrade)
        upgradeSkillLevel = 0
        if upgradeSkill is not None:
            upgradeSkillLevel = upgradeSkill.effectiveSkillLevel
        boxBar = ClickableBoxBar(align=uiconst.CENTERTOP, width=280, height=16, parent=boxBarCont, numBoxes=6, boxValues=range(0, 6), boxWidth=45, boxHeight=14, readonly=False, backgroundColor=(0.0, 0.0, 0.0, 0.0), colorDict=colorDict, minimumValue=self.currLevel + 1, hintformat=None, maximumValue=upgradeSkillLevel, aboveMaxHint=localization.GetByLabel('UI/PI/Common/UpgradeFailedInsufficientSkill', skillName=evetypes.GetName(const.typeCommandCenterUpgrade)))
        boxBar.OnValueChanged = self.OnUpgradeBarValueChanged
        boxBar.OnAttemptBoxClicked = self.OnUpgradeBarBoxClicked
        self.upgradeText = EveLabelSmall(parent=boxBarCont, text=localization.GetByLabel('UI/PI/Common/NoUpgradeSelected'), align=uiconst.CENTERBOTTOM)
        if self.currLevel == planetCommonUI.PLANET_COMMANDCENTERMAXLEVEL:
            self.upgradeText.SetText(localization.GetByLabel('UI/PI/Common/MaximumUpgradeLevelReached'))
            return cont
        bottomCont = Container(name='bottomCont', align=uiconst.TOTOP, parent=cont, height=50, padTop=16)
        leftBottomCont = Container(name='leftBottomCont', align=uiconst.TOLEFT_PROP, width=0.5, parent=bottomCont)
        rightBottomCont = Container(name='rightBottomCont', align=uiconst.TOLEFT_PROP, width=0.5, parent=bottomCont)
        powerValue = float(self.currPowerOutput) / self.maxPowerOutput
        self.upgradePowerGauge = GaugeMultiValue(parent=leftBottomCont, value=0.0, colors=[planetCommonUI.PLANET_COLOR_POWER, planetCommonUI.PLANET_COLOR_POWERUPGRADE], values=[powerValue, 0.0], label=localization.GetByLabel('UI/PI/Common/PowerOutput'))
        self.upgradePowerGauge.ShowMarker(value=powerValue, color=Color.GetGrayRGBA(0.0, 0.5))
        self.costText = CaptionAndSubtext(parent=leftBottomCont, caption=localization.GetByLabel('UI/Common/Cost'), subtext=localization.GetByLabel('UI/PI/Common/NoCost'), top=42)
        cpuValue = float(self.currCPUOutput) / self.maxCPUOutput
        self.upgradeCPUGauge = GaugeMultiValue(parent=rightBottomCont, colors=[planetCommonUI.PLANET_COLOR_CPU, planetCommonUI.PLANET_COLOR_CPUUPGRADE], values=[cpuValue, 0.0], label=localization.GetByLabel('UI/PI/Common/CpuOutput'))
        self.upgradeCPUGauge.ShowMarker(value=cpuValue, color=Color.GetGrayRGBA(0.0, 0.5))
        btnGroup = ButtonGroup(parent=cont, align=uiconst.TOBOTTOM)
        self.upgradeButton = Button(parent=btnGroup, label=localization.GetByLabel('UI/PI/Common/Upgrade'), func=self._ApplyUpgrade, args=None, enabled=False)
        return cont

    def OnUpgradeBarValueChanged(self, oldValue, newValue):
        self.newLevel = newValue
        txt = localization.GetByLabel('UI/PI/Common/UpgradeFromLevelXToY', currLevel=IntToRoman(self.currLevel + 1), newLevel=IntToRoman(self.newLevel + 1))
        skill = sm.GetService('skills').GetSkill(const.typeCommandCenterUpgrade)
        commandCenterSkillLevel = 0
        if skill is not None:
            commandCenterSkillLevel = skill.effectiveSkillLevel
        if commandCenterSkillLevel < newValue:
            hint = localization.GetByLabel('UI/PI/Common/NeedSkillToUpgrade', skillLevel=IntToRoman(newValue), skillName=evetypes.GetName(const.typeCommandCenterUpgrade))
            txt = localization.GetByLabel('UI/PI/Common/InsufficientSkillForUpgrade')
            self.upgradeButton.Disable()
        else:
            hint = ''
            self.upgradeButton.Enable()
        self.upgradeText.SetText(txt)
        self.upgradeText.hint = hint
        newPowerOutput = planetCommon.GetPowerOutput(self.newLevel)
        self.upgradePowerGauge.SetValue(gaugeNum=1, value=newPowerOutput / self.maxPowerOutput)
        self.upgradePowerGauge.hint = self._GetPowerGaugeHint(newPowerOutput)
        self._SetPowerGaugeSubText(newPowerOutput)
        newCPUOutput = planetCommon.GetCPUOutput(self.newLevel)
        self.upgradeCPUGauge.SetValue(gaugeNum=1, value=newCPUOutput / self.maxCPUOutput)
        self.upgradeCPUGauge.hint = self._GetCPUGaugeHint(newCPUOutput)
        self._SetCPUGaugeSubText(newCPUOutput)
        iskCost = FmtISK(planetCommon.GetUpgradeCost(self.currLevel, self.newLevel), showFractionsAlways=0)
        self.costText.SetSubtext(iskCost)

    def _SetPowerGaugeSubText(self, newPowerOutput):
        diff = newPowerOutput - self.currPowerOutput
        subText = '+%s MW' % diff
        self.upgradePowerGauge.SetSubText(subText)

    def _GetPowerGaugeHint(self, newOutput):
        return localization.GetByLabel('UI/PI/Common/UpgradeHintPower', current=self.currPowerOutput, after=newOutput)

    def _GetCPUGaugeHint(self, newOutput):
        return localization.GetByLabel('UI/PI/Common/UpgradeHintCPU', current=self.currCPUOutput, after=newOutput)

    def _SetCPUGaugeSubText(self, newCPUOutput):
        diff = newCPUOutput - self.currCPUOutput
        subText = localization.GetByLabel('UI/PI/Common/CPUAdded', teraFlops=diff)
        self.upgradeCPUGauge.SetSubText(subText)

    def OnUpgradeBarBoxClicked(self, oldValue, newValue):
        return True

    def _ApplyUpgrade(self, *args):
        self.planetUISvc.planet.UpgradeCommandCenter(self.pin.id, self.newLevel)
        sm.GetService('audio').SendUIEvent('msg_pi_upgrade_play')
        self.HideCurrentPanel()
