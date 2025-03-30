#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dogma\units.py
from fsdBuiltData.common.base import BuiltDataLoader
import logging
logger = logging.getLogger(__name__)
try:
    import dogmaUnitsLoader
except ImportError:
    dogmaEffectsLoader = None
    logger.debug('dogmaUnitsLoader not available')

class DogmaUnits(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/dogmaUnits.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/dogmaUnits.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/dogmaUnits.fsdbinary'
    __loader__ = dogmaUnitsLoader


def _get_units():
    return DogmaUnits.GetData()


def get_all_units():
    return {unit_id:unit for unit_id, unit in _get_units().iteritems()}


def get_unit(unit_id):
    return _get_units()[unit_id]


def has_unit(unit_id):
    return unit_id in _get_units()


def get_display_name(unit_id):
    import localization
    unit = get_unit(unit_id)
    if unit.displayNameID:
        return localization.GetByMessageID(unit.displayNameID)
    else:
        return ''
