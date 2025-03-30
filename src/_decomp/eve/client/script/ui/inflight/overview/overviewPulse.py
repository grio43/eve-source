#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\overview\overviewPulse.py
import logging
import uthread2
from eve.client.script.ui.inflight.overview import overviewConst
from signals import Signal
on_visible_entry_update = Signal('on_visible_entry_update')
_visible_entry_update_thread = None
log = logging.getLogger(__name__)

def connect_to_visible_entry_update_pulse(callback):
    global _visible_entry_update_thread
    if _visible_entry_update_thread is None:
        _visible_entry_update_thread = uthread2.start_tasklet(update_thread)
    on_visible_entry_update.connect(callback)


def update_thread():
    while True:
        on_visible_entry_update()
        uthread2.sleep(overviewConst.VISIBLE_ENTRY_UPDATE_SLEEP)
