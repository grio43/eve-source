#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\surveys\client\api\twelveTraitsClientAPI.py
from surveys.client.api.baseSurveyClientAPI import BaseSurveyClientAPI

class TwelveTraitsClientAPI(BaseSurveyClientAPI):

    def FormatSurveyURL(self, unformattedURL):
        if not unformattedURL:
            raise ValueError('FormatSurveyURL - invalid URL format')
        return unformattedURL % session.userid
