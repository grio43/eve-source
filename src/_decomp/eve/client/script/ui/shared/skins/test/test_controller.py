#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\skins\test\test_controller.py
import __builtin__
import contextlib
import mock
import unittest
import signals
from testhelpers.evemocks import SMMock
from testsuites.testcases import ClientTestCase

class MockSkin(object):

    def __init__(self, materialID, skinID = None, licensed = False):
        self.materialID = materialID
        self.skinID = skinID
        self.licensed = licensed

    @property
    def material(self):
        return str(self.materialID)

    def __eq__(self, other):
        if other is None:
            return False
        return self.materialID == other.materialID and self.skinID == other.skinID and self.licensed == other.licensed

    def __repr__(self):
        return '<MockSkin materialID=%s skinID=%s licensed=%s>' % (self.materialID, self.skinID, self.licensed)


class MockFittingController(object):

    def __init__(self, itemID, typeID):
        self.itemID = itemID
        self.typeID = typeID
        self.on_new_itemID = signals.Signal(signalName='on_new_itemID')
        self.material = None

    def GetItemID(self):
        return self.itemID

    def GetTypeID(self):
        return self.typeID

    def UpdateItem(self, itemID, typeID):
        oldItemID = self.itemID
        oldTypeID = self.typeID
        self.itemID = itemID
        self.typeID = typeID
        self.on_new_itemID(self.itemID, oldItemID, self.typeID, oldTypeID)

    def SetSkinMaterial(self, material):
        self.material = material


class MockLock(object):

    def __init__(self, lock):
        self._lock = lock

    def __enter__(self):
        self._lock.acquire()

    def __exit__(self, ex_type, ex_value, traceback):
        self._lock.release()
        return ex_type is None

    @property
    def acquire(self):
        return self._lock.acquire

    @property
    def release(self):
        return self._lock.release


TYPE_ID = 1
OTHER_TYPE_ID = 2
SKIN_ID = 10
SKIN = MockSkin(materialID=1)
OTHER_SKIN = MockSkin(materialID=2)
LICENSED_SKIN = MockSkin(materialID=1, skinID=20, licensed=True)
OTHER_LICENSED_SKIN = MockSkin(materialID=2, skinID=30, licensed=True)
UNLICENSED_SKIN = MockSkin(materialID=3, licensed=False)
OTHER_UNLICENSED_SKIN = MockSkin(materialID=4, licensed=False)
ITEM_ID = 100
OTHER_ITEM_ID = 200

class SkinPanelControllerBase(ClientTestCase):

    @classmethod
    def setUpClass(cls):
        super(SkinPanelControllerBase, cls).setUpClass()
        cls.locks_module = mock.Mock()
        mock_modules = {'uthread': mock.Mock(),
         'locks': cls.locks_module,
         'trinity': mock.Mock()}
        cls.import_patcher = mock.patch.dict('sys.modules', mock_modules)
        cls.import_patcher.start()
        from eve.client.script.ui.shared.skins import controller
        cls.module = controller

    @classmethod
    def tearDownClass(cls):
        super(SkinPanelControllerBase, cls).tearDownClass()
        cls.import_patcher.stop()

    def setUp(self):
        super(SkinPanelControllerBase, self).setUp()
        self.lock = MockLock(mock.MagicMock())
        self.locks_module.Lock.return_value = self.lock

    def prime_skins_cache(self, cached = None, fresh = None):
        cached = cached or []
        fresh = fresh or []
        self.adapter.GetSkins.return_value = cached
        self.controller.skins
        self.adapter.GetSkins.return_value = fresh

    def assertSkinState(self, applied = None, pending = None, previewed = None):
        if applied is None:
            self.assertIsNone(self.controller.applied)
        else:
            self.assertEqual(self.controller.applied, applied)
        if pending is None:
            self.assertIsNone(self.controller.pending)
        else:
            self.assertEqual(self.controller.pending, pending)
        if previewed is None:
            self.assertIsNone(self.controller.previewed)
        else:
            self.assertEqual(self.controller.previewed, previewed)

    @contextlib.contextmanager
    def assertLockedTransaction(self):
        self.lock.acquire.reset_mock()
        self.lock.release.reset_mock()
        try:
            yield
        finally:
            self.lock.acquire.assert_called_once_with()
            self.lock.release.assert_called_once_with()

    @contextlib.contextmanager
    def assertNotLockedTransaction(self):
        self.lock.acquire.reset_mock()
        self.lock.release.reset_mock()
        try:
            yield
        finally:
            self.assertFalse(self.lock.acquire.called)
            self.assertFalse(self.lock.release.called)


class TestSkinPanelController(SkinPanelControllerBase):
    SKIN_LIST = [SKIN, OTHER_SKIN]

    def setUp(self):
        super(TestSkinPanelController, self).setUp()
        self.adapter = mock.Mock(spec=self.module.SkinPanelAdapter)
        self.adapter.GetSkins.return_value = self.SKIN_LIST
        self.adapter.GetTypesForSkin.return_value = [TYPE_ID]
        __builtin__.sm = SMMock()
        self.controller = self.module.SkinPanelController(adapter=self.adapter, hullTypeID=TYPE_ID)
        self.events = mock.Mock()
        self.controller.onChange.connect(self.events.onChange)
        self.controller.onSkinsChange.connect(self.events.onSkinsChange)

    def test_initial_state(self):
        self.assertEqual(self.controller.typeID, TYPE_ID)
        self.assertSkinState(applied=None, previewed=None, pending=None)

    @unittest.skip('test is failing and needs fixing')
    def test_change_type(self):
        with self.assertLockedTransaction():
            self.controller.typeID = OTHER_TYPE_ID
        self.events.onChange.assert_called_once_with()
        self.events.onSkinsChange.assert_called_once_with()
        self.assertEqual(self.controller.typeID, OTHER_TYPE_ID)
        self.assertSkinState(applied=None, previewed=None, pending=None)

    @unittest.skip('test is failing and needs fixing')
    def test_pick_skin(self):
        with self.assertLockedTransaction():
            self.controller.PickSkin(SKIN)
        self.events.onChange.assert_called_once_with()
        self.assertSkinState(previewed=SKIN)

    def test_change_type_resets_picked_skin(self):
        self.controller.PickSkin(SKIN)
        self.controller.typeID = OTHER_TYPE_ID
        self.assertSkinState(applied=None, previewed=None, pending=None)

    def test_pick_same_skin_again(self):
        self.controller.PickSkin(SKIN)
        self.controller.PickSkin(SKIN)
        self.assertSkinState(applied=None, previewed=None, pending=None)

    def test_pick_none_skin_after_another_skin(self):
        self.controller.PickSkin(SKIN)
        self.controller.PickSkin(None)
        self.assertSkinState(applied=None, previewed=None, pending=None)

    def test_pick_another_skin(self):
        self.controller.PickSkin(SKIN)
        self.controller.PickSkin(OTHER_SKIN)
        self.assertSkinState(previewed=OTHER_SKIN)

    def test_change_type_with_picked_skin(self):
        self.controller.PickSkin(SKIN)
        self.controller.typeID = OTHER_TYPE_ID
        self.assertEqual(self.controller.typeID, OTHER_TYPE_ID)
        self.assertSkinState(previewed=None)

    def test_get_skins(self):
        self.adapter.GetSkins.return_value = self.SKIN_LIST
        skins = self.controller.skins
        self.assertItemsEqual(skins, self.SKIN_LIST)

    def test_skins_are_cached(self):
        self.prime_skins_cache(cached=self.SKIN_LIST)
        with self.assertNotLockedTransaction():
            skins = self.controller.skins
        self.assertItemsEqual(skins, self.SKIN_LIST)

    def test_changing_type_resets_skins_cache(self):
        self.prime_skins_cache(fresh=self.SKIN_LIST)
        self.controller.typeID = OTHER_TYPE_ID
        self.assertItemsEqual(self.controller.skins, self.SKIN_LIST)

    @unittest.skip('test is failing and needs fixing')
    def test_controller_registers_for_events(self):
        self.assertIn('OnSkinLicenseActivated', self.controller.__notifyevents__)
        self.adapter.RegisterNotify.assert_called_once_with(self.controller)

    @unittest.skip('test is failing and needs fixing')
    def test_skin_license_activated_event(self):
        with self.assertLockedTransaction():
            self.controller.OnSkinLicenseActivated(SKIN_ID)
        self.events.onChange.assert_called_once_with()
        self.events.onSkinsChange.assert_called_once_with()

    @unittest.skip('test is failing and needs fixing')
    def test_skins_cache_is_reset_on_license_activated_for_relevant_type(self):
        self.prime_skins_cache(fresh=self.SKIN_LIST)
        self.controller.OnSkinLicenseActivated(SKIN_ID)
        self.assertItemsEqual(self.controller.skins, self.SKIN_LIST)

    @unittest.skip('test is failing and needs fixing')
    def test_skins_cache_is_not_reset_on_license_activated_for_irrelevant_type(self):
        self.adapter.GetTypesForSkin.return_value = [OTHER_TYPE_ID]
        self.prime_skins_cache(cached=self.SKIN_LIST)
        self.controller.OnSkinLicenseActivated(SKIN_ID)
        self.assertItemsEqual(self.controller.skins, self.SKIN_LIST)

    @unittest.skip('test is failing and needs fixing')
    def test_license_activated_does_not_change_preview_state(self):
        self.controller.PickSkin(SKIN)
        self.adapter.GetSkins.return_value = [LICENSED_SKIN]
        self.events.onChange.reset_mock()
        self.controller.OnSkinLicenseActivated(LICENSED_SKIN.skinID)
        self.events.onChange.assert_called_once_with()
        self.events.onSkinsChange.assert_called_once_with()
        self.assertSkinState(previewed=LICENSED_SKIN)


if __name__ == '__main__':
    unittest.main()
