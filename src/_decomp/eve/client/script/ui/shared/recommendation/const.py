#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\recommendation\const.py
CURRENT_ACTIVE = 1
ANOTHER_ACTIVE = 2
NO_ACTIVE = 3
REJECTED = 4
COMPLETED = 5
TAG_MINING = 7
TAG_ORE = 9
TAG_COMBAT = 11
TAG_DISTRIBUTION = 12
TAG_EPIC_ARC = 13
TAG_EXPLORATION = 14
TAG_INDUSTRY = 15
TAG_MARKET = 16
TAG_SALVAGING = 17
TAG_SOCIAL = 18
TAG_LANDMARK = 39
BACKROUNDS_BY_TAG_ID = {TAG_MINING: 'res:/UI/Texture/classes/Treatments/backgroundImages/mining.png',
 TAG_ORE: 'res:/UI/Texture/classes/Treatments/backgroundImages/mining.png',
 TAG_COMBAT: 'res:/UI/Texture/classes/Treatments/backgroundImages/combat.png',
 TAG_DISTRIBUTION: 'res:/UI/Texture/classes/Treatments/backgroundImages/distribution.png',
 TAG_EPIC_ARC: 'res:/UI/Texture/classes/Treatments/backgroundImages/epicArc.png',
 TAG_EXPLORATION: 'res:/UI/Texture/classes/Treatments/backgroundImages/exploration.png',
 TAG_INDUSTRY: 'res:/UI/Texture/classes/Treatments/backgroundImages/industry.png',
 TAG_MARKET: 'res:/UI/Texture/classes/Treatments/backgroundImages/market.png',
 TAG_SALVAGING: 'res:/UI/Texture/classes/Treatments/backgroundImages/salvaging.png',
 TAG_SOCIAL: 'res:/UI/Texture/classes/Treatments/backgroundImages/social.png',
 TAG_LANDMARK: 'res:/UI/Texture/classes/Treatments/backgroundImages/landmarks.png'}
HINT_BY_TAG_ID = {TAG_MINING: 'UI/recommendations/Hints/MiningTag',
 TAG_ORE: 'UI/recommendations/Hints/OreTag',
 TAG_COMBAT: 'UI/recommendations/Hints/CombatTag',
 TAG_DISTRIBUTION: 'UI/recommendations/Hints/DistributionTag',
 TAG_EPIC_ARC: 'UI/recommendations/Hints/EpicArcTag',
 TAG_EXPLORATION: 'UI/recommendations/Hints/ExplorationTag',
 TAG_INDUSTRY: 'UI/recommendations/Hints/IndustryTag',
 TAG_MARKET: 'UI/recommendations/Hints/MarketTag',
 TAG_SALVAGING: 'UI/recommendations/Hints/SalvagingTag',
 TAG_SOCIAL: 'UI/recommendations/Hints/SocialTag',
 TAG_LANDMARK: 'UI/recommendations/Hints/LandmarksTag'}

class Sounds(object):
    ACCEPT = 'opportunities_window_accept_play'
    OPEN = 'opportunities_window_open_play'
    QUIT = 'opportunities_window_quit_play'
    DISMISS = 'opportunities_window_recycle_play'
    HOVER = 'opportunities_window_hover_play'
    ATMOSPHERE_START = 'opportunities_window_atmo_play'
    ATMOSPHERE_STOP = 'opportunities_window_atmo_stop'


UPDATE_TIMEOUT_SECONDS = 3
NUM_SLOTS = 3
MAX_QUEUE_LENGTH = 10
