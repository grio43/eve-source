#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\neocom2\transaction.py
from eve.common.lib.appConst import corpHeraldry
from localization import GetByLabel

class Transaction(object):

    def __init__(self, new_balance, transaction):
        self.new_balance = new_balance
        self.transaction = transaction

    def __eq__(self, other):
        return (other.new_balance, other.transaction) == (self.new_balance, self.transaction)

    def __repr__(self):
        return '{}: ({}, {})'.format(self.__class__, self.new_balance, self.transaction)

    def get_value(self):
        return self.transaction

    def get_start_balance_value(self):
        return self.new_balance - self.transaction

    def _get_prefix(self, amount):
        if amount > 0:
            return '+'
        else:
            return ''

    def get_transaction_label(self):
        value = self.get_value()
        if value > 0:
            return GetByLabel('Tooltips/Neocom/WalletCredit')
        else:
            return GetByLabel('Tooltips/Neocom/WalletDebit')

    def get_formatted_value(self):
        value = self.get_value()
        return self.format_amount(value, use_prefix=True)

    def get_formatted_start_balance_value(self):
        value = self.get_start_balance_value()
        return self.format_amount(value, use_prefix=False)

    def format_amount(self, amount, use_prefix = False):
        formatted_amount = self._format_amount(amount)
        if use_prefix:
            prefix = self._get_prefix(amount)
            return '%s' % prefix + formatted_amount
        return formatted_amount

    def _format_amount(self, amount):
        raise NotImplementedError('Must implement _format_amount in derived class')

    def get_balance_label(self):
        raise NotImplementedError('Must implement get_balance_label in derived class')


class IskTransaction(Transaction):

    def _format_amount(self, amount):
        from eve.common.script.util.eveFormat import FmtISK
        return FmtISK(amount, showFractionsAlways=False)

    def get_balance_label(self):
        return GetByLabel('Tooltips/Neocom/Balance')


class LpTransaction(Transaction):

    def __init__(self, corporation_id, new_balance, transaction):
        self.corporation_id = corporation_id
        super(LpTransaction, self).__init__(new_balance, transaction)

    def _format_amount(self, amount):
        if self.corporation_id == corpHeraldry:
            return GetByLabel('UI/Common/NumEverMarksShort', quantity=int(amount))
        from eve.common.script.util.eveFormat import FmtLP
        return FmtLP(amount)

    def get_balance_label(self):
        corporation_name = cfg.eveowners.Get(self.corporation_id).name
        return GetByLabel('Tooltips/Neocom/LoyaltyPointBalance', corporationName=corporation_name)
