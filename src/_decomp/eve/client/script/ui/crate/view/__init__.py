#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\crate\view\__init__.py
from .fixed import FixedView, FixedViewForRandomizedLoot
from .hacking import HackingView
LOOT_PRESENTATION_TO_VIEW_CLASS = {'fixed': FixedView,
 'hacking': HackingView}

def _GetViewClass(controller):
    amountOfLoot = len(controller.loot + controller.specialLoot)
    presentation = controller.staticData.lootPresentationType
    if presentation == 'hacking' and amountOfLoot > 8:
        return FixedViewForRandomizedLoot
    return LOOT_PRESENTATION_TO_VIEW_CLASS[presentation]


def CreateView(controller, **kwargs):
    viewClass = _GetViewClass(controller)
    return viewClass(controller=controller, **kwargs)
