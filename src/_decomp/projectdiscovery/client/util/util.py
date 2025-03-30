#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\util\util.py
from projectdiscovery.common.const import TIERS

def calculate_score_bar_length(experience, total_xp_needed_for_current_rank, total_xp_needed_for_next_rank, max_score_bar_length):
    xp_available_for_next_rank = float(experience - total_xp_needed_for_current_rank)
    xp_needed_for_next_rank = float(total_xp_needed_for_next_rank - total_xp_needed_for_current_rank)
    tol = 0.001
    if xp_needed_for_next_rank < tol:
        ratio = 1
    else:
        ratio = xp_available_for_next_rank / xp_needed_for_next_rank
    length = ratio * max_score_bar_length
    if length > max_score_bar_length:
        length = length - max_score_bar_length
    return length


RANK_BAND_BY_LEVEL = {15: 1,
 30: 2,
 60: 3,
 90: 4,
 120: 5,
 180: 6,
 210: 7,
 240: 8,
 300: 9,
 450: 10,
 750: 11,
 1000: 12}

def calculate_rank_band(rank):
    current_rank_band = 1
    for level in sorted(RANK_BAND_BY_LEVEL.keys()):
        rank_band = RANK_BAND_BY_LEVEL[level]
        if level > rank:
            return current_rank_band
        current_rank_band = rank_band

    return current_rank_band
