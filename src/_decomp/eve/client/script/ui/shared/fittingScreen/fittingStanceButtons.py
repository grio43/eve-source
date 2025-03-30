#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\fittingStanceButtons.py
from eve.client.script.ui.inflight.shipstance import ShipStanceButtonController

class GhostShipStanceButtonController(ShipStanceButtonController):

    def get_ship_stance(self, ship_id, type_id):
        return sm.GetService('ghostFittingSvc').GetSimulatedShipStance(ship_id, type_id)

    def set_stance(self, stance_id, ship_id, type_id):
        return sm.GetService('ghostFittingSvc').SetSimulatedStance(stance_id, ship_id)
