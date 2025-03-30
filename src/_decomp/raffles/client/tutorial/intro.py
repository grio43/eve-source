#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\tutorial\intro.py
import eveui
from raffles.client.tutorial.page import WelcomePage, BrowsePage, BuyPage, WinPage
from raffles.client.tutorial.panel import TutorialPanel
from raffles.client.tutorial.controller import TutorialController
INTRODUCTION_SEEN_KEY = 'hyper_net_introduction_seen'

def have_seen_introduction():
    return settings.char.ui.Get(INTRODUCTION_SEEN_KEY, False)


def show_introduction(container):
    pages = [WelcomePage(),
     BrowsePage(),
     BuyPage(),
     WinPage()]
    controller = TutorialController(pages=pages)
    controller.on_closed.connect(set_introduction_seen)
    panel = TutorialPanel(parent=container, align=eveui.Align.center, tutorial_controller=controller, opacity=0.0)
    eveui.fade_in(panel, duration=0.3)
    return controller


def set_introduction_seen(seen = True):
    settings.char.ui.Set(INTRODUCTION_SEEN_KEY, seen)
