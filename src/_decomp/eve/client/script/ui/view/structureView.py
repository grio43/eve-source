#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\view\structureView.py
from eve.client.script.ui.services.viewStateSvc import View
from eve.client.script.ui.structure.navigation import StructureLayer
from eve.client.script.ui.view.viewStateConst import ViewState
from evecamera import CAM_STRUCTURE

class StructureView(View):
    __guid__ = 'viewstate.StructureView'
    __suppressedOverlays__ = {'shipui', 'target'}
    __overlays__ = {'sidePanels'}
    __notifyevents__ = ['OnBallparkSetState']
    __dependencies__ = ['autoPilot', 'dockingHeroNotification']
    __layerClass__ = StructureLayer

    def ShowView(self, **kwargs):
        self.autoPilot.SetOff()
        settings.user.ui.Set('defaultStructureView', ViewState.Structure)
        sm.GetService('sceneManager').SetPrimaryCamera(CAM_STRUCTURE)

    def HideView(self):
        pass

    def OnBallparkSetState(self):
        if self.IsActive():
            sm.GetService('sceneManager').SetPrimaryCamera(CAM_STRUCTURE)
