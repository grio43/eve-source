#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\view\starMapView.py
from eve.client.script.ui.services.viewStateSvc import View
from eve.client.script.ui.shared.maps.navigation import StarMapLayer

class StarMapView(View):
    __guid__ = 'viewstate.StarMapView'
    __notifyevents__ = ['OnSessionChanged']
    __dependencies__ = ['map', 'starmap']
    __layerClass__ = StarMapLayer

    def __init__(self):
        View.__init__(self)

    def LoadView(self, **kwargs):
        settings.user.ui.Set('activeMap', 'starmap')
        self.starmap.InitMap()
        self.map.MinimizeWindows()
        self.map.OpenMapsPalette()
        sm.GetService('audio').SendUIEvent('ui_map_soundscape_play')

    def ShowView(self, interestID = None, starColorMode = None, drawRoute = None, tileMode = None, hightlightedSolarSystems = None, **kwargs):
        sm.ScatterEvent('OnMapModeChangeDone', 'starmap')
        if interestID:
            self.starmap.SetInterest(interestID, forceframe=True)
        if starColorMode:
            self.starmap.SetStarColorMode(starColorMode)
        if drawRoute:
            sourceID, destinationID = drawRoute
            self.starmap.DrawRouteTo(destinationID, sourceID=sourceID)
        if hightlightedSolarSystems:
            self.starmap.HighlightSolarSystems(hightlightedSolarSystems)
        if tileMode:
            self.starmap.SetTileMode(tileMode)

    def UnloadView(self):
        if 'starmap' in sm.GetActiveServices():
            self.starmap.CleanUp()
        if sm.GetService('viewState').isOpeningView != 'systemmap':
            self.map.ResetMinimizedWindows()
            self.map.CloseMapsPalette()
        sm.GetService('sceneManager').SetRegisteredScenes('default')
        activeScene = sm.GetService('sceneManager').GetActiveScene()
        if activeScene:
            activeScene.display = 1
        sm.GetService('audio').SendUIEvent('ui_map_soundscape_stop')

    def OnSessionChanged(self, isremote, session, change):
        self.starmap.ShowWhereIAm()

    def CheckShouldReopen(self, newKwargs, cachedKwargs):
        return True
