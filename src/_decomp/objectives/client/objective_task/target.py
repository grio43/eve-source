#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\objectives\client\objective_task\target.py
import evetypes
import localization
import logging
import threadutils
import uthread2
from carbon.common.script.util.format import FmtDist
from carbonui.uicore import uicore
import eve.client.script.parklife.states as states
import log
from objectives.client.objective_task.base import ObjectiveTask, ObjectiveTaskGroup
from objectives.client.objective_task.generic import ProgressTask, ValueRangeTask
from objectives.client.ui.objective_task_widget import ProgressBarTaskWidget
from objectives.common.util import value_as_set
logger = logging.getLogger('objectives')

class TargetTask(ObjectiveTask):
    objective_task_content_id = 24

    def __init__(self, target = None, **kwargs):
        self._slim_item = None
        self._target = None
        self._slim_item_tasklet = None
        self._use_custom_title = bool(kwargs.get('title'))
        super(TargetTask, self).__init__(hidden=(not self._use_custom_title), **kwargs)
        self.target = target

    def get_values(self):
        result = super(TargetTask, self).get_values()
        result['slim_item'] = self._slim_item
        result['item_id'] = self.item_id
        result['type_id'] = self.type_id
        result['dungeon_object_id'] = self.dungeon_object_id
        return result

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, value):
        if self._target == value:
            return
        self._target = value
        self._slim_item = None
        if isinstance(self._target, dict):
            if self.type_id:
                self._set_target_title(evetypes.GetName(self.type_id))
                self.update()
        else:
            self._slim_item = self._target
        if self._slim_item_tasklet:
            self._slim_item_tasklet.kill()
        if self._target:
            self._slim_item_tasklet = uthread2.start_tasklet(self._initialize_slim_item)

    @property
    def item_id(self):
        if self._slim_item:
            return self._slim_item.itemID
        if self._target:
            return self._target.get('item_id', None)

    @property
    def type_id(self):
        if self._slim_item:
            return self._slim_item.typeID
        if self._target:
            return self._target.get('type_id', None)

    @property
    def group_id(self):
        if self._slim_item:
            return self._slim_item.groupID
        if self._target:
            return self._target.get('group_id', None)

    @property
    def dungeon_object_id(self):
        if self._slim_item:
            return getattr(self._slim_item, 'dunObjectID', None)
        if self._target:
            return self._target.get('dungeon_object_id', None)

    def _set_target_title(self, value):
        if self._use_custom_title:
            return
        if self._title == value:
            return
        self._title = value
        self.hidden = not bool(self._title)

    def _initialize_slim_item(self):
        while not self._slim_item:
            if self.item_id:
                self._slim_item = sm.GetService('michelle').GetItem(self.item_id)
            elif self.type_id or self.group_id or self.dungeon_object_id:
                self._find_target()
            if not self._slim_item:
                uthread2.sleep(0.5)

        title = None
        if self._slim_item.nameID:
            title = localization.GetByMessageID(self._slim_item.nameID)
        elif self._slim_item.charID:
            try:
                character_info = cfg.eveowners.Get(self._slim_item.charID)
                title = character_info.name
            except KeyError:
                pass

        if not title:
            title = evetypes.GetName(self.type_id)
        self._slim_item_tasklet = None
        self._set_target_title(title)
        self._set_target_highlight()
        self._slim_item_initialized()
        self.update()

    def _find_target(self):
        if self.dungeon_object_id:
            from nodegraph.client.getters.object import GetDungeonObject
            dungeon_object = GetDungeonObject(dungeon_object_id=self.dungeon_object_id).get_values()
            if dungeon_object:
                self._slim_item = dungeon_object['slim_item']
        else:
            from nodegraph.client.getters.object import FindClosestObject
            target = FindClosestObject(type_id=self.type_id, group_id=self.group_id).get_values()
            if target and 'slim_item' in target:
                self._slim_item = target['slim_item']

    def _set_target_highlight(self):
        from nodegraph.client.actions.highlights import HighlightSpaceObject
        self.highlight = HighlightSpaceObject(item_id=self.item_id)

    def _slim_item_initialized(self):
        pass

    def mouse_down(self, ui_widget):
        item_id = self.item_id
        sm.GetService('stateSvc').SetState(item_id, states.selected, 1)
        sm.GetService('menu').TacticalItemClicked(item_id)
        sm.GetService('menu').TryExpandActionMenu(item_id, ui_widget)

    def click(self):
        camera = sm.GetService('sceneManager').GetActiveSpaceCamera()
        if camera:
            camera.Track(self.item_id)

    def double_click(self, *args):
        if uicore.cmd.IsSomeCombatCommandLoaded():
            return
        if self._slim_item:
            sm.GetService('menu').Activate(self._slim_item)

    def get_context_menu(self):
        return sm.GetService('menu').CelestialMenu(self.item_id)

    def _stop(self):
        if self._slim_item_tasklet:
            self._slim_item_tasklet.kill()
            self._slim_item_tasklet = None

    @staticmethod
    def get_custom_task_id(target):
        try:
            if isinstance(target, dict):
                return target.get('item_id') or target.get('dungeon_object_id') or target.get('type_id') or target.get('group_id') or None
            return target.itemID
        except:
            log.LogException()
            return None


class TargetsTaskGroup(ObjectiveTaskGroup):
    TASK = TargetTask
    KEY = 'targets'
    objective_task_content_id = None

    def __init__(self, targets = None, **kwargs):
        super(TargetsTaskGroup, self).__init__(**kwargs)
        self._update_targets(targets)

    def update_value(self, key, value):
        super(TargetsTaskGroup, self).update_value(key, value)
        if key == self.KEY:
            self._update_targets(value)

    def _update_targets(self, targets):
        self.clear_tasks()
        if targets is None:
            targets = []
        elif not isinstance(targets, list):
            targets = [targets]
        for target in targets:
            self._add_target(target, start_task=False)

        self.all_tasks_added()

    def _get_task_by_item_id(self, item_id):
        if item_id in self.tasks:
            return self.tasks[item_id]
        for task in self.tasks.itervalues():
            if task.item_id == item_id:
                return task

    def _add_target(self, target, start_task = False):
        task_id = self.TASK.get_custom_task_id(target)
        self.add_task(task_id=task_id, target=target, start_task=start_task)


class BaseTargetsTask(ObjectiveTaskGroup):
    objective_task_content_id = None
    TASK = TargetTask
    __notifyevents__ = ['OnBallAdded', 'DoBallRemove']

    def start(self):
        self.clear_tasks()
        if self._is_active:
            self.update()
        else:
            super(BaseTargetsTask, self).start()

    def _start(self):
        super(BaseTargetsTask, self)._start()
        self._find_targets()

    def OnBallAdded(self, slim_item):
        if self._validate_target(slim_item):
            self._add_target(slim_item)

    def DoBallRemove(self, ball, *args, **kwargs):
        if ball is not None:
            self.remove_task(task_id=ball.id)

    def _find_targets(self):
        ballpark = sm.GetService('michelle').GetBallpark()
        if not ballpark:
            return
        for ball_id in ballpark.balls.iterkeys():
            if ball_id == session.shipid:
                continue
            slim_item = ballpark.GetInvItem(ball_id)
            if slim_item and self._validate_target(slim_item):
                self._add_target(slim_item, start_task=False)

        self.all_tasks_added()

    def _validate_target(self, slim_item):
        return True

    def _add_target(self, slim_item, start_task = True):
        self.add_task(task_id=slim_item.itemID, target=slim_item, start_task=start_task)


class TargetsTask(BaseTargetsTask):

    def __init__(self, type_ids = None, group_ids = None, type_list_id = None, objective_target_groups = None, item_ids = None, dungeon_object_ids = None, *args, **kwargs):
        self._item_ids = value_as_set(item_ids)
        self._dungeon_object_ids = value_as_set(dungeon_object_ids)
        self._objective_target_groups = value_as_set(objective_target_groups)
        self._type_ids = value_as_set(type_ids)
        self._group_ids = value_as_set(group_ids)
        self._type_list_id = None
        self._type_ids_from_type_list = set()
        if type_list_id:
            self._update_type_list()
        super(TargetsTask, self).__init__(*args, **kwargs)

    @property
    def item_ids(self):
        return self._item_ids

    @item_ids.setter
    def item_ids(self, value):
        if self._item_ids == value:
            return
        self._item_ids = value_as_set(value)
        self._parameter_updated()

    @property
    def dungeon_object_ids(self):
        return self._dungeon_object_ids

    @dungeon_object_ids.setter
    def dungeon_object_ids(self, value):
        if self._dungeon_object_ids == value:
            return
        self._dungeon_object_ids = value_as_set(value)
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
    def objective_target_groups(self):
        return self._objective_target_groups

    @objective_target_groups.setter
    def objective_target_groups(self, value):
        if self._objective_target_groups == value:
            return
        self._objective_target_groups = value_as_set(value)
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
        self.clear_tasks()
        if self.is_active:
            self._find_targets()
            self.update()

    def _validate_target(self, slim_item):
        if self._objective_target_groups and getattr(slim_item, 'objectiveTargetGroup', None) in self._objective_target_groups:
            return True
        if self._type_ids and getattr(slim_item, 'typeID', None) in self._type_ids:
            return True
        if self._group_ids and getattr(slim_item, 'groupID', None) in self._group_ids:
            return True
        if self._type_ids_from_type_list and getattr(slim_item, 'typeID', None) in self._type_ids_from_type_list:
            return True
        if self._item_ids and getattr(slim_item, 'itemID', None) in self._item_ids:
            return True
        if self._dungeon_object_ids and getattr(slim_item, 'dunObjectID', None) in self._dungeon_object_ids:
            return True
        return False


class GetWithinRangeTask(TargetTask):
    objective_task_content_id = 7
    WIDGET = ProgressBarTaskWidget

    def __init__(self, distance = 500, **kwargs):
        self._distance = distance
        self._target_ball = None
        self._max_distance = distance + 1
        self._distance_to_target = self._max_distance
        super(GetWithinRangeTask, self).__init__(**kwargs)

    @property
    def distance(self):
        return self._distance

    @distance.setter
    def distance(self, value):
        if self._distance == value:
            return
        self._distance = value
        self._max_distance = max(self._max_distance, self._distance + 1)
        self.update()

    def _slim_item_initialized(self):
        super(GetWithinRangeTask, self)._slim_item_initialized()
        ballpark = sm.GetService('michelle').GetBallpark()
        self._target_ball = ballpark.GetBall(self.item_id)
        self._update_distance_routine()

    @threadutils.threaded
    def _update_distance_routine(self):
        while self.is_active:
            value = max(0, self._target_ball.surfaceDist - self.distance)
            if self._distance_to_target != value:
                self._distance_to_target = value
                self._max_distance = max(self._max_distance, self._distance_to_target)
                self.update()
                self.completed = self._distance_to_target == 0
            uthread2.sleep(1)

    @property
    def progress(self):
        return 1.0 - min(self._distance_to_target / float(self._max_distance), 1.0)

    @property
    def value(self):
        return FmtDist(self._distance_to_target, 0)


class TargetWithProgressTask(TargetTask, ProgressTask):
    objective_task_content_id = 32
    WIDGET = ProgressBarTaskWidget


class TargetWithValueRangeTask(TargetTask, ValueRangeTask):
    objective_task_content_id = 43
    WIDGET = ProgressBarTaskWidget
