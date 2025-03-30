#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\station\agents\agentConst.py
from carbonui.util.color import Color
from eve.common.lib import appConst
from localization import GetByLabel
MISSIONSTATELABELS = {appConst.agentMissionStateAllocated: GetByLabel('UI/Journal/JournalWindow/Agents/StateOffered'),
 appConst.agentMissionStateOffered: GetByLabel('UI/Journal/JournalWindow/Agents/StateOffered'),
 appConst.agentMissionStateAccepted: GetByLabel('UI/Journal/JournalWindow/Agents/StateAccepted'),
 appConst.agentMissionStateFailed: GetByLabel('UI/Journal/JournalWindow/Agents/StateFailed')}
COLOR_ACCEPTED = Color.HextoRGBA('#6f9e39')
COLOR_ACCEPTED_LAST = Color.HextoRGBA('#75b8bb')
COLOR_OFFERED = Color.HextoRGBA('#e19722')
COLOR_EXPIRED = (0.922, 0.216, 0.0, 1.0)
COLOR_ACTIVE = Color.HextoRGBA('#1d779e')
COLOR_UNAVAILABLE = Color.GRAY5
LABEL_BY_BUTTON_TYPE = {appConst.agentDialogueButtonViewMission: 'UI/Agents/Dialogue/Buttons/ViewMission',
 appConst.agentDialogueButtonRequestMission: 'UI/Agents/Dialogue/Buttons/RequestMission',
 appConst.agentDialogueButtonAccept: 'UI/Agents/Dialogue/Buttons/AcceptMission',
 appConst.agentDialogueButtonAcceptChoice: 'UI/Agents/Dialogue/Buttons/AcceptThisChoice',
 appConst.agentDialogueButtonAcceptRemotely: 'UI/Agents/Dialogue/Buttons/AcceptRemotely',
 appConst.agentDialogueButtonComplete: 'UI/Agents/Dialogue/Buttons/CompleteMission',
 appConst.agentDialogueButtonCompleteRemotely: 'UI/Agents/Dialogue/Buttons/CompleteRemotely',
 appConst.agentDialogueButtonContinue: 'UI/Agents/Dialogue/Buttons/Continue',
 appConst.agentDialogueButtonDecline: 'UI/Agents/Dialogue/Buttons/DeclineMission',
 appConst.agentDialogueButtonDefer: 'UI/Agents/Dialogue/Buttons/DeferMission',
 appConst.agentDialogueButtonQuit: 'UI/Agents/Dialogue/Buttons/QuitMission',
 appConst.agentDialogueButtonStartResearch: 'UI/Agents/Dialogue/Buttons/StartResearch',
 appConst.agentDialogueButtonCancelResearch: 'UI/Agents/Dialogue/Buttons/CancelResearch',
 appConst.agentDialogueButtonBuyDatacores: 'UI/Agents/Dialogue/Buttons/BuyDatacores',
 appConst.agentDialogueButtonLocateCharacter: 'UI/Agents/Dialogue/Buttons/LocateCharacter',
 appConst.agentDialogueButtonLocateAccept: 'UI/Agents/Dialogue/Buttons/LocateCharacterAccept',
 appConst.agentDialogueButtonLocateReject: 'UI/Agents/Dialogue/Buttons/LocateCharacterReject',
 appConst.agentDialogueButtonYes: 'UI/Common/Buttons/Yes',
 appConst.agentDialogueButtonNo: 'UI/Common/Buttons/No'}
