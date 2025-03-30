#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\neocom\neocomButtonClasses.py
from eve.client.script.ui.shared.neocom.neocom import neocomConst
from eve.client.script.ui.shared.neocom.neocom.buttonContextualOffer import ButtonContextualOffer
from eve.client.script.ui.shared.neocom.neocom.buttonEvent import ButtonEvent
from eve.client.script.ui.shared.neocom.neocom.buttons.buttonAirCareerProgram import ButtonAIRCareerProgram
from eve.client.script.ui.shared.neocom.neocom.buttons.buttonAura import ButtonAura
from eve.client.script.ui.shared.neocom.neocom.buttons.buttonChat import ButtonChat
from eve.client.script.ui.shared.neocom.neocom.buttons.buttonGroup import ButtonGroup
from eve.client.script.ui.shared.neocom.neocom.buttons.buttonInventory import ButtonInventory
from eve.client.script.ui.shared.neocom.neocom.buttons.buttonNotification import ButtonNotification
from eve.client.script.ui.shared.neocom.neocom.buttons.buttonRedeem import ButtonRedeem
from eve.client.script.ui.shared.neocom.neocom.buttons.buttonReward import ButtonReward
from eve.client.script.ui.shared.neocom.neocom.buttons.buttonWindow import ButtonWindow
from eve.client.script.ui.shared.neocom.neocom.buttons.buttonJobBoard import ButtonJobBoard
from neocom2 import btnIDs
import log
NEOCOM_BUTTON_CLASSES_BY_ID = {'InstructionsConversationWindow': ButtonAura,
 btnIDs.JOB_BOARD_ID: ButtonJobBoard}

def GetBtnClassByBtnType(btnData):
    if btnData.id in NEOCOM_BUTTON_CLASSES_BY_ID:
        return NEOCOM_BUTTON_CLASSES_BY_ID[btnData.id]
    if btnData.btnType == neocomConst.BTNTYPE_WINDOW and btnData.children:
        btnType = btnData.children[0].btnType
    else:
        btnType = btnData.btnType
    btnsByTypeID = {neocomConst.BTNTYPE_CMD: ButtonWindow,
     neocomConst.BTNTYPE_WINDOW: ButtonWindow,
     neocomConst.BTNTYPE_GROUP: ButtonGroup,
     neocomConst.BTNTYPE_CHAT: ButtonChat,
     neocomConst.BTNTYPE_INVENTORY: ButtonInventory,
     neocomConst.BTNTYPE_NOTIFICATION: ButtonNotification,
     neocomConst.BTNTYPE_OFFERS: ButtonContextualOffer,
     neocomConst.BTNTYPE_REDEEM: ButtonRedeem,
     neocomConst.BTNTYPE_REWARD: ButtonReward,
     neocomConst.BTNTYPE_EVENT: ButtonEvent,
     neocomConst.BTNTYPE_CAREER_PROGRAM: ButtonAIRCareerProgram}
    if btnType not in btnsByTypeID:
        log.LogError('No neocom button Class defined for button type')
    return btnsByTypeID[btnType]
