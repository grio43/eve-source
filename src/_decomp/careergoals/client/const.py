#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\careergoals\client\const.py
import characterdata.careerpathconst as cpConst
from itertoolsext.Enum import Enum
from collections import OrderedDict

@Enum

class RewardType(object):
    TYPE_ID = 'TYPE_ID'


@Enum

class RewardLabel(object):
    ALPHA = 'alpha'
    OMEGA = 'omega'


@Enum

class GoalSubType(object):
    CAREER_PATH_GOAL = 'CAREER_PATH_GOAL'
    OVERALL_GOAL = 'OVERALL_GOAL'


@Enum

class GoalThreat(object):
    THREAT_NONE = 0
    THREAT_LOW = 1
    THREAT_MEDIUM = 2
    THREAT_HIGH = 3


PROTO_CAREER_EXPLORER_ID = 1
PROTO_CAREER_INDUSTRIALIST_ID = 2
PROTO_CAREER_ENFORCER_ID = 3
PROTO_CAREER_SOLDIER_OF_FORTUNE_ID = 4

def get_career_path_id_from_proto_id(protobufCareerPathID):
    if protobufCareerPathID == PROTO_CAREER_EXPLORER_ID:
        return cpConst.career_path_explorer
    elif protobufCareerPathID == PROTO_CAREER_INDUSTRIALIST_ID:
        return cpConst.career_path_industrialist
    elif protobufCareerPathID == PROTO_CAREER_ENFORCER_ID:
        return cpConst.career_path_enforcer
    elif protobufCareerPathID == PROTO_CAREER_SOLDIER_OF_FORTUNE_ID:
        return cpConst.career_path_soldier_of_fortune
    else:
        return 0


GOAL_ANNOTATION_DURATION = 'duration'
GOAL_ANNOTATION_ACTIVITY_GROUP = 'group'
GOAL_ANNOTATION_GOAL_SUBTYPE = 'subtype'
GOAL_ANNOTATION_AURA_TEXT_ID = 'auraTextID'
GOAL_ANNOTATION_AGENCY_LINK_TEXT_ID = 'agencyLinkTextID'
GOAL_ANNOTATION_AGENCY_SCREEN_ID = 'agencyScreen'
GOAL_ANNOTATION_ORDER = 'order'
GOAL_ANNOTATION_VIDEO = 'videoID'
EXPLORER_CAREERAGENTMISSIONS = 101
EXPLORER_SCANNING = 102
EXPLORER_HACKING = 103
EXPLORER_HACKING2 = 104
EXPLORER_WORMHOLES = 105
EXPLORER_GASSITES = 106
EXPLORER_COMBATSITES = 107
EXPLORER_NAVIGATION = 108
EXPLORER_NAVIGATION2 = 109
EXPLORER_PROJECTDISCOVERY = 110
INDUSTRIALIST_CAREERAGENTMISSIONS = 201
INDUSTRIALIST_MARKET = 203
INDUSTRIALIST_SALVAGE = 204
INDUSTRIALIST_RESOURCEHARVESTING = 205
INDUSTRIALIST_REFINING = 206
INDUSTRIALIST_MANUFACTURING = 207
INDUSTRIALIST_DISTRIBUTIONAGENT = 208
INDUSTRIALIST_MININGAGENT = 209
INDUSTRIALIST_RESEARCH = 210
ENFORCER_ENFORCERCAREERAGENTMISSIONS = 301
ENFORCER_SECURITYAGENT = 302
ENFORCER_ABYSSALDEADSPACE = 303
ENFORCER_COMBAT = 304
ENFORCER_BOUNTIES = 305
ENFORCER_COMBATSITES = 306
ENFORCER_EPICARC = 307
ENFORCER_MARKET = 308
ENFORCER_STANDINGS = 309
ENFORCER_LOYALTYPOINTS = 310
SOLDIEROFFORTUNE_CAREERAGENTMISSIONS = 401
SOLDIEROFFORTUNE_SOCIAL = 402
SOLDIEROFFORTUNE_ELECTRONICWARFARE = 403
SOLDIEROFFORTUNE_COMBAT1 = 404
SOLDIEROFFORTUNE_PVP = 405
SOLDIEROFFORTUNE_CAPACITORWARFARE = 406
SOLDIEROFFORTUNE_FACTIONWARFARE = 407
SOLDIEROFFORTUNE_SUPPORT = 408
SOLDIEROFFORTUNE_DESTRUCTION = 409
SOLDIEROFFORTUNE_DUELS = 410
CAREER_PATH_GROUPS = {cpConst.career_path_explorer: OrderedDict([('CareerAgentMissions', EXPLORER_CAREERAGENTMISSIONS),
                                ('Scanning', EXPLORER_SCANNING),
                                ('Hacking', EXPLORER_HACKING),
                                ('AdvancedHacking', EXPLORER_HACKING2),
                                ('Wormholes', EXPLORER_WORMHOLES),
                                ('GasSites', EXPLORER_GASSITES),
                                ('CombatSites', EXPLORER_COMBATSITES),
                                ('Navigation', EXPLORER_NAVIGATION),
                                ('AdvancedNavigation', EXPLORER_NAVIGATION2),
                                ('ProjectDiscovery', EXPLORER_PROJECTDISCOVERY)]),
 cpConst.career_path_industrialist: OrderedDict([('IndustrialistCareerAgentsMissions', INDUSTRIALIST_CAREERAGENTMISSIONS),
                                     ('Market', INDUSTRIALIST_MARKET),
                                     ('Salvage', INDUSTRIALIST_SALVAGE),
                                     ('ResourceHarvesting', INDUSTRIALIST_RESOURCEHARVESTING),
                                     ('Refining', INDUSTRIALIST_REFINING),
                                     ('Manufacturing', INDUSTRIALIST_MANUFACTURING),
                                     ('DistributionAgent', INDUSTRIALIST_DISTRIBUTIONAGENT),
                                     ('MiningAgent', INDUSTRIALIST_MININGAGENT),
                                     ('Research', INDUSTRIALIST_RESEARCH)]),
 cpConst.career_path_enforcer: OrderedDict([('CareerAgentMissions', ENFORCER_ENFORCERCAREERAGENTMISSIONS),
                                ('SecurityAgent', ENFORCER_SECURITYAGENT),
                                ('AbyssalDeadspace', ENFORCER_ABYSSALDEADSPACE),
                                ('Combat', ENFORCER_COMBAT),
                                ('Bounties', ENFORCER_BOUNTIES),
                                ('CombatSites', ENFORCER_COMBATSITES),
                                ('EpicArc', ENFORCER_EPICARC),
                                ('Market', ENFORCER_MARKET),
                                ('Standings', ENFORCER_STANDINGS),
                                ('LoyaltyPoints', ENFORCER_LOYALTYPOINTS)]),
 cpConst.career_path_soldier_of_fortune: OrderedDict([('CareerAgentMissions', SOLDIEROFFORTUNE_CAREERAGENTMISSIONS),
                                          ('Social', SOLDIEROFFORTUNE_SOCIAL),
                                          ('ElectronicWarfare', SOLDIEROFFORTUNE_ELECTRONICWARFARE),
                                          ('Combat', SOLDIEROFFORTUNE_COMBAT1),
                                          ('PvP', SOLDIEROFFORTUNE_PVP),
                                          ('CapacitorWarfare', SOLDIEROFFORTUNE_CAPACITORWARFARE),
                                          ('FactionWarfare', SOLDIEROFFORTUNE_FACTIONWARFARE),
                                          ('Support', SOLDIEROFFORTUNE_SUPPORT),
                                          ('Destruction', SOLDIEROFFORTUNE_DESTRUCTION),
                                          ('Duels', SOLDIEROFFORTUNE_DUELS)])}

def get_career_path_group_id(careerPathID, annotationString):
    careerPath = CAREER_PATH_GROUPS.get(careerPathID, None)
    if careerPath:
        return careerPath.get(annotationString, None)
