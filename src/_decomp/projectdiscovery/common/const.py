#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\common\const.py
from projectdiscovery.common.projects.covid.iskmultipliers import ISK_MULTIPLIERS as COVID_ISK_MULTIPLIERS
from projectdiscovery.common.projects.covid.leveluprewards import CRATES as COVID_CRATES
from projectdiscovery.common.projects.covid.tiers import TIERS as COVID_TIERS
from projectdiscovery.common.projects.exoplanets.iskmultipliers import ISK_MULTIPLIERS as EXOPLANET_ISK_MULTIPLIERS
from projectdiscovery.common.projects.exoplanets.leveluprewards import CRATES as EXOPLANET_CRATES
from projectdiscovery.common.projects.exoplanets.tiers import TIERS as EXOPLANET_TIERS
EXOPLANETS_PROJECT_ID = 'unige-exoplanet'
COVID_PROJECT_ID = 'mcgill-polyseg'
ACTIVE_PROJECT_ID = COVID_PROJECT_ID
IS_API_MOCKED = False
INITIAL_PLAYER_SCORE = 0
PLAYER_NOT_IN_DATABASE_ERROR_CODE = 103010
MAX_TASKS_PER_MINUTE = 5
TASK_ALLOWANCE_MET_MSG = 'StopSpamProjectDiscoveryTaskSubmission'
TASK_ALLOWANCE_MET_MSG_OMEGA = 'StopSpamProjectDiscoveryTaskSubmissionOmega'
TASK_ALLOWANCE_PER_MINUTE_MSG = 'StopSpamProjectDiscoveryTaskRetrieval'
TIERS_BY_PROJECT_ID = {COVID_PROJECT_ID: COVID_TIERS,
 EXOPLANETS_PROJECT_ID: EXOPLANET_TIERS}
ISK_MULTIPLIERS_BY_PROJECT_ID = {COVID_PROJECT_ID: COVID_ISK_MULTIPLIERS,
 EXOPLANETS_PROJECT_ID: EXOPLANET_ISK_MULTIPLIERS}
CRATES_BY_PROJECT_ID = {COVID_PROJECT_ID: COVID_CRATES,
 EXOPLANETS_PROJECT_ID: EXOPLANET_CRATES}
TIERS = TIERS_BY_PROJECT_ID.get(ACTIVE_PROJECT_ID, COVID_TIERS)
ISK_MULTIPLIERS = ISK_MULTIPLIERS_BY_PROJECT_ID.get(ACTIVE_PROJECT_ID, COVID_ISK_MULTIPLIERS)
CRATES = CRATES_BY_PROJECT_ID.get(ACTIVE_PROJECT_ID, COVID_CRATES)
NEEDED_LEVEL_FOR_SUPERIOR_CRATES = 25
SUPERIOR_LOOT_CRATE_TYPE_ID = CRATES[1]
LOOT_CRATE_TYPE_ID = CRATES[0]
