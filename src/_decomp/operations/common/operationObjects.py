#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\operations\common\operationObjects.py


class TaskHint(object):

    def __init__(self, text, iconPath):
        self.text = text
        self.iconPath = iconPath


class ItemReward(object):

    def __init__(self, typeID, amount, raceID):
        self.typeID = typeID
        self.amount = amount
        self.raceID = raceID


class TitledItemReward(ItemReward):

    def __init__(self, typeID, amount, raceID, title = None, description = None):
        self.title = title
        self.description = description
        super(TitledItemReward, self).__init__(typeID, amount, raceID)


class SkillReward(object):

    def __init__(self, skillTypeID, level, sp, raceID):
        self.skillTypeID = skillTypeID
        self.level = level
        self.sp = sp
        self.raceID = raceID


def construct_item_rewards(item_rewards):
    return [ ItemReward(reward.typeID, reward.amount, reward.raceID) for reward in item_rewards ]


def construct_titled_item_rewards(item_rewards):
    return [ TitledItemReward(reward.typeID, reward.amount, reward.raceID, reward.title, reward.description) for reward in item_rewards ]


def construct_skill_rewards(skill_rewards):
    return [ SkillReward(skill_reward.skillTypeID, skill_reward.level, skill_reward.sp, skill_reward.raceID) for skill_reward in skill_rewards ]


class Task(object):

    def __init__(self, id, name, title, description, taskHint, achievementEventType, targetValue, eventConditions, serverSkipConditions, clientSkipConditions, isOptional, isSupreme, isCheckpoint, isSiteRelevant, completionRewards, delayBefore, dungeonBlackboardMessages = None):
        self.id = id
        self.name = name
        self.title = title
        self.description = description
        self.taskHint = TaskHint(taskHint.text, taskHint.iconPath) if taskHint else None
        self.achievementEventType = achievementEventType
        self.targetValue = targetValue
        self.eventConditionsByType = eventConditions
        self.eventConditions = sorted([ (condition_string, type_list) for condition_string, type_list in eventConditions.iteritems() ])
        self.serverSkipConditions = serverSkipConditions
        self.clientSkipConditions = clientSkipConditions
        self.formattedEventType = _format_event_type(achievementEventType, eventConditions)
        self.is_optional = isOptional
        self.is_supreme = isSupreme
        self.is_checkpoint = isCheckpoint
        self.is_site_relevant = isSiteRelevant
        self.completion_rewards = construct_item_rewards(completionRewards)
        self.delayBefore = delayBefore
        self.dungeonBlackboardMessages = dungeonBlackboardMessages

    def get_event_conditions(self, conditionType):
        value_list = self.eventConditionsByType.get(conditionType, [])
        if conditionType:
            value_list = [ self._try_get_as_number(type_id_str) for type_id_str in value_list ]
        return value_list

    def _try_get_as_number(self, value):
        try:
            return int(value)
        except ValueError:
            return value


class Operation(object):

    def __init__(self, title, description, iskReward, itemActivationRewards, itemCompletionRewards, skillRewards, moduleRequirements, notificationTitle, notificationDescription, taskList, operationID, isReplayable, siteID = None, operationPrerequisites = None, functionDescription = None, name = '', musicTrigger = None):
        self.operationID = operationID
        self.name = name
        self.title = title
        self.description = description
        self.iskReward = iskReward
        self.itemActivationRewards = construct_titled_item_rewards(itemActivationRewards)
        self.itemCompletionRewards = construct_titled_item_rewards(itemCompletionRewards)
        self.skillRewards = construct_skill_rewards(skillRewards)
        self.moduleRequirements = moduleRequirements
        self.notificationTitle = notificationTitle
        self.notificationDescription = notificationDescription
        self.taskList = taskList
        self.isReplayable = isReplayable
        self.siteID = siteID
        self.operationPrerequisites = operationPrerequisites
        self.functionDescription = functionDescription
        self.musicTrigger = musicTrigger

    def iter_task_ids(self):
        for task in self.taskList:
            yield task.id

    def reverse_iter_task_ids(self):
        for task in reversed(self.taskList):
            yield task.id

    def get_first_task_id(self):
        try:
            return self.taskList[0].id
        except IndexError:
            return None

    def get_last_task_id(self):
        try:
            return self.taskList[-1].id
        except IndexError:
            return None

    def has_task_with_id(self, task_id):
        return task_id in [ task.id for task in self.taskList ]


class OperationCategory(object):

    def __init__(self, title, description, iconPath, iskReward, notificationTitle, notificationDescription, operationTreeData, categoryID):
        self.title = title
        self.description = description
        self.iconPath = iconPath
        self.iskReward = iskReward
        self.notificationTitle = notificationTitle
        self.notificationDescription = notificationDescription
        self.categoryID = categoryID
        self.operationTrees = self._read_operation_trees(operationTreeData)

    def _read_operation_trees(self, operation_tree_data):
        operation_trees = [ (tree_id, OperationTree(self.categoryID, tree, tree_id=tree_id)) for tree_id, tree in operation_tree_data ]
        return operation_trees

    def get_tree_by_id(self, tree_id_to_find):
        for tree_id, tree in self.operationTrees:
            if tree_id == tree_id_to_find:
                return tree

    def iter_operation_ids(self):
        for tree_id, tree in self.operationTrees:
            for operation_id in tree.depth_first_iter():
                yield operation_id

    def get_head_operation_ids(self):
        head_operation_ids = []
        for tree_id, tree in self.operationTrees:
            head_operation_ids.extend(tree.get_head_nodes())

        return head_operation_ids


def format_event_conditions(conditions):
    formatted_condition_list = []
    for condition_string in sorted(conditions.keys()):
        type_list = conditions[condition_string]
        formatted_condition_list.append(':'.join([condition_string] + [ str(i) for i in type_list ]))

    return ':'.join(formatted_condition_list)


def _format_event_type(achievement_event_type, event_conditions):
    if not event_conditions:
        return achievement_event_type
    condition_string = format_event_conditions(event_conditions)
    return '{event_type}:{condition_string}'.format(event_type=achievement_event_type, condition_string=condition_string)


class OperationTree(object):

    def __init__(self, category_id, branch_dict, tree_id = None):
        self.tree_id = tree_id
        self.category_id = category_id
        self.connections = branch_dict
        self.head_nodes = None
        self.leaf_nodes = None
        self.initialize()

    def initialize(self):
        nodes_with_children = set()
        nodes_with_parents = set()
        self.head_nodes = set()
        self.leaf_nodes = set()
        for parent, list_of_children in self.connections.iteritems():
            if not list_of_children or list_of_children == [parent]:
                self.head_nodes.add(parent)
                if parent not in nodes_with_parents and not list_of_children:
                    self.leaf_nodes.add(parent)
            elif parent in self.head_nodes and list_of_children != [parent]:
                self.head_nodes.remove(parent)
            for child in list_of_children:
                if child == parent:
                    continue
                nodes_with_children.add(parent)
                nodes_with_parents.add(child)

        self.head_nodes.update(nodes_with_children - nodes_with_parents)
        self.leaf_nodes.update(nodes_with_parents - nodes_with_children)

    def get_first_active_node(self):
        try:
            return sorted(list(self.head_nodes))[0]
        except IndexError:
            return None

    def get_head_nodes(self):
        return self.head_nodes

    def get_leaf_nodes(self):
        return self.leaf_nodes

    def get_children(self, operation_id):
        return self.connections.get(operation_id, [])

    def depth_first_iter(self, nodes = None):
        if nodes is None:
            nodes = list(self.head_nodes)
        traversed_nodes = set()
        while nodes:
            n = nodes.pop()
            nodes.extend(self.get_children(n))
            if n not in traversed_nodes:
                yield n
                traversed_nodes.add(n)

        raise StopIteration

    def breadth_first_iter(self, nodes = None):
        if nodes is None:
            nodes = list(self.head_nodes)
        traversed_nodes = set()
        while nodes:
            n = nodes.pop()
            children = self.get_children(n)
            nodes = children.extend(nodes)
            if n not in traversed_nodes:
                yield n
                traversed_nodes.add(n)

        raise StopIteration

    def has_node(self, node_to_find):
        for node in self.depth_first_iter():
            if node == node_to_find:
                return True

        return False
