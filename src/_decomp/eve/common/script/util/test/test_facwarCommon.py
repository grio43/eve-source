#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\util\test\test_facwarCommon.py
import unittest
from appConst import factionAmarrEmpire, factionCaldariState, factionGallenteFederation, factionMinmatarRepublic, factionGuristasPirates, factionAngelCartel
from eve.common.script.util import facwarCommon
OCCUPIER_FACTIONS = (factionAmarrEmpire,
 factionCaldariState,
 factionGallenteFederation,
 factionMinmatarRepublic)
PIRATE_FACTIONS = (factionGuristasPirates, factionAngelCartel)

class OccupierTestCase(unittest.TestCase):

    def test_GetOccupierFWFactions(self):
        occupierFactions = facwarCommon.GetOccupierFWFactions()
        self.assertItemsEqual(OCCUPIER_FACTIONS, occupierFactions)

    def test_IsOccupierFWFaction(self):
        self.assertTrue(facwarCommon.IsOccupierFWFaction(factionAmarrEmpire))
        self.assertFalse(facwarCommon.IsOccupierFWFaction(factionGuristasPirates))

    def test_GetPirateFWFactions(self):
        pirateFactions = facwarCommon.GetPirateFWFactions()
        self.assertItemsEqual(PIRATE_FACTIONS, pirateFactions)

    def test_IsPirateFWFaction(self):
        self.assertTrue(facwarCommon.IsPirateFWFaction(factionGuristasPirates))
        self.assertFalse(facwarCommon.IsPirateFWFaction(factionAmarrEmpire))

    def test_GetAllFWFactions(self):
        allFWFactions = facwarCommon.GetAllFWFactions()
        self.assertItemsEqual(OCCUPIER_FACTIONS + PIRATE_FACTIONS, allFWFactions)

    def test_IsAnyFWFaction(self):
        self.assertTrue(facwarCommon.IsAnyFWFaction(factionAmarrEmpire))
        self.assertTrue(facwarCommon.IsAnyFWFaction(factionGuristasPirates))
        self.assertFalse(facwarCommon.IsAnyFWFaction(1234))

    def test_IsOccupierEnemyFaction(self):
        self.assertTrue(facwarCommon.IsOccupierEnemyFaction(factionAmarrEmpire, factionMinmatarRepublic))
        self.assertTrue(facwarCommon.IsOccupierEnemyFaction(factionMinmatarRepublic, factionAmarrEmpire))
        self.assertFalse(facwarCommon.IsOccupierEnemyFaction(factionCaldariState, factionMinmatarRepublic))
        self.assertFalse(facwarCommon.IsOccupierEnemyFaction(factionMinmatarRepublic, factionCaldariState))
        self.assertFalse(facwarCommon.IsOccupierEnemyFaction(factionCaldariState, factionGuristasPirates))
        self.assertFalse(facwarCommon.IsOccupierEnemyFaction(factionGuristasPirates, factionCaldariState))
        self.assertFalse(facwarCommon.IsOccupierEnemyFaction(factionMinmatarRepublic, factionGuristasPirates))
        self.assertFalse(facwarCommon.IsOccupierEnemyFaction(factionGuristasPirates, factionMinmatarRepublic))
        self.assertFalse(facwarCommon.IsOccupierEnemyFaction(factionAngelCartel, factionGuristasPirates))
        self.assertFalse(facwarCommon.IsOccupierEnemyFaction(factionGuristasPirates, factionAngelCartel))

    def test_IsInsurgencyEnemyFaction(self):
        self.assertFalse(facwarCommon.IsInsurgencyEnemyFaction(factionAmarrEmpire, factionMinmatarRepublic))
        self.assertFalse(facwarCommon.IsInsurgencyEnemyFaction(factionMinmatarRepublic, factionAmarrEmpire))
        self.assertFalse(facwarCommon.IsInsurgencyEnemyFaction(factionCaldariState, factionMinmatarRepublic))
        self.assertFalse(facwarCommon.IsInsurgencyEnemyFaction(factionMinmatarRepublic, factionCaldariState))
        self.assertTrue(facwarCommon.IsInsurgencyEnemyFaction(factionCaldariState, factionGuristasPirates))
        self.assertTrue(facwarCommon.IsInsurgencyEnemyFaction(factionGuristasPirates, factionCaldariState))
        self.assertFalse(facwarCommon.IsInsurgencyEnemyFaction(factionMinmatarRepublic, factionGuristasPirates))
        self.assertFalse(facwarCommon.IsInsurgencyEnemyFaction(factionGuristasPirates, factionMinmatarRepublic))
        self.assertFalse(facwarCommon.IsInsurgencyEnemyFaction(factionAngelCartel, factionGuristasPirates))
        self.assertFalse(facwarCommon.IsInsurgencyEnemyFaction(factionGuristasPirates, factionAngelCartel))

    def test_IsCombatEnemyFaction(self):
        self.assertTrue(facwarCommon.IsCombatEnemyFaction(factionAmarrEmpire, factionMinmatarRepublic))
        self.assertTrue(facwarCommon.IsCombatEnemyFaction(factionMinmatarRepublic, factionAmarrEmpire))
        self.assertFalse(facwarCommon.IsCombatEnemyFaction(factionCaldariState, factionMinmatarRepublic))
        self.assertFalse(facwarCommon.IsCombatEnemyFaction(factionMinmatarRepublic, factionCaldariState))
        self.assertTrue(facwarCommon.IsCombatEnemyFaction(factionCaldariState, factionGuristasPirates))
        self.assertTrue(facwarCommon.IsCombatEnemyFaction(factionGuristasPirates, factionCaldariState))
        self.assertFalse(facwarCommon.IsCombatEnemyFaction(factionMinmatarRepublic, factionGuristasPirates))
        self.assertFalse(facwarCommon.IsCombatEnemyFaction(factionGuristasPirates, factionMinmatarRepublic))
        self.assertFalse(facwarCommon.IsCombatEnemyFaction(factionAngelCartel, factionGuristasPirates))
        self.assertFalse(facwarCommon.IsCombatEnemyFaction(factionGuristasPirates, factionAngelCartel))

    def test_IsSameFwFaction(self):
        self.assertTrue(facwarCommon.IsSameFwFaction(factionAmarrEmpire, factionAmarrEmpire))
        self.assertTrue(facwarCommon.IsSameFwFaction(factionGuristasPirates, factionGuristasPirates))
        self.assertFalse(facwarCommon.IsSameFwFaction(factionAmarrEmpire, factionMinmatarRepublic))
        self.assertFalse(facwarCommon.IsSameFwFaction(factionAmarrEmpire, factionAngelCartel))
        self.assertFalse(facwarCommon.IsSameFwFaction(factionAmarrEmpire, None))
        self.assertFalse(facwarCommon.IsSameFwFaction(1234, 1234))
        self.assertFalse(facwarCommon.IsSameFwFaction(1234, None))

    def test_GetOccupationEnemyFaction(self):
        self.assertEqual(factionMinmatarRepublic, facwarCommon.GetOccupationEnemyFaction(factionAmarrEmpire))
        self.assertEqual(factionAmarrEmpire, facwarCommon.GetOccupationEnemyFaction(factionMinmatarRepublic))
        with self.assertRaises(RuntimeError):
            facwarCommon.GetOccupationEnemyFaction(factionAngelCartel)
        with self.assertRaises(RuntimeError):
            facwarCommon.GetOccupationEnemyFaction(1234)

    def test_GetCombatEnemyFactions(self):
        self.assertItemsEqual([factionMinmatarRepublic, factionAngelCartel], facwarCommon.GetCombatEnemyFactions(factionAmarrEmpire))
        self.assertItemsEqual([factionAmarrEmpire, factionAngelCartel], facwarCommon.GetCombatEnemyFactions(factionMinmatarRepublic))
        self.assertItemsEqual([factionAmarrEmpire, factionMinmatarRepublic], facwarCommon.GetCombatEnemyFactions(factionAngelCartel))

    def test_GetInsurgencyEnemyFactions(self):
        self.assertItemsEqual([factionAngelCartel], facwarCommon.GetInsurgencyEnemyFactions(factionAmarrEmpire))
        self.assertItemsEqual([factionAngelCartel], facwarCommon.GetInsurgencyEnemyFactions(factionMinmatarRepublic))
        self.assertItemsEqual([factionAmarrEmpire, factionMinmatarRepublic], facwarCommon.GetInsurgencyEnemyFactions(factionAngelCartel))
