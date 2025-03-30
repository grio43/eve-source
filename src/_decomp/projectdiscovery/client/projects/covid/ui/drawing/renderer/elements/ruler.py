#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\ui\drawing\renderer\elements\ruler.py
import math
import carbonui.fontconst
from carbonui import uiconst
from carbonui.primitives import container
from carbonui.primitives import line
from carbonui.primitives import transform
from carbonui.uicore import uicore
from eve.client.script.ui.control import eveLabel
from projectdiscovery.client.projects.covid.ui.drawing.renderer.elements import colors
import logging
log = logging.getLogger('projectdiscovery.covid.renderer.ruler')
ORIENTATION_UP = 1
ORIENTATION_DOWN = 2
ORIENTATION_LEFT = 3
ORIENTATION_RIGHT = 4

class RulerPin(container.Container):
    default_height = 10
    default_width = 10
    default_align = uiconst.BOTTOMLEFT
    default_state = uiconst.UI_DISABLED
    default_show_label = False
    default_orientation = ORIENTATION_UP

    def __init__(self, orientation = None, show_label = None, **attributes):
        self.orientation = orientation or self.default_orientation
        self.show_label = self.default_show_label if show_label is None else show_label
        self.pin_line = None
        self.pin_label = None
        self.flipper = None
        base_attr = self._get_orientation_attributes()
        base_attr.update(attributes or {})
        log.warning('self.orientation=%r', self.orientation)
        log.warning('attributes=%r', attributes)
        super(RulerPin, self).__init__(orientation=self.orientation, show_label=self.show_label, **base_attr)

    def _get_orientation_attributes(self):
        if self.orientation == ORIENTATION_DOWN:
            base = {'align': uiconst.BOTTOMLEFT}
        elif self.orientation == ORIENTATION_LEFT:
            base = {'align': uiconst.BOTTOMLEFT}
        elif self.orientation == ORIENTATION_RIGHT:
            base = {'align': uiconst.BOTTOMRIGHT}
        else:
            if self.orientation != ORIENTATION_UP:
                log.error('unknown orientation: %r', self.orientation)
            base = {'align': uiconst.TOPLEFT}
        return base

    def _get_label_attributes(self):
        attr = dict(fontsize=carbonui.fontconst.EVE_SMALL_FONTSIZE, fontStyle=carbonui.fontconst.STYLE_SMALLTEXT, color=colors.WHITE.as_tuple, text='100.0', autoFitToText=True, wrapMode=uiconst.WRAPMODE_FORCENONE)
        if self.orientation == ORIENTATION_DOWN:
            self.flipper = self._get_flipper(align=uiconst.BOTTOMRIGHT, left=3, top=-10, width=32, height=13, rotationCenter=(1.0, 1.0))
            attr['parent'] = self.flipper
            attr['align'] = uiconst.TOPRIGHT
            attr['width'] = 32
            attr['height'] = 13
        elif self.orientation == ORIENTATION_LEFT:
            attr['parent'] = self
            attr['align'] = uiconst.BOTTOMRIGHT
            attr['width'] = 32
            attr['height'] = 13
            attr['left'] = 20
            attr['top'] = -6
        elif self.orientation == ORIENTATION_RIGHT:
            attr['parent'] = self
            attr['align'] = uiconst.BOTTOMLEFT
            attr['width'] = 32
            attr['height'] = 13
            attr['left'] = 20
            attr['top'] = -6
        else:
            self.flipper = self._get_flipper(align=uiconst.TOPLEFT, left=-6, top=-10, width=32, height=13, rotationCenter=(0.0, 0.0))
            attr['parent'] = self.flipper
            attr['align'] = uiconst.TOPLEFT
            attr['width'] = 32
            attr['height'] = 13
        return attr

    def _get_line_attributes(self):
        attr = dict(parent=self, color=colors.WHITE.as_tuple)
        if self.orientation == ORIENTATION_DOWN:
            attr['align'] = uiconst.BOTTOMLEFT
            attr['width'] = 1
            attr['height'] = 10
        elif self.orientation == ORIENTATION_LEFT:
            attr['align'] = uiconst.BOTTOMLEFT
            attr['width'] = 10
            attr['height'] = 1
        elif self.orientation == ORIENTATION_RIGHT:
            attr['align'] = uiconst.BOTTOMRIGHT
            attr['width'] = 10
            attr['height'] = 1
        else:
            attr['align'] = uiconst.TOPLEFT
            attr['width'] = 1
            attr['height'] = 10
        return attr

    def _get_flipper(self, **attr):
        if self.orientation in (ORIENTATION_DOWN, ORIENTATION_UP):
            attr.update(dict(parent=self, rotation=math.pi * 0.5))
            return transform.Transform(**attr)

    def _get_label(self):
        if self.show_label:
            return eveLabel.Label(**self._get_label_attributes())

    def ApplyAttributes(self, attributes):
        super(RulerPin, self).ApplyAttributes(attributes)
        self.pin_label = self._get_label()
        self.pin_line = line.Line(**self._get_line_attributes())

    def update(self, new_text):
        if self.show_label:
            if self.pin_label:
                self.pin_label.SetText(new_text)

    def folow_mouse(self):
        self.unfollow_mouse()
        setattr(self, '_follow_cookie', uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEMOVE, self.on_mouse_move))

    def unfollow_mouse(self):
        cookie = getattr(self, '_follow_cookie', None)
        if cookie:
            uicore.event.UnregisterForTriuiEvents(cookie)

    def on_mouse_move(self, element, event_id, params):
        self.SetPosition(uicore.uilib.x, uicore.uilib.y)
        self.update('%.1f' % (uicore.uilib.y / 10.0))
        return True

    def OnMouseMove(self, *args):
        self.SetPosition(uicore.uilib.x, uicore.uilib.y)
        self.update('%.1f' % (uicore.uilib.y / 10.0))
        return True


class Ruler(container.Container):
    default_name = 'ruler'
    default_ruler_length = 512
    default_ruler_thickness = 20
    default_align = uiconst.BOTTOMLEFT
    default_state = uiconst.UI_DISABLED
    default_orientation = ORIENTATION_UP
    default_show_label = True

    def __init__(self, ruler_length = None, ruler_thickness = None, orientation = None, show_label = None, **attributes):
        self.orientation = orientation or self.default_orientation
        self.show_label = self.default_show_label if show_label is None else show_label
        self.ruler_length = ruler_length or self.default_ruler_length
        self.ruler_thickness = ruler_thickness or self.default_ruler_thickness
        self.pin_position = 0
        self.pin = None
        base_attr = self._get_orientation_attributes()
        base_attr.update(attributes or {})
        super(Ruler, self).__init__(ruler_length=self.ruler_length, ruler_thickness=self.ruler_thickness, orientation=self.orientation, show_label=self.show_label, **base_attr)

    def _get_orientation_attributes(self):
        if self.orientation == ORIENTATION_DOWN:
            base = dict(align=uiconst.BOTTOMLEFT, width=self.ruler_length, height=self.ruler_thickness)
        elif self.orientation == ORIENTATION_LEFT:
            base = dict(align=uiconst.BOTTOMLEFT, width=self.ruler_thickness, height=self.ruler_length)
        elif self.orientation == ORIENTATION_RIGHT:
            base = dict(align=uiconst.BOTTOMLEFT, width=self.ruler_thickness, height=self.ruler_length)
        else:
            if self.orientation != ORIENTATION_UP:
                log.error('unknown orientation: %r', self.orientation)
            base = dict(align=uiconst.BOTTOMLEFT, width=self.ruler_length, height=self.ruler_thickness)
        return base

    def ApplyAttributes(self, attributes):
        super(Ruler, self).ApplyAttributes(attributes)
        self.pin = RulerPin(parent=self, orientation=self.orientation, show_label=self.show_label)

    @property
    def pin_percentage(self):
        return self.pin_position * 100.0 / (self.ruler_length - 1)

    def update(self, pin_position):
        if self.pin_position != pin_position:
            self.pin_position = pin_position
            if self.orientation in (ORIENTATION_RIGHT, ORIENTATION_LEFT):
                self.pin.top = self.pin_position
                self.pin.update('%.1f' % self.pin_percentage)
            else:
                self.pin.left = self.pin_position
                self.pin.update('%.1f' % self.pin_percentage)
