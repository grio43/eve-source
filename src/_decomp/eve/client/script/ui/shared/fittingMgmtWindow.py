#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingMgmtWindow.py
import eveicon
import evetypes
import log
import uthread2
from carbon.common.script.sys.serviceConst import ROLE_WORLDMOD
from carbonui import AxisAlignment, TextAlign, TextColor, uiconst
from carbonui.control.combo import Combo
from carbonui.control.comboEntryData import ComboEntryData
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.decorative.panelUnderlay import PanelUnderlay
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.util.various_unsorted import SortListOfTuples
from eve.client.script.ui.control import eveScroll
from carbonui.button.menu import MenuButtonIcon
from eve.common.lib import appConst as const
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.button import Button
from eve.client.script.ui.control.divider import Divider
from eve.client.script.ui.control.entries.fitting import FittingEntry
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.header import Header
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveLabel import EveCaptionLarge
from carbonui.control.window import Window
from eve.client.script.ui.control.listgroup import ListGroup
from eve.client.script.ui.shared.export import ExportFittingsWindow, ImportFittingsWindow
from eve.client.script.ui.shared.fitting.fittingMgmtCont import FittingMgmtContInWnd, FittingMgmtContInStandalone
from eve.client.script.ui.shared.fitting.fittingUtil import GetDeletableNodes, DeleteFittings
from eve.common.script.sys.eveCfg import IsDocked
from eveexceptions import ServiceNotFound, UserError
from globalConfig.getFunctions import GetMaxShipsToFit
from inventorycommon.const import numVisibleSubsystems
from inventorycommon.util import IsModularShip, IsSubsystemFlag
from localization import GetByLabel
from menu import MenuLabel
MENU_ICON_NO = 'ui_73_16_50'

class FittingMgmt(Window):
    __guid__ = 'form.FittingMgmt'
    __notifyevents__ = ['OnRedrawFittingMgmt']
    default_windowID = 'FittingMgmt'
    default_captionLabelPath = 'UI/Fitting/FittingWindow/FittingManagement/WindowCaption'
    default_iconNum = 'res:/ui/Texture/WindowIcons/fittingManagement.png'
    default_minSize = (525, 400)
    default_width = 620
    default_height = 600
    _left_cont = None
    _word_filter = None
    _export_button = None
    _fitting_management_cont = None
    _search_field = None
    _scroll = None
    _left_underlay = None

    def __init__(self, **kwargs):
        self._selected_owner_id = session.charid
        super(FittingMgmt, self).__init__(**kwargs)

    def ApplyAttributes(self, attributes):
        super(FittingMgmt, self).ApplyAttributes(attributes)
        self.DrawLeftSide()
        self.DrawRightSide()
        self.HideRightPanel()
        self.on_content_padding_changed.connect(self._on_window_content_padding_changed)

    @property
    def _fitting_service(self):
        return sm.GetService('fittingSvc')

    def DrawLeftSide(self):
        self._left_cont = Container(name='leftside', parent=self.content, align=uiconst.TOLEFT, width=256)
        self._left_underlay = PanelUnderlay(bgParent=self._left_cont, align=uiconst.TOALL, padding=self._get_left_underlay_padding())
        options = [ComboEntryData(label=GetByLabel('UI/Fitting/FittingWindow/FittingManagement/PersonalFittings'), returnValue=session.charid), ComboEntryData(label=GetByLabel('UI/Fitting/FittingWindow/FittingManagement/CorporationFittings'), returnValue=session.corpid)]
        if session.allianceid:
            options.append(ComboEntryData(label=GetByLabel('UI/Fitting/FittingWindow/FittingManagement/AllianceFittings'), returnValue=session.allianceid))
        selected = settings.user.ui.Get('savedFittingsCombo', None)
        if selected not in [ x.returnValue for x in options ]:
            selected = session.charid
        self._selected_owner_id = selected
        Combo(name='savedFittingsCombo', parent=self._left_cont, align=uiconst.TOTOP, padding=(0, 8, 8, 0), options=options, select=selected, callback=self.ChangeOwnerFilter)
        search_cont = ContainerAutoSize(name='searchContainer', parent=self._left_cont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, top=8, padRight=8)
        MenuButtonIcon(parent=ContainerAutoSize(parent=search_cont, align=uiconst.TOLEFT, left=-4), align=uiconst.CENTER, widht=24, height=24, texturePath=eveicon.load, iconSize=16, hint=GetByLabel('UI/Commands/Import'), get_menu_func=self._get_import_menu)
        ButtonIcon(parent=ContainerAutoSize(parent=search_cont, align=uiconst.TOLEFT), align=uiconst.CENTER, widht=24, height=24, texturePath=eveicon.export, iconSize=16, hint=GetByLabel('UI/Commands/Export'), func=self.ExportFittings)
        ButtonIcon(name='collapse', parent=ContainerAutoSize(parent=search_cont, align=uiconst.TOLEFT, padRight=8), align=uiconst.CENTER, width=24, height=24, iconSize=12, texturePath='res:/UI/Texture/classes/Scroll/Collapse.png', func=self.CollapseAll, hint=GetByLabel('UI/Common/Buttons/CollapseAll'))
        self._search_field = SingleLineEditText(name='searchTextField', parent=search_cont, align=uiconst.TOTOP, maxLength=40, OnChange=self.Search, OnReturn=self.Search, hintText=GetByLabel('UI/Common/Buttons/Search'))
        self._search_field.ShowClearButton()
        self._scroll = eveScroll.Scroll(parent=self._left_cont, align=uiconst.TOALL, padding=(0, 8, 0, 0))
        self.DrawFittings()
        divider = Divider(name='divider', parent=self.content, align=uiconst.TOLEFT, width=8, padRight=8, state=uiconst.UI_NORMAL, cross_axis_alignment=AxisAlignment.START)
        divider.Startup(self._left_cont, 'width', 'x', 160, 350)

    def _get_left_underlay_padding(self):
        pad_left, _, _, pad_bottom = self.content_padding
        return (-pad_left,
         0,
         0,
         -pad_bottom)

    def _update_left_underlay_padding(self):
        if self._left_underlay:
            self._left_underlay.padding = self._get_left_underlay_padding()

    def _on_window_content_padding_changed(self, window):
        self._update_left_underlay_padding()

    def _get_import_menu(self):
        menu = MenuData()
        menu.AddEntry(text=GetByLabel('UI/Fitting/FittingWindow/FittingManagement/ImportFromFile'), func=self.ImportFittings)
        menu.AddEntry(text=GetByLabel('UI/Fitting/FittingWindow/FittingManagement/ImportFromClipboard'), func=lambda : sm.GetService('fittingSvc').ImportFittingFromClipboard(), hint=GetByLabel('UI/Fitting/FittingWindow/FittingManagement/ImportFromClipboardHint'))
        return menu

    def ConstructImportExportButtons(self):
        fitButtons = FlowContainer(name='buttonParent', parent=self._left_cont, align=uiconst.TOBOTTOM, padding=6, autoHeight=True, centerContent=True, contentSpacing=uiconst.BUTTONGROUPMARGIN, idx=0)
        self._export_button = Button(parent=fitButtons, label=GetByLabel('UI/Commands/Export'), func=self.ExportFittings, align=uiconst.NOALIGN)
        Button(parent=fitButtons, label=GetByLabel('UI/Commands/Import'), func=self.ImportFittings, align=uiconst.NOALIGN)
        importFromClipboardButton = Button(parent=fitButtons, align=uiconst.NOALIGN, label=GetByLabel('UI/Fitting/FittingWindow/FittingManagement/ImportFromClipboard'), func=lambda button: sm.GetService('fittingSvc').ImportFittingFromClipboard())
        importFromClipboardButton.hint = GetByLabel('UI/Fitting/FittingWindow/FittingManagement/ImportFromClipboardHint')

    def DrawRightSide(self):
        self.noContentHint = EveCaptionLarge(parent=self.content, align=uiconst.TOTOP, padding=(32, 32, 32, 0), color=TextColor.SECONDARY, text=GetByLabel('UI/Fitting/FittingWindow/FittingManagement/NoFittingSelected'), textAlign=TextAlign.CENTER)
        self._fitting_management_cont = FittingMgmtContInWnd(parent=self.content, align=uiconst.TOALL)

    def EnableExportButton(self, enable):
        if enable:
            self._export_button.SetLabel(GetByLabel('UI/Commands/Export'))
            self._export_button.state = uiconst.UI_NORMAL
        else:
            self._export_button.SetLabel(GetByLabel('UI/Fitting/FittingWindow/FittingManagement/ExportDisabled'))
            self._export_button.state = uiconst.UI_DISABLED

    def Search(self, *args):
        self._perform_search()

    @uthread2.debounce(wait=0.3)
    def _perform_search(self):
        query = self._search_field.GetValue()
        if self._word_filter != query:
            self._word_filter = query
            self.DrawFittings()

    def CollapseAll(self, *args):
        self._scroll.CollapseAll()

    def ChangeOwnerFilter(self, combo, label, ownerID, *args):
        if self._selected_owner_id != ownerID:
            self._selected_owner_id = ownerID
            settings.user.ui.Set('savedFittingsCombo', ownerID)
            self.DrawFittings()
            self.HideRightPanel()

    def DrawFittings(self, *args):
        scrolllist = []
        fittings = self._fitting_service.GetFittings(self._selected_owner_id).items()
        fittingsByGroupID = {}
        shipGroups = []
        if self._word_filter:
            query = self._word_filter.lower()
            for fittingID, fitting in fittings[:]:
                if query not in fitting.name.lower():
                    fittings.remove((fittingID, fitting))

        for fittingID, fitting in fittings:
            shipTypeID = fitting.shipTypeID
            if not evetypes.Exists(shipTypeID):
                log.LogError('Ship in stored fittings does not exist, shipID=%s, fittingID=%s' % (shipTypeID, fittingID))
                continue
            groupID = evetypes.GetGroupID(shipTypeID)
            if groupID not in fittingsByGroupID:
                fittingsByGroupID[groupID] = []
            fittingsByGroupID[groupID].append(fitting)
            groupName = evetypes.GetGroupNameByGroup(groupID)
            if (groupName, groupID) not in shipGroups:
                shipGroups.append((groupName, groupID))

        shipGroups.sort()
        if len(fittings) == 0 and self._word_filter:
            scrolllist.append(GetFromClass(Generic, {'label': GetByLabel('UI/Common/NothingFound')}))
        else:
            if self._selected_owner_id == session.charid:
                maxFittings = const.maxCharFittings
            elif self._selected_owner_id == session.corpid:
                maxFittings = const.maxCorpFittings
            else:
                maxFittings = None
            if maxFittings is not None:
                label = GetByLabel('UI/Fitting/FittingWindow/FittingManagement/FittingsListHeader', numFittings=len(fittings), maxFittings=maxFittings)
                scrolllist.append(GetFromClass(Header, {'label': label,
                 'selectable': 0}))
            for groupName, groupID in shipGroups:
                scrolllist.append(GetFromClass(ListGroup, {'GetSubContent': self.GetShipGroupSubContent,
                 'label': groupName,
                 'fittings': fittingsByGroupID[groupID],
                 'groupItems': fittingsByGroupID[groupID],
                 'id': ('fittingMgmtScrollWndGroup', groupName),
                 'showicon': 'hide',
                 'state': 'locked',
                 'BlockOpenWindow': 1,
                 'selectable': 0}))

        self._scroll.Load(contentList=scrolllist)

    def GetShipGroupSubContent(self, nodedata, *args):
        scrolllist = []
        fittingsByType = {}
        shipTypes = []
        for fitting in nodedata.fittings:
            shipTypeID = fitting.shipTypeID
            if not evetypes.Exists(shipTypeID):
                log.LogError('Ship in stored fittings does not exist, shipID=%s, fittingID=%s' % (shipTypeID, fitting.fittingID))
                continue
            if shipTypeID not in fittingsByType:
                fittingsByType[shipTypeID] = []
            fittingsByType[shipTypeID].append(fitting)
            typeName = evetypes.GetName(shipTypeID)
            if (typeName, shipTypeID) not in shipTypes:
                shipTypes.append((typeName, shipTypeID))

        shipTypes.sort()
        for typeName, typeID in shipTypes:
            scrolllist.append(GetFromClass(ListGroup, {'GetSubContent': self.GetFittingSubContent,
             'label': typeName,
             'groupItems': fittingsByType[typeID],
             'fittings': fittingsByType[typeID],
             'id': ('fittingMgmtScrollWndType', typeName),
             'sublevel': 1,
             'showicon': 'hide',
             'state': 'locked',
             'selectable': 0}))

        return scrolllist

    def GetFittingSubContent(self, nodedata, *args):
        scrolllist = []
        fittings = []
        for fitting in nodedata.fittings:
            fittings.append((fitting.name, fitting))

        fittings.sort()
        for fittingName, fitting in fittings:
            scrolllist.append((fittingName.lower(), GetFromClass(FittingEntry, {'label': fittingName,
              'fittingID': fitting.fittingID,
              'fitting': fitting,
              'ownerID': self._selected_owner_id,
              'showinfo': 1,
              'GetMenu': self.GetFittingMenu,
              'showicon': 'hide',
              'sublevel': 2,
              'OnClick': self.ClickEntry,
              'ignoreRightClick': 1})))

        scrolllist = SortListOfTuples(scrolllist)
        return scrolllist

    def GetFittingMenu(self, entry):
        m = []
        if not self or self.destroyed:
            return m
        node = entry.sr.node
        selectedNodes = node.scroll.GetSelectedNodes(node)
        multiSelected = len(selectedNodes) > 1
        fittingID = entry.sr.node.fittingID
        ownerID = entry.sr.node.ownerID
        maxShipsAllowed = GetMaxShipsToFit(sm.GetService('machoNet'))
        m = []
        if not multiSelected:
            if evetypes.GetCategoryID(entry.sr.node.fitting.shipTypeID) != const.categoryStructure:
                m += [(GetByLabel('UI/Fitting/FittingWindow/FitFittingToActiveShip'), self._fitting_service.LoadFittingFromFittingID, [ownerID, fittingID])]
            if maxShipsAllowed and IsDocked():
                m += [(GetByLabel('UI/Fitting/FittingWindow/FittingManagement/OpenMultifit'), self.DoBulkFit, [entry])]
            if session.role & ROLE_WORLDMOD:
                try:
                    fitting_spawner = sm.GetService('fittingspawner')
                except ServiceNotFound:
                    pass
                else:
                    m.append(None)
                    m.append(('DEV Hax This Together!', fitting_spawner.SpawnFitting, [ownerID, entry.sr.node.fitting]))
                    m.append(('Mass DEV Hax This Together!', fitting_spawner.MassSpawnFitting, [ownerID, entry.sr.node.fitting]))

        m += [None]
        deletable = GetDeletableNodes(selectedNodes)
        if deletable:
            m += [(MenuLabel('UI/Fitting/FittingWindow/FittingManagement/DeleteFitting'), self.DeleteFitting, [entry, deletable])]
        return m

    def DeleteFitting(self, entry, selectedNodes):
        fittingID = entry.sr.node.fittingID
        fittingDeleted = DeleteFittings(selectedNodes)
        if not fittingDeleted:
            return
        loadedFitting = self.GetVisibleFitting()
        if loadedFitting is not None and loadedFitting.fittingID == fittingID:
            self.HideRightPanel()

    def DoBulkFit(self, entry):
        fitting = entry.sr.node.fitting
        OpenOrLoadMultiFitWnd(fitting)

    def ClickEntry(self, entry, *args):
        if not self or self.destroyed:
            return
        self.ShowRightPanel()
        fitting = self.GetVisibleFitting()
        if fitting is not None and fitting.fittingID == entry.sr.node.fitting.fittingID:
            return
        fitting = entry.sr.node.fitting
        self._fitting_management_cont.LoadNewFitting(fitting)

    def Fit(self, *args):
        visibleFitting = self.GetVisibleFitting()
        if visibleFitting is None:
            return
        self._fitting_service.LoadFittingFromFittingIDAndGetBuyOptionOnFailure(self._selected_owner_id, visibleFitting.fittingID)

    def HideRightPanel(self):
        self.noContentHint.Show()
        self._fitting_management_cont.HidePanel()

    def ShowRightPanel(self):
        self.noContentHint.Hide()
        self._fitting_management_cont.ShowPanel()

    def GetVisibleFitting(self):
        if self._fitting_management_cont:
            return self._fitting_management_cont.GetSelectedFitting()

    def ExportFittings(self, *args):
        ExportFittingsWindow.Open(ownerID=self._selected_owner_id)

    def ImportFittings(self, *args):
        ImportFittingsWindow.Open()

    def OnRedrawFittingMgmt(self, *args):
        self.DrawFittings()


class ViewFitting(Window):
    __guid__ = 'form.ViewFitting'
    __nonpersistvars__ = []
    __notifyevents__ = ['OnSessionChanged']
    default_width = 410
    default_height = 580
    default_captionLabelPath = 'UI/Fitting/ShipFitting'
    default_minSize = (250, 300)
    default_windowID = 'ViewFitting'
    default_iconNum = 'res:/ui/Texture/WindowIcons/fittingManagement.png'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.fitting = attributes.fitting
        self.truncated = attributes.truncated
        self._fitting_service = sm.GetService('fittingSvc')
        self.ReconstructLayout()
        sm.RegisterNotify(self)

    def GetHeaderIconMenu(self, *args):
        m = MenuData()
        self._AddCustomMenuOptions(m)
        return m

    def GetMenuMoreOptions(self):
        menuData = super(ViewFitting, self).GetMenuMoreOptions()
        self._AddCustomMenuOptions(menuData)
        return menuData

    def _AddCustomMenuOptions(self, menu):
        if IsDocked():
            fittingcopy = self.fitting.copy()
            menu.AddEntry(GetByLabel('UI/Fitting/FittingWindow/FittingManagement/OpenMultifit'), lambda : OpenOrLoadMultiFitWnd(fittingcopy))
        menu.AddEntry(GetByLabel('UI/Fitting/FittingWindow/FittingManagement/ExportToClipboard'), self._fitting_management_cont.ExportFittingToClipboard, hint=GetByLabel('UI/Fitting/FittingWindow/FittingManagement/ExportToClipboardHint'))

    def ClickDragIcon(self, *args):
        subsystems = {}
        if IsModularShip(self.fitting.shipTypeID):
            for typeID, flag, qty in self.fitting.fitData:
                if IsSubsystemFlag(flag):
                    subsystems[evetypes.GetGroupID(typeID)] = typeID

            if len(subsystems) != numVisibleSubsystems:
                raise UserError('NotEnoughSubSystemsNotify', {})
        sm.GetService('preview').PreviewType(self.fitting.shipTypeID, subsystems)

    def ReloadWnd(self, windowID, fitting, truncated):
        self.fitting = fitting
        self.truncated = truncated
        self.windowID = windowID
        self.ReconstructLayout()

    def ReconstructLayout(self):
        self.content.Flush()
        self.UpdateHeader()
        self._fitting_management_cont = FittingMgmtContInStandalone(parent=self.content, saveCallback=self.CloseByUser)
        self._fitting_management_cont.LoadNewFitting(self.fitting, self.truncated)

    def UpdateHeader(self):
        self.UpdateCaption()

    def UpdateCaption(self):
        self.caption = GetByLabel(self.default_captionLabelPath) + ': %s' % evetypes.GetName(self.fitting.shipTypeID)

    def OnSessionChanged(self, isRemote, session, change):
        if 'stationid' in change or 'structureid' in change:
            self.UpdateHeader()


def OpenOrLoadMultiFitWnd(fitting):
    sm.GetService('fittingSvc').CheckBusyFittingAndRaiseIfNeeded()
    from eve.client.script.ui.shared.fitting.multiFitWnd import MultiFitWnd
    wnd = MultiFitWnd.GetIfOpen()
    if wnd:
        wnd.LoadWindow(fitting)
        wnd.Maximize()
    else:
        wnd = MultiFitWnd.Open(fitting=fitting)
    return wnd
