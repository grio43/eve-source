#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\storylines\common\nes_intro_constants.py
from eve.common.lib.appConst import raceAmarr
from eve.common.lib.appConst import raceCaldari
from eve.common.lib.appConst import raceGallente
from eve.common.lib.appConst import raceMinmatar
NES_INTRO_NODE_GRAPH_ID = 510

class NesIntroState(object):
    UNSET = 0
    ACTIVE = 1
    COMPLETED = 2
    SKIPPED = 3


CHECKPOINT_START = 73
CHECKPOINT_CRATE_RECEIVED = 74
CHECKPOINT_CRATE_OPENED = 84
CHECKPOINT_SKIN_BOUGHT = 79
CHECKPOINT_SKIN_APPLIED = 82
CHECKPOINT_END = 83
ALL_CHECKPOINTS = [CHECKPOINT_START,
 CHECKPOINT_CRATE_RECEIVED,
 CHECKPOINT_CRATE_OPENED,
 CHECKPOINT_SKIN_BOUGHT,
 CHECKPOINT_SKIN_APPLIED,
 CHECKPOINT_END]
ALL_OFFER_IDS = {raceAmarr: ['VEVC-6314', 'VEVC-6315', 'VEVC-6316'],
 raceCaldari: ['VEVC-6317', 'VEVC-6318', 'VEVC-6319'],
 raceGallente: ['VEVC-6320', 'VEVC-6321', 'VEVC-6322'],
 raceMinmatar: ['VEVC-6323', 'VEVC-6324', 'VEVC-6325']}

def is_nes_intro_checkpoint(checkpoint_id):
    if checkpoint_id in ALL_CHECKPOINTS:
        return True
    return False
