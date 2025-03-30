#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\corporation\client\goals\featureFlag.py
from corporation.client.goals import goalSignals
from launchdarkly.client.featureflag import create_boolean_flag_check
are_corporation_goals_enabled = create_boolean_flag_check(launchdarkly_key='corp-goals-enabled-feature-flag', fallback_value=True, on_flag_changed_callback=goalSignals.on_availability_changed)
are_corporation_goal_payments_enabled = create_boolean_flag_check(launchdarkly_key='goal-payment-enabled-feature-flag', fallback_value=True, on_flag_changed_callback=goalSignals.on_payment_availability_changed)
