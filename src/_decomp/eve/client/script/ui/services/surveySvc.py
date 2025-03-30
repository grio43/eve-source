#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\surveySvc.py
import blue
from carbon.common.script.sys.service import Service
from carbonui.uicore import uicore
from eve.client.script.ui.login.charSelection.surveyClaimWnd import ClaimSurveyRewardsWnd
from surveys import GetActiveSurvey, GetExpiredSurveysInGracePeriod
from surveys.client import GetSurveyClientAPI
from uthread2 import BufferedCall
TEST_SURVEY_ID = 1

class SurveySvc(Service):
    __guid__ = 'svc.survey'
    __servicename__ = 'survey'
    __displayname__ = 'Survey Service'
    __notifyevents__ = ['OnSurveyRewardsAvailable']

    def Run(self, memStream = None):
        super(SurveySvc, self).Run(memStream)
        self.surveysToRewardFor = set()

    def OnSurveyRewardsAvailable(self, surveyID):
        self.surveysToRewardFor.add(surveyID)
        self.ShowClaimWnd()

    @BufferedCall(2000)
    def ShowClaimWnd(self):
        surveyIDs = self.surveysToRewardFor.copy()
        if not surveyIDs:
            return
        wnd = ClaimSurveyRewardsWnd.GetIfOpen()
        if wnd:
            wnd.Close()
        wnd = ClaimSurveyRewardsWnd.Open(surveyIDs=surveyIDs)
        wnd.ShowModal()
        self.ClaimSurveyRewards()
        self.surveysToRewardFor.clear()

    def ClaimSurveyRewards(self):
        sm.RemoteSvc('survey').ClaimSurveyRewards()

    def AccessSurvey(self):
        surveyURL = uicore.cmd.GetURLWithParameters(url=self.GetSurveyURL(), origin='Survey')
        blue.os.ShellExecute(surveyURL)

    def GetSurveyURL(self):
        if not session.userid:
            return
        survey = GetActiveSurvey()
        if not survey:
            return
        clientAPI = GetSurveyClientAPI(survey)
        if not clientAPI:
            return
        url = survey.GetSurveyURL()
        return clientAPI.FormatSurveyURL(url)

    def GetActiveSurveyID(self):
        if not session.userid:
            return
        survey = GetActiveSurvey()
        if not survey:
            return
        return self._GetActiveSurveyIDFromServer()

    def PerformSurveyChecks(self):
        if not GetActiveSurvey() and not GetExpiredSurveysInGracePeriod():
            return
        sm.RemoteSvc('survey').PerformSurveyChecks()

    def _GetActiveSurveyIDFromServer(self):
        if not GetActiveSurvey():
            return
        try:
            return sm.RemoteSvc('survey').GetActiveSurveyID()
        except StandardError:
            self.LogException()
