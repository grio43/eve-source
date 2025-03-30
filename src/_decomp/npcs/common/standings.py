#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\npcs\common\standings.py
STANDINGS_HOSTILE = -1
STANDINGS_NEUTRAL = 0
STANDINGS_FRIENDLY = 1
STANDINGS_CLASSES = [STANDINGS_HOSTILE, STANDINGS_NEUTRAL, STANDINGS_FRIENDLY]
NAME_BY_STANDINGS_CLASSES = {STANDINGS_HOSTILE: 'Hostile',
 STANDINGS_NEUTRAL: 'Neutral',
 STANDINGS_FRIENDLY: 'Friendly'}

def classify_standings(hostile_threshold, friendly_threshold, standings):
    if standings <= hostile_threshold:
        return STANDINGS_HOSTILE
    elif standings >= friendly_threshold:
        return STANDINGS_FRIENDLY
    else:
        return STANDINGS_NEUTRAL
