#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\ui\drawing\renderer\elements\area.py
from carbonui.primitives import container
from carbonui import const
CURSOR_NORMAL = 'res:/UI/Cursor/DrawingTool/picker3.png'
import logging
log = logging.getLogger('projectdiscovery.covid.renderer.area')

class DrawingArea(container.Container):
    default_name = 'drawing_area'
    default_state = const.UI_NORMAL

    def __init__(self, mouse_enter_callback, **kwargs):
        self.cursor = CURSOR_NORMAL
        self.background_sprite = None
        self.mouse_enter_callback = mouse_enter_callback
        super(DrawingArea, self).__init__(cursor=self.cursor, **kwargs)

    def ApplyAttributes(self, attributes):
        super(DrawingArea, self).ApplyAttributes(attributes)

    def OnMouseEnter(self, *args):
        log.warning('%s:OnMouseEnter:self=%r, args=%r', self.__class__.__name__, self, args)
        self.mouse_enter_callback()

    def OnMouseExit(self, *args):
        log.warning('%s:OnMouseExit:self=%r, args=%r', self.__class__.__name__, self, args)
        self.mouse_enter_callback(is_exit=True)
