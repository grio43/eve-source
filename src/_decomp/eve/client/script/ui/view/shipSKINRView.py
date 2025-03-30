#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\view\shipSKINRView.py
from eve.client.script.ui.services.viewStateSvc import View
from eve.client.script.ui.view.viewStateConst import ViewOverlay

class ShipSKINRView(View):
    __guid__ = 'viewstate.ShipSKINRView'
    __layerClass__ = None
    __suppressedOverlays__ = set(ViewOverlay.SidePanels)
