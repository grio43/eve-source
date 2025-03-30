#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dynamicresources\client\ui\link.py
from evelink.client import default_with_subtle_color_info
SCHEME_ESS_TRANSACTION_HISTORY = 'essTransactionHistory'

def register_link_handlers(registry):
    registry.register(scheme=SCHEME_ESS_TRANSACTION_HISTORY, handler=handle_ess_transaction_history_link, color_info=default_with_subtle_color_info)


def handle_ess_transaction_history_link(url):
    from dynamicresources.client.ui.transaction_history_window import TransactionHistoryWindow
    action = url.split(':')[1]
    if action == 'reserveBank':
        TransactionHistoryWindow.OpenToReserveBank()
    elif action == 'mainBank':
        TransactionHistoryWindow.OpenToMainBank()
