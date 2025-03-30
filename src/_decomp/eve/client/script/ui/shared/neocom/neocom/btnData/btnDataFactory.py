#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\neocom\btnData\btnDataFactory.py
import localization
import log
from carbonui.uicore import uicore
from eve.client.script.ui.shared.careerPortal.neocom import BtnDataNodeAirCareerProgram
from eve.client.script.ui.shared.inventory.neocomInventoryBadging import UnseenInventoryItemsBtnData
from eve.client.script.ui.shared.neocom.neocom import neocomConst
from eve.client.script.ui.shared.neocom.neocom.btnData.btnDataCorporation import BtnDataNodeCorporation
from eve.client.script.ui.shared.neocom.neocom.btnData.btnDataNode import BtnDataNode
from eve.client.script.ui.shared.neocom.neocom.btnData.btnDataNodeAgency import BtnDataNodeAgency
from eve.client.script.ui.shared.neocom.neocom.btnData.btnDataNodeChat import BtnDataNodeChat
from eve.client.script.ui.shared.neocom.neocom.btnData.btnDataNodeGroup import BtnDataNodeGroup
from eve.client.script.ui.shared.neocom.neocom.btnData.btnDataJobBoard import BtnDataNodeJobBoard
from eve.client.script.ui.shared.neocom.neocom.btnData.btnDataNodeShipTree import BtnDataNodeShipTree
from eve.client.script.ui.shared.neocom.neocom.btnData.btnDataRaw import BTNDATARAW_BY_ID
from eve.client.script.ui.shared.neocom.neocom.neocomUtil import ConvertOldTypeOfRawData
from neocom2 import btnIDs
from uihider import get_ui_hider
NODECLASS_BY_TYPE = {neocomConst.BTNTYPE_CHAT: BtnDataNodeChat,
 neocomConst.BTNTYPE_GROUP: BtnDataNodeGroup,
 neocomConst.BTNTYPE_INVENTORY: UnseenInventoryItemsBtnData,
 neocomConst.BTNTYPE_CAREER_PROGRAM: BtnDataNodeAirCareerProgram}
NODECLASS_BY_ID = {'agency': BtnDataNodeAgency,
 'inventory': UnseenInventoryItemsBtnData,
 btnIDs.AIR_CAREER_PROGRAM_ID: BtnDataNodeAirCareerProgram,
 btnIDs.CORP_ID: BtnDataNodeCorporation,
 btnIDs.JOB_BOARD_ID: BtnDataNodeJobBoard,
 btnIDs.SHIP_TREE_ID: BtnDataNodeShipTree}

def GetClass(btnID, btnType):
    if btnID in NODECLASS_BY_ID:
        nodeClass = NODECLASS_BY_ID[btnID]
    elif btnType in NODECLASS_BY_TYPE:
        nodeClass = NODECLASS_BY_TYPE[btnType]
    else:
        nodeClass = BtnDataNode
    return nodeClass


def ConstructButtonDataFromRawData(parent, rawDataList, isRemovable):
    for rawData in rawDataList:
        rawData = ConvertOldTypeOfRawData(rawData)
        btnDataRaw = BTNDATARAW_BY_ID.get(rawData.id)
        cmdName = wndCls = iconPath = None
        if btnDataRaw:
            label = None
            if btnDataRaw.cmdName:
                cmd = uicore.cmd.commandMap.GetCommandByName(btnDataRaw.cmdName)
                if cmd:
                    label = cmd.GetName()
            if label is None:
                if rawData.Get('label', None):
                    label = rawData.label
                elif btnDataRaw.label is None:
                    log.LogError('Neocom button {} is missing a label'.format(rawData.id))
                else:
                    label = localization.GetByLabel(btnDataRaw.label)
            iconPath = btnDataRaw.iconPath
            cmdName = btnDataRaw.cmdName
            wndCls = btnDataRaw.wndCls
        elif rawData.btnType == neocomConst.BTNTYPE_GROUP:
            label = rawData.label
            iconPath = neocomConst.ICONPATH_GROUP
        elif rawData.btnType == neocomConst.BTNTYPE_SPACER:
            label = ''
        else:
            continue
        if wndCls and get_ui_hider().is_ui_element_hidden(wndCls.default_windowID):
            continue
        labelAbbrev = rawData.Get('labelAbbrev', None)
        btnData = ConstructBtnData(parent, rawData.id, rawData.btnType, label, iconPath, isRemovable=isRemovable, labelAbbrev=labelAbbrev, cmdName=cmdName, wndCls=wndCls)
        if rawData.children:
            ConstructButtonDataFromRawData(btnData, rawData.children, isRemovable)


def ConstructBtnData(parent, btnID, btnType, label, iconPath, isRemovable = True, **kwargs):
    nodeClass = GetClass(btnID, btnType)
    btnData = nodeClass(parent=parent, btnID=btnID, btnType=btnType, label=label, iconPath=iconPath, isRemovable=isRemovable, **kwargs)
    return btnData
