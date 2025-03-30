#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\careergoals\client\signal.py
from signals import Signal
on_definitions_loaded = Signal(signalName='on_definitions_loaded')
on_states_loaded = Signal(signalName='on_states_loaded')
on_goal_progress_changed = Signal(signalName='on_goal_progress_changed')
on_goal_completed = Signal(signalName='on_goal_completed')
on_reward_claimed = Signal(signalName='on_reward_claimed')
on_reward_claimed_failed = Signal(signalName='on_reward_claimed_failed')
on_air_career_program_availability_changed = Signal(signalName='on_air_career_program_availability_changed')
