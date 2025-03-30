#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\surveys\survey.py
import datetimeutils
import gametime
from eveprefs import boot
import datetime
DEFAULT_REGION = 'ccp'

class Survey(object):

    def __init__(self, surveyID, fsdData):
        self.surveyID = surveyID
        self.fsdData = fsdData

    def __repr__(self):
        return 'Survey ID: %s, API class: %s' % (self.surveyID, self.GetAPIClassName())

    def GetSurveyID(self):
        return self.surveyID

    def GetRegion(self):
        return self.fsdData.region or DEFAULT_REGION

    def IsAllowedInCurrentRegion(self):
        return self.GetRegion() == boot.region

    def IsActive(self):
        return self.GetStartDate() <= self._GetToday() < self.GetEndDate()

    def IsExpired(self):
        return self.GetEndDate() <= self._GetToday()

    def IsWithinGracePeriod(self):
        endDate = self.GetEndDate()
        endDatePlusGracePeriod = endDate + datetime.timedelta(self.GetGracePeriodDays())
        return endDate <= self._GetToday() < endDatePlusGracePeriod

    def GetStartDate(self):
        return self._GetDateFromString(self.fsdData.startDate)

    def GetEndDate(self):
        endDate = self.fsdData.endDate
        if endDate:
            return self._GetDateFromString(endDate)

    def _GetToday(self):
        now = datetimeutils.filetime_to_datetime(gametime.GetWallclockTime())
        return now.date()

    def _GetDateFromString(self, dateString):
        if not dateString:
            return None
        day, month, year = dateString.split('/')
        return datetime.date(int(year), int(month), int(day))

    def GetItemRewards(self):
        return self.fsdData.itemRewards

    def GetVGSRewards(self):
        return self.fsdData.vgsRewards

    def GetBannerTexturePath(self):
        return self.fsdData.resPath

    def GetAPIClassName(self):
        return self.fsdData.apiClassName

    def GetInternalName(self):
        return self.fsdData.name

    def GetGracePeriodDays(self):
        return self.fsdData.gracePeriod

    def GetMinAccountAgeInHours(self):
        return self.fsdData.minAccountAgeHours

    def GetClaimLabelID(self):
        return self.fsdData.claimLabelID

    def GetSurveyURL(self):
        return self.fsdData.url
