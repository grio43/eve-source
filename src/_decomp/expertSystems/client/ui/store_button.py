#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\expertSystems\client\ui\store_button.py
from carbonui.control.button import Button
from localization import GetByLabel
from expertSystems.client.util import browse_expert_systems

class ViewExpertSystemInStoreButton(Button):
    default_label = GetByLabel('UI/InfoWindow/ViewExpertSystemInStore')

    def __init__(self, expert_system_type_id, **kwargs):
        self._expert_system_type_id = expert_system_type_id
        super(ViewExpertSystemInStoreButton, self).__init__(**kwargs)

    def OnClick(self, *args):
        browse_expert_systems(self._expert_system_type_id)
