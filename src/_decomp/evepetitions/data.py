#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evepetitions\data.py
import logging
import localization
from caching import Memoize
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import petitionPropertiesLoader
except ImportError:
    petitionPropertiesLoader = None

try:
    import petitionCategoryPropertiesLoader
except ImportError:
    petitionCategoryPropertiesLoader = None

try:
    import petitionEventsLoader
except ImportError:
    petitionEventsLoader = None

log = logging.getLogger(__name__)

class PetitionCategoryProperties(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/petitionCategoryProperties.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/petitionCategoryProperties.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/petitionCategoryProperties.fsdbinary'
    __loader__ = petitionCategoryPropertiesLoader


class PetitionProperties(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/petitionProperties.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/petitionProperties.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/petitionProperties.fsdbinary'
    __loader__ = petitionPropertiesLoader


class PetitionEvents(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/petitionEvents.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/petitionEvents.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/petitionEvents.fsdbinary'
    __loader__ = petitionEventsLoader


def _get_petition_properties():
    return PetitionProperties.GetData()


def _get_petition_property(property_id):
    return _get_petition_properties().get(property_id)


def petition_property_exists(property_id):
    return _get_petition_property(property_id) is not None


def _get_petition_property_attribute(property_id, attribute, default = None):
    prop = _get_petition_property(property_id)
    if prop is not None:
        return getattr(prop, attribute)
    return default


def get_property_name(property_id):
    return _get_petition_property_attribute(property_id, 'propertyName')


def get_property_output_template(property_id):
    return _get_petition_property_attribute(property_id, 'outputTemplate')


def property_is_obsolete(property_id):
    return _get_petition_property_attribute(property_id, 'obsolete', False)


def property_is_required(property_id):
    return _get_petition_property_attribute(property_id, 'required', False)


def get_property_required_int(property_id):
    prop = _get_petition_property(property_id)
    if prop is None:
        return
    if prop.required:
        return 1
    return 0


def get_property_description_id(property_id):
    return _get_petition_property_attribute(property_id, 'descriptionID')


def get_property_input_type(property_id):
    return _get_petition_property_attribute(property_id, 'inputType')


def get_property_input_info(property_id):
    return _get_petition_property_attribute(property_id, 'inputInfo')


def get_property_description(property_id):
    description_id = _get_petition_property_attribute(property_id, 'descriptionID')
    if description_id is not None:
        return localization.GetByMessageID(description_id)


def get_non_obsolete_properties():
    property_ids = set()
    for property_id in _get_petition_properties():
        if property_is_obsolete(property_id):
            continue
        property_ids.add(property_id)

    return property_ids


def get_property_order_weight(property_id):
    return _get_petition_property_attribute(property_id, 'orderWeight')


def _get_petition_category_properties():
    return PetitionCategoryProperties.GetData()


@Memoize
def get_category_by_property_id():
    category_by_property_id = {}
    category_props = _get_petition_category_properties()
    for category_id, props in category_props.iteritems():
        for propertyID in props:
            if propertyID in category_by_property_id:
                log.error('petitionCategoryPropertiesFSD: One property ID per category ID constraint broken')
            category_by_property_id[propertyID] = category_id

    return category_by_property_id


def get_category_id(property_id):
    category_by_property_id = get_category_by_property_id()
    return category_by_property_id.get(property_id)


def _get_category_property(property_id):
    category_id = get_category_id(property_id)
    props = _get_petition_category_properties()
    return props.get(category_id, {}).get(property_id, None)


def get_category_property_name_id(property_id):
    prop = _get_category_property(property_id)
    return prop.propertyNameID


def get_category_property_seq_number(property_id):
    prop = _get_category_property(property_id)
    return prop.seq


def _get_petition_events():
    return PetitionEvents.GetData()


def _get_petition_event(event_id):
    return _get_petition_events().get(event_id)


def get_petition_event_ids():
    return set(_get_petition_events().iterkeys())


def get_event_text(event_id):
    event = _get_petition_event(event_id)
    return localization.GetByMessageID(event.eventTextID)


def petition_event_exists(event_id):
    return event_id in get_petition_event_ids()


def get_petition_event_texts():
    return {event_id:get_event_text(event_id) for event_id in get_petition_event_ids()}
