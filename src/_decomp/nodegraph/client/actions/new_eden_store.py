#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\actions\new_eden_store.py
from .base import Action
from ast import literal_eval
from logging import getLogger
logger = getLogger(__name__)

class SetFeaturedOffers(Action):
    atom_id = 583

    def __init__(self, offer_id_list = None, **kwargs):
        super(SetFeaturedOffers, self).__init__(**kwargs)
        self.offer_id_list = offer_id_list

    def start(self, **kwargs):
        super(SetFeaturedOffers, self).start(**kwargs)
        if self.offer_id_list:
            sm.GetService('vgsService').SetFeaturedOffers(self.offer_id_list)

    def stop(self):
        super(SetFeaturedOffers, self).stop()
        ClearFeaturedOffers().start()


class ClearFeaturedOffers(Action):
    atom_id = 584

    def start(self, **kwargs):
        super(ClearFeaturedOffers, self).start(**kwargs)
        sm.GetService('vgsService').SetFeaturedOffers()
