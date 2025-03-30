#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\feature_flag.py
from launchdarkly.client.featureflag import create_boolean_flag_check
is_new_character_creation_enabled = create_boolean_flag_check(launchdarkly_key='enable_new_character_creation', fallback_value=False)
