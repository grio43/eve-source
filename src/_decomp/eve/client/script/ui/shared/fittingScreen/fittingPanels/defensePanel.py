#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\fittingPanels\defensePanel.py
import math
import dogma.const
import dogma.data
from carbon.common.script.util.format import FmtAmt
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.text.settings import check_convert_font_size
from carbonui.uianimations import animations
from carbonui.util.various_unsorted import IsUnder, GetAttrs
from carbonui.window.underlay import WindowUnderlay
from eve.client.script.ui.control.damageGaugeContainers import DamageGaugeContainerFitting
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelMedium, Label
from eve.client.script.ui.shared.fitting.fittingUtil import PASSIVESHIELDRECHARGE, ARMORREPAIRRATEACTIVE, HULLREPAIRRATEACTIVE, SHIELDBOOSTRATEACTIVE, FONTCOLOR_DEFAULT2, GetDefensiveLayersInfo, GetShipAttributeWithDogmaLocation, PANEL_WIDTH_RIGHT
from eve.client.script.ui.shared.fittingScreen.fittingUtil import GetColoredText
from eve.client.script.ui.station.fitting.fittingTooltipUtils import SetFittingTooltipInfo
from eve.client.script.ui.shared.fittingScreen.fittingPanels.basePanel import BaseMenuPanel
from eve.common.lib.appConst import SEC
from inventorycommon.const import fittingFlags, groupArmorRepairUnit, groupFueledArmorRepairer, groupFueledShieldBooster, groupHullRepairUnit, groupShieldBooster
from localization import GetByLabel, GetByMessageID
from carbonui.uicore import uicore
MAXDEFENCELABELWIDTH = 62
MAXDEFENCELABELHEIGHT = 34
ACTIVE_DEFENSES_TOOLTIP_NAME = 'ActiveDefenses'
MILLION = 1000000
SECONDS_DAY = 86400
ICON_SIZE = 20
resAttributeIDs = ((dogma.const.attributeEmDamageResonance, 'ResistanceHeaderEM', 'res:/UI/Texture/classes/Fitting/StatsIcons/EMResistance.png'),
 (dogma.const.attributeThermalDamageResonance, 'ResistanceHeaderThermal', 'res:/UI/Texture/classes/Fitting/StatsIcons/thermalResistance.png'),
 (dogma.const.attributeKineticDamageResonance, 'ResistanceHeaderKinetic', 'res:/UI/Texture/classes/Fitting/StatsIcons/kineticResistance.png'),
 (dogma.const.attributeExplosiveDamageResonance, 'ResistanceHeaderExplosive', 'res:/UI/Texture/classes/Fitting/StatsIcons/explosiveResistance.png'))
rowsInfo = [('UI/Common/Shield', 'shield', 'res:/UI/Texture/classes/Fitting/StatsIcons/shieldHP.png', 'UI/Fitting/FittingWindow/ShieldHPAndRecharge'), ('UI/Common/Armor', 'armor', 'res:/UI/Texture/classes/Fitting/StatsIcons/armorHP.png', 'UI/Common/Armor'), ('UI/Fitting/Structure', 'structure', 'res:/UI/Texture/classes/Fitting/StatsIcons/structureHP.png', 'UI/Fitting/Structure')]
DATASET_FOR_REPAIRERS = {ARMORREPAIRRATEACTIVE: ('UI/Fitting/FittingWindow/ArmorRepairRate',
                         (groupArmorRepairUnit, groupFueledArmorRepairer),
                         dogma.const.attributeArmorDamageAmount,
                         dogma.const.attributeChargedArmorDamageMultiplier,
                         'res:/UI/Texture/classes/Fitting/StatsIcons/armorRepairRate.png'),
 HULLREPAIRRATEACTIVE: ('UI/Fitting/FittingWindow/HullRepairRate',
                        (groupHullRepairUnit,),
                        dogma.const.attributeStructureDamageAmount,
                        None,
                        'res:/UI/Texture/classes/Fitting/StatsIcons/hullRepairRate.png'),
 SHIELDBOOSTRATEACTIVE: ('UI/Fitting/FittingWindow/ShieldBoostRate',
                         (groupShieldBooster, groupFueledShieldBooster),
                         dogma.const.attributeShieldBonus,
                         None,
                         'res:/UI/Texture/classes/Fitting/StatsIcons/shieldBoostRate.png'),
 PASSIVESHIELDRECHARGE: ('UI/Fitting/FittingWindow/PassiveShieldRecharge', None, None, None, 'res:/UI/Texture/classes/Fitting/StatsIcons/passiveShieldRecharge.png')}

class DefensePanel(BaseMenuPanel):
    col1Width = 90

    def ApplyAttributes(self, attributes):
        BaseMenuPanel.ApplyAttributes(self, attributes)

    def LoadPanel(self, initialLoad = False):
        self.Flush()
        self.ResetStatsDicts()
        self.display = True
        tRow = Container(name='topRow', parent=self, align=uiconst.TOTOP, height=28, padTop=5, padLeft=3)
        self.AddBestRepairPicker(tRow)
        self.AddColumnHeaderIcons(tRow)
        for idx in xrange(len(rowsInfo)):
            self.AddRow(idx)

        BaseMenuPanel.FinalizePanelLoading(self, initialLoad)

    def AddBestRepairPicker(self, tRow):
        self.bestRepairPickerPanel = None
        bestPar = Container(name='bestPar', parent=tRow, align=uiconst.TOPLEFT, height=32, width=self.col1Width, state=uiconst.UI_NORMAL)
        bestPar.OnClick = self.ExpandBestRepair
        SetFittingTooltipInfo(targetObject=bestPar, tooltipName=ACTIVE_DEFENSES_TOOLTIP_NAME)
        self.expandIcon = Icon(name='expandIcon', icon='ui_38_16_229', parent=bestPar, state=uiconst.UI_DISABLED, align=uiconst.TOPLEFT, rotation=math.pi, pos=(-5, -5, 0, 0))
        numPar = Container(name='numPar', parent=bestPar, pos=(0, 0, 11, 11), align=uiconst.BOTTOMLEFT, state=uiconst.UI_DISABLED)
        numLabel = EveLabelMedium(text='', parent=numPar, atop=-1, state=uiconst.UI_DISABLED, align=uiconst.CENTER, shadowOffset=(0, 0))
        Fill(parent=numPar, color=(0.0, 0.0, 0.0, 0.5))
        self.activeBestRepairNumLabel = numLabel
        icon = Icon(parent=bestPar, state=uiconst.UI_DISABLED, width=ICON_SIZE, height=ICON_SIZE, align=uiconst.CENTERLEFT)
        statusLabel = Label(name='statusLabel', text='', parent=bestPar, left=icon.left + icon.width, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT)
        statusLabel.SetRightAlphaFade(fadeEnd=self.col1Width - 20, maxFadeWidth=15)
        self.activeBestRepairLabel = statusLabel
        self.activeBestRepairParent = bestPar
        self.activeBestRepairIcon = icon

    def AddColumnHeaderIcons(self, tRow):
        step = (PANEL_WIDTH_RIGHT - self.col1Width - 10) / 4.0
        left = self.col1Width
        counter = 0
        for attributeID, tooltipName, texturePath in resAttributeIDs:
            contLeft = left + int(counter * step)
            cont = Container(parent=tRow, align=uiconst.TOLEFT_NOPUSH, pos=(contLeft,
             0,
             int(step),
             0))
            icon = Icon(parent=cont, pos=(-6, 0, 24, 24), idx=0, hint=dogma.data.get_attribute_display_name(attributeID), icon=texturePath, align=uiconst.CENTER)
            SetFittingTooltipInfo(icon, tooltipName=tooltipName, includeDesc=True)
            counter += 1

    def AddRow(self, idx):
        labelPath, what, iconNo, labelHintPath = rowsInfo[idx]
        rowName = 'row_%s' % what
        row = Container(name='row_%s' % rowName, parent=self, align=uiconst.TOTOP, height=32, padLeft=3)
        mainIcon = Icon(icon=iconNo, parent=row, pos=(0,
         0,
         ICON_SIZE,
         ICON_SIZE), ignoreSize=True, align=uiconst.CENTERLEFT)
        mainIcon.hint = GetByLabel(labelPath)
        statusLabel = Label(text='', parent=row, left=mainIcon.left + mainIcon.width, state=uiconst.UI_NORMAL, align=uiconst.CENTERLEFT, width=62)
        statusLabel.hint = GetByLabel(labelHintPath)
        self.statsLabelsByIdentifier[what] = statusLabel
        dmgContainer = Container(parent=row, name='dmgContainer', left=self.col1Width)
        gaugeCont = DamageGaugeContainerFitting(parent=dmgContainer)
        self.statsContsByIdentifier[what] = gaugeCont

    def SetEffectiveHpHeader(self):
        effectiveHpInfo = self.controller.GetEffectiveHp()
        text = GetByLabel('UI/Fitting/FittingWindow/ColoredEffectiveHp', effectiveHp=int(effectiveHpInfo.value))
        coloredText = GetColoredText(isBetter=effectiveHpInfo.isBetterThanBefore, text=text)
        self.SetStatusText(coloredText)

    def UpdateDefensePanel(self):
        self.SetEffectiveHpHeader()
        allDefensiveLayersInfo = GetDefensiveLayersInfo(self.controller)
        for whatLayer, layerInfo in allDefensiveLayersInfo.iteritems():
            hpInfo = layerInfo.hpInfo
            isRechargable = layerInfo.isRechargable
            layerResistancesInfo = layerInfo.resistances
            if not hpInfo:
                continue
            self.SetDefenseLayerText(hpInfo, whatLayer, isRechargable)
            self.UpdateGaugesForLayer(layerResistancesInfo, whatLayer)

    def UpdateGaugesForLayer(self, layerResistancesInfo, whatLayer):
        dmgGaugeCont = self.statsContsByIdentifier.get(whatLayer, None)
        for dmgType, valueInfo in layerResistancesInfo.iteritems():
            value = valueInfo.value
            if self.state != uiconst.UI_HIDDEN and dmgGaugeCont:
                text = GetByLabel('UI/Fitting/FittingWindow/ColoredResistanceLabel', number=100 - int(value * 100))
                coloredText = GetColoredText(isBetter=valueInfo.isBetterThanBefore, text=text)
                attributeInfo = dogma.data.get_attribute(valueInfo.attributeID)
                tooltipTitleID = attributeInfo.tooltipTitleID
                if tooltipTitleID:
                    tooltipText = GetByMessageID(attributeInfo.tooltipTitleID)
                else:
                    tooltipText = dogma.data.get_attribute_display_name(valueInfo.attributeID)
                info = {'value': 1.0 - value,
                 'valueText': coloredText,
                 'text': tooltipText,
                 'dmgType': dmgType}
                dmgGaugeCont.UpdateGauge(info, animate=True)

    def SetDefenseLayerText(self, statusInfo, what, isRechargable):
        label = self.statsLabelsByIdentifier.get(what, None)
        if not label:
            return
        hpText = self._GetFormattedValue(statusInfo.value)
        text = None
        if isRechargable:
            rechargeTimeInfo = self.controller.GetRechargeRate()
            rechargeValue = rechargeTimeInfo.value
            if rechargeValue < SECONDS_DAY * SEC:
                text = GetByLabel('UI/Fitting/FittingWindow/ColoredHitpointsAndRechargeTime2', hp=hpText, rechargeTime=int(rechargeValue * 0.001), startColorTag1='', startColorTag2='', endColorTag='')
        if text is None:
            text = GetByLabel('UI/Fitting/FittingWindow/ColoredHp2', hp=hpText)
        coloredText = GetColoredText(isBetter=statusInfo.isBetterThanBefore, text=text)
        maxTextHeight = MAXDEFENCELABELHEIGHT
        maxTextWidth = MAXDEFENCELABELWIDTH
        textWidth, textHeight = label.MeasureTextSize(coloredText)
        fontsize = check_convert_font_size(label.default_fontsize)
        lineSpacing = -0.2
        while textWidth > maxTextWidth or textHeight > maxTextHeight:
            fontsize -= 1
            textWidth, textHeight = label.MeasureTextSize(coloredText, fontsize=fontsize, lineSpacing=lineSpacing)

        label.fontsize = fontsize
        label.lineSpacing = lineSpacing
        label.text = coloredText

    def _GetFormattedValue(self, value):
        if value > 100 * MILLION:
            fmt = 'sn'
        else:
            fmt = 'ln'
        valueText = FmtAmt(int(value), fmt=fmt)
        return valueText

    def ExpandBestRepair(self, *args):
        if self.bestRepairPickerPanel is not None:
            self.PickBestRepair(None)
            return
        self.sr.bestRepairPickerCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEUP, self.OnGlobalMouseUp_BestRepair)
        bestRepairParent = self.activeBestRepairParent
        l, t, w, h = bestRepairParent.GetAbsolute()
        bestRepairPickerPanel = Container(parent=uicore.desktop, name='bestRepairPickerPanel', align=uiconst.TOPLEFT, width=150, height=100, left=l, top=t + h, state=uiconst.UI_NORMAL, idx=0, clipChildren=1)
        subpar = Container(parent=bestRepairPickerPanel, name='subpar', align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN, pos=(0, 0, 0, 0))
        active = settings.user.ui.Get('activeBestRepair', PASSIVESHIELDRECHARGE)
        top = 0
        mw = 32
        for flag in (ARMORREPAIRRATEACTIVE,
         HULLREPAIRRATEACTIVE,
         PASSIVESHIELDRECHARGE,
         SHIELDBOOSTRATEACTIVE):
            hintPath, _, _, _, iconNo = self.GetDataSetForRepairers(flag)
            hint = GetByLabel(hintPath)
            entry = Container(name='entry', parent=subpar, align=uiconst.TOTOP, height=32, state=uiconst.UI_NORMAL)
            icon = Icon(icon=iconNo, parent=entry, state=uiconst.UI_DISABLED, pos=(2,
             0,
             ICON_SIZE,
             ICON_SIZE), ignoreSize=True, align=uiconst.CENTERLEFT)
            label = Label(text=hint, parent=entry, left=icon.left + icon.width + 2, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT)
            entry.OnClick = (self.PickBestRepair, entry)
            entry.OnMouseEnter = (self.OnMouseEnterBestRepair, entry)
            entry.bestRepairFlag = flag
            entry.sr.hilite = Fill(parent=entry, state=uiconst.UI_HIDDEN)
            if active == flag:
                Fill(parent=entry, color=(1.0, 1.0, 1.0, 0.125))
            top += 32
            mw = max(label.textwidth + label.left + 6, mw)

        bestRepairPickerPanel.width = mw
        bestRepairPickerPanel.height = 32
        bestRepairPickerPanel.opacity = 0.0
        WindowUnderlay(bgParent=bestRepairPickerPanel)
        self.bestRepairPickerPanel = bestRepairPickerPanel
        animations.MorphScalar(bestRepairPickerPanel, 'height', endVal=top, duration=0.25)
        animations.FadeIn(bestRepairPickerPanel, duration=0.25)
        self.RotateExpandIconDown()

    def RotateExpandIconDown(self):
        animations.MorphScalar(self.expandIcon, 'rotation', self.expandIcon.rotation, 0, duration=0.25, curveType=uiconst.ANIM_LINEAR)

    def RotateExpandIconUp(self):
        animations.MorphScalar(self.expandIcon, 'rotation', self.expandIcon.rotation, math.pi, duration=0.25, curveType=uiconst.ANIM_LINEAR)

    def UpdateBestRepair(self):
        if not self.panelLoaded:
            return
        activeRepairLabel = self.activeBestRepairLabel
        activeBestRepairParent = self.activeBestRepairParent
        activeBestRepairNumLabel = self.activeBestRepairNumLabel
        activeBestRepairIcon = self.activeBestRepairIcon
        if not activeRepairLabel:
            return
        activeBestRepair = settings.user.ui.Get('activeBestRepair', PASSIVESHIELDRECHARGE)
        if activeBestRepair == PASSIVESHIELDRECHARGE:
            SetFittingTooltipInfo(activeBestRepairParent, ACTIVE_DEFENSES_TOOLTIP_NAME)
            return self.UpdatePassiveShieldRecharge()
        hintPath, groupIDs, repairAttributeID, chargeMultiplierAttributeID, iconNum = self.GetDataSetForRepairers(activeBestRepair)
        hint = GetByLabel(hintPath)
        activeBestRepairParent.hint = hint
        modulesAndCharges = self.FindModulesAndChargesByGroups(groupIDs)
        if modulesAndCharges:
            totalHpPerSec = self.GetTotalHpPerSec(modulesAndCharges, repairAttributeID, chargeMultiplierAttributeID)
            if totalHpPerSec:
                text = GetByLabel('UI/Fitting/FittingWindow/ColoredPassiveRepairRate', hpPerSec=totalHpPerSec)
                activeRepairLabel.text = text
            else:
                activeRepairLabel.text = 0
            SetFittingTooltipInfo(activeBestRepairParent, ACTIVE_DEFENSES_TOOLTIP_NAME)
            text = GetByLabel('UI/Fitting/FittingWindow/ColoredBestRepairNumber', numberOfModules=len(modulesAndCharges))
            activeBestRepairNumLabel.text = text
            activeBestRepairNumLabel.bold = True
            activeBestRepairNumLabel.parent.state = uiconst.UI_DISABLED
        else:
            activeRepairLabel.text = GetByLabel('UI/Fitting/FittingWindow/NoModule')
            activeBestRepairNumLabel.text = GetByLabel('UI/Fitting/FittingWindow/NoModuleNumber')
            SetFittingTooltipInfo(activeBestRepairParent, ACTIVE_DEFENSES_TOOLTIP_NAME, extraHeader=GetByLabel('UI/Fitting/FittingWindow/NoModule'))
            activeBestRepairNumLabel.parent.state = uiconst.UI_DISABLED
        activeBestRepairIcon.LoadIcon(iconNum, ignoreSize=True)

    def FindModulesAndChargesByGroups(self, groupIDs):
        modulesAndCharges = []
        modulesByFlagID = self.controller.GetFittedModulesByFlagID()
        for eachFlag in fittingFlags:
            module = modulesByFlagID.get((eachFlag, False), None)
            if not module:
                continue
            if module.groupID not in groupIDs:
                continue
            charge = modulesByFlagID.get((eachFlag, True), None)
            modulesAndCharges.append((module, charge))

        return modulesAndCharges

    def GetDataSetForRepairers(self, activeBestRepair):
        return DATASET_FOR_REPAIRERS[activeBestRepair]

    def GetTextWithColor(self, color, text):
        activeRepairText = '<color=%s>' % color
        activeRepairText += text
        activeRepairText += '</color>'
        return activeRepairText

    def UpdatePassiveShieldRecharge(self):
        passiveRechargeRateInfo = self.controller.GetPassiveRechargeRate()
        activeRepairText = GetByLabel('UI/Fitting/FittingWindow/ColoredPassiveRepairRate', hpPerSec=int(passiveRechargeRateInfo.value))
        coloredText = GetColoredText(isBetter=passiveRechargeRateInfo.isBetterThanBefore, text=activeRepairText)
        self.activeBestRepairLabel.text = coloredText
        self.activeBestRepairParent.hint = GetByLabel('UI/Fitting/FittingWindow/PassiveShieldRecharge')
        self.activeBestRepairNumLabel.parent.state = uiconst.UI_HIDDEN
        _, _, _, _, shieldIconID = self.GetDataSetForRepairers(PASSIVESHIELDRECHARGE)
        self.activeBestRepairIcon.LoadIcon(shieldIconID, ignoreSize=True)

    def GetTotalHpPerSec(self, modulesAndCharges, repairAttributeID, chargeMultiplierAttributeID = None):
        hpsAndDurations = []
        totalPerSec = 0

        def GetHpPerSec(hpValue, durationValue):
            return hpValue / (durationValue / 1000.0)

        for module, charges in modulesAndCharges:
            dogmaItem = self.dogmaLocation.dogmaItems.get(module.itemID, None)
            include = self.IncludeModuleInHpCalculation(dogmaItem)
            if not include:
                continue
            shipID = self.dogmaLocation.GetCurrentShipID()
            if dogmaItem and dogmaItem.locationID == shipID:
                duration = self.dogmaLocation.GetAccurateAttributeValue(dogmaItem.itemID, dogma.const.attributeDuration)
                hp = self.dogmaLocation.GetAccurateAttributeValue(dogmaItem.itemID, repairAttributeID)
                multiplier = 1.0
                if charges and chargeMultiplierAttributeID:
                    multiplier = self.dogmaLocation.GetAccurateAttributeValue(dogmaItem.itemID, chargeMultiplierAttributeID)
                hp *= multiplier
                totalPerSec += GetHpPerSec(hp, duration)
                hpsAndDurations.append((hp, duration))
            else:
                duration = self.dogmaLocation.dogmaStaticMgr.GetTypeAttribute2(module.typeID, dogma.const.attributeDuration)
                hp = self.dogmaLocation.dogmaStaticMgr.GetTypeAttribute2(module.typeID, repairAttributeID)
                if charges:
                    multiplier = self.dogmaLocation.dogmaStaticMgr.GetTypeAttribute2(module.typeID, chargeMultiplierAttributeID)
                    hp *= multiplier
                totalPerSec += GetHpPerSec(hp, duration)

        return totalPerSec

    def IncludeModuleInHpCalculation(self, module):
        if not sm.GetService('fittingSvc').IsShipSimulated():
            return True
        if not module:
            return False
        typeEffectInfo = sm.GetService('ghostFittingSvc').GetDefaultAndOverheatEffect(module.typeID)
        if not typeEffectInfo.defaultEffect or not typeEffectInfo.isActivatable:
            return True
        if not module.IsActive():
            return False
        return True

    def GetShipAttribute(self, attributeID):
        dogmaLocation = self.controller.GetDogmaLocation()
        shipID = dogmaLocation.GetCurrentShipID()
        return GetShipAttributeWithDogmaLocation(dogmaLocation, shipID, attributeID)

    def OnGlobalMouseUp_BestRepair(self, fromwhere, *etc):
        if self.bestRepairPickerPanel:
            if uicore.uilib.mouseOver == self.bestRepairPickerPanel or IsUnder(fromwhere, self.bestRepairPickerPanel) or fromwhere == self.activeBestRepairParent:
                import log
                log.LogInfo('Combo.OnGlobalClick Ignoring all clicks from comboDropDown')
                return 1
        if self.bestRepairPickerPanel and not self.bestRepairPickerPanel.destroyed:
            self.bestRepairPickerPanel.Close()
        self.bestRepairPickerPanel = None
        if self.sr.bestRepairPickerCookie:
            uicore.event.UnregisterForTriuiEvents(self.sr.bestRepairPickerCookie)
        self.sr.bestRepairPickerCookie = None
        self.RotateExpandIconUp()
        return 0

    def PickBestRepair(self, entry):
        if entry:
            settings.user.ui.Set('activeBestRepair', entry.bestRepairFlag)
            self.controller.UpdateStats()
        if self.bestRepairPickerPanel and not self.bestRepairPickerPanel.destroyed:
            self.bestRepairPickerPanel.Close()
        self.bestRepairPickerPanel = None
        if self.sr.bestRepairPickerCookie:
            uicore.event.UnregisterForTriuiEvents(self.sr.bestRepairPickerCookie)
        self.sr.bestRepairPickerCookie = None
        self.RotateExpandIconUp()

    def OnMouseEnterBestRepair(self, entry):
        for each in entry.parent.children:
            if GetAttrs(each, 'sr', 'hilite'):
                each.sr.hilite.state = uiconst.UI_HIDDEN

        entry.sr.hilite.state = uiconst.UI_DISABLED
