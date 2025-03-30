#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\activities\activity.py
import time
import localization
from eve.client.script.ui.shared.activities.activitiesUIConst import SHOW_LEFT_TIME_TEXT_SECONDS, ONE_DAY, ONE_HOUR, LABEL_LEFT_DAYS, LABEL_LEFT_HOURS, LABEL_LESS_HOURS
from eve.client.script.ui.shared.activities.bannerEvent import DoAction
from localization import GetByMessageID
import logging
logger = logging.getLogger(__file__)

class ReleasedActivity(object):
    datetime_format = '%Y-%m-%d %H:%M'

    def __init__(self, activityID, fsdData):
        self.activityID = activityID
        self.fsdData = fsdData
        self.isForceShown = False
        self.isUnseen = True

    def SetSeen(self):
        self.isUnseen = False

    def IsUnseen(self):
        return self.isUnseen

    def GetID(self):
        return self.activityID

    def GetName(self):
        return GetByMessageID(self.fsdData.nameID)

    def GetIntroduce(self):
        return GetByMessageID(self.fsdData.introduceID)

    def GetInfo(self):
        if self.fsdData.infoID:
            return GetByMessageID(self.fsdData.infoID)

    def GetTexturePath(self):
        return self.fsdData.bannerPath

    def GetIconPath(self):
        return self.fsdData.iconPath

    def GetStartDatetime(self):
        return self.fsdData.startDatetime

    def GetEndDatetime(self):
        return self.fsdData.endDatetime

    def GetIntegerParameter(self):
        return self.fsdData.integerParameter

    def GetUrl(self):
        return self.fsdData.url

    def GetIntegerListParameter(self):
        return self.fsdData.integerListParameter

    def GetRemainingSeconds(self):
        endTime = time.mktime(time.strptime(self.GetEndDatetime(), self.datetime_format))
        nowTime = time.time()
        return int(endTime - nowTime)

    def _CalcDays(self, leftTime):
        days = localization.formatters.FormatNumeric(leftTime // ONE_DAY)
        return localization.GetByLabel(LABEL_LEFT_DAYS, days=days)

    def _CalcHours(self, leftTime):
        hours = localization.formatters.FormatNumeric(leftTime // ONE_HOUR)
        return localization.GetByLabel(LABEL_LEFT_HOURS, hours=hours)

    def _CalcLess(self, _):
        hours = localization.formatters.FormatNumeric(1)
        return localization.GetByLabel(LABEL_LESS_HOURS, hours=hours)

    def _GetShowedText(self, leftTime):
        if leftTime >= ONE_DAY:
            text = self._CalcDays(leftTime)
        elif leftTime >= ONE_HOUR:
            text = self._CalcHours(leftTime)
        else:
            text = self._CalcLess(leftTime)
        return text

    def IsCountdownVisible(self):
        leftTime = self.GetRemainingSeconds()
        return leftTime <= SHOW_LEFT_TIME_TEXT_SECONDS

    def GetTimeLeftText(self):
        leftTime = self.GetRemainingSeconds()
        return self.IsCountdownVisible() and self._GetShowedText(leftTime) or None

    def IsVideo(self):
        bannerPath = self.GetTexturePath()
        if bannerPath.find('.') < 0:
            return False
        return bannerPath.split('.')[-1].lower() == 'webm'

    def IsShown(self):
        startTime = time.mktime(time.strptime(self.GetStartDatetime(), self.datetime_format))
        endTime = time.mktime(time.strptime(self.GetEndDatetime(), self.datetime_format))
        nowTime = time.time()
        return startTime <= nowTime <= endTime

    def GetEvent(self):
        return self.fsdData.bannerEvent

    def ExecuteCallToAction(self):
        return DoAction(self)
