#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\talecommon\scenetypes.py
from brennivin.itertoolsext import Bundle
scenesTypes = Bundle()
conditionalScenesTypes = Bundle()
sceneTypesByID = {1: Bundle(name='headquarters', display='Headquarters'),
 2: Bundle(name='assault', display='Assault'),
 3: Bundle(name='vanguard', display='Vanguard'),
 4: Bundle(name='staging', display='Staging'),
 5: Bundle(name='testscene', display='Test Scene'),
 6: Bundle(name='system', display='Solar System'),
 7: Bundle(name='incursionNeutral', display='Incursion Neutral'),
 8: Bundle(name='incursionStaging', display='Incursion Staging'),
 9: Bundle(name='incursionLightInfestation', display='Incursion Light Infestation'),
 10: Bundle(name='incursionMediumInfestation', display='Incursion Medium Infestation'),
 11: Bundle(name='incursionHeavyInfestation', display='Incursion Heavy Infestation'),
 12: Bundle(name='incursionFinalEncounter', display='Incursion Final Encounter'),
 13: Bundle(name='incursionEndTale', display='Incursion End Tale'),
 100: Bundle(name='onionHeadquarters', display='Central System (Manager)'),
 101: Bundle(name='onionJump1', display='Systems 1 Jump Away'),
 102: Bundle(name='onionJump2', display='Systems 2 Jump Away'),
 103: Bundle(name='onionJump3', display='Systems 3 Jump Away'),
 104: Bundle(name='onionJump4', display='Systems 4 Jump Away'),
 105: Bundle(name='onionJump5', display='Systems 5 Jump Away'),
 106: Bundle(name='onionJump6', display='Systems 6 Jump Away'),
 107: Bundle(name='onionJump7', display='Systems 7 Jump Away'),
 108: Bundle(name='onionJump8', display='Systems 8 Jump Away'),
 109: Bundle(name='onionJump9', display='Systems 9 Jump Away'),
 110: Bundle(name='onionJump10', display='Systems 10 Jump Away'),
 1000001: Bundle(name='boss', display='Boss Spawn'),
 1000002: Bundle(name='endTale', display='End Tale'),
 1000003: Bundle(name='conditionalScene1', display='Conditional Scene 1'),
 1000004: Bundle(name='conditionalScene2', display='Conditional Scene 2'),
 1000005: Bundle(name='conditionalScene3', display='Conditional Scene 3'),
 2000001: Bundle(name='testscene1', display='Conditional Test Scene 1'),
 2000002: Bundle(name='testscene2', display='Conditional Test Scene 2'),
 2000003: Bundle(name='testscene3', display='Conditional Test Scene 3'),
 2000004: Bundle(name='testscene4', display='Conditional Test Scene 4'),
 2000005: Bundle(name='testscene5', display='Conditional Test Scene 5'),
 5000001: Bundle(name='managerInit', display='Initialize Manager ')}
SCENE_DISPLAY_NAME_BY_SCENE_ID = dict([ (scene_id, data.display) for scene_id, data in sceneTypesByID.iteritems() ])
for _constID, _constNames in sceneTypesByID.iteritems():
    setattr(scenesTypes, _constNames.name, _constID)
