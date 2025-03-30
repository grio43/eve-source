#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\storylines\const.py
from metadata.common.content_tags import ContentTags
from storylines.client.airnpe import skip_air_npe
from storylines.client.nes_intro import skip_nes_intro
AIR_NPE_ACT_1_NODE_GRAPH_ID = 707
AIR_NPE_ACT_2_NODE_GRAPH_ID = 708
AIR_NPE_ACT_1_CONTENT_ID = 'AIR_NPE_ACT_1'
AIR_NPE_ACT_2_CONTENT_ID = 'AIR_NPE_ACT_2'
NES_INTRO_NODE_GRAPH_ID = 745
NES_INTRO_CONTENT_ID = 'NES_INTRO'
NODE_GRAPH_ID_TO_CONTENT_ID = {AIR_NPE_ACT_1_NODE_GRAPH_ID: AIR_NPE_ACT_1_CONTENT_ID,
 AIR_NPE_ACT_2_NODE_GRAPH_ID: AIR_NPE_ACT_2_CONTENT_ID,
 NES_INTRO_NODE_GRAPH_ID: NES_INTRO_CONTENT_ID}
TEMP_STORYLINE_DATA = {AIR_NPE_ACT_1_CONTENT_ID: {'objective_chain_id': 51,
                            'title': 'UI/Opportunities/Storylines/AIR_NPE_ACT_1_TITLE',
                            'description': 'UI/Opportunities/Storylines/AIR_NPE_ACT_1_DESCRIPTION',
                            'operational_intel': 'UI/Opportunities/Storylines/AIR_NPE_ACT_1_INTEL',
                            'tag_line': 'UI/Opportunities/Storylines/AIR_NPE_ACT_1_TAGLINE',
                            'arc_title': 'UI/Opportunities/Storylines/AIR_NPE_ACT_1_ARC_TITLE',
                            'background_image': 'res:/UI/Texture/Classes/Opportunities/hero_card_npe_act_1.png',
                            'content_tag_ids': [ContentTags.feature_introductions,
                                                ContentTags.career_path_enforcer,
                                                ContentTags.career_path_explorer,
                                                ContentTags.career_path_soldier_of_fortune,
                                                ContentTags.career_path_industrialist,
                                                ContentTags.activity_combat],
                            'skip_function': skip_air_npe,
                            'distributor_id': 1000413},
 AIR_NPE_ACT_2_CONTENT_ID: {'objective_chain_id': 51,
                            'title': 'UI/Opportunities/Storylines/AIR_NPE_ACT_2_TITLE',
                            'description': 'UI/Opportunities/Storylines/AIR_NPE_ACT_2_DESCRIPTION',
                            'operational_intel': 'UI/Opportunities/Storylines/AIR_NPE_ACT_2_INTEL',
                            'tag_line': 'UI/Opportunities/Storylines/AIR_NPE_ACT_2_TAGLINE',
                            'arc_title': 'UI/Opportunities/Storylines/AIR_NPE_ACT_2_ARC_TITLE',
                            'background_image': 'res:/UI/Texture/Classes/Opportunities/hero_card_npe_act_2.png',
                            'content_tag_ids': [ContentTags.feature_introductions,
                                                ContentTags.career_path_industrialist,
                                                ContentTags.career_path_enforcer,
                                                ContentTags.career_path_explorer,
                                                ContentTags.career_path_soldier_of_fortune,
                                                ContentTags.activity_mining,
                                                ContentTags.activity_trading],
                            'skip_function': skip_air_npe,
                            'distributor_id': 1000413},
 NES_INTRO_CONTENT_ID: {'objective_chain_id': 61,
                        'title': 'UI/Opportunities/Storylines/NES_INTRO_TITLE',
                        'description': 'UI/Opportunities/Storylines/NES_INTRO_DESCRIPTION',
                        'operational_intel': 'UI/Opportunities/Storylines/NES_INTRO_INTEL',
                        'tag_line': 'UI/Opportunities/Storylines/NES_INTRO_TAGLINE',
                        'background_image': 'res:/UI/Texture/Classes/Opportunities/hero_card_nes_intro.png',
                        'content_tag_ids': [ContentTags.feature_introductions],
                        'skip_function': skip_nes_intro}}
