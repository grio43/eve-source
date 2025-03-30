#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\progression\common\objectives.py
from utillib import KeyVal
from progression.common import tasks
from localization import GetByMessageID
LOBBY_ROOM = 27151
EMPIRE_ROOM = 27152
TRIGLAVIAN_ROOM = 27153
TRIGLAVIAN_GATE_OBJECT_ID = 1071397
EMPIRE_GATE_OBJECT_ID = 1071396

class ObjectiveType(object):
    OBJECTIVE_TYPE_COMPLETE_ALL_TASKS = 1
    OBJECTIVE_TYPE_CHOICE = 2


VICTORY_TRIGLAVIAN_OBJECTIVE = KeyVal(objective_id=5, room_ids=[EMPIRE_ROOM], connecting_gate_ids=[], objective_type_id=ObjectiveType.OBJECTIVE_TYPE_COMPLETE_ALL_TASKS, title=GetByMessageID(553429), description=GetByMessageID(553882), tasks=[], next_objective=None)
DESTROY_EMPIRE_STRUCTURE_OBJECTIVE = KeyVal(objective_id=6, room_ids=[EMPIRE_ROOM], connecting_gate_ids=[TRIGLAVIAN_GATE_OBJECT_ID], objective_type_id=ObjectiveType.OBJECTIVE_TYPE_COMPLETE_ALL_TASKS, title=GetByMessageID(553431), description=GetByMessageID(553539), tasks=[tasks.DESTROY_EMPIRE_STRUCTURE_TASK.task_id], next_objective=VICTORY_TRIGLAVIAN_OBJECTIVE.objective_id)
KILL_EMPIRE_DREAD_OBJECTIVE = KeyVal(objective_id=4, room_ids=[EMPIRE_ROOM], connecting_gate_ids=[TRIGLAVIAN_GATE_OBJECT_ID], objective_type_id=ObjectiveType.OBJECTIVE_TYPE_COMPLETE_ALL_TASKS, title=GetByMessageID(553432), description='', tasks=[tasks.KILL_EMPIRE_DREAD_TASK.task_id], next_objective=DESTROY_EMPIRE_STRUCTURE_OBJECTIVE.objective_id)
DESTROY_EMPIRE_OBJECTIVE = KeyVal(objective_id=3, room_ids=[EMPIRE_ROOM], connecting_gate_ids=[TRIGLAVIAN_GATE_OBJECT_ID], objective_type_id=ObjectiveType.OBJECTIVE_TYPE_COMPLETE_ALL_TASKS, title=GetByMessageID(553433), description='', tasks=[tasks.KILL_EMPIRE_WAVE_TASK.task_id], next_objective=KILL_EMPIRE_DREAD_OBJECTIVE.objective_id)
VICTORY_EMPIRE_OBJECTIVE = KeyVal(objective_id=9, room_ids=[TRIGLAVIAN_ROOM], connecting_gate_ids=[], objective_type_id=ObjectiveType.OBJECTIVE_TYPE_COMPLETE_ALL_TASKS, title=GetByMessageID(553434), description=GetByMessageID(553880), tasks=[], next_objective=None)
DESTROY_TRIGLAVIAN_STRUCTURE_OBJECTIVE = KeyVal(objective_id=12, room_ids=[TRIGLAVIAN_ROOM], connecting_gate_ids=[EMPIRE_GATE_OBJECT_ID], objective_type_id=ObjectiveType.OBJECTIVE_TYPE_COMPLETE_ALL_TASKS, title=GetByMessageID(553435), description=GetByMessageID(553538), tasks=[tasks.DESTROY_TRIGLAVIAN_STRUCTURE_TASK.task_id], next_objective=VICTORY_EMPIRE_OBJECTIVE.objective_id)
KILL_TRIGLAVIAN_DREAD_OBJECTIVE = KeyVal(objective_id=11, room_ids=[TRIGLAVIAN_ROOM], connecting_gate_ids=[EMPIRE_GATE_OBJECT_ID], objective_type_id=ObjectiveType.OBJECTIVE_TYPE_COMPLETE_ALL_TASKS, title=GetByMessageID(553437), description='', tasks=[tasks.KILL_TRIGLAVIAN_DREAD_TASK.task_id], next_objective=DESTROY_TRIGLAVIAN_STRUCTURE_OBJECTIVE.objective_id)
DESTROY_TRIGLAVIAN_OBJECTIVE = KeyVal(objective_id=10, room_ids=[TRIGLAVIAN_ROOM], connecting_gate_ids=[EMPIRE_GATE_OBJECT_ID], objective_type_id=ObjectiveType.OBJECTIVE_TYPE_COMPLETE_ALL_TASKS, title=GetByMessageID(553438), description='', tasks=[tasks.KILL_TRIGLAVIAN_WAVE_TASK.task_id], next_objective=KILL_TRIGLAVIAN_DREAD_OBJECTIVE.objective_id)
PICK_A_SIDE_OBJECTIVE = KeyVal(objective_id=100, room_ids=[LOBBY_ROOM], connecting_gate_ids=[], objective_type_id=ObjectiveType.OBJECTIVE_TYPE_CHOICE, title=GetByMessageID(553439), description=GetByMessageID(553440), tasks=[tasks.EMPIRE_SIDE_TASK.task_id, tasks.TRIGLAVIAN_SIDE_TASK.task_id], next_objectives={tasks.EMPIRE_SIDE_TASK.task_id: DESTROY_TRIGLAVIAN_OBJECTIVE.objective_id,
 tasks.TRIGLAVIAN_SIDE_TASK.task_id: DESTROY_EMPIRE_OBJECTIVE.objective_id})
FAKE_FSD_OBJECTIVES = {PICK_A_SIDE_OBJECTIVE.objective_id: PICK_A_SIDE_OBJECTIVE,
 DESTROY_EMPIRE_OBJECTIVE.objective_id: DESTROY_EMPIRE_OBJECTIVE,
 KILL_EMPIRE_DREAD_OBJECTIVE.objective_id: KILL_EMPIRE_DREAD_OBJECTIVE,
 DESTROY_EMPIRE_STRUCTURE_OBJECTIVE.objective_id: DESTROY_EMPIRE_STRUCTURE_OBJECTIVE,
 VICTORY_TRIGLAVIAN_OBJECTIVE.objective_id: VICTORY_TRIGLAVIAN_OBJECTIVE,
 DESTROY_TRIGLAVIAN_OBJECTIVE.objective_id: DESTROY_TRIGLAVIAN_OBJECTIVE,
 KILL_TRIGLAVIAN_DREAD_OBJECTIVE.objective_id: KILL_TRIGLAVIAN_DREAD_OBJECTIVE,
 DESTROY_TRIGLAVIAN_STRUCTURE_OBJECTIVE.objective_id: DESTROY_TRIGLAVIAN_STRUCTURE_OBJECTIVE,
 VICTORY_EMPIRE_OBJECTIVE.objective_id: VICTORY_EMPIRE_OBJECTIVE}

def load_objective(objective_id):
    return FAKE_FSD_OBJECTIVES[objective_id]
