#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\window.py
import eveui
import threadutils
import uthread2
from carbonui.control.window import Window
from carbonui.uicore import uicore
from carbonui.window.header.tab_navigation import TabNavigationWindowHeader
from raffles.client import texture
from raffles.client.browse.page import BrowsePage
from raffles.client.controller import RaffleWindowController
from raffles.client.create.page import CreatePage
from raffles.client.details.page import DetailsPage
from raffles.client.history.page import HistoryPage
from raffles.client.localization import Text
from raffles.client.tutorial import have_seen_introduction, show_introduction
from raffles.client.widget.navigation_bar import NavigationBar
from raffles.client.widget.wallet_balance import WalletBalance
pages = {'browse': BrowsePage,
 'history': HistoryPage,
 'create': CreatePage,
 'details': DetailsPage}

class RaffleWindow(Window):
    default_name = 'RaffleWindow'
    default_windowID = 'RaffleWindow'
    default_fixedWidth = 1024
    default_fixedHeight = 720
    default_isStackable = False
    default_isLightBackgroundConfigurable = False
    default_isCollapseable = False
    default_clipChildren = True
    isDropLocation = True
    default_captionLabelPath = Text.raffle_window_title.value
    default_descriptionLabelPath = Text.raffle_window_description.value
    default_iconNum = texture.raffle_window_icon

    def __init__(self, **kwargs):
        super(RaffleWindow, self).__init__(**kwargs)
        self._controller = RaffleWindowController()
        self._navigation = self._controller.navigation_controller
        self.OnBack = self._navigation.go_back
        self.OnForward = self._navigation.go_forward
        self._layout()
        self._navigation.on_page_change.connect(self._on_page_change)
        self._controller.on_focus_window.connect(self._on_focus_window)

    @classmethod
    def Open(cls, *args, **kwargs):
        sm.GetService('raffleSvc').check_can_open()
        window = super(RaffleWindow, cls).Open(*args, **kwargs)
        if not hasattr(window, '_navigation'):
            return window
        if 'raffle_id' in kwargs:
            window._navigation.open_details_page(kwargs['raffle_id'])
        else:
            window.header.tab_group.AutoSelect()
        return window

    def Close(self, *args, **kwds):
        super(RaffleWindow, self).Close(*args, **kwds)
        if hasattr(self, '_controller'):
            self._controller.close()

    def Prepare_Header_(self):
        self.header = TabNavigationWindowHeader(on_tab_selected=self.OnMainTabGroup)

    def _on_focus_window(self):
        self.Maximize()

    def _on_page_change(self, page_id, **kwargs):
        if page_id == 'details':
            self._deselect_tab()
        else:
            self.header.tab_group.SelectByID(page_id, useCallback=False)
        self.content_container.Flush()
        self.background_layer.Flush()
        uicore.registry.SetFocus(self)
        pages[page_id](window_controller=self._controller, parent=self.content_container, background_layer=self.background_layer, **kwargs)
        eveui.fade(self.content_container, start_value=0.0, end_value=1.0, duration=0.5)
        eveui.fade(self.background_layer, start_value=0.0, end_value=1.0, duration=0.5)

    def _deselect_tab(self):
        tab = self.header.tab_group.GetSelectedTab()
        if tab:
            tab.Deselect()

    def OnMainTabGroup(self, tabID, oldTabID):
        self._navigation.open_page(tabID)

    def GetMainTabData(self):
        return ((Text.raffle_window_title(),
          None,
          None,
          'browse'), (Text.tab_my_raffles(),
          None,
          None,
          'history'), (Text.tab_create(),
          None,
          None,
          'create'))

    @eveui.lazy
    def _tutorial_layer(self):
        tutorial_layer = eveui.Container(name='tutorial_layer', parent=self.GetMainArea(), align=eveui.Align.to_all, state=eveui.State.normal, padTop=-38, idx=0)
        eveui.Fill(bgParent=tutorial_layer, color=(0, 0, 0), opacity=0.7)
        return tutorial_layer

    def _close_introduction(self):
        self.main_layer.state = eveui.State.pick_children
        eveui.fade_out(self._tutorial_layer, duration=0.3, on_complete=self._tutorial_layer.Close)

    @threadutils.threaded
    def _show_introduction(self):
        self.main_layer.state = eveui.State.disabled
        eveui.fade(self._tutorial_layer, start_value=0.0, end_value=1.0, duration=0.6)
        uthread2.sleep(0.5)
        tutorial_controller = show_introduction(self._tutorial_layer)
        tutorial_controller.on_closed.connect(self._close_introduction)

    def _layout(self):
        for label, _, _, tab_id in self.GetMainTabData():
            self.header.tab_group.AddTab(label=label, tabID=tab_id)

        self.main_layer = eveui.Container(name='main_layer', parent=self.GetMainArea(), align=eveui.Align.to_all)
        self.background_layer = eveui.Container(name='background_layer', parent=self.GetMainArea(), align=eveui.Align.to_all, state=eveui.State.disabled, padding=(-16, -52, -16, -16), clipChildren=True)
        navigation_cont = eveui.Container(name='navigation_cont', parent=self.main_layer, align=eveui.Align.to_top, height=24, padding=(0, 0, 0, 16))
        NavigationBar(parent=navigation_cont, align=eveui.Align.to_left, navigation_controller=self._controller.navigation_controller)
        WalletBalance(parent=navigation_cont, align=eveui.Align.center_right)
        eveui.GradientSprite(parent=navigation_cont, align=eveui.Align.center_right, left=-16, height=38, width=160, rgbData=[(0, (0, 0, 0))], alphaData=[(0, 0), (1, 0.6)])
        self.content_container = eveui.Container(name='contentCont', parent=self.main_layer)
        if not have_seen_introduction():
            self._show_introduction()

    def OnDropData(self, source, data):
        item = getattr(data[0], 'item', None)
        if item:
            self._controller.on_drop_item(item)
            self._controller.on_drag_exit(item)

    def OnDragEnter(self, source, data):
        item = getattr(data[0], 'item', None)
        if item:
            self._controller.on_drag_enter(item)

    def OnDragExit(self, source, data):
        item = getattr(data[0], 'item', None)
        if item:
            self._controller.on_drag_exit(item)


def __SakeReloadHook():
    try:
        instance = RaffleWindow.GetIfOpen()
        if instance:
            RaffleWindow.Reload(instance)
    except Exception:
        import log
        log.LogException()
