#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\util\characterCreationUtil.py
import gatekeeper

def IsInStreamlinedCCFlowCohort():
    return gatekeeper.user.IsInitialized() and gatekeeper.user.IsInCohort(gatekeeper.cohortStreamlinedCharacterCreation)
