#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\bracketsAndTargets\inSpaceBracket.py
import math
import weakref
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.util import timerstuff
from carbon.common.script.util.format import FmtAmt, FmtDate, FmtDist
from carbonui.fontconst import EVE_MEDIUM_FONTSIZE
from carbonui.primitives.bracket import Bracket
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
import overviewPresets.overviewSettingsConst as osConst
from eve.client.script.spacecomponents.activatecontroller import ActivateCounterController
from eve.client.script.spacecomponents.hostileBaiterController import HostileBaiterCounterController
from eve.client.script.spacecomponents.linkWithShipController import LinkWithShipCounterController
from eve.client.script.spacecomponents.proximitylockcontroller import ProximityLockCounterController
from eve.client.script.spacecomponents.reinforcecontroller import ReinforceCounterController
from eve.client.script.spacecomponents.jumppolarizationcontroller import JumpPolarizationCounterController
from eve.client.script.ui.control import eveIcon, eveLabel
from eve.client.script.ui.control.eveHint import BubbleHint
from eve.client.script.ui.control.hackingNumberGrid import HackingNumberGrid
from eve.client.script.ui.control.hackingProgressBar import HackingProgressBar
from eve.client.script.ui.inflight.bracket import BracketShadowLabel
from eve.client.script.ui.inflight.bracketsAndTargets import bracketVarious
from eve.client.script.ui.inflight.bracketsAndTargets.blinkingSpriteOnSharedCurve import BlinkingSpriteOnSharedCurve
from eve.client.script.ui.inflight.bracketsAndTargets.bracketVarious import BracketSubIconNew
from eve.client.script.ui.inflight.bracketsAndTargets.targetOnBracket import ActiveTargetOnBracket, TargetOnBracket
from eve.client.script.ui.inflight.squadrons.squadronManagementCont import SquadronNumber
from eve.client.script.ui.shared.fleet.fleetBroadcastConst import iconsByBroadcastType
from eve.client.script.ui.shared.maps.maputils import GetMyPos
from eve.client.script.ui.shared.stateFlag import FlagIconWithState, GetExtraInfoForSlimItem, GetIconFlagAndBackgroundFlag
from eve.client.script.util.bubble import SlimItemFromCharID
from eve.common.script.sys import idCheckers
import evetypes
from spacecomponents.common.helper import HasActivateComponent, HasReinforceComponent, HasJumpPolarizationComponent, HasProximityUnlockComponent, HasEntityStandingsComponent, HasLinkWithShipComponent, HasHostileBaiterComponent
import blue
import telemetry
import trinity
import carbonui.const as uiconst
import localization
from eve.client.script.parklife import states as state
import uthread
from eve.client.script.ui.shared.fleet import fleetbroadcastexports as fleetbr
from eve.client.script.ui.tooltips.tooltipHandler import TOOLTIP_DELAY_BRACKET, TOOLTIP_SETTINGS_BRACKET
import eve.common.script.mgt.entityConst as entityConst
import hackingcommon.hackingConstants as hackingConst
from carbonui.uicore import uicore
from eveprefs import prefs
from eveservices.menu import GetMenuService
import inventorycommon.util as invutil
SHOWLABELS_NEVER = 0
SHOWLABELS_ONMOUSEENTER = 1
SHOWLABELS_ALWAYS = 2
TARGETTING_UI_UPDATE_RATE = 50
LABELMARGIN = 6
TOOLTIPLABELCUTOFF = 150
TOOLTIPPANEL_HEIGHTCAP = 200
TOOLTIPPANEL_ENTRIESCAP = 10
TOOLTIP_OPACITY = 0.8
OWN_BRACKET_PATH = 'res:/UI/Texture/Shared/Brackets/ownShip.png'

class InSpaceBracket(Bracket):
    default_width = 16
    default_height = 16
    IsBracket = 1
    invisible = False
    inflight = False
    categoryID = None
    groupID = None
    itemID = None
    displayName = ''
    displaySubLabel = ''
    subItemsUpdateTimer = None
    subLabelCallback = None
    targetingPath = None
    stateItemID = None
    fleetBroadcastIcon = None
    fleetTagAndTarget = None
    label = None
    subLabel = None
    fadeColor = True
    iconNo = None
    iconXOffset = 0
    lastPosEvent = None
    scanAttributeChangeFlag = False
    iconTop = 0
    tagAndTargetStr = None
    squadronNumber = None
    _originalIconColor = None
    _fleetTag = None
    _fleetTargetNo = None
    _displayName = None
    _slimItem = None
    _ball = None

    def CloseSubLabel(self):
        if getattr(self, 'subLabel', None):
            self.subLabel.Close()
        self.subLabel = None

    def CloseLabel(self):
        if getattr(self, 'label', None):
            self.label.Close()
        self.label = None

    def Close(self, *args, **kw):
        self.subItemsUpdateTimer = None
        self.CloseLabel()
        self.CloseSubLabel()
        if getattr(self, 'fleetBroadcastIcon', None):
            self.fleetBroadcastIcon.Close()
            self.fleetBroadcastIcon = None
        if getattr(self, 'fleetTagAndTarget', None):
            self.fleetTagAndTarget.Close()
            self.fleetTagAndTarget = None
        if getattr(self, 'capture', None):
            self.capture.Close()
            self.capture = None
        Bracket.Close(self, *args, **kw)

    @telemetry.ZONE_METHOD
    def Startup(self, slimItem, ball = None, transform = None):
        self.iconNo, dockType, minDist, maxDist, iconOffset, logflag = self.data
        self.slimItem = slimItem
        self.itemID = slimItem.itemID
        self.typeID = slimItem.typeID
        self.groupID = slimItem.groupID
        self.categoryID = slimItem.categoryID
        self.sr.targetItem = None
        self.subLabelCallback = None
        self.controllers = []
        self.isSelected = None
        if not self.invisible:
            self.LoadIcon(self.iconNo)
        self.UpdateStructureState(slimItem)
        self.UpdateCaptureProgress(None)
        self.UpdatePlanetaryLaunchContainer(slimItem)
        self.SetBracketAnchoredState(slimItem)
        self.CreateSpaceComponentUI(slimItem)
        self.overrideLabel = False
        self.Load_update(slimItem)
        if self.itemID == session.shipid:
            if self.sr.icon:
                self.sr.icon.SetTexturePath(OWN_BRACKET_PATH)
            self.showMyIconDist = bracketVarious.GetMinDispRangeForOwnShip(self.slimItem.typeID)
            self.projectBracket.bracketUpdateCallback = self.OnOwnBracketUpdated

    def IsFloating(self):
        bracketRO = self.renderObject
        x, y = bracketRO.displayX, bracketRO.displayY
        bracketLayerWidth = self.parent.renderObject.displayWidth
        bracketLayerHeight = self.parent.renderObject.displayHeight
        if x <= 0:
            return False
        if y <= 0:
            return False
        if x + bracketRO.displayWidth >= bracketLayerWidth:
            return False
        if y + bracketRO.displayHeight >= bracketLayerHeight:
            return False
        return True

    def Show(self):
        projectBracket = self.projectBracket
        if projectBracket:
            projectBracket.bracket = self.renderObject
        Bracket.Show(self)

    def Hide(self):
        Bracket.Hide(self)
        self.KillLabel()
        projectBracket = self.projectBracket
        if projectBracket:
            projectBracket.bracket = None

    @telemetry.ZONE_METHOD
    def LoadIcon(self, iconNo):
        if getattr(self, 'noIcon', 0) == 1:
            return
        if self.sr.icon is None:
            icon = Sprite(parent=self, name='mainicon', state=uiconst.UI_DISABLED, pos=(0, 0, 16, 16), texturePath=iconNo, align=uiconst.CENTER)
            if self.fadeColor:
                self.color = icon.color
            else:
                icon.opacity = 0.75
            self.sr.icon = icon
        else:
            self.sr.icon.LoadIcon(iconNo)

    def UpdateIcon(self):
        if not self.sr.icon:
            return
        self.iconNo = sm.GetService('bracket').GetBracketIcon(self.slimItem.typeID, itemID=self.slimItem.itemID)
        self.sr.icon.LoadIcon(self.iconNo)

    def _ShowLabel(self):
        blue.pyos.synchro.SleepWallclock(50)
        if self.destroyed:
            return
        over = uicore.uilib.mouseOver
        if getattr(over, 'stateItemID', None) == self.itemID:
            self.ShowLabel()

    def ShowLabel(self, *args):
        if not self.destroyed and (self.displayName == '' or not getattr(self, 'showLabel', True)):
            return
        if self.overrideLabel and self.itemID == session.shipid:
            return
        if not self.label:
            self.label = BracketShadowLabel(parent=self.parent, name='labelparent', align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, text=self.displayName, bracket=self, idx=0)
        else:
            self.label.SetOrder(0)
        if self.SubLabelExists():
            self.subLabel.SetOrder(0)
        else:
            self.CreateSubLabelIfNeeded()
            return
        if hasattr(self, 'UpdateSubItems'):
            self.UpdateSubItems()

    def SubLabelExists(self):
        if self.subLabel is None:
            return False
        if self.subLabel.destroyed:
            return False
        return True

    def CreateSubLabelIfNeeded(self):
        if self.SubLabelExists():
            return
        if self.displaySubLabel:
            self.subLabel = BracketShadowLabel(parent=self.parent, name='sublabelparent', align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, text=self.displaySubLabel, bracket=self, color=(0.75, 0.75, 0.75, 0.75), idx=0)
        if hasattr(self, 'UpdateSubItems'):
            self.UpdateSubItems()

    def KillLabel(self, *args, **kwds):
        self.CloseLabel()
        self.CloseSubLabel()
        if hasattr(self, 'UpdateSubItems'):
            self.UpdateSubItems()

    @apply
    def ball():
        doc = ''

        def fget(self):
            if self._ball:
                return self._ball()

        def fset(self, value):
            if value is None:
                self._ball = None
                return
            self._ball = weakref.ref(value)

        return property(**locals())

    def GetSlimItem(self):
        return self.slimItem

    @apply
    def slimItem():

        def fget(self):
            if self._slimItem:
                return self._slimItem()
            else:
                return None

        def fset(self, value):
            if value is None:
                self._slimItem = None
            else:
                self._slimItem = weakref.ref(value)

        return property(**locals())

    @apply
    def displayName():
        doc = 'Property to dynamically fetch displayName if it hasnt been set'

        def fset(self, value):
            self._displayName = value

        def fget(self):
            if self._displayName:
                return self._displayName
            slimItem = self.slimItem
            if slimItem:
                self._displayName = sm.GetService('bracket').GetDisplayNameForBracket(slimItem)
            return self._displayName

        return property(**locals())

    def GetMenu(self):
        return GetMenuService().CelestialMenu(self.itemID, slimItem=self.slimItem)

    @telemetry.ZONE_METHOD
    def GetDistance(self):
        ball = self.ball
        if ball:
            return ball.surfaceDist
        slimItem = self.GetSlimItem()
        if slimItem:
            ballPark = sm.GetService('michelle').GetBallpark()
            if ballPark and slimItem.itemID in ballPark.balls:
                return ballPark.balls[slimItem.itemID].surfaceDist
        elif self.trackTransform or self.sr.trackTransform:
            tf = self.trackTransform or self.sr.trackTransform
            trans = tf.translation
            pos = trinity.TriVector(trans[0], trans[1], trans[2])
            myPos = GetMyPos()
            return (pos - myPos).Length()

    def HideBubble(self):
        if self.sr.bubble is not None:
            self.sr.bubble.Close()
            self.sr.bubble = None

    def ShowBubble(self, hint):
        if self.sr.bubble is not None:
            self.sr.bubble.Close()
            self.sr.bubble = None
        if hint:
            bubble = BubbleHint(parent=self, name='bubblehint', align=uiconst.TOPLEFT, width=0, height=0, idx=0, state=uiconst.UI_PICKCHILDREN)
            pointer = {const.groupStargate: 5,
             const.groupStation: 3}.get(self.groupID, 0)
            bubble.ShowHint(hint, pointer)
            self.sr.bubble = bubble
            self.sr.bubble.state = uiconst.UI_NORMAL

    def GetLockedPositionTopBottomMargin(self):
        hasBubble = bool(self.sr.bubble)
        topMargin = 1
        bottomMargin = 1
        if hasBubble:
            if self.sr.bubble.data[1] in (3, 4, 5):
                bottomMargin += self.sr.bubble.height + 8
            elif self.sr.bubble.data[1] in (0, 1, 2):
                topMargin += self.sr.bubble.height + 8
        else:
            if getattr(self, 'subLabel', None):
                bottomMargin += self.subLabel.textheight
            if getattr(self, 'fleetTagAndTarget', None):
                topMargin += self.fleetTagAndTarget.textheight
        return (topMargin, bottomMargin)

    def OnAttribute(self, attributeName, item, newValue):
        self.scanAttributeChangeFlag = True

    @telemetry.ZONE_METHOD
    def UpdateFlagPositions(self, icon = None):
        if icon is None:
            icon = self.sr.icon
        flag = self.sr.flag
        if icon and flag:
            if settings.user.overview.Get(osConst.SETTING_NAME_SMALL_TAGS, 0):
                flag.width = flag.height = 5
                flag.left = icon.left + 10
                flag.top = icon.top + 10
            else:
                flag.width = flag.height = 9
                flag.left = icon.left + 9
                flag.top = icon.top + 8

    @telemetry.ZONE_METHOD
    def CountDown(self, target):
        if self.destroyed:
            return
        self.scanAttributeChangeFlag = False
        if not target:
            return
        if not target.IsTargetingIndicatorsEnabled():
            return
        slimItem = self.slimItem
        source = eve.session.shipid
        time = sm.GetService('bracket').GetScanSpeed(source, slimItem)
        leftTimer = target.leftTimer
        rightTimer = target.rightTimer
        leftTimer.display = True
        rightTimer.display = True
        leftTimer.rotationSecondary = math.pi
        rightTimer.rotationSecondary = math.pi
        leftTimer.opacity = 0.4
        rightTimer.opacity = 0.4
        t = target.lockingText
        targetSvc = sm.GetService('target')
        startTime = targetSvc.GetTargetingStartTime(slimItem.itemID)
        if startTime is None:
            return
        lockedText = localization.GetByLabel('UI/Inflight/Brackets/TargetLocked')
        while not self.destroyed:
            if not target.IsTargetingIndicatorsEnabled():
                return
            now = blue.os.GetSimTime()
            dt = blue.os.TimeDiffInMs(startTime, now)
            if self.scanAttributeChangeFlag:
                waitRatio = dt / float(time)
                self.scanAttributeChangeFlag = False
                time = sm.GetService('bracket').GetScanSpeed(source, slimItem)
                startTime = now - long(time * waitRatio * 10000)
                dt = blue.os.TimeDiffInMs(startTime, now)
            if t.destroyed:
                return
            t.text = FmtAmt((time - dt) / 1000.0, showFraction=1)
            if dt > time:
                t.text = lockedText
                break
            ratio = (time - dt) / time
            if ratio > 0.5:
                rightTimer.rotationSecondary = math.pi + ratio * 2 * math.pi
                leftTimer.rotationSecondary = math.pi
            else:
                leftTimer.rotationSecondary = ratio * 2 * math.pi
                rightTimer.rotationSecondary = 0
            blue.pyos.synchro.Sleep(TARGETTING_UI_UPDATE_RATE)

        if not target.IsTargetingIndicatorsEnabled():
            return
        leftTimer.rotationSecondary = 0
        rightTimer.rotationSecondary = 0
        target.BlinkArrowsAndText()

    def GBEnemySpotted(self, active, fleetBroadcastID, charID):
        self.NearIDFleetBroadcast(active, fleetBroadcastID, charID, 'EnemySpotted')

    def GBNeedBackup(self, active, fleetBroadcastID, charID):
        self.NearIDFleetBroadcast(active, fleetBroadcastID, charID, 'NeedBackup')

    def GBInPosition(self, active, fleetBroadcastID, charID):
        self.NearIDFleetBroadcast(active, fleetBroadcastID, charID, 'InPosition')

    def GBHoldPosition(self, active, fleetBroadcastID, charID):
        self.NearIDFleetBroadcast(active, fleetBroadcastID, charID, 'HoldPosition')

    @telemetry.ZONE_METHOD
    def NearIDFleetBroadcast(self, active, fleetBroadcastID, charID, broadcastType):
        inBubble = bool(SlimItemFromCharID(charID))
        if inBubble:
            return self.FleetBroadcast(active, broadcastType, fleetBroadcastID, charID)
        if not active:
            if fleetBroadcastID == getattr(self, 'fleetBroadcastID', None):
                if self.fleetBroadcastIcon is not None:
                    self.fleetBroadcastIcon.Close()
                    self.fleetBroadcastIcon = None
                    self.UpdateSubItems()
                self.fleetBroadcastSender = self.fleetBroadcastType = self.fleetBroadcastID = None

    def GetHostileUI(self):
        if self.sr.hostile:
            return self.sr.hostile
        threat = BlinkingSpriteOnSharedCurve(parent=self, name='threatHostile', pos=(0, 0, 32, 32), align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Bracket/targetAggressIcon.png', curveSetName='sharedHostileCurveSet')
        self.sr.hostile = threat
        return threat

    def GetHostileAttackingUI(self):
        if self.sr.hostile_attacking:
            return self.sr.hostile_attacking
        threat = BlinkingSpriteOnSharedCurve(parent=self, name='threatAttacking', pos=(0, 0, 32, 32), align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Bracket/targetAggressIcon.png', curveSetName='sharedHostileCurveSet')
        self.sr.hostile_attacking = threat
        return threat

    @telemetry.ZONE_METHOD
    def GetHitSprite(self, create = True, *args):
        hitSprite = getattr(self, 'hitSprite', None)
        if hitSprite and not hitSprite.destroyed:
            return hitSprite
        if not create:
            return
        texturePath = 'res:/UI/Texture/classes/Bracket/damageDealer.png'
        hitSprite = Sprite(parent=self, name='hitSprite', pos=(0, 0, 100, 100), state=uiconst.UI_PICKCHILDREN, texturePath=texturePath, align=uiconst.CENTER, color=(1, 0, 0, 0))
        self.hitSprite = hitSprite
        return hitSprite

    @telemetry.ZONE_METHOD
    def GetCanTargetSprite(self, create = True, *args):
        canTargetSprite = getattr(self, 'canTargetSprite', None)
        if canTargetSprite and not canTargetSprite.destroyed:
            return canTargetSprite
        if not create:
            return
        canTargetSprite = Sprite(parent=self, name='canTargetSprite', pos=(0, 0, 40, 40), state=uiconst.UI_PICKCHILDREN, texturePath='res:/UI/Texture/classes/Bracket/canTarget2.png', align=uiconst.CENTER)
        self.canTargetSprite = canTargetSprite
        canTargetSprite.SetRGBA(1.0, 1.0, 1.0, 0.05)
        return canTargetSprite

    @telemetry.ZONE_METHOD
    def GetRadialMenuIndicator(self, create = True, *args):
        radialMenuSprite = getattr(self, 'radialMenuSprite', None)
        if radialMenuSprite and not radialMenuSprite.destroyed:
            return radialMenuSprite
        if not create:
            return
        radialMenuSprite = Sprite(name='radialMenuSprite', parent=self, texturePath='res:/UI/Texture/classes/RadialMenu/bracketHilite.png', pos=(0, 0, 20, 20), color=(0.5, 0.5, 0.5, 0.5), idx=-1, align=uiconst.CENTER, state=uiconst.UI_DISABLED)
        self.radialMenuSprite = radialMenuSprite
        return radialMenuSprite

    def GetActiveTargetUI(self):
        return ActiveTargetOnBracket(parent=self, itemID=self.itemID)

    def GetTargetedUI(self):
        return TargetOnBracket(parent=self)

    @telemetry.ZONE_METHOD
    def AddBinding(self, sourceObject, sourceAttribute, destObject, destAttribute, curveSet):
        binding = trinity.TriValueBinding()
        binding.sourceObject = sourceObject
        binding.sourceAttribute = sourceAttribute
        binding.destinationObject = destObject.GetRenderObject()
        binding.destinationAttribute = destAttribute
        curveSet.bindings.append(binding)
        return binding

    @telemetry.ZONE_METHOD
    def Select(self, status):
        wasSelected = self.isSelected
        self.isSelected = bool(status)
        if self.isSelected:
            if not self.sr.selection:
                self.sr.selection = Sprite(parent=self, pos=(0, 0, 30, 30), name='selection', state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Bracket/selectionCircle.png', align=uiconst.CENTER, color=(1, 1, 1, 0.5))
            self.sr.selection.display = True
            self.ShowLabel()
            sm.ScatterEvent('OnClientEvent_SelectSpaceBracket', self.slimItem)
        else:
            if self.sr.selection:
                self.sr.selection.state = uiconst.UI_HIDDEN
            if self.projectBracket and self.projectBracket.bracket:
                if not self.overrideLabel:
                    self.KillLabel()
        if bool(wasSelected) != bool(self.isSelected):
            sm.ScatterEvent('OnSpaceBracketSelectionChanged', self.slimItem)

    def OnOwnBracketUpdated(self, projectBracket):
        if self.sr.icon is None or self.sr.icon.destroyed or getattr(self.sr.icon, 'showingMyShip', False):
            return
        if projectBracket.cameraDistance > self.showMyIconDist and not self.overrideLabel:
            self.sr.icon.display = True
        else:
            self.sr.icon.display = False

    def ShowOwnShip(self):
        if self.sr.icon:
            self.sr.icon.display = True
            self.sr.icon.glowExpand = 0.01
            self.sr.icon.glowColor = const.OVERVIEW_OWN_SHIP_COLOR + (0.08,)
            self.sr.icon.showingMyShip = True

    def SetNormalInvisibleStateForOwnShip(self):
        if self.sr.icon:
            self.sr.icon.glowExpand = 0
            self.sr.icon.showingMyShip = False

    def OnMouseDown(self, *args):
        if getattr(self, 'slimItem', None):
            if GetMenuService().TryExpandActionMenu(self.itemID, self):
                return
        sm.GetService('viewState').GetView('inflight').layer.looking = True

    def OnMouseEnter(self, *args):
        if uicore.uilib.leftbtn:
            return
        if bracketVarious.IsTargetingOrSettingSecondPoint():
            return
        if not getattr(self, 'invisible', False) or self.itemID == session.shipid:
            PlaySound(uiconst.SOUND_ENTRY_HOVER)
            sm.GetService('stateSvc').SetState(self.itemID, state.mouseOver, 1)

    def OnMouseExit(self, *args):
        if uicore.uilib.leftbtn:
            return
        if self.projectBracket and self.projectBracket.bracket:
            sm.GetService('stateSvc').SetState(self.itemID, state.mouseOver, 0)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        uicore.layer.inflight.PrepareTooltipLoad(self)

    def GetTooltipDelay(self):
        return settings.user.ui.Get(TOOLTIP_SETTINGS_BRACKET, TOOLTIP_DELAY_BRACKET)

    def GetAbsolutePosition(self):
        if self.destroyed or not self.display:
            return (0, 0)
        x = self.renderObject.displayX
        y = self.renderObject.displayY
        parent = self.parent
        while parent:
            x += parent.renderObject.displayX
            y += parent.renderObject.displayY
            parent = parent.parent

        return (uicore.ReverseScaleDpi(x), uicore.ReverseScaleDpi(y))

    def OnClick(self, *args):
        if bracketVarious.IsTargetingOrSettingSecondPoint():
            uicore.layer.inflight.SetMouseDownAndDoMouseUp()
            return
        PlaySound(uiconst.SOUND_ENTRY_SELECT)
        if self.sr.clicktime and blue.os.TimeDiffInMs(self.sr.clicktime, blue.os.GetWallclockTime()) < 1000.0:
            sm.GetService('stateSvc').SetState(self.itemID, state.selected, 1)
            slimItem = getattr(self, 'slimItem', None)
            if slimItem:
                if uicore.cmd.IsSomeCombatCommandLoaded():
                    return
                GetMenuService().Activate(slimItem)
            self.sr.clicktime = None
        else:
            self.OnClickSelect()
            if sm.GetService('target').IsTarget(self.itemID):
                sm.GetService('stateSvc').SetState(self.itemID, state.activeTarget, 1)
            self.sr.clicktime = blue.os.GetWallclockTime()
        self.OnTacticalItemClick()

    def OnClickSelect(self):
        sm.GetService('stateSvc').SetState(self.itemID, state.selected, 1)

    def OnTacticalItemClick(self):
        GetMenuService().TacticalItemClicked(self.itemID)

    @telemetry.ZONE_METHOD
    def Load_update(self, slimItem, *args):
        if slimItem is None:
            return
        self.stateItemID = slimItem.itemID
        selected, hilited, attacking, hostile, targeting, targeted, activeTarget = sm.GetService('stateSvc').GetStates(self.stateItemID, [state.selected,
         state.mouseOver,
         state.threatAttackingMe,
         state.threatTargetsMe,
         state.targeting,
         state.targeted,
         state.activeTarget])
        self.Select(selected)
        self.Hilite(hilited)
        self.Targeted(targeted)
        self.ActiveTarget(activeTarget)
        self.UpdateIconColor(slimItem)
        if not activeTarget:
            self.Targeting(targeting)
        if self.updateItem:
            self.UpdateFlagAndBackground(slimItem)
            self.Attacking(attacking)
            self.Hostile(not attacking and hostile, attacking)
        else:
            if self.sr.flag:
                self.sr.flag.Close()
                self.sr.flag = None
            self.RemoveBackgroundColor()
            if self.sr.hostile_attacking:
                self._RemoveHostileAttackingUI()
            if self.sr.hostile:
                self._RemoveHostileUI()
        fleetTag = sm.GetService('fleet').GetTargetTag(slimItem.itemID)
        self.AddFleetTag(fleetTag)
        if slimItem.groupID == const.groupWreck:
            uthread.worker('bracket.WreckEmpty', self.WreckEmpty, slimItem.isEmpty)
        elif slimItem.hackingSecurityState is not None:
            uthread.new(self.SetHackingIcon, slimItem.hackingSecurityState)
        broadcastID, broadcastType, broadcastData = sm.GetService('fleet').GetCurrentFleetBroadcastOnItem(slimItem.itemID)
        if broadcastID is not None:
            uthread.worker('bracket.UpdateFleetBroadcasts', self.UpdateFleetBroadcasts, broadcastID, broadcastType, broadcastData)

    @telemetry.ZONE_METHOD
    def UpdateFleetBroadcasts(self, broadcastID, broadcastType, broadcastData):
        if self.destroyed:
            return
        for typeName in iconsByBroadcastType:
            if broadcastType == getattr(state, 'gb%s' % typeName):
                handler = getattr(self, 'GB%s' % typeName, None)
                if handler is None:
                    self.FleetBroadcast(True, typeName, broadcastID, *broadcastData)
                else:
                    handler(True, broadcastID, *broadcastData)
                break

    def RefreshBounty(self):
        self.UpdateFlagAndBackground(self.slimItem)

    def UpdateSquadronNumber(self, tubeFlagID):
        if tubeFlagID is None:
            if self.squadronNumber:
                self.squadronNumber.Close()
                self.squadronNumber = None
        else:
            self.squadronNumber = SquadronNumber(parent=self, top=-10, left=-10)
            self.squadronNumber.SetColor(False)
            self.squadronNumber.SetText(tubeFlagID)

    @telemetry.ZONE_METHOD
    def UpdateFlagAndBackground(self, slimItem, *args):
        if self.destroyed or not self.updateItem:
            return
        try:
            if slimItem.groupID != const.groupAgentsinSpace and (slimItem.ownerID and invutil.IsNPC(slimItem.ownerID) or slimItem.charID and invutil.IsNPC(slimItem.charID)) and slimItem.categoryID != const.categoryStation and slimItem.groupID != const.groupStargate:
                if self.sr.flag:
                    self.sr.flag.Close()
                    self.sr.flag = None
                self.RemoveBackgroundColor()
            else:
                stateSvc = sm.GetService('stateSvc')
                iconFlag, backgroundFlag = GetIconFlagAndBackgroundFlag(slimItem, stateSvc)
                icon = None
                if self.sr.icon and self.sr.icon.display:
                    icon = self.sr.icon
                if icon and iconFlag and iconFlag != -1:
                    if self.sr.flag is None:
                        self.sr.flag = FlagIconWithState(parent=self, state=uiconst.UI_DISABLED, align=uiconst.TOPLEFT)
                    flagInfo = stateSvc.GetStatePropsColorAndBlink(iconFlag)
                    self.sr.flag.ModifyIcon(flagInfo=flagInfo, showHint=False, extraInfo=GetExtraInfoForSlimItem(slimItem))
                    if settings.user.overview.Get(osConst.SETTING_NAME_SMALL_TAGS, 0):
                        self.sr.flag.ChangeFlagPos(icon.left + 10, icon.top + 10, 5, 5)
                    else:
                        self.sr.flag.ChangeFlagPos(icon.left + 9, icon.top + 8, 9, 9)
                    hideIcon = settings.user.overview.Get(osConst.SETTING_NAME_SMALL_TAGS, 0)
                    self.sr.flag.ChangeIconVisibility(display=not hideIcon)
                elif self.sr.flag:
                    self.sr.flag.Close()
                    self.sr.flag = None
                if backgroundFlag and backgroundFlag != -1:
                    r, g, b, a = stateSvc.GetStateBackgroundColor(backgroundFlag)
                    a = a * 0.5
                    if not self.sr.bgColor:
                        self.sr.bgColor = Sprite(bgParent=self, name='bgColor', texturePath='res:/UI/Texture/classes/Bracket/bracketBackground.png', color=(r,
                         g,
                         b,
                         a))
                    else:
                        self.sr.bgColor.SetRGBA(r, g, b, a)
                    blink = stateSvc.GetStateBackgroundBlink(backgroundFlag)
                    if blink:
                        if not self.sr.bgColor.HasAnimation('opacity'):
                            uicore.animations.FadeTo(self.sr.bgColor, startVal=0.0, endVal=a, duration=0.75, loops=uiconst.ANIM_REPEAT, curveType=uiconst.ANIM_WAVE)
                    else:
                        self.sr.bgColor.StopAnimations()
                elif self.sr.bgColor:
                    self.RemoveBackgroundColor()
                self.TryCorrectHostileUI()
        except AttributeError:
            if not self.destroyed:
                raise

    def RemoveBackgroundColor(self, *args):
        if self.sr.bgColor and self.sr.bgColor in self.background:
            self.background.remove(self.sr.bgColor)
            self.sr.bgColor = None

    @telemetry.ZONE_METHOD
    def UpdateIconColor(self, slimItem):
        if self.destroyed:
            return
        if self.sr.icon is None or not slimItem:
            return
        if self.sr.node and self.sr.node.iconColor is not None and not HasEntityStandingsComponent(slimItem.typeID):
            iconColor = self.sr.node.iconColor
        else:
            iconColor = bracketVarious.GetIconColor(slimItem)
        self.SetColor(*iconColor)
        if slimItem.groupID in (const.groupWreck, const.groupSpawnContainer) and sm.GetService('wreck').IsViewedWreck(slimItem.itemID):
            self.SetViewState(isViewed=True)

    def _IsFleetMember(self):
        if not session.fleetid or not self.slimItem or not self.slimItem.ownerID:
            return False
        return sm.GetService('fleet').IsMember(self.slimItem.ownerID)

    @telemetry.ZONE_METHOD
    def OnStateChange(self, itemID, flag, status, *args):
        if self.stateItemID != itemID:
            return
        if flag == state.mouseOver:
            self.Hilite(status)
        elif flag == state.selected:
            self.Select(status)
        elif flag == state.threatTargetsMe:
            attacking = sm.StartService('stateSvc').GetStates(itemID, [state.threatAttackingMe])
            if attacking is not None and len(attacking) > 0:
                attacking = attacking[0]
            else:
                attacking = 0
            self.Hostile(status, attacking=attacking)
        elif flag == state.threatAttackingMe:
            self.Attacking(status)
        elif flag == state.targeted:
            self.Targeted(status)
        elif flag == state.targeting:
            self.Targeting(status)
        elif flag == state.activeTarget:
            self.ActiveTarget(status)
        elif flag == state.flagWreckAlreadyOpened:
            self.SetViewState(isViewed=status)
        elif flag == state.flagWreckEmpty:
            self.WreckEmpty(status)
        else:
            for name in iconsByBroadcastType:
                if flag == getattr(state, 'gb%s' % name):
                    handler = getattr(self, 'GB%s' % name, None)
                    if handler is None:
                        self.FleetBroadcast(status, name, *args)
                    else:
                        handler(status, *args)
                    break

    def SetColor(self, r, g, b, _save = True):
        if _save:
            self._originalIconColor = (r, g, b)
        self.sr.icon.SetRGB(r, g, b)

    @telemetry.ZONE_METHOD
    def SetViewState(self, isViewed):
        if not self._originalIconColor:
            color = self.sr.icon.color
            self._originalIconColor = (color.r, color.g, color.b)
        r, g, b = self._originalIconColor
        if isViewed:
            attenuation = 0.55
            self.SetColor(r * attenuation, g * attenuation, b * attenuation, _save=False)
        else:
            self.SetColor(r, g, b, _save=False)

    def WreckEmpty(self, isEmpty):
        icon = sm.GetService('bracket').GetBracketIcon(self.slimItem.typeID, isEmpty)
        self.sr.icon.LoadIcon(icon)
        self.iconNo = icon

    def SetHackingIcon(self, securityState):
        iconNo, iconHint = InSpaceBracket.GetHackingIcon(securityState)
        self.sr.icon.LoadIcon(iconNo)
        self.iconNo = iconNo

    @staticmethod
    def GetHackingIcon(securityState):
        if securityState == hackingConst.hackingStateSecure:
            return ('res:/UI/Texture/Shared/Brackets/scatterContainerUnopened.png', '')
        elif securityState == hackingConst.hackingStateBeingHacked:
            return ('res:/UI/Texture/Shared/Brackets/scatterContainerBeingHacked.png', '')
        else:
            return ('res:/UI/Texture/Shared/Brackets/scatterContainerEmpty.png', localization.GetByLabel('Tooltips/Overview/ScatterContainerHacked'))

    def AddFleetTag(self, tag):
        self._fleetTag = tag
        self.UpdateFleetTagAndTarget()

    @telemetry.ZONE_METHOD
    def UpdateFleetTagAndTarget(self):
        tagAndTargetStr = ''
        if self._fleetTargetNo:
            tagAndTargetStr += unicode(self._fleetTargetNo)
        if self._fleetTag:
            if tagAndTargetStr:
                tagAndTargetStr += ' / '
            tagAndTargetStr += unicode(self._fleetTag)
        self.tagAndTargetStr = tagAndTargetStr
        if tagAndTargetStr:
            if not self.fleetTagAndTarget:
                self.fleetTagAndTarget = BracketShadowLabel(parent=self.parent, name='fleetTagAndTarget', align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, text=tagAndTargetStr, fontsize=EVE_MEDIUM_FONTSIZE, bracket=self, bold=True, idx=0)
            else:
                self.fleetTagAndTarget.text = tagAndTargetStr
        elif self.fleetTagAndTarget:
            self.fleetTagAndTarget.Close()
            self.fleetTagAndTarget = None
        self.UpdateSubItems()

    @telemetry.ZONE_METHOD
    def GBTarget(self, active, fleetBroadcastID, charID, targetNo = None):
        self.FleetBroadcast(active, 'Target', fleetBroadcastID, charID)
        if active:
            self._fleetTargetNo = targetNo
        else:
            self._fleetTargetNo = None
        self.UpdateFleetTagAndTarget()

    @telemetry.ZONE_METHOD
    def FleetBroadcast(self, active, broadcastType, fleetBroadcastID, charID):
        if active:
            self.fleetBroadcastSender = charID
            self.fleetBroadcastType = broadcastType
            self.fleetBroadcastID = fleetBroadcastID
            if self.fleetBroadcastIcon:
                self.fleetBroadcastIcon.Close()
                self.fleetBroadcastIcon = None
                self.UpdateSubItems()
            icon = iconsByBroadcastType[broadcastType]
            if not self.sr.icon and self.stateItemID != eve.session.shipid:
                self.LoadIcon(self.iconNo)
            self.fleetBroadcastIcon = BracketSubIconNew(icon=icon, parent=self.parent, state=uiconst.UI_NORMAL, name='fleetBroadcastIcon', bracket=self, hint=fleetbr.GetBroadcastName(broadcastType), idx=0, width=16, height=16)
            self.UpdateSubItems()
        elif fleetBroadcastID == getattr(self, 'fleetBroadcastID', None):
            if self.fleetBroadcastIcon:
                self.fleetBroadcastIcon.Close()
                self.fleetBroadcastIcon = None
                self.UpdateSubItems()
            self.fleetBroadcastSender = self.fleetBroadcastType = self.fleetBroadcastID = None

    def _UpdateSubItems(self):
        self.UpdateSubItems()

    def GetLabelMargin(self):
        if self.controllers:
            return LABELMARGIN + max((c.GetHorizontalLabelPixelOffset() for c in self.controllers))
        else:
            return LABELMARGIN

    def _UpdateFleetTagAndTargetOffset(self, bracketLayerWidth, labelsXOffset, mainLabelsYOffset, maxLabelWidth, x, y):
        maxLabelWidth = max(maxLabelWidth, self.fleetTagAndTarget.textwidth)
        xb, yb = self.fleetTagAndTarget.bindings
        labelMargin = self.GetLabelMargin()
        if x + self.width + labelMargin + maxLabelWidth > bracketLayerWidth:
            xb.offset = (self.ScaleDpi(-self.fleetTagAndTarget.textwidth) - labelMargin - labelsXOffset,
             0,
             0,
             0)
        else:
            xb.offset = (self.width + labelMargin + labelsXOffset,
             0,
             0,
             0)
        if y <= 0:
            tagLabelYShift = (self.height - self.fleetTagAndTarget.textheight) / 2 + 1
            yb.offset = (tagLabelYShift,
             0,
             0,
             0)
            mainLabelsYOffset = self.fleetTagAndTarget.textheight
        else:
            yb.offset = (-self.fleetTagAndTarget.textheight,
             0,
             0,
             0)
        return (mainLabelsYOffset, maxLabelWidth)

    def _UpdateLabelOffsets(self, bracketLayerWidth, labelsXOffset, mainLabelsYOffset, maxLabelWidth, x):
        xb, yb = self.label.bindings
        mainLabelsYOffset += (self.height - self.label.textheight) / 2 + 1
        yb.offset = (mainLabelsYOffset,
         0,
         0,
         0)
        labelMargin = self.GetLabelMargin()
        if x + self.width + labelMargin + maxLabelWidth > bracketLayerWidth:
            xb.offset = (self.ScaleDpi(-self.label.textwidth) - labelMargin - labelsXOffset,
             0,
             0,
             0)
            if self.subLabel:
                sxb, syb = self.subLabel.bindings
                sxb.offset = (self.ScaleDpi(-self.subLabel.textwidth) - labelMargin - labelsXOffset,
                 0,
                 0,
                 0)
                syb.offset = (mainLabelsYOffset + self.label.textheight,
                 0,
                 0,
                 0)
        else:
            xb.offset = (self.width + labelMargin + labelsXOffset,
             0,
             0,
             0)
            if self.subLabel:
                sxb, syb = self.subLabel.bindings
                sxb.offset = (self.width + labelMargin + labelsXOffset,
                 0,
                 0,
                 0)
                syb.offset = (mainLabelsYOffset + self.label.textheight,
                 0,
                 0,
                 0)

    def _UpdateFleetBroadcastIcon(self, bracketLayerWidth, labelsXOffset, x, y):
        xb, yb = self.fleetBroadcastIcon.bindings
        if x <= 0:
            xb.offset = (self.width + 2,
             0,
             0,
             0)
            yb.offset = ((self.height - self.fleetBroadcastIcon.height) / 2,
             0,
             0,
             0)
            labelsXOffset = self.fleetBroadcastIcon.width
        elif x + self.width >= bracketLayerWidth:
            xb.offset = (-self.fleetBroadcastIcon.width - 2,
             0,
             0,
             0)
            yb.offset = ((self.height - self.fleetBroadcastIcon.height) / 2,
             0,
             0,
             0)
            labelsXOffset = self.fleetBroadcastIcon.width
        elif self.projectBracket and self.projectBracket.bracket:
            xb.offset = ((self.width - self.fleetBroadcastIcon.width) / 2,
             0,
             0,
             0)
            if y <= 0:
                yb.offset = (self.fleetBroadcastIcon.height,
                 0,
                 0,
                 0)
            else:
                yb.offset = (-self.fleetBroadcastIcon.height,
                 0,
                 0,
                 0)
        else:
            yb.offset = ((self.height - self.fleetBroadcastIcon.height) / 2,
             0,
             0,
             0)
            xb.offset = (-self.fleetBroadcastIcon.width - 2,
             0,
             0,
             0)
        return labelsXOffset

    def UpdateSubLabelText(self):
        if self.subLabel is None:
            return
        if not self.subLabelCallback:
            return
        self.displaySubLabel = self.subLabelCallback()
        self.subLabel.text = self.displaySubLabel or ''

    def GetSubLabelCallback(self):
        return self.subLabelCallback

    def SetSubLabelCallback(self, callback):
        self.subLabelCallback = callback
        self.displaySubLabel = callback()

    def RemoveSubLabelCallback(self, callback):
        if callback != self.subLabelCallback:
            return
        self.subLabelCallback = None
        self.CloseSubLabel()
        self.displaySubLabel = None

    @telemetry.ZONE_METHOD
    def UpdateSubItems(self):
        if self.destroyed:
            return
        bracketRO = self.renderObject
        x, y = bracketRO.displayX, bracketRO.displayY
        bracketLayerWidth = uicore.layer.bracket.renderObject.displayWidth
        labelsXOffset = 0
        if self.fleetBroadcastIcon:
            labelsXOffset = self._UpdateFleetBroadcastIcon(bracketLayerWidth, labelsXOffset, x, y)
        if self.label:
            newStr = self.displayName
            if newStr is None:
                sm.GetService('bracket').RemoveBracket(self.itemID)
                return
            if hasattr(self, 'GetDocked'):
                docked = self.GetDocked()
                if docked is not None:
                    newStr += ' [{}]'.format(docked)
            if getattr(self, 'showDistance', 1):
                distance = self.GetDistance()
                if distance:
                    newStr += ' ' + FmtDist(distance)
            self.label.text = newStr
        elif self.slimItem.categoryID == 6 and self.slimItem.groupID != 29:
            if prefs.GetValue('bracketsAlwaysShowShipText', False):
                self.ShowLabel()
                self.overrideLabel = True
            else:
                self.overrideLabel = False
        self.UpdateSubLabelText()
        mainLabelsYOffset = 0
        maxLabelWidth = 0
        if self.label:
            maxLabelWidth = max(maxLabelWidth, self.label.textwidth)
        if self.SubLabelExists():
            maxLabelWidth = max(maxLabelWidth, self.subLabel.textwidth)
        if self.fleetTagAndTarget:
            self.fleetTagAndTarget.display = self.display
            mainLabelsYOffset, maxLabelWidth = self._UpdateFleetTagAndTargetOffset(bracketLayerWidth, labelsXOffset, mainLabelsYOffset, maxLabelWidth, x, y)
        if self.label:
            self._UpdateLabelOffsets(bracketLayerWidth, labelsXOffset, mainLabelsYOffset, maxLabelWidth, x)
        if not (self.label or self.subLabel or self.fleetBroadcastIcon or self.fleetTagAndTarget):
            self.subItemsUpdateTimer = None
        elif not getattr(self, 'subItemsUpdateTimer', None):
            self.subItemsUpdateTimer = timerstuff.AutoTimer(500, self._UpdateSubItems)

    def getActiveStateOverride(self, activeState):
        targetSvc = sm.GetService('target')
        if targetSvc.disableSpinnyReticule:
            activeState = False
        return activeState

    @telemetry.ZONE_METHOD
    def ActiveTarget(self, activestate):
        activestate = self.getActiveStateOverride(activestate)
        if activestate:
            if not self.sr.activeTarget:
                self.sr.activeTarget = self.GetActiveTargetUI()
            if self.sr.targetItem:
                self.sr.targetItem.ChangeLineOpacity(faded=0)
        else:
            if self.sr.activeTarget:
                self.sr.activeTarget.Close()
                self.sr.activeTarget = None
            if self.sr.targetItem:
                self.sr.targetItem.ChangeLineOpacity(faded=1)

    @telemetry.ZONE_METHOD
    def Targeted(self, state):
        state = self.getActiveStateOverride(state)
        if state:
            if not self.sr.targetItem:
                targ = self.GetTargetedUI()
                lines = targ.lines
                targetCrosshair = sm.GetService('overviewPresetSvc').GetSettingValueOrDefaultFromName(osConst.SETTING_TARGET_CROSSHAIR, True)
                if not targetCrosshair:
                    lines.display = False
                else:
                    lines.display = True
                    bracketVarious.FixLines(targ)
                self.sr.targetItem = targ
            circle = self.sr.targetItem.circle
            if circle is not None and not circle.destroyed:
                circle.state = uiconst.UI_DISABLED
        else:
            if self.sr.activeTarget:
                self.sr.activeTarget.Close()
                self.sr.activeTarget = None
            if self.sr.targetItem:
                self.sr.targetItem.Close()
                self.sr.targetItem = None

    @telemetry.ZONE_METHOD
    def Targeting(self, state):
        state = self.getActiveStateOverride(state)
        if state:
            if self.sr.targetItem is None or self.sr.targetItem.destroyed:
                self.Targeted(1)
            if self.sr.targetItem:
                uthread.new(self.CountDown, self.sr.targetItem)
                self.sr.targetItem.ShowTargetingIndicators()
        elif self.sr.targetItem:
            self.sr.targetItem.HideTargetingIndicators()

    @telemetry.ZONE_METHOD
    def Hilite(self, status):
        if status and self.state != uiconst.UI_HIDDEN:
            if self.IsFloating():
                uthread.pool('Bracket::Hilite', self._ShowLabel)
            if not self.sr.hilite:
                self.sr.hilite = Sprite(parent=self, pos=(0, 0, 30, 30), name='hilite', state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Bracket/selectionCircle.png', align=uiconst.CENTER, color=(1, 1, 1, 0.3))
            self.sr.hilite.Show()
        else:
            if self.projectBracket and self.projectBracket.bracket and sm.GetService('stateSvc').GetExclState(state.selected) != self.itemID:
                self.KillLabel()
            if self.sr.hilite:
                self.sr.hilite.Close()
                self.sr.hilite = None

    @telemetry.ZONE_METHOD
    def Hostile(self, state, attacking = 0):
        if state:
            if self.sr.hostile_attacking is not None:
                self._RemoveHostileAttackingUI()
            fleetMember = self._IsFleetMember()
            yellowColor = (1, 0.8, 0, 0.5)
            if fleetMember:
                color = sm.GetService('bracket').GetFleetBracketColor() or yellowColor
            else:
                color = yellowColor
            attckingIcon = self.GetHostileUI()
            attckingIcon.SetRGBA(*color)
            attckingIcon.state = uiconst.UI_DISABLED
        elif not attacking and self.sr.hostile:
            self._RemoveHostileUI()
        self.UpdateIconColor(self.slimItem)

    def _RemoveHostileAttackingUI(self):
        self.sr.hostile_attacking.Close()
        self.sr.hostile_attacking = None

    def _RemoveHostileUI(self):
        attckingIcon = self.sr.hostile
        self.sr.hostile = None
        attckingIcon.Close()

    def TryCorrectHostileUI(self):
        if not self.sr.hostile:
            return
        isFleetMember = self._IsFleetMember()
        if getattr(self.sr.hostile, 'isFleetMember', False) != isFleetMember:
            self.Hostile(1)

    @telemetry.ZONE_METHOD
    def Attacking(self, state):
        if state:
            if self.sr.hostile is not None:
                self._RemoveHostileUI()
            attckingIcon = self.GetHostileAttackingUI()
            attckingIcon.SetRGBA(0.8, 0, 0, 0.3)
            attckingIcon.state = uiconst.UI_DISABLED
        elif self.itemID in sm.GetService('target').GetTargetedBy():
            self.Hostile(1)
        elif self.sr.hostile_attacking:
            attckingIcon = self.sr.hostile_attacking
            self.sr.hostile_attacking = None
            attckingIcon.Close()
        self.UpdateIconColor(self.slimItem)

    @telemetry.ZONE_METHOD
    def UpdateStructureState(self, slimItem):
        if not idCheckers.IsStarbase(slimItem.categoryID):
            return
        self.lastPosEvent = blue.os.GetWallclockTime()
        stateName, stateTimestamp, stateDelay = sm.GetService('pwn').GetStructureState(slimItem)
        if self.sr.posStatus is None:
            self.sr.posStatus = eveLabel.EveLabelSmall(text=entityConst.POS_STRUCTURE_STATE[stateName], parent=self, left=24, top=30, state=uiconst.UI_NORMAL)
        else:
            self.sr.posStatus.text = entityConst.POS_STRUCTURE_STATE[stateName]
        if stateName in ('anchoring', 'onlining', 'unanchoring', 'reinforced', 'operating', 'incapacitated'):
            uthread.new(self.StructureProgress, self.lastPosEvent, stateName, stateTimestamp, stateDelay)

    @telemetry.ZONE_METHOD
    def UpdateOrbitalState(self, slimItem):
        if not idCheckers.IsOrbital(slimItem.categoryID):
            return
        self.lastOrbitalEvent = blue.os.GetWallclockTime()
        if slimItem.orbitalState in (entityConst.STATE_ANCHORING, entityConst.STATE_ONLINING, entityConst.STATE_SHIELD_REINFORCE) or slimItem.groupID == const.groupOrbitalConstructionPlatforms:
            statusString = bracketVarious.GetEntityStateString(slimItem.orbitalState)
            if self.sr.orbitalStatus is None:
                self.sr.orbitalStatus = eveLabel.EveLabelSmall(text=statusString, parent=self, left=24, top=30, state=uiconst.UI_NORMAL)
            else:
                self.sr.orbitalStatus.text = statusString
        if slimItem.orbitalState in (entityConst.STATE_UNANCHORED, entityConst.STATE_IDLE, entityConst.STATE_ANCHORED) and slimItem.groupID != const.groupOrbitalConstructionPlatforms:
            if self.sr.orbitalStatus is not None:
                self.sr.orbitalStatus.Close()
                self.sr.orbitalStatus = None
        if slimItem.orbitalHackerID is not None:
            if self.sr.orbitalHack is None:
                self.sr.orbitalHack = HackingNumberGrid(parent=self, width=140, height=140, numCellRows=7, cellsPerRow=7, cellHeight=20, cellWidth=20, align=uiconst.CENTERTOP, top=-150)
                self.sr.orbitalHack.BeginColorCycling()
            progress = 0.0 if slimItem.orbitalHackerProgress is None else slimItem.orbitalHackerProgress
            self.sr.orbitalHack.SetProgress(progress)
        elif self.sr.orbitalHack is not None:
            self.sr.orbitalHack.StopColorCycling()
            self.children.remove(self.sr.orbitalHack)
            self.sr.orbitalHack = None
        if slimItem.orbitalState in (entityConst.STATE_ONLINING,
         entityConst.STATE_OFFLINING,
         entityConst.STATE_ANCHORING,
         entityConst.STATE_UNANCHORING,
         entityConst.STATE_SHIELD_REINFORCE):
            uthread.new(self.OrbitalProgress, self.lastOrbitalEvent, slimItem)

    @telemetry.ZONE_METHOD
    def UpdatePlanetaryLaunchContainer(self, slimItem):
        if slimItem.typeID != const.typePlanetaryLaunchContainer:
            return
        uthread.new(self._UpdatePlanetaryLaunchContainer, slimItem)

    @telemetry.ZONE_METHOD
    def _UpdatePlanetaryLaunchContainer(self, slimItem):
        cnt = 0
        while slimItem.launchTime is None and cnt < 90:
            blue.pyos.synchro.SleepWallclock(1000)
            cnt += 1

        if getattr(self, 'planetaryLaunchContainerThreadRunning', False) == False and slimItem.launchTime is not None:
            uthread.new(self.PlanetaryLaunchContainerProgress, slimItem.launchTime, long(slimItem.launchTime + const.piLaunchOrbitDecayTime))

    @telemetry.ZONE_METHOD
    def PlanetaryLaunchContainerProgress(self, startTime, endTime):
        self.planetaryLaunchContainerThreadRunning = True
        try:
            boxwidth = 82
            fillwidth = boxwidth - 2
            boxheight = 14
            fillheight = boxheight - 2
            boxtop = 30
            filltop = boxtop + 1
            boxleft = -(boxwidth / 2) + 5
            fillleft = boxleft + 1
            boxcolor = (1.0, 1.0, 1.0, 0.35)
            fillcolor = (1.0, 1.0, 1.0, 0.25)
            if not hasattr(self, 'burnupFill'):
                self.burnupFill = Fill(parent=self, align=uiconst.RELATIVE, width=fillwidth, height=fillheight, left=fillleft, top=filltop, color=fillcolor)
            burnupFill = self.burnupFill
            if not hasattr(self, 'burnupTimeText'):
                self.burnupTimeText = eveLabel.EveLabelSmall(text=' ', parent=self, left=-10, top=32, lineSpacing=0.2, state=uiconst.UI_NORMAL)
            timeText = self.burnupTimeText
            if not hasattr(self, 'burnupFrame'):
                self.burnupFrame = Frame(parent=self, align=uiconst.RELATIVE, width=boxwidth, height=boxheight, left=boxleft, top=boxtop, color=boxcolor)
            frame = self.burnupFrame
            while not self.destroyed and self.planetaryLaunchContainerThreadRunning:
                currentTime = blue.os.GetWallclockTime()
                portion = float(currentTime - startTime) / (endTime - startTime)
                if portion > 1.0:
                    break
                width = min(int(portion * fillwidth), fillwidth)
                width = fillwidth - abs(width)
                if burnupFill.width != width:
                    burnupFill.width = width
                newTimeText = FmtDate(endTime - currentTime, 'ss')
                if timeText.text != newTimeText:
                    timeText.text = newTimeText
                    timeText.left = -32
                blue.pyos.synchro.SleepWallclock(1000)

        finally:
            self.planetaryLaunchContainerThreadRunning = False

    @telemetry.ZONE_METHOD
    def UpdateCaptureProgress(self, captureData):
        slimItem = self.slimItem
        if slimItem.groupID not in (const.groupCapturePointTower, const.groupSatellite):
            return
        if captureData:
            self.captureData = captureData
        else:
            self.captureData = sm.GetService('bracket').GetCaptureData(self.itemID)
        if not self.captureData:
            return
        if self.captureData.get('completion'):
            self.captureData['points'] = 100.0 - (self.captureData['completion'] - blue.os.GetSimTime()) / (self.captureData['captureTime'] * const.MIN) * 100.0
        if not getattr(self, 'captureTaskletRunning', False):
            uthread.new(self.CaptureProgress)

    def GetCaptureProgress(self):
        portion = float(self.captureData['points']) / 100
        if self.captureData.get('captureID') != 'contested':
            difference = blue.os.TimeDiffInMs(self.captureData['lastIncident'], blue.os.GetSimTime())
            portion += float(difference) / self.captureData['captureTime'] / 60 / 1000
        return min(max(portion, -1), 1)

    @telemetry.ZONE_METHOD
    def CaptureProgress(self):
        self.captureTaskletRunning = True
        try:
            boxwidth = 82
            fillwidth = boxwidth - 2
            boxheight = 14
            fillheight = boxheight - 2
            boxtop = 30
            filltop = boxtop + 1
            boxleft = -(boxwidth / 2) + 5
            fillleft = boxleft + 1
            boxcolor = (1.0, 1.0, 1.0, 0.35)
            fillcolor = (1.0, 1.0, 1.0, 0.25)
            if not getattr(self, 'capture', None):
                self.capture = Container(parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED)
                self.sr.captureFrame = Frame(parent=self.capture, align=uiconst.RELATIVE, width=boxwidth, height=boxheight, left=boxleft, top=boxtop, color=boxcolor)
                self.sr.captureState = Fill(parent=self.capture, align=uiconst.RELATIVE, width=0, height=fillheight, left=fillleft, top=filltop, color=fillcolor)
                self.sr.captureStateText = eveLabel.EveLabelSmall(text=' ', parent=self.capture, left=boxleft, top=boxtop + boxheight + 2, state=uiconst.UI_DISABLED)
                self.sr.captureStateTimeText = eveLabel.EveLabelSmall(text=' ', parent=self.capture, left=-10, top=filltop + 1, state=uiconst.UI_DISABLED)
                self.sr.captureLogo = None
            while not self.destroyed:
                self.capture.state = uiconst.UI_DISABLED
                progress = self.GetCaptureProgress()
                if self.captureData.get('captureID') is None and self.captureData['lastCapturing'] is None:
                    self.capture.Close()
                    self.capture = None
                    return
                if self.GetDistance() > const.minCaptureBracketDistance:
                    self.capture.state = uiconst.UI_HIDDEN
                elif progress == 1 and self.captureData['lastCapturing']:
                    self.SetCaptureLogo(self.captureData['lastCapturing'])
                    self.sr.captureState.width = abs(int(progress * fillwidth))
                    self.sr.captureStateText.text = cfg.eveowners.Get(self.captureData['lastCapturing']).name
                    self.sr.captureStateTimeText.text = self.GetCaptureTimeString(progress)
                elif self.captureData.get('captureID') == 'contested':
                    self.SetCaptureLogo(self.captureData['lastCapturing'])
                    self.sr.captureState.width = abs(int(progress * fillwidth))
                    self.sr.captureStateText.text = localization.GetByLabel('UI/Inflight/Brackets/SystemContested')
                    self.sr.captureStateTimeText.text = self.GetCaptureTimeString(progress)
                elif self.captureData.get('captureID'):
                    if progress < 0.0:
                        self.SetCaptureLogo(self.captureData['lastCapturing'])
                    else:
                        self.SetCaptureLogo(self.captureData['captureID'])
                    self.sr.captureState.width = abs(int(progress * fillwidth))
                    self.sr.captureStateText.text = localization.GetByLabel('UI/Inflight/Brackets/FacWarCapturing', ownerName=cfg.eveowners.Get(self.captureData['captureID']).name)
                    self.sr.captureStateTimeText.text = self.GetCaptureTimeString(progress)
                    self.sr.captureStateTimeText.left = -8
                blue.pyos.synchro.SleepWallclock(900)

        finally:
            self.captureTaskletRunning = False

    @telemetry.ZONE_METHOD
    def GetCaptureTimeString(self, portion):
        if self.captureData['captureID'] == 'contested':
            return ' '
        timeScalar = 1 - portion
        if timeScalar <= 0:
            return localization.GetByLabel('UI/Inflight/Brackets/FacWarCaptured')
        maxTime = self.captureData['captureTime']
        timeLeft = timeScalar * maxTime
        properTime = long(60000L * const.dgmTauConstant * timeLeft)
        return FmtDate(properTime, 'ns')

    @telemetry.ZONE_METHOD
    def SetCaptureLogo(self, teamID):
        if teamID == 'contested' or teamID is None:
            return
        if self.sr.Get('captureLogo'):
            if self.sr.captureLogo.name == cfg.eveowners.Get(teamID).name:
                self.sr.captureLogo.state = uiconst.UI_DISABLED
                return
            self.sr.captureLogo.Close()
        itemID = const.raceByFaction.get(teamID, teamID)
        self.sr.captureLogo = eveIcon.LogoIcon(itemID=itemID, parent=self.capture, state=uiconst.UI_DISABLED, size=32, pos=(-70, 22, 32, 32), name=cfg.eveowners.Get(teamID).name, align=uiconst.RELATIVE, ignoreSize=True, isSmall=True)

    @telemetry.ZONE_METHOD
    def StructureProgress(self, lastPosEvent, stateName, stateTimestamp, stateDelay):
        if self.destroyed:
            return
        t = self.sr.posStatus
        Frame(parent=self, align=uiconst.RELATIVE, width=82, height=13, left=18, top=30, color=(1.0, 1.0, 1.0, 0.5))
        p = Fill(parent=self, align=uiconst.RELATIVE, width=80, height=11, left=19, top=31, color=(1.0, 1.0, 1.0, 0.25))
        startTime = blue.os.GetWallclockTime()
        if stateDelay:
            stateDelay = float(stateDelay * const.MSEC)
        doneStr = {'anchoring': localization.GetByLabel('UI/Entities/States/Anchored'),
         'onlining': localization.GetByLabel('UI/Entities/States/Online'),
         'unanchoring': localization.GetByLabel('UI/Entities/States/Unanchored'),
         'reinforced': localization.GetByLabel('UI/Entities/States/Online'),
         'operating': localization.GetByLabel('UI/Entities/States/Operating'),
         'incapacitated': localization.GetByLabel('UI/Entities/States/Incapacitated')}.get(stateName, localization.GetByLabel('UI/Entities/States/Done'))
        endTime = 0
        if stateDelay:
            endTime = stateTimestamp + stateDelay
        while 1 and endTime:
            if not self or self.destroyed or lastPosEvent != self.lastPosEvent:
                return
            timeLeft = endTime - blue.os.GetWallclockTime()
            portion = timeLeft / stateDelay
            timeLeftSec = timeLeft / 1000.0
            if timeLeft <= 0:
                t.text = doneStr
                break
            t.text = localization.GetByLabel('UI/Inflight/Brackets/StructureProgress', stateName=entityConst.POS_STRUCTURE_STATE[stateName], timeRemaining=long(timeLeft))
            p.width = int(80 * portion)
            blue.pyos.synchro.SleepWallclock(900)

        blue.pyos.synchro.SleepWallclock(250)
        if not self or self.destroyed:
            return
        for each in self.children[-2:]:
            if each is not None and not getattr(each, 'destroyed', 0):
                each.Close()

        if lastPosEvent != self.lastPosEvent:
            return
        t.text = ''
        blue.pyos.synchro.SleepWallclock(250)
        if not self or self.destroyed or lastPosEvent != self.lastPosEvent:
            return
        t.text = doneStr
        blue.pyos.synchro.SleepWallclock(250)
        if not self or self.destroyed or lastPosEvent != self.lastPosEvent:
            return
        t.text = ''
        blue.pyos.synchro.SleepWallclock(250)
        if not self or self.destroyed or lastPosEvent != self.lastPosEvent:
            return
        t.text = doneStr

    @telemetry.ZONE_METHOD
    def OrbitalProgress(self, lastOrbitalEvent, slimItem):
        if self.destroyed:
            return
        t = self.sr.orbitalStatus
        Frame(parent=self, align=uiconst.TOPLEFT, width=82, height=13, left=18, top=30, color=(1.0, 1.0, 1.0, 0.5))
        p = Fill(parent=self, align=uiconst.TOPLEFT, width=80, height=11, left=19, top=31, color=(1.0, 1.0, 1.0, 0.25))
        stateName = bracketVarious.GetEntityStateString(slimItem.orbitalState)
        stateTimestamp = slimItem.orbitalTimestamp
        stateDelay = None
        doneText = localization.GetByLabel('UI/Entities/States/Done')
        godmaSM = sm.GetService('godma').GetStateManager()
        if slimItem.orbitalState == entityConst.STATE_ANCHORING:
            stateDelay = godmaSM.GetType(slimItem.typeID).anchoringDelay
            doneText = bracketVarious.GetEntityStateString(entityConst.STATE_ANCHORED)
        elif slimItem.orbitalState == entityConst.STATE_ONLINING:
            stateName = localization.GetByLabel('UI/Entities/States/Upgrading')
            stateDelay = godmaSM.GetType(slimItem.typeID).onliningDelay
            doneText = localization.GetByLabel('UI/Entities/States/Online')
        elif slimItem.orbitalState == entityConst.STATE_UNANCHORING:
            stateDelay = godmaSM.GetType(slimItem.typeID).unanchoringDelay
            doneText = bracketVarious.GetEntityStateString(entityConst.STATE_UNANCHORED)
        elif slimItem.orbitalState == entityConst.STATE_SHIELD_REINFORCE:
            doneText = bracketVarious.GetEntityStateString(entityConst.STATE_ANCHORED)
        if stateDelay:
            stateDelay = float(stateDelay * const.MSEC)
        else:
            stateDelay = const.DAY
        timeLeft = stateTimestamp - blue.os.GetWallclockTime()
        try:
            while timeLeft > 0:
                blue.pyos.synchro.SleepWallclock(900)
                if not self or self.destroyed or lastOrbitalEvent != self.lastOrbitalEvent:
                    return
                timeLeft = stateTimestamp - blue.os.GetWallclockTime()
                portion = max(0.0, min(1.0, timeLeft / stateDelay))
                t.text = localization.GetByLabel('UI/Inflight/Brackets/StructureProgress', stateName=stateName, timeRemaining=long(timeLeft))
                p.width = int(80 * portion)

            t.text = doneText
            blue.pyos.synchro.SleepWallclock(250)
            if not self or self.destroyed:
                return
        finally:
            if self and not self.destroyed:
                t.text = doneText
                for each in self.children[-2:]:
                    if each is not None and not getattr(each, 'destroyed', 0):
                        each.Close()

        if lastOrbitalEvent != self.lastOrbitalEvent:
            return
        t.text = ''
        blue.pyos.synchro.SleepWallclock(250)
        if not self or self.destroyed or lastOrbitalEvent != self.lastOrbitalEvent:
            return
        t.text = doneText
        blue.pyos.synchro.SleepWallclock(250)
        if not self or self.destroyed or lastOrbitalEvent != self.lastOrbitalEvent:
            return
        t.text = ''
        blue.pyos.synchro.SleepWallclock(250)
        if not self or self.destroyed or lastOrbitalEvent != self.lastOrbitalEvent:
            return
        t.text = doneText

    @telemetry.ZONE_METHOD
    def SetBracketAnchoredState(self, slimItem):
        if not evetypes.GetIsGroupAnchorableByGroup(slimItem.groupID):
            return
        if not slimItem or slimItem.itemID == eve.session.shipid or slimItem.ownerID != eve.session.charid and slimItem.ownerID != eve.session.corpid:
            return
        ball = self.ball
        if ball is None:
            bp = sm.GetService('michelle').GetBallpark()
            ball = bp.GetBall(slimItem.itemID)
            if not ball:
                return
        _iconNo, _dockType, _minDist, _maxDist, _iconOffset, _logflag = sm.GetService('bracket').GetBracketProps(slimItem, ball)
        iconNo, dockType, minDist, maxDist, iconOffset, logflag = self.data
        for each in self.children:
            if each.name == 'anchoredicon':
                if ball.isFree:
                    self.data = (iconNo,
                     dockType,
                     _minDist,
                     _maxDist,
                     iconOffset,
                     logflag)
                    each.Close()
                return

        if not ball.isFree:
            self.data = (iconNo,
             dockType,
             0.0,
             1e+32,
             iconOffset,
             logflag)
            Sprite(icon='res:/UI/Texture/Icons/38_16_15', name='anchoredicon', parent=self, pos=(0, 16, 16, 16), align=uiconst.TOPLEFT)

    @telemetry.ZONE_METHOD
    def UpdateHackProgress(self, hackProgress):
        if self.sr.orbitalHackLocal is None:
            return
        self.sr.orbitalHackLocal.SetValue(hackProgress)

    @telemetry.ZONE_METHOD
    def BeginHacking(self):
        if self.sr.orbitalHackLocal is None:
            self.sr.orbitalHackLocal = HackingProgressBar(parent=self, height=20, width=120, align=uiconst.CENTERBOTTOM, top=-50, color=(0.0, 0.8, 0.0, 1.0), backgroundColor=(0.25, 0.0, 0.0, 1.0))

    def _StopHacking(self):
        blue.pyos.synchro.SleepWallclock(5000)
        if self and self.sr.orbitalHackLocal:
            self.sr.orbitalHackLocal.state = uiconst.UI_HIDDEN
            self.sr.orbitalHackLocal.Close()
            self.sr.orbitalHackLocal = None

    def StopHacking(self, success = False):
        if self.sr.orbitalHackLocal is not None:
            self.sr.orbitalHackLocal.Finalize(complete=success)
            uthread.new(self._StopHacking)

    def ShowRadialMenuIndicator(self, slimItem = None, *args):
        if getattr(self, 'invisible', False) and (self.sr.selection is None or not self.sr.selection.display):
            return
        mySprite = self.GetRadialMenuIndicator(create=True)
        mySprite.display = True

    def HideRadialMenuIndicator(self, slimItem = None, *args):
        mySprite = self.GetRadialMenuIndicator(create=False)
        if mySprite:
            mySprite.display = False

    def CreateCounterController(self, controllerClass, componentRegistry, slimItem):
        try:
            controller = controllerClass(self, componentRegistry, slimItem)
            self.controllers.append(controller)
        except KeyError:
            pass

    def GetCounterControllerForClass(self, controllerClass):
        for c in self.controllers:
            if isinstance(c, controllerClass):
                return c

    def CreateSpaceComponentUI(self, slimItem):
        bp = sm.GetService('michelle').GetBallpark()
        if bp is not None:
            componentRegistry = bp.componentRegistry
            if HasActivateComponent(slimItem.typeID):
                self.CreateCounterController(ActivateCounterController, componentRegistry, slimItem)
            if HasReinforceComponent(slimItem.typeID):
                self.CreateCounterController(ReinforceCounterController, componentRegistry, slimItem)
            if HasJumpPolarizationComponent(slimItem.typeID):
                self.CreateCounterController(JumpPolarizationCounterController, componentRegistry, slimItem)
            if HasProximityUnlockComponent(slimItem.typeID):
                self.CreateCounterController(ProximityLockCounterController, componentRegistry, slimItem)
            if HasLinkWithShipComponent(slimItem.typeID):
                self.CreateCounterController(LinkWithShipCounterController, componentRegistry, slimItem)
            if HasHostileBaiterComponent(slimItem.typeID):
                self.CreateCounterController(HostileBaiterCounterController, componentRegistry, slimItem)

    def IsSelectedOrHilted(self):
        stateSvc = sm.GetService('stateSvc')
        selected = stateSvc.GetExclState(state.selected)
        if selected == self.itemID:
            return True
        hilited = stateSvc.GetExclState(state.mouseOver)
        if hilited == self.itemID:
            return True
        return False

    def UpdateSubLabelIfNeeded(self, text):
        self.displaySubLabel = text
        if self.IsSelectedOrHilted():
            self.CreateSubLabelIfNeeded()
            if self.SubLabelExists():
                self.subLabel.text = self.displaySubLabel

    def OnSlimItemChange(self, oldSlim, newSlim):
        self.slimItem = newSlim
        if self._ShouldUpdateIconColor(oldSlim, newSlim):
            self.UpdateIconColor(newSlim)

    def _ShouldUpdateIconColor(self, oldSlim, newSlim):
        if not hasattr(newSlim, 'hostile_response_threshold'):
            return False
        elif oldSlim.hostile_response_threshold != newSlim.hostile_response_threshold:
            return True
        elif oldSlim.friendly_response_threshold != newSlim.friendly_response_threshold:
            return True
        else:
            return False
