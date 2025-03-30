#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\planet\colonyTemplateLoading.py
import evetypes
import locks
import blue
import uthread2
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.client.script.ui.shared.messagebox import MessageBox
from eve.client.script.ui.shared.planet import planetUtil
import eve.client.script.ui.shared.planet.planetConst as planetConst
from eve.client.script.ui.shared.planet.planetUtil import ConvertPinType
from eve.common.script.planet.planetUtil import CMDCTRSTRING
from eve.common.script.planet.surfacePoint import SurfacePoint
from eveplanet.client.templates.templateConst import TemplateDictKeys, TemplatePinDataDictKeys, TemplateLinkDataDictKeys, TemplateRouteDataDictKeys
from eveplanet.client.templates.verification import VerifyTemplate
from localization import GetByLabel
from carbonui.uicore import uicore
import carbonui.const as uiconst
import inventorycommon.const as invConst
import eve.common.lib.appConst as appConst

def PreviewLoad(colonyTemplate):
    VerifyTemplate(colonyTemplate.loadedTemplate)
    if not planetUtil.IsSerenity():
        planetUI = sm.GetService('planetUI')
        cmdCtrPin = planetUI.myPinManager.GetCommandCenterPin()
        if cmdCtrPin is None or cmdCtrPin.pin.IsInEditMode():
            raise UserError('NeedCmdCtrToUseTemplate')
    from eve.client.script.ui.shared.planet.templatePreviewWindow import TemplatePreviewWindow
    wnd = TemplatePreviewWindow.GetIfOpen()
    if wnd:
        wnd.Maximize()
        ShowQuickMessage(GetByLabel('UI/PI/AlreadyLoading'))
        return
    tpw = TemplatePreviewWindow(parent=uicore.layer.planet, template=colonyTemplate, clientPlanet=sm.GetService('planetUI').GetCurrentPlanet())


def LoadPiTemplate(newSPs, colonyTemplate):
    with locks.TempLock('PITemplate_Load'):
        return _LoadPiTemplate(newSPs, colonyTemplate)


def _LoadPiTemplate(newSPs, colonyTemplate):
    planetUI = sm.GetService('planetUI')
    hasCommandCenterInTemplate = False
    cmdCtrPin = planetUI.myPinManager.GetCommandCenterPin()
    alreadyHaveCmdCtr = bool(cmdCtrPin)
    if not planetUtil.IsSerenity():
        if cmdCtrPin is None or cmdCtrPin.pin.IsInEditMode():
            raise UserError('NeedCmdCtrToUseTemplate')
    cmdCtrItemID = None
    templateData = colonyTemplate.loadedTemplate
    ShowQuickMessage(GetByLabel('UI/PI/PinBuildingStarted'))
    if newSPs is None:
        newSPs = {}
        for pin in templateData[TemplateDictKeys.PinData]:
            point = SurfacePoint(theta=pin[TemplatePinDataDictKeys.Longi], phi=pin[TemplatePinDataDictKeys.Lat])
            newSPs[str(pin)] = (point,)

    for pin in templateData[TemplateDictKeys.PinData]:
        pinTypeInTemplate = pin[TemplatePinDataDictKeys.PinTypeID]
        pinType = ConvertPinType(pinTypeInTemplate, planetUI.planet.GetPlanetTypeID())
        if pinType is None:
            uicore.Message('CustomError', {'error': GetByLabel('UI/PI/DoNotHaveCorrespondingPin', pinTypeName=evetypes.GetName(pinTypeInTemplate))})
            return False
        if pinType not in planetConst.TYPEIDS_COMMAND_CENTER:
            continue
        cmdCtrPinPos = newSPs[str(pin)][0]
        if not alreadyHaveCmdCtr:
            planetUI.myPinManager.PlacePinType(cmdCtrPinPos, pinType)
            _AttemptToUpgradeCommandCenter(templateData)
        cmdCtrItemID = planetUI.planet.colony.colonyData.commandPin.id
        hasCommandCenterInTemplate = True
        break

    pinIDCountCompensator = 0
    if not hasCommandCenterInTemplate:
        if alreadyHaveCmdCtr:
            pinIDCountCompensator = -1
            cmdCtrItemID = planetUI.planet.colony.colonyData.commandPin.id
            if planetUI.planet.colony.colonyData.level < templateData[TemplateDictKeys.CmdCenterLV]:
                _AttemptToUpgradeCommandCenter(templateData)
        else:
            sm.GetService('gameui').MessageBox(text=GetByLabel('UI/PI/NoCmdCtrWillSupportSoon'), title=GetByLabel('UI/Common/Error'), buttons=uiconst.CLOSE, icon=uiconst.ERROR)
            return False
    cmdCtrPinPos = SurfacePoint(theta=planetUI.planet.colony.colonyData.commandPin.longitude, phi=planetUI.planet.colony.colonyData.commandPin.latitude)
    pinIDCount = 1
    blue.pyos.synchro.SleepWallclock(1000)
    existedPinsRecorder = set(planetUI.myPinManager.pinsByID.keys())
    idxToPinTable = {}
    idxToPinTable[CMDCTRSTRING] = CMDCTRSTRING
    debugIdxToPinTable = {}
    totalNumPins = len(templateData[TemplateDictKeys.PinData])
    for pin in templateData[TemplateDictKeys.PinData]:
        pinTypeInTemplate = pin[TemplatePinDataDictKeys.PinTypeID]
        pinType = ConvertPinType(pinTypeInTemplate, planetUI.planet.GetPlanetTypeID())
        if pinType is None:
            MessageBox.show_message_modal('CustomError', {'error': GetByLabel('UI/PI/DoNotHaveCorrespondingPin', pinTypeName=evetypes.GetName(pinTypeInTemplate))})
            return False
        if pinType in planetConst.TYPEIDS_COMMAND_CENTER:
            existedPinsRecorder = set(planetUI.myPinManager.pinsByID.keys())
            continue
        position = newSPs[str(pin)][0]
        planetUI.myPinManager.PlacePinType(position, pinType)
        blue.pyos.synchro.SleepWallclock(200)
        newExistedPinsRecorder = set(planetUI.myPinManager.pinsByID.keys())
        newPinIDs = newExistedPinsRecorder.difference(existedPinsRecorder)
        if len(newPinIDs) != 1 and cmdCtrItemID not in newPinIDs:
            raise UserError('CustomError', {'error': GetByLabel('UI/PI/PINError')})
        else:
            popped = newPinIDs.pop()
            if popped == cmdCtrItemID:
                popped = newPinIDs.pop()
            idxToPinTable[pinIDCount] = popped[1]
            debugIdxToPinTable[pinIDCount] = evetypes.GetName(pinType)
            existedPinsRecorder = set(planetUI.myPinManager.pinsByID.keys())
        if pinType in planetConst.TYPEIDS_PROCESSORS and pin[TemplatePinDataDictKeys.Product] is not None:
            try:
                planetUI.myPinManager.InstallSchematic((1, idxToPinTable[pinIDCount]), planetConst.OUTPUT_TO_SCHEMATICID[pin[TemplatePinDataDictKeys.Product]])
            except:
                pass

        elif evetypes.GetGroupID(pinType) == invConst.groupExtractionControlUnitPins:
            pass
        ShowQuickMessage(GetByLabel('UI/PI/PinBuildingProgress', currentNum=pinIDCount, totalNum=totalNumPins), flashNewText=False)
        pinIDCount += 1

    ShowQuickMessage(GetByLabel('UI/PI/LinkBuildingStarted'), flashNewText=False)
    totalNumLinks = len(templateData[TemplateDictKeys.LinkData])
    for i, link in enumerate(templateData[TemplateDictKeys.LinkData]):
        sou = idxToPinTable[link[TemplateLinkDataDictKeys.Source]]
        des = idxToPinTable[link[TemplateLinkDataDictKeys.Destination]]
        if sou != CMDCTRSTRING and des != CMDCTRSTRING and sou > des:
            sou, des = des, sou
        oneSou = (1, sou) if sou != CMDCTRSTRING else cmdCtrItemID
        oneDes = (1, des) if des != CMDCTRSTRING else cmdCtrItemID
        planetUI.myPinManager.SetLinkChild(oneSou, oneDes, False)
        blue.pyos.synchro.SleepWallclock(100)
        planetUI.myPinManager.UpgradeLink(oneSou, oneDes, link[TemplateLinkDataDictKeys.Level])
        ShowQuickMessage(GetByLabel('UI/PI/LinkBuildingProgress', currentNum=i + 1, totalNum=totalNumLinks), flashNewText=False)

    uthread2.Yield()
    ShowQuickMessage(GetByLabel('UI/PI/RouteBuildingStarted'), flashNewText=False)
    totalNumRoutes = len(templateData[TemplateDictKeys.RouteData])
    failedRoutes = []
    for i, route in enumerate(templateData[TemplateDictKeys.RouteData]):
        path = []
        skipThisRoute = False
        for node in route[TemplateRouteDataDictKeys.Path]:
            if node == CMDCTRSTRING:
                uicore.Message('CustomError', {'error': GetByLabel('UI/PI/LinkWithCmdCtrNotAvailable')})
                skipThisRoute = True
                break
            else:
                path.append((1, idxToPinTable[node]))
                adjustedNode = node + pinIDCountCompensator
                pinType = templateData[TemplateDictKeys.PinData][adjustedNode][TemplatePinDataDictKeys.PinTypeID]
                if evetypes.GetGroupID(pinType) == invConst.groupExtractionControlUnitPins:
                    skipThisRoute = True
                    break

        if skipThisRoute:
            continue
        try:
            planetUI.planet.CreateRoute(path, route[TemplateRouteDataDictKeys.ItemType], route[TemplateRouteDataDictKeys.ItemQuantity])
        except StandardError:
            failedRoutes.append(route)

        ShowQuickMessage(GetByLabel('UI/PI/RouteBuildingProgress', currentNum=i + 1, totalNum=totalNumRoutes), flashNewText=False)

    if failedRoutes:
        textList = []
        for eachRoute in failedRoutes:
            rTextList = []
            for pinInRoute in eachRoute[TemplateRouteDataDictKeys.Path]:
                adjustedPin = pinInRoute + pinIDCountCompensator
                pinType = templateData[TemplateDictKeys.PinData][adjustedPin][TemplatePinDataDictKeys.PinTypeID]
                convertedPinType = ConvertPinType(pinType, planetUI.planet.GetPlanetTypeID())
                rTextList.append(evetypes.GetName(convertedPinType))

            itemTypeName = evetypes.GetName(eachRoute[TemplateRouteDataDictKeys.ItemType])
            routeText = ' -> '.join(rTextList)
            textList.append(u'\u2022 %s (%s)' % (routeText, itemTypeName))

        routeList = '<br>'.join(textList)
        eve.Message('PiTemplateRoutesFailed', {'routeList': routeList})
    return True


def _AttemptToUpgradeCommandCenter(templateData):
    planetUI = sm.GetService('planetUI')
    currentLevel = planetUI.planet.colony.colonyData.level
    commandCenterLevel = templateData[TemplateDictKeys.CmdCenterLV]
    try:
        planetUI.planet.UpgradeCommandCenter(planetUI.planet.colony.colonyData.commandPin.id, commandCenterLevel)
    except UserError as e:
        if e.msg == 'CantUpgradeCommandCenterSkillRequired':
            text = GetByLabel('UI/PI/UnableToUpgradeCommandCenter', skillName=evetypes.GetName(appConst.typeCommandCenterUpgrade), requestedLevel=e.dict['requestedLevel'])
            ShowQuickMessage(text)
            skillLevel = sm.GetService('skills').GetEffectiveLevel(appConst.typeCommandCenterUpgrade)
            if skillLevel and skillLevel > currentLevel:
                planetUI.planet.UpgradeCommandCenter(planetUI.planet.colony.colonyData.commandPin.id, skillLevel)
        else:
            raise
