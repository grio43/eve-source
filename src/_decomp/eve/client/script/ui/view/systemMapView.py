#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\view\systemMapView.py
from eve.client.script.ui.services.viewStateSvc import View
from eve.client.script.ui.shared.infoPanels.infoPanelLocationInfo import InfoPanelLocationInfo
from eve.client.script.ui.shared.infoPanels.infoPanelRoute import InfoPanelRoute
from eve.client.script.ui.shared.infoPanels.infoPanelSearch import InfoPanelSearch
from eve.client.script.ui.shared.maps.navigation_systemmap import SystemMapLayer

class SystemMapView(View):
    __guid__ = 'viewstate.SystemMapView'
    __notifyevents__ = ['OnStateChange']
    __dependencies__ = ['map', 'station', 'bracket']
    __layerClass__ = SystemMapLayer
    __subLayers__ = (('l_systemMapBrackets', None, None),)

    def __init__(self):
        View.__init__(self)

    def LoadView(self, **kwargs):
        mapSvc = sm.GetService('map')
        mapSvc.MinimizeWindows()
        mapSvc.OpenMapsPalette()
        settings.user.ui.Set('activeMap', 'systemmap')
        systemMapSvc = sm.GetService('systemmap')
        systemMapSvc.InitMap()
        sm.ScatterEvent('OnMapModeChangeDone', 'systemmap')

    def UnloadView(self):
        if 'systemmap' in sm.GetActiveServices():
            sm.GetService('systemmap').CleanUp()
        if sm.GetService('viewState').isOpeningView != 'starmap':
            self.map.ResetMinimizedWindows()
            self.map.CloseMapsPalette()
        sm.GetService('map').CloseMapsPalette()
        sm.GetService('sceneManager').SetRegisteredScenes('default')
        activeScene = sm.GetService('sceneManager').GetActiveScene()
        if activeScene:
            activeScene.display = 1
