#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\newFeatures\feature.py
import datetime
import logging
from gametime import downtime
from localization import GetByMessageID, GetByLabel
from eveprefs import boot
from newFeatures import callToActionCommands
from newFeatures.newFeatureConst import ISNEW_DAYS_THRESHOLD, SETTING_ID
logger = logging.getLogger(__file__)

class ReleasedFeature(object):

    def __init__(self, featureID, fsdData):
        self.featureID = featureID
        self.fsdData = fsdData
        self.isForceShown = False

    def _GetDateFromString(self, dateString):
        if not dateString:
            return None
        year, month, day = dateString.split('-')
        return datetime.date(int(year), int(month), int(day))

    def GetID(self):
        return self.featureID

    def GetName(self):
        return GetByMessageID(self.fsdData.nameID)

    def GetDescription(self):
        return GetByMessageID(self.fsdData.descriptionID)

    def GetBulletPoints(self):
        return [ GetByMessageID(bulletPointID) for bulletPointID in self.fsdData.bulletPoints or [] ]

    def GetTexturePath(self):
        return self.fsdData.bannerPath

    def GetAgencyTexturePath(self):
        return self.fsdData.agencyTexturePath

    def IsVideo(self):
        return self.GetTexturePath().split('.')[-1].lower() == 'webm'

    def GetIconTexturePath(self):
        return self.fsdData.iconPath

    def GetNeocomBtnID(self):
        return self.fsdData.neocomBtnID

    def GetCallToActionMethod(self):
        return self.fsdData.callToActionMethod

    def GetCallToActionLabel(self):
        if not self.GetCallToActionMethod():
            return None
        return self.fsdData.callToActionLabel or 'UI/Common/Open'

    def CallToActionOpensInAgency(self):
        callToActionMethod = self.fsdData.callToActionMethod
        if callToActionMethod is None:
            return False
        if callToActionMethod.startswith('Agency'):
            return True
        return False

    def GetDaysSinceRelease(self):
        return (self._GetToday() - self.GetReleaseDate()).days

    def ExecuteCallToAction(self, *argss):
        methodName = self.GetCallToActionMethod()
        if not methodName:
            return
        method = getattr(callToActionCommands, methodName, None)
        if method is not None:
            method()
        else:
            logger.warning('Method could not be executed, since it was not callable.  methodName: %s' % methodName)

    def GetReleaseDate(self):
        return self._GetDateFromString(self.fsdData.startDate)

    def GetEndDate(self):
        endDate = self.fsdData.endDate
        if endDate:
            return self._GetDateFromString(endDate)
        else:
            return self.GetReleaseDate() + datetime.timedelta(days=ISNEW_DAYS_THRESHOLD)

    def _GetToday(self):
        return datetime.date.today()

    def IsReleased(self):
        if self.GetReleaseDate() < self._GetToday():
            return True
        if self.GetReleaseDate() == self._GetToday():
            return downtime.is_downtime_done_today()
        return False

    def IsExpired(self):
        if self.GetEndDate() < self._GetToday():
            return True
        if self.GetEndDate() == self._GetToday():
            return downtime.is_downtime_done_today()
        return False

    def IsAlreadySeen(self):
        return self.featureID in self._GetSeenIDs()

    def MarkAsSeen(self):
        alreadySeen = self._GetSeenIDs()
        if self.featureID not in alreadySeen:
            alreadySeen.append(self.featureID)
        self.isForceShown = False
        settings.user.ui.Set(SETTING_ID, alreadySeen)

    def _GetSeenIDs(self):
        return settings.user.ui.Get(SETTING_ID, [])

    def MarkAsUnseen(self):
        alreadySeen = self._GetSeenIDs()
        if self.featureID in alreadySeen:
            alreadySeen.remove(self.featureID)
        settings.user.ui.Set(SETTING_ID, alreadySeen)

    def MarkAsForceShow(self):
        self.isForceShown = True

    def GetRegion(self):
        return self.fsdData.region or 'ccp'

    def IsInCurrentRegion(self):
        return self.GetRegion() == boot.region

    def IsShown(self):
        return self.isForceShown or self.IsApproriateToShow() and not self.IsAlreadySeen()

    def IsApproriateToShow(self):
        return self.IsInCurrentRegion() and self.IsReleased() and not self.IsExpired()

    @property
    def availableToAgency(self):
        return getattr(self.fsdData, 'availableToAgency', False)
