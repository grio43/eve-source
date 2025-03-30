#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\surveys\client\__init__.py
import logging
import api
logger = logging.getLogger(__name__)

def GetSurveyClientAPI(survey):
    if not survey:
        return
    apiName = survey.GetAPIClassName()
    try:
        apiClass = getattr(api, apiName)
    except StandardError:
        logger.exception('GetSurveyClientAPI - Unable to find a client API called %s, maybe you forgot to import it?' % apiName)
    else:
        return apiClass()
