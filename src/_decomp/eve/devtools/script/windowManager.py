#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\windowManager.py
from carbon.common.script.sys.service import ROLE_ADMIN
from carbon.common.script.sys.sessions import ThrottlePerMinute
from carbonui.control.combo import Combo
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.primitives.flowcontainer import FlowContainer
from eve.client.script.ui.inflight.overview.overviewWindowUtil import OpenOverview, CloseAllOverviewWindows
from carbonui.control.button import Button
from eve.client.script.ui.control.eveLabel import Label
from carbonui.control.window import Window
from eve.client.script.ui.inflight.activeitem import ActiveItem
from eve.client.script.ui.inflight.drone import DroneView
from eve.client.script.ui.inflight.drones.dronesWindow import DronesWindow
from eve.client.script.ui.inflight.selectedItemWnd import SelectedItemWnd
from eve.client.script.ui.shared.activities import newActivityNotify
from eve.client.script.ui.shared.maps.browserwindow import MapBrowserWnd
from globalConfig import GetNewMissionGiverEnabled
import carbonui.const as uiconst
from carbonui.uicore import uicore
from newFeatures import newFeatureNotify
from newFeatures.debugwindow import NewFeatureNotifyDebugWindow

class WindowManager(Window):
    __guid__ = 'form.WindowManager'
    default_windowID = 'WindowManager'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.SetCaption('Window manager')
        self.SetMinSize([478, 470])
        options = []
        for wndCls in Window.__subclasses__():
            options.append((wndCls.__name__, wndCls))

        options.sort()
        topCont = Container(name='params', parent=self.sr.main, align=uiconst.TOTOP, pad=(5, 5, 5, 5), pos=(0, 16, 0, 30))
        self.mainCont = Container(name='params', parent=self.sr.main, align=uiconst.TOTOP, pos=(0, 0, 0, 50), padding=(5, 15, 5, 5))
        self.extrasCont = Container(name='params', parent=self.sr.main, padding=5)
        self.combo = Combo(parent=topCont, label='Select window', options=options, name='', select=self.GetWndClsByName(settings.user.ui.Get('windowManagerOpenWindow')), callback=self.OnComboChanged, pos=(5, 0, 0, 0), width=150, align=uiconst.TOPLEFT)
        self.startupArgs = SingleLineEditText(name='', label='attributes', parent=topCont, setvalue='', align=uiconst.TOPLEFT, left=165, width=100)
        Button(parent=topCont, label='Load', align=uiconst.RELATIVE, func=self.OpenWindow, pos=(300, 0, 0, 0))
        self.filenameEdit = SingleLineEditText(name='', label='Location', parent=self.mainCont, setvalue='', align=uiconst.TOTOP, top=15, readonly=True)
        self.ConstructButtonCont()
        self.ConstructNewFeatureCont()
        self.ConstructNewActivitiesCont()
        self.UpdateInfo(self.combo.GetKey(), self.combo.GetValue())

    def ConstructNewActivitiesCont(self):
        Label(text='NEW ACTIVITIES NOTIFY', parent=self.extrasCont, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, padTop=10)
        newActivitiesCont = Container(name='newActivitiesCont', parent=self.extrasCont, align=uiconst.TOTOP, padding=5, height=30)
        Button(parent=newActivitiesCont, label='Show Current', align=uiconst.TOLEFT, func=self.ShowNewActivitiesNotifyWnd, padLeft=1)

    def ConstructNewFeatureCont(self):
        Label(text='NEW FEATURE NOTIFY', parent=self.extrasCont, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, padTop=10)
        newFeatureCont = Container(name='newFeatureCont', parent=self.extrasCont, align=uiconst.TOTOP, padding=5, height=30)
        Button(parent=newFeatureCont, label='Show Current', align=uiconst.TOLEFT, func=self.ShowNewFeatureNotifyWnd, padLeft=1)
        Button(parent=newFeatureCont, label='Show most recent', align=uiconst.TOLEFT, func=self.ShowNewFeatureNotifyWndForceShow, padLeft=1)
        Button(parent=newFeatureCont, label='Show Specific', align=uiconst.TOLEFT, func=NewFeatureNotifyDebugWindow.Open, padLeft=1)

    def ConstructButtonCont(self):
        Label(text='RELOAD', parent=self.extrasCont, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        buttonCont = FlowContainer(name='buttonCont', parent=self.extrasCont, align=uiconst.TOTOP, height=30, padding=5, contentSpacing=(1, 1))
        Button(parent=buttonCont, label='ShipUI', align=uiconst.NOALIGN, func=self.ReloadShipUI, fixedheight=30)
        Button(parent=buttonCont, label='NEOCOM', align=uiconst.NOALIGN, func=self.ReloadNeocom, fixedheight=30)
        Button(parent=buttonCont, label='Info Panels', align=uiconst.NOALIGN, func=self.ReloadInfoPanels, fixedheight=30)
        Button(parent=buttonCont, label='Lobby', align=uiconst.NOALIGN, func=self.ReloadLobby, fixedheight=30)
        Button(parent=buttonCont, label='Overview', align=uiconst.NOALIGN, func=self.ReloadOverview, fixedheight=30)
        Button(parent=buttonCont, label='Map Browser', align=uiconst.NOALIGN, func=self.ReloadMapBrowser, fixedheight=30)
        Button(parent=buttonCont, label='Char Select', align=uiconst.NOALIGN, func=self.ReloadCharacterSelection, fixedheight=30)
        Button(parent=buttonCont, label='TreatmentWnd', align=uiconst.NOALIGN, func=self.TreatmentWnd, fixedheight=30)
        Button(parent=buttonCont, label='Career Portal', align=uiconst.NOALIGN, func=self.CareerPortal, fixedheight=30)
        Button(parent=buttonCont, label='System Menu', align=uiconst.NOALIGN, func=self.ReloadSystemMenu, fixedheight=30)
        if session.role & ROLE_ADMIN:
            self._AddAgentDialogReloaders(buttonCont)

    def _AddAgentDialogReloaders(self, buttonContainer):
        Button(parent=buttonContainer, label='Old Agent Dialog', align=uiconst.NOALIGN, func=lambda *args: self.ReloadAgentDialogs(useNewStyle=False), fixedheight=30)
        Button(parent=buttonContainer, label='New Agent Dialog', align=uiconst.NOALIGN, func=lambda *args: self.ReloadAgentDialogs(useNewStyle=True), fixedheight=30)

    def ShowNewFeatureNotifyWnd(self, *args):
        newFeatureNotify.MarkAllAsUnseen()
        newFeatureNotify.CheckOpenNewFeatureNotifyWindow()

    def ShowNewFeatureNotifyWndForceShow(self, *args):
        newFeatureNotify.MarkAllAsForceShow()
        newFeatureNotify.CheckOpenNewFeatureNotifyWindow()

    def ShowNewActivitiesNotifyWnd(self, *args):
        newActivityNotify.CheckOpenNewActivitiesNotifyWindow()

    def OnComboChanged(self, combo, key, wndCls):
        self.UpdateInfo(key, wndCls)

    def UpdateInfo(self, key, wndCls):
        self.filenameEdit.SetValue(wndCls.ApplyAttributes.func_code.co_filename)
        settings.user.ui.Set('windowManagerOpenWindow', wndCls.__name__)

    def GetWndClsByName(self, name):
        for wndCls in Window.__subclasses__():
            if wndCls.__name__ == name:
                return wndCls

    def OpenWindow(self, *args):
        windowClass = self.combo.GetValue()
        windowClass.CloseIfOpen()
        attributes = {}
        try:
            attributesStr = self.startupArgs.GetValue()
            if attributesStr:
                for s in attributesStr.split(','):
                    keyword, value = s.split('=')
                    keyword = keyword.strip()
                    value = value.strip()
                    try:
                        if value.find('.') != -1:
                            value = float(value)
                        else:
                            value = int(value)
                    except ValueError:
                        pass

                    if value == 'None':
                        value = None
                    attributes[keyword] = value

        except:
            eve.Message('CustomInfo', {'info': 'attributes must be on the form: attr1=1, attr2=Some random text'})
            raise

        windowClass.Open(**attributes)

    def ReloadShipUI(self, *args):
        if eve.session.stationid is None:
            uicore.layer.shipui.CloseView()
            uicore.layer.shipui.OpenView()

    def ReloadNeocom(self, *args):
        sm.GetService('neocom').Reload()

    def ReloadInfoPanels(self, *args):
        sm.GetService('infoPanel').Reload()

    def ReloadLobby(self, *args):
        if session.stationid or session.structureid:
            from eve.client.script.ui.shared.dockedUI import ReloadLobbyWnd
            ReloadLobbyWnd()

    def ReloadMapBrowser(self, *args):
        MapBrowserWnd.CloseIfOpen()
        uicore.cmd.OpenMapBrowser()

    def ReloadOverview(self, *args):
        CloseAllOverviewWindows()
        if session.solarsystemid:
            OpenOverview()
        SelectedItemWnd.CloseIfOpen()
        if session.solarsystemid:
            sm.GetService('tactical').InitSelectedItem()
        DronesWindow.CloseIfOpen()
        if session.solarsystemid:
            sm.GetService('tactical').InitDrones()

    def ReloadCharacterSelection(self, *args):
        characterSelectionLayer = uicore.layer.charsel
        if characterSelectionLayer.IsClosed():
            return
        characterSelectionLayer.OnRefreshScreen()

    def TreatmentWnd(self, *args):
        from eve.client.script.ui.shared.recommendation.recommendationWnd import RecommendationWnd
        RecommendationWnd.CloseIfOpen()
        wnd = RecommendationWnd.Open()
        wnd.ShowDialog(modal=True, state=uiconst.UI_PICKCHILDREN, closeWhenClicked=True)

    def CareerPortal(self, *args):
        from eve.client.script.ui.shared.careerPortal.careerPortalWnd import CareerPortalDockablePanel
        CareerPortalDockablePanel.ToggleOpenClose()

    def ReloadSystemMenu(self, *args):
        uicore.layer.systemmenu.Reset()

    def ReloadAgentDialogs(self, useNewStyle = True):
        currentUseNewStyle = GetNewMissionGiverEnabled(sm.GetService('machoNet'))
        if currentUseNewStyle == useNewStyle:
            sm.GetService('agents').ReloadAgentDialogWindows()
        else:
            self.ChangeAgentDialogStyle(useNewStyle)

    @ThrottlePerMinute(10)
    def ChangeAgentDialogStyle(self, useNewStyle):
        sm.RemoteSvc('machoNet').SetGlobalConfigValue(key='new_mission_giver_enabled', value='1' if useNewStyle else '0')
