#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\actions\overview.py
from nodegraph.client.util import get_item_name
from .base import Action

class BlockOverview(Action):
    atom_id = 425

    def start(self, **kwargs):
        super(BlockOverview, self).start(**kwargs)
        sm.GetService('overviewPresetSvc').BlockOverview()


class UnblockOverview(Action):
    atom_id = 426

    def start(self, **kwargs):
        super(UnblockOverview, self).start(**kwargs)
        sm.GetService('overviewPresetSvc').UnblockOverview()


class AddOverviewOverride(Action):
    atom_id = 462

    def __init__(self, should_display = None, type_id = None, group_id = None, category_id = None, **kwargs):
        super(AddOverviewOverride, self).__init__(**kwargs)
        self.should_display = self.get_atom_parameter_value('should_display', should_display)
        self.type_id = type_id
        self.group_id = group_id
        self.category_id = category_id

    def start(self, **kwargs):
        super(AddOverviewOverride, self).start(**kwargs)
        sm.GetService('overviewPresetSvc').overviewOverride.add(self.should_display, type_id=self.type_id, group_id=self.group_id, category_id=self.category_id)

    def stop(self):
        super(AddOverviewOverride, self).stop()
        sm.GetService('overviewPresetSvc').overviewOverride.remove(type_id=self.type_id, group_id=self.group_id, category_id=self.category_id)

    @classmethod
    def get_subtitle(cls, **kwargs):
        return get_item_name(**kwargs)


class RemoveOverviewOverride(Action):
    atom_id = 463

    def __init__(self, type_id = None, group_id = None, category_id = None, **kwargs):
        super(RemoveOverviewOverride, self).__init__(**kwargs)
        self.type_id = type_id
        self.group_id = group_id
        self.category_id = category_id

    def start(self, **kwargs):
        super(RemoveOverviewOverride, self).start(**kwargs)
        sm.GetService('overviewPresetSvc').overviewOverride.remove(type_id=self.type_id, group_id=self.group_id, category_id=self.category_id)

    @classmethod
    def get_subtitle(cls, **kwargs):
        return get_item_name(**kwargs)
