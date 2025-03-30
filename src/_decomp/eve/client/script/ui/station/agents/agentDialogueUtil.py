#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\station\agents\agentDialogueUtil.py
import localization
from carbon.common.script.util.commonutils import StripTags
from carbonui.util.color import Color
from eve.common.lib import appConst
from eve.common.script.sys import idCheckers
from eve.common.script.util.eveFormat import FmtISK
from eveformat.client.location import get_security_status
from fsdBuiltData.common.iconIDs import GetIconFile
from npcs.divisions import get_division_name
from security.client.securityColor import get_security_status_color
CHECK_ICON = '<img src=icon:38_193 size=16>'
CROSS_ICON = '<img src=icon:38_194 size=16>'
CIRCLE_ICON = '<img src=icon:38_195 size=16>'
HIGH_SEC_COLOR = (0, 255, 255)
MEDIUM_HIGH_SEC_COLOR = (0, 255, 0)
MEDIUM_SEC_COLOR = (255, 255, 0)
LOW_SEC_COLOR = (255, 0, 0)

def _ProcessObjectiveEntry(objType, objData):
    html = ''
    if objType == 'agent':
        agentID, agentLocation = objData
        agentInfoIcon = '<a href=showinfo:%d//%d><img src=icon:38_208 size=16 alt="%s"></a>' % (cfg.eveowners.Get(agentID).typeID, agentID, StripTags(localization.GetByLabel('UI/Commands/ShowInfo')))
        html = '\n            <span id=caption>%(speakWithString)s %(agentInfoIcon)s</span><br>\n            <table>\n                <tr valign=middle>\n                    <td width=64>%(agentGraphic)s</td>\n                    <td>%(agentLocationHeader)s</td>\n                    <td>%(dropoffLocation)s</td>\n                </tr>\n            </table>\n            <br>\n        ' % {'speakWithString': localization.GetByLabel('UI/Agents/StandardMission/ObjectiveReportToAgent', agentID=agentID),
         'agentInfoIcon': agentInfoIcon,
         'agentGraphic': '<img src="portrait:%d" size=64 hspace=2 vspace=2>' % agentID,
         'dropoffLocation': LocationWrapper(agentLocation, 'agenthomebase'),
         'agentLocationHeader': localization.GetByLabel('UI/Agents/StandardMission/AgentLocation')}
    elif objType == 'transport':
        pickupOwnerID, pickupLocation, dropoffOwnerID, dropoffLocation, cargo = objData
        cargoObjectiveIcon = CHECK_ICON if cargo['hasCargo'] else CIRCLE_ICON
        isAtPickupLocation = pickupLocation['locationID'] == session.locationid
        if isAtPickupLocation or cargo['hasCargo']:
            pickupObjectiveIcon = CHECK_ICON
        else:
            pickupObjectiveIcon = CIRCLE_ICON
        pickupGraphic = _OwnerWrap(pickupOwnerID)
        isAtDropoffLocation = dropoffLocation['locationID'] == session.locationid
        if isAtDropoffLocation and (isAtPickupLocation or cargo['hasCargo']):
            dropoffObjectiveIcon = CHECK_ICON
        else:
            dropoffObjectiveIcon = CIRCLE_ICON
        dropoffGraphic = _OwnerWrap(dropoffOwnerID)
        cargoText = localization.GetByLabel('UI/Common/QuantityAndItem', quantity=cargo['quantity'], item=cargo['typeID'])
        if cargo['volume'] > 0:
            cargoText = localization.GetByLabel('UI/Agents/StandardMission/CargoDescriptionWithSize', cargoDescription=cargoText, size=cargo['volume'])
        cargoGraphic = _IconWrap(cargo['typeID'])
        html = '\n            <span id=caption>%(transportHeader)s</span><br>\n            <div id=basetext>%(transportBlurb)s\n            <br>\n            <table>\n                <tr valign=middle>\n                    <td>%(pickupObjectiveIcon)s</td>                \n                    <td width=32>%(pickupGraphic)s</td>\n                    <td>%(transportPickup)s</td>\n                    <td>%(pickupLocation)s</td>\n                </tr>\n                <tr valign=middle>\n                    <td>%(dropoffObjectiveIcon)s</td>                \n                    <td width=32>%(dropoffGraphic)s</td>\n                    <td>%(transportDropOff)s</td>\n                    <td>%(dropoffLocation)s</td>\n                </tr>\n                <tr valign=middle>\n                    <td>%(cargoObjectiveIcon)s</td>\n                    <td width=32>%(cargoGraphic)s</td>\n                    <td>%(transportCargo)s</td>\n                    <td>%(cargo)s</td>\n                </tr>\n            </table></div>\n            <br>\n        ' % {'transportHeader': localization.GetByLabel('UI/Agents/StandardMission/TransportObjectiveHeader'),
         'transportBlurb': localization.GetByLabel('UI/Agents/StandardMission/TransportBlurb'),
         'pickupObjectiveIcon': pickupObjectiveIcon,
         'pickupGraphic': pickupGraphic,
         'transportPickup': localization.GetByLabel('UI/Agents/StandardMission/TransportPickupLocation'),
         'pickupLocation': LocationWrapper(pickupLocation),
         'dropoffObjectiveIcon': dropoffObjectiveIcon,
         'dropoffGraphic': dropoffGraphic,
         'transportDropOff': localization.GetByLabel('UI/Agents/StandardMission/TransportDropOffLocation'),
         'dropoffLocation': LocationWrapper(dropoffLocation),
         'cargoObjectiveIcon': cargoObjectiveIcon,
         'cargoGraphic': cargoGraphic,
         'transportCargo': localization.GetByLabel('UI/Agents/StandardMission/TransportCargo'),
         'cargo': cargoText}
    elif objType == 'fetch':
        dropoffOwnerID, dropoffLocation, cargo = objData
        isAtDropoffLocation = dropoffLocation is not None and dropoffLocation['locationID'] == session.locationid
        dropoffObjectiveIcon = CHECK_ICON if isAtDropoffLocation else CIRCLE_ICON
        dropoffGraphic = _OwnerWrap(dropoffOwnerID)
        if dropoffLocation is not None:
            dropoffLocationText = LocationWrapper(dropoffLocation)
        else:
            dropoffLocationText = _OwnerWrap(dropoffOwnerID)
        cargoObjectiveIcon = CHECK_ICON if cargo['hasCargo'] else CIRCLE_ICON
        cargoGraphic = _IconWrap(cargo['typeID'])
        cargoText = localization.GetByLabel('UI/Common/QuantityAndItem', quantity=cargo['quantity'], item=cargo['typeID'])
        if cargo['volume'] > 0:
            cargoText = localization.GetByLabel('UI/Agents/StandardMission/CargoDescriptionWithSize', cargoDescription=cargoText, size=cargo['volume'])
        html = '\n            <span id=caption>%(fetchHeader)s</span><br>\n            <div id=basetext>%(fetchBlurb)s<br><br>\n            <table>\n                <tr valign=middle>\n                    <td>%(dropoffObjectiveIcon)s</td>\n                    <td width=32>%(dropoffGraphic)s</td>\n                    <td>%(fetchDropOff)s</td>\n                    <td>%(dropoffLocation)s</td>\n                </tr>\n                <tr valign=middle>\n                    <td>%(cargoObjectiveIcon)s</td>\n                    <td width=32>%(cargoGraphic)s</td>\n                    <td>%(fetchItem)s</td>\n                    <td>%(cargo)s</td>\n                </tr>\n            </table>\n            </div>\n            <br>\n        ' % {'fetchHeader': localization.GetByLabel('UI/Agents/StandardMission/FetchObjectiveHeader'),
         'fetchBlurb': localization.GetByLabel('UI/Agents/StandardMission/FetchObjectiveBlurb'),
         'dropoffObjectiveIcon': dropoffObjectiveIcon,
         'dropoffGraphic': dropoffGraphic,
         'fetchDropOff': localization.GetByLabel('UI/Agents/StandardMission/FetchObjectiveDropOffLocation'),
         'dropoffLocation': dropoffLocationText,
         'cargoObjectiveIcon': cargoObjectiveIcon,
         'cargoGraphic': cargoGraphic,
         'fetchItem': localization.GetByLabel('UI/Agents/StandardMission/FetchObjectiveItem'),
         'cargo': cargoText}
    return html


def _ProcessDungeonData(dunData, agentID):
    s1, s2 = ('', '')
    if 'completionStatus' in dunData:
        lbl = ['UI/Agents/StandardMission/DungeonObjectiveFailed', 'UI/Agents/StandardMission/DungeonObjectiveCompleted'][dunData['completionStatus']]
        s1 = '<strike>'
        s2 = '</strike> %s' % localization.GetByLabel(lbl)
    if dunData['optional']:
        objectiveTextTitle = localization.GetByLabel('UI/Agents/StandardMission/OptionalObjectiveHeader')
        objectiveTextBody = localization.GetByLabel('UI/Agents/StandardMission/OptionalObjectiveBody')
    else:
        objectiveTextTitle = localization.GetByLabel('UI/Agents/StandardMission/ObjectiveHeader')
        objectiveTextBody = localization.GetByLabel('UI/Agents/StandardMission/DungeonObjectiveBody')
    if 'briefingMessage' in dunData:
        objectiveTextBody = sm.GetService('agents').ProcessMessage(dunData['briefingMessage'], agentID)
    if dunData['objectiveCompleted'] is not None:
        objectiveIcon = [CROSS_ICON, CHECK_ICON][dunData['objectiveCompleted']]
    else:
        objectiveIcon = CIRCLE_ICON
    if 'ownerID' in dunData:
        dungeonGraphic = _OwnerWrap(dunData['ownerID'])
    else:
        dungeonGraphic = ''
    html = '\n        <span id=caption>%(objectiveTextTitle)s</span><br>\n        <div id=basetext> %(s1)s%(objectiveTextBody)s%(s2)s<br>\n        <table>\n            <tr valign=middle>\n                <td>%(objectiveIcon)s</td>\n                <td width=32>%(dungeonGraphic)s</td>\n                <td width=50>%(locationHeader)s</td>\n                <td width=200>%(dungeonLocation)s</td>\n            </tr>\n        </table></div>\n    ' % {'objectiveTextTitle': objectiveTextTitle,
     'objectiveTextBody': objectiveTextBody,
     'objectiveIcon': objectiveIcon,
     's1': s1,
     's2': s2,
     'locationHeader': localization.GetByLabel('UI/Agents/StandardMission/ObjectiveLocation'),
     'dungeonGraphic': dungeonGraphic,
     'dungeonLocation': LocationWrapper(dunData['location'])}
    if 'shipRestrictions' in dunData:
        lbl = ['UI/Agents/StandardMission/DungeonObjectiveNormalRestrictions', 'UI/Agents/StandardMission/DungeonObjectiveSpecialRestrictions'][dunData['shipRestrictions']]
        httpLink = '<a href=localsvc:method=PopupDungeonShipRestrictionList&agentID=%d&charID=%d&dungeonID=%d>' % (agentID, session.charid, dunData['dungeonID'])
        if dunData['shipRestrictions'] == 1:
            html += '<font color=#E3170D>'
        html += localization.GetByLabel(lbl, startHttpLink=httpLink, endHttpLink='</a>')
        if dunData['shipRestrictions'] == 1:
            html += '</font>'
        html += '<br>'
    return html


def _GetSecurityModifierIcon(solarSystemID):
    res = sm.GetService('securitySvc').get_security_modifier_icon_res_path(solarSystemID)
    if res:
        return '<a href=showinfo:{typeSolarSystem}//{solarSystemID}><img src="{resPath}" width=12 height=10 hspace=2 vspace=2></a>'.format(typeSolarSystem=appConst.typeSolarSystem, solarSystemID=solarSystemID, resPath=res)
    return ''


def LocationWrapper(location, locationType = None):
    if locationType is None and 'locationType' in location:
        locationType = location['locationType']
    solarSystemID = location['solarsystemID']
    securityStatus = get_security_status(solarSystemID)
    secColor = get_security_status_color(securityStatus)
    secColorAsHtml = Color.RGBtoHex(*secColor)
    secWarning = '<font color=#E3170D>'
    secClass = sm.GetService('securitySvc').get_modified_security_class(solarSystemID)
    if secClass <= appConst.securityClassLowSec:
        secWarning += localization.GetByLabel('UI/Agents/LowSecWarning')
    elif sm.GetService('crimewatchSvc').GetMySecurityStatus() <= -5:
        secWarning += localization.GetByLabel('UI/Agents/HighSecWarning')
    secWarning += '</font>'
    if 'coords' in location:
        x, y, z = location['coords']
        refAgentString = str(location['agentID'])
        if 'referringAgentID' in location:
            refAgentString += ',' + str(location['referringAgentID'])
        infoLinkData = ['showinfo',
         location['typeID'],
         location['locationID'],
         x,
         y,
         z,
         refAgentString,
         0,
         locationType]
    else:
        infoLinkData = ['showinfo', location['typeID'], location['locationID']]
    spacePigShipType = location.get('shipTypeID', None)
    if spacePigShipType is not None:
        locationName = localization.GetByLabel('UI/Agents/Items/ItemLocation', typeID=spacePigShipType, locationID=location['locationID'])
    else:
        locationName = cfg.evelocations.Get(location['locationID']).locationName
    image = _GetSecurityModifierIcon(solarSystemID)
    return localization.GetByLabel('UI/Agents/LocationWrapper', startFontTag='<font color=%s>' % secColorAsHtml, endFontTag='</font>', image=image, securityRating=securityStatus, locationName=locationName, linkdata=infoLinkData, securityWarning=secWarning)


def _OwnerWrap(ownerID, typeID = None):
    if ownerID is None:
        return ''
    elif idCheckers.IsFaction(ownerID):
        return '<a href=showinfo:%d//%d><img src="factionlogo:%d" width=32 height=32 hspace=2 vspace=2></a>' % (appConst.typeFaction, ownerID, ownerID)
    elif idCheckers.IsCorporation(ownerID):
        return '<a href=showinfo:%d//%d><img src="corplogo:%d" width=32 height=32 hspace=2 vspace=2></a>' % (appConst.typeCorporation, ownerID, ownerID)
    else:
        if not typeID:
            typeID = cfg.eveowners.Get(ownerID).typeID
        return '<a href=showinfo:%d//%d><img src="portrait:%d" width=32 height=32 hspace=2 vspace=2></a>' % (typeID, ownerID, ownerID)


def _IconWrap(typeID, extra = None):
    if typeID is None:
        return ''
    elif typeID == appConst.typeCredits:
        return '<img style:vertical-align:bottom src="icon:06_03" size="32">'
    elif extra and 'blueprintInfo' in extra:
        bpInfo = extra['blueprintInfo']
        return '<a href=showinfo:%d//0//%d//%d//%d//%d><img src="typeicon:%d" width=32 height=32 align=left iscopy=1></a>' % (typeID,
         bpInfo.get('licensedProductionRunsRemaining', 0),
         bpInfo.get('copy', 1),
         bpInfo.get('productivityLevel', 0),
         bpInfo.get('materialLevel', 0),
         typeID)
    else:
        return '<a href=showinfo:%d><img src="typeicon:%d" width=32 height=32 align=left></a>' % (typeID, typeID)


def _ProcessTypeAndQuantity(typeID, quantity, extra = None):
    if typeID == appConst.typeCredits:
        return FmtISK(quantity)
    elif extra is None:
        return cfg.FormatConvert(appConst.UE_TYPEIDANDQUANTITY, typeID, quantity)
    else:
        specificItemID = extra.get('specificItemID', 0)
        blueprintInfo = extra.get('blueprintInfo', None)
        if blueprintInfo is None:
            if specificItemID:
                props = [localization.GetByLabel('UI/Agents/Items/SpecificItems')]
            else:
                return cfg.FormatConvert(appConst.UE_TYPEIDANDQUANTITY, typeID, quantity)
        else:
            props = []
            if specificItemID:
                props.append(localization.GetByLabel('UI/Agents/Items/SpecificItems'))
            if blueprintInfo.get('licensedProductionRunsRemaining', 0) > 1:
                runsRemaining = blueprintInfo.get('licensedProductionRunsRemaining', 0)
                props.append(localization.GetByLabel('UI/Agents/Items/BlueprintInfoMultirun', runsRemaining=runsRemaining))
            elif blueprintInfo.get('licensedProductionRunsRemaining', 0) == 1:
                props.append(localization.GetByLabel('UI/Agents/Items/BlueprintInfoSingleRun'))
            if blueprintInfo.get('copy', 0):
                props.append(localization.GetByLabel('UI/Agents/Items/BlueprintInfoCopy'))
            else:
                props.append(localization.GetByLabel('UI/Agents/Items/BlueprintInfoOriginal'))
            if blueprintInfo.get('materialLevel', 0):
                props.append(localization.GetByLabel('UI/Agents/Items/BlueprintInfoMaterialLevel', materialLevel=blueprintInfo.get('materialLevel', 0)))
            if blueprintInfo.get('productivityLevel', 0):
                props.append(localization.GetByLabel('UI/Agents/Items/ProductivityLevel', productivityLevel=blueprintInfo.get('productivityLevel', 0)))
        return localization.GetByLabel('UI/Agents/Items/NumItemsAndProperties', itemAndQuantity=cfg.FormatConvert(appConst.UE_TYPEIDANDQUANTITY, typeID, quantity), propertyList=localization.formatters.FormatGenericList(props))


def GetMissionObjectiveHTML(agentID, objectiveData):
    html = ''
    if objectiveData.get('importantStandings', 0):
        html += '<span id=ip>%s</span><br><br>' % localization.GetByLabel('UI/Agents/StandardMission/ImportantStandingsWarning')
    cmpStatus = objectiveData['completionStatus']
    if isinstance(objectiveData['missionTitleID'], basestring):
        missionName = objectiveData['missionTitleID']
    else:
        missionName = localization.GetByMessageID(objectiveData['missionTitleID'])
    isMissionFinished = cmpStatus > 0
    isMissionFailed = objectiveData['missionState'] == appConst.agentMissionStateFailed
    isMissionCheatCompleted = cmpStatus == 2
    if isMissionFailed:
        missionHeaderColor = '<font color=#E3170D>'
        missionHeader = localization.GetByLabel('UI/Agents/StandardMission/MissionObjectivesFailed', missionName=missionName)
    elif isMissionFinished:
        missionHeaderColor = '<font color=#5ABA56>'
        missionHeader = localization.GetByLabel('UI/Agents/StandardMission/MissionObjectivesComplete', missionName=missionName)
    else:
        missionHeaderColor = '<font>'
        missionHeader = localization.GetByLabel('UI/Agents/StandardMission/MissionObjectives', missionName=missionName)
    if isMissionCheatCompleted:
        gmStatusHeader = '<font color=#00FF00>Debug Mode: Cheat Complete Enabled</div></font>'
    else:
        gmStatusHeader = ''
    objectives = ''
    for objType, objData in objectiveData['objectives']:
        objectives += _ProcessObjectiveEntry(objType, objData)

    for dunData in objectiveData['dungeons']:
        if isMissionFailed:
            dunData['completionStatus'] = 0
            dunData['objectiveCompleted'] = 0
        objectives += _ProcessDungeonData(dunData, agentID)

    html += '\n        %(GMStatusHeader)s\n        <span id=subheader>%(missionHeaderColor)s%(missionHeader)s</font></span><br>\n        <div id=basetext>%(objectivesHeader)s<br>\n        <br>\n        <span id=basetext>\n        %(objectives)s\n        </span>\n        <br>\n    ' % {'GMStatusHeader': gmStatusHeader,
     'missionHeader': missionHeader,
     'missionHeaderColor': missionHeaderColor,
     'objectivesHeader': localization.GetByLabel('UI/Agents/StandardMission/OverviewAndObjectivesBlurb'),
     'objectives': objectives}
    secWarning = GetSecurityWarning(objectiveData['locations'])
    if secWarning:
        html += '<font color=red>%s</font><br><br>' % secWarning

    def ProcessEntry(typeID, quantity, extra):
        if idCheckers.IsCharacter(typeID):
            iconWrap = _OwnerWrap(typeID)
            description = localization.GetByLabel('UI/Agents/StandardMission/MissionReferral', agentID=typeID)
        else:
            iconWrap = _IconWrap(typeID, extra)
            description = _ProcessTypeAndQuantity(typeID, quantity, extra)
        return (iconWrap, description)

    grantedItems = [ (typeID, quantity, extra) for typeID, quantity, extra in objectiveData['agentGift'] if quantity > 0 ]
    if len(grantedItems) > 0:
        if objectiveData['missionState'] in (appConst.agentMissionStateAccepted, appConst.agentMissionStateFailed):
            grantedItemsDetail = localization.GetByLabel('UI/Agents/StandardMission/AcceptedGrantedItemDetail')
        else:
            grantedItemsDetail = localization.GetByLabel('UI/Agents/StandardMission/GrantedItemDetail')
        html += '<br>\n            <span id=subheader>%s</span>\n            <div id=basetext>%s</div>\n            <div><table>\n        ' % (localization.GetByLabel('UI/Agents/StandardMission/GrantedItems'), grantedItemsDetail)
        for typeID, quantity, extra in grantedItems:
            icon, text = ProcessEntry(typeID, quantity, extra)
            html += '\n                <tr valign=middle>\n                    <td width=36>%s</td>\n                    <td width=352>%s</td>\n                </tr>\n                ' % (icon, text)

        html += '</table></div><br>'
    normalRewards = [ (typeID, quantity, extra) for typeID, quantity, extra in objectiveData['normalRewards'] if quantity > 0 ]
    loyaltyPoints = objectiveData['loyaltyPoints']
    researchPoints = objectiveData['researchPoints']
    if len(normalRewards) or loyaltyPoints > 0 or researchPoints > 0:
        html += '\n            <span id=subheader>%s</span>\n            <div id=basetext>%s</div>\n            <div><table>\n        ' % (localization.GetByLabel('UI/Agents/StandardMission/RewardsTitle'), localization.GetByLabel('UI/Agents/StandardMission/RewardsHeader'))
        for reward in normalRewards:
            typeID, quantity, extra = reward
            icon, text = ProcessEntry(typeID, quantity, extra)
            html += '\n                <tr valign=middle>\n                    <td width=36>%s</td>\n                    <td width=352>%s</td>\n                </tr>\n            ' % (icon, text)

        if loyaltyPoints > 0:
            icon, text = _GetLoyaltyPointsDisplay(agentID, loyaltyPoints)
            html += '\n                <tr valign=middle>\n                    <td width=36>%s</td>\n                    <td width=352>%s</td>\n                </tr>\n            ' % (icon, text)
        if objectiveData['researchPoints'] > 0:
            icon = _IconWrap(appConst.typeResearch)
            quantity = round(researchPoints, 0)
            text = localization.GetByLabel('UI/Agents/StandardMission/NumResearchPoints', rpAmount=quantity)
            html += '\n                <tr valign=middle>\n                    <td width=36>%s</td>\n                    <td width=352>%s</td>\n                </tr>\n            ' % (icon, text)
        html += '</table></div><br>'
    bonusRewards = [ (timeRemaining,
     typeID,
     quantity,
     extra,
     timeBonusIntervalMin) for timeRemaining, typeID, quantity, extra, timeBonusIntervalMin in objectiveData['bonusRewards'] if quantity > 0 ]
    if len(bonusRewards) > 0:
        html += '<span id=subheader>%s</span><br>' % localization.GetByLabel('UI/Agents/StandardMission/BonusRewardsTitle')
        for timeRemaining, typeID, quantity, extra, timeBonusIntervalMin in bonusRewards:
            if timeRemaining > 0:
                header = localization.GetByLabel('UI/Agents/StandardMission/BonusRewardsHeader', timeRemaining=timeRemaining)
            else:
                header = localization.GetByLabel('UI/Agents/StandardMission/BonusTimePassed')
            icon, text = ProcessEntry(typeID, quantity, extra)
            html += '\n                <div id=basetext>%s<br>\n                <div><table>\n                    <tr valign=middle>\n                        <td width=36>%s</TD>\n                        <td width=352>%s</TD>\n                    </tr>\n                </table></div>\n            ' % (header, icon, text)

        html += '<br>'
    collateral = [ (typeID, quantity, extra) for typeID, quantity, extra in objectiveData['collateral'] if quantity > 0 ]
    if len(collateral) > 0:
        html += '\n            <span id=subheader>%s</span>\n            <div id=basetext>%s</div><br>\n            <div><table>\n        ' % (localization.GetByLabel('UI/Agents/StandardMission/CollateralTitle'), localization.GetByLabel('UI/Agents/StandardMission/CollateralHeader'))
        for typeID, quantity, extra in collateral:
            icon = _IconWrap(typeID, extra)
            text = _ProcessTypeAndQuantity(typeID, quantity, extra)
            html += '\n                <tr valign=middle>\n                    <td width=36>%s</td>\n                    <td width=352>%s</td>\n                </tr>\n            ' % (icon, text)

        html += '</table></div><br>'
    if 'missionExtra' in objectiveData:
        headerID, bodyID = objectiveData['missionExtra']
        html += '\n            <span id=subheader>%s</span>\n            <div id=basetext>%s</div>\n        ' % (sm.GetService('agents').ProcessMessage((headerID, objectiveData['contentID']), agentID), sm.GetService('agents').ProcessMessage((bodyID, objectiveData['contentID']), agentID))
    return html


def _GetLoyaltyPointsDisplay(agentID, loyaltyPoints):
    agent = sm.GetService('agents').GetAgentByID(agentID)
    if agent and agent.divisionID == appConst.corpDivisionHeraldry:
        typeID = appConst.typeLoyaltyPointsHeraldry
        icon = _IconWrap(typeID)
        text = localization.GetByLabel('UI/Common/QuantityAndItem', quantity=loyaltyPoints, item=typeID)
        return (icon, text)
    icon = _IconWrap(appConst.typeLoyaltyPoints)
    text = localization.GetByLabel('UI/Agents/StandardMission/NumLoyaltyPoints', lpAmount=loyaltyPoints)
    return (icon, text)


def GetSecurityWarning(locations):
    routeStart = session.solarsystemid2
    charSecStatus = sm.GetService('crimewatchSvc').GetMySecurityStatus()
    secWarning = ''
    for each in locations:
        if len(secWarning) > 0:
            break
        if routeStart == session.solarsystemid2 and each == session.solarsystemid2:
            continue
        else:
            route = sm.GetService('clientPathfinderService').GetAutopilotPathBetween(routeStart, each)
        if route is None:
            secWarning = localization.GetByLabel('UI/Agents/Dialogue/AutopilotRouteNotFound')
            break
        elif len(route) > 0:
            routeStart = route[len(route) - 1]
            for solarsystem in route:
                if charSecStatus > -5.0 and sm.GetService('securitySvc').get_modified_security_class(solarsystem) <= appConst.securityClassLowSec:
                    secWarning = localization.GetByLabel('UI/Agents/Dialogue/AutopilotRouteLowSecWarning')
                    break
                elif charSecStatus < -5.0 and sm.GetService('securitySvc').get_modified_security_class(solarsystem) == appConst.securityClassHighSec:
                    secWarning = localization.GetByLabel('UI/Agents/Dialogue/AutopilotRouteHighSecWarning')
                    break

    return secWarning


def GetMissionDetailsWindowHTML(missionInfo, agentID):
    missionName = sm.GetService('agents').ProcessMessage((missionInfo['missionNameID'], missionInfo['contentID']), agentID)
    missionBriefing = sm.GetService('agents').ProcessMessage((missionInfo['briefingTextID'], missionInfo['contentID']), agentID)
    html = '\n        <html>\n        <head>\n            <LINK REL="stylesheet" TYPE="text/css" HREF="res:/ui/css/missionjournal.css">\n        </head>\n        <body>\n    '
    if 'iconID' in missionInfo:
        missionGraphic = GetIconFile(missionInfo['iconID'])
        if missionGraphic:
            html += '<p><img src="icon:%s" width=64 height=64 align=left hspace=4 vspace=4><br>' % missionGraphic
    html += '\n        <span id=mainheader>%(missionName)s</span><br>\n        <hr>\n        <center><span id=ip>%(missionImage)s</span></center><br>\n        </p>\n        <span id=subheader>%(briefingTitle)s</span>\n        <div id=basetext>%(missionBriefing)s</div>\n        <br>\n    ' % {'missionName': missionName,
     'missionImage': missionInfo['missionImage'],
     'briefingTitle': localization.GetByLabel('UI/Agents/StandardMission/MissionBriefing'),
     'missionBriefing': missionBriefing}
    expirationTime = missionInfo['expirationTime']
    if expirationTime is not None:
        if missionInfo['missionState'] in (appConst.agentMissionStateAllocated, appConst.agentMissionStateOffered):
            expirationMessage = localization.GetByLabel('UI/Agents/Dialogue/ThisOfferExpiresAt', expireTime=expirationTime)
        else:
            expirationMessage = localization.GetByLabel('UI/Agents/Dialogue/ThisMissionExpiresAt', expireTime=expirationTime)
        html += '<span id=ip>%s</span><br><br>' % expirationMessage
    html += GetMissionObjectiveHTML(agentID, missionInfo['objectives'])
    html += '</body></html>'
    return html


def GetAgentNameAndLevel(agentID, level):
    return localization.GetByLabel('UI/Agents/AgentEntryNameAndLevel', ownerID=agentID, level=level)


def GetAgentLocationHeader(agentInfo, agentLocation, loyaltyPoints = None):
    cfgAgent = cfg.eveowners.Get(agentInfo.agentID)
    agentInfoIcon = '<a href=showinfo:%d//%d><img src=icon:38_208 size=16 alt="%s"></a>' % (cfgAgent.typeID, agentInfo.agentID, StripTags(localization.GetByLabel('UI/Commands/ShowInfo'), stripOnly=['localized']))
    blurbDivision = localization.GetByLabel('UI/Agents/Dialogue/Division', divisionName=get_division_name(agentInfo.divisionID))
    s = [sm.GetService('standing').GetStandingWithSkillBonus(agentInfo.factionID, session.charid), sm.GetService('standing').GetStandingWithSkillBonus(agentInfo.corporationID, session.charid), sm.GetService('standing').GetStandingWithSkillBonus(agentInfo.agentID, session.charid)]
    if min(*s) <= -2.0:
        es = min(*s)
        blurbEffectiveStanding = localization.GetByLabel('UI/Agents/Dialogue/EffectiveStandingLow', effectiveStanding=es)
    else:
        es = max(*s) or 0.0
        blurbEffectiveStanding = localization.GetByLabel('UI/Agents/Dialogue/EffectiveStanding', effectiveStanding=es)
    if loyaltyPoints:
        loyaltyPointsBlurb = localization.GetByLabel('UI/Agents/Dialogue/LoyaltyPointsTableRow', loyaltyPoints=loyaltyPoints)
    else:
        loyaltyPointsBlurb = ''
    return '\n        <table border=0 cellpadding=0 cellspacing=0>\n            <tr>\n                <td valign=top width=140>\n                    <img src="portrait:%(agentID)d" width=128 height=128 size=256 style=margin-right:10>\n                </td>\n                <td valign=top>\n                    <font size=18>%(agentName)s</font> %(showInfoLink)s\n                    <br>\n                    %(blurbDivision)s\n                    <br><br>\n                    %(agentLocation)s\n                    <br>\n                    <br>\n                    %(blurbEffectiveStanding)s\n                    <br>\n                    %(loyaltyPoints)s\n                </td>\n            </tr>\n        </table>\n    ' % {'agentID': agentInfo.agentID,
     'agentName': cfgAgent.name,
     'showInfoLink': agentInfoIcon,
     'blurbDivision': blurbDivision,
     'agentLocation': LocationWrapper(agentLocation),
     'blurbEffectiveStanding': blurbEffectiveStanding,
     'loyaltyPoints': loyaltyPointsBlurb}
