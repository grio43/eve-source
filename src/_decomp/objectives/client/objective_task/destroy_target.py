#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\objectives\client\objective_task\destroy_target.py
from objectives.client.objective_task.target import TargetTask, TargetsTask, TargetsTaskGroup
from objectives.client.ui.objective_task_widget import EnemyTargetWidget

class DestroyTargetTask(TargetTask):
    WIDGET = EnemyTargetWidget

    def __init__(self, **kwargs):
        self._damage_state = None
        super(DestroyTargetTask, self).__init__(**kwargs)

    def _slim_item_initialized(self):
        super(DestroyTargetTask, self)._slim_item_initialized()
        ballpark = sm.GetService('michelle').GetBallpark()
        self.damage_state = ballpark.GetDamageState(self.item_id)

    @property
    def damage_state(self):
        return self._damage_state

    @damage_state.setter
    def damage_state(self, value):
        if value == self._damage_state:
            return
        self._damage_state = value
        self.update()
        self._update_complete_state()

    def _update_complete_state(self):
        if not self._damage_state:
            self.completed = False
            return
        shield, armor, hull, _, _ = self._damage_state
        self.completed = hull == 0


class DestroyTargetsTask(TargetsTask):
    objective_task_content_id = 52
    TASK = DestroyTargetTask
    __notifyevents__ = TargetsTask.__notifyevents__ + ['OnDamageStateChange', 'OnObjectExplode']

    def OnObjectExplode(self, type_id, item_id):
        if item_id in self.tasks:
            self.tasks[item_id].damage_state = (0, 0, 0, 0, 0)

    def OnDamageStateChange(self, ship_id, damage_state):
        if ship_id not in self.tasks:
            return
        self.tasks[ship_id].damage_state = damage_state


class DestroyTargetTaskGroup(TargetsTaskGroup):
    objective_task_content_id = 5
    TASK = DestroyTargetTask
    __notifyevents__ = ['OnDamageStateChange', 'OnObjectExplode', 'DoBallRemove']

    def OnObjectExplode(self, type_id, item_id):
        task = self._get_task_by_item_id(item_id)
        if task:
            task.damage_state = (0, 0, 0, 0, 0)

    def OnDamageStateChange(self, ship_id, damage_state):
        task = self._get_task_by_item_id(ship_id)
        if task:
            task.damage_state = damage_state

    def DoBallRemove(self, ball, *args, **kwargs):
        if ball:
            self.OnObjectExplode(None, ball.id)


class DestroyDungeonObjects(DestroyTargetTaskGroup):
    objective_task_content_id = 40
    KEY = 'dungeon_object_ids'

    def __init__(self, dungeon_object_ids = None, **kwargs):
        super(DestroyDungeonObjects, self).__init__(targets=dungeon_object_ids, **kwargs)

    def _update_targets(self, targets):
        if targets is None:
            targets = []
        elif not isinstance(targets, list):
            targets = [targets]
        targets = [ {'dungeon_object_id': target} for target in targets ]
        super(DestroyDungeonObjects, self)._update_targets(targets)


class DestroyEntityGroups(DestroyTargetTaskGroup):
    objective_task_content_id = 41
    __notifyevents__ = DestroyTargetTaskGroup.__notifyevents__ + ['OnBallAdded']

    def __init__(self, entity_group_ids = None, **kwargs):
        self._entity_group_ids = entity_group_ids
        super(DestroyEntityGroups, self).__init__(**kwargs)

    @property
    def entity_group_ids(self):
        return self._entity_group_ids

    @entity_group_ids.setter
    def entity_group_ids(self, value):
        if self._entity_group_ids == value:
            return
        if value and not isinstance(value, list):
            self._entity_group_ids = [value]
        else:
            self._entity_group_ids = value or []
        self._find_targets()

    def OnBallAdded(self, slim_item):
        if slim_item.entityGroupID in self._entity_group_ids:
            self._add_target(slim_item, start_task=True)

    def _start(self):
        super(DestroyEntityGroups, self)._start()
        self._find_targets()

    def _find_targets(self):
        if not self.is_active:
            return
        from nodegraph.client.getters.object import GetSlimItems
        targets = []
        for entity_group_id in self._entity_group_ids:
            result = GetSlimItems(entity_group_id=entity_group_id).get_values()
            if result:
                targets.extend(result.get('slim_items', []))

        self._update_targets(targets)


class DestroyTypes(DestroyTargetTaskGroup):
    objective_task_content_id = 48
    __notifyevents__ = DestroyTargetTaskGroup.__notifyevents__ + ['OnBallAdded']

    def __init__(self, type_ids = None, **kwargs):
        self._type_ids = type_ids
        super(DestroyTypes, self).__init__(**kwargs)

    @property
    def type_ids(self):
        return self._type_ids

    @type_ids.setter
    def type_ids(self, value):
        if self._type_ids == value:
            return
        if value and not isinstance(value, list):
            self._type_ids = [value]
        else:
            self._type_ids = value or []
        self._find_targets()

    def OnBallAdded(self, slim_item):
        if slim_item.typeID in self._type_ids:
            self._add_target(slim_item, start_task=True)

    def _start(self):
        super(DestroyTypes, self)._start()
        self._find_targets()

    def _find_targets(self):
        if not self.is_active:
            return
        from nodegraph.client.getters.object import GetSlimItems
        targets = []
        for type_id in self._type_ids:
            result = GetSlimItems(type_id=type_id).get_values()
            if result:
                targets.extend(result.get('slim_items', []))

        self._update_targets(targets)
