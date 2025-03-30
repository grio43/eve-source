#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\view\aurumstore\specialNeocomButton.py
import launchdarkly
from eve.client.script.ui.shared.neocom.neocom import neocomConst
from eve.client.script.ui.shared.neocom.neocom.btnData.btnDataNode import BtnDataNode
from eve.client.script.ui.shared.neocom.neocom.fixedButtonExtension import FixedButtonExtension
FEATURE_FLAG_KEY = 'eve-new-eden-store-shortcut-in-neocom'
FEATURE_FLAG_FALLBACK = True

class AurumStoreNeocomButtonExtension(FixedButtonExtension):

    def __init__(self):
        self._available = FEATURE_FLAG_FALLBACK
        launchdarkly.get_client().notify_flag(FEATURE_FLAG_KEY, FEATURE_FLAG_FALLBACK, self._refresh_feature_flag)

    def _refresh_feature_flag(self, ld_client, flag_key, flag_fallback, flag_deleted):
        self._available = ld_client.get_bool_variation(feature_key=flag_key, fallback=flag_fallback)
        self.on_visible_changed(self)

    @property
    def is_visible(self):
        return self._available

    def create_button_data(self, parent):
        return AurumStoreButtonDataNode(parent)


class AurumStoreButtonDataNode(BtnDataNode):

    def __init__(self, parent):
        BtnDataNode.__init__(self, parent=parent, btnType=neocomConst.BTNTYPE_CMD, iconPath='res:/ui/texture/WindowIcons/NES.png', cmdName='ToggleAurumStore', btnID='AurumStoreBtnDataNode', isRemovable=False)
