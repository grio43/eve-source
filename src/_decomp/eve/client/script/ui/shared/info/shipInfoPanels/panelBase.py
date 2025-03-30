#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\info\shipInfoPanels\panelBase.py
import eveicon
from carbonui import Align
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from eve.client.script.ui.shared.info.shipInfoConst import DOWN_FRONT_LEFT
from carbonui.primitives.gradientSprite import GradientSprite

class PanelBase(Container):
    RIGHT_CONT_WIDTH = 420
    COMPACT_TOP_PADDING = 40
    __notifyevents__ = []

    def ApplyAttributes(self, attributes):
        super(PanelBase, self).ApplyAttributes(attributes)
        self._controller = attributes.controller
        self._params = attributes.params
        self._construct_layout()
        self._gather_data()
        self._construct_content()
        self._construct_content_minimized()
        sm.RegisterNotify(self)

    @property
    def typeID(self):
        return self._controller.type_id

    @property
    def itemID(self):
        return self._controller.item_id

    @property
    def groupID(self):
        return self._controller.group_id

    @property
    def ownerID(self):
        return self._controller.owner_id

    @property
    def item(self):
        return self._controller.item

    @item.setter
    def item(self, value):
        self._controller.item = value

    def Close(self):
        super(PanelBase, self).Close()
        sm.UnregisterNotify(self)

    def _gather_data(self):
        pass

    def _construct_layout(self):
        self.expandedCont = Container(parent=self, name='expandedCont', align=Align.TOALL)
        self.leftCont = Container(parent=self.expandedCont, name='leftCont', align=Align.TOLEFT, padRight=10)
        self.rightCont = Container(parent=self.expandedCont, name='rightCont', align=Align.TOALL)
        GradientSprite(bgParent=self.rightCont, padding=-130, rgbData=((0, (0, 0, 0)),), alphaData=((0.0, 0.0), (0.25, 0.6)))
        self.minimizedCont = Container(parent=self, name='minimizedCont', align=Align.TOALL)
        self.minimized_footer = Container(name='minimized_footer', parent=self.minimizedCont, display=False, align=Align.TOBOTTOM, padTop=10)
        self._construct_minimized_content_scroll()

    def _construct_minimized_content_scroll(self):
        self.content_scroll_minimized = ScrollContainer(parent=self.minimizedCont, align=Align.TOALL)

    def _construct_content(self):
        pass

    def _construct_content_minimized(self):
        pass

    def show_expanded_view(self):
        self.minimizedCont.Hide()
        self._enable_expanded_view()
        self.expandedCont.Show()

    def _enable_expanded_view(self):
        pass

    def show_minimized_view(self, is_compact):
        self.expandedCont.Hide()
        self._enable_minimized_view()
        self.minimizedCont.padTop = self._get_compact_top_padding() if is_compact else 0
        self.minimizedCont.Show()

    def _enable_minimized_view(self):
        pass

    def on_reset(self, initialize):
        pass

    def _OnSizeChange_NoBlock(self, width, height):
        self.leftCont.width = width - min(width / 2, self.RIGHT_CONT_WIDTH) - self.leftCont.padRight

    @classmethod
    def get_name(cls):
        return ''

    @classmethod
    def get_icon(cls):
        return eveicon.info

    @classmethod
    def is_visible(cls, typeID, itemID = None, rec = None):
        return True

    def get_camera_position(self):
        return DOWN_FRONT_LEFT

    def get_zoom(self):
        return 0.6

    def get_tab_type(self):
        return 0

    def _get_compact_top_padding(self):
        return self.COMPACT_TOP_PADDING
