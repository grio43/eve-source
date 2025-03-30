#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fleet\panelFormFleet.py
import localization.util
from carbonui import uiconst
from carbonui.control.button import Button
from carbonui.control.combo import Combo
from carbonui.control.comboEntryData import ComboEntryData
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.layoutGrid import LayoutGrid
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveCaptionMedium
from evefleet.client.util import GetFleetSetupOptionHint
from evefleet.fleetSetupConst import FS_NAME
from localization import GetByLabel

class PanelFormFleet(Container):

    def __init__(self, **kwargs):
        self._setup_choice = None
        super(PanelFormFleet, self).__init__(**kwargs)

    def ApplyAttributes(self, attributes):
        super(PanelFormFleet, self).ApplyAttributes(attributes)
        scroll_cont = ScrollContainer(parent=self)
        EveCaptionMedium(parent=scroll_cont, align=uiconst.TOTOP, text=GetByLabel('UI/Fleet/FleetWindow/FormFleetHeader'))
        EveLabelMedium(parent=scroll_cont, align=uiconst.TOTOP, padTop=4, text=GetByLabel('UI/Fleet/FleetWindow/FormFleetDescription'))
        grid = LayoutGrid(parent=ContainerAutoSize(parent=self, align=uiconst.TOBOTTOM, padTop=8, idx=0), align=uiconst.TOPLEFT, columns=2, cellSpacing=(8, 8))
        Button(parent=grid, align=uiconst.TOPLEFT, label=GetByLabel('UI/Fleet/FleetWindow/FormFleet'), func=self._form_fleet, args=())
        self._setup_choice = Combo(parent=grid, align=uiconst.TOPLEFT, options=get_fleet_setup_options())

    def _form_fleet(self):
        setup = self._setup_choice.GetValue()
        return sm.GetService('fleet').StartNewFleet(setup)


def get_fleet_setup_options():
    setups = [(GetByLabel('UI/Fleet/FleetWindow/DefaultSetup'), None)]
    fleet_service = sm.GetService('fleet')
    comboData = [ ComboEntryData(info[FS_NAME], info[FS_NAME], hint=GetFleetSetupOptionHint(info)) for info in fleet_service.GetFleetSetups().values() ]
    setups.extend(localization.util.Sort(comboData, key=lambda x: x.returnValue.lower()))
    return setups
