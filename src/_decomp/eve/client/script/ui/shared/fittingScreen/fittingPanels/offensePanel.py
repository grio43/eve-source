#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\fittingPanels\offensePanel.py
import eveui
import uthread
from carbonui import const as uiconst
from carbonui.primitives.sprite import Sprite
from dogma.attributes.format import GetFormattedAttributeAndValueAllowZero
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.shared.fittingScreen.fittingPanels.basePanel import BaseMenuPanel
from eve.client.script.ui.shared.fittingScreen.fittingUtil import GetColoredText
from eve.client.script.ui.station.fitting.fittingTooltipUtils import SetFittingTooltipInfo, GetTooltipPathFromTooltipName
from fighters import GetAbilityNameID
from localization import GetByLabel, GetByMessageID
from shipfitting.fittingDogmaLocationUtil import GetAllDpsInfo
import eveicon

class OffensePanel(BaseMenuPanel):
    default_iconSize = 20
    damageStats = (('totalDps', 'res:/UI/Texture/classes/Fitting/StatsIcons/turretDPS.png', ''), ('alphaStrike', 'res:/UI/Texture/classes/Fitting/StatsIcons/alphaStrike.png', 'AlpaStrike'))

    def ApplyAttributes(self, attributes):
        BaseMenuPanel.ApplyAttributes(self, attributes)

    def LoadPanel(self, initialLoad = False):
        self.Flush()
        self.ResetStatsDicts()
        self.display = True
        parentGrid = self.GetValueParentGrid()
        for dps, texturePath, tooltipName in self.damageStats:
            c = self.GetValueCont(self.iconSize)
            parentGrid.AddCell(cellObject=c)
            icon = self._AddIcon(c, texturePath)
            label = EveLabelMedium(text='', parent=c, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT)
            self.statsLabelsByIdentifier[dps] = label
            self.statsIconsByIdentifier[dps] = icon
            self.statsContsByIdentifier[dps] = c
            if dps == 'totalDps':
                c.LoadTooltipPanel = self.LoadDpsTooltipPanel
            else:
                SetFittingTooltipInfo(targetObject=c, tooltipName=tooltipName)

        BaseMenuPanel.FinalizePanelLoading(self, initialLoad)

    def UpdateOffenseStats(self):
        uthread.new(self._UpdateOffenseStats)

    @eveui.skip_if_destroyed
    def _UpdateOffenseStats(self):
        if not self.IsCurrentShipReady():
            return
        try:
            totalDpsInfo = self.controller.GetTotalDps()
        except KeyError:
            self.SetStatusText('-')
            self.SetLabel('totalDps', '-')
            self.SetLabel('alphaStrike', '-')
            return

        totalDps = totalDpsInfo.value
        totalDpsText = GetByLabel('UI/Fitting/FittingWindow/DpsLabel', dps=totalDps)
        totalDpsColoredText = GetColoredText(isBetter=totalDpsInfo.isBetterThanBefore, text=totalDpsText)
        self.SetStatusText(totalDpsColoredText)
        if self.destroyed:
            return
        totalDpsWithReloadInfo = self.controller.GetTotalDpsWithReload()
        totalDpsWithReload = totalDpsWithReloadInfo.value
        if totalDpsWithReload and totalDpsWithReload != totalDps:
            withReload = GetByLabel('UI/Fitting/FittingWindow/DpsLabel', dps=totalDpsWithReload)
            withReloadColoredText = GetColoredText(isBetter=totalDpsInfo.isBetterThanBefore, text=withReload)
            totalDpsColoredText += ' (%s)' % withReloadColoredText
        self.SetLabel('totalDps', totalDpsColoredText)
        alphaStrikeInfo = self.controller.GetAlphaStrike()
        alphaText = GetFormattedAttributeAndValueAllowZero(const.attributeDamage, int(round(alphaStrikeInfo.value))).value
        alphaStrikeColoredText = GetColoredText(isBetter=alphaStrikeInfo.isBetterThanBefore, text=alphaText)
        self.SetLabel('alphaStrike', alphaStrikeColoredText)

    def LoadDpsTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric3ColumnTemplate()
        tooltipPanel.cellSpacing = (10, 0)
        shipItem = self.controller.dogmaLocation.GetShip()
        if not shipItem:
            return
        isStructure = shipItem.categoryID == const.categoryStructure
        labelPaths = GetTooltipPathFromTooltipName('DamagePerSecond')
        headerLabelPath, descriptionLabelPath = labelPaths
        tooltipPanel.AddLabelMedium(text=GetByLabel(headerLabelPath), bold=True, colSpan=tooltipPanel.columns)
        tooltipPanel.AddLabelMedium(text=GetByLabel(descriptionLabelPath), align=uiconst.TOPLEFT, wrapWidth=200, colSpan=tooltipPanel.columns, color=(0.6, 0.6, 0.6, 1))
        itemID = self.dogmaLocation.GetCurrentShipID()
        dpsInfo = GetAllDpsInfo(itemID, self.dogmaLocation)
        if dpsInfo.turretDps:
            self._AddSpacer(tooltipPanel)
            self._AddIcon(tooltipPanel, 'res:/UI/Texture/classes/Fitting/StatsIcons/turretDPS.png')
            label = GetByLabel('UI/Fitting/FittingWindow/TurretsDps')
            tooltipPanel.AddLabelMedium(text=label, align=uiconst.CENTERLEFT, bold=True)
            self._AddDpsText(tooltipPanel, dpsInfo.turretDps, dpsInfo.turretDpsWithReload)
        if dpsInfo.missileDps:
            self._AddSpacer(tooltipPanel)
            self._AddIcon(tooltipPanel, 'res:/UI/Texture/classes/Fitting/StatsIcons/missileDPS.png')
            label = GetByLabel('UI/Fitting/FittingWindow/MissilesDps')
            tooltipPanel.AddLabelMedium(text=label, align=uiconst.CENTERLEFT, bold=True)
            self._AddDpsText(tooltipPanel, dpsInfo.missileDps, dpsInfo.missileDpsWithReload)
        if dpsInfo.dotDps:
            self._AddSpacer(tooltipPanel)
            self._AddIcon(tooltipPanel, eveicon.damage_over_time)
            label = GetByLabel('UI/Fitting/FittingWindow/DotDps')
            tooltipPanel.AddLabelMedium(text=label, align=uiconst.CENTERLEFT, bold=True)
            self._AddDpsText(tooltipPanel, dpsInfo.dotDps, None)
        if dpsInfo.droneDps:
            self._AddSpacer(tooltipPanel)
            self._AddIcon(tooltipPanel, 'res:/UI/Texture/classes/Fitting/StatsIcons/droneDPS.png')
            label = GetByLabel('UI/Fitting/FittingWindow/DronesDps')
            tooltipPanel.AddLabelMedium(text=label, align=uiconst.CENTERLEFT, bold=True)
            self._AddDpsText(tooltipPanel, dpsInfo.droneDps, None)
        if dpsInfo.fighterDps:
            self._AddSpacer(tooltipPanel)
            self._AddIcon(tooltipPanel, 'res:/UI/Texture/classes/Fitting/StatsIcons/droneDPS.png')
            label = GetByLabel('UI/Fitting/FittingWindow/StandardAttack')
            tooltipPanel.AddLabelMedium(text=label, align=uiconst.CENTERLEFT, bold=True)
            standardDps = sum(dpsInfo.dpsByPrimaryAbilityID.values())
            self._AddDpsText(tooltipPanel, standardDps, None)
            specialAbilityInfo = []
            for eachAbilityID, eachDps in dpsInfo.dpsBySecondaryAbilityID.iteritems():
                name = GetAbilityNameID(eachAbilityID)
                if eachDps:
                    specialAbilityInfo.append((GetByMessageID(name), eachDps))

            specialAbilityInfo.sort(key=lambda x: x[0])
            for eachName, eachDps in specialAbilityInfo:
                self._AddIcon(tooltipPanel, 'res:/UI/Texture/classes/Fitting/StatsIcons/droneDPS.png')
                tooltipPanel.AddLabelMedium(text=eachName, align=uiconst.CENTERLEFT, bold=True)
                self._AddDpsText(tooltipPanel, eachDps, None)

        if dpsInfo.aoeDps:
            self._AddSpacer(tooltipPanel)
            if isStructure:
                label = GetByLabel('UI/Fitting/FittingWindow/PointDefenseBatteryDps')
            else:
                label = GetByLabel('UI/Fitting/FittingWindow/SmartbombsDps')
            self._AddIcon(tooltipPanel, 'res:/UI/Texture/Icons/26_64_1.png')
            tooltipPanel.AddLabelMedium(text=label, align=uiconst.CENTERLEFT, bold=True)
            self._AddDpsText(tooltipPanel, dpsInfo.aoeDps, None)

    def _AddDpsText(self, tooltipPanel, dps, dpsWithReload):
        turretDpsText, withReload = self._GetDpsText(dps, dpsWithReload)
        tooltipPanel.AddLabelMedium(text=turretDpsText, align=uiconst.CENTERLEFT)
        if withReload:
            tooltipPanel.AddCell()
            tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Fitting/FittingWindow/WithReloadTimeText'), align=uiconst.CENTERLEFT, bold=True)
            tooltipPanel.AddLabelMedium(text=withReload, align=uiconst.TOPLEFT)

    def _GetDpsText(self, dps, dpsWithReload):
        text = GetByLabel('UI/Fitting/FittingWindow/DpsLabel', dps=dps)
        if dpsWithReload and dpsWithReload != dps:
            withReload = GetByLabel('UI/Fitting/FittingWindow/DpsLabel', dps=dpsWithReload)
            withReload = '(%s)' % withReload
        else:
            withReload = None
        return (text, withReload)

    def _AddIcon(self, tooltipPanel, texturePath):
        icon = Sprite(texturePath=texturePath, parent=tooltipPanel, align=uiconst.CENTERLEFT, pos=(3,
         0,
         self.iconSize,
         self.iconSize), state=uiconst.UI_DISABLED)
        return icon

    def _AddSpacer(self, tooltipPanel):
        tooltipPanel.AddSpacer(width=0, height=10)
        tooltipPanel.FillRow()
