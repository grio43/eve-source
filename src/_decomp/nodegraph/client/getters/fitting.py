#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\getters\fitting.py
from .base import GetterAtom

class GetFittingWindowTabState(GetterAtom):
    atom_id = 580

    def get_values(self, **kwargs):
        super(GetFittingWindowTabState, self).get_values(**kwargs)
        from eve.client.script.ui.shared.fittingScreen.fittingWnd import FittingWindow
        fitting_window = FittingWindow.GetIfOpen()
        if fitting_window is None:
            return
        return {'tab_id': fitting_window.open_fitting_window_tab}
