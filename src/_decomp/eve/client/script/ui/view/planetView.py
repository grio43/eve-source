#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\view\planetView.py
import carbonui.const as uiconst
import uthread
from eve.client.script.ui.services.viewStateSvc import View
from eve.client.script.ui.shared.planet.planetNavigation import PlanetLayer

class PlanetView(View):
    __guid__ = 'viewstate.PlanetView'
    __notifyevents__ = ['OnUIRefresh']
    __dependencies__ = []
    __layerClass__ = PlanetLayer

    def CanEnter(self, planetID = None, **kwargs):
        canEnter = True
        if planetID is None:
            self.LogInfo('Must have a valid planetID to open planet view')
            canEnter = False
        elif self.IsActive() and planetID == sm.GetService('planetUI').planetID:
            self.LogInfo('Planet', planetID, 'is already open and loaded')
            canEnter = False
        if canEnter:
            try:
                sm.GetService('planetSvc').GetPlanet(planetID)
            except UserError as e:
                eve.Message(*e.args)
                canEnter = False

        return canEnter

    def CanExit(self):
        currentPlanet = sm.GetService('planetUI').GetCurrentPlanet()
        if currentPlanet and currentPlanet.IsInEditMode():
            if eve.Message('ExitPlanetModeWhileInEditMode', {}, uiconst.YESNO) != uiconst.ID_YES:
                return False
            currentPlanet.RevertChanges()
        return True

    def LoadView(self, planetID = None, **kwargs):
        planetUI = sm.GetService('planetUI')
        if self.IsActive():
            planetUI.Close(clearAll=False)
        planetUI._Open(planetID)
        self.lastPlanetID = planetID

    def UnloadView(self):
        planetUI = sm.GetService('planetUI')
        planetUI.Close()

    def OnUIRefresh(self):
        uthread.new(self._ReOpen)

    def _ReOpen(self):
        viewState = sm.GetService('viewState')
        viewState.CloseSecondaryView('planet')
        planetID = getattr(self, 'lastPlanetID', None)
        viewState.ActivateView('planet', planetID=planetID)
