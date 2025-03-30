#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\planet\mecDen\mercDenUiController.py
import sys
from carbonui.services.setting import CharSettingNumeric
from clonegrade import CLONE_STATE_ALPHA
from eve.client.script.ui.shared.planet.mecDen.mercDenUtil import MercDenEntryInfo
from localization import GetByLabel
from sovereignty.mercenaryden.client.repository import get_mercenary_den_repository
from sovereignty.mercenaryden.common.errors import ServiceUnavailable, UnknownMercenaryDen, GenericError

class MercDenUiController(object):

    def __init__(self):
        self._absoluteMaxDens = None
        self._myMaxDens = None
        self._repository = get_mercenary_den_repository()
        self.selectedSetting = CharSettingNumeric('mercDenSelected', 0, 0, sys.maxsize)

    def GetEntryInfosForMyMercDens(self):
        mercDenIDs = self._repository.get_my_mercenary_dens_ids()
        if not mercDenIDs:
            return []
        activites = self._repository.get_all_mercenary_den_activities_for_character()
        mercDens = []
        for eachID in mercDenIDs:
            mercDen = self.GetMercDenEntryInfo(eachID, activites)
            mercDens.append(mercDen)

        return mercDens

    def GetMercDenEntryInfo(self, itemID, activites = None):
        try:
            if activites is None:
                activites = self._repository.get_all_mercenary_den_activities_for_character()
            mercDen = self._repository.get_mercenary_den(itemID)
            activitesForDen = [ x for x in activites if x.den_id == itemID ]
            return MercDenEntryInfo(itemID, mercDen, activitesForDen)
        except (ServiceUnavailable, UnknownMercenaryDen, GenericError):
            return MercDenEntryInfo(itemID)

    @property
    def absoluteMaxDenNum(self):
        if self._absoluteMaxDens is None:
            self._fetch_max_dens()
        return self._absoluteMaxDens

    @property
    def myMaxDenNum(self):
        if self._myMaxDens is None:
            self._fetch_max_dens()
        return self._myMaxDens

    def _fetch_max_dens(self):
        self._myMaxDens, self._absoluteMaxDens = self._repository.get_maximum_dens_for_character()

    def ClearMyMaxDens(self):
        self._myMaxDens = None

    def GetDeployedDensText(self, numDens):
        if self.absoluteMaxDenNum is None or self.myMaxDenNum is None:
            return GetByLabel('UI/Sovereignty/MercenaryDen/MyMercenaryDensWindow/InfoNotAvailable')
        return GetByLabel('UI/Sovereignty/MercenaryDen/MyMercenaryDensWindow/NumMyDensAndMax', numMyDens=numDens, numMax=self.myMaxDenNum)

    def SelectEntry(self, itemID):
        self.selectedSetting.set(itemID)

    def GetSelectedItemID(self):
        return self.selectedSetting.get()

    def IsAlpha(self):
        clone_state = sm.GetService('cloneGradeSvc').GetCloneGrade()
        return clone_state == CLONE_STATE_ALPHA

    def CanTrainMoreSkills(self):
        if self.absoluteMaxDenNum is None:
            return False
        if self.myMaxDenNum < self.absoluteMaxDenNum:
            return True
        return False
