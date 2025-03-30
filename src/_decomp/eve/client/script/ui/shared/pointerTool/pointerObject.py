#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\pointerTool\pointerObject.py
import re
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
import eveicon
import localization
from carbonui.uicore import uicore
from characterdata import factions
from characterdata.careerpath import get_career_path_name_id
from eve.client.script.ui.inflight import actionConst
from eve.client.script.ui.inflight.selectedItemConst import POINTER_ACTIONS
from eve.client.script.ui.shared.careerPortal import careerConst
from eve.client.script.ui.shared.pointerTool.pointerToolUtil import TextAndTexture
from eve.client.script.ui.skillPlan.skillPlanConst import ICON_BY_FACTION_ID
from eveicon import IconData
from fsdBuiltData.common.iconIDs import GetIconFile
from localization import GetByMessageID, GetByLabel, GetMessageIDForLabel
from uihighlighting import UiHighlightDirections
REGEX = re.compile('{.*}')
tokenReplacer = '{...}'

class PointerObject(object):

    def __init__(self, uiElementName, label, **kwargs):
        self.uiElementName = uiElementName
        self.label = label
        self.labelLower = label.lower()
        self.labelLong = kwargs.get('labelLong', None)
        self.texturePath = kwargs.get('texturePath', None)
        self.iconData = kwargs.get('iconData', None)
        self.iconSizes = kwargs.get('iconSizes', None)
        self.cmdName = kwargs.get('cmdName', None)
        self.offset = kwargs.get('offset', None)
        self.defaultDirection = kwargs.get('defaultDirection', None)
        self.pointerScope = kwargs.get('pointerScope', None)
        self.isMenuOption = kwargs.get('isMenuOption', False)

    def GetTexAndTexture(self):
        return TextAndTexture(self.label, self.texturePath, self.iconSizes, iconData=self.iconData)


def GetPointerObjectFromAuthoredPointer(pointerData):
    iconData = None
    texturePath = getattr(pointerData, 'texturePath', None)
    if not texturePath and pointerData.iconID:
        texturePath = GetIconFile(pointerData.iconID)
    if not texturePath and getattr(pointerData, 'iconDataName', None):
        iconName = pointerData.iconDataName.replace('eveicon.', '')
        iconData = eveicon.get(iconName)
    return PointerObject(pointerData.uiElementName, GetByMessageID(pointerData.title), texturePath=texturePath, offset=getattr(pointerData, 'offset', None), defaultDirection=getattr(pointerData, 'defaultDirection', None), pointerScope=getattr(pointerData, 'pointerScope', None), isMenuOption=getattr(pointerData, 'isMenuOption', None), iconData=iconData)


def GetPointerObjectFromActions(labelPath, action):
    if labelPath in POINTER_ACTIONS:
        return
    text = GetMessageLabelForAction(labelPath)
    if text is None:
        return
    labelLong = GetByLabel('UI/Help/PointerWndSelectedItemAction', actionName=text)
    iconData = actionConst.ICON_BY_ACTIONID.get(labelPath, None)
    if iconData:
        texturePath = None
    elif isinstance(action.iconPath, IconData):
        texturePath = None
        iconData = action.iconPath
    else:
        texturePath = action.iconPath
        iconData = None
    return PointerObject(action.uniqueUiName, label=text, texturePath=texturePath, iconData=iconData, labelLong=labelLong)


def GetPointerObjectForStationSvc(serviceInfo):
    serviceLabel = serviceInfo.label
    cmd = uicore.cmd.commandMap.GetCommandByName(serviceInfo.command)
    if cmd:
        serviceLabel = cmd.GetName()
    labelLong = GetByLabel('UI/Help/PointerWndStationServicesLongName', serviceName=serviceLabel)
    return PointerObject(pConst.GetUniqueStationServiceName(serviceInfo.name), label=serviceLabel, texturePath=serviceInfo.iconID, labelLong=labelLong)


def GetPointerObjectForAgencyTab(agencyContentGroup):
    uiElementName = pConst.GetUniqueAgencyTabName(agencyContentGroup.GetID())
    label = GetByLabel('UI/Help/AgencyTabName', tabName=agencyContentGroup.GetName())
    return PointerObject(uiElementName, label, texturePath='res:/UI/Texture/classes/HelpPointer/tabFlat.png')


def GetPointerObjectForAgencyCard(agencyContentGroup):
    uiElementName = pConst.GetUniqueAgencyCardName(agencyContentGroup.GetID())
    label = GetByLabel('UI/Help/AgencyCardName', cardName=agencyContentGroup.GetName())
    return PointerObject(uiElementName, label, texturePath='res:/UI/Texture/classes/HelpPointer/agencyCardFlat.png')


def GetPointerObjectForNeocom(btnID, btnData, label):
    texturePath = btnData.iconPath
    if not texturePath and btnData.wndCls:
        texturePath = btnData.wndCls.default_iconNum
    return PointerObject(pConst.GetUniqueNeocomPointerName(btnID), label, texturePath=texturePath, cmdName=btnData.cmdName)


def GetPointerObjectForSkillPlan(skillPlan):
    uiElementName = pConst.GetUniqueSkillPlanName(skillPlan.GetID().int)
    label = GetByLabel('UI/Help/SkillPlansName', skillPlanName=skillPlan.GetName())
    return PointerObject(uiElementName, label, texturePath='res:/UI/Texture/classes/HelpPointer/skillCardFlat.png')


def GetPointerObjectForSkillPlanFaction(skillPlan):
    if None in (skillPlan.careerPathID, skillPlan.factionID):
        return
    uiElementName = pConst.GetUniqueSkillPlanFactionName(skillPlan.careerPathID, skillPlan.factionID)
    careerPathName = GetByMessageID(get_career_path_name_id(skillPlan.careerPathID))
    factionName = factions.get_faction_name(skillPlan.factionID)
    factionIcon = ICON_BY_FACTION_ID.get(skillPlan.factionID, None)
    label = GetByLabel('UI/Help/SkillPlansFaction', careerPathName=careerPathName, factionName=factionName)
    return PointerObject(uiElementName, label, defaultDirection=UiHighlightDirections.UP, texturePath=factionIcon)


def GetPointerObjectForSkillPlanCareer(skillPlan):
    if skillPlan.careerPathID is None:
        return
    uiElementName = pConst.GetUniqueSkillPlanCareerName(skillPlan.careerPathID)
    careerPathName = GetByMessageID(get_career_path_name_id(skillPlan.careerPathID))
    careerIcon = careerConst.CAREERS_32_SIZES.get(skillPlan.careerPathID, None)
    label = GetByLabel('UI/Help/SkillPlansCareer', careerPathName=careerPathName)
    return PointerObject(uiElementName, label, defaultDirection=UiHighlightDirections.UP, texturePath=careerIcon)


def GetMessageLabelForAction(labelPath):
    try:
        messageID = GetMessageIDForLabel(labelPath)
    except KeyError:
        return None

    try:
        text = localization._GetRawByMessageID(messageID)
        return re.sub('{.*}', tokenReplacer, text)
    except KeyError:
        return None
