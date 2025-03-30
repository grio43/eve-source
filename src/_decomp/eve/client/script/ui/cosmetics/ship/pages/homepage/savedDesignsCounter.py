#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\homepage\savedDesignsCounter.py
import uthread2
from carbonui import Align, TextBody, TextColor
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from cosmetics.client.ships import ship_skin_signals
from cosmetics.client.shipSkinDesignSvc import get_ship_skin_design_svc
from eve.client.script.ui.control.message import ShowQuickMessage

class SavedDesignsCounter(ContainerAutoSize):
    default_height = 18

    def __init__(self, *args, **kwargs):
        super(SavedDesignsCounter, self).__init__(*args, **kwargs)
        self.update_thread = None
        self.construct_layout()
        self.connect_signals()

    def Close(self):
        try:
            self.kill_threads()
            self.disconnect_signals()
        finally:
            super(SavedDesignsCounter, self).Close()

    def kill_threads(self):
        if self.update_thread is not None:
            self.update_thread.kill()
            self.update_thread = None

    def connect_signals(self):
        ship_skin_signals.on_skin_design_saved.connect(self.on_skin_design_saved)
        ship_skin_signals.on_skin_design_deleted.connect(self.on_skin_design_deleted)

    def disconnect_signals(self):
        ship_skin_signals.on_skin_design_saved.disconnect(self.on_skin_design_saved)
        ship_skin_signals.on_skin_design_deleted.disconnect(self.on_skin_design_deleted)

    def construct_layout(self):
        self.label = TextBody(name='label', parent=self, align=Align.TOLEFT, color=TextColor.SECONDARY)
        self.update()

    def update(self):
        self.update_thread = uthread2.StartTasklet(self.update_async)

    def update_async(self):
        try:
            self.update_label()
        except Exception as e:
            ShowQuickMessage(e.message)
            raise
        finally:
            self.update_thread = None

    def update_label(self):
        try:
            count = len(get_ship_skin_design_svc().get_all_owned_designs())
        except Exception as e:
            count = 0

        try:
            limit = get_ship_skin_design_svc().get_saved_designs_capacity()
        except Exception as e:
            limit = 0

        self.label.text = '{count}/{limit}'.format(count=count, limit=limit)

    def on_skin_design_saved(self, *args):
        self.update()

    def on_skin_design_deleted(self, *args):
        self.update()
