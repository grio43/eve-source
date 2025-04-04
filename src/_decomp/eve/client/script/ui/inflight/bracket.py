#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\bracket.py
import math
import weakref
from carbon.common.script.util import timerstuff
from carbon.common.script.util.format import FmtAmt, FmtDist
from carbonui import fontconst
from carbonui.control.label import LabelCore
from carbonui.primitives.bracket import Bracket as BracketCore
from carbonui.primitives.container import Container
from carbonui.primitives.base import ScaleDpi
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
import overviewPresets.overviewSettingsConst as osConst
from eve.client.script.ui.inflight.bracketsAndTargets import bracketVarious
from eve.client.script.ui.inflight.bracketsAndTargets.targetOnBracket import ActiveTargetOnBracket
from eve.client.script.ui.inflight.bracketsAndTargets.targetOnBracket import TargetOnBracket
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from eve.client.script.ui.control.eveHint import BubbleHint
from eve.client.script.ui.shared.fleet.fleetBroadcastConst import iconsByBroadcastType
from eve.client.script.ui.shared.stateFlag import FlagIconWithState, GetExtraInfoForSlimItem
import evetypes
import blue
import telemetry
import uthread
from eve.client.script.parklife import states as state
import trinity
from eve.client.script.ui.shared.fleet import fleetbroadcastexports as fleetbr
import carbonui.const as uiconst
from eve.client.script.ui.shared.maps import maputils
import localization
from eve.client.script.util.bubble import SlimItemFromCharID
from eve.common.script.mgt.entityConst import POS_STRUCTURE_STATE
from carbonui.uicore import uicore
from eve.common.script.sys import idCheckers
from eveservices.menu import GetMenuService
from spacecomponents.common.helper import HasEntityStandingsComponent
SHOWLABELS_NEVER = 0
SHOWLABELS_ONMOUSEENTER = 1
SHOWLABELS_ALWAYS = 2
TARGETTING_UI_UPDATE_RATE = 50
LABELMARGIN = 6

class BracketShadowLabel(Container):
    displayText = None
    default_fontsize = fontconst.EVE_SMALL_FONTSIZE
    default_fontStyle = fontconst.STYLE_SMALLTEXT

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.top = -500
        self.renderObject.displayY = -500.0
        bracket = attributes.bracket
        cs = uicore.uilib.bracketCurveSet
        xBinding = trinity.CreateBinding(cs, bracket.renderObject, 'displayX', self.renderObject, 'displayX')
        yBinding = trinity.CreateBinding(cs, bracket.renderObject, 'displayY', self.renderObject, 'displayY')
        self.bindings = (xBinding, yBinding)
        self.DelegateEvents(bracket)
        self.mainLabel = LabelCore(parent=self, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT, color=(1, 1, 1, 1), fontsize=attributes.fontsize or self.default_fontsize, fontStyle=attributes.fontStyle or self.default_fontStyle, bold=attributes.bold or False)
        self.mainShadowLabel = LabelCore(parent=self, state=uiconst.UI_DISABLED, align=uiconst.TOPLEFT, color=(0, 0, 0, 1), fontsize=attributes.fontsize or self.default_fontsize, fontStyle=attributes.fontStyle or self.default_fontStyle, bold=attributes.bold or False)
        self.mainShadowLabel.renderObject.spriteEffect = trinity.TR2_SFX_BLUR
        self.text = attributes.text

    @apply
    def text():

        def fset(self, value):
            self.mainLabel.text = value
            self.mainShadowLabel.text = value
            self.width = self.mainLabel.width
            self.height = self.mainLabel.height

        def fget(self):
            return self.mainLabel.text

        return property(**locals())

    @apply
    def textwidth():

        def fset(self, value):
            pass

        def fget(self):
            return self.mainLabel.textwidth

        return property(**locals())

    @apply
    def textheight():

        def fset(self, value):
            pass

        def fget(self):
            return self.mainLabel.textheight

        return property(**locals())

    def Close(self, *args, **kw):
        if getattr(self, 'bindings', None):
            cs = uicore.uilib.bracketCurveSet
            for each in self.bindings:
                if cs and each in cs.bindings:
                    cs.bindings.remove(each)

        Container.Close(self, *args, **kw)


class BracketLabel(Label):
    __guid__ = 'xtriui.BracketLabel'
    default_fontsize = fontconst.EVE_SMALL_FONTSIZE
    default_fontStyle = fontconst.STYLE_SMALLTEXT
    displayText = None

    def ApplyAttributes(self, attributes):
        Label.ApplyAttributes(self, attributes)
        bracket = attributes.bracket
        cs = uicore.uilib.bracketCurveSet
        xBinding = trinity.CreateBinding(cs, bracket.renderObject, 'displayX', self.renderObject, 'displayX')
        yBinding = trinity.CreateBinding(cs, bracket.renderObject, 'displayY', self.renderObject, 'displayY')
        self.bindings = (xBinding, yBinding)
        self.OnMouseUp = bracket.OnMouseUp
        self.OnMouseDown = bracket.OnMouseDown
        self.OnMouseEnter = bracket.OnMouseEnter
        self.OnMouseExit = bracket.OnMouseExit
        self.OnMouseHover = bracket.OnMouseHover
        self.OnClick = bracket.OnClick
        self.OnDblClick = bracket.OnDblClick
        self.GetMenu = bracket.GetMenu

    def Close(self, *args, **kw):
        if getattr(self, 'bindings', None):
            cs = uicore.uilib.bracketCurveSet
            for each in self.bindings:
                if cs and each in cs.bindings:
                    cs.bindings.remove(each)

        self.OnMouseUp = None
        self.OnMouseDown = None
        self.OnMouseEnter = None
        self.OnMouseExit = None
        self.OnMouseHover = None
        self.OnClick = None
        self.GetMenu = None
        Label.Close(self, *args, **kw)

    @apply
    def displayX():
        fget = Label.displayX.fget

        def fset(self, value):
            pass

        return property(**locals())

    @apply
    def displayY():
        fget = Label.displayY.fget

        def fset(self, value):
            pass

        return property(**locals())

    @apply
    def displayRect():
        fget = Label.displayRect.fget

        def fset(self, value):
            displayX, displayY, displayWidth, displayHeight = value
            self._displayWidth = int(round(displayWidth))
            self._displayHeight = int(round(displayHeight))
            ro = self.renderObject
            if ro:
                ro.displayWidth = self._displayWidth
                ro.displayHeight = self._displayHeight
                if self.isAffectedByPushAlignment:
                    ro.textWidth = ro.displayWidth
                    ro.textHeight = ro.displayHeight
                else:
                    ro.textWidth = ScaleDpi(self.width)
                    ro.textHeight = ScaleDpi(self.height)

        return property(**locals())


class BracketSubIcon(Icon):

    def ApplyAttributes(self, attributes):
        Icon.ApplyAttributes(self, attributes)
        bracket = attributes.bracket
        cs = uicore.uilib.bracketCurveSet
        xBinding = trinity.CreateBinding(cs, bracket.renderObject, 'displayX', self.renderObject, 'displayX')
        yBinding = trinity.CreateBinding(cs, bracket.renderObject, 'displayY', self.renderObject, 'displayY')
        self.bindings = (xBinding, yBinding)
        self.OnMouseUp = bracket.OnMouseUp
        self.OnMouseDown = bracket.OnMouseDown
        self.OnMouseEnter = bracket.OnMouseEnter
        self.OnMouseExit = bracket.OnMouseExit
        self.OnMouseHover = bracket.OnMouseHover
        self.OnClick = bracket.OnClick
        self.GetMenu = bracket.GetMenu

    def Close(self, *args, **kw):
        if getattr(self, 'bindings', None):
            cs = uicore.uilib.bracketCurveSet
            for each in self.bindings:
                if cs and each in cs.bindings:
                    cs.bindings.remove(each)

        self.OnMouseUp = None
        self.OnMouseDown = None
        self.OnMouseEnter = None
        self.OnMouseExit = None
        self.OnMouseHover = None
        self.OnClick = None
        self.GetMenu = None
        Icon.Close(self, *args, **kw)


class SimpleBracket(BracketCore):
    __guid__ = 'xtriui.SimpleBracket'
    default_width = 16
    default_height = 16
    targetingPath = None
    stateItemID = None
    fleetBroadcastIcon = None
    fleetTagAndTarget = None
    _originalIconColor = None
    _fleetTag = None
    _fleetTargetNo = None

    def Startup_update(self, *args):
        self.sr.targetItem = None

    def ApplyAttributes(self, attributes):
        super(SimpleBracket, self).ApplyAttributes(attributes)
        self.IsBracket = 1
        self.invisible = False
        self.inflight = False
        self.categoryID = None
        self.groupID = None
        self.itemID = None
        self.displayName = ''
        self.displaySubLabel = ''
        self.sr.icon = None
        self.sr.flag = None
        self.sr.bgColor = None
        self.sr.hilite = None
        self.sr.selection = None
        self.sr.posStatus = None
        self.slimItem = None
        self.ball = None
        self.stateItemID = None
        self.label = None
        self.subLabel = None
        self.fadeColor = True
        self.iconNo = None
        self.iconXOffset = 0
        self.lastPosEvent = None
        self.scanAttributeChangeFlag = False
        self.iconTop = 0

    def Close(self, *args, **kw):
        self.subItemsUpdateTimer = None
        if getattr(self, 'label', None):
            self.label.Close()
            self.label = None
        if getattr(self, 'subLabel', None):
            self.subLabel.Close()
            self.subLabel = None
        if getattr(self, 'fleetBroadcastIcon', None):
            self.fleetBroadcastIcon.Close()
            self.fleetBroadcastIcon = None
        if getattr(self, 'fleetTagAndTarget', None):
            self.fleetTagAndTarget.Close()
            self.fleetTagAndTarget = None
        super(SimpleBracket, self).Close(*args, **kw)

    def Show(self):
        projectBracket = self.projectBracket
        if projectBracket:
            projectBracket.bracket = self.renderObject
        super(SimpleBracket, self).Show()

    def Hide(self):
        super(SimpleBracket, self).Hide()
        self.KillLabel()
        projectBracket = self.projectBracket
        if projectBracket:
            projectBracket.bracket = None

    def Startup(self, itemID, groupID, categoryID, iconNo):
        self.iconNo = iconNo
        self.LoadIcon(iconNo)
        self.itemID = itemID
        self.stateItemID = itemID
        self.groupID = groupID
        self.categoryID = categoryID

    def LoadIcon(self, iconNo):
        if getattr(self, 'noIcon', 0) == 1:
            return
        if self.sr.icon is None:
            icon = Icon(parent=self, name='mainicon', state=uiconst.UI_DISABLED, pos=(0, 0, 16, 16), icon=iconNo, align=uiconst.RELATIVE)
            if self.fadeColor:
                self.color = icon.color
            else:
                icon.opacity = 0.75
            self.sr.icon = icon
        else:
            self.sr.icon.LoadIcon(iconNo)

    def ShowLabel(self, *args):
        if not self.destroyed and (self.displayName == '' or not getattr(self, 'showLabel', True)):
            return
        if not self.label:
            self.label = BracketLabel(parent=self.parent, name='labelparent', idx=0, align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, text=self.displayName, bracket=self)
        if not self.subLabel and self.displaySubLabel:
            self.subLabel = BracketLabel(parent=self.parent, name='sublabelparent', align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, text=self.displaySubLabel, bracket=self)
        if hasattr(self, 'UpdateSubItems'):
            self.UpdateSubItems()

    def KillLabel(self, *args, **kwds):
        if getattr(self, 'label', None):
            self.label.Close()
        if getattr(self, 'subLabel', None):
            self.subLabel.Close()
        self.label = None
        self.subLabel = None
        if hasattr(self, 'UpdateSubItems'):
            self.UpdateSubItems()

    def GetMenu(self):
        return None

    def Select(self, status):
        if status:
            if not self.sr.selection:
                self.sr.selection = Sprite(parent=self, pos=(0, 0, 30, 30), name='selection', state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Bracket/selectionCircle.png', align=uiconst.CENTER, color=(1, 1, 1, 0.5))
            self.sr.selection.display = True
            self.ShowLabel()
        else:
            if self.sr.selection:
                self.sr.selection.state = uiconst.UI_HIDDEN
            if self.projectBracket and self.projectBracket.bracket:
                self.KillLabel()

    def Hilite(self, status):
        if status and self.state != uiconst.UI_HIDDEN:
            uthread.pool('Bracket::Hilite', self._ShowLabel)
        elif self.projectBracket and self.projectBracket.bracket and sm.GetService('stateSvc').GetExclState(state.selected) != self.itemID:
            self.KillLabel()

    def _ShowLabel(self):
        blue.pyos.synchro.SleepWallclock(50)
        if self.destroyed:
            return
        over = uicore.uilib.mouseOver
        if getattr(over, 'stateItemID', None) == self.itemID:
            self.ShowLabel()

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
            myPos = maputils.GetMyPos()
            return (pos - myPos).Length()

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

    subItemsUpdateTimer = None

    def OnMouseDown(self, *args):
        if getattr(self, 'slimItem', None):
            if GetMenuService().TryExpandActionMenu(self.itemID, self):
                return
        sm.GetService('viewState').GetView('inflight').layer.looking = True

    def OnMouseEnter(self, *args):
        if uicore.uilib.leftbtn:
            return
        if self.itemID == sm.GetService('bracket').CheckingOverlaps():
            return
        if not getattr(self, 'invisible', False):
            sm.GetService('stateSvc').SetState(self.itemID, state.mouseOver, 1)
        if self.projectBracket and self.projectBracket.bracket:
            sm.GetService('bracket').CheckOverlaps(self, not getattr(self, 'inflight', 1))

    def OnMouseExit(self, *args):
        if uicore.uilib.leftbtn:
            return
        if self.projectBracket and self.projectBracket.bracket:
            over = uicore.uilib.mouseOver
            if self.itemID == sm.GetService('bracket').CheckingOverlaps():
                return
            sm.GetService('stateSvc').SetState(self.itemID, state.mouseOver, 0)

    def OnClick(self, *args):
        if self.sr.clicktime and blue.os.TimeDiffInMs(self.sr.clicktime, blue.os.GetWallclockTime()) < 1000.0:
            sm.GetService('stateSvc').SetState(self.itemID, state.selected, 1)
            slimItem = getattr(self, 'slimItem', None)
            if slimItem:
                if uicore.uilib.Key(uiconst.VK_CONTROL):
                    return
                GetMenuService().Activate(slimItem)
            self.sr.clicktime = None
        else:
            sm.GetService('stateSvc').SetState(self.itemID, state.selected, 1)
            if sm.GetService('target').IsTarget(self.itemID):
                sm.GetService('stateSvc').SetState(self.itemID, state.activeTarget, 1)
            elif uicore.uilib.Key(uiconst.VK_CONTROL) and uicore.uilib.Key(uiconst.VK_SHIFT):
                sm.GetService('fleet').SendBroadcast_Target(self.itemID)
            self.sr.clicktime = blue.os.GetWallclockTime()
        GetMenuService().TacticalItemClicked(self.itemID)

    def OnDblClick(self, *args):
        pass

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
        self.UpdateIconColor(slimItem)
        self.ActiveTarget(activeTarget)
        if not activeTarget:
            self.Targeting(targeting)
            if not targeting:
                targeted, = sm.GetService('stateSvc').GetStates(slimItem.itemID, [state.targeted])
                self.Targeted(targeted)
        if self.updateItem:
            self.UpdateFlagAndBackground(slimItem)
            self.Attacking(attacking)
            self.Hostile(not attacking and hostile, attacking)
        else:
            if self.sr.flag:
                self.sr.flag.Close()
                self.sr.flag = None
            if self.sr.bgColor:
                self.sr.bgColor.Close()
                self.sr.bgColor = None
        fleetTag = sm.GetService('fleet').GetTargetTag(slimItem.itemID)
        self.AddFleetTag(fleetTag)
        if slimItem.groupID == const.groupWreck:
            uthread.worker('bracket.WreckEmpty', self.WreckEmpty, slimItem.isEmpty)
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

    @telemetry.ZONE_METHOD
    def UpdateFlagAndBackground(self, slimItem, *args):
        if self.destroyed or not self.updateItem:
            return
        try:
            if slimItem.groupID != const.groupAgentsinSpace and (slimItem.ownerID and idCheckers.IsNPC(slimItem.ownerID) or slimItem.charID and idCheckers.IsNPC(slimItem.charID)):
                if self.sr.flag:
                    self.sr.flag.Close()
                    self.sr.flag = None
                if self.sr.bgColor:
                    self.sr.bgColor.Close()
                    self.sr.bgColor = None
            else:
                stateSvc = sm.GetService('stateSvc')
                iconFlag, backgroundFlag = stateSvc.GetIconAndBackgroundFlags(slimItem)
                icon = None
                if self.sr.icon and self.sr.icon.display:
                    icon = self.sr.icon
                if icon and iconFlag and iconFlag != -1:
                    if self.sr.flag is None:
                        self.sr.flag = FlagIconWithState(parent=self, left=0, top=0, state=uiconst.UI_DISABLED, align=uiconst.TOPLEFT)
                    flagInfo = stateSvc.GetStatePropsColorAndBlink(iconFlag)
                    self.sr.flag.ModifyIcon(flagInfo=flagInfo, showHint=False, extraInfo=GetExtraInfoForSlimItem(slimItem))
                    if settings.user.overview.Get(osConst.SETTING_NAME_SMALL_TAGS, 0):
                        self.sr.flag.ChangeFlagPos(icon.left + 10, icon.top + 10, 5, 5)
                    else:
                        self.sr.flag.ChangeFlagPos(icon.left + 9, icon.top + 8, 9, 9)
                    hideIcon = settings.user.overview.Get(osConst.SETTING_NAME_SMALL_TAGS, 0)
                    self.sr.flag.ChangeIconVisibility(display=not hideIcon)
                    props = stateSvc.GetStateProps(iconFlag)
                    col = stateSvc.GetStateFlagColor(iconFlag)
                    blink = stateSvc.GetStateBackgroundBlink(iconFlag)
                    self.sr.flag.children[0].SetRGBA(*props.iconColor)
                    self.sr.flag.children[1].SetRGBA(*col)
                    if blink:
                        if not self.sr.flag.HasAnimation('opacity'):
                            uicore.animations.FadeTo(self.sr.flag, startVal=0.0, endVal=1.0, duration=0.5, loops=uiconst.ANIM_REPEAT, curveType=uiconst.ANIM_WAVE)
                    else:
                        self.sr.flag.StopAnimations()
                        self.sr.flag.opacity = 1.0
                    self.UpdateFlagPositions(icon)
                    if settings.user.overview.Get(osConst.SETTING_NAME_SMALL_TAGS, 0):
                        iconNum = 0
                    else:
                        iconNum = props.iconIndex + 1
                    self.sr.flag.children[0].rectLeft = iconNum * 10
                    self.sr.flag.state = uiconst.UI_DISABLED
                elif self.sr.flag:
                    self.sr.flag.Close()
                    self.sr.flag = None
                if backgroundFlag and backgroundFlag != -1:
                    r, g, b, a = stateSvc.GetStateBackgroundColor(backgroundFlag)
                    a = a * 0.5
                    if not self.sr.bgColor:
                        self.sr.bgColor = Fill(name='bgColor', parent=self, state=uiconst.UI_DISABLED, color=(r,
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
                    self.sr.bgColor.Close()
                    self.sr.bgColor = None
        except AttributeError:
            if not self.destroyed:
                raise

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
            self.SetViewState(True)

    def UpdateFlagPositions(self, *args, **kwds):
        pass

    def CreateFlagMarker(self):
        flag = Container(parent=self, name='flag', pos=(0, 0, 10, 10), align=uiconst.TOPLEFT, idx=0)
        icon = Sprite(parent=flag, name='icon', pos=(0, 0, 10, 10), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Bracket/flagIcons.png')
        icon.rectWidth = 10
        icon.rectHeight = 10
        Fill(parent=flag)
        return flag

    def OnStateChange(self, itemID, flag, status, *args):
        if self.stateItemID != itemID:
            return
        if flag == state.mouseOver:
            self.Hilite(status)
        elif flag == state.selected:
            self.Select(status)
        elif flag == state.targeted:
            self.Targeted(status)
        elif flag == state.targeting:
            self.Targeting(status)
        elif flag == state.activeTarget:
            self.ActiveTarget(status)
        elif flag == state.flagWreckAlreadyOpened:
            self.SetViewState(status)
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
        self.sr.icon.SetRGBA(r, g, b)

    def SetViewState(self, status):
        if not self._originalIconColor:
            color = self.sr.icon.color
            self._originalIconColor = (color.r, color.g, color.b)
        r, g, b = self._originalIconColor
        if status:
            attenuation = 0.55
            self.SetColor(r * attenuation, g * attenuation, b * attenuation, _save=False)
        else:
            self.SetColor(r, g, b, _save=False)

    def WreckEmpty(self, isEmpty):
        icon = sm.GetService('bracket').GetBracketIcon(self.slimItem.typeID, isEmpty)
        self.sr.icon.LoadIcon(icon)
        self.iconNo = icon

    def AddFleetTag(self, tag):
        self._fleetTag = tag
        self.UpdateFleetTagAndTarget()

    def UpdateFleetTagAndTarget(self):
        tagAndTargetStr = ''
        if self._fleetTargetNo:
            tagAndTargetStr += unicode(self._fleetTargetNo)
        if self._fleetTag:
            if tagAndTargetStr:
                tagAndTargetStr += ' / '
            tagAndTargetStr += unicode(self._fleetTag)
        if tagAndTargetStr:
            if not self.fleetTagAndTarget:
                self.fleetTagAndTarget = BracketLabel(parent=self.parent, name='fleetTagAndTarget', align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, text=tagAndTargetStr, fontsize=fontconst.EVE_MEDIUM_FONTSIZE, bracket=self, bold=True, idx=0)
            else:
                self.fleetTagAndTarget.text = tagAndTargetStr
        elif self.fleetTagAndTarget:
            self.fleetTagAndTarget.Close()
            self.fleetTagAndTarget = None
        self.UpdateSubItems()

    def GBTarget(self, active, fleetBroadcastID, charID, targetNo = None):
        self.FleetBroadcast(active, 'Target', fleetBroadcastID, charID)
        if active:
            self._fleetTargetNo = targetNo
        else:
            self._fleetTargetNo = None
        self.UpdateFleetTagAndTarget()

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
            self.fleetBroadcastIcon = BracketSubIcon(icon=icon, parent=self.parent, state=uiconst.UI_NORMAL, name='fleetBroadcastIcon', bracket=self, hint=fleetbr.GetBroadcastName(broadcastType), idx=0, width=16, height=16)
            self.UpdateSubItems()
        elif fleetBroadcastID == getattr(self, 'fleetBroadcastID', None):
            if self.fleetBroadcastIcon:
                self.fleetBroadcastIcon.Close()
                self.fleetBroadcastIcon = None
                self.UpdateSubItems()
            self.fleetBroadcastSender = self.fleetBroadcastType = self.fleetBroadcastID = None

    def _UpdateSubItems(self):
        self.UpdateSubItems()

    def UpdateSubItems(self):
        if self.destroyed:
            return
        bracketRO = self.renderObject
        x, y = bracketRO.displayX, bracketRO.displayY
        bracketLayerWidth = uicore.layer.bracket.renderObject.displayWidth
        labelsXOffset = 0
        if self.fleetBroadcastIcon:
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
        if self.label:
            newStr = self.displayName
            if newStr is None:
                self.Close()
                return
            if getattr(self, 'showDistance', 1):
                distance = self.GetDistance()
                if distance:
                    newStr += ' ' + FmtDist(distance)
            self.label.text = newStr
        mainLabelsYOffset = 0
        maxLabelWidth = 0
        if self.label:
            maxLabelWidth = max(maxLabelWidth, self.label.textwidth)
        if self.subLabel:
            maxLabelWidth = max(maxLabelWidth, self.subLabel.textwidth)
        if self.fleetTagAndTarget:
            maxLabelWidth = max(maxLabelWidth, self.fleetTagAndTarget.textwidth)
            xb, yb = self.fleetTagAndTarget.bindings
            if x + self.width + LABELMARGIN + maxLabelWidth > bracketLayerWidth:
                xb.offset = (-self.fleetTagAndTarget.textwidth - LABELMARGIN - labelsXOffset,
                 0,
                 0,
                 0)
            else:
                xb.offset = (self.width + LABELMARGIN + labelsXOffset,
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
        if self.label:
            xb, yb = self.label.bindings
            mainLabelsYOffset += (self.height - self.label.textheight) / 2 + 1
            yb.offset = (mainLabelsYOffset,
             0,
             0,
             0)
            if x + self.width + LABELMARGIN + maxLabelWidth > bracketLayerWidth:
                xb.offset = (-self.label.textwidth - LABELMARGIN - labelsXOffset,
                 0,
                 0,
                 0)
                if self.subLabel:
                    sxb, syb = self.subLabel.bindings
                    sxb.offset = (-self.subLabel.textwidth - LABELMARGIN - labelsXOffset,
                     0,
                     0,
                     0)
                    syb.offset = (mainLabelsYOffset + self.label.textheight,
                     0,
                     0,
                     0)
            else:
                xb.offset = (self.width + LABELMARGIN + labelsXOffset,
                 0,
                 0,
                 0)
                if self.subLabel:
                    sxb, syb = self.subLabel.bindings
                    sxb.offset = (self.width + LABELMARGIN + labelsXOffset,
                     0,
                     0,
                     0)
                    syb.offset = (mainLabelsYOffset + self.label.textheight,
                     0,
                     0,
                     0)
        if not (self.label or self.subLabel or self.fleetBroadcastIcon or self.fleetTagAndTarget):
            self.subItemsUpdateTimer = None
        elif not getattr(self, 'subItemsUpdateTimer', None):
            self.subItemsUpdateTimer = timerstuff.AutoTimer(500, self._UpdateSubItems)

    def ActiveTarget(self, activestate):
        for each in self.children[:]:
            if each.name == 'activetarget':
                each.Close()

        if activestate:
            activeTarget = self.GetActiveTargetUI()
        else:
            targeted, = sm.GetService('stateSvc').GetStates(self.stateItemID, [state.targeted])
            self.Targeted(targeted, 0)

    def Targeted(self, state, tryActivate = 1):
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
            if tryActivate:
                self.ActiveTarget(0)
            t = self.sr.targetItem
            self.sr.targetItem = None
            if t is not None:
                t.Close()

    def Targeting(self, state):
        if state:
            if self.sr.targetItem is None or self.sr.targetItem.destroyed:
                self.Targeted(1)
            if self.sr.targetItem:
                uthread.new(self.CountDown, self.sr.targetItem)
                self.sr.targetItem.ShowTargetingIndicators()
        elif self.sr.targetItem:
            self.sr.targetItem.HideTargetingIndicators()

    def CountDown(self, *args):
        pass

    def UpdateStructureState(self, slimItem):
        if not idCheckers.IsStarbase(slimItem.categoryID):
            return
        self.lastPosEvent = blue.os.GetWallclockTime()
        stateName, stateTimestamp, stateDelay = sm.GetService('pwn').GetStructureState(slimItem)
        if self.sr.posStatus is None:
            self.sr.posStatus = EveLabelSmall(text=POS_STRUCTURE_STATE[stateName], parent=self, left=24, top=30, state=uiconst.UI_NORMAL)
        else:
            self.sr.posStatus.text = POS_STRUCTURE_STATE[stateName]
        if stateName in ('anchoring', 'onlining', 'unanchoring', 'reinforced', 'operating', 'incapacitated'):
            uthread.new(self.StructureProgress, self.lastPosEvent, stateName, stateTimestamp, stateDelay)

    def StructureProgress(self, lastPosEvent, stateName, stateTimestamp, stateDelay):
        if self.destroyed:
            return
        t = self.sr.posStatus
        Frame(parent=self, align=uiconst.RELATIVE, width=82, height=13, left=18, top=30, color=(1.0, 1.0, 1.0, 0.5))
        p = Fill(parent=self, align=uiconst.RELATIVE, width=80, height=11, left=19, top=31, color=(1.0, 1.0, 1.0, 0.25))
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
            if timeLeft <= 0:
                t.text = doneStr
                break
            t.text = localization.GetByLabel('UI/Inflight/Brackets/StructureProgress', stateName=POS_STRUCTURE_STATE[stateName], timeRemaining=long(timeLeft))
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
            Icon(icon='ui_38_16_15', name='anchoredicon', parent=self, pos=(0, 16, 16, 16), align=uiconst.TOPLEFT)

    def GetActiveTargetUI(self):
        return ActiveTargetOnBracket(parent=self)

    def GetTargetedUI(self):
        return TargetOnBracket(parent=self)


class Bracket(SimpleBracket):
    __guid__ = 'xtriui.Bracket'
    _displayName = None
    _slimItem = None

    def Startup(self, slimItem, ball = None, transform = None):
        self.iconNo, dockType, minDist, maxDist, iconOffset, logflag = self.data
        self.slimItem = slimItem
        self.itemID = slimItem.itemID
        self.groupID = slimItem.groupID
        self.categoryID = slimItem.categoryID
        SimpleBracket.Startup_update(self)
        if not self.invisible:
            self.LoadIcon(self.iconNo)
        self.UpdateStructureState(slimItem)
        self.SetBracketAnchoredState(slimItem)
        SimpleBracket.Load_update(self, slimItem)

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

    def OnAttribute(self, attributeName, item, newValue):
        self.scanAttributeChangeFlag = True

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
        if not target:
            return
        self.scanAttributeChangeFlag = False
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
        targetSvc = sm.GetService('target')
        startTime = targetSvc.GetTargetingStartTime(slimItem.itemID)
        if startTime is None:
            return
        t = EveLabelSmall(text='', parent=target, state=uiconst.UI_NORMAL, align=uiconst.CENTERTOP, top=64)
        targetSvc = sm.GetService('target')
        lockedText = localization.GetByLabel('UI/Inflight/Brackets/TargetLocked')
        while not self.destroyed:
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

        blue.pyos.synchro.SleepWallclock(250)
        if t.destroyed:
            return
        t.text = ''
        blue.pyos.synchro.SleepWallclock(250)
        if t.destroyed:
            return
        t.text = lockedText
        blue.pyos.synchro.SleepWallclock(250)
        if t.destroyed:
            return
        t.text = ''
        blue.pyos.synchro.SleepWallclock(250)
        if t.destroyed:
            return
        t.text = lockedText
        blue.pyos.synchro.SleepWallclock(250)

    def GBEnemySpotted(self, active, fleetBroadcastID, charID):
        self.NearIDFleetBroadcast(active, fleetBroadcastID, charID, 'EnemySpotted')

    def GBNeedBackup(self, active, fleetBroadcastID, charID):
        self.NearIDFleetBroadcast(active, fleetBroadcastID, charID, 'NeedBackup')

    def GBInPosition(self, active, fleetBroadcastID, charID):
        self.NearIDFleetBroadcast(active, fleetBroadcastID, charID, 'InPosition')

    def GBHoldPosition(self, active, fleetBroadcastID, charID):
        self.NearIDFleetBroadcast(active, fleetBroadcastID, charID, 'HoldPosition')

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

    def GetRadialMenuIndicator(self, create = True, *args):
        radialMenuSprite = getattr(self, 'radialMenuSprite', None)
        if radialMenuSprite and not radialMenuSprite.destroyed:
            return radialMenuSprite
        if not create:
            return
        radialMenuSprite = Sprite(name='radialMenuSprite', parent=self, texturePath='res:/UI/Texture/classes/RadialMenu/bracketHilite.png', pos=(0, 0, 20, 20), color=(0.5, 0.5, 0.5, 0.5), idx=-1, align=uiconst.CENTER, state=uiconst.UI_DISABLED)
        self.radialMenuSprite = radialMenuSprite
        return radialMenuSprite

    def ShowRadialMenuIndicator(self, slimItem, *args):
        mySprite = self.GetRadialMenuIndicator(create=True)
        mySprite.display = True

    def HideRadialMenuIndicator(self, slimItem, *args):
        mySprite = self.GetRadialMenuIndicator(create=False)
        if mySprite:
            mySprite.display = False


import carbon.common.script.util.autoexport as autoexport
exports = autoexport.AutoExports('bracket', locals())
