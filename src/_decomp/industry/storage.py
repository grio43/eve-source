#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\industry\storage.py
import collections
import fsdlite

def ActivityTargetFiltersStorage():
    try:
        return ActivityTargetFiltersStorage._storage
    except AttributeError:
        ActivityTargetFilterAttributes = collections.namedtuple('ActivityTargetFilterAttributes', ['categoryIDs', 'groupIDs', 'name'])
        mapping = [('$', ActivityTargetFilterAttributes)]
        ActivityTargetFiltersStorage._storage = fsdlite.EveStorage(data='industry/activity_target_filters', cache='industry_activity_target_filters.static', mapping=mapping, coerce=int)
        return ActivityTargetFiltersStorage._storage


def ActivityModifierSourcesStorage():
    try:
        return ActivityModifierSourcesStorage._storage
    except AttributeError:
        ActivityModifierSourcesAttributes = collections.namedtuple('ActivityModifierSourcesAttributes', ['copying',
         'invention',
         'manufacturing',
         'research_material',
         'research_time',
         'reaction'])
        ActivityAttributes = collections.namedtuple('ActivityAttributes', ['cost', 'material', 'time'])
        ModifierSourceAttributes = collections.namedtuple('ModifierSourceAttributes', ['dogmaAttributeID', 'filterID'])
        mapping = [('copying$', ActivityAttributes),
         ('invention$', ActivityAttributes),
         ('manufacturing$', ActivityAttributes),
         ('research_material$', ActivityAttributes),
         ('research_time$', ActivityAttributes),
         ('reaction$', ActivityAttributes),
         ('[a-z_]+.cost$', ModifierSourceAttributes),
         ('[a-z_]+.material$', ModifierSourceAttributes),
         ('[a-z_]+.time$', ModifierSourceAttributes),
         ('$', ActivityModifierSourcesAttributes)]
        ActivityModifierSourcesStorage._storage = fsdlite.EveStorage(data='industry/activity_modifier_sources', cache='industry_activity_modifier_sources.static', mapping=mapping, coerce=int)
        return ActivityModifierSourcesStorage._storage


def ActivitiesStorage():
    try:
        return ActivitiesStorage._storage
    except AttributeError:
        ActivitiesAttributes = collections.namedtuple('ActivitiesAttributes', ['activityID', 'activityName', 'description'])
        mapping = [('$', ActivitiesAttributes)]
        ActivitiesStorage._storage = fsdlite.EveStorage(data='industry/activities', cache='industry_activities.static', mapping=mapping, coerce=int)
        return ActivitiesStorage._storage


def AssemblylineStorage():
    try:
        return AssemblylineStorage._storage
    except AttributeError:
        AssemblylineAttributes = collections.namedtuple('AssemblylineAttributes', ['id',
         'name',
         'description',
         'activity',
         'base_time_multiplier',
         'base_material_multiplier',
         'base_cost_multiplier',
         'details_per_type_list',
         'details_per_group',
         'details_per_category'])
        TypeDetailAttributes = collections.namedtuple('TypeDetailAttributes', ['type_list_id',
         'time_multiplier',
         'material_multiplier',
         'cost_multiplier'])
        GroupDetailAttributes = collections.namedtuple('GroupDetailAttributes', ['groupID',
         'time_multiplier',
         'material_multiplier',
         'cost_multiplier'])
        CategoryDetailAttributes = collections.namedtuple('CategoryDetailAttributes', ['categoryID',
         'time_multiplier',
         'material_multiplier',
         'cost_multiplier'])
        mapping = [('id$', AssemblylineAttributes),
         ('name$', AssemblylineAttributes),
         ('description$', AssemblylineAttributes),
         ('activity$', AssemblylineAttributes),
         ('base_time_multiplier$', AssemblylineAttributes),
         ('base_material_multiplier$', AssemblylineAttributes),
         ('base_cost_multiplier$', AssemblylineAttributes),
         ('details_per_type_list$', TypeDetailAttributes),
         ('details_per_group$', GroupDetailAttributes),
         ('details_per_category$', CategoryDetailAttributes)]
        AssemblylineStorage._storage = fsdlite.EveStorage(data='industry/assembly_lines', cache='industry_assembly_lines.static', mapping=mapping, coerce=int)
        return AssemblylineStorage._storage


def InstallationTypeStorage():
    try:
        return InstallationTypeStorage._storage
    except AttributeError:
        InstallationTypeAttributes = collections.namedtuple('InstallationTypeAttributes', ['type_id', 'assembly_lines'])
        mapping = [('$', InstallationTypeAttributes)]
        InstallationTypeStorage._storage = fsdlite.EveStorage(data='industry/installation_types', cache='industry_installation_types.static', mapping=mapping, coerce=int)
        return InstallationTypeStorage._storage


def CloseStorage():
    ActivityTargetFiltersStorage().cache.close()
    ActivityModifierSourcesStorage().cache.close()
    ActivitiesStorage().cache.close()
    AssemblylineStorage().cache.close()
    InstallationTypeStorage().cache.close()
