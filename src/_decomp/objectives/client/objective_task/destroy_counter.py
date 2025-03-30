#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\objectives\client\objective_task\destroy_counter.py
import evetypes
import uthread2
import eveformat
from npcs.client.entitystandings import is_hostile_npc_target
from inventorycommon.const import categoryEntity
import eve.client.script.ui.eveColor as color
from objectives.client.objective_task.base import ObjectiveTask
from objectives.client.ui.objective_task_widget import ProgressBarTaskWidget
from objectives.common.util import value_as_set
import logging
logger = logging.getLogger(__name__)

class _DestroyTargetsCounterTask(ObjectiveTask):
    objective_task_content_id = None
    WIDGET = ProgressBarTaskWidget
    __notifyevents__ = ['OnDamageStateChange',
     'OnObjectExplode',
     'DoBallRemove',
     'OnBallAdded']

    def __init__(self, *args, **kwargs):
        self._targets = set()
        self._destroyed_targets = set()
        super(_DestroyTargetsCounterTask, self).__init__(hidden=True, *args, **kwargs)

    @property
    def progress_bar_color(self):
        return color.DANGER_RED

    @property
    def progress_bar_color_completed(self):
        return color.DANGER_RED

    @property
    def progress(self):
        goal_value = self.goal_value
        if not goal_value:
            return 0
        return self.current_value / float(goal_value)

    @property
    def goal_value(self):
        return len(self._targets)

    @property
    def current_value(self):
        return len(self._targets) - len(self._destroyed_targets)

    @property
    def value(self):
        if not self._targets:
            return ''
        return u'{}/{}'.format(eveformat.number(self.current_value, 0), eveformat.number(self.goal_value, 0))

    def OnBallAdded(self, slim_item):
        if self._validate_target(slim_item):
            self._add_target(slim_item)

    def OnObjectExplode(self, type_id, item_id):
        if item_id in self._targets:
            self._target_destroyed(item_id)

    def OnDamageStateChange(self, ship_id, damage_state):
        if ship_id not in self._targets:
            return
        _, _, hull, _, _ = damage_state
        if hull == 0:
            self._target_destroyed(ship_id)

    def DoBallRemove(self, ball, *args, **kwargs):
        if ball and ball.id in self._targets:
            self._target_destroyed(ball.id)

    def _update(self):
        super(_DestroyTargetsCounterTask, self)._update()
        self.completed = bool(self._targets) and self.current_value == 0
        self.hidden = not bool(self._targets)

    def start(self):
        self._targets.clear()
        self._destroyed_targets.clear()
        if self._is_active:
            self.update()
        else:
            super(_DestroyTargetsCounterTask, self).start()

    def _start(self):
        self._find_targets()
        super(_DestroyTargetsCounterTask, self)._start()

    def _find_targets(self):
        ballpark = sm.GetService('michelle').GetBallpark()
        if not ballpark:
            return
        for ball_id in ballpark.balls.iterkeys():
            if ball_id == session.shipid:
                continue
            slim_item = ballpark.GetInvItem(ball_id)
            if slim_item and self._validate_target(slim_item):
                self._add_target(slim_item)

    def _validate_target(self, slim_item):
        return False

    def _add_target(self, slim_item):
        self._targets.add(slim_item.itemID)
        self.update()

    def _target_destroyed(self, item_id):
        self._destroyed_targets.add(item_id)
        self.update()


class DestroyHostileTargetsTask(_DestroyTargetsCounterTask):
    objective_task_content_id = 14

    def _validate_target(self, slim_item):
        if getattr(slim_item, 'categoryID', None) != categoryEntity:
            return False
        return is_hostile_npc_target(slim_item)


class DestroyTargetsCounterTask(_DestroyTargetsCounterTask):
    objective_task_content_id = 45

    def __init__(self, objective_target_groups = None, type_ids = None, group_ids = None, entity_group_ids = None, type_list_id = None, *args, **kwargs):
        self._objective_target_groups = value_as_set(objective_target_groups)
        self._type_ids = value_as_set(type_ids)
        self._group_ids = value_as_set(group_ids)
        self._entity_group_ids = value_as_set(entity_group_ids)
        self._type_list_id = None
        self._type_ids_from_type_list = set()
        if type_list_id:
            self._update_type_list()
        super(DestroyTargetsCounterTask, self).__init__(*args, **kwargs)

    @property
    def objective_target_groups(self):
        return self._objective_target_groups

    @objective_target_groups.setter
    def objective_target_groups(self, value):
        if self._objective_target_groups == value:
            return
        self._objective_target_groups = value_as_set(value)
        self._parameter_updated()

    @property
    def type_ids(self):
        return self._type_ids

    @type_ids.setter
    def type_ids(self, value):
        if self._type_ids == value:
            return
        self._type_ids = value_as_set(value)
        self._parameter_updated()

    @property
    def group_ids(self):
        return self._group_ids

    @group_ids.setter
    def group_ids(self, value):
        if self._group_ids == value:
            return
        self._group_ids = value_as_set(value)
        self._parameter_updated()

    @property
    def entity_group_ids(self):
        return self._entity_group_ids

    @entity_group_ids.setter
    def entity_group_ids(self, value):
        if self._entity_group_ids == value:
            return
        self._entity_group_ids = value_as_set(value)
        self._parameter_updated()

    @property
    def type_list_id(self):
        return self._type_list_id

    @type_list_id.setter
    def type_list_id(self, value):
        if self._type_list_id == value:
            return
        self._type_list_id = value
        self._update_type_list()
        self._parameter_updated()

    def _update_type_list(self):
        if not self._type_list_id:
            self._type_ids_from_type_list.clear()
        else:
            try:
                type_ids = evetypes.GetTypeIDsByListID(self._type_list_id)
            except StandardError as e:
                logger.exception('%s: Failed to get type list', self.__class__.__name__)
                return

            self._type_ids_from_type_list = set(type_ids)

    @uthread2.debounce(0.1)
    def _parameter_updated(self):
        self._targets.clear()
        self._destroyed_targets.clear()
        if self.is_active:
            self._find_targets()
            self.update()

    def _validate_target(self, slim_item):
        slim_type_id = getattr(slim_item, 'typeID', None)
        if self._objective_target_groups and getattr(slim_item, 'objectiveTargetGroup', None) in self._objective_target_groups:
            return True
        if self._type_ids and slim_type_id in self._type_ids:
            return True
        if self._type_ids_from_type_list and slim_type_id in self._type_ids_from_type_list:
            return True
        if self._group_ids and getattr(slim_item, 'groupID', None) in self._group_ids:
            return True
        if self._entity_group_ids and getattr(slim_item, 'entityGroupID', None) in self._entity_group_ids:
            return True
        return False
