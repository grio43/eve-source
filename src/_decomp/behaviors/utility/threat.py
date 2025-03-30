#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\utility\threat.py
import gametime

def get_damage_tracker(task):
    return task.context.damageTracker


def get_damage_and_healing(task, target_id, sample_interval_seconds):
    damage_tracker = get_damage_tracker(task)
    return get_damage_and_healing_with_tracker(damage_tracker, target_id, sample_interval_seconds)


def get_damage_and_healing_with_tracker(damage_tracker, target_id, sample_interval_seconds = 10.0):
    time_stamp = gametime.GetSimTimeAfterSeconds(-sample_interval_seconds)
    damage = damage_tracker.GetDamageForShipSince(target_id, time_stamp, toNpcOnly=True)
    healing = damage_tracker.GetHealingDoneByShipSince(target_id, time_stamp)
    return damage + healing


def evaluate_target(damage_tacker, dogma_lm, target_id, sample_interval_seconds):
    threat_value = get_damage_and_healing_with_tracker(damage_tacker, target_id, sample_interval_seconds)
    if dogma_lm.IsShipAbandoned(target_id):
        threat_value *= 0.1
    return threat_value
