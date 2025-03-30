#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dogma\data.py
import math
import re
import logging
from collections import defaultdict, namedtuple
import evetypes
from caching.memoize import Memoize
from dogma.const import attributeDataTypeTypeDamage, attributeMass, attributeCapacity, attributeVolume, attributeRadius
from dogma.identity import get_safe_dogma_identity
from fsdBuiltData.common.base import BuiltDataLoader
logger = logging.getLogger(__name__)
try:
    import typeDogmaLoader
except ImportError:
    typeDogmaLoader = None
    logger.debug('typeDogmaLoader not available')

try:
    import dogmaAttributesLoader
except ImportError:
    dogmaAttributesLoader = None
    logger.debug('dogmaAttributesLoader not available')

try:
    import dogmaAttributeCategoriesLoader
except ImportError:
    dogmaAttributeCategoriesLoader = None
    logger.debug('dogmaAttributeCategoriesLoader not available')

try:
    import dogmaEffectsLoader
except ImportError:
    dogmaEffectsLoader = None
    logger.debug('dogmaEffectsLoader not available')

charge_group_regex = re.compile('chargeGroup\\d{1,2}')
module_ship_group_regex = re.compile('moduleShipGroup\\d{1,2}')
DogmaTypeAttribute = namedtuple('DogmaTypeAttribute', ['attributeID', 'value'])

class DogmaAttributeCategories(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/dogmaAttributeCategories.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/dogmaAttributeCategories.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/dogmaAttributeCategories.fsdbinary'
    __loader__ = dogmaAttributeCategoriesLoader


class DogmaAttributes(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/dogmaAttributes.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/dogmaAttributes.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/dogmaAttributes.fsdbinary'
    __dataemporiumDatasetName__ = 'staticdata:/dogma/dogmaAttributes'
    __loader__ = dogmaAttributesLoader


class TypeDogma(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/typeDogma.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/typeDogma.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/typeDogma.fsdbinary'
    __dataemporiumDatasetName__ = 'staticdata:/dogma/typeDogma'
    __loader__ = typeDogmaLoader


class DogmaEffects(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/dogmaEffects.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/dogmaEffects.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/dogmaEffects.fsdbinary'
    __dataemporiumDatasetName__ = 'staticdata:/dogma/dogmaEffects'
    __loader__ = dogmaEffectsLoader


def _get_dogma_attributes():
    return DogmaAttributes.GetData()


def _get_type_dogma():
    return TypeDogma.GetData()


def get_type_dogma(type_id):
    type_id = get_safe_dogma_identity(type_id)
    return _get_type_dogma().get(type_id)


def refresh_dogma():
    for name, func in globals().iteritems():
        if callable(func) and hasattr(func, 'clear_memoized'):
            logger.debug('clearing memoize cache for dogma function %s', name)
            func.clear_memoized()


def _get_effects():
    return DogmaEffects.GetData()


def _get_attribute_categories():
    return DogmaAttributeCategories.GetData()


def get_all_attributes():
    return _get_dogma_attributes().values()


def get_all_attribute_ids():
    return _get_dogma_attributes().keys()


@Memoize
def get_all_attributes_by_name():
    return {attribute.name:attribute for attribute in _get_dogma_attributes().itervalues()}


def get_all_attributes_by_id():
    return _get_dogma_attributes()


@Memoize
def get_attribute_names_by_id():
    return {attribute.attributeID:attribute.name for attribute in _get_dogma_attributes().itervalues()}


@Memoize
def get_attribute_ids_by_name():
    return {attribute.name:attribute.attributeID for attribute in _get_dogma_attributes().itervalues()}


@Memoize
def get_attributes_sorted_by_name():
    return tuple(sorted(get_all_attributes(), key=lambda x: x.name))


@Memoize
def get_attribute_list_by_data_type():
    attribute_list_by_category_id = {}
    for attribute in _get_dogma_attributes().itervalues():
        if attribute.dataType not in attribute_list_by_category_id:
            attribute_list_by_category_id[attribute.dataType] = [attribute]
        else:
            attribute_list_by_category_id[attribute.dataType].append(attribute)

    return attribute_list_by_category_id


@Memoize
def get_attribute_list_by_charge_recharge_time_id():
    attribute_list_by_charge_recharge_time_id = {}
    for attribute in _get_dogma_attributes().itervalues():
        if not getattr(attribute, 'chargeRechargeTimeID', False):
            continue
        if attribute.chargeRechargeTimeID not in attribute_list_by_charge_recharge_time_id:
            attribute_list_by_charge_recharge_time_id[attribute.chargeRechargeTimeID] = [attribute]
        else:
            attribute_list_by_charge_recharge_time_id[attribute.chargeRechargeTimeID].append(attribute)

    return attribute_list_by_charge_recharge_time_id


@Memoize
def get_charge_group_attributes():
    return tuple((a for a in _get_dogma_attributes().itervalues() if charge_group_regex.match(a.name) is not None))


@Memoize
def get_charge_group_attribute_ids():
    return frozenset((a.attributeID for a in get_charge_group_attributes()))


@Memoize
def get_module_ship_group_attributes():
    return tuple((a for a in _get_dogma_attributes().itervalues() if module_ship_group_regex.match(a.name) is not None))


@Memoize
def get_module_ship_group_attribute_ids():
    return frozenset((a.attributeID for a in get_module_ship_group_attributes()))


def get_attribute(attribute_id):
    attribute_id = get_safe_dogma_identity(attribute_id)
    return _get_dogma_attributes()[attribute_id]


def get_attribute_with_default(attribute_id, default_value = None):
    if is_attribute(attribute_id):
        return get_attribute(attribute_id)
    else:
        return default_value


def is_attribute(attribute_id):
    return attribute_id in _get_dogma_attributes()


def get_attribute_data_type(attribute_id):
    return get_attribute(attribute_id).dataType


def get_attribute_name(attribute_id):
    return get_attribute(attribute_id).name


def get_attribute_default_value(attribute_id):
    return get_attribute(attribute_id).defaultValue


def get_attribute_icon_id(attribute_id):
    return get_attribute(attribute_id).iconID


def get_attribute_display_name(attribute_id):
    import localization
    attribute = get_attribute(attribute_id)
    if attribute.displayNameID:
        return localization.GetByMessageID(attribute.displayNameID)
    else:
        return ''


def get_attribute_unit_id(attribute_id):
    return get_attribute(attribute_id).unitID


@Memoize
def get_type_attributes(type_id):
    type_dogma = get_type_dogma(type_id)
    if type_dogma:
        attributes = [ attribute for attribute in type_dogma.dogmaAttributes ]
    else:
        attributes = []
    attributes.extend([DogmaTypeAttribute(attributeID=attributeMass, value=evetypes.GetMass(type_id)),
     DogmaTypeAttribute(attributeID=attributeCapacity, value=evetypes.GetCapacity(type_id)),
     DogmaTypeAttribute(attributeID=attributeVolume, value=evetypes.GetVolume(type_id)),
     DogmaTypeAttribute(attributeID=attributeRadius, value=evetypes.GetRadius(type_id))])
    return attributes


@Memoize
def get_type_attributes_raw(type_id):
    type_dogma = get_type_dogma(type_id)
    if type_dogma:
        attributes = [ attribute for attribute in type_dogma.dogmaAttributes ]
    else:
        attributes = []
    return attributes


def get_type_attribute(type_id, attribute_id, default_value = None):
    attribute = get_type_attributes_by_id(type_id).get(attribute_id)
    if attribute:
        return attribute.value
    else:
        return default_value


def get_type_attribute_or_default(type_id, attribute_id):
    attribute = get_type_attribute(type_id, attribute_id)
    if attribute is None:
        return get_attribute_default_value(attribute_id)
    else:
        return attribute


@Memoize
def get_type_attributes_by_id(type_id):
    return {type_attribute.attributeID:type_attribute for type_attribute in get_type_attributes(type_id)}


def get_type_attribute_values_by_id(type_id):
    type_attributes = get_type_attributes_by_id(type_id)
    return {attribute_id:attribute.value for attribute_id, attribute in type_attributes.iteritems()}


def get_type_and_value_by_attribute_id(attribute_id):
    type_and_value_by_attribute_id = {}
    for type_id, attributes in iter_type_id_and_attributes():
        for attribute in attributes:
            if attribute.attributeID == attribute_id:
                type_and_value_by_attribute_id[type_id] = attribute.value
                break

    return type_and_value_by_attribute_id


def has_type_attributes(type_id):
    attributes = get_type_attributes(type_id)
    return len(attributes) > 0


@Memoize
def get_type_id_set_by_attribute_id():
    type_id_set_by_attribute_id = defaultdict(set)
    for type_id, attributes in iter_type_id_and_attributes():
        for attribute in attributes:
            type_id_set_by_attribute_id[attribute.attributeID].add(type_id)

    return type_id_set_by_attribute_id


def iter_type_id_and_attributes():
    for type_id in _get_type_dogma().iterkeys():
        yield (type_id, get_type_attributes(type_id))


def get_all_effects():
    return _get_effects().values()


@Memoize
def get_all_effects_by_name():
    return {effect.effectName:effect for effect in _get_effects().itervalues()}


@Memoize
def get_all_effects_by_id():
    return {effect.effectID:effect for effect in _get_effects().itervalues()}


@Memoize
def get_all_effect_ids():
    return tuple(_get_effects().keys())


def is_effect(effect_id):
    return effect_id in _get_effects()


def get_effect(effect_id):
    effect_id = get_safe_dogma_identity(effect_id)
    return _get_effects()[effect_id]


def get_effect_with_default(effect_id, default_value = None):
    try:
        return get_effect(effect_id)
    except KeyError:
        return default_value


def get_effect_display_name(effect_id):
    import localization
    effect = get_effect(effect_id)
    if effect.displayNameID:
        return localization.GetByMessageID(get_effect(effect_id).displayNameID)
    else:
        return ''


def get_effect_description(effect_id):
    import localization
    effect = get_effect(effect_id)
    if effect.descriptionID:
        return localization.GetByMessageID(get_effect(effect_id).descriptionID)
    else:
        return ''


def get_effect_name(effect_id):
    return get_effect(effect_id).effectName


def get_effect_category(effect_id):
    return get_effect(effect_id).effectCategory


def is_effect_warp_safe(effect_id):
    return get_effect(effect_id).isWarpSafe


def is_effect_offensive(effect_id):
    return get_effect(effect_id).isOffensive


@Memoize
def get_all_type_effects():
    return {type_id:type_dogma.dogmaEffects for type_id, type_dogma in _get_type_dogma().iteritems()}


def get_type_effects(type_id):
    type_dogma = get_type_dogma(type_id)
    if type_dogma:
        return type_dogma.dogmaEffects
    return []


def get_type_effect_ids(type_id):
    return [ effect.effectID for effect in get_type_effects(type_id) ]


def get_type_effects_by_id(type_id):
    return {effect.effectID:effect for effect in get_type_effects(type_id)}


def has_type_effects(type_id):
    effects = get_type_effects(type_id)
    return len(effects) > 0


@Memoize
def get_all_type_effect_effects():
    return tuple((type_dogma.dogmaEffects for type_dogma in _get_type_dogma().itervalues()))


@Memoize
def get_all_type_ids_and_effects():
    return tuple(((type_id, type_dogma.dogmaEffects) for type_id, type_dogma in _get_type_dogma().iteritems()))


def get_attribute_categories_ids():
    return [ x for x in _get_attribute_categories().iterkeys() ]


def get_attribute_category(category_id):
    category_id = get_safe_dogma_identity(category_id)
    return _get_attribute_categories().get(category_id, None)


def get_all_attribute_categories():
    return {key:val for key, val in _get_attribute_categories().iteritems()}


@Memoize
def get_effects_indexed_by_type_id_and_effect_id():
    effects_dict_by_type_id = {}
    for type_id, effects in get_all_type_ids_and_effects():
        effects_by_id = {}
        for effect in effects:
            effects_by_id[effect.effectID] = effect

        effects_dict_by_type_id[type_id] = effects_by_id

    return effects_dict_by_type_id


@Memoize
def get_effects_indexed_by_effect_id_and_type_id():
    effects_dict_by_effect_id = {}
    for type_id, effects in get_all_type_ids_and_effects():
        for effect in effects:
            if effect.effectID not in effects_dict_by_effect_id:
                effects_dict_by_effect_id[effect.effectID] = {}
            effects_dict_by_effect_id[effect.effectID][type_id] = effect

    return effects_dict_by_effect_id


@Memoize
def get_charge_recharge_time_attributes_by_id():
    return {attribute.attributeID:attribute for attribute in get_all_attributes() if attribute.chargeRechargeTimeID and attribute.dataType != attributeDataTypeTypeDamage}


def get_attributes_by_charge_recharge_time_id():
    attributes_by_charge_recharge_time_id = defaultdict(list)
    for attribute in get_all_attributes():
        if attribute.chargeRechargeTimeID and attribute.dataType != attributeDataTypeTypeDamage:
            attributes_by_charge_recharge_time_id[attribute.chargeRechargeTimeID].append(attribute)

    return attributes_by_charge_recharge_time_id
