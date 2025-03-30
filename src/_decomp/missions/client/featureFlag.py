#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\missions\client\featureFlag.py
from launchdarkly.client.featureflag import create_boolean_flag_check
import missions.client.missionSignals as missionSignals
are_mission_objectives_enabled = create_boolean_flag_check(launchdarkly_key='mission-objectives-enabled-feature-flag', fallback_value=True, on_flag_changed_callback=missionSignals.on_objectives_availability_changed)
