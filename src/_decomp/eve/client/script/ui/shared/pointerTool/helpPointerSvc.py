#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\pointerTool\helpPointerSvc.py
import re
import blue
import carbonui.const as uiconst
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
import eveexceptions
import log
import mathext
import uthread
from carbon.common.script.sys.service import Service
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.uicore import uicore
from eve.client.script.ui.inflight.selectedItemConst import ICON_ID_AND_CMD_BY_ACTIONID
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupProvider
from eve.client.script.ui.shared.agencyNew.contentGroups.contentGroupConst import contentGroupNameByID
from eve.client.script.ui.shared.neocom.neocom.btnData.btnDataRaw import BTNDATARAW_BY_ID
from eve.client.script.ui.shared.neocom.neocom.buttons.buttonEveMenu import ButtonEveMenu
from eve.client.script.ui.shared.neocom.neocom.neocomConst import BTNTYPE_GROUP, BTNTYPE_CMD, BTNTYPE_INVENTORY, BTNTYPE_CHAT, RAWDATA_SKILLS, BTNTYPE_CAREER_PROGRAM
from eve.client.script.ui.shared.neocom.neocom.neocomRawData import GetEveMenuRawData
from eve.client.script.ui.shared.pointerTool.entry import PointerWndEntry
from eve.client.script.ui.shared.pointerTool.link import SCHEME_HELP_POINTER
from eve.client.script.ui.shared.pointerTool.message_bus.helpPointerMessenger import HelpPointerMessenger
from eve.client.script.ui.shared.pointerTool.pointerObject import GetPointerObjectFromAuthoredPointer, GetPointerObjectFromActions, GetPointerObjectForStationSvc, GetPointerObjectForAgencyTab, GetPointerObjectForNeocom, GetPointerObjectForAgencyCard, GetPointerObjectForSkillPlan, GetPointerObjectForSkillPlanFaction, GetPointerObjectForSkillPlanCareer
from eve.client.script.ui.shared.pointerTool.pointerOverlay import PointerOverlay
from eve.client.script.ui.shared.pointerTool.pointerToolUtil import GetFilteredNodes, TextAndTexture
from eve.client.script.ui.shared.pointerTool.textContainerWithSubIcon import PointerContainerWithPath
from eve.client.script.ui.station.stationServiceConst import serviceDataByNameID
from eve.common.script.sys.idCheckers import IsNPCCorporation
from eveexceptions import UserError
from expiringdict import ExpiringDict
from fsdBuiltData.common.uiHelpPointersFSDLoader import UiHelpPointersFSDLoader
from localization import GetByLabel
from skills.skillplan.skillPlanService import GetSkillPlanSvc
from uihighlighting import UiHighlightDirections
from uihighlighting.ui.uipointer import CONTENT_CONTAINER_PADDING, UIPOINTER_WIDTH
NEOCOM_E_ICON = 'res:/UI/Texture/icons/79_64_11.png'
urlText = 'a href="{}:'.format(SCHEME_HELP_POINTER)
POINTER_TAG_PATTERN = '<%s[\\w.]+">' % urlText
POINTER_URL_END = '">'

class HelpPointerSvc(Service):
    __guid__ = 'svc.helpPointer'
    __servicename__ = 'helpPointer'
    __displayname__ = 'Help Pointer Service'

    def __init__(self):
        self._action_label_paths_by_element_name = None
        self._agency_label_by_element_name = None
        self._all_pointers_by_element_name = None
        self._highlight_by_element_name = None
        self._loading = False
        self._neocom_pointers_by_element_name = None
        self._ready = False
        self._station_service_text_by_element_name = None
        self._skill_plans_by_name = None
        self.pendingPointers = ExpiringDict(100, 5)
        self.pendingThread = None
        self.pointerOverlay = None
        self.utilMenuHighlights = ExpiringDict(100, 5)
        super(HelpPointerSvc, self).__init__()

    def GetActionLabelPathsByElementName(self):
        return self.action_label_paths_by_element_name

    @property
    def action_label_paths_by_element_name(self):
        self._ensure_loaded()
        return self._action_label_paths_by_element_name

    def GetHighlightByElementName(self):
        return self.highlight_by_element_name

    @property
    def highlight_by_element_name(self):
        self._ensure_loaded()
        return self._highlight_by_element_name

    def GetStationServiceTextByElementName(self):
        return self.station_service_text_by_element_name

    @property
    def station_service_text_by_element_name(self):
        self._ensure_loaded()
        return self._station_service_text_by_element_name

    def GetAgencyLabelByElementName(self):
        return self.agency_label_by_element_name

    @property
    def agency_label_by_element_name(self):
        self._ensure_loaded()
        return self._agency_label_by_element_name

    def GetNeocomPointersByElementName(self):
        return self.neocom_pointers_by_element_name

    @property
    def neocom_pointers_by_element_name(self):
        self._ensure_loaded()
        return self._neocom_pointers_by_element_name

    @property
    def skill_plans_by_name(self):
        self._ensure_loaded()
        return self._skill_plans_by_name

    def GetSkillPlansByElementName(self):
        return self.skill_plans_by_name

    def GetAllPointersByElementName(self):
        return self.all_pointers_by_element_name

    @property
    def all_pointers_by_element_name(self):
        self._ensure_loaded()
        return self._all_pointers_by_element_name

    def _ensure_loaded(self):
        if self._ready:
            return
        if self._loading:
            while self._loading:
                blue.synchro.Yield()

            return
        self._loading = True
        try:
            self._load_data()
            self._ready = True
        finally:
            self._loading = False

    def _load_data(self):
        higlights_data = UiHelpPointersFSDLoader.GetData()
        self._highlight_by_element_name = {x.uiElementName:GetPointerObjectFromAuthoredPointer(x) for x in higlights_data.itervalues()}
        self._action_label_paths_by_element_name = self._load_all_action_options_pointers()
        self._station_service_text_by_element_name = self._load_station_services_by_unique_name()
        self._agency_label_by_element_name = self._load_agency_pointers()
        self._neocom_pointers_by_element_name = self._load_neocom_buttons_by_pointer()
        self._skill_plans_by_name = self._load_skill_plans_pointers()
        self._all_pointers_by_element_name = self._action_label_paths_by_element_name.copy()
        self._all_pointers_by_element_name.update(self._station_service_text_by_element_name)
        self._all_pointers_by_element_name.update(self._agency_label_by_element_name)
        self._all_pointers_by_element_name.update(self._neocom_pointers_by_element_name)
        self._all_pointers_by_element_name.update(self._highlight_by_element_name)
        self._all_pointers_by_element_name.update(self._skill_plans_by_name)

    def _load_station_services_by_unique_name(self):
        wanted = [serviceDataByNameID['charcustomization'],
         serviceDataByNameID['medical'],
         serviceDataByNameID['repairshop'],
         serviceDataByNameID['reprocessingPlant'],
         serviceDataByNameID['navyoffices'],
         serviceDataByNameID['insurance'],
         serviceDataByNameID['lpstore'],
         serviceDataByNameID['securityoffice']]
        servicesByUniqueName = {}
        for serviceInfo in wanted:
            pointerObj = GetPointerObjectForStationSvc(serviceInfo)
            servicesByUniqueName[pointerObj.uiElementName] = pointerObj

        return servicesByUniqueName

    def _load_all_action_options_pointers(self):
        ret = {}
        for labelPath, action in ICON_ID_AND_CMD_BY_ACTIONID.iteritems():
            pointerObj = GetPointerObjectFromActions(labelPath, action)
            if pointerObj is not None:
                ret[pointerObj.uiElementName] = pointerObj

        return ret

    def _load_agency_pointers(self):
        ret = {}
        rootContentGroup = contentGroupProvider.GetRootContentGroup()
        for g in rootContentGroup.children:
            if not g.IsContentAvailable():
                continue
            pointerObject = GetPointerObjectForAgencyTab(g)
            ret[pointerObject.uiElementName] = pointerObject
            self._add_agency_card_children(ret, g.children)

        return ret

    def _add_agency_card_children(self, pointerDict, groupChildren, level = 0):
        for eachChild in groupChildren:
            contentGroupID = eachChild.contentGroupID
            namePath = contentGroupNameByID.get(contentGroupID, None)
            if namePath:
                pointerObject = GetPointerObjectForAgencyCard(eachChild)
                pointerDict[pointerObject.uiElementName] = pointerObject
            self._add_agency_card_children(pointerDict, eachChild.children, level=level + 1)

    def _load_skill_plans_pointers(self):
        ret = {}
        allCertifiedSkillPlans = GetSkillPlanSvc().GetAllCertified()
        for eachPlan in allCertifiedSkillPlans.itervalues():
            pointerObject = GetPointerObjectForSkillPlan(eachPlan)
            ret[pointerObject.uiElementName] = pointerObject
            pointerObject = GetPointerObjectForSkillPlanFaction(eachPlan)
            if pointerObject:
                ret[pointerObject.uiElementName] = pointerObject
            pointerObject = GetPointerObjectForSkillPlanCareer(eachPlan)
            if pointerObject:
                ret[pointerObject.uiElementName] = pointerObject

        return ret

    def _load_neocom_buttons_by_pointer(self):
        from eve.client.script.ui.shared.neocom.neocom.btnData.btnDataRaw import BTNDATARAW_BY_ID
        neocomDataByPointerName = {}
        allValidBtnIDs = set()
        btnData = GetEveMenuRawData() + list(RAWDATA_SKILLS) + [(BTNTYPE_CHAT, 'chat', None)]
        self._add_valid_buttons_for_data(btnData, allValidBtnIDs)
        validBtnData = []
        for eachBtnID in allValidBtnIDs:
            eachData = BTNDATARAW_BY_ID.get(eachBtnID, None)
            if not eachData or not uicore.cmd.IsCommandAllowed(eachData.cmdName):
                continue
            validBtnData.append((eachBtnID, eachData))

        fixedBtnData = sm.GetService('neocom').GetFixedButtonData()
        if fixedBtnData:
            for eachDataNode in fixedBtnData.children:
                validBtnData.append((eachDataNode.id, eachDataNode))

        for eachBtnID, eachData in validBtnData:
            cmd = uicore.cmd.commandMap.GetCommandByName(eachData.cmdName)
            if cmd:
                text = cmd.GetName()
            elif eachData and eachData.label is not None:
                text = GetByLabel(eachData.label)
            else:
                continue
            pointerObject = GetPointerObjectForNeocom(eachBtnID, eachData, text)
            neocomDataByPointerName[pointerObject.uiElementName] = pointerObject

        return neocomDataByPointerName

    def _add_valid_buttons_for_data(self, btnData, validBtns):
        for each in btnData:
            btnType, btnID, btnChildren = each
            if btnType in (BTNTYPE_CMD,
             BTNTYPE_INVENTORY,
             BTNTYPE_CHAT,
             BTNTYPE_CAREER_PROGRAM):
                validBtns.add(btnID)
            if btnType == BTNTYPE_GROUP and btnChildren:
                self._add_valid_buttons_for_data(btnChildren, validBtns)

    def ActivateHelperPointer(self, pointerUniqueName, sourceLocation = 0):
        self.LogPointerCreated(pointerUniqueName, sourceLocation)
        self._ActivateHelperPointer(pointerUniqueName)

    def _ActivateHelperPointer(self, pointerUniqueName, isFirstCall = True):
        myHighlight = self.GetAuthoredHighlightByName(pointerUniqueName)
        if myHighlight:
            textAndTexture = myHighlight.GetTexAndTexture()
        elif pointerUniqueName in self.action_label_paths_by_element_name:
            pointerObject = self.action_label_paths_by_element_name[pointerUniqueName]
            textAndTexture = pointerObject.GetTexAndTexture()
        elif pointerUniqueName in self.station_service_text_by_element_name:
            pointerObject = self.station_service_text_by_element_name[pointerUniqueName]
            textAndTexture = pointerObject.GetTexAndTexture()
        elif pointerUniqueName in self.agency_label_by_element_name:
            pointerObject = self.agency_label_by_element_name[pointerUniqueName]
            textAndTexture = pointerObject.GetTexAndTexture()
        elif pointerUniqueName in self.skill_plans_by_name:
            pointerObject = self.skill_plans_by_name[pointerUniqueName]
            textAndTexture = pointerObject.GetTexAndTexture()
        elif pointerUniqueName.startswith(pConst.NEOCOM_PREFIX):
            neocomID = pointerUniqueName.replace(pConst.NEOCOM_PREFIX, '')
            btnData = sm.GetService('neocom').GetBtnData(neocomID)
            if btnData and btnData.cmdName is not None:
                cmd = uicore.cmd.commandMap.GetCommandByName(btnData.cmdName)
                textAndTexture = TextAndTexture(cmd.GetName(), getattr(btnData, 'iconPath', None))
            elif btnData and btnData.label is not None:
                textAndTexture = TextAndTexture(btnData.label, getattr(btnData, 'iconPath', None))
            else:
                if pointerUniqueName in self.neocom_pointers_by_element_name:
                    label = getattr(self.neocom_pointers_by_element_name[pointerUniqueName], 'label', None)
                    if label:
                        notifyText = GetByLabel('UI/Help/PointerWndNotOnScreen', elementName=label)
                        raise UserError('CustomNotify', {'notify': notifyText})
                log.LogWarn('PointerWnd: Invalid pointer, pointerUniqueName=%s' % pointerUniqueName)
                raise UserError('CustomNotify', {'notify': GetByLabel('UI/Help/PointerWndInvalidPointer')})
        else:
            log.LogWarn('PointerWnd: Invalid pointer, pointerUniqueName=%s' % pointerUniqueName)
            raise UserError('CustomNotify', {'notify': GetByLabel('UI/Help/PointerWndInvalidPointer')})
        self.ShowPointer(pointerUniqueName, textAndTexture, isFirstCall)

    def ShowPointer(self, pointerUniqueName, uiPointerTextAndTexture, isFirstCall = True):
        if pointerUniqueName is None or pointerUniqueName == '':
            return
        pointToElement, newPointerName, extraLines, scopeWarnings, chainElements = self.FindElementToPointToAndScopeCheck(pointerUniqueName)
        from carbonui.control.window import Window
        if isinstance(pointToElement, Window):
            newPointerName = pointToElement.name
        if not pointToElement or not pointToElement.IsVisible():
            notifyText = '<br>'.join([GetByLabel('UI/Help/PointerWndNotOnScreen', elementName=uiPointerTextAndTexture.GetText())] + scopeWarnings)
            raise UserError('CustomNotify', {'notify': notifyText})
        subTextLines = self.GetSubText(pointerUniqueName, pointToElement, extraLines, chainElements)
        pointerNameToFind = newPointerName or pointerUniqueName
        defaultDirection = self.GetDirection(pointerNameToFind, pointToElement)
        uthread.new(self._ShowPointerThread, pointerNameToFind, uiPointerTextAndTexture, subTextLines, defaultDirection, not bool(chainElements))
        if self.IsMenuHighlight(pointerUniqueName):
            self.AddUniqueNameToUtilMenuHighlights(pointerUniqueName)
        if isFirstCall and chainElements:
            self.pendingPointers[pointerUniqueName] = True
            if self.pendingThread is None:
                self.pendingThread = AutoTimer(500, self.ShowPendingPointersThread)

    def FindElementToPointToAndScopeCheck(self, pointerName):
        elementKeyVal = sm.GetService('uipointerSvc').FindElementToPointTo(pointerName.split('.'), blinkNeocom=False, findWindow=True)
        element = elementKeyVal.pointToElement if elementKeyVal else None
        extraLines = getattr(elementKeyVal, 'extraTextLines', [])
        scopeWarningListEmpty = []
        chainElementsEmpty = []
        if element and element.IsVisible():
            return (element,
             None,
             extraLines,
             scopeWarningListEmpty,
             chainElementsEmpty)
        if element and not element.IsVisible() and not pointerName.startswith(pConst.NEOCOM_PREFIX):
            newPointerName = pConst.GetUniqueNeocomPointerName(pointerName)
            newElementKeyVal = sm.GetService('uipointerSvc').FindElementToPointTo(newPointerName.split('.'), blinkNeocom=False)
            if newElementKeyVal and newElementKeyVal.pointToElement:
                return (newElementKeyVal.pointToElement,
                 newPointerName,
                 extraLines,
                 scopeWarningListEmpty,
                 chainElementsEmpty)
        if not element or not element.IsVisible():
            scopeWarnings = self.GetScopeWarnings(pointerName)
            if scopeWarnings:
                return (None,
                 None,
                 [],
                 scopeWarnings,
                 chainElementsEmpty)
            from eve.client.script.ui.shared.pointerTool.pointerChains import FindChainForPointer
            pointerChain = FindChainForPointer(pointerName)
            chainElements = []
            for eachPointerName in reversed(pointerChain):
                nextElementKeyVal = sm.GetService('uipointerSvc').FindElementToPointTo(eachPointerName.split('.'), blinkNeocom=False, findWindow=True)
                chainElements.insert(0, eachPointerName)
                if nextElementKeyVal and nextElementKeyVal.pointToElement and nextElementKeyVal.pointToElement.IsVisible():
                    return (nextElementKeyVal.pointToElement,
                     eachPointerName,
                     extraLines,
                     scopeWarningListEmpty,
                     chainElements)

        return (None,
         None,
         extraLines,
         scopeWarningListEmpty,
         chainElementsEmpty)

    def GetAuthoredHighlightByName(self, pointerName):
        return self.highlight_by_element_name.get(pointerName, None)

    def GetDirection(self, pointerName, pointToElement = None):
        from carbonui.control.window import Window
        if isinstance(pointToElement, Window):
            return UiHighlightDirections.UP
        if pointerName in self.agency_label_by_element_name:
            return UiHighlightDirections.UP
        if pointerName in self.agency_label_by_element_name:
            return UiHighlightDirections.UP
        myHighlight = self.all_pointers_by_element_name.get(pointerName, None)
        if myHighlight:
            return myHighlight.defaultDirection

    def GetOffset(self, pointerName):
        if pointerName in self.action_label_paths_by_element_name:
            return -12
        myHighlight = self.GetAuthoredHighlightByName(pointerName)
        if myHighlight:
            return myHighlight.offset

    def IsMenuHighlight(self, pointerUniqueName):
        myHighlight = self.GetAuthoredHighlightByName(pointerUniqueName)
        if myHighlight:
            if myHighlight.isMenuOption:
                return True
        return False

    def GetScopeWarnings(self, pointerName):
        if pointerName in self.action_label_paths_by_element_name and not session.solarsystemid:
            return [GetByLabel('UI/HelpPointers/Wnd/ScopeInSpace')]
        myHighlight = self.GetAuthoredHighlightByName(pointerName)
        if not myHighlight:
            return ''
        pointerScope = myHighlight.pointerScope
        if not pointerScope:
            return ''
        scopeWarningList = []
        scope = [ x for x in pointerScope ]
        if 'Fleet' in scope and not session.fleetid:
            scopeWarningList.append(GetByLabel('UI/HelpPointers/Wnd/ScopeFleet'))
        if 'Docked' in scope and session.solarsystemid:
            scopeWarningList.append(GetByLabel('UI/HelpPointers/Wnd/ScopeDocked'))
        if 'InSpace' in scope and not session.solarsystemid:
            scopeWarningList.append(GetByLabel('UI/HelpPointers/Wnd/ScopeInSpace'))
        if 'PlayerCorp' in scope and IsNPCCorporation(session.corpid):
            scopeWarningList.append(GetByLabel('UI/HelpPointers/Wnd/ScopeInPlayerCorp'))
        return scopeWarningList

    def GetNameElements(self, pointerName):
        nameElements = pointerName.split('.')
        return nameElements

    def GetSubText(self, pointerName, pointToElement, extraLines, chainElements):
        extraTextList = []
        for x in extraLines or ():
            extraTextList.append(TextAndTexture(x, indentChar=''))

        extraTextList += self.FindSubTextAndIconForNeocomPointer(pointerName, pointToElement)
        for eachPointerName in chainElements:
            if eachPointerName in self.highlight_by_element_name:
                element = self.highlight_by_element_name[eachPointerName]
                extraTextList.append(TextAndTexture(element.label, element.texturePath, element.iconSizes, iconData=element.iconData))
            else:
                textPath = self.FindSubTextAndIconForNeocomPointer(eachPointerName, pointToElement)
                if textPath:
                    extraTextList = textPath + extraTextList
                else:
                    pointerObject = self.all_pointers_by_element_name.get(eachPointerName, None)
                    pointerText = pointerObject.label if pointerObject else ''
                    extraTextList.append(TextAndTexture(pointerText, pointerObject.texturePath, pointerObject.iconSizes, pointerObject.iconData))

        return extraTextList

    def FindSubTextAndIconForNeocomPointer(self, pointerName, pointToElement):
        if not isinstance(pointToElement, ButtonEveMenu) or not pointerName.startswith('neocom.'):
            return []
        nameElements = self.GetNameElements(pointerName)
        wndID = nameElements[1]
        actualBtn = pointToElement.btnData.GetBtnDataByTypeAndID(wndID, recursive=True)
        if actualBtn and getattr(actualBtn, 'parent', None):
            label = getattr(actualBtn.parent, 'label', None)
            if label:
                iconPath = getattr(actualBtn.parent, 'iconPath', None)
                pathList = [TextAndTexture(GetByLabel('UI/Help/PointerWndNeocomHeader'), NEOCOM_E_ICON), TextAndTexture(label, iconPath), TextAndTexture(actualBtn.label, actualBtn.iconPath)]
                return pathList
        return []

    def _ShowPointerThread(self, pointerName, uiPointerTextAndTexture, subTextLines, defaultDirection = None, finalPointer = True):
        offset = self.GetOffset(pointerName)
        highlightingSvc = sm.GetService('uiHighlightingService')
        if finalPointer:
            fadoutTime = 2
        else:
            fadoutTime = 0.75
        iconSize = 24
        maxTextWidth = 0
        if uiPointerTextAndTexture:
            maxTextWidth = uiPointerTextAndTexture.GetMaxWidth(0, iconSize)
        if subTextLines:
            maxSubLines = max((x.GetMaxWidth(i, iconSize) for i, x in enumerate(subTextLines)))
            maxTextWidth = max(maxTextWidth, maxSubLines)
        maxTextWidth += 2 * CONTENT_CONTAINER_PADDING
        defaultPointerWidth = UIPOINTER_WIDTH - 2 * CONTENT_CONTAINER_PADDING
        pointerWidth = mathext.clamp(maxTextWidth, defaultPointerWidth, 2 * UIPOINTER_WIDTH - 2 * CONTENT_CONTAINER_PADDING)
        highlight_content = PointerContainerWithPath(align=uiconst.TOLEFT, name='textContainer', width=pointerWidth, height=0, titleAndIcon=uiPointerTextAndTexture, textAndIconObjects=subTextLines, iconSize=iconSize)
        highlightingSvc.custom_highlight_ui_element_by_name(ui_element_name=pointerName, offset=offset, highlight_content=highlight_content, fadeout_seconds=fadoutTime, allowOffscreenPointing=True, default_direction=defaultDirection, idx=0)

    def ShowPendingPointersThread(self):
        pointersFound = False
        try:
            for pointerName in self.pendingPointers.iterkeys():
                if self.pendingPointers.get(pointerName, False):
                    pointersFound = True
                    self._ActivateHelperPointer(pointerName, isFirstCall=False)

            if not pointersFound:
                self.pendingThread = None
        except StandardError:
            self.pendingPointers.clear()
            self.pendingThread = None
            raise

    def SearchPointers(self, searchStr):
        filteredNodes = GetFilteredNodes(searchStr, sourceLocation=pConst.SOURCE_LOCATION_SEARCH)
        if filteredNodes:
            from eve.client.script.ui.control.entries.util import GetFromClass
            from eve.client.script.ui.control.listgroup import ListGroup
            from eve.client.script.ui.util.searchUtil import GetScrollListGroup
            data = GetScrollListGroup(filteredNodes, PointerWndEntry, GetByLabel('UI/Help/PointerWndUiElementsSearch'), 'uiPointers')
            return ([GetFromClass(ListGroup, data)], len(filteredNodes))
        return ([], 0)

    def FindLocalChatWindow(self, uniqueUiName):
        return self._FindChatWnd('chatchannel_local', uniqueUiName)

    def FindCorpChatWindow(self, uniqueUiName):
        return self._FindChatWnd('chatchannel_corp', uniqueUiName)

    def FindFleetChatWindow(self, uniqueUiName):
        return self._FindChatWnd('chatchannel_fleet', uniqueUiName)

    def _FindChatWnd(self, windowID, uniqueUiName):
        from chat.client.window import BaseChatWindow
        wnd = BaseChatWindow.GetIfOpen(windowID=windowID)
        if wnd and not wnd.destroyed:
            wnd.uniqueUiName = uniqueUiName
            if hasattr(wnd, 'InStack') and wnd.InStack():
                return wnd.sr.tab
            return wnd

    @eveexceptions.EatsExceptions('protoClientLogs')
    def LogPointerCreated(self, pointerUniqueName, sourceLocation):
        message_bus = HelpPointerMessenger(sm.GetService('publicGatewaySvc'))
        message_bus.pointer_created(pointerUniqueName, sourceLocation)

    @eveexceptions.EatsExceptions('protoClientLogs')
    def LogPointerLinkCreated(self, pointerUniqueName):
        message_bus = HelpPointerMessenger(sm.GetService('publicGatewaySvc'))
        message_bus.link_created(pointerUniqueName)

    def FindTagToIgnore(self, text):
        if text.find(SCHEME_HELP_POINTER) < 0:
            return []
        matches = re.findall(POINTER_TAG_PATTERN, text)
        tagsToIgnore = []
        for eachMatch in matches:
            pointerName = eachMatch.replace('<%s' % urlText, '')
            if pointerName.endswith(POINTER_URL_END):
                pointerName = pointerName.rstrip(POINTER_URL_END)
            if self._IsValidPointerName(pointerName):
                tag = '%s%s"' % (urlText, pointerName)
                tagsToIgnore.append(tag)

        if tagsToIgnore:
            tagsToIgnore.append('/a')
        return tagsToIgnore

    def _IsValidPointerName(self, pointerName):
        if pointerName in self.highlight_by_element_name:
            return True
        if pointerName in self.all_pointers_by_element_name:
            return True
        if pointerName.startswith(pConst.NEOCOM_PREFIX):
            neocomID = pointerName.replace(pConst.NEOCOM_PREFIX, '')
            btnData = BTNDATARAW_BY_ID.get(neocomID)
            if btnData and btnData.cmdName is not None:
                return True
        return False

    def IsUtilMenuEntryHighlighted(self, uniqueUiName):
        return uniqueUiName in self.utilMenuHighlights

    def AddUniqueNameToUtilMenuHighlights(self, uniqueUiName):
        self.utilMenuHighlights[uniqueUiName] = True

    def GetPointerOverlay(self, create = False):
        if self.pointerOverlay is None and create:
            self.pointerOverlay = PointerOverlay()
        return self.pointerOverlay

    def HidePointerOverlay(self):
        self.LogInfo('cmd:UI Pointer overlay: unload callback called')
        pointerHelper = self.GetPointerOverlay()
        if pointerHelper:
            self.LogInfo('cmd:UI Pointer overlay: hide overlay 1')
            pointerHelper.HideOverlay()
            self.LogInfo('cmd:Pointer overlay: hide overlay 2')
