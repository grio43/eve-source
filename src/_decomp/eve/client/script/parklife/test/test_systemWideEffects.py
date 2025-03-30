#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\test\test_systemWideEffects.py
from eve.client.script.parklife.systemWideEffects import SystemWideEffects
from testsuites.testcases import ClientTestCase

class SystemWideEffectsTestCase(ClientTestCase):

    def test_single_system_effect_started(self):
        me = SystemWideEffects()
        me.OnSystemWideEffectStart(1, 1000, 20)
        self.assertEqual(me.GetSystemWideEffectsOnShip(), {(1000, 20): {1}})

    def test_multiple_system_effects_with_same_type_and_effect(self):
        me = SystemWideEffects()
        me.OnSystemWideEffectStart(1, 1000, 20)
        me.OnSystemWideEffectStart(2, 1001, 20)
        self.assertEqual(me.GetSystemWideEffectsOnShip(), {(1000, 20): {1},
         (1001, 20): {2}})

    def test_single_system_effect_started_and_stoped(self):
        me = SystemWideEffects()
        me.OnSystemWideEffectStart(1, 1000, 20)
        me.OnSystemWideEffectStop(1, 1000, 20)
        self.assertEqual(me.GetSystemWideEffectsOnShip(), {})

    def test_system_effects_updated(self):
        me = SystemWideEffects()
        me.OnSystemWideEffectStart(1, 1000, 20)
        me.OnSystemWideEffectStart(2, 2000, 30)
        me.OnUpdateSystemWideEffectInfo({(3000, 40): {3},
         (3001, 20): {2}})
        self.assertEqual(me.GetSystemWideEffectsOnShip(), {(3000, 40): {3},
         (3001, 20): {2}})
