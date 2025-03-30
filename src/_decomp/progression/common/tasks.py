#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\progression\common\tasks.py
from progression.common import widgets
from utillib import KeyVal
from localization import GetByMessageID

class TaskType(object):
    TASK_TYPE_DUNGEON_TRIGGER_FIRED = 1
    TASK_TYPE_DUNGEON_EVENT_FIRED = 2


EMPIRE_SIDE_TASK = KeyVal(task_id=101, task_type_id=TaskType.TASK_TYPE_DUNGEON_TRIGGER_FIRED, completion_text=GetByMessageID(553441), trigger_id=64908, task_widgets=[widgets.REACTIVE_PICK_A_SIDE_WIDGET_EMPIRE.task_widget_id])
KILL_EMPIRE_WAVE_TASK = KeyVal(task_id=146, task_type_id=TaskType.TASK_TYPE_DUNGEON_TRIGGER_FIRED, completion_text=GetByMessageID(553442), trigger_id=64910, task_widgets=[widgets.REACTIVE_EMPIRE_WIDGET.task_widget_id])
KILL_EMPIRE_DREAD_TASK = KeyVal(task_id=4, task_type_id=TaskType.TASK_TYPE_DUNGEON_TRIGGER_FIRED, completion_text=GetByMessageID(553443), trigger_id=64913, task_widgets=[widgets.HEALTH_BAR_EMPIRE_DREAD_WIDGET.task_widget_id,
 widgets.TIME_UNTIL_SIEGE_START_EMPIRE_DREAD_WIDGET.task_widget_id,
 widgets.TIME_UNTIL_SIEGE_END_EMPIRE_DREAD_WIDGET.task_widget_id,
 widgets.DUNGEON_COUNTER_TRIGLAVIAN_ENRAGE_WIDGET.task_widget_id])
DESTROY_EMPIRE_STRUCTURE_TASK = KeyVal(task_id=5, task_type_id=TaskType.TASK_TYPE_DUNGEON_TRIGGER_FIRED, completion_text=GetByMessageID(553444), trigger_id=64914, task_widgets=[widgets.HEALTH_BAR_EMPIRE_STRUCTURE_WIDGET.task_widget_id, widgets.DUNGEON_COUNTER_EMPIRE_BUFFS_WIDGET.task_widget_id, widgets.DUNGEON_COUNTER_EMPIRE_GREATER_THAN_WIDGET.task_widget_id])
TRIGLAVIAN_SIDE_TASK = KeyVal(task_id=102, task_type_id=TaskType.TASK_TYPE_DUNGEON_TRIGGER_FIRED, completion_text=GetByMessageID(553445), trigger_id=64907, task_widgets=[widgets.REACTIVE_PICK_A_SIDE_WIDGET_TRIGLAVIAN.task_widget_id])
KILL_TRIGLAVIAN_WAVE_TASK = KeyVal(task_id=147, task_type_id=TaskType.TASK_TYPE_DUNGEON_TRIGGER_FIRED, completion_text=GetByMessageID(553446), trigger_id=64919, task_widgets=[widgets.REACTIVE_TRIGLAVIAN_WIDGET.task_widget_id])
KILL_TRIGLAVIAN_DREAD_TASK = KeyVal(task_id=49, task_type_id=TaskType.TASK_TYPE_DUNGEON_TRIGGER_FIRED, completion_text=GetByMessageID(553447), trigger_id=64922, task_widgets=[widgets.HEALTH_BAR_TRIGLAVIAN_DREAD_WIDGET.task_widget_id,
 widgets.TIME_UNTIL_SIEGE_START_TRIGLAVIAN_DREAD_WIDGET.task_widget_id,
 widgets.TIME_UNTIL_SIEGE_END_TRIGLAVIAN_DREAD_WIDGET.task_widget_id,
 widgets.DUNGEON_COUNTER_EMPIRE_ENRAGE_WIDGET.task_widget_id])
DESTROY_TRIGLAVIAN_STRUCTURE_TASK = KeyVal(task_id=53, task_type_id=TaskType.TASK_TYPE_DUNGEON_TRIGGER_FIRED, completion_text=GetByMessageID(553448), trigger_id=64923, task_widgets=[widgets.HEALTH_BAR_TRIGLAVIAN_STRUCTURE_WIDGET.task_widget_id, widgets.DUNGEON_COUNTER_TRIGLAVIAN_BUFFS_WIDGET.task_widget_id, widgets.DUNGEON_COUNTER_TRIGLAVIAN_GREATER_THAN_WIDGET.task_widget_id])
FAKE_FSD_TASKS = {EMPIRE_SIDE_TASK.task_id: EMPIRE_SIDE_TASK,
 KILL_EMPIRE_DREAD_TASK.task_id: KILL_EMPIRE_DREAD_TASK,
 DESTROY_EMPIRE_STRUCTURE_TASK.task_id: DESTROY_EMPIRE_STRUCTURE_TASK,
 KILL_EMPIRE_WAVE_TASK.task_id: KILL_EMPIRE_WAVE_TASK,
 TRIGLAVIAN_SIDE_TASK.task_id: TRIGLAVIAN_SIDE_TASK,
 KILL_TRIGLAVIAN_WAVE_TASK.task_id: KILL_TRIGLAVIAN_WAVE_TASK,
 KILL_TRIGLAVIAN_DREAD_TASK.task_id: KILL_TRIGLAVIAN_DREAD_TASK,
 DESTROY_TRIGLAVIAN_STRUCTURE_TASK.task_id: DESTROY_TRIGLAVIAN_STRUCTURE_TASK}

def load_task(task_id):
    return FAKE_FSD_TASKS[task_id]
