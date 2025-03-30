#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\clonegrade\cloneGradeSvc.py
import uthread
import urlparse
from carbon.common.script.sys import service
import clonegrade
import evetypes
import inventorycommon.const as invconst
from carbonui.uicore import uicore
from eve.client.script.ui.shared.cloneGrade import open_omega_state_window, open_alpha_state_window
import trinity
import blue
from eve.common.lib.vgsConst import CATEGORYTAG_GAMETIME
from eve.common.script.util.industryCommon import IsBlueprintCategory
from eveexceptions import UserError
from eveexceptions.exceptionEater import ExceptionEater
from eveprefs import boot
from skills import skillConst

class CloneGradeSvc(service.Service):
    __guid__ = 'svc.cloneGradeSvc'
    __servicename__ = 'cloneGradeSvc'
    __displayname__ = 'Clone Grade Service'
    __notifyevents__ = ['OnSubscriptionChangedServer', 'OnApplicationFocusChanged']

    def Run(self, ms):
        service.Service.Run(self, ms)
        self._cloneState = None
        self.upgradeFanfareMomentPending = False

    def GetCloneGrade(self):
        if self._cloneState is None:
            self.PrimeCloneState()
        return self._cloneState

    def PrimeCloneState(self):
        self._cloneState = sm.RemoteSvc('subscriptionMgr').GetCloneGrade()

    def GetMaxSkillLevel(self, skillID, cloneGrade = None):
        if cloneGrade is None:
            cloneGrade = self.GetCloneGrade()
        if cloneGrade == clonegrade.CLONE_STATE_OMEGA:
            return skillConst.skill_max_level
        if cloneGrade == clonegrade.CLONE_STATE_ALPHA:
            clone = clonegrade.CloneGradeStorage()[session.raceID]
            try:
                return clone.skillsByTypeID[skillID].level
            except KeyError:
                return 0

        else:
            raise RuntimeError('Unknown Clone Grade {}'.format(cloneGrade))

    def IsOmega(self):
        return self.GetCloneGrade() == clonegrade.CLONE_STATE_OMEGA

    def IsRestricted(self, typeID, cloneGrade = None):
        if cloneGrade is None:
            cloneGrade = self.GetCloneGrade()
        if self.IsRequirementsRestricted(typeID, cloneGrade):
            return True
        if evetypes.GetCategoryID(typeID) == invconst.categorySkill:
            return self.GetMaxSkillLevel(typeID, cloneGrade) < 1
        if IsBlueprintCategory(evetypes.GetCategoryID(typeID)):
            return self._IsBlueprintRestricted(typeID, cloneGrade)
        return False

    def IsRequirementsRestricted(self, typeID, cloneGrade = None):
        if cloneGrade is None:
            cloneGrade = self.GetCloneGrade()
        requiredSkills = sm.GetService('skills').GetRequiredSkillsRecursive(typeID)
        for skillID, requiredLevel in requiredSkills.iteritems():
            if self.IsSkillLevelRestricted(skillID, requiredLevel, cloneGrade):
                return True

        return False

    def IsSkillLevelRestricted(self, typeID, level, cloneGrade = None):
        return self.GetMaxSkillLevel(typeID, cloneGrade) < level

    def _IsBlueprintRestricted(self, typeID, cloneState):
        blueprint = sm.GetService('blueprintSvc').GetBlueprintType(typeID)
        for activity in blueprint.activities.values():
            if not activity.IsClonestateRestricted(cloneState):
                return False

        return True

    def IsRestrictedForAlpha(self, typeID):
        return self.IsRestricted(typeID, clonegrade.CLONE_STATE_ALPHA)

    def OnSubscriptionChangedServer(self, newState):
        self._cloneState = newState
        if self.IsOmega():
            sm.GetService('audio').SendUIEvent('upgrade_to_omega_play')
            if trinity.app.active:
                self.TriggerCloneStateUpgradeFanfare()
            else:
                self.upgradeFanfareMomentPending = True
        else:
            sm.ScatterEvent('OnSubscriptionChanged')
            sm.GetService('audio').SendUIEvent('downgrade_to_alpha_play')
            self.TriggerLapseWindow()

    def TriggerCloneStateUpgradeFanfare(self):
        uthread.new(self._TriggerCloneStateUpgradeFanfare)

    def _TriggerCloneStateUpgradeFanfare(self):
        loadingSvc = sm.GetService('loading')
        loadingSvc.FadeIn()
        sm.ScatterEvent('OnSubscriptionChanged')
        open_omega_state_window()
        loadingSvc.FadeOut(600)

    def TriggerLapseWindow(self):
        open_alpha_state_window()

    def OnApplicationFocusChanged(self, hasFocus):
        if self.upgradeFanfareMomentPending and hasFocus:
            self.upgradeFanfareMomentPending = False
            blue.synchro.SleepWallclock(1000)
            self.TriggerCloneStateUpgradeFanfare()

    def UpgradeCloneAction(self, origin = None, reason = None):
        if boot.region == 'optic':
            sm.GetService('vgsService').OpenStore(categoryTag=CATEGORYTAG_GAMETIME)
            return
        try:
            baseUrl = uicore.cmd.GetStoreServerUrl()
            accountUrl = uicore.cmd.GetURLWithParameters(baseUrl, path='omega', origin=origin, reason=reason)
            if 'secure' in baseUrl.lower():
                baseUrl = urlparse.urljoin(baseUrl, 'store/omega')
                accountUrl = uicore.cmd.GetURLWithParameters(baseUrl, origin=origin, reason=reason)
            blue.os.ShellExecute(accountUrl)
        except Exception:
            self.LogException('Failed to execute Upgrade Clone action')
            raise UserError('FailedToOpenCloneGradeUpgradeUrl')

        with ExceptionEater('eventLog'):
            uthread.new(sm.ProxySvc('eventLog').LogClientEvent, 'trial', ['origin', 'reason'], 'OpenSubscriptionPage', origin, reason)
