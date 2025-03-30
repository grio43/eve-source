#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\station\agents\agentDialogueWindow.py
import logging
import blue
import telemetry
import carbonui.const as uiconst
import localization
from carbon.common.script.util.format import FmtTimeInterval
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from eve.client.script.ui.control import eveEdit
from carbonui.button.group import ButtonGroup
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.eveColor import SUCCESS_GREEN_HEX
from eve.client.script.ui.station.agents import agentDialogueUtil
from eve.client.script.ui.station.agents.agentConst import LABEL_BY_BUTTON_TYPE
from eve.client.script.ui.station.agents.agentDialogueUtil import GetAgentNameAndLevel
from eve.common.lib import appConst
from gametime import MIN
from random import choice
from jobboard.client import get_agent_mission_job
from jobboard.client.ui.track_button import TrackJobButton
from localization import GetByLabel
SINGLE_PANE_VIEW = 'SinglePaneView'
DOUBLE_PANE_VIEW = 'DoublePaneView'
MIN_HEIGHT = 545
MIN_WIDTH = 835
logger = logging.getLogger(__name__)

class AgentDialogueWindow(Window):
    __guid__ = 'form.AgentDialogueWindow'
    __notifyevents__ = ['OnSessionChanged', 'OnAgentMissionChange']
    default_width = 900
    default_height = 650
    default_minSize = (MIN_WIDTH, MIN_HEIGHT)
    default_windowID = 'AgentDialogueWindow'
    default_iconNum = 'res:/ui/Texture/WindowIcons/agent.png'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.isLoading = False
        self.objectiveHtml = None
        self.briefingHtml = None
        self.viewMode = None
        self.leftPane = None
        self.rightPane = None
        self.agentID = None
        self.agentDivisionID = None
        self.SetAgentID(attributes.agentID)
        self.buttonGroup = ButtonGroup(parent=self.content, align=uiconst.TOBOTTOM)
        self.mainCont = Container(name='mainCont', parent=self.content, padBottom=16)
        self.loadingWheel = LoadingWheel(parent=self, align=uiconst.CENTER, state=uiconst.UI_HIDDEN, idx=0)

    def ConstructBrowsers(self):
        self.briefingBrowser = eveEdit.Edit(name='briefing_browser', parent=self.leftPane, readonly=1)
        self.briefingBrowser.sr.window = self
        self.objectiveBrowser = eveEdit.Edit(name='objective_browser', parent=self.rightPane, readonly=1)
        self.objectiveBrowser.sr.window = self

    def SetAgentID(self, agentID):
        if agentID is not None:
            agentInfo = sm.GetService('agents').GetAgentByID(agentID)
            agentNameAndLevel = GetAgentNameAndLevel(agentID, agentInfo.level)
            self.SetCaption(localization.GetByLabel('UI/Agents/Dialogue/AgentConversationWith', agentNameAndLevel=agentNameAndLevel))
            self.agentDivisionID = agentInfo.divisionID
        self.agentID = agentID

    def GetAgentID(self):
        return self.agentID

    def GetAgentMoniker(self):
        return sm.GetService('agents').GetAgentMoniker(self.GetAgentID())

    def OnSessionChanged(self, isRemote, sess, change):
        if not self.destroyed:
            self.briefingBrowser.SessionChanged()
            self.objectiveBrowser.SessionChanged()
        if 'stationid' in change:
            self.InteractWithAgent()

    def OnAgentMissionChange(self, action, agentID):
        if not self.destroyed:
            if action == appConst.agentMissionModified and self.agentID == agentID:
                self.InteractWithAgent()

    def DisableButtons(self):
        for button in self.buttonGroup.buttons:
            button.Disable()

    def SetBriefingHTML(self, html):
        self.briefingHtml = html

    def SetObjectiveHTML(self, html):
        self.objectiveHtml = html

    def LoadBriefingBrowserHTML(self, html, hideBackground = 0, newThread = 1):
        if self.destroyed:
            return
        if not self.viewMode:
            self.SetSinglePaneView()
        if not self.briefingBrowser:
            return
        self.ShowLoad()
        self.briefingHtml = html
        self.briefingBrowser.sr.hideBackground = hideBackground
        while self.briefingBrowser.IsLoading():
            blue.pyos.synchro.Yield()

        self.briefingBrowser.LoadHTML(html, newThread=newThread)

    def LoadObjectiveBrowserHTML(self, html, hideBackground = 0, newThread = 1):
        if self.destroyed:
            return
        if not self.viewMode:
            self.SetDoublePaneView()
        if not self.objectiveBrowser:
            return
        self.ShowLoad()
        self.objectiveHtml = html
        self.objectiveBrowser.sr.hideBackground = hideBackground
        while self.objectiveBrowser.IsLoading():
            blue.pyos.synchro.Yield()

        self.objectiveBrowser.LoadHTML(html, newThread=newThread)

    @telemetry.ZONE_METHOD
    def SetSinglePaneView(self, briefingHtml = None):
        if self.viewMode != SINGLE_PANE_VIEW:
            self._ReconstructSinglePane()
        if briefingHtml:
            self.SetBriefingHTML(briefingHtml)
            self.LoadBriefingBrowserHTML(self.briefingHtml)

    def _ReconstructSinglePane(self):
        self.viewMode = SINGLE_PANE_VIEW
        self.LockWidth(MIN_WIDTH / 2)
        self.mainCont.Flush()
        self.leftPane = Container(name='leftPane', parent=self.mainCont, align=uiconst.TOALL)
        self.ConstructBrowsers()

    @telemetry.ZONE_METHOD
    def SetDoublePaneView(self, briefingHtml = None, objectiveHtml = None):
        if self.viewMode != DOUBLE_PANE_VIEW:
            self._ReconstructDoublePane()
        if briefingHtml:
            self.SetBriefingHTML(briefingHtml)
            self.LoadBriefingBrowserHTML(briefingHtml)
        if objectiveHtml:
            self.SetObjectiveHTML(objectiveHtml)
            self.LoadObjectiveBrowserHTML(objectiveHtml)

    def _ReconstructDoublePane(self):
        self.viewMode = DOUBLE_PANE_VIEW
        self.SetFixedWidth(None)
        self.SetMinSize((MIN_WIDTH, MIN_HEIGHT))
        self.mainCont.Flush()
        self.leftPane = Container(name='leftPane', parent=self.mainCont, align=uiconst.TOLEFT_PROP, width=0.5, padRight=8)
        self.rightPane = Container(name='rightPane', parent=self.mainCont, align=uiconst.TOALL, padLeft=8)
        self.ConstructBrowsers()

    def RefreshBrowsers(self):
        self.briefingBrowser.UpdatePosition(fromWhere='AgentDialogueWindow.RefreshBrowsers')
        self.objectiveBrowser.UpdatePosition(fromWhere='AgentDialogueWindow.RefreshBrowsers')

    @telemetry.ZONE_METHOD
    def InteractWithAgent(self, actionID = None):
        if self.isLoading:
            return
        self.isLoading = True
        try:
            self._StartLoading(actionID)
            agentSaysText, actions, lastActionInfo = self._GetConversation(actionID)
            if self.destroyed or agentSaysText is None:
                return
            self.ReconstructLayout(actions, agentSaysText, lastActionInfo)
        finally:
            self._StopLoading()

    def _StartLoading(self, actionID):
        if actionID:
            self.DisableButtons()
        self.loadingWheel.Show()

    def _StopLoading(self):
        self.isLoading = False
        self.loadingWheel.Hide()

    def ReconstructLayout(self, actions, agentSaysText, lastActionInfo):
        actions = actions or []
        briefingHTML = self.GetBriefingHTML(actions, agentSaysText, lastActionInfo)
        objectiveHtml = self.GetObjectiveHTML(lastActionInfo)
        if objectiveHtml or lastActionInfo.get('missionCompleted'):
            self.SetDoublePaneView(briefingHtml=briefingHTML, objectiveHtml=objectiveHtml)
        else:
            self.SetSinglePaneView(briefingHtml=briefingHTML)
        self.ReconstructButtons(actions, lastActionInfo)

    def GetObjectiveHTML(self, lastActionInfo):
        objectiveData = self.GetAgentMoniker().GetMissionObjectiveInfo()
        if objectiveData and not (lastActionInfo['missionCompleted'] or lastActionInfo['missionDeclined'] or lastActionInfo['missionQuit'] or lastActionInfo['missionCantReplay']):
            return self._GetObjectiveHTML(objectiveData)
        else:
            return None

    def _GetObjectiveHTML(self, objectiveData):
        return '\n                <html>\n                <head>\n                    <link rel="stylesheet" type="text/css" href="res:/ui/css/missionobjectives.css">\n                </head>\n                <body>\n                %s\n                </body>\n                </html>\n            ' % agentDialogueUtil.GetMissionObjectiveHTML(self.GetAgentID(), objectiveData)

    def GetBriefingHTML(self, actions, agentSaysText, lastActionInfo):
        agentHeader = self.GetAgentHeader(lastActionInfo)
        briefingData = sm.GetService('agents').GetMissionBriefingInfo(self.GetAgentID())
        missionTitle = self._GetMissionTitleHTML(briefingData) if briefingData else ''
        replayTimer = ''
        timeLeft = lastActionInfo.get('missionCantReplay', None)
        if timeLeft:
            agentSaysText = self._GetNoMissionMessage(timeLeft)
            replayTimer = localization.GetByLabel('UI/Agents/DefaultMessages/MissionCantReplay', timeLeft=FmtTimeInterval(timeLeft, breakAt='min' if timeLeft > MIN else 'sec'), timerColor=SUCCESS_GREEN_HEX)
            replayTimer = '<br>' + replayTimer
            replayTimer = replayTimer.replace('<color=', '<font color=')
            replayTimer = replayTimer.replace('</color>', '</font>')
            extraMissionInfoHTML = None
        else:
            specialInteractionActions = [ (actionID, actionData) for actionID, actionData in actions if type(actionData) == dict ]
            extraMissionInfoHTML = self.GetExtraMissionInfoHTML(specialInteractionActions, briefingData)
        adminHTML = self.GetAdminHTML(actions)
        return self._GetBriefingHTML(agentHeader, missionTitle, agentSaysText, replayTimer, extraMissionInfoHTML, adminHTML)

    def _GetNoMissionMessage(self, timeLeft):
        if self.agentDivisionID and self.agentDivisionID == appConst.corpDivisionHeraldry:
            if timeLeft:
                label = 'UI/Agents/DefaultMessages/NoMissionHeraldryTimer'
            else:
                label = 'UI/Agents/DefaultMessages/NoMissionHeraldry'
        else:
            label = choice(['UI/Agents/DefaultMessages/NoMission1', 'UI/Agents/DefaultMessages/NoMission2'])
        return localization.GetByLabel(label)

    def _GetBriefingHTML(self, agentHeader, missionTitle, agentSaysText, replayTimer, extraMissionInfoHTML, adminHTML):
        body = ''
        for item in [agentHeader,
         missionTitle,
         agentSaysText,
         replayTimer,
         extraMissionInfoHTML,
         adminHTML]:
            if item:
                if body:
                    body += '<br>'
                body += unicode(item)

        return '\n                <html>\n                <head>\n                    <link rel="stylesheet" type="text/css" href="res:/ui/css/agentconvo.css">\n                </head>\n                    <body background-color=#00000000 link=#ffa800>\n                        %s\n                    </body>\n                </html>\n            ' % body

    def GetAgentHeader(self, lastActionInfo):
        lp = lastActionInfo.get('loyaltyPoints', 0)
        agentLocationWrap = self.GetAgentMoniker().GetAgentLocationWrap()
        agent = sm.GetService('agents').GetAgentByID(self.GetAgentID())
        agentHeader = agentDialogueUtil.GetAgentLocationHeader(agent, agentLocationWrap, lp)
        return agentHeader

    def GetExtraMissionInfoHTML(self, specialInteractionActions, briefingInformation):
        extraMissionInfo = ''
        if specialInteractionActions:
            extraMissionInfo += self.GetSpecialInteractionHTML(specialInteractionActions)
        elif briefingInformation:
            extraMissionInfo += self.GetMissionTimeHTML(briefingInformation)
            extraMissionInfo += '<br><center>%s</center>' % briefingInformation[appConst.agentMissionBriefingImage]
        return extraMissionInfo

    def GetMissionTimeHTML(self, briefingInformation):
        missionTimeText = self.GetMissionTimeText(briefingInformation)
        if missionTimeText:
            return '<br>%s' % missionTimeText
        else:
            return ''

    def GetSpecialInteractionHTML(self, specialInteractionActions):
        specialInteractionHTML = ''
        for actionID, briefingData in specialInteractionActions:
            sm.GetService('agents').PrimeMessageArguments(self.GetAgentID(), briefingData[appConst.agentMissionBriefingMissionID], briefingData[appConst.agentMissionBriefingKeywords])
            message = (briefingData[appConst.agentMissionBriefingTitleID], briefingData[appConst.agentMissionBriefingMissionID])
            missionTitle = self.GetMessageText(message)
            specialInteractionHTML += '\n                    <span id=subheader><a href="localsvc:method=AgentDoAction&agentID=%d&actionID=%d">%s</a> &gt;&gt;</span><br>\n                ' % (self.GetAgentID(), actionID, missionTitle)
            if briefingData[appConst.agentMissionBriefingBriefingID] is not None:
                if isinstance(briefingData[appConst.agentMissionBriefingBriefingID], basestring) or briefingData[appConst.agentMissionBriefingBriefingID] > 0:
                    message = (briefingData[appConst.agentMissionBriefingBriefingID], briefingData[appConst.agentMissionBriefingMissionID])
                    briefingText = self.GetMessageText(message)
                else:
                    briefingText = localization.GetByLabel('UI/Agents/Dialogue/StandardMission/CorruptBriefing')
                specialInteractionHTML += '\n                        <div id=basetext>%s</div>\n                        <br>\n                    ' % briefingText

        return specialInteractionHTML

    def _GetMissionTitleHTML(self, briefingData):
        message = (briefingData[appConst.agentMissionBriefingTitleID], briefingData[appConst.agentMissionBriefingMissionID])
        missionTitle = self.GetMessageText(message)
        return '<br><span id=subheader>%s</span><br>' % missionTitle

    def GetMessageText(self, message):
        return sm.GetService('agents').ProcessMessage(message, self.GetAgentID())

    def GetMissionTimeText(self, briefingInformation):
        if briefingInformation[appConst.agentMissionBriefingDeclineTime] is not None:
            if briefingInformation[appConst.agentMissionBriefingDeclineTime] == -1:
                return localization.GetByLabel('UI/Agents/StandardMission/DeclineMessageGeneric')
            else:
                timeRemaining = briefingInformation[appConst.agentMissionBriefingDeclineTime]
                timeBreakAt = 'min' if timeRemaining > appConst.MIN else 'sec'
                return localization.GetByLabel('UI/Agents/StandardMission/DeclineMessageTimeLeft', timeRemaining=FmtTimeInterval(timeRemaining, breakAt=timeBreakAt))
        elif briefingInformation[appConst.agentMissionBriefingExpirationTime] is not None:
            return localization.GetByLabel('UI/Agents/Dialogue/ThisMissionExpiresAt', expireTime=briefingInformation[appConst.agentMissionBriefingExpirationTime])

    def ReconstructButtons(self, actions, lastActionInfo):
        self.buttonGroup.FlushButtons()
        cantReplay = lastActionInfo.get('missionCantReplay', None)
        if not cantReplay:
            for actionID, actionData in actions:
                if type(actionData) is int:
                    label, func, kwargs = self._GetActionButtonData(actionData, actionID)
                    self.buttonGroup.AddButton(label, func, **kwargs)

        appendCloseButton = not self.buttonGroup.buttons or any((self._IsCloseButtonAction(actionData) for actionID, actionData in actions))
        if appendCloseButton and len(self.buttonGroup.buttons) < 3:
            self.buttonGroup.AddButton(localization.GetByLabel('UI/Common/Buttons/Close'), self.CloseByUser, uiName='CloseAgentConversation_Button')
        job = get_agent_mission_job(self.agentID, wait=False)
        if job:
            TrackJobButton(parent=self.buttonGroup, job=job)
        self.buttonGroup.state = uiconst.UI_PICKCHILDREN

    def GetAdminHTML(self, actions):
        adminHTML = ''
        adminOptions = self._GetAdminOptions(actions)
        if adminOptions:
            if len(adminOptions) == 1:
                adminHTML = '<br>'
                adminHTML += adminOptions[0]
            else:
                adminHTML = '<ol>'
                adminHTML += ''.join([ '<br><li>%s</li>' % x for x in adminOptions ])
                adminHTML += '</ol>'
        return adminHTML

    def _GetAdminOptions(self, actions):
        adminOptions = []
        for actionID, actionData in actions:
            if type(actionData) in (str, unicode):
                adminOptions.append('<a href="localsvc:method=AgentDoAction&agentID=%d&actionID=%d">%s</a>' % (self.GetAgentID(), actionID, actionData))

        return adminOptions

    def _GetActionButtonData(self, actionData, actionID):
        labelPath = LABEL_BY_BUTTON_TYPE.get(actionData, None)
        if labelPath:
            label = localization.GetByLabel(labelPath)
        else:
            logger.error('Unknown button ID for agent action, id =', actionData)
            label = 'Unknown ID ' + str(actionData)
        btnData = (label, sm.GetService('agents').DoAction, {'args': (self.GetAgentID(), actionID),
          'uiName': u'{}_Button'.format(labelPath.split('/')[-1])})
        return btnData

    def _IsCloseButtonAction(self, actionData):
        return actionData in (appConst.agentDialogueButtonRequestMission,
         appConst.agentDialogueButtonContinue,
         appConst.agentDialogueButtonQuit,
         appConst.agentDialogueButtonCancelResearch)

    def _GetConversation(self, actionID):
        (agentSaysMsg, availableActions), lastActionInfo = self.ExecuteAgentAction(actionID)
        if actionID is None and len(availableActions):
            firstAction = availableActions[0]
            firstActionID, firstActionMsg = firstAction
            if firstActionMsg in (appConst.agentDialogueButtonRequestMission, appConst.agentDialogueButtonViewMission) and (len(availableActions) == 1 or not self._IsLocatorAgent(availableActions) and not self._IsResearchAgent()):
                (agentSaysMsg, availableActions), lastActionInfo = self.ExecuteAgentAction(firstActionID)
        agentSaysText = self.GetMessageText(agentSaysMsg)
        return (agentSaysText, availableActions, lastActionInfo)

    def _IsResearchAgent(self):
        isResearchAgent = False
        if sm.GetService('agents').GetAgentByID(self.GetAgentID()).agentTypeID == appConst.agentTypeResearchAgent:
            isResearchAgent = True
        return isResearchAgent

    def _IsLocatorAgent(self, availableActions):
        agentHasLocatorService = False
        for id, dlg in availableActions:
            if dlg == appConst.agentDialogueButtonLocateCharacter:
                agentHasLocatorService = True

        return agentHasLocatorService

    def ExecuteAgentAction(self, actionID):
        return self.GetAgentMoniker().DoAction(actionID)

    def ShowMissionObjectives(self, contentID):
        objectiveData = self.GetAgentMoniker().GetMissionObjectiveInfo(session.charid, contentID)
        if not self.destroyed:
            if objectiveData:
                objectiveHtml = self._GetObjectiveHTML(objectiveData)
                self.SetDoublePaneView(objectiveHtml=objectiveHtml)
            else:
                self.SetSinglePaneView()
