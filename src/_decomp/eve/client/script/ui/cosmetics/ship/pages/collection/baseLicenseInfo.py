#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\collection\baseLicenseInfo.py
from carbonui import Align
from carbonui.primitives.container import Container
from cosmetics.client.ships import ship_skin_signals
from eve.client.script.ui.cosmetics.ship.pages.collection import collectionSignals

class LicenseInfo(Container):
    default_alignMode = Align.TOTOP
    default_opacity = 0.0

    def __init__(self, *args, **kwargs):
        super(LicenseInfo, self).__init__(*args, **kwargs)
        self.construct_layout()
        self.connect_signals()

    def Close(self):
        try:
            self.disconnect_signals()
        finally:
            super(LicenseInfo, self).Close()

    def connect_signals(self):
        collectionSignals.on_first_party_skin_selected.connect(self.on_first_party_skin_selected)
        collectionSignals.on_activated_skin_license_selected.connect(self.on_activated_skin_license_selected)
        collectionSignals.on_unactivated_skin_license_selected.connect(self.on_unactivated_skin_license_selected)
        collectionSignals.on_component_license_selected.connect(self.on_component_license_selected)
        ship_skin_signals.on_skin_license_activated.connect(self.on_skin_license_activated)
        ship_skin_signals.on_skin_state_set.connect(self.on_skin_state_set)

    def disconnect_signals(self):
        collectionSignals.on_first_party_skin_selected.disconnect(self.on_first_party_skin_selected)
        collectionSignals.on_activated_skin_license_selected.disconnect(self.on_activated_skin_license_selected)
        collectionSignals.on_unactivated_skin_license_selected.disconnect(self.on_unactivated_skin_license_selected)
        collectionSignals.on_component_license_selected.disconnect(self.on_component_license_selected)
        ship_skin_signals.on_skin_license_activated.disconnect(self.on_skin_license_activated)
        ship_skin_signals.on_skin_state_set.disconnect(self.on_skin_state_set)

    def construct_layout(self):
        pass

    def update(self):
        pass

    def on_first_party_skin_selected(self, *args):
        pass

    def on_unactivated_skin_license_selected(self, skin_license):
        pass

    def on_activated_skin_license_selected(self, skin_license):
        pass

    def on_component_license_selected(self, *args):
        pass

    def on_skin_license_activated(self, *args):
        self.update()

    def on_skin_state_set(self, _ship_instance_id, _skin_state):
        pass
