#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\utility\context.py
CONTEXT_MY_DUNGEON_SPAWN_ID = 'myDungeonSpawnId'
CONTEXT_MY_DUNGEON_ID = 'myDungeonId'
CONTEXT_MY_DUNGEON_SPAWN_SCENARIO_ID = 'myDungeonSpawnScenarioId'
CONTEXT_MY_TALE_ID = 'myTaleId'
CONTEXT_MY_SPAWN_POINT_POOL_ID = 'mySpawnPointPoolId'
CONTEXT_MY_SPAWN_TABLE_ID = 'mySpawnTableId'
CONTEXT_MY_ENTITY_GROUP_ID = 'myEntityGroupId'
CONTEXT_MY_NODE_GRAPH_INSTANCE_ID = 'myNodeGraphInstanceId'
CONTEXT_TO_COPY_TO_ITEM = [CONTEXT_MY_DUNGEON_SPAWN_ID,
 CONTEXT_MY_DUNGEON_ID,
 CONTEXT_MY_TALE_ID,
 CONTEXT_MY_SPAWN_POINT_POOL_ID,
 CONTEXT_MY_SPAWN_TABLE_ID,
 CONTEXT_MY_NODE_GRAPH_INSTANCE_ID]

def get_extra_context(task):
    spawn_pool_id = None
    if hasattr(task, 'get_spawn_pool_id'):
        spawn_pool_id = task.get_spawn_pool_id()
    spawn_table_id = None
    if hasattr(task, 'get_spawn_table_id'):
        spawn_table_id = task.get_spawn_table_id()
    context = {CONTEXT_MY_TALE_ID: None}
    copy_context_to_context(context, task.context)
    context[CONTEXT_MY_SPAWN_POINT_POOL_ID] = spawn_pool_id
    context[CONTEXT_MY_SPAWN_TABLE_ID] = spawn_table_id
    return context


def get_dungeon_context_from_spawn(spawn, scenario_id):
    extra_context = {CONTEXT_MY_DUNGEON_SPAWN_ID: spawn.spawnID,
     CONTEXT_MY_DUNGEON_ID: spawn.dungeonID,
     CONTEXT_MY_DUNGEON_SPAWN_SCENARIO_ID: scenario_id}
    if spawn.extraContext:
        extra_context.update(spawn.extraContext)
    return extra_context


def get_spawn_point_pool_context(spawn_point_pool_id, spawn_table_id):
    return {CONTEXT_MY_SPAWN_POINT_POOL_ID: spawn_point_pool_id,
     CONTEXT_MY_SPAWN_TABLE_ID: spawn_table_id}


def copy_context_to_context(to_context, from_context):
    for context_name in CONTEXT_TO_COPY_TO_ITEM:
        if context_name in from_context:
            to_context[context_name] = from_context[context_name]
