#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\operations\common\progression.py
from operations.common.const import OperationState, TaskState
from operations.common.util import is_operation_active
from signals import Signal
import logging
logger = logging.getLogger(__name__)

class Node(object):

    def __init__(self, category_id, operation_id, state, next_nodes = None):
        self.category_id = category_id
        self.operation_id = operation_id
        self.child_nodes = next_nodes or []
        self.on_complete = Signal(signalName='on_complete')
        self.state = state
        self.parent_node = None

    def is_in_an_active_state(self):
        return is_operation_active(self.state)

    def get_child_nodes(self):
        return self.child_nodes

    def get_nodes_to_activate_on_completion(self):
        nodes = []
        for child in self.child_nodes:
            if child.state == OperationState.LOCKED:
                nodes.append(child)
            elif is_operation_active(child.state):
                nodes.append(child)
                continue
            elif child.state == OperationState.COMPLETE:
                nodes.extend(child.get_nodes_to_activate_on_completion())

        return nodes

    def get_parent_node(self):
        return self.parent_node

    def add_child(self, node):
        node.parent_node = self
        self.child_nodes.append(node)

    def complete(self):
        if self.state != OperationState.COMPLETE:
            self.state = OperationState.COMPLETE
            self.on_complete(self)

    def lock(self):
        self.state = OperationState.LOCKED

    def lock_branch(self):
        self.lock()
        for c in self.child_nodes:
            c.lock_branch()

    def __repr__(self):
        return '{classname}: {category_id}-{operation_id}'.format(classname=self.__class__, operation_id=self.operation_id, category_id=self.category_id)


class Tree(object):

    def __init__(self, character_id, has_operation_ever_been_completed):
        self.character_id = character_id
        self.has_operation_ever_been_completed = has_operation_ever_been_completed
        self.active_node = None
        self.on_node_complete = Signal(signalName='on_node_complete')
        self.root_nodes = set()

    def add_node(self, node):
        node.on_complete.connect(self._on_complete)
        self.root_nodes.add(node)

    def _expand(self, node):
        if node.state == OperationState.LOCKED:
            node.on_complete.connect(self._on_complete)

    def _activate_first_active(self, node_list):
        for node in node_list:
            if node.is_in_an_active_state():
                self.set_active_node(node)
                return True

        return False

    def _activate_first(self, node_list):
        for node in node_list:
            self.set_active_node(node)
            return True

        return False

    def activate(self):
        if self._activate_first_active(self.root_nodes):
            return True
        return self._activate_first(self.root_nodes)

    def _on_complete(self, node):
        if self.active_node == node:
            self.active_node = None
        nodes_to_activate = node.get_nodes_to_activate_on_completion()
        nodes_to_expand = [ n for n in nodes_to_activate if n.state == OperationState.LOCKED ]
        map(self._expand, nodes_to_expand)
        self._activate_first_active(nodes_to_activate)
        if self.active_node is None:
            self._activate_first(nodes_to_activate)
        self.on_node_complete(self.character_id, node)

    def get_active_node(self):
        return self.active_node

    def set_active_node(self, node):
        if self.active_node is not None and self.active_node.is_in_an_active_state():
            self.active_node.state = OperationState.LOCKED
        if self.active_node is not None:
            self.active_node.on_complete.disconnect(self._on_complete)
        node.on_complete.connect(self._on_complete)
        is_reactivation = self.active_node and self.has_operation_ever_been_completed(self.character_id, self.active_node.category_id, self.active_node.operation_id)
        node.state = OperationState.REACTIVATED if is_reactivation else OperationState.ACTIVE
        self.active_node = node

    def _iter_states(self, node, states_list):
        states_list.append((node.operation_id, node.state))
        for child in node.child_nodes:
            self._iter_states(child, states_list)

    def iter_states(self):
        states = []
        for node in self.root_nodes:
            self._iter_states(node, states)

        return states

    def _find_node(self, node, operation_id):
        if node.operation_id == operation_id:
            return node
        for child in node.child_nodes:
            found_node = self._find_node(child, operation_id)
            if found_node is not None:
                return found_node

    def get_node_by_operation_id(self, operation_id):
        for root in self.root_nodes:
            found_node = self._find_node(root, operation_id)
            if found_node is not None:
                return found_node

    def reset_progress(self):
        for node in self.root_nodes:
            node.lock_branch()


class LinearProgressTreeValidator(object):

    def _check_node_for_lost_state(self, n, potentially_missing_operations, unlocked_state_found = False, locked_state_found_after_unlocked_state = False):
        if n.state == OperationState.LOCKED:
            if unlocked_state_found:
                locked_state_found_after_unlocked_state = True
                potentially_missing_operations.append(n)
        else:
            unlocked_state_found = True
            if locked_state_found_after_unlocked_state:
                return True
        for child in n.child_nodes:
            if self._check_node_for_lost_state(child, potentially_missing_operations, unlocked_state_found, locked_state_found_after_unlocked_state):
                return True

        return False

    def _check_node_for_multiple_active_operations(self, n, active_operations):
        if is_operation_active(n.state):
            active_operations.append(n)
        for child in n.child_nodes:
            self._check_node_for_multiple_active_operations(child, active_operations)

        if len(active_operations) > 1:
            return True
        return False

    def _validate_linear_tree_root_node(self, root):
        potentially_missing_operations = []
        if self._check_node_for_lost_state(root, potentially_missing_operations):
            logger.error('Operation progress has disappeared')
            for operation_node in potentially_missing_operations:
                logger.error('missing operation %s-%s' % (operation_node.category_id, operation_node.operation_id))

        active_operations = []
        if self._check_node_for_multiple_active_operations(root, active_operations):
            missing_category_id = active_operations[0].category_id
            missing_operation_ids = [ n.operation_id for n in active_operations ]
            logger.error('Tree for category %s has multiple active operations active %s' % (missing_category_id, missing_operation_ids))

    def check_for_errors(self, tree):
        root_count = len(tree.root_nodes)
        if root_count > 1:
            logger.error('Tree is not linear')
        elif not root_count:
            logger.error('Tree is missing a root node.')
        else:
            self._validate_linear_tree_root_node(list(tree.root_nodes)[0])


class TreeKeeper(object):

    def __init__(self, character_id, operations_cache, unlocked_categories, operation_states, has_operation_ever_been_completed):
        self.character_id = character_id
        self.operations_cache = operations_cache
        self.unlocked_categories = unlocked_categories
        self.operation_states = operation_states
        self.has_operation_ever_been_completed = has_operation_ever_been_completed
        self._progress_trees_by_category_and_tree_id = {}
        self._linear_progress_tree_validator = LinearProgressTreeValidator()
        self._load_progress_trees()

    def _create_head_node(self, tree, category_id, operation_id, state):
        return Node(category_id, operation_id, state=state)

    def _load_progress_trees(self):
        if self._progress_trees_by_category_and_tree_id:
            return
        for category_id in self.unlocked_categories:
            self.reset_progress_trees_for_category(category_id)

    def reset_progress_trees_for_category(self, category_id):
        category = self.operations_cache.get_operation_category_by_id(category_id)
        for tree_id, tree_order in category.operationTrees:
            self._construct_progress_tree(category, tree_id)

    def find_active_node(self, n):
        if n.is_in_an_active_state():
            return n
        for c in n.child_nodes:
            a = self.find_active_node(c)
            if a is not None:
                return a

    def _construct_progress_tree(self, category, tree_id):
        category_id = category.categoryID
        operation_tree = category.get_tree_by_id(tree_id)
        if category_id not in self._progress_trees_by_category_and_tree_id:
            self._progress_trees_by_category_and_tree_id[category_id] = {}
        tree = Tree(self.character_id, self.has_operation_ever_been_completed)
        head_operations = operation_tree.get_head_nodes()
        head_nodes = []
        nodes_created = {}
        for operation_id in sorted(head_operations):
            state = self.operation_states[category_id][operation_id]
            head = self._create_head_node(tree, category_id, operation_id, state)
            head_nodes.append(head)
            nodes_created[operation_id] = head

        for node in head_nodes:
            self._create_branch_nodes(nodes_created, operation_tree, category_id, node, self.character_id)

        for node in head_nodes:
            tree.add_node(node)
            if not tree.active_node:
                node_to_activate = self.find_active_node(node)
                if node_to_activate:
                    tree.set_active_node(node_to_activate)

        self._linear_progress_tree_validator.check_for_errors(tree)
        self._progress_trees_by_category_and_tree_id[category_id][tree_id] = tree

    def _sort_operations(self, operations):
        sorted_operation_keys = sorted(operations.keys())
        sorted_operations = []
        for operation_key in sorted_operation_keys:
            operation = operations[operation_key]
            sorted_operations.append(operation.operationID)

        return sorted_operations

    def _create_branch_nodes(self, nodes_created, operationTree, category_id, previous_node, character_id):
        for child_operation_id in operationTree.get_children(previous_node.operation_id):
            state = self.operation_states[category_id].get(child_operation_id, OperationState.LOCKED)
            if child_operation_id not in nodes_created:
                node = Node(category_id, child_operation_id, state=state)
                nodes_created[child_operation_id] = node
                self._create_branch_nodes(nodes_created, operationTree, category_id, node, character_id)
            previous_node.add_child(nodes_created[child_operation_id])

    def get_progress_trees_by_category(self):
        return self._progress_trees_by_category_and_tree_id

    def get_active_progress_tree_for_category(self, category_id):
        active_category_trees = self._get_active_progress_trees_for_category(category_id)
        for tree_id, tree in active_category_trees.items():
            operation_node = tree.get_active_node()
            if operation_node is not None and operation_node.is_in_an_active_state():
                return (tree_id, tree)

        return (None, None)

    def get_progress_tree_for_category_and_operation(self, category_id, operation_id):
        category_trees = self.get_progress_trees_for_category(category_id)
        for tree in category_trees:
            operation_node = tree.get_node_by_operation_id(operation_id)
            if operation_node is not None:
                return tree

    def get_progress_trees_for_category(self, category_id):
        return self._progress_trees_by_category_and_tree_id.get(category_id, {}).values()

    def get_progress_trees_and_ids_for_category(self, category_id):
        return self._progress_trees_by_category_and_tree_id.get(category_id, {})

    def get_progress_tree(self, category_id, tree_id):
        try:
            return self._progress_trees_by_category_and_tree_id[category_id][tree_id]
        except KeyError:
            return None

    def get_active_operation_node(self, category_id):
        progress_trees_for_character = self._get_active_progress_trees_for_category(category_id)
        for tree in progress_trees_for_character.values():
            operation_node = tree.get_active_node()
            if operation_node is not None and operation_node.is_in_an_active_state():
                return operation_node

    def _get_active_progress_trees_for_category(self, category_id):
        active_progress_trees = self.get_progress_trees_and_ids_for_category(category_id)
        return active_progress_trees

    def lock_items(self, character_id, items_to_lock, func_store_operation, func_store_task):
        for category_id, items in items_to_lock.items():
            operations_to_lock = items['operations']
            tasks_to_lock = items['tasks']
            for operation_id in operations_to_lock:
                progress_tree = self.get_progress_tree_for_category_and_operation(category_id, operation_id)
                node = progress_tree.get_node_by_operation_id(operation_id)
                if node is not None:
                    node.lock()
                    if func_store_operation:
                        func_store_operation(character_id, category_id, operation_id, OperationState.LOCKED)

            for locked_task in tasks_to_lock:
                _, operation_id, task_id = locked_task
                if func_store_task:
                    func_store_task(character_id, category_id, operation_id, task_id, TaskState.LOCKED, 0)

    def skip_items(self, character_id, items_to_skip, func_store_operation, func_store_task):
        for category_id, items in items_to_skip.items():
            operations_to_complete = items['operations']
            tasks_to_skip = items['tasks']
            for operation_id in operations_to_complete:
                progress_tree = self.get_progress_tree_for_category_and_operation(category_id, operation_id)
                node = progress_tree.get_node_by_operation_id(operation_id)
                if node is not None:
                    node.complete()
                if func_store_operation:
                    func_store_operation(character_id, category_id, operation_id, OperationState.COMPLETE)

            for skipped_task in tasks_to_skip:
                category_id, operation_id, task_id = skipped_task
                if func_store_task:
                    func_store_task(character_id, category_id, operation_id, task_id, TaskState.SKIPPED, 0)

    def activate_items(self, character_id, task_to_activate, operations_cache):
        category_id, operation_id, _ = task_to_activate
        category = operations_cache.get_operation_category_by_id(category_id)
        for tree_id, tree in category.operationTrees:
            is_tree_to_activate = tree.has_node(operation_id)
            if is_tree_to_activate:
                if not self.get_progress_tree(category_id, tree_id):
                    self._construct_progress_tree(category, tree_id)
                    break

        progress_tree = self.get_progress_tree_for_category_and_operation(category_id, operation_id)
        if progress_tree:
            node = progress_tree.get_node_by_operation_id(operation_id)
            if node:
                progress_tree.set_active_node(node)
