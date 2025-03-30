#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\progression\common\widgets.py
from utillib import KeyVal
from localization import GetByMessageID

class TaskWidgetMode(object):
    TASK_WIDGET_MODE_NORMAL = 1
    TASK_WIDGET_MODE_ATTENTION = 2
    TASK_WIDGET_MODE_ALERT = 3


class TaskWidgetType(object):
    TASK_WIDGET_TYPE_TEXT = 1
    TASK_WIDGET_TYPE_NPC_KILL_COUNTER = 2
    TASK_WIDGET_TYPE_ENTITY_HEALTH_BAR = 3
    TASK_WIDGET_TYPE_DUNGEON_TIMER = 4
    TASK_WIDGET_TYPE_DUNGEON_COUNTER = 5
    TASK_WIDGET_TYPE_OBJECT_HEALTH_BAR = 6
    TASK_WIDGET_TYPE_REACTIVE_SPAWNER_POINTS_KILLED = 7
    TASK_WIDGET_TYPE_DUNGEON_COUNTER_GREATER_THAN = 8
    TASK_WIDGET_TYPE_REACTIVE_SPAWNER_ENTITY_HEALTH_BAR = 9


REACTIVE_PICK_A_SIDE_WIDGET_TRIGLAVIAN = KeyVal(task_widget_id=1, icon_grouping_id=1, task_widget_type_id=TaskWidgetType.TASK_WIDGET_TYPE_REACTIVE_SPAWNER_POINTS_KILLED, text=GetByMessageID(553449), bold=True, total_points_destroyed_trigger_id=64907, trigger_events_that_spawn_object=[])
REACTIVE_EMPIRE_WIDGET = KeyVal(task_widget_id=11, icon_grouping_id=1, task_widget_type_id=TaskWidgetType.TASK_WIDGET_TYPE_REACTIVE_SPAWNER_POINTS_KILLED, text=GetByMessageID(553450), total_points_destroyed_trigger_id=64910, trigger_events_that_spawn_object=[112064], bold=True)
HEALTH_BAR_EMPIRE_DREAD_WIDGET = KeyVal(task_widget_id=5, icon_grouping_id=1, task_widget_type_id=TaskWidgetType.TASK_WIDGET_TYPE_REACTIVE_SPAWNER_ENTITY_HEALTH_BAR, total_points_destroyed_trigger_id=64913, trigger_events_that_spawn_object=[112066], text=GetByMessageID(553452), wait_text=GetByMessageID(553453), bold=True)
TIME_UNTIL_SIEGE_START_EMPIRE_DREAD_WIDGET = KeyVal(task_widget_id=7, icon_grouping_id=2, task_widget_type_id=TaskWidgetType.TASK_WIDGET_TYPE_DUNGEON_TIMER, timer_id=1, text=GetByMessageID(553455), mode=TaskWidgetMode.TASK_WIDGET_MODE_NORMAL, highlight_type_ids=[52964,
 52965,
 52966,
 52967], bold=False)
TIME_UNTIL_SIEGE_END_EMPIRE_DREAD_WIDGET = KeyVal(task_widget_id=8, icon_grouping_id=2, task_widget_type_id=TaskWidgetType.TASK_WIDGET_TYPE_DUNGEON_TIMER, timer_id=2, text=GetByMessageID(553456), mode=TaskWidgetMode.TASK_WIDGET_MODE_ATTENTION, highlight_type_ids=[52964,
 52965,
 52966,
 52967], bold=False)
HEALTH_BAR_EMPIRE_STRUCTURE_WIDGET = KeyVal(task_widget_id=6, icon_grouping_id=1, task_widget_type_id=TaskWidgetType.TASK_WIDGET_TYPE_ENTITY_HEALTH_BAR, entity_id=141305, text='', wait_text='', bold=True)
DUNGEON_COUNTER_EMPIRE_BUFFS_WIDGET = KeyVal(task_widget_id=9, icon_grouping_id=3, task_widget_type_id=TaskWidgetType.TASK_WIDGET_TYPE_DUNGEON_COUNTER, counter_id=1, target_value=7, text=GetByMessageID(553457), highlight_space_object_ids=[1071470, 1071471], bold=False)
DUNGEON_COUNTER_EMPIRE_GREATER_THAN_WIDGET = KeyVal(task_widget_id=12, icon_grouping_id=3, task_widget_type_id=TaskWidgetType.TASK_WIDGET_TYPE_DUNGEON_COUNTER_GREATER_THAN, counter_id=1, show_when_counter_greater_than=6, text=GetByMessageID(553458), highlight_type_ids=[52701], dependent_type_list=[52701], bold=False, mode=TaskWidgetMode.TASK_WIDGET_MODE_NORMAL)
DUNGEON_COUNTER_EMPIRE_ENRAGE_WIDGET = KeyVal(task_widget_id=20, icon_grouping_id=3, task_widget_type_id=TaskWidgetType.TASK_WIDGET_TYPE_DUNGEON_COUNTER_GREATER_THAN, counter_id=3, show_when_counter_greater_than=2, text=GetByMessageID(553917), highlight_type_ids=[52701], bold=False, mode=TaskWidgetMode.TASK_WIDGET_MODE_ALERT)
REACTIVE_PICK_A_SIDE_WIDGET_EMPIRE = KeyVal(task_widget_id=2, icon_grouping_id=1, task_widget_type_id=TaskWidgetType.TASK_WIDGET_TYPE_REACTIVE_SPAWNER_POINTS_KILLED, text=GetByMessageID(553460), bold=True, total_points_destroyed_trigger_id=64908, trigger_events_that_spawn_object=[])
REACTIVE_TRIGLAVIAN_WIDGET = KeyVal(task_widget_id=13, icon_grouping_id=1, task_widget_type_id=TaskWidgetType.TASK_WIDGET_TYPE_REACTIVE_SPAWNER_POINTS_KILLED, text=GetByMessageID(553461), total_points_destroyed_trigger_id=64919, trigger_events_that_spawn_object=[112104], bold=True)
HEALTH_BAR_TRIGLAVIAN_DREAD_WIDGET = KeyVal(task_widget_id=15, icon_grouping_id=1, task_widget_type_id=TaskWidgetType.TASK_WIDGET_TYPE_REACTIVE_SPAWNER_ENTITY_HEALTH_BAR, total_points_destroyed_trigger_id=64922, trigger_events_that_spawn_object=[112105], text=GetByMessageID(553468), wait_text=GetByMessageID(553462), bold=True)
TIME_UNTIL_SIEGE_START_TRIGLAVIAN_DREAD_WIDGET = KeyVal(task_widget_id=17, icon_grouping_id=2, task_widget_type_id=TaskWidgetType.TASK_WIDGET_TYPE_DUNGEON_TIMER, timer_id=1, text=GetByMessageID(553464), mode=TaskWidgetMode.TASK_WIDGET_MODE_NORMAL, highlight_type_ids=[52701], bold=False)
TIME_UNTIL_SIEGE_END_TRIGLAVIAN_DREAD_WIDGET = KeyVal(task_widget_id=18, icon_grouping_id=2, task_widget_type_id=TaskWidgetType.TASK_WIDGET_TYPE_DUNGEON_TIMER, timer_id=2, text=GetByMessageID(553465), mode=TaskWidgetMode.TASK_WIDGET_MODE_ATTENTION, highlight_type_ids=[52701], bold=False)
HEALTH_BAR_TRIGLAVIAN_STRUCTURE_WIDGET = KeyVal(task_widget_id=16, icon_grouping_id=1, task_widget_type_id=TaskWidgetType.TASK_WIDGET_TYPE_ENTITY_HEALTH_BAR, entity_id=141304, text='', wait_text='', bold=True)
DUNGEON_COUNTER_TRIGLAVIAN_BUFFS_WIDGET = KeyVal(task_widget_id=19, icon_grouping_id=3, task_widget_type_id=TaskWidgetType.TASK_WIDGET_TYPE_DUNGEON_COUNTER, counter_id=100, target_value=7, text=GetByMessageID(553466), highlight_space_object_ids=[1071468, 1071469], bold=False)
DUNGEON_COUNTER_TRIGLAVIAN_GREATER_THAN_WIDGET = KeyVal(task_widget_id=122, icon_grouping_id=3, task_widget_type_id=TaskWidgetType.TASK_WIDGET_TYPE_DUNGEON_COUNTER_GREATER_THAN, counter_id=100, show_when_counter_greater_than=6, text=GetByMessageID(553467), highlight_type_ids=[52964,
 52965,
 52966,
 52967], dependent_type_list=[52964,
 52965,
 52966,
 52967], bold=False, mode=TaskWidgetMode.TASK_WIDGET_MODE_NORMAL)
DUNGEON_COUNTER_TRIGLAVIAN_ENRAGE_WIDGET = KeyVal(task_widget_id=21, icon_grouping_id=3, task_widget_type_id=TaskWidgetType.TASK_WIDGET_TYPE_DUNGEON_COUNTER_GREATER_THAN, counter_id=3, show_when_counter_greater_than=2, text=GetByMessageID(553918), highlight_type_ids=[52964,
 52965,
 52966,
 52967], bold=False, mode=TaskWidgetMode.TASK_WIDGET_MODE_ALERT)
FAKE_FSD_WIDGETS = {REACTIVE_PICK_A_SIDE_WIDGET_TRIGLAVIAN.task_widget_id: REACTIVE_PICK_A_SIDE_WIDGET_TRIGLAVIAN,
 REACTIVE_EMPIRE_WIDGET.task_widget_id: REACTIVE_EMPIRE_WIDGET,
 HEALTH_BAR_EMPIRE_DREAD_WIDGET.task_widget_id: HEALTH_BAR_EMPIRE_DREAD_WIDGET,
 TIME_UNTIL_SIEGE_START_EMPIRE_DREAD_WIDGET.task_widget_id: TIME_UNTIL_SIEGE_START_EMPIRE_DREAD_WIDGET,
 TIME_UNTIL_SIEGE_END_EMPIRE_DREAD_WIDGET.task_widget_id: TIME_UNTIL_SIEGE_END_EMPIRE_DREAD_WIDGET,
 HEALTH_BAR_EMPIRE_STRUCTURE_WIDGET.task_widget_id: HEALTH_BAR_EMPIRE_STRUCTURE_WIDGET,
 DUNGEON_COUNTER_EMPIRE_BUFFS_WIDGET.task_widget_id: DUNGEON_COUNTER_EMPIRE_BUFFS_WIDGET,
 DUNGEON_COUNTER_EMPIRE_ENRAGE_WIDGET.task_widget_id: DUNGEON_COUNTER_EMPIRE_ENRAGE_WIDGET,
 DUNGEON_COUNTER_EMPIRE_GREATER_THAN_WIDGET.task_widget_id: DUNGEON_COUNTER_EMPIRE_GREATER_THAN_WIDGET,
 REACTIVE_PICK_A_SIDE_WIDGET_EMPIRE.task_widget_id: REACTIVE_PICK_A_SIDE_WIDGET_EMPIRE,
 REACTIVE_TRIGLAVIAN_WIDGET.task_widget_id: REACTIVE_TRIGLAVIAN_WIDGET,
 HEALTH_BAR_TRIGLAVIAN_DREAD_WIDGET.task_widget_id: HEALTH_BAR_TRIGLAVIAN_DREAD_WIDGET,
 TIME_UNTIL_SIEGE_START_TRIGLAVIAN_DREAD_WIDGET.task_widget_id: TIME_UNTIL_SIEGE_START_TRIGLAVIAN_DREAD_WIDGET,
 TIME_UNTIL_SIEGE_END_TRIGLAVIAN_DREAD_WIDGET.task_widget_id: TIME_UNTIL_SIEGE_END_TRIGLAVIAN_DREAD_WIDGET,
 HEALTH_BAR_TRIGLAVIAN_STRUCTURE_WIDGET.task_widget_id: HEALTH_BAR_TRIGLAVIAN_STRUCTURE_WIDGET,
 DUNGEON_COUNTER_TRIGLAVIAN_BUFFS_WIDGET.task_widget_id: DUNGEON_COUNTER_TRIGLAVIAN_BUFFS_WIDGET,
 DUNGEON_COUNTER_TRIGLAVIAN_GREATER_THAN_WIDGET.task_widget_id: DUNGEON_COUNTER_TRIGLAVIAN_GREATER_THAN_WIDGET,
 DUNGEON_COUNTER_TRIGLAVIAN_ENRAGE_WIDGET.task_widget_id: DUNGEON_COUNTER_TRIGLAVIAN_ENRAGE_WIDGET}

def load_widget(task_widget_id):
    return FAKE_FSD_WIDGETS[task_widget_id]
