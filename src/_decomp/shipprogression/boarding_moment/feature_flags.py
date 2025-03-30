#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipprogression\boarding_moment\feature_flags.py
from launchdarkly.client.featureflag import create_boolean_flag_check
are_first_time_boarding_moments_enabled = create_boolean_flag_check(launchdarkly_key='autoplay_boarding_moment', fallback_value=True)
