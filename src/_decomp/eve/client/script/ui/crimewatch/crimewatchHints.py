#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\crimewatch\crimewatchHints.py
import dogma.data as dogma_data
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from dogma.attributes.format import GetFormatAndValue
from eve.client.script.parklife import states as state
import evetypes
import localization
import uthread
import copy
import blue
import carbonui.const as uiconst
from carbonui.primitives.fill import Fill
from carbonui.util.color import Color
from dogma.const import attributeNonDiminishingSkillInjectorUses
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import Label, EveLabelSmall
from carbonui.util.various_unsorted import IsUnder
from eve.client.script.ui.crimewatch.crimewatchConst import Colors
from eve.client.script.ui.shared.stateFlag import FlagIconWithState
from utillib import KeyVal
from carbonui.control.scrollContainer import ScrollContainer
from localization.formatters.timeIntervalFormatters import FormatTimeInterval
from carbonui.uicore import uicore
from eveservices.menu import GetMenuService
import jumpFatigue.const as jumpFatigueConst
from stargate.client.gateLockController import GateLockController
from stargate.client import get_gate_lock_messenger
import eve.common.lib.appConst as appConst
HINT_FRAME_COLOR = (1.0, 1.0, 1.0, 0.25)
HINT_BACKGROUND_COLOR = (0, 0, 0, 0.85)
MAX_ENGAGED_VISIBLE = 10

def FmtTime(timeLeft):
    if timeLeft > 0:
        minutes, seconds = divmod(timeLeft / const.SEC, 60)
        hours, minutes = divmod(minutes, 60)
    else:
        hours = 0
        minutes = 0
        seconds = 0
    if hours > 0:
        return '%02d:%02d:%02d' % (hours, max(0, minutes), max(0, seconds))
    else:
        return '%02d:%02d' % (max(0, minutes), max(0, seconds))


class TimerHint(Container):
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL
    default_bgColor = HINT_BACKGROUND_COLOR
    default_width = 300
    default_height = 48
    TIME_WIDTH = 58
    TEXT_WIDTH = 242

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.parentTimer = attributes.get('parentTimer')
        self.timerData = attributes.get('timerData')
        self.GetTime = self.timerData.timerFunc
        Frame(pgParent=self, state=uiconst.UI_DISABLED, color=HINT_FRAME_COLOR)
        leftCont = Container(parent=self, align=uiconst.TOLEFT, width=self.TIME_WIDTH)
        rightCont = Container(parent=self, align=uiconst.TOALL)
        self.time = eveLabel.Label(parent=leftCont, name='counter', text=str(int(self.timerData.maxTimeout / const.SEC)), fontsize=self.GetTimerFontSize(), bold=False, align=uiconst.CENTERLEFT, color=self.timerData.color, left=2 * const.defaultPadding)
        self.text = eveLabel.EveLabelSmall(left=const.defaultPadding, parent=rightCont, name='timer description', text=self.GetTooltipText(), align=uiconst.CENTERLEFT, width=self.TEXT_WIDTH - 2 * const.defaultPadding)
        self.height = self.text.actualTextHeight + 2 * const.defaultPadding
        self.activeBlink = None
        self.doUpdates = True
        uthread.new(self.UpdateTimer)
        self.opacity = 0.0
        uicore.animations.FadeIn(self, duration=0.5)

    def GetTimerFontSize(self):
        if session.languageID == 'ZH':
            return 16
        else:
            return 20

    def _OnClose(self):
        self.doUpdates = False
        self.parentTimer.timerHint = None

    def UpdateTimer(self):
        wallclockStartTime = blue.os.GetWallclockTime()
        while self.doUpdates:
            timeNow = self.GetTime()
            wallclockTimeNow = blue.os.GetWallclockTime()
            if self.parentTimer.expiryTime is not None:
                timeLeft = max(0, self.parentTimer.expiryTime - timeNow)
                if timeLeft == 0:
                    self.doUpdates = False
                if self.activeBlink is not None:
                    self.activeBlink.Stop()
                    self.time.opacity = 1.0
                    self.activeBlink = None
            else:
                timeLeft = self.timerData.maxTimeout
                if self.activeBlink is None:
                    self.activeBlink = uicore.animations.BlinkOut(self.time, duration=1.0, loops=uiconst.ANIM_REPEAT)
            if wallclockStartTime + const.SEC < wallclockTimeNow:
                if not (uicore.uilib.mouseOver is self or IsUnder(uicore.uilib.mouseOver, self.parentTimer)):
                    self.doUpdates = False
            try:
                self.OnUpdate(timeLeft)
            except StandardError:
                pass

            if self.doUpdates:
                blue.pyos.synchro.SleepWallclock(200)

        uicore.animations.FadeOut(self, sleep=True)
        self.Close()

    def OnUpdate(self, timeLeft):
        self.time.text = FmtTime(timeLeft)

    def GetTooltipArguments(self):
        return {}

    def GetTooltipText(self):
        return localization.GetByLabel(self.timerData.tooltip, **self.GetTooltipArguments())


class EngagementEntry(Container):
    default_align = uiconst.TOTOP
    default_height = 32
    default_padBottom = 1
    default_state = uiconst.UI_NORMAL
    isDragObject = True
    __notifyevents__ = ['OnCrimewatchEngagementUpdated']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.charID = attributes.get('charID')
        self.timeout = attributes.get('timeout')
        self.isDragObject = True
        self.itemID = self.charID
        self.info = cfg.eveowners.Get(self.charID)
        self.activeBlink = None
        self.highlight = Fill(bgParent=self, color=(1, 1, 1, 0.1), state=uiconst.UI_HIDDEN)
        leftCont = Container(parent=self, align=uiconst.TOLEFT, width=54)
        self.time = eveLabel.Label(parent=leftCont, name='counter', text='', fontsize=16, bold=False, align=uiconst.CENTERLEFT, color=Colors.Engagement.GetRGBA(), left=2 * const.defaultPadding)
        self.portrait = Sprite(parent=self, pos=(50, 0, 32, 32), state=uiconst.UI_DISABLED)
        eveLabel.EveLabelSmall(parent=self, name='name', text=self.info.ownerName, align=uiconst.TOPLEFT, top=1, left=96)
        self.corpText = eveLabel.EveLabelSmall(parent=self, name='corporation', text='', align=uiconst.TOPLEFT, top=17, left=96)
        self.stateFlag = FlagIconWithState(parent=self, align=uiconst.TOPRIGHT, left=13, top=4)
        self.LoadData()
        sm.RegisterNotify(self)

    def LoadData(self):
        self.SetTimer()
        sm.GetService('photo').GetPortrait(self.charID, 32, self.portrait)
        uthread.new(self.LazyLoadData)

    def OnMouseEnter(self, *args):
        self.highlight.display = True

    def OnMouseExit(self, *args):
        self.highlight.display = False

    def SetTimer(self):
        if self.timeout == const.crimewatchEngagementTimeoutOngoing:
            self.time.text = FmtTime(const.crimewatchEngagementDuration)
            if self.activeBlink is None:
                self.activeBlink = uicore.animations.BlinkOut(self.time, duration=1.0, loops=uiconst.ANIM_REPEAT)
        else:
            self.time.text = FmtTime(self.timeout - blue.os.GetWallclockTime())
            if self.activeBlink is not None:
                self.activeBlink.Stop()
                self.activeBlink = None
                self.time.opacity = 1.0

    def LazyLoadData(self):
        slimItem = sm.GetService('crimewatchSvc').GetSlimItemDataForCharID(self.charID)
        if slimItem is not None:
            self.corpText.text = cfg.eveowners.Get(slimItem.corpID).ownerName
            stateSvc = sm.GetService('stateSvc')
            flagCode = stateSvc.CheckFilteredFlagState(slimItem, (state.flagLimitedEngagement,))
            flagInfo = stateSvc.GetStatePropsColorAndBlink(flagCode)
            self.stateFlag.ModifyIcon(flagInfo=flagInfo)
            self.slimItem = copy.copy(slimItem)

    def OnClick(self):
        sm.GetService('info').ShowInfo(typeID=self.info.typeID, itemID=self.charID)

    def GetDragData(self, *args):
        if self and not self.destroyed:
            fakeNode = KeyVal()
            fakeNode.charID = self.charID
            fakeNode.typeID = self.info.typeID
            fakeNode.info = self.info
            fakeNode.itemID = self.itemID
            fakeNode.__guid__ = 'listentry.User'
            return [fakeNode]
        else:
            return []

    def GetMenu(self):
        if self.slimItem:
            if self.slimItem.itemID:
                return GetMenuService().CelestialMenu(self.slimItem.itemID)
            else:
                return GetMenuService().GetMenuFromItemIDTypeID(self.itemID, self.info.typeID)

    def OnCrimewatchEngagementUpdated(self, otherCharId, timeout):
        if otherCharId == self.charID:
            if timeout is None:
                uicore.animations.FadeOut(self, duration=0.5, sleep=True)
                self.Close()
                sm.ScatterEvent('OnEngagementTimerHintResize')
            else:
                self.timeout = timeout


class BaseAdvancedTimerHint(ContainerAutoSize):
    default_name = 'BaseAdvancedTimerHint'
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL
    default_bgColor = HINT_BACKGROUND_COLOR
    default_width = 240

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        self.parentTimer = attributes.get('parentTimer')
        self.timerData = attributes.get('timerData')
        self.GetTime = self.timerData.timerFunc
        self.doUpdates = True
        Frame(bgParent=self, state=uiconst.UI_DISABLED, color=(1.0, 1.0, 1.0, 0.25))
        self.mainText = eveLabel.EveLabelMedium(parent=self, align=uiconst.TOTOP, text='', padding=(8, 8, 8, 8), state=uiconst.UI_DISABLED)
        self.entryContainer = ScrollContainer(parent=self, align=uiconst.TOTOP)

    def UpdateTimer(self):
        startTime = self.GetTime()
        count = 0
        while self.doUpdates:
            timeNow = self.GetTime()
            self._UpdateTimers()
            if startTime + const.SEC < timeNow:
                if not (uicore.uilib.mouseOver is self or IsUnder(uicore.uilib.mouseOver, self) or IsUnder(uicore.uilib.mouseOver, self.parentTimer)):
                    if count > 2:
                        self.doUpdates = False
                    else:
                        count += 1
                else:
                    count = 0
            if self.doUpdates:
                blue.pyos.synchro.SleepWallclock(200)

        uicore.animations.FadeOut(self, sleep=True)
        self.Close()

    def _UpdateTimers(self):
        for child in self.entryContainer.mainCont.children[:]:
            child.SetTimer()

        self.UpdateHeightAndWidth()

    def _OnClose(self):
        self.doUpdates = False
        self.parentTimer.timerHint = None


class EngagementTimerHint(BaseAdvancedTimerHint):
    __notifyevents__ = ['OnEngagementTimerHintResize', 'OnCrimewatchEngagementUpdated']
    default_name = 'EngagementTimerHint'

    def ApplyAttributes(self, attributes):
        BaseAdvancedTimerHint.ApplyAttributes(self, attributes)
        self.LoadData()
        uthread.new(self.UpdateTimer)
        sm.RegisterNotify(self)

    def OnEngagementTimerHintResize(self):
        self.UpdateScrollHeight()

    def SortKey(self, entry):
        if entry[0] == const.crimewatchEngagementTimeoutOngoing:
            return blue.os.GetWallclockTime()

    def LoadData(self):
        engagements = sm.GetService('crimewatchSvc').GetMyEngagements()
        cfg.eveowners.Prime(engagements.keys())
        engagementList = [ (timeout, charID) for charID, timeout in engagements.iteritems() ]
        engagementList.sort(key=self.SortKey)
        for timeout, charID in engagementList:
            self.AddEntry(charID, timeout)

        self.mainText.text = localization.GetByLabel('UI/Crimewatch/Timers/EngagementTooltipHintHeader', count=len(engagementList))
        self.UpdateScrollHeight()

    def AddEntry(self, charID, timeout):
        EngagementEntry(parent=self.entryContainer, charID=charID, timeout=timeout)

    def UpdateScrollHeight(self):
        self.entryContainer.height = sum((x.height + x.padBottom for x in self.entryContainer.mainCont.children[:MAX_ENGAGED_VISIBLE]))

    def OnCrimewatchEngagementUpdated(self, otherCharId, timeout):
        for child in self.entryContainer.mainCont.children[:]:
            if otherCharId == child.charID:
                break
        else:
            self.AddEntry(otherCharId, timeout)
            self.UpdateScrollHeight()

    def UpdateHeightAndWidth(self):
        pass


class BoosterTimerHint(BaseAdvancedTimerHint):
    default_name = 'BoosterTimerHint'

    def ApplyAttributes(self, attributes):
        BaseAdvancedTimerHint.ApplyAttributes(self, attributes)
        self.mainText.text = localization.GetByLabel('UI/Crimewatch/Timers/ActiveBoosters')
        self.entryContainer = ScrollContainer(parent=self, align=uiconst.TOTOP)
        self.LoadData()
        uthread.new(self.UpdateTimer)

    def LoadData(self):
        boosters = sm.GetService('crimewatchSvc').GetMyBoosters()
        sortedBoosters = [ (b.expiryTime, b) for b in boosters if b.boosterDuration ]
        sortedBoosters.sort(reverse=True)
        for expiryTime, booster in sortedBoosters:
            effects = sm.GetService('crimewatchSvc').GetBoosterEffects(booster)
            self.AddEntry(booster, expiryTime, effects)

        self.UpdateHeightAndWidth()

    def AddEntry(self, booster, expiryTime, effects):
        entry = BoosterEntry(parent=self.entryContainer, booster=booster, expiryTime=expiryTime, effects=effects)
        return entry

    def UpdateHeightAndWidth(self):
        if not self.entryContainer.mainCont.children:
            return
        self.entryContainer.height = sum((x.height + x.padBottom for x in self.entryContainer.mainCont.children))
        timerWidth = max((x.time.width for x in self.entryContainer.mainCont.children)) + 2 * const.defaultPadding
        for x in self.entryContainer.mainCont.children:
            x.time.parent.width = timerWidth

        self.width = timerWidth + max((x.maxtextwidth + 10 for x in self.entryContainer.mainCont.children))


class BoosterEntry(Container):
    default_align = uiconst.TOTOP
    default_height = 50
    default_padBottom = 1
    default_state = uiconst.UI_NORMAL
    TIME_WIDTH = 60

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.booster = attributes.get('booster')
        self.expiryTime = attributes.get('expiryTime')
        self.effects = attributes.get('effects')
        self.positiveEffects = self.effects.get('positive', [])
        self.negativeEffects = self.effects.get('negative', [])
        self.typeID = self.booster.typeID
        self.activeBlink = None
        self.highlight = Fill(bgParent=self, color=(1, 1, 1, 0.1), state=uiconst.UI_HIDDEN)
        leftCont = Container(parent=self, align=uiconst.TOLEFT, width=self.TIME_WIDTH)
        rightCont = Container(parent=self, align=uiconst.TOALL)
        self.time = Label(parent=leftCont, name='counter', text='', fontsize=16, bold=False, align=uiconst.TOPLEFT, color=(1, 1, 1, 0.75), left=2 * const.defaultPadding)
        self.boosterSprite = Icon(parent=rightCont, name='boosterIcon', icon=evetypes.GetIconID(self.typeID), pos=(0, 0, 24, 24), ignoreSize=True, state=uiconst.UI_DISABLED)
        left = self.boosterSprite.width
        boosterName = EveLabelSmall(parent=rightCont, name='name', text=evetypes.GetName(self.typeID), align=uiconst.TOPLEFT, top=1, left=left)
        self.maxtextwidth = boosterName.textwidth + boosterName.left
        padTop = boosterName.textheight + 4
        allModified = self.GetBoosterEffectsInfo(self.positiveEffects) + self.GetBoosterEffectsInfo(self.negativeEffects, True)
        self._AddNonDiminishingInjections(allModified)
        addedText = set()
        for lineText in allModified:
            if lineText in addedText:
                continue
            effectLabel = EveLabelSmall(parent=rightCont, name='effect', text=lineText, align=uiconst.TOPLEFT, padTop=padTop, left=30)
            addedText.add(lineText)
            padTop += effectLabel.textheight + 2
            self.maxtextwidth = max(self.maxtextwidth, effectLabel.textwidth + effectLabel.left)

        self.height = max(padTop + 4, self.boosterSprite.height + 2)
        self.LoadData()

    def _AddNonDiminishingInjections(self, allModified):
        dogmaLM = sm.GetService('clientDogmaIM').GetDogmaLocation()
        if dogmaLM.dogmaStaticMgr.GetTypeAttribute(self.typeID, attributeNonDiminishingSkillInjectorUses, defaultValue=0):
            nonDiminishingInjectionsRemaining = sm.GetService('nonDiminishingInjection').GetRemaining()
            effectText = localization.GetByLabel('UI/Skills/NonDiminishingInjectionsRemainingForBooster', timesRemaining=int(nonDiminishingInjectionsRemaining))
            allModified.append(effectText)

    def GetBoosterEffectsInfo(self, effects, isNegative = False):
        dogmaLM = sm.GetService('clientDogmaIM').GetDogmaLocation()
        neurotoxinControlTypeID = 25538
        effectsTextList = []
        for eff in effects:
            if eff.modifierInfo:
                modifyingAttributeID = eff.modifierInfo[0].modifyingAttributeID
                effectAmount = dogmaLM.dogmaStaticMgr.GetTypeAttribute(self.booster.typeID, modifyingAttributeID)
                if isNegative and effectAmount:
                    neurotoxinControlSkill = sm.GetService('skills').GetSkill(neurotoxinControlTypeID)
                    effectModifier = dogmaLM.dogmaStaticMgr.GetSkillModifiedAttributePercentageValue(modifyingAttributeID, appConst.attributeBoosterAttributeModifier, neurotoxinControlTypeID, neurotoxinControlSkill)
                    effectAmount *= effectModifier
                    effectAmount *= self._GetToxinControlImplantModifier()
                attributes = dogma_data.get_attribute(modifyingAttributeID)
                effectText = localization.GetByLabel('UI/Crimewatch/Timers/BoosterPenaltyWithValue', value=GetFormatAndValue(attributes, abs(effectAmount)), penaltyName=dogma_data.get_attribute_display_name(modifyingAttributeID))
            else:
                effectText = dogma_data.get_effect_display_name(eff.effectID)
            effectsTextList.append(effectText)

        return effectsTextList

    def _GetToxinControlImplantModifier(self):
        implants = sm.GetService('godma').GetItem(session.charid).implants
        ret = 1.0
        if not implants:
            return ret
        for implant in implants:
            if implant.typeID in [appConst.typeNeurotoxinControl903, appConst.typeNeurotoxinControl905]:
                dogmaLM = sm.GetService('clientDogmaIM').GetDogmaLocation()
                mod = dogmaLM.dogmaStaticMgr.GetTypeAttribute2(implant.typeID, appConst.attributeBoosterAttributeModifier)
                if mod:
                    return (100 + mod) / 100.0

        return ret

    def LoadData(self):
        self.SetTimer()

    def OnMouseEnter(self, *args):
        self.highlight.display = True

    def OnMouseExit(self, *args):
        self.highlight.display = False

    def SetTimer(self):
        self.time.text = FmtTime(self.expiryTime - blue.os.GetWallclockTime())
        if self.activeBlink is not None:
            self.activeBlink.Stop()
            self.activeBlink = None
            self.time.opacity = 1.0

    def OnClick(self):
        sm.GetService('info').ShowInfo(typeID=self.typeID, itemID=self.booster.boosterID)

    def GetMenu(self):
        return GetMenuService().GetMenuFromItemIDTypeID(itemID=self.booster.boosterID, typeID=self.typeID)


class JumpTimerHint(TimerHint):

    def ApplyAttributes(self, attributes):
        TimerHint.ApplyAttributes(self, attributes)
        self.time.parent.Close()
        self.text.parent.Close()
        self.container = ContainerAutoSize(parent=self, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, padding=(3 * const.defaultPadding,
         2 * const.defaultPadding,
         2 * const.defaultPadding,
         2 * const.defaultPadding), callback=self.OnContainerResized)
        self.time = eveLabel.Label(parent=self.container, align=uiconst.TOTOP, fontsize=self.GetTimerFontSize(), color=self.timerData.color)
        self.text = eveLabel.EveLabelSmall(parent=self.container, align=uiconst.TOTOP, top=const.defaultPadding)
        self.next = eveLabel.EveLabelSmall(parent=self.container, align=uiconst.TOTOP, top=2 * const.defaultPadding, color=self.timerData.color)

    def OnContainerResized(self):
        self.height = self.container.height + 4 * const.defaultPadding

    def OnUpdate(self, remaining):
        color = Color.RGBtoHex(*self.timerData.color)
        if remaining:
            self.time.text = FormatTimeInterval(remaining, color, color)
            self.text.text = self.GetTooltipText()
            self.AddExtraHint(remaining)

    def AddExtraHint(self, remaining):
        pass


class JumpTimerFatigueHint(JumpTimerHint):

    def AddExtraHint(self, remaining):
        newMinimumActivationTime, maxSecondsWhereDistanceMatters = GetJumpActivationTimes(remaining)
        isAccurate = newMinimumActivationTime >= maxSecondsWhereDistanceMatters
        newActivationTime = FmtActivationTime(long(newMinimumActivationTime * const.SEC))
        if isAccurate:
            text = localization.GetByLabel('UI/Crimewatch/Timers/JumpFatigueNextActivation', time=newActivationTime)
        else:
            maxTime = FmtActivationTime(long(maxSecondsWhereDistanceMatters * const.SEC))
            text = localization.GetByLabel('UI/Crimewatch/Timers/JumpFatigueNextActivationRange', minTime=newActivationTime, maxTime=maxTime)
        self.next.text = text


class EmanationLockHint(TimerHint):
    default_width = 500
    default_height = 48
    TIME_WIDTH = 85
    TEXT_WIDTH = 415

    def ApplyAttributes(self, attributes):
        TimerHint.ApplyAttributes(self, attributes)
        sm.GetService('uiHighlightingService').clear_ui_highlighting_for_element(pointToID=self.parentTimer.name)

    def GetTooltipArguments(self):
        arguments = {}
        controller = GateLockController.get_instance(get_gate_lock_messenger(sm.GetService('publicGatewaySvc')))
        lockDetails = controller.get_current_system_lock()
        if lockDetails is not None:
            arguments['gate'] = cfg.evelocations.Get(lockDetails.gate_id).name
            arguments['system'] = cfg.evelocations.Get(lockDetails.solar_system_id).name
        return arguments


def GetJumpActivationTimes(remainingFatigue):
    dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
    shipMultiplier = dogmaLocation.GetAttributeValue(session.shipid, const.attributeJumpFatigueMultiplier)
    shipMaxDistance = dogmaLocation.GetAttributeValue(session.shipid, const.attributeJumpDriveRange)
    multiplier = jumpFatigueConst.ADDITIONAL_DISTANCE
    minimumActivationSeconds = multiplier * jumpFatigueConst.ACTIVATION_SECONDS_PER_DISTANCE
    multiplier = jumpFatigueConst.ADDITIONAL_DISTANCE + shipMaxDistance * shipMultiplier
    maxSecondsWhereDistanceMatters = multiplier * jumpFatigueConst.ACTIVATION_SECONDS_PER_DISTANCE
    remainingFatigueSec = remainingFatigue / const.SEC
    newActicationTimeRaw = remainingFatigueSec * jumpFatigueConst.FATIGUE_RATIO
    newActivationTime = max(minimumActivationSeconds, newActicationTimeRaw)
    return (newActivationTime, maxSecondsWhereDistanceMatters)


def FmtActivationTime(time):
    mins = localization.formatters.FormatNumeric(time / const.MIN, leadingZeroes=2)
    secs = localization.formatters.FormatNumeric(time % const.MIN / const.SEC, leadingZeroes=2)
    return localization.GetByLabel('/Carbon/UI/Common/DateTimeQuantity/DateTimeShort2Elements', value1=mins, value2=secs)
