#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\walletConst.py
from eve.common.lib import appConst
from eve.common.lib import appConst as const
SETTINGS_PERSONAL = ('notifyAccountChange', 'notifyShareChange', 'walletShowCents', 'walletShowBalanceUpdates', 'walletShowLpUpdates')
SETTINGS_CORP = ('notifyAccountChangeCorp', 'notifyBillChange', 'notifyShareChangeCorp')
SETTING_DEFAULTS = {'notifyAccountChange': False,
 'notifyAccountChangeCorp': False,
 'notifyBillChange': True,
 'notifyShareChange': True,
 'notifyShareChangeCorp': True,
 'walletShowCents': False,
 'walletShowBalanceUpdates': True,
 'iskNotifyThreshold': 0,
 'walletShowLpUpdates': True}
SETTING_LABELS = {'notifyAccountChange': 'UI/Wallet/WalletWindow/NotifyAccountChange',
 'notifyAccountChangeCorp': 'UI/Wallet/WalletWindow/NotifyAccountChange',
 'notifyBillChange': 'UI/Wallet/WalletWindow/NotifyBillChange',
 'notifyShareChange': 'UI/Wallet/WalletWindow/NotifyShareChange',
 'notifyShareChangeCorp': 'UI/Wallet/WalletWindow/NotifyShareChange',
 'walletShowCents': 'UI/Wallet/WalletWindow/WalletShowCents',
 'walletShowBalanceUpdates': 'UI/Wallet/WalletWindow/Configuration/WalletShowBalanceChange',
 'walletShowLpUpdates': 'UI/Wallet/WalletWindow/Configuration/WalletShowLpUpdate'}
SKIP_REF_TYPES = [const.refATMWithdraw,
 const.refATMDeposit,
 const.refBackwardCompatible,
 const.refFactorySlotRentalFee,
 18,
 const.refMissionExpiration,
 const.refMissionCompletion,
 const.refCourierMissionEscrow,
 const.refMissionCost,
 const.refAgentDonation,
 const.refAgentSecurityServices,
 32,
 const.refCSPAOfflineRefund,
 43,
 const.refMarketFinePaid,
 45,
 47,
 const.refTransactionTax,
 const.refDuplicating,
 const.refReverseEngineering]
WALLET_BILLS_SCROLLID = 'wallet_show_bills'
WALLET_DIVISIONS_SCROLLID = 'wallet_show_divisions'
WALLET_CORPTRANSACTIONS_SCROLLID = 'wallet_show_journal'
WALLET_SHARES_SCROLLID = 'wallet_show_shares'
WALLET_TRANSACTIONS_SCROLLID = 'wallet_show_transactions'
CURRENCY_DISPLAY_LABEL = 'UI/Wallet/WalletWindow/CurrencyDisplay'
PANEL_PERSONAL = 'personal'
PANEL_CORP = 'corp'
PANEL_SETTINGS = 'settings'
PANEL_PERSONALISK = 'mywallet'
PANEL_PLEX = 'plex'
PANEL_LP = 'loyaltypoints'
PANEL_EVERMARKS = 'evermarks'
PANEL_CORPISK = 'corpwallet'
PANEL_CORPLP = 'corplp'
PANEL_CORPEVERMARKS = 'corpevermarks'
PANEL_OVERVIEW = 'overview'
PANEL_TRANSACTIONS = 'transactions'
PANEL_SHARES = 'shares'
PANEL_MARKETTRANSACTIONS = 'marketTransactions'
PANEL_PAYSETTINGS = 'personalAutoPayment'
PANEL_GIVEISK = 'personalGiveISK'
PANEL_CORPBILLS = 'bills'
PANEL_CORPBILLS_PAYABLE = 'billsIn'
PANEL_CORPBILLS_RECEIVABLE = 'billsOut'
PANEL_CORPBILLS_AUTOPAY = 'automaticallyPaid'
PANEL_CORPBILLS_AUTOPAYSETTINGS = 'automaticpayment'
PANEL_CORPTRANSACTIONS = 'corpTransactions'
PANEL_CORPSHARES = 'shares'
PANEL_CORPSHARES_OWNED = 'shares_ownedby'
PANEL_CORPSHAREHOLDERS = 'shares_shareholders'
PANEL_CORPWALLETDIVISIONS = 'divisions'
PANEL_CORPMARKETTRANSACTIONS = 'corpMarketTransactions'
PANEL_LP_BALANCE = 'lp_balance'
PANEL_LP_INCURSIONS = 'lp_incursions'
PANEL_LP_DONATE = 'lp_donate'
PANEL_EM_BALANCE = 'em_balance'
PANEL_EM_DONATE = 'em_donate'
PANEL_CORP_LP_BALANCE = 'corp_lp_balance'
PANEL_CORP_LP_DONATE = 'corp_lp_donate'
PANEL_CORP_EM_ACTIONS = 'corp_em_actions'
PANEL_CORP_EM_DONATE = 'corp_em_donate'
corpWalletRoles = {1000: appConst.corpRoleAccountCanTake1,
 1001: appConst.corpRoleAccountCanTake2,
 1002: appConst.corpRoleAccountCanTake3,
 1003: appConst.corpRoleAccountCanTake4,
 1004: appConst.corpRoleAccountCanTake5,
 1005: appConst.corpRoleAccountCanTake6,
 1006: appConst.corpRoleAccountCanTake7}
ANIM_DURATION = 0.25
NUM_TRANSACTIONS_PER_PAGE = 100
