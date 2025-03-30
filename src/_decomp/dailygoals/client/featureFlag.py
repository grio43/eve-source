#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dailygoals\client\featureFlag.py
import dailygoals.client.goalSignals as dailyGoalSignals
from launchdarkly.client.featureflag import create_boolean_flag_check
are_daily_goals_enabled = create_boolean_flag_check(launchdarkly_key='daily-goals-enabled-feature-flag', fallback_value=True, on_flag_changed_callback=dailyGoalSignals.on_availability_changed)
are_daily_goal_payments_enabled = create_boolean_flag_check(launchdarkly_key='daily-goal-payment-enabled-feature-flag', fallback_value=True, on_flag_changed_callback=dailyGoalSignals.on_payment_availability_changed)
