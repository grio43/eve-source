#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\assetholding\client\assetholding_svc.py
import logging
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceConst import ROLE_QA
logger = logging.getLogger(__name__)

class AssetHoldingService(Service):
    __guid__ = 'svc.assetHoldingSvc'

    def __init__(self):
        self._remote_inventory = None
        self._is_item_failure_enabled = None
        self._is_item_validation_enabled = None
        super(AssetHoldingService, self).__init__()

    @property
    def remote_inventory(self):
        if self._remote_inventory is None:
            self._remote_inventory = sm.RemoteSvc('inventoryAssetHoldingMgr')
        return self._remote_inventory

    @property
    def is_item_failure_enabled(self):
        is_qa = bool(session.role & ROLE_QA)
        if not is_qa:
            return False
        if self._is_item_failure_enabled is None:
            self._is_item_failure_enabled = self.remote_inventory.is_item_failure_enabled()
        return self._is_item_failure_enabled

    def toggle_item_failure(self):
        is_qa = bool(session.role & ROLE_QA)
        if not is_qa:
            return
        should_enable_item_failure = not self.is_item_failure_enabled
        self.remote_inventory.set_item_failure_enabled(should_enable_item_failure)
        self._is_item_failure_enabled = should_enable_item_failure

    @property
    def is_item_validation_enabled(self):
        is_qa = bool(session.role & ROLE_QA)
        if not is_qa:
            return True
        if self._is_item_validation_enabled is None:
            self._is_item_validation_enabled = self.remote_inventory.is_item_validation_enabled()
        return self._is_item_validation_enabled

    def toggle_item_validation(self):
        is_qa = bool(session.role & ROLE_QA)
        if not is_qa:
            return
        should_enable_item_validation = not self.is_item_validation_enabled
        self.remote_inventory.set_item_validation_enabled(should_enable_item_validation)
        self._is_item_validation_enabled = should_enable_item_validation
