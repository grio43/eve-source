#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\fwWarzonesWnd.py
from carbonui.control.button import Button
import blue
import carbonui.const as uiconst
from carbonui.control.button import Button
from carbonui.control.combo import Combo
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.control.dragResizeCont import DragResizeCont
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.services.setting import UserSettingEnum
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveLabel import EveLabelLarge
from eve.client.script.ui.control.eveScroll import Scroll
from eve.common.script.sys.idCheckers import IsSolarSystem
from eveexceptions import UserError
from evelink.client import location_link
from eveservices.menu import GetMenuService
from factionwarfare.const import ADJACENCY_STATE_DEBUG_NAMES
from fwwarzone.client.dashboard.fwWarzoneDashboard import FwWarzoneDashboard

class FwWarzoneWnd(Window):
    __notifyevents__ = ['OnSessionChanged', 'OnWarzoneOccupationStateUpdated_Local', 'OnGlobalConfigChanged']
    default_height = 500
    default_width = 500
    default_minSize = [330, 256]
    default_windowID = 'fwWarzoneWnd'

    def DebugReload(self, *args):
        self.Reload(self)

    def ApplyAttributes(self, attributes):
        super(FwWarzoneWnd, self).ApplyAttributes(attributes)
        self.previousStates = {}
        self.elementsByWarzoneID = {}
        reloadBtn = Button(parent=self.content, label='Reload', align=uiconst.TOPRIGHT, func=self.DebugReload, top=14, idx=0)
        self.contentCont = Container(parent=self.content, padding=10)
        self.ConstructBtns()
        self._ConstructWarzoneMapControls()
        self.ConstructScrolls()
        self.LoadData()

    def ConstructBtns(self):
        wndCont = ContainerAutoSize(parent=self.contentCont, name='flipLocalCont', align=uiconst.TOTOP, top=0)
        wndBtn = Button(parent=wndCont, label='Open FW window', align=uiconst.TOPLEFT, func=self.OpenFwWarzoneDashboard)
        localCont = ContainerAutoSize(parent=self.contentCont, name='flipLocalCont', align=uiconst.TOTOP, top=20)
        localBtn = Button(parent=localCont, label='Get local info', align=uiconst.TOPRIGHT, func=lambda *args: sm.GetService('slash').SlashCmd('/fw localinfo'))
        warzoneCont = ContainerAutoSize(parent=self.contentCont, name='warzoneCont', align=uiconst.TOTOP, top=10)
        warzoneBtn = Button(parent=warzoneCont, label='Get warzone info', align=uiconst.TOPRIGHT, func=lambda *args: sm.GetService('slash').SlashCmd('/fw warzoneinfo'))
        flipLocalCont = ContainerAutoSize(parent=self.contentCont, name='flipLocalCont', align=uiconst.TOTOP, top=20)
        flipLocalBtn = Button(parent=flipLocalCont, label='Flip current system (%s)' % cfg.evelocations.Get(session.solarsystemid2).name, align=uiconst.TOPLEFT, func=self.FlipCurrentSystem)
        flipSolarsystemCont = ContainerAutoSize(parent=self.contentCont, name='flipSolarsystem', align=uiconst.TOTOP, top=10)
        self.flipSolarsystemEdit = SingleLineEditText(name='flipSolarsystemEdit', parent=flipSolarsystemCont, align=uiconst.TOPLEFT, width=100, hintText='solarsystemID', OnChange=self.OnSolarSystemEditChanged)
        self.flipSolarsystemBtn = Button(name='flipSolarsystemBtn', parent=flipSolarsystemCont, label='Flip solarsystem', align=uiconst.TOPLEFT, func=self.FlipSolarsystemByID, left=self.flipSolarsystemEdit.left + self.flipSolarsystemEdit.width + 10)

    def _ConstructWarzoneMapControls(self):
        warzoneMapModeSetting = UserSettingEnum('warzone_map_mode', 'Active', options=('Full', 'Active'))
        self.debugControlsCont = ContainerAutoSize(parent=self.contentCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP)
        EveLabelLarge(parent=self.debugControlsCont, padTop=50, padLeft=10, align=uiconst.TOTOP, text='Map Controls')
        Combo(parent=self.debugControlsCont, padTop=10, padLeft=5, padRight=5, align=uiconst.TOTOP, options=[('Caldari vs Gallente', 2), ('Ammar vs Minmatar', 1)], callback=self._SelectWarzoneCallback)

    def _SelectWarzoneCallback(self, _comboBox, _key, value):
        self.warzoneID = value
        wnd = FwWarzoneDashboard.GetIfOpen()
        if wnd and not wnd.destroyed:
            wnd.warzoneMap.DebugReloadMap()
        else:
            self.OpenFwWarzoneDashboard()
            wnd = FwWarzoneDashboard.GetIfOpen()
        wnd.DEBUG_SelectWrazoneCallback(value)

    def ConstructScrolls(self):
        scrollCont = Container(parent=self.contentCont)
        fwDebugWndDiv = DragResizeCont(name='fwDebugWndDiv', settingsID='fwDebugWndDiv', parent=scrollCont, align=uiconst.TOTOP_PROP, minSize=0.25, maxSize=0.75, defaultSize=0.5, clipChildren=True)
        self.zone1Label = eveLabel.EveLabelMedium(name='warzoneNum', parent=fwDebugWndDiv, align=uiconst.TOTOP, top=10, text='warzoneID:')
        self.scroll1 = Scroll(name='scroll1', parent=fwDebugWndDiv)
        self.zone2Label = eveLabel.EveLabelMedium(name='zone2Label', parent=scrollCont, align=uiconst.TOTOP, top=10, text='warzoneID:')
        self.scroll2 = Scroll(name='scroll2', parent=scrollCont)
        self.elementsByWarzoneID[1] = (self.zone1Label, self.scroll1)
        self.elementsByWarzoneID[2] = (self.zone2Label, self.scroll2)

    def LoadData(self):
        self.LoadScroll()

    def FlipCurrentSystem(self, *args):
        self._FlipSolarSystem(session.solarsystemid2)

    def FlipSolarsystemByID(self, *args):
        solarSystemID = self._GetSolarsystemID()
        self._FlipSolarSystem(solarSystemID)

    def _FlipSolarSystem(self, solarSystemID):
        if not IsSolarSystem(solarSystemID):
            raise UserError('SlashError', {'reason': 'Must enter valid solarsystemID'})
        if not self._AskConfirm(solarSystemID):
            return
        sm.GetService('slash').SlashCmd('/fw flip %s' % solarSystemID)
        self.LoadData()
        self._UpdateMap()

    def _UpdateMap(self):
        from fwwarzone.client.dashboard.fwWarzoneDashboard import FwWarzoneDashboard
        wnd = FwWarzoneDashboard.GetIfOpen()
        if wnd and not wnd.destroyed:
            wnd.warzoneMap.DebugReloadMap()

    def _AskConfirm(self, solarSystemID):
        locationLink = location_link(solarSystemID)
        questionText = 'Are you sure you want to flip %s ?' % locationLink
        if eve.Message('CustomQuestion', {'header': 'Flip Solarsystem',
         'question': questionText}, uiconst.YESNO) == uiconst.ID_YES:
            return True
        return False

    def OnSolarSystemEditChanged(self, *args):
        solarSystemID = self._GetSolarsystemID()
        if IsSolarSystem(solarSystemID):
            btnText = 'Flip solarsystem (%s)' % cfg.evelocations.Get(solarSystemID).name
        else:
            btnText = 'Flip solarsystem'
        self.flipSolarsystemBtn.label = btnText

    def _GetSolarsystemID(self):
        solarSystemIDText = self.flipSolarsystemEdit.GetValue()
        try:
            solarSystemID = int(solarSystemIDText)
        except:
            solarSystemID = None

        return solarSystemID

    def OnSessionChanged(self, isRemote, session, change):
        if 'solarsystemid2' in change:
            self.LoadData()

    def LoadScroll(self):
        previousStates = self.previousStates
        allStates = sm.GetService('fwWarzoneSvc').GetAllOccupationStatesUncached()
        self.previousStates = allStates
        fwVictoryPointSvc = sm.GetService('fwVictoryPointSvc')
        for warZoneID, solarsystemOccupationState in allStates.iteritems():
            scrollList = []
            warzoneLalbel, scroll = self.elementsByWarzoneID[warZoneID]
            warZoneText = 'WarzoneID: %s' % warZoneID
            if session.solarsystemid2 in solarsystemOccupationState:
                warZoneText = "<b><font color='green'>%s</b>" % warZoneText
            warzoneLalbel.text = warZoneText
            for sID, occupationState in solarsystemOccupationState.iteritems():
                adjState = occupationState.adjacencyState
                stateName = ADJACENCY_STATE_DEBUG_NAMES.get(adjState, '?')
                occupierID = occupationState.occupierID
                occupierName = cfg.eveowners.Get(occupierID).name
                previousInfo = previousStates.get(warZoneID, {}).get(sID, None)
                prevOccupierID = prevOccupierName = prevState = prevStateName = ''
                if previousInfo and (previousInfo.occupierID != occupierID or previousInfo.adjacencyState != adjState):
                    prevOccupierID = previousInfo.occupierID
                    prevOccupierName = cfg.eveowners.Get(prevOccupierID).name
                    prevState = previousInfo.adjacencyState
                    prevStateName = ADJACENCY_STATE_DEBUG_NAMES.get(prevState, '?')
                    if previousInfo.occupierID != occupierID:
                        occupierName = "<b><font color='green'>%s</font></b>" % occupierName
                    if previousInfo.adjacencyState != adjState:
                        stateName = "<b><font color='green'>%s</font></b>" % stateName
                victoryPointState = fwVictoryPointSvc.GetVictoryPointState(sID)
                label = '%s<t>%s<t>%s<t>%s<t>%s<t>%s<t>%s<t>%s<t>%s<t>%s<t>%s<t>%s<t>%s' % (sID,
                 cfg.evelocations.Get(sID).name,
                 occupierID,
                 occupierName,
                 victoryPointState.contestedFraction,
                 '%s / %s' % (victoryPointState._vpScore, victoryPointState._vpThreshold),
                 adjState,
                 stateName,
                 '',
                 '<font color="grey">%s</font>' % prevOccupierID,
                 '<font color="grey">%s</font>' % prevOccupierName,
                 '<font color="grey">%s</font>' % prevState,
                 '<font color="grey">%s</font>' % prevStateName)
                data = {'solarsystemID': sID,
                 'occupierID': occupierID,
                 'label': label,
                 'GetMenu': self.GetEntryMenu}
                entry = GetFromClass(Generic, data)
                scrollList.append(entry)

            headers = ['solarsystemID',
             'name',
             'occupierID',
             '',
             'vp',
             '',
             '',
             'adjacencyState',
             '',
             'prevOccupierID',
             '',
             '',
             'prevAdjState']
            scroll.Load(contentList=scrollList, headers=headers)

    def GetEntryMenu(self, entry):
        node = entry.sr.node
        m = MenuData()
        solarSystemID = node.solarsystemID
        m += [('Solar System', GetMenuService().GetMenuFromItemIDTypeID(solarSystemID, const.typeSolarSystem))]
        m.AddEntry('Copy SolarystemID: %s' % node.solarsystemID, lambda *args: blue.pyos.SetClipboardData(unicode(solarSystemID)))
        m.AddEntry('Copy occupierID: %s' % node.occupierID, lambda *args: blue.pyos.SetClipboardData(unicode(node.occupierID)))
        m.AddSeparator()
        m.AddEntry('Flip solarsystem: %s' % node.solarsystemID, lambda *args: self._FlipSolarSystem(node.solarsystemID))
        return m

    def OpenFwWarzoneDashboard(self, *args):
        from fwwarzone.client.dashboard.fwWarzoneDashboard import FwWarzoneDashboard
        wnd = FwWarzoneDashboard.GetIfOpen()
        if wnd and not wnd.destroyed:
            wnd.Maximize()
        else:
            FwWarzoneDashboard.Open()

    def OnGlobalConfigChanged(self, *args):
        self.LoadData()

    def OnWarzoneOccupationStateUpdated_Local(self):
        self.LoadData()
        self._UpdateMap()
