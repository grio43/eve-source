#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evewar\const.py
from carbon.common.lib.const import HOUR, DAY, WEEK
warRelationshipUnknown = 0
warRelationshipYourCorp = 1
warRelationshipYourAlliance = 2
warRelationshipAtWar = 3
warRelationshipAtWarCanFight = 4
warRelationshipAlliesAtWar = 5
COST_OF_WAR = 100000000
BILLING_PERIOD = WEEK
WAR_NEGOTIATION_TYPE_ALLY_OFFER = 0
WAR_NEGOTIATION_TYPE_SURRENDER_OFFER = 2
WAR_NEGOTIATION_STATE_NEW = 0
WAR_NEGOTIATION_STATE_ACCEPTED = 1
WAR_NEGOTIATION_STATE_DECLINED = 2
WAR_NEGOTIATION_STATE_RETRACTED = 3
WAR_NEGOTIATION_EXPIRY = DAY
ENDED_NONE = None
ENDED_UNLICENSED_AGGRESSOR = 1
ENDED_UNLICENSED_DEFENDER = 2
ENDED_WARHQ_GONE = 3
ENDED_WAR_ADOPTED = 4
ENDED_CORP_DELETED = 5
ENDED_RETRACTED = 6
ENDED_SURRENDER = 7
ENDED_CONCORD = 8
ENDED_HQ_OWNER_LEFT = 9
ENDED_UNPAID_BILL = 10
ENDED_MUTUAL_END = 11
ENDED_LEFT_ALLIANCE = 12
ENDED_ALLIANCE_DELETED = 13
ENDED_GM_ACTION = 14
ENDED_WAR_HQ_SYSTEM_SECURITY_DROP = 15
STRINGS_ENDED = {v:k for k, v in locals().iteritems() if k.startswith('ENDED_')}
STARTED_NONE = None
STARTED_PLAYER_DECLARED = 1
STARTED_ADOPTION = 2
STARTED_INHERITED = 3
STARTED_GM_ACTION = 4
STRINGS_STARTED = {v:k for k, v in locals().iteritems() if k.startswith('STARTED_')}
PEACE_REASON_UNDEFINED = 0
PEACE_REASON_HQ_REMOVED = 1
PEACE_REASON_HQ_OWNER_LEFT_ALLIANCE = 2
PEACE_REASON_CORP_LEFT_ALLIANCE = 3
PEACE_REASON_WAR_SURRENDER = 4
PEACE_REASON_UNPAID_BILL = 5
PEACE_REASON_STRINGS = {PEACE_REASON_UNDEFINED: 'Undefined',
 PEACE_REASON_HQ_REMOVED: 'HQ removed',
 PEACE_REASON_HQ_OWNER_LEFT_ALLIANCE: 'HQ owner left alliance',
 PEACE_REASON_CORP_LEFT_ALLIANCE: 'Corp left alliance',
 PEACE_REASON_WAR_SURRENDER: 'Surrender',
 PEACE_REASON_UNPAID_BILL: 'Attacker did not pay war bill'}
WAR_SPOOLUP_HOURS = 24
WAR_SPOOLUP = WAR_SPOOLUP_HOURS * HOUR
WAR_COOLDOWN_HOURS = 24
WAR_COOLDOWN = WAR_COOLDOWN_HOURS * HOUR
WAR_MUTUAL_WAR_EXPIRY_DAYS = 7
ALLY_SPOOLUP = 4 * HOUR
ALLY_COMMITMENT_PERIOD = 2 * WEEK
FORCED_PEACE_PERIOD = 2 * WEEK
