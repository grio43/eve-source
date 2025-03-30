#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\widget\meta_group_combo.py
import eveui
import metaGroups
from raffles.client.localization import Text

class MetaGroupCombo(eveui.Combo):

    def __init__(self, **kwargs):
        meta_group_options = sorted(((meta_group.name, meta_group.id) for meta_group in metaGroups.iter_meta_groups()))
        meta_group_options.insert(0, (Text.all_meta_groups(), None))
        super(MetaGroupCombo, self).__init__(options=meta_group_options, **kwargs)

    def clear(self):
        self.SelectItemByIndex(0)
        if self.OnChange:
            self.OnChange(self, self.GetKey(), self.GetValue())
