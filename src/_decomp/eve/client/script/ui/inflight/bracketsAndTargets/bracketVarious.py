#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\bracketsAndTargets\bracketVarious.py
from behaviors.const.combat import FW_ATTACK_NOT_SAME_FACTION
from carbonui.primitives.vectorlinetrace import VectorLineTrace
from eve.client.script.ui.control.eveIcon import Icon
import evetypes
import trinity
import carbonui.const as uiconst
import telemetry
import eve.common.script.mgt.entityConst as entities
import localization
from eve.common.script.sys.idCheckers import IsPlayerOwner
from spacecomponents.client.components.entitystandings import get_icon_color_sort_value_and_hint_for_owner_standing, get_icon_color_sort_value_and_hint_for_fw_attack_method, ICON_COLOR_NEUTRAL, ICON_COLOR_BAD
from spacecomponents.common.helper import HasEntityStandingsComponent, HasBehaviorComponent
from carbonui.uicore import uicore
import logging
logger = logging.getLogger(__name__)
LEFT = 0
TOP = 1
RIGHT = 2
BOTTOM = 3
SHOWLABELS_NEVER = 0
SHOWLABELS_ONMOUSEENTER = 1
SHOWLABELS_ALWAYS = 2
TARGETTING_UI_UPDATE_RATE = 50
MAXOVERLAP_TOOLTIP_ENTRIES = 15
LABELMARGIN = 6
GROUPS_WITH_LOOTRIGHTS = (const.groupWreck, const.groupCargoContainer, const.groupFreightContainer)
entityStateStrings = {entities.STATE_ANCHORING: 'UI/Entities/States/Anchoring',
 entities.STATE_ONLINING: 'UI/Entities/States/Onlining',
 entities.STATE_ANCHORED: 'UI/Entities/States/Anchored',
 entities.STATE_UNANCHORING: 'UI/Entities/States/Unanchoring',
 entities.STATE_UNANCHORED: 'UI/Entities/States/Unanchored',
 entities.STATE_INCAPACITATED: 'UI/Entities/States/Incapacitated',
 entities.STATE_IDLE: 'UI/Entities/States/Idle',
 entities.STATE_COMBAT: 'UI/Entities/States/Fighting',
 entities.STATE_MINING: 'UI/Entities/States/Mining',
 entities.STATE_APPROACHING: 'UI/Entities/States/Approaching',
 entities.STATE_FLEEING: 'UI/Entities/States/Fleeing',
 entities.STATE_REINFORCED: 'UI/Entities/States/Reinforced',
 entities.STATE_OPERATING: 'UI/Entities/States/Operating',
 entities.STATE_VULNERABLE: 'UI/Entities/States/Vulnerable',
 entities.STATE_INVULNERABLE: 'UI/Entities/States/Invulnerable',
 entities.STATE_SHIELD_REINFORCE: 'UI/Entities/States/ShieldReinforced',
 entities.STATE_ARMOR_REINFORCE: 'UI/Entities/States/ArmorReinforced',
 entities.STATE_SALVAGING: 'UI/Entities/States/Salvaging'}

def GetEntityStateString(entityState):
    if entityState in entityStateStrings:
        return localization.GetByLabel(entityStateStrings[entityState])
    else:
        return localization.GetByLabel('UI/Entities/States/Unknown', entityStateID=entityState)


class BracketSubIconNew(Icon):

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


@telemetry.ZONE_METHOD
def GetIconColor(slimItem, getSortValue = False, getColorHint = False):
    iconColor = const.OVERVIEW_NORMAL_COLOR
    colorSortValue = 0
    colorHint = None
    if slimItem.categoryID in (const.categoryShip, const.categoryDrone):
        if slimItem.itemID == session.shipid:
            iconColor = const.OVERVIEW_OWN_SHIP_COLOR
    elif IsNpcObject(slimItem) and slimItem.typeID:
        iconColor = ICON_COLOR_NEUTRAL
        fwAttackMethod = getattr(slimItem, 'fwAttackMethod', None)
        if fwAttackMethod and session.warfactionid:
            iconColor, colorSortValue, colorHint = get_icon_color_sort_value_and_hint_for_fw_attack_method(slimItem, session.warfactionid, slimItem.fwAttackMethod)
        if fwAttackMethod == FW_ATTACK_NOT_SAME_FACTION:
            pass
        elif iconColor != ICON_COLOR_BAD:
            if fwAttackMethod is not None and HasBehaviorComponent(slimItem.typeID) and getattr(slimItem, 'group_standings_disabled', None) is True:
                pass
            elif HasEntityStandingsComponent(slimItem.typeID):
                iconColor, colorSortValue, colorHint = get_icon_color_sort_value_and_hint_for_owner_standing(slimItem, session.charid)
    elif slimItem.groupID == const.groupStation or slimItem.categoryID == const.categoryStructure:
        waypoints = sm.GetService('starmap').GetWaypoints()
        destinationPath = sm.GetService('starmap').GetDestinationPath()
        jumpToLocationID = getattr(slimItem, 'targetSolarsystemID', None)
        if jumpToLocationID and destinationPath and jumpToLocationID == destinationPath[0]:
            iconColor = const.OVERVIEW_AUTO_PILOT_DESTINATION_COLOR
            colorSortValue = -1
            colorHint = 'Tooltips/Overview/StargateOnRoute'
        elif waypoints and slimItem.itemID == waypoints[0]:
            iconColor = const.OVERVIEW_AUTO_PILOT_DESTINATION_COLOR
            colorSortValue = -1
            colorHint = 'Tooltips/Overview/StargateOnRoute'
        elif HasEntityStandingsComponent(slimItem.typeID):
            iconColor, colorSortValue, colorHint = get_icon_color_sort_value_and_hint_for_owner_standing(slimItem, session.charid)
    elif slimItem.groupID == const.groupStargate and slimItem.jumps:
        destinationPath = sm.GetService('starmap').GetDestinationPath()
        jumpToLocationID = slimItem.jumps[0].locationID
        if destinationPath and jumpToLocationID == destinationPath[0]:
            iconColor = const.OVERVIEW_AUTO_PILOT_DESTINATION_COLOR
            colorSortValue = -1
            colorHint = 'Tooltips/Overview/StargateOnRoute'
    elif IsAbandonedContainer(slimItem):
        iconColor = const.OVERVIEW_ABANDONED_CONTAINER_COLOR
        colorHint = 'Tooltips/Overview/AbandonedContainer'
    elif IsForbiddenContainer(slimItem):
        iconColor = const.OVERVIEW_FORBIDDEN_CONTAINER_COLOR
        colorHint = 'Tooltips/Overview/RestrictedContainer'
        colorSortValue = -1
    if getSortValue:
        if getColorHint:
            return (iconColor, colorSortValue, localization.GetByLabel(colorHint) if colorHint else None)
        return (iconColor, colorSortValue)
    if getColorHint:
        return (iconColor, localization.GetByLabel(colorHint) if colorHint else None)
    return iconColor


def IsForbiddenContainer(slimItem):
    if slimItem.groupID not in GROUPS_WITH_LOOTRIGHTS:
        return False
    bp = sm.StartService('michelle').GetBallpark()
    if bp is None:
        return False
    if bp.HaveLootRight(slimItem.itemID):
        return False
    return True


def IsAbandonedContainer(slimItem):
    if slimItem.groupID not in GROUPS_WITH_LOOTRIGHTS:
        return False
    bp = sm.StartService('michelle').GetBallpark()
    if bp is None:
        return False
    if bp.IsAbandoned(slimItem.itemID):
        return True
    return False


def GetAbsolute(bracket):
    ro = bracket.renderObject
    x = ro.displayX
    y = ro.displayY
    centerX = x + ro.displayWidth / 2
    centerY = y + ro.displayHeight / 2
    return [centerX - 8,
     centerY - 8,
     centerX + 8,
     centerY + 8]


def GetOverlaps(sender, useMousePosition = True, customBracketParent = None):
    overlaps = []
    if customBracketParent is None or customBracketParent is sender.parent:
        overlaps.append(sender)
    excludedC = (const.categoryAsteroid,)
    excludedG = (const.groupHarvestableCloud,)
    bBox = GetAbsolute(sender)
    senderParent = customBracketParent or sender.parent
    parentOffsetX, parentOffsetY = senderParent.GetAbsolutePosition()
    mouseX = uicore.ReverseScaleDpi(uicore.uilib.x) - parentOffsetX
    mouseY = uicore.ReverseScaleDpi(uicore.uilib.y) - parentOffsetY
    for bracket in senderParent.children:
        if not (isinstance(bracket, sender.__class__) or getattr(bracket, 'IsBracket', 0)) or not bracket.displayName or not bracket.display or bracket.invisible or bracket.categoryID in excludedC or bracket.groupID in excludedG or bracket in overlaps:
            continue
        b = GetAbsolute(bracket)
        if useMousePosition:
            overlapx = b[LEFT] <= mouseX <= b[RIGHT]
            overlapy = b[TOP] <= mouseY <= b[BOTTOM]
        else:
            overlapx = not (b[RIGHT] <= bBox[LEFT] or b[LEFT] >= bBox[RIGHT])
            overlapy = not (b[BOTTOM] <= bBox[TOP] or b[TOP] >= bBox[BOTTOM])
        if overlapx and overlapy:
            overlaps.append(bracket)
            if len(overlaps) == MAXOVERLAP_TOOLTIP_ENTRIES:
                break

    overlaps = sorted(overlaps, key=lambda x: x.displayName)
    return (overlaps, bBox)


class TargetingHairlines:
    __guid__ = 'bracketUtils.TargetingHairlines'

    def __init__(self):
        self.trace = None
        self.line = None

    def CreateHairlines(self, moduleID, bracket, target):
        self.trace = VectorLineTrace(parent=uicore.layer.shipui, lineWidth=2.5, idx=-1, name='vectorlineTrace')
        self.trace.SetRGBA(0.5, 0.7, 0.6, 0.5)
        self.line = VectorLineTrace(parent=uicore.layer.shipui, lineWidth=0.1, idx=-1, name='vectorline')
        linePoints = self.GetHairlinePoints(moduleID, bracket, target)
        if linePoints is None:
            return
        startPoint, midPoint, endPoint = linePoints
        self.line.AddPoint(startPoint)
        self.line.AddPoint(midPoint)
        self.line.AddPoint(endPoint)
        self.trace.AddPoint(startPoint)
        self.trace.AddPoint(midPoint)
        self.trace.AddPoint(endPoint)
        return (self.trace, self.line)

    def UpdateHairlinePoints(self, moduleID, bracket, target):
        linePoints = self.GetHairlinePoints(moduleID, bracket, target)
        if linePoints is None:
            return
        startPoint, midPoint, endPoint = linePoints
        if self.line.renderObject is None or self.trace.renderObject is None:
            sm.GetService('bracket').LogWarn('Hairlines were broken, new ones were made')
            self.line.Close()
            self.trace.Close()
            self.CreateHairlines(moduleID, bracket, target)
        self.line.renderObject.vertices[0].position = startPoint
        self.line.renderObject.vertices[1].position = midPoint
        self.line.renderObject.vertices[2].position = endPoint
        self.line.renderObject.isDirty = True
        self.trace.renderObject.vertices[0].position = startPoint
        self.trace.renderObject.vertices[1].position = midPoint
        self.trace.renderObject.vertices[2].position = endPoint
        self.trace.renderObject.isDirty = True
        self.ShowLines()

    def GetHairlinePoints(self, moduleID, bracket, target, *args):
        moduleButton = uicore.layer.shipui.GetModuleFromID(moduleID)
        ro = bracket.GetRenderObject()
        if not ro or moduleButton is None:
            return
        x = uicore.ScaleDpi(moduleButton.absoluteLeft + moduleButton.width / 2.0)
        y = uicore.ScaleDpi(moduleButton.absoluteTop + moduleButton.height / 2.0)
        startPoint = (x, y)
        weapon = target.GetWeapon(moduleID)
        if weapon:
            endPointObject = weapon
        else:
            endPointObject = target
        x = uicore.ScaleDpi(endPointObject.absoluteLeft + endPointObject.width / 2.0)
        y = uicore.ScaleDpi(endPointObject.absoluteTop + endPointObject.height / 2.0)
        endPoint = (x, y)
        x = ro.displayX
        y = ro.displayY
        l, r = uicore.layer.sidePanels.GetSideOffset()
        x += uicore.ScaleDpi(l)
        midPoint = (int(x + bracket.width / 2.0), int(y + bracket.height / 2.0))
        return (startPoint, midPoint, endPoint)

    def StartAnimation(self, reverse = False, *args):
        if reverse:
            start_values = (0.99, 0.0)
            end_values = (1.0, 0.01)
        else:
            start_values = (0.0, 1.0)
            end_values = (0.01, 1.01)
        uicore.animations.MorphScalar(self.trace, 'start', startVal=start_values[0], endVal=start_values[1], duration=1.0, loops=1, curveType=uiconst.ANIM_LINEAR)
        uicore.animations.MorphScalar(self.trace, 'end', startVal=end_values[0], endVal=end_values[1], duration=1.0, loops=1, curveType=uiconst.ANIM_LINEAR)

    def ShowLines(self, *args):
        self.line.display = True
        self.trace.display = True

    def HideLines(self, *args):
        self.line.display = False
        self.trace.display = False

    def StopAnimations(self, *args):
        self.trace.StopAnimations()


def FixLines(target):

    def FindLine(name):
        return getattr(target.lines, name)

    l, r, t, b = map(FindLine, ['lineleft',
     'lineright',
     'linetop',
     'linebottom'])
    l.left -= uicore.desktop.width - l.width
    l.width = r.width = uicore.desktop.width
    t.top -= uicore.desktop.height - t.height
    t.height = b.height = uicore.desktop.height


def GetMinDispRangeForOwnShip(typeID):
    radius = evetypes.GetRadius(typeID)
    if radius >= 5000:
        return 100000
    elif radius >= 1500:
        return 40000
    elif radius >= 700:
        return 27000
    elif radius >= 200:
        return 18000
    else:
        return 5000


def IsTargetingOrSettingSecondPoint():
    positionalControl = uicore.layer.inflight.positionalControl
    if positionalControl.IsTargeting():
        return True
    if positionalControl.IsFirstPointSet():
        return True
    return False


def IsNpcObject(slimItem):
    if slimItem.categoryID != const.categoryEntity and slimItem.groupID != const.groupLargeCollidableObject:
        return False
    return not IsPlayerOwner(slimItem.ownerID)
