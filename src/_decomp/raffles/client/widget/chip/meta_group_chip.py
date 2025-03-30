#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\widget\chip\meta_group_chip.py
from fsdBuiltData.common.iconIDs import GetIconFile
import metaGroups
import eveui
from .chip import Chip

class MetaGroupChip(Chip):
    default_name = 'MetaGroupChip'

    def __init__(self, meta_group_id = None, **kwargs):
        super(MetaGroupChip, self).__init__(**kwargs)
        self.icon = eveui.Sprite(parent=self, align=eveui.Align.center_left, width=24, height=24, opacity=0.3, top=-2)
        self._meta_group_id = None
        if meta_group_id:
            self.meta_group_id = meta_group_id

    @property
    def meta_group_id(self):
        return self._meta_group_id

    @meta_group_id.setter
    def meta_group_id(self, meta_group_id):
        if self._meta_group_id == meta_group_id:
            return
        self._meta_group_id = meta_group_id
        if meta_group_id:
            self.icon.SetTexturePath(GetIconFile(metaGroups.get_icon_id(meta_group_id)))
            self.text = metaGroups.get_name(meta_group_id)
        else:
            self.clear()
