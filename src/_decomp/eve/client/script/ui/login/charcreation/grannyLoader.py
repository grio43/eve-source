#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation\grannyLoader.py
import os
import trinity
BLOODLINE_ANIMATION_ROOT = 'res:\\animation\\%s\\charactercreation'
BLOODLINE_IDLE_ANIMATIONS = {0: 'selection_amarr_amarr.gr2',
 1: 'selection_amarr_khanid.gr2',
 2: 'selection_amarr_nikuni.gr2',
 3: 'selection_caldari_achura.gr2',
 4: 'selection_caldari_civere.gr2',
 5: 'selection_caldari_deties.gr2',
 6: 'selection_gallente_gallente.gr2',
 7: 'selection_gallente_intaki.gr2',
 8: 'selection_gallente_jin-mei.gr2',
 9: 'selection_minmatar_brutor.gr2',
 10: 'selection_minmatar_sebiestor.gr2',
 11: 'selection_minmatar_vherokior.gr2'}
HEAD_LEFT_ANIMATION = 'customization_headlookleft.gr2'
GENDER_NAMES = {0: 'female',
 1: 'male'}

def GrannyBloodlineAnimationLoader(avatar, genderID, poseID):
    anim_path = os.path.join(BLOODLINE_ANIMATION_ROOT % GENDER_NAMES[genderID], BLOODLINE_IDLE_ANIMATIONS[poseID])
    updater = trinity.Tr2GrannyAnimation()
    updater.resPath = str(anim_path)
    avatar.animationUpdater = updater
    trinity.WaitForResourceLoads()
    updater.animationEnabled = True
    clip = updater.grannyRes.GetAnimationName(0)
    updater.PlayAnimationEx(clip, 0, 0, 1)
