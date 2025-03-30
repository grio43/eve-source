#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\loaders\scripted_behavior_loader.py
from behaviors.blackboards.scopes import ScopeTypes
from behaviors.loaders import BehaviorDoesNotExistError
from behaviors.trees.drifters.driftertree import CreateDrifterBehaviorTree, CreateHiveSystemDrifterBehaviorTree
from behaviors.trees.fighters import CreateFighterBehaviorTree
from behaviors.trees.groups.incursions import CreateDrifterGroupBehaviorTree, CreateGroupBehaviorTree
from behaviors.trees.harvesting import CreateHarvestOutpostBehaviorTree
from behaviors.trees.incursions.dungeonseekertree import CreateDungeonSeekerBehaviorTree
from behaviors.trees.miners.antidps import CreateAntiDpsBehaviorTree
from behaviors.trees.miners.antilogistics import CreateAntiLogisticsBehaviorTree
from behaviors.trees.miners.basicdpstree import CreateBasicDpsBehaviorTree
from behaviors.trees.miners.tackler import CreateTacklerBehaviorTree
from behaviors.trees.pirate.shadow_of_the_serpent_trees import CreateRoamingShadowOfTheSerpentTree, CreateShadowOfTheSerpentisGroupTree
from behaviors.trees.reinforcements import CreateReinforcementTree
from behaviors.trees.scoutsidle import CreateAnalyzeTree
from behaviors.trees.sleep import CreateSleepBehaviorTree
from behaviors.trees.sleeperscouts import CreateSleeperScoutBehaviorTree, CreateHiveSystemSleeperScoutBehaviorTree
from behaviors.trees.driftercommander.driftercommandertree import CreateDrifterCommanderBehaviorTree
from behaviors.trees.dungeonboss.dungeonbosstree import CreateDungeonBossBehaviorTree
from behaviors.trees.incursions.dungeondriftertree import CreateDungeonDrifterBehaviorTree
from behaviors.trees.incursions.roamingdriftertree import CreateRoamingDrifterBehaviorTree
from behaviors.registry import get_task_registry
from ccpProfile import TimedFunction

class ScriptedBehaviorLoader(object):

    def __init__(self):
        self.registry = get_task_registry()
        self.behaviors_by_scope_by_id = {ScopeTypes.Item: {'sleep': CreateSleepBehaviorTree,
                           'scan': CreateAnalyzeTree,
                           'reinforce': CreateReinforcementTree,
                           'harvest': CreateHarvestOutpostBehaviorTree,
                           'Roaming Sleeper Scout': CreateSleeperScoutBehaviorTree,
                           'Roaming Sleeper Scout In Hive System': CreateHiveSystemSleeperScoutBehaviorTree,
                           'Drifter Battleship': CreateDrifterBehaviorTree,
                           'Drifter Battleship In Hive System': CreateHiveSystemDrifterBehaviorTree,
                           'Drifter Commander': CreateDrifterCommanderBehaviorTree,
                           'Dungeon Boss': CreateDungeonBossBehaviorTree,
                           'Incursion Dungeon Drifter': CreateDungeonDrifterBehaviorTree,
                           'Incursion Dungeon Seeker': CreateDungeonSeekerBehaviorTree,
                           'Incursion Roaming Drifter': CreateRoamingDrifterBehaviorTree,
                           'fighter': CreateFighterBehaviorTree,
                           'Shadow Of The Serpent': CreateRoamingShadowOfTheSerpentTree,
                           'dps': CreateBasicDpsBehaviorTree,
                           'tackler': CreateTacklerBehaviorTree,
                           'antilogistics': CreateAntiLogisticsBehaviorTree,
                           'antidps': CreateAntiDpsBehaviorTree},
         ScopeTypes.EntityGroup: {'sleep': CreateSleepBehaviorTree,
                                  'Incursion Group': CreateGroupBehaviorTree,
                                  'Incursion Drifter Group': CreateDrifterGroupBehaviorTree,
                                  'Shadow Of The Serpent Group': CreateShadowOfTheSerpentisGroupTree}}

    @TimedFunction('behaviors::loaders::ScriptedBehaviorLoader::load')
    def load(self, behavior_id, scope_type = None):
        behavior_tree_script = None
        if scope_type:
            if scope_type in self.behaviors_by_scope_by_id:
                behaviors_by_id = self.behaviors_by_scope_by_id.get(scope_type)
                if behaviors_by_id:
                    behavior_tree_script = behaviors_by_id.get(behavior_id)
        else:
            for behaviors_by_id in self.behaviors_by_scope_by_id:
                if behavior_id in behaviors_by_id:
                    behavior_tree_script = behaviors_by_id[behavior_id]

        if behavior_tree_script is None:
            raise BehaviorDoesNotExistError()
        behavior_tree = behavior_tree_script()
        behavior_tree.behaviorId = behavior_id
        behavior_tree.scopeType = scope_type
        return behavior_tree

    def get_id_and_names_by_scope(self, scope_type):
        return [ (str(behavior_id), '[Python] %s' % behavior_id) for behavior_id in self.behaviors_by_scope_by_id.get(scope_type, []) ]

    def convert_script_to_fsd(self, behavior_id, scope_type):
        behavior_tree = self.load(behavior_id, scope_type=scope_type)
        root_task = behavior_tree.GetRootTask()
        behavior_tree_data = {'name': behavior_id,
         'description': behavior_id,
         'scopeType': scope_type,
         'root': self.convert_task_to_dict(root_task)}
        return behavior_tree_data

    def convert_task_to_dict(self, task):
        task_name = get_class_name(task)
        subTasks = []
        if task.HasSubTasks():
            for sub in task.GetSubTasks():
                subTasks.append(self.convert_task_to_dict(sub))

        return {'taskClass': task_name,
         'attributes': self.convert_attributes(task_name, task.attributes),
         'subTasks': subTasks}

    def convert_attributes(self, task_name, attributes):
        try:
            return {name:self.convert_value_to_fsd(task_name, name, value) for name, value in attributes.iteritems()}
        except:
            raise

    def convert_value_to_fsd(self, task_name, name, value):
        if name == 'name':
            return value
        task_attributes = self.registry.get_class_attributes(task_name)
        attribute = task_attributes[name]
        return attribute.convert_attribute_to_fsd(value)


def get_class_name(task):
    return '%s.%s' % (task.__class__.__module__, task.__class__.__name__)
