#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\blackboards\scopes.py
import collections
from brennivin.itertoolsext import Bundle
try:
    from eve.common.script.sys.idCheckers import IsPlayerItem
except ImportError:

    def IsPlayerItem(_):
        return False


Scope = collections.namedtuple('Scope', ['scopeType', 'id'])
ScopeTypes = Bundle(Item='item', EntityGroup='entity_group', Dungeon='dungeon', Tale='tale', SpawnPointPool='spawn_point_pool', NodeGraph='node_graph')
CONTEXT_ID_BY_SCOPE = {ScopeTypes.Item: 'myItemId',
 ScopeTypes.EntityGroup: 'myEntityGroupId',
 ScopeTypes.Dungeon: 'myDungeonSpawnId',
 ScopeTypes.Tale: 'myTaleId',
 ScopeTypes.SpawnPointPool: 'mySpawnPointPoolId',
 ScopeTypes.NodeGraph: 'myNodeGraphInstanceId'}
SCOPE_DISPLAY_INFO = [(ScopeTypes.Item, 'Item Blackboard: %s'),
 (ScopeTypes.EntityGroup, 'Entity Group Blackboard: %s'),
 (ScopeTypes.Dungeon, 'Dungeon Blackboard (spawn): %s'),
 (ScopeTypes.Tale, 'Tale Blackboard: %s'),
 (ScopeTypes.SpawnPointPool, 'Spawn Point Pool Blackboard: %s'),
 (ScopeTypes.NodeGraph, 'Node Graph Blackboard: %s')]

class BlackboardContextIdNotInBehaviorContextError(Exception):
    pass


def ItemScope(itemID):
    return Scope(ScopeTypes.Item, itemID)


def EntityGroupScope(groupID):
    return Scope(ScopeTypes.EntityGroup, groupID)


def DungeonScope(spawnID):
    return Scope(ScopeTypes.Dungeon, spawnID)


def TaleScope(taleID):
    return Scope(ScopeTypes.Tale, taleID)


def SpawnPointPoolScope(spawnPointPoolID):
    return Scope(ScopeTypes.SpawnPointPool, spawnPointPoolID)


def NodeGraphScope(instanceID):
    return Scope(ScopeTypes.NodeGraph, instanceID)


def GetBlackboardFromContext(context, blackboardScope):
    scope = GetBlackboardIdFromScopeAndContext(blackboardScope, context)
    return context.blackboardManager.GetBlackboard(scope)


def GetBlackboardIdFromScopeAndContext(blackboardScope, context):
    scope = Scope(blackboardScope, GetIdFromContextByScope(blackboardScope, context))
    return scope


def GetIdFromContextByScope(blackboardScope, context):
    context_id = CONTEXT_ID_BY_SCOPE[blackboardScope]
    try:
        return context[context_id]
    except KeyError:
        raise BlackboardContextIdNotInBehaviorContextError()


def GetChannelFromAddress(context, blackboardAddress):
    blackboardScope, messageName = blackboardAddress
    blackboard = GetBlackboardFromContext(context, blackboardScope)
    return blackboard.GetMessageChannel(messageName)


def IsItemScope(scope):
    return scope.scopeType == ScopeTypes.Item


def IsEntityGroupScope(scope):
    return scope.scopeType == ScopeTypes.EntityGroup


def IsDungeonScope(scope):
    return scope.scopeType == ScopeTypes.Dungeon


def IsTaleScope(scope):
    return scope.scopeType == ScopeTypes.Tale


def IsSpawnPointPoolScope(scope):
    return scope.scopeType == ScopeTypes.SpawnPointPool


def IsNodeGraphScope(scope):
    return scope.scopeType == ScopeTypes.NodeGraph


def IsReusableScope(scope):
    return IsItemScope(scope) and IsPlayerItem(scope.id)


def GetBlackboardScopeFromAddress(address):
    return address[0]


def GetBlackboardChannelNameFromAddress(address):
    return address[1]
