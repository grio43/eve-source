#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\fittingPanels\basePanel.py
import eveui
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.layoutGrid import LayoutGrid
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.shared.fitting.fittingUtil import EatSignalChangingErrors
from eve.client.script.ui.station.fitting.fittingTooltipUtils import SetFittingTooltipInfo
from signals.signalUtil import ChangeSignalConnect

class BaseMenuPanel(Container):
    default_iconSize = 32

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.iconSize = attributes.get('iconSize', self.default_iconSize)
        self.controller = attributes.controller
        self.ChangeSignalConnection()
        self.dogmaLocation = self.controller.GetDogmaLocation()
        self.SetShipID(self.controller.GetItemID())
        self.panelLoaded = False
        self.ResetStatsDicts()
        panelName = attributes.name
        tooltipName = attributes.tooltipName
        labelHint = attributes.labelHint
        self.headerParent = self.GetHeaderStatsParent('%s_HeaderStatsParent' % panelName)
        self.statusText = self.GetHeaderLabel(self.headerParent)
        if labelHint:
            self.statusText.hint = labelHint
        if tooltipName:
            SetFittingTooltipInfo(targetObject=self.statusText, tooltipName=tooltipName)

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.controller.on_new_itemID, self.OnNewShipLoaded)]
        ChangeSignalConnect(signalAndCallback, connect)

    @eveui.skip_if_destroyed
    def OnNewShipLoaded(self, *args):
        self.SetDogmaLocation()
        self.SetShipID(self.controller.GetItemID())

    def SetDogmaLocation(self):
        self.dogmaLocation = self.controller.GetDogmaLocation()

    def SetShipID(self, shipID):
        self.shipID = shipID

    def FinalizePanelLoading(self, initialLoad = False):
        self.panelLoaded = True
        if not initialLoad:
            self.controller.UpdateStats()

    def ResetStatsDicts(self):
        self.statsLabelsByIdentifier = {}
        self.statsIconsByIdentifier = {}
        self.statsContsByIdentifier = {}

    def GetHeaderStatsParent(self, name):
        return Container(name=name, parent=None, align=uiconst.TORIGHT, state=uiconst.UI_PICKCHILDREN, width=200)

    def GetHeaderLabel(self, parent):
        return EveLabelMedium(text='', parent=parent, left=8, top=1, aidx=0, state=uiconst.UI_NORMAL, align=uiconst.CENTERRIGHT)

    def SetStatusText(self, text, hintText = None):
        self.statusText.text = text
        if hintText:
            self.statusText.hint = hintText

    def SetLabel(self, identifier, text):
        label = self.statsLabelsByIdentifier.get(identifier, None)
        if label:
            label.text = text

    def LoadIcon(self, identifier, iconID):
        icon = self.statsIconsByIdentifier.get(identifier, None)
        if icon:
            icon.LoadIcon(iconID, ignoreSize=True)

    def GetValueCont(self, iconSize):
        attributeCont = LayoutGrid(columns=3, state=uiconst.UI_NORMAL, align=uiconst.CENTERLEFT, padTop=1)
        attributeCont.AddCell()
        attributeCont.AddCell(cellObject=Container(name='widthSpacer', align=uiconst.TOLEFT, width=7 + iconSize))
        attributeCont.FillRow()
        attributeCont.AddCell(cellObject=Container(name='heightSpacer', align=uiconst.TOTOP, height=26))
        return attributeCont

    def GetValueParentGrid(self, columns = 2):
        self.state = uiconst.UI_PICKCHILDREN
        l, t, w, h = self.GetAbsolute()
        step = w / columns
        parentGrid = LayoutGrid(name='parentGrid', parent=self, columns=columns, state=uiconst.UI_PICKCHILDREN, align=uiconst.TOTOP)
        for i in xrange(columns):
            parentGrid.AddCell(cellObject=Container(name='spacer', align=uiconst.TOLEFT, width=step))

        return parentGrid

    def Close(self):
        with EatSignalChangingErrors(errorMsg='BaseMenuPanel'):
            self.ChangeSignalConnection(connect=False)
        self.controller = None
        Container.Close(self)

    def IsCurrentShipReady(self):
        if not self.controller or not self.controller.CurrentShipIsLoaded():
            return False
        return True
