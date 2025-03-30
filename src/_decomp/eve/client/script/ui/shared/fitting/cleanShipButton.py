#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fitting\cleanShipButton.py
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.control.button import Button
from carbonui import const as uiconst
from eve.common.script.net import eveMoniker
from localization import GetByLabel
from eve.client.script.ui.view.viewStateConst import ViewState

class CleanShipButton(ContainerAutoSize):
    default_padding = 8

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.controller = attributes.controller
        self.AddButton()

    def AddButton(self):
        self.cleanButton = Button(label=GetByLabel('UI/Fitting/FittingWindow/CleanShip'), parent=self, align=uiconst.CENTER, func=self.CleanShip, soundClick='fitting_window_clean_ship_play')

    def CleanShip(self, *args):
        shipID = self.controller.GetItemID()
        newDirtTimestamp = eveMoniker.GetShipAccess().ResetDirtTimestamp(shipID)
        hangar_view = sm.GetService('viewState').GetView(ViewState.Hangar)
        if hangar_view is not None:
            hangar_view.OnDirtLevelChanged(shipID)
        print 'Ship cleaned! New dirt timestamp for ship %s is %s' % (shipID, newDirtTimestamp)

    def Close(self):
        self.controller = None
        Container.Close(self)

    def Enable(self, *args):
        return self.cleanButton.Enable()

    def Disable(self, *args):
        return self.cleanButton.Disable()
