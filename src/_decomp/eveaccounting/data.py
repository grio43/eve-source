#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveaccounting\data.py
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import accountingEntryTypesLoader
except ImportError:
    accountingEntryTypesLoader = None

try:
    import accountingKeysLoader
except ImportError:
    accountingKeysLoader = None

class AccountingEntryTypes(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/accountingEntryTypes.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/accountingEntryTypes.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/accountingEntryTypes.fsdbinary'
    __loader__ = accountingEntryTypesLoader


class AccountingKeys(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/accountingKeys.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/accountingKeys.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/accountingKeys.fsdbinary'
    __loader__ = accountingKeysLoader


def get_entry_types():
    return AccountingEntryTypes.GetData()


def get_accounting_entry_type(entry_id):
    return get_entry_types().get(entry_id, None)


def iter_accounting_entry_types():
    return {entry_id for entry_id in get_entry_types()}


def get_entry_format_localization_id(entry_id):
    return get_accounting_entry_type(entry_id).entryJournalMessageID


def get_accounting_keys():
    return AccountingKeys.GetData()


def get_accounting_key_ids():
    return {key_id for key_id in get_accounting_keys()}


def get_accounting_key(key_id):
    accounting_keys = get_accounting_keys()
    return accounting_keys.get(key_id, None)


def get_accounting_key_for_name(name, default = None):
    accounting_keys = get_accounting_keys()
    for key_id, key in accounting_keys.iteritems():
        if key.keyName == name:
            return key_id

    return default


def get_accounting_key_name(key_id, default = None):
    key = get_accounting_key(key_id)
    if key:
        return key.keyName
    return default


def get_account_key_names_by_id():
    accounting_keys = get_accounting_keys()
    return {key_id:key.keyName for key_id, key in accounting_keys.iteritems()}


def get_account_key_ids_by_name():
    accounting_keys = get_accounting_keys()
    return {key.keyName:key_id for key_id, key in accounting_keys.iteritems()}


def get_accounting_key_name_id(key_id):
    key = get_accounting_key(key_id)
    if key:
        return key.keyNameID


def accounting_key_exists(key_id):
    return key_id in get_accounting_keys()


def get_accounting_key_currency(key_id):
    key = get_accounting_key(key_id)
    if key:
        return key.currency


def get_accounting_key_type(key_id):
    key = get_accounting_key(key_id)
    if key:
        return key.keyType
