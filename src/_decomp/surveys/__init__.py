#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\surveys\__init__.py
from fsdBuiltData.common.surveysFSDLoader import SurveyFSDLoader
from .survey import Survey
import logging
logger = logging.getLogger(__name__)

def GetActiveSurvey():
    activeSurveys = GetActiveSurveys()
    if activeSurveys:
        return activeSurveys[0]


def GetActiveSurveys():
    surveys = SurveyFSDLoader.GetData()
    activeSurveys = []
    for surveyID, surveyData in surveys.iteritems():
        surveyObject = Survey(surveyID, surveyData)
        if surveyObject.IsActive() and surveyObject.IsAllowedInCurrentRegion():
            activeSurveys.append(surveyObject)

    if not activeSurveys:
        logger.debug('Survey::GetActiveSurvey - No active survey found')
    return sorted(activeSurveys, key=lambda x: x.GetSurveyID())


def GetAllSurveys():
    surveys = SurveyFSDLoader.GetData()
    surveyObjects = []
    for surveyID, surveyData in surveys.iteritems():
        surveyObject = Survey(surveyID, surveyData)
        if surveyObject.IsAllowedInCurrentRegion():
            surveyObjects.append(surveyObject)

    if not surveyObjects:
        logger.debug('Survey::GetAllSurveys - No surveys.')
    return surveyObjects


def GetExpiredSurveysInGracePeriod():
    surveys = SurveyFSDLoader.GetData()
    expiredSurveys = []
    for surveyID, surveyData in surveys.iteritems():
        surveyObject = Survey(surveyID, surveyData)
        if not surveyObject.IsAllowedInCurrentRegion():
            continue
        if surveyObject.IsExpired() and surveyObject.IsWithinGracePeriod():
            expiredSurveys.append(surveyObject)

    if not expiredSurveys:
        logger.debug('Survey::GetExpiredSurveys - No expired survey found')
    return sorted(expiredSurveys, key=lambda x: x.GetSurveyID())


def GetSurveyByID(surveyID):
    surveys = SurveyFSDLoader.GetData()
    for sID, surveyData in surveys.iteritems():
        if sID == surveyID:
            return Survey(surveyID, surveyData)
