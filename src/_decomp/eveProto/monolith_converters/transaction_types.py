#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\monolith_converters\transaction_types.py
from eve.common.script.mgt.appLogConst import eventLoyaltyPointsGranted, eventLoyaltyPointsDailyGoalReward
LP_EVENT_TYPES = [eventLoyaltyPointsGranted, eventLoyaltyPointsDailyGoalReward]

def get_event_type_from_lp_transaction_type(transaction_type_value):
    if transaction_type_value < len(LP_EVENT_TYPES):
        return LP_EVENT_TYPES[transaction_type_value]
    raise ValueError('Transaction type does not correspond to an event type')
