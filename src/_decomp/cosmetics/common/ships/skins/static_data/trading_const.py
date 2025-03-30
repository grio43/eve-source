#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\common\ships\skins\static_data\trading_const.py
from eve.common.lib import appConst
max_concurrent_listings_default = 1
max_concurrent_listings_skills = (appConst.typeHubPromotion, appConst.typeHubAlgorithmOptimization)
max_concurrent_listings_added_by_skill_and_level = {max_concurrent_listings_skills[0]: {1: 1,
                                     2: 1,
                                     3: 1,
                                     4: 1,
                                     5: 1},
 max_concurrent_listings_skills[1]: {1: 4,
                                     2: 5,
                                     3: 5,
                                     4: 5,
                                     5: 5}}
tax_rate_reduction_skills = (appConst.typeParagonRelations, appConst.typeParagonPartnership, appConst.typeExecutiveParagonPartnership)
tax_rate_percent_reduction_per_level = {tax_rate_reduction_skills[0]: {1: 1,
                                2: 1,
                                3: 1,
                                4: 1,
                                5: 1},
 tax_rate_reduction_skills[1]: {1: 1,
                                2: 1,
                                3: 1,
                                4: 1,
                                5: 1},
 tax_rate_reduction_skills[2]: {1: 1,
                                2: 1,
                                3: 1,
                                4: 1,
                                5: 1}}
