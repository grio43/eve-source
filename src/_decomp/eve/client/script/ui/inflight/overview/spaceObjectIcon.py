#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\overview\spaceObjectIcon.py
import localization
import uthread
import telemetry
import blue
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from carbonui.util.color import Color
from eve.client.script.parklife import states as state
from eve.client.script.ui.inflight.bracketsAndTargets.blinkingSpriteOnSharedCurve import BlinkingSpriteOnSharedCurve
from eve.client.script.ui.inflight.bracketsAndTargets.bracketVarious import GetIconColor
from eve.client.script.ui.inflight.bracketsAndTargets.inSpaceBracket import InSpaceBracket
from eve.client.script.ui.inflight.overview.overviewUtil import IsFleetMember
from eve.client.script.ui.shared.stateFlag import FlagIconWithState, GetExtraInfoForSlimItem, GetIconFlagAndBackgroundFlag, HasDockingRights
from eve.common.lib import appConst as const
from overviewPresets import overviewSettingsConst as osConst
from structures import STATE_UNANCHORED
from structures.types import IsFlexStructure

class SpaceObjectIcon(Container):
    iconSprite = None
    hostileIndicator = None
    attackingMeIndicator = None
    targetingIndicator = None
    targetedByMeIndicator = None
    myActiveTargetIndicator = None
    flagIcon = None
    flagIconBackground = None
    flagBackgroundColor = None
    default_width = 18
    default_height = 16
    default_align = uiconst.TOPLEFT
    iconHint = None
    iconColorHint = None
    flagStateHint = None
    flagStateOwnerHint = None

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.typeID = attributes.get('typeID', None)
        self.iconSprite = Sprite(parent=self, name='iconSprite', state=uiconst.UI_DISABLED, pos=(0, 0, 16, 16))

    def SetHostileState(self, state, isFleetMember, *args, **kwds):
        if state:
            if self.hostileIndicator:
                if getattr(self.hostileIndicator, 'isFleetMember', False) == isFleetMember:
                    return
                self.SetHostileIndicatorColor(isFleetMember)
            else:
                color = self.GetColorForHostileState(isFleetMember)
                self.hostileIndicator = BlinkingSpriteOnSharedCurve(parent=self, name='hostile', pos=(-1, -1, 18, 18), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Bracket/hostileBracket.png', align=uiconst.TOPLEFT, color=color, curveSetName='sharedHostileCurveSet')
                self.hostileIndicator.isFleetMember = isFleetMember
        elif self.hostileIndicator:
            self._RemoveHostileUI()

    def SetHostileIndicatorColor(self, isFleetMember):
        if self.hostileIndicator:
            color = self.GetColorForHostileState(isFleetMember)
            self.hostileIndicator.SetRGBA(*color)
            self.hostileIndicator.isFleetMember = isFleetMember

    def GetColorForHostileState(self, isFleetMember):
        if isFleetMember:
            color = sm.GetService('bracket').GetFleetBracketColor()
        else:
            color = (1.0, 0.8, 0.0, 0.3)
        return color

    def _RemoveHostileUI(self):
        self.hostileIndicator.Close()
        self.hostileIndicator = None

    def SetAttackingState(self, state):
        if state:
            if not self.attackingMeIndicator:
                self.attackingMeIndicator = BlinkingSpriteOnSharedCurve(parent=self, name='attackingMe', pos=(-1, -1, 18, 18), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Bracket/hostileBracket.png', align=uiconst.TOPLEFT, color=(0.8, 0.0, 0.0, 0.3), curveSetName='sharedHostileCurveSet')
            if self.hostileIndicator:
                self._RemoveHostileUI()
        elif self.attackingMeIndicator:
            self.attackingMeIndicator.Close()
            self.attackingMeIndicator = None

    def SetTargetedByMeState(self, state):
        if state:
            if not self.targetedByMeIndicator:
                self.targetedByMeIndicator = Sprite(parent=self, name='targetedByMeIndicator', pos=(-1, -1, 18, 18), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Bracket/activeTarget.png', align=uiconst.TOPLEFT, color=(1.0, 1.0, 1.0, 0.5), idx=0)
        elif self.targetedByMeIndicator:
            self.targetedByMeIndicator.Close()
            self.targetedByMeIndicator = None

    def SetActiveTargetState(self, state):
        if state:
            if not self.myActiveTargetIndicator:
                self.myActiveTargetIndicator = Sprite(parent=self, name='myActiveTargetIndicator', pos=(-1, -1, 18, 18), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Bracket/activeTarget.png', align=uiconst.TOPLEFT, idx=0)
        elif self.myActiveTargetIndicator:
            self.myActiveTargetIndicator.Close()
            self.myActiveTargetIndicator = None

    def SetIconFlag(self, iconFlag, extraInfo = None):
        if iconFlag and iconFlag != -1:
            stateSvc = sm.GetService('stateSvc')
            if self.flagIcon is None:
                self.flagIcon = FlagIconWithState(parent=self, left=-1, top=-2, state=uiconst.UI_DISABLED, align=uiconst.BOTTOMRIGHT, extraInfo=extraInfo)
            flagInfo = stateSvc.GetStatePropsColorAndBlink(iconFlag)
            self.flagIcon.ModifyIcon(flagInfo=flagInfo, showHint=False, extraInfo=extraInfo)
            self.flagStateHint = flagInfo.flagProperties.text
            self.flagStateOwnerHint = flagInfo.flagProperties.ownerText
            if settings.user.overview.Get(osConst.SETTING_NAME_SMALL_TAGS, 0):
                iconSize = 6
            else:
                iconSize = 10
            self.flagIcon.ChangeFlagPos(self.flagIcon.left, self.flagIcon.top, iconSize, iconSize)
            hideIcon = settings.user.overview.Get(osConst.SETTING_NAME_SMALL_TAGS, 0)
            self.flagIcon.ChangeIconVisibility(display=not hideIcon)
        elif self.flagIcon:
            self.flagIcon.Close()
            self.flagIcon = None
            self.flagStateHint = None

    def SetBackgroundColorFlag(self, backgroundFlag):
        if backgroundFlag and backgroundFlag != -1:
            stateSvc = sm.GetService('stateSvc')
            r, g, b, a = stateSvc.GetStateBackgroundColor(backgroundFlag)
            a = a * 0.5
            if not self.flagBackgroundColor:
                self.flagBackgroundColor = Sprite(bgParent=self, name='bgColor', texturePath='res:/UI/Texture/classes/Bracket/bracketBackground.png', color=(r,
                 g,
                 b,
                 a), padRight=2)
            else:
                self.flagBackgroundColor.SetRGBA(r, g, b, a)
            blink = stateSvc.GetStateBackgroundBlink(backgroundFlag)
            if blink:
                if not self.flagBackgroundColor.HasAnimation('color'):
                    uicore.animations.FadeTo(self.flagBackgroundColor, startVal=0.0, endVal=a, duration=0.75, loops=uiconst.ANIM_REPEAT, curveType=uiconst.ANIM_WAVE)
            else:
                self.flagBackgroundColor.StopAnimations()
        elif self.flagBackgroundColor:
            self.flagBackgroundColor.Close()
            self.flagBackgroundColor = None

    def SetTargetingState(self, state):
        if state:
            if not self.targetingIndicator:
                par = Container(name='targeting', align=uiconst.CENTER, width=28, height=28, left=-1, parent=self)
                self.targetingIndicator = par
                Fill(parent=par, align=uiconst.TOPLEFT, left=0, top=3, width=5, height=2, color=(1.0, 1.0, 1.0, 0.5))
                Fill(parent=par, align=uiconst.TOPRIGHT, left=0, top=3, width=5, height=2, color=(1.0, 1.0, 1.0, 0.5))
                Fill(parent=par, align=uiconst.BOTTOMLEFT, left=0, top=3, width=5, height=2, color=(1.0, 1.0, 1.0, 0.5))
                Fill(parent=par, align=uiconst.BOTTOMRIGHT, left=0, top=3, width=5, height=2, color=(1.0, 1.0, 1.0, 0.5))
                Fill(parent=par, align=uiconst.TOPLEFT, left=3, top=0, width=2, height=3, color=(1.0, 1.0, 1.0, 0.5))
                Fill(parent=par, align=uiconst.TOPRIGHT, left=3, top=0, width=2, height=3, color=(1.0, 1.0, 1.0, 0.5))
                Fill(parent=par, align=uiconst.BOTTOMLEFT, left=3, top=0, width=2, height=3, color=(1.0, 1.0, 1.0, 0.5))
                Fill(parent=par, align=uiconst.BOTTOMRIGHT, left=3, top=0, width=2, height=3, color=(1.0, 1.0, 1.0, 0.5))
                uthread.pool('Tactical::Targeting', self.AnimateTargeting, par)
        elif self.targetingIndicator:
            self.targetingIndicator.Close()
            self.targetingIndicator = None

    def AnimateTargeting(self, par):
        while par and not par.destroyed:
            p = par.children[0]
            for i in xrange(1, 8):
                par.width = par.height = 28 - i * 2
                blue.pyos.synchro.SleepSim(50)

    @telemetry.ZONE_METHOD
    def UpdateSpaceObjectIcon(self, slimItem, ball):
        if self.destroyed:
            return
        iconHint = None
        if slimItem.hackingSecurityState is not None:
            iconNo, iconHint = InSpaceBracket.GetHackingIcon(slimItem.hackingSecurityState)
        else:
            iconNo, _dockType, _minDist, _maxDist, _iconOffset, _logflag = sm.GetService('bracket').GetBracketProps(slimItem, ball)
        if slimItem.groupID == const.groupWreck:
            if slimItem.isEmpty:
                iconHint = localization.GetByLabel('Tooltips/Overview/EmptyWreck')
            else:
                iconHint = localization.GetByLabel('Tooltips/Overview/ContainsLoot')
        elif slimItem.categoryID == const.categoryStructure and slimItem.state != STATE_UNANCHORED and not IsFlexStructure(slimItem.typeID):
            structureProximityTracker = sm.GetService('structureProximityTracker')
            if structureProximityTracker.HasDockingAccessChanged():
                iconHint = localization.GetByLabel('UI/Overview/FetchingDockingAccess')
            elif HasDockingRights(slimItem, structureProximityTracker):
                iconHint = localization.GetByLabel('UI/Overview/YouCanDock')
            else:
                iconHint = localization.GetByLabel('UI/Overview/YouCannotDock')
        self.iconSprite.LoadIcon(iconNo)
        self.iconHint = iconHint

    @telemetry.ZONE_METHOD
    def UpdateSpaceObjectIconColor(self, slimItem):
        if self.destroyed:
            return
        iconColor, colorHint = GetIconColor(slimItem, getColorHint=True)
        if slimItem.groupID in (const.groupWreck, const.groupSpawnContainer) and sm.GetService('wreck').IsViewedWreck(slimItem.itemID):
            iconColor = Color(*iconColor).SetBrightness(0.55).GetRGBA()
        self.iconColorHint = colorHint
        self.SetIconColor(iconColor)

    def SetIconColor(self, color):
        self.iconSprite.SetRGBA(*color)

    def UpdateSpaceObjectFlagAndBackgroundColor(self, slimItem, ball):
        stateService = sm.GetService('stateSvc')
        updateItem = stateService.CheckIfUpdateItem(slimItem)
        if updateItem:
            iconFlag, backgroundFlag = GetIconFlagAndBackgroundFlag(slimItem)
            self.SetIconFlag(iconFlag, GetExtraInfoForSlimItem(slimItem))
            self.SetBackgroundColorFlag(backgroundFlag)
            self.SetHostileIndicatorColor(IsFleetMember(slimItem))

    def UpdateSpaceObjectState(self, slimItem, ball):
        if self.destroyed:
            return
        stateService = sm.GetService('stateSvc')
        attacking, hostile, targeting, targeted, activeTarget = stateService.GetStates(slimItem.itemID, [state.threatAttackingMe,
         state.threatTargetsMe,
         state.targeting,
         state.targeted,
         state.activeTarget])
        self.SetActiveTargetState(activeTarget)
        self.SetTargetedByMeState(targeted)
        self.SetTargetingState(targeting)
        updateItem = stateService.CheckIfUpdateItem(slimItem)
        if updateItem:
            fleetMember = IsFleetMember(slimItem)
            self.SetHostileState(hostile, fleetMember)
            self.SetAttackingState(attacking)
