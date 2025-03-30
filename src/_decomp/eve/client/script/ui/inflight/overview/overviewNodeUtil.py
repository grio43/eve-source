#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\overview\overviewNodeUtil.py
import re
import telemetry
import geo2
import blue
from eve.client.script.ui.inflight.bracketsAndTargets.bracketVarious import GetIconColor
from eve.client.script.ui.inflight.overview.overviewConst import HTML_ENTITIES, HTML_ENTITY_REPLACEMENTS, COLUMN_CORPORATION, COLUMN_ALLIANCE
from eve.client.script.ui.inflight.overview.overviewUtil import GetCorpTickerName, GetAllianceTickerName, PrepareLocalizationTooltip
from eve.client.script.ui.shared.stateFlag import GetIconFlagAndBackgroundFlag
from eve.client.script.ui.util import uix
from eve.common.lib import appConst as const

def _Encode(text):
    return re.sub(HTML_ENTITIES, lambda match: HTML_ENTITY_REPLACEMENTS[match.group()], text)


def PrimeDisplayName(node):
    slimItem = node.slimItem()
    if not slimItem:
        return
    name = uix.GetSlimItemName(slimItem)
    if slimItem.groupID == const.groupStation:
        name = uix.EditStationName(name, usename=0)
    if node.usingLocalizationTooltips:
        name, hint = PrepareLocalizationTooltip(name)
        node.hint_NAME = hint
    node.display_NAME = _Encode(name)
    if node.sortNameIndex is not None:
        node.sortValue[node.sortNameIndex] = name.lower()
    node.hint_NAME = sm.GetService('bracket').GetDisplayNameForBracket(slimItem)


@telemetry.ZONE_METHOD
def UpdateIconAndBackgroundFlagsOnNode(node):
    slimItem = node.slimItem()
    if slimItem is None:
        return
    iconFlag, backgroundFlag = (0, 0)
    if node.updateItem:
        iconFlag, backgroundFlag = GetIconFlagAndBackgroundFlag(slimItem)
    node.iconAndBackgroundFlags = (iconFlag, backgroundFlag)
    if node.sortIconIndex is not None:
        iconFlag, backgroundFlag = node.iconAndBackgroundFlags
        node.iconColor, colorSortValue = GetIconColor(slimItem, getSortValue=True)
        node.sortValue[node.sortIconIndex] = [iconFlag,
         colorSortValue,
         backgroundFlag,
         slimItem.categoryID,
         slimItem.groupID,
         slimItem.typeID]
    if node.panel:
        node.panel.UpdateFlagAndBackground(slimItem)


def PrimeCorpAndAllianceName(node, columnSettings):
    slimItem = node.slimItem()
    if not slimItem:
        return
    if slimItem.categoryID != const.categoryShip:
        return
    showCorporation, sortCorporationIndex = columnSettings[COLUMN_CORPORATION]
    if showCorporation:
        if slimItem.corpID:
            corpTag = GetCorpTickerName(slimItem)
        else:
            corpTag = ''
        node.display_CORPORATION = corpTag
        if sortCorporationIndex is not None:
            node.sortValue[sortCorporationIndex] = corpTag.lower()
    showAlliance, sortAllianceIndex = columnSettings[COLUMN_ALLIANCE]
    if showAlliance:
        if slimItem.allianceID:
            alliance = GetAllianceTickerName(slimItem)
        else:
            alliance = ''
        node.display_ALLIANCE = alliance
        if sortAllianceIndex is not None:
            node.sortValue[sortAllianceIndex] = alliance.lower()


@telemetry.ZONE_METHOD
def UpdateVelocityData(node, ball, myBall, calculateVelocity, calculateRadialVelocity, calculateCombinedVelocity, calculateRadialNormal, calculateTransveralVelocity, calculateAngularVelocity):
    surfaceDist = max(ball.surfaceDist, 0)
    velocity = None
    radialVelocity = None
    angularVelocity = None
    transveralVelocity = None
    if calculateCombinedVelocity:
        CombVel4 = (ball.vx - myBall.vx, ball.vy - myBall.vy, ball.vz - myBall.vz)
    if calculateRadialNormal:
        RadNorm4 = geo2.Vec3Normalize((ball.x - myBall.x, ball.y - myBall.y, ball.z - myBall.z))
    if calculateVelocity:
        velocity = ball.GetVectorDotAt(blue.os.GetSimTime()).Length()
    if calculateRadialVelocity:
        radialVelocity = geo2.Vec3Dot(CombVel4, RadNorm4)
    if calculateTransveralVelocity:
        transveralVelocity = geo2.Vec3Length(geo2.Vec3Subtract(CombVel4, geo2.Vec3Scale(RadNorm4, radialVelocity)))
    if calculateAngularVelocity:
        angularVelocity = transveralVelocity / max(1.0, surfaceDist)
    node.rawVelocity = velocity
    node.rawRadialVelocity = radialVelocity
    node.rawAngularVelocity = angularVelocity
    node.rawTransveralVelocity = transveralVelocity
    if node.sortVelocityIndex is not None:
        node.sortValue[node.sortVelocityIndex] = velocity
    if node.sortRadialVelocityIndex is not None:
        node.sortValue[node.sortRadialVelocityIndex] = radialVelocity
    if node.sortAngularVelocityIndex is not None:
        node.sortValue[node.sortAngularVelocityIndex] = angularVelocity
    if node.sortTransversalVelocityIndex is not None:
        node.sortValue[node.sortTransversalVelocityIndex] = transveralVelocity
