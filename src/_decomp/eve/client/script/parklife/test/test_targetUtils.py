#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\test\test_targetUtils.py
from collections import namedtuple
from eve.client.script.parklife.targetUtils import get_closest_entity_target
from mock import Mock
from testhelpers.evemocks import SMMock
import unittest
from testsuites.testcases import ClientTestCase
EntityMock = namedtuple('Entity', 'itemID groupID')
MOCK_GROUP_DRIFTER = 1310
MOCK_GROUP_SEEKER = 1768
MOCK_GROUP_SOMETHING_ELSE = 12345

class MichelleMock(object):

    def __init__(self):
        self.ballpark = Mock()
        self.SetEntitiesInRange(entities=[])

    def InWarp(self):
        return False

    def GetBallpark(self):
        return self.ballpark

    def SetEntitiesInRange(self, entities):
        self.ballpark.GetItemsAndDistanceByCategory = Mock(return_value=entities)


class TestGetClosestEntityTarget(ClientTestCase):

    def setUp(self):
        super(TestGetClosestEntityTarget, self).setUp()
        self.michelle_mock = MichelleMock()
        import __builtin__
        __builtin__.sm = SMMock(services={'michelle': self.michelle_mock})

    def test_returns_none_if_no_entities_in_range(self):
        self.assertIsNone(get_closest_entity_target())

    def test_returns_closest_entity_if_no_priorities_defined(self):
        self.michelle_mock.SetEntitiesInRange([(2000, EntityMock(1, MOCK_GROUP_DRIFTER)), (1000, EntityMock(2, MOCK_GROUP_SEEKER))])
        self.assertEqual(get_closest_entity_target(), 2)

    def test_returns_closest_drifter_if_drifters_prioritized(self):
        self.michelle_mock.SetEntitiesInRange([(2000, EntityMock(1, MOCK_GROUP_DRIFTER)), (1000, EntityMock(2, MOCK_GROUP_SEEKER))])
        target_priority = [MOCK_GROUP_DRIFTER, MOCK_GROUP_SEEKER]
        self.assertEqual(get_closest_entity_target(target_priority), 1)

    def test_ignores_items_not_listed_in_priorities(self):
        self.michelle_mock.SetEntitiesInRange([(100, EntityMock(0, MOCK_GROUP_SOMETHING_ELSE)), (2000, EntityMock(1, MOCK_GROUP_DRIFTER)), (1000, EntityMock(2, MOCK_GROUP_SEEKER))])
        target_priority = [MOCK_GROUP_DRIFTER, MOCK_GROUP_SEEKER]
        self.assertEqual(get_closest_entity_target(target_priority), 1)

    def test_ignores_priorities_when_not_found(self):
        self.michelle_mock.SetEntitiesInRange([(100, EntityMock(0, MOCK_GROUP_SOMETHING_ELSE)), (1000, EntityMock(2, MOCK_GROUP_SEEKER))])
        target_priority = [MOCK_GROUP_DRIFTER, MOCK_GROUP_SEEKER]
        self.assertEqual(get_closest_entity_target(target_priority), 2)


if __name__ == '__main__':
    unittest.main()
