#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\shipHud\buffButtons.py
from collections import OrderedDict
from operator import itemgetter
from carbon.common.lib.const import MSEC
import carbonui.const as uiconst
from carbon.common.script.util.timerstuff import AutoTimer
from dbuff.client.uiFormatters import GetDisplayNameAndValue
import eve.client.script.parklife.states as stateConst
import dotWeapons.client.dotClientUtil as dotClientUtil
from eve.client.script.ui.inflight.shipHud.buffButtonsUtil import HintRow
from eve.common.script.mgt.buffBarConst import DBUFFS_BY_SLOT, Slot_DotWeaponTarget, Slot_DotWeaponAttacker
import evetypes
from gametime import GetSimTime
from localization.formatters import FormatTimeIntervalShortWritten
import trinity
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.inflight.moduleEffectTimer import ModuleEffectTimer
from eve.common.script.mgt import buffBarConst
from localization import GetByLabel
from localization.util import Sort
from carbonui.uicore import uicore
from eveservices.menu import GetMenuService
MAX_ITEMS_IN_HINT = 6
SLOT_WIDTH = 48
ICON_SIZE = 40

class BuffHintProvider(object):

    def __init__(self, effectType):
        self.effectType = effectType
        self.dbuffIDsForButton = DBUFFS_BY_SLOT.get(effectType, [])
        captionLabel = buffBarConst.BUFF_SLOT_HINTS.get(effectType, None)
        if captionLabel is not None:
            self.caption = '<b>%s</b>' % GetByLabel(captionLabel)
        else:
            self.caption = None

    def GetCaptionHintList(self):
        items = []
        if self.caption:
            items.append(HintRow(col1=self.caption))
        return items

    def GetNormalHintList(self, effectSources):
        items = []
        if self.effectType == buffBarConst.Slot_Electronic:
            items.extend(self._GetEcmHintItems(effectSources))
        else:
            items.extend(self._GetBuffHintItems(effectSources))
        return items

    def _GetEcmHintItems(self, effectSources):
        ewarAggressors = self._GetEwarAggressorsByJammingType(effectSources)
        activeList = []
        inactiveList = []
        for sourceID, moduleCount, activeCount in ewarAggressors:
            if activeCount:
                targetedBuffSourceText = self._GetTextForTargetedBuffSource(sourceID, activeCount)
                if targetedBuffSourceText:
                    activeList.append(targetedBuffSourceText)
            if moduleCount > activeCount:
                targetedBuffSourceText = self._GetTextForTargetedBuffSource(sourceID, moduleCount - activeCount)
                if targetedBuffSourceText:
                    inactiveList.append(targetedBuffSourceText)

        Sort(activeList, key=lambda x: x.col2)
        Sort(inactiveList, key=lambda x: x.col2)
        hintList = activeList[:MAX_ITEMS_IN_HINT]
        if len(activeList) < MAX_ITEMS_IN_HINT and len(inactiveList):
            hintList.append(HintRow(fullRowText='<color=gray>%s</color>' % GetByLabel('UI/Inflight/EwarHints/FailedEwarAttempts')))
            for eachHintRow in inactiveList[:MAX_ITEMS_IN_HINT - len(activeList)]:
                hintList.append(eachHintRow)

        extraAttackers = len(activeList) + len(inactiveList) - MAX_ITEMS_IN_HINT
        hintList += self._GetExtraAttackersText(extraAttackers)
        return hintList

    def _GetEwarAggressorsByJammingType(self, effectSources):
        activeModulesBySource = self._FindActiveJammers()
        ewarAggressors = []
        for sourceID, moduleCount in effectSources.iteritems():
            activeCount = activeModulesBySource.get(sourceID, 0)
            ewarAggressors.append((sourceID, moduleCount, activeCount))

        ewarAggressors.sort(key=lambda x: -x[2])
        return ewarAggressors

    def _FindActiveJammers(self):
        allActiveJams = sm.GetService('godma').activeJams
        activeJammers = {}
        for sourceBallID, moduleID, targetBallID, _jammingType in allActiveJams:
            if self.effectType != _jammingType:
                continue
            count = activeJammers.get(sourceBallID, 0)
            activeJammers[sourceBallID] = count + 1

        return activeJammers

    def GetDbuffHintItemList(self, incomingDbuffTracker):
        hintList = []
        for dbuffID in self.dbuffIDsForButton:
            buffState = incomingDbuffTracker.incomingDbuffs.get(dbuffID, None)
            if buffState is not None:
                buffValue, expiryTime = buffState
                displayName, formattedValue = GetDisplayNameAndValue(dbuffID, buffValue)
                if displayName is None:
                    continue
                if expiryTime is not None:
                    timeRemaining = max(0L, expiryTime - GetSimTime())
                    formattedTimeRemaining = FormatTimeIntervalShortWritten(timeRemaining)
                else:
                    formattedTimeRemaining = ''
                hr = HintRow(col1=formattedValue, col2=displayName, col3=formattedTimeRemaining)
                hintList.append(hr)

        return hintList

    def _GetBuffHintItems(self, effectSources):
        hintList = []
        extraAttackers = 0
        sortedEffectSources = sorted(effectSources.iteritems(), key=itemgetter(1), reverse=True)
        for shipID, num in sortedEffectSources:
            if len(hintList) >= MAX_ITEMS_IN_HINT:
                extraAttackers = len(effectSources) - len(hintList)
                break
            targetedBuffSourceText = self._GetTextForTargetedBuffSource(shipID, num)
            if targetedBuffSourceText:
                hintList.append(targetedBuffSourceText)

        hintList = Sort(hintList, key=lambda x: x.col2)
        hintList += self._GetExtraAttackersText(extraAttackers)
        return hintList

    def _GetTextForTargetedBuffSource(self, sourceID, numModules):
        invItem = sm.GetService('michelle').GetBallpark().GetInvItem(sourceID)
        if not invItem:
            return
        attackerShipTypeID = invItem.typeID
        numModulesText = GetByLabel('UI/Inflight/NumAttacks', num=numModules)
        hr = HintRow(col1=numModulesText)
        if invItem.charID:
            attackerID = invItem.charID
            hr.col2 = GetByLabel('UI/Inflight/EwarAttacker2', attackerID=attackerID, attackerShipID=attackerShipTypeID)
        else:
            hr.col2 = GetByLabel('UI/Inflight/EwarAttackerNPC2', attackerShipID=attackerShipTypeID)
        return hr

    def _GetExtraAttackersText(self, extraAttackers):
        if extraAttackers > 0:
            return [HintRow(col2=GetByLabel('UI/Inflight/AndMorewarAttackers', num=extraAttackers))]
        return []

    def GetDotWeaponHintList(self, incomingDotWeaponTracker):
        hintList = []
        if self.effectType == Slot_DotWeaponTarget:
            hintList += dotClientUtil.GetTotalTimeHintRow(incomingDotWeaponTracker)
            hintList += dotClientUtil.GetFormattedDotInfoForCurrentShip(incomingDotWeaponTracker)
        if self.effectType == Slot_DotWeaponAttacker:
            hintList += dotClientUtil.GetFormattedPendingDotsAsAttacker(incomingDotWeaponTracker)
        return hintList


class BuffBtnController(object):

    def __init__(self, effectType):
        self.effectType = effectType
        self.tacticalSvc = sm.GetService('tactical')
        self.hintProvider = BuffHintProvider(self.effectType)

    def GetCaptionHintList(self):
        return self.hintProvider.GetCaptionHintList()

    def GetNormalHintList(self):
        effectSources = self._FindWhoIsAffectingMe()
        return self.hintProvider.GetNormalHintList(effectSources)

    def GetDbuffHintItemList(self):
        incomingDbuffTracker = sm.GetService('dbuffClient').incomingDbuffTracker
        return self.hintProvider.GetDbuffHintItemList(incomingDbuffTracker)

    def GetDotWeaponItemList(self):
        incomingDotWeaponTracker = sm.GetService('dotWeaponSvc').incomingDotTracker
        return self.hintProvider.GetDotWeaponHintList(incomingDotWeaponTracker)

    def GetButtonMenu(self):
        effectSources = self._FindWhoIsAffectingMe()
        ballpark = sm.GetService('michelle').GetBallpark()
        m = []
        for shipID, num in effectSources.iteritems():
            invItem = ballpark.GetInvItem(shipID)
            if invItem:
                if invItem.charID:
                    sourceName = cfg.eveowners.Get(invItem.charID).name
                else:
                    sourceName = evetypes.GetName(invItem.typeID)
                m.append([sourceName, ('isDynamic', GetMenuService().CelestialMenu, (invItem.itemID,
                   None,
                   invItem,
                   invItem.typeID))])

        m = Sort(m, key=lambda x: x[0])
        return m

    def OnButtonClick(self):
        if not uicore.cmd.IsSomeCombatCommandLoaded():
            return
        michelle = sm.GetService('michelle')
        stateSvc = sm.GetService('stateSvc')
        targets = []
        effectSources = self._FindWhoIsAffectingMe()
        targetStates = (stateConst.targeted, stateConst.targeting)
        targeting = uicore.cmd.combatCmdLoaded.name == 'CmdLockTargetItem'
        for sourceID in effectSources:
            try:
                if targeting and any(stateSvc.GetStates(sourceID, targetStates)):
                    continue
                ball = michelle.GetBall(sourceID)
                targets.append((ball.surfaceDist, sourceID))
            except RuntimeError:
                pass

        if len(targets) > 0:
            targets.sort()
            itemID = targets[0][1]
            uicore.cmd.ExecuteCombatCommand(itemID, uiconst.UI_CLICK)

    def _FindWhoIsAffectingMe(self):
        return self.tacticalSvc.GetEffectSourcesAndCountByJammingType(self.effectType)


class BuffSlotParent(Container):
    default_align = uiconst.TOLEFT
    default_width = SLOT_WIDTH
    default_height = ICON_SIZE
    effectGuidForButtonType = None
    dbuffIDsForButton = None
    currentDbuffExpiryTime = None
    currentDotExpiryTime = None

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.display = False
        self.fadingOut = False
        self.effectType = attributes.effectType
        graphicID = attributes.graphicID
        btnClass = BUTTON_CLASS_BY_SLOT.get(self.effectType, BuffButton)
        self.btn = btnClass(parent=self, name=self.effectType, align=uiconst.CENTER, width=ICON_SIZE, height=ICON_SIZE, graphicID=graphicID, effectType=self.effectType)
        self.effectGuidForButtonType = buffBarConst.FX_GUIDS_BY_SLOT.get(self.effectType, None)
        self.dbuffIDsForButton = DBUFFS_BY_SLOT.get(self.effectType, [])

    def UpdateVisibility(self, jammersByType, myShipEffectGuids, incomingDbuffTracker, incomingDotTracker, genericBuffBarIcons, doAnimate):
        if self._ShouldBeVisible(jammersByType, myShipEffectGuids, incomingDbuffTracker, incomingDotTracker, genericBuffBarIcons):
            if self.btn.IsOffensive():
                order = self._GetNumberOfActiveDebuffs(jammersByType) - 1
            else:
                order = -1
            self.FadeButtonIn(doAnimate, order)
        else:
            self.FadeButtonOut(doAnimate)

    def _ShouldBeVisible(self, jammersByType, myShipEffectGuids, incomingDbuffTracker, incomingDotTracker, genericBuffBarIcons):
        if jammersByType.get(self.effectType, None):
            return True
        if self.effectGuidForButtonType and self.effectGuidForButtonType in myShipEffectGuids:
            return True
        if self.effectType in genericBuffBarIcons:
            return True
        for dbuffID in self.dbuffIDsForButton:
            if dbuffID in incomingDbuffTracker.incomingDbuffs:
                return True

        if self.effectType == Slot_DotWeaponTarget and incomingDotTracker.CurrentShipHasIncomingDotApps():
            return True
        if self.effectType == Slot_DotWeaponAttacker and incomingDotTracker.ShouldShowAttackingBtn():
            return True
        return False

    def _GetNumberOfActiveDebuffs(self, jammersByType):
        return len(jammersByType.get(self.effectType, []))

    def FadeButtonIn(self, doAnimate = False, order = -1):
        if not self.display or self.fadingOut:
            self.fadingOut = False
            self.SetOrder(order)
            self.display = True
            if doAnimate:
                uicore.animations.FadeIn(self, duration=0.25)
                uicore.animations.MorphScalar(self, 'width', startVal=0, endVal=SLOT_WIDTH, duration=0.25)
            else:
                self.opacity = 1.0
                self.width = SLOT_WIDTH

    def FadeButtonOut(self, doAnimate = True):
        if not self.display:
            return
        if not self.fadingOut:
            self.fadingOut = True
            if doAnimate:
                uicore.animations.MorphScalar(self, 'width', startVal=SLOT_WIDTH, endVal=0, duration=0.25)
                uicore.animations.FadeOut(self, duration=0.25, sleep=True)
                if self.fadingOut:
                    self.display = False
            else:
                self.display = False
                self.opacity = 0.0
                self.width = 0

    def UpdateDbuffTimer(self, incomingDbuffTracker):
        myDbuffExpiryTimes = [ expiryTime for dbuffID, (value, expiryTime) in incomingDbuffTracker.incomingDbuffs.iteritems() if dbuffID in self.dbuffIDsForButton ]
        if len(myDbuffExpiryTimes) == 0 or None in myDbuffExpiryTimes:
            self.currentDbuffExpiryTime = None
            self.btn.RemoveTimer('DBUFF_TIMER_ID')
        else:
            latestExpiryTime = max(myDbuffExpiryTimes)
            if self.currentDbuffExpiryTime != latestExpiryTime:
                self.currentDbuffExpiryTime = latestExpiryTime
                duration = max((latestExpiryTime - GetSimTime()) / MSEC, 0.2)
                self.btn.GetTimer('DBUFF_TIMER_ID').StartTimer(duration)

    def UpdateDotTimer(self, incomingDotTracker):
        if self.effectType != Slot_DotWeaponTarget:
            return
        latestExpiryTime = incomingDotTracker.GetLastExpiryTimestampForCurrentShip()
        nowInSim = GetSimTime()
        timerID = 'DOT_TIMER_ID'
        if latestExpiryTime < nowInSim:
            self.currentDbuffExpiryTime = None
            self.btn.RemoveTimer(timerID)
        elif self.currentDotExpiryTime != latestExpiryTime:
            self.currentDotExpiryTime = latestExpiryTime
            duration = max((latestExpiryTime - nowInSim) / MSEC, 0.2)
            self.btn.GetTimer(timerID).StartTimer(duration)


class BuffButton(Container):
    __guid__ = 'BuffButton'
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.RELATIVE
    default_pickRadius = -1
    ICON_BASE_ALPHA = 1.0
    ICON_HIGHLIGHTED_ALPHA = 1.5
    ICON_COLOR = (1.0,
     1.0,
     1.0,
     ICON_BASE_ALPHA)
    SLOT_COLOR = (1.0, 1.0, 1.0, 1)
    SLOT_TEXTURE_PATH = 'res:/UI/Texture/classes/ShipUI/EwarBar/ewarBarUnderlayClean.png'
    SLOT_GRADIENT_TEXTURE_PATH = 'res:/UI/Texture/classes/ShipUI/EwarBar/ewarBarUnderlayGrad.png'
    SLOT_BASE_ALPHA = 0.2
    SLOT_GRADIENT_ALPHA = 0.25
    SHADOW_COLOR = (1.0, 1.0, 1.0, 0.25)
    SHADOW_TEXTURE_PATH = 'res:/UI/Texture/classes/ShipUI/EwarBar/ewarBarShadow.png'
    TIMER_OPACITY = 0.65
    TIMER_COLOR = (1.0, 1.0, 1.0)
    TIMER_RIGHT_COUNTER_TEXTURE_PATH = 'res:/UI/Texture/classes/ShipUI/EwarBar/ewarCounterRight.png'
    TIMER_LEFT_COUNTER_TEXTURE_PATH = 'res:/UI/Texture/classes/ShipUI/EwarBar/ewarCounterLeft.png'
    TIMER_COUNTER_GAUGE_TEXTURE_PATH = 'res:/UI/Texture/classes/ShipUI/EwarBar/ewarCounterGauge.png'
    TIMER_INCREASE = False
    isOffensive = False

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.btnName = attributes.btnName
        self.effectType = attributes.effectType
        self.orgTop = None
        self.timers = OrderedDict()
        self._tooltipUpdateTimer = None
        self.controller = BuffBtnController(self.effectType)
        graphicID = attributes.graphicID
        iconSize = self.height
        self.icon = Icon(parent=self, name='bufficon', pos=(0,
         0,
         iconSize,
         iconSize), align=uiconst.CENTER, state=uiconst.UI_DISABLED, ignoreSize=1, color=self.ICON_COLOR)
        Sprite(parent=self, name='slot_gradient', align=uiconst.TOALL, state=uiconst.UI_DISABLED, color=self.SLOT_COLOR, blendMode=trinity.TR2_SBM_ADD, texturePath=self.SLOT_GRADIENT_TEXTURE_PATH, opacity=self.SLOT_GRADIENT_ALPHA)
        Sprite(parent=self, name='slot_base', align=uiconst.TOALL, state=uiconst.UI_DISABLED, color=self.SLOT_COLOR, blendMode=trinity.TR2_SBM_ADD, texturePath=self.SLOT_TEXTURE_PATH, opacity=self.SLOT_BASE_ALPHA)
        Sprite(parent=self, name='shadow', align=uiconst.TOALL, state=uiconst.UI_DISABLED, color=self.SHADOW_COLOR, texturePath=self.SHADOW_TEXTURE_PATH)
        self.LoadIcon(graphicID)

    def LoadIcon(self, graphicID):
        self.icon.LoadIconByIconID(graphicID)

    def GetTimer(self, timerId):
        if timerId not in self.timers:
            timer = ModuleEffectTimer(parent=self, timerColor=self.TIMER_COLOR, timerOpacity=self.TIMER_OPACITY, timerRightCounterTexturePath=self.TIMER_RIGHT_COUNTER_TEXTURE_PATH, timerLeftCounterTexturePath=self.TIMER_LEFT_COUNTER_TEXTURE_PATH, timerCounterGaugeTexturePath=self.TIMER_COUNTER_GAUGE_TEXTURE_PATH, timeIncreases=self.TIMER_INCREASE, idx=0)
            self.timers[timerId] = timer
        else:
            timer = self.timers.pop(timerId)
            self.timers[timerId] = timer
        return timer

    def RemoveTimer(self, timerId):
        if timerId in self.timers:
            self.timers[timerId].RemoveTimer()
            del self.timers[timerId]

    def GetHint(self):
        return ''

    def LoadTooltipPanel(self, tooltipPanel, *args, **kwds):
        tooltipPanel.LoadGeneric3ColumnTemplate()
        tooltipPanel.cellSpacing = (10, 4)
        self._LoadTooltipPanel(tooltipPanel)
        self._tooltipUpdateTimer = AutoTimer(250, self._LoadTooltipPanel, tooltipPanel)

    def _LoadTooltipPanel(self, tooltipPanel):
        if tooltipPanel.destroyed:
            self._tooltipUpdateTimer = None
            return
        tooltipPanel.Flush()
        hintList = self.controller.GetCaptionHintList()
        for eachHintRow in hintList:
            tooltipPanel.AddLabelLarge(text=eachHintRow.col1, colSpan=3)

        hintList = self.controller.GetNormalHintList()
        hintList += self.controller.GetDotWeaponItemList()
        hintList += self.controller.GetDbuffHintItemList()
        for eachHintRow in hintList:
            if eachHintRow.fullRowText:
                tooltipPanel.AddLabelMedium(text=eachHintRow.fullRowText, colSpan=3)
            else:
                tooltipPanel.AddLabelMedium(text=eachHintRow.col1, align=uiconst.CENTERRIGHT)
                tooltipPanel.AddLabelMedium(text=eachHintRow.col2)
                if eachHintRow.col3:
                    tooltipPanel.AddLabelMedium(text=eachHintRow.col3)
                tooltipPanel.FillRow()

    def OnMouseEnter(self, *args):
        self.icon.SetAlpha(self.ICON_HIGHLIGHTED_ALPHA)

    def OnMouseExit(self, *args):
        if getattr(self, 'orgTop', None) is not None:
            self.top = self.orgTop
        self.icon.SetAlpha(self.ICON_BASE_ALPHA)

    def GetMenu(self, *args):
        return self.controller.GetButtonMenu()

    def OnClick(self, *args):
        return self.controller.OnButtonClick()

    def IsOffensive(self):
        return self.isOffensive


class OffensiveBuffButton(BuffButton):
    SLOT_COLOR = (0.7, 0.0, 0.0, 1)
    ICON_COLOR = (1.0,
     0.7,
     0.7,
     BuffButton.ICON_BASE_ALPHA)
    TIMER_COLOR = (1.0, 0.3, 0.0)
    isOffensive = True


class DefensiveBuffButton(BuffButton):
    SLOT_COLOR = (0.0, 0.6, 0.6, 1)
    ICON_COLOR = (0.7,
     1,
     1,
     BuffButton.ICON_BASE_ALPHA)
    TIMER_COLOR = (0.0, 0.8, 0.8)
    isOffensive = False


BUTTON_CLASS_BY_SLOT = {buffBarConst.Slot_WarpScramblerMWD: OffensiveBuffButton,
 buffBarConst.Slot_WarpScrambler: OffensiveBuffButton,
 buffBarConst.Slot_FighterTackle: OffensiveBuffButton,
 buffBarConst.Slot_FocusedWarpScrambler: OffensiveBuffButton,
 buffBarConst.Slot_Webify: OffensiveBuffButton,
 buffBarConst.Slot_Electronic: OffensiveBuffButton,
 buffBarConst.Slot_EwRemoteSensorDamp: OffensiveBuffButton,
 buffBarConst.Slot_EwTrackingDisrupt: OffensiveBuffButton,
 buffBarConst.Slot_EwGuidanceDisrupt: OffensiveBuffButton,
 buffBarConst.Slot_EwTargetPaint: OffensiveBuffButton,
 buffBarConst.Slot_EwEnergyVampire: OffensiveBuffButton,
 buffBarConst.Slot_EwEnergyNeut: OffensiveBuffButton,
 buffBarConst.Slot_RemoteTracking: DefensiveBuffButton,
 buffBarConst.Slot_EnergyTransfer: DefensiveBuffButton,
 buffBarConst.Slot_SensorBooster: DefensiveBuffButton,
 buffBarConst.Slot_EccmProjector: DefensiveBuffButton,
 buffBarConst.Slot_RemoteHullRepair: DefensiveBuffButton,
 buffBarConst.Slot_RemoteArmorRepair: DefensiveBuffButton,
 buffBarConst.Slot_ShieldTransfer: DefensiveBuffButton,
 buffBarConst.Slot_Tethering: DefensiveBuffButton,
 buffBarConst.Slot_TetheringRepair: DefensiveBuffButton,
 buffBarConst.Slot_ShieldBurst: DefensiveBuffButton,
 buffBarConst.Slot_ArmorBurst: DefensiveBuffButton,
 buffBarConst.Slot_InformationBurst: DefensiveBuffButton,
 buffBarConst.Slot_SkirmishBurst: DefensiveBuffButton,
 buffBarConst.Slot_MiningBurst: DefensiveBuffButton,
 buffBarConst.Slot_InvulnerabilityBurst: DefensiveBuffButton,
 buffBarConst.Slot_TitanBurst: DefensiveBuffButton,
 buffBarConst.Slot_NotTethered: OffensiveBuffButton,
 buffBarConst.Slot_RemoteArmorMutadaptiveRepairer: DefensiveBuffButton,
 buffBarConst.Slot_CloakDisrupt: OffensiveBuffButton,
 buffBarConst.Slot_CloakDefense: DefensiveBuffButton,
 buffBarConst.Slot_LinkWithShipBonuses: DefensiveBuffButton,
 buffBarConst.Slot_TetheringRestrictedBySecurity: OffensiveBuffButton,
 buffBarConst.Slot_RemoteRepairImpedance: OffensiveBuffButton,
 buffBarConst.Slot_DotWeaponTarget: OffensiveBuffButton,
 buffBarConst.Slot_DotWeaponAttacker: DefensiveBuffButton,
 buffBarConst.Slot_LinkedToTraceGate: DefensiveBuffButton}
