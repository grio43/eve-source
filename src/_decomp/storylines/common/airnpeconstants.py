#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\storylines\common\airnpeconstants.py
AIR_NPE_NODE_GRAPH_ID = 49
AIR_NPE_CLIENT_NODE_GRAPH_ID = 716
AIR_NPE_ASTERO_SHIP_TYPE = 58745

class AirNpeState(object):
    ACTIVE = 1
    COMPLETED = 2
    SKIPPED = 3


class AirNpeScene(object):
    SCENE_1_1 = 1.1
    SCENE_1_2 = 1.2
    SCENE_1_3 = 1.3
    SCENE_1_4 = 1.4
    SCENE_1_5 = 1.5
    SCENE_2_1 = 2.1
    SCENE_2_2 = 2.2
    SCENE_2_3 = 2.3
    SCENE_2_4 = 2.4
    SCENE_2_5 = 2.5


CHECKPOINT_1_1_01 = 12
CHECKPOINT_1_2_01 = 16
CHECKPOINT_1_3_01 = 44
CHECKPOINT_1_3_02 = 85
CHECKPOINT_1_3_03 = 86
CHECKPOINT_1_3_04 = 87
CHECKPOINT_1_3_05 = 88
CHECKPOINT_1_4_01 = 45
CHECKPOINT_1_5_01 = 89
CHECKPOINT_1_5_02 = 46
CHECKPOINT_1_5_03 = 47
CHECKPOINT_1_5_04 = 48
CHECKPOINT_1_5_05 = 49
CHECKPOINT_1_5_06 = 55
CHECKPOINT_1_5_07 = 90
CHECKPOINT_2_1_01 = 50
CHECKPOINT_2_1_02 = 51
CHECKPOINT_2_1_03 = 52
CHECKPOINT_2_1_04 = 56
CHECKPOINT_2_1_05 = 53
CHECKPOINT_2_1_06 = 54
CHECKPOINT_2_2_01 = 57
CHECKPOINT_2_2_02 = 58
CHECKPOINT_2_2_03 = 59
CHECKPOINT_2_2_04 = 60
CHECKPOINT_2_2_05 = 62
CHECKPOINT_2_3_01 = 63
CHECKPOINT_2_4_01 = 64
CHECKPOINT_2_4_02 = 65
CHECKPOINT_2_4_03 = 66
CHECKPOINT_2_5_01 = 67
CHECKPOINT_2_5_02 = 91
CHECKPOINT_2_5_03 = 92
CHECKPOINTS_BY_SCENE = {AirNpeScene.SCENE_1_1: [CHECKPOINT_1_1_01],
 AirNpeScene.SCENE_1_2: [CHECKPOINT_1_2_01],
 AirNpeScene.SCENE_1_3: [CHECKPOINT_1_3_01,
                         CHECKPOINT_1_3_02,
                         CHECKPOINT_1_3_03,
                         CHECKPOINT_1_3_04,
                         CHECKPOINT_1_3_05],
 AirNpeScene.SCENE_1_4: [CHECKPOINT_1_4_01],
 AirNpeScene.SCENE_1_5: [CHECKPOINT_1_5_01,
                         CHECKPOINT_1_5_02,
                         CHECKPOINT_1_5_03,
                         CHECKPOINT_1_5_04,
                         CHECKPOINT_1_5_05,
                         CHECKPOINT_1_5_06,
                         CHECKPOINT_1_5_07],
 AirNpeScene.SCENE_2_1: [CHECKPOINT_2_1_01,
                         CHECKPOINT_2_1_02,
                         CHECKPOINT_2_1_03,
                         CHECKPOINT_2_1_04,
                         CHECKPOINT_2_1_05,
                         CHECKPOINT_2_1_06],
 AirNpeScene.SCENE_2_2: [CHECKPOINT_2_2_01,
                         CHECKPOINT_2_2_02,
                         CHECKPOINT_2_2_03,
                         CHECKPOINT_2_2_04,
                         CHECKPOINT_2_2_05],
 AirNpeScene.SCENE_2_3: [CHECKPOINT_2_3_01],
 AirNpeScene.SCENE_2_4: [CHECKPOINT_2_4_01, CHECKPOINT_2_4_02, CHECKPOINT_2_4_03],
 AirNpeScene.SCENE_2_5: [CHECKPOINT_2_5_01, CHECKPOINT_2_5_02, CHECKPOINT_2_5_03]}

def is_air_npe_checkpoint(checkpoint_id):
    for scene_checkpoints in CHECKPOINTS_BY_SCENE.values():
        if checkpoint_id in scene_checkpoints:
            return True

    return False


def get_scene_from_checkpoint(checkpoint_id):
    for scene_id, scene_checkpoints in CHECKPOINTS_BY_SCENE.items():
        if checkpoint_id in scene_checkpoints:
            return scene_id

    return AirNpeScene.SCENE_1_1
