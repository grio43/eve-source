#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\objectives\client\ui\objective_chain.py
import eveui
from .objective import ObjectiveEntry

class ObjectiveChainEntry(eveui.ContainerAutoSize):
    default_align = eveui.Align.to_top
    default_alignMode = eveui.Align.to_top

    def __init__(self, objective_chain, *args, **kwargs):
        kwargs.setdefault('name', 'objective_chain_{}'.format(objective_chain.content_id))
        super(ObjectiveChainEntry, self).__init__(*args, **kwargs)
        self.objective_chain = objective_chain
        self.objective_chain.context.subscribe_to_message('on_objectives_changed', self._objectives_changed)
        self._objective_entries = {}
        self._objectives_changed()

    def Close(self):
        if self.objective_chain:
            self.objective_chain.context.unsubscribe_from_message('on_objectives_changed', self._objectives_changed)
        super(ObjectiveChainEntry, self).Close()
        self._objective_entries.clear()
        self.objective_chain = None

    def _objectives_changed(self, **kwargs):
        for objective_id in self._objective_entries.keys():
            if objective_id not in self.objective_chain.objectives:
                entry = self._objective_entries.pop(objective_id)
                entry.close()

        index = 0
        sorted_objectives = sorted(self.objective_chain.objectives.values(), key=lambda x: x.rendering_order)
        for objective in sorted_objectives:
            if objective.objective_id not in self._objective_entries:
                entry = ObjectiveEntry(parent=self, objective=objective, padTop=4, idx=index)
                self._objective_entries[objective.objective_id] = entry
            index += 1
