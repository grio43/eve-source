#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\billtypes\data.py
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import localization
except ImportError:
    localization = None

try:
    import billTypesLoader
except ImportError:
    billTypesLoader = None

class BillTypes(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/billTypes.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/billTypes.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/billTypes.fsdbinary'
    __loader__ = billTypesLoader


def get_bill_types():
    return BillTypes.GetData()


def get_bill_type_ids():
    return [ x for x in get_bill_types().iterkeys() ]


def get_bill_type_name(bill_type_id):
    bill_type = get_bill_types().get(bill_type_id, None)
    if bill_type is not None:
        return bill_type.billTypeName


def get_bill_type_name_id(bill_type_id):
    bill_type = get_bill_types().get(bill_type_id, None)
    if bill_type is not None and hasattr(bill_type, 'nameID'):
        return bill_type.nameID
