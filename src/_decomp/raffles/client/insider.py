#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\insider.py
from carbon.common.script.sys.serviceManager import ServiceManager
from carbonui.uicore import uicore
from eve.client.script.ui.util import uix
from raffles import RaffleStatus
from raffles.client.window import RaffleWindow

def get_insider_qa_menu():
    return ('HyperNet Relay (Raffles)', [('Seed offers', seed_raffles), ('Reset tutorials', reset_raffle_tutorials), ('Reset ALL seen raffle results', reset_raffle_seen_status)])


def seed_raffles():
    result = uix.QtyPopup(minvalue=1, maxvalue=10000, caption='How many?', label='', hint='Specify number the of offers to seed:')
    if result:
        ServiceManager.Instance().RemoteSvc('raffleMgr').QA_SeedRaffles(result['qty'])


def reset_raffle_tutorials():
    from raffles.client.tutorial import reset_tutorials
    reset_tutorials()


def reset_raffle_seen_status():
    window = RaffleWindow.GetIfOpen()
    if not window:
        uicore.Message('CustomNotify', {'notify': 'You need to have the HyperNet Relay window open to do that.'})
        return
    for raffle in window._controller._storage._raffles.itervalues():
        if raffle.raffle_status == RaffleStatus.finished_undelivered:
            raffle.update_winner_seen(False)
