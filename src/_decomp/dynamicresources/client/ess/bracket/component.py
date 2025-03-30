#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dynamicresources\client\ess\bracket\component.py
import eveui
import spacecomponents.client
import threadutils
from dynamicresources.client.ess.bracket.root import EssBracket as EssBracketUi
from dynamicresources.client.service import get_dynamic_resource_service
from dynamicresources.common.ess.const import ESS_MAX_LINK_DISTANCE_METERS

class EssBracket(spacecomponents.Component):

    def __init__(self, itemID, typeID, attributes, componentRegistry):
        super(EssBracket, self).__init__(itemID, typeID, attributes, componentRegistry)
        self._bracket_ui = None
        self.SubscribeToMessage(spacecomponents.MSG_ON_ADDED_TO_SPACE, self._on_added_to_space)
        self.SubscribeToMessage(spacecomponents.MSG_ON_REMOVED_FROM_SPACE, self._on_removed_from_space)

    def _on_added_to_space(self, slim_item):
        if self._bracket_ui is None:
            self._bracket_ui = EssBracketUi(slim_item.itemID)
        self._start_range_update_loop()

    def _on_removed_from_space(self):
        if self._bracket_ui:
            self._bracket_ui.close()
            self._bracket_ui = None
        self._update_range_state(in_range=False)

    @threadutils.threaded
    def _start_range_update_loop(self):
        while self._bracket_ui is not None:
            eveui.wait_for_next_frame()
            ballpark = sm.GetService('michelle').GetBallpark()
            if ballpark is None:
                self._update_range_state(in_range=False)
                continue
            if any((ballpark.GetBall(item_id) is None for item_id in (self.itemID, session.shipid))):
                self._update_range_state(in_range=False)
                continue
            distance = ballpark.DistanceBetween(session.shipid, self.itemID)
            in_range = distance <= ESS_MAX_LINK_DISTANCE_METERS
            self._update_range_state(in_range)

    def _update_range_state(self, in_range):
        service = get_dynamic_resource_service()
        service.ess_state_provider.evolve(in_range=in_range)
