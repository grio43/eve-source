#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\colorpicker.py
import trinity
import log
from carbonui import uiconst
from carbonui.control.contextMenu.menuUtil import ClearMenuLayer
from carbonui.primitives.frame import Frame
from carbonui.window.underlay import WindowUnderlay
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.uicore import uicore

class ColorSwatch(Container):
    swatches = [('faf5e1', None),
     ('ebd492', None),
     ('cb9133', None),
     ('825830', None),
     ('f6e631', None),
     ('f59122', None),
     ('d95100', None),
     ('bf1616', None),
     ('790000', None),
     ('7f1157', None),
     ('abc8e2', None),
     ('598cb9', None),
     ('375d81', None),
     ('3b8bd1', None),
     ('124d8c', None),
     ('183152', None),
     ('185662', None),
     ('6e9058', None),
     ('3f740b', None),
     ('516324', None),
     ('384328', None),
     ('bfb7aa', None),
     ('625e57', None),
     ('19191c', None)]
    swatchsize = 16

    def hex_to_rgb(self, colorstring):
        colorstring = colorstring.strip()
        if len(colorstring) != 6:
            raise ValueError, 'input #%s is not in #RRGGBB format' % colorstring
        r, g, b = colorstring[:2], colorstring[2:4], colorstring[4:]
        r, g, b = [ int(n, 16) for n in (r, g, b) ]
        return (r / 255.0, g / 255.0, b / 255.0)

    def Startup(self, frameColor = (0.5, 0.5, 0.5, 1.0), padding = 0, *args):
        l, t, w, h = self.GetAbsolute()
        swatchesperrow = abs(w / self.swatchsize)
        x, y = (0, 0)
        for hex, swatchID in self.swatches:
            sc = Container(name='bottom', parent=self, align=uiconst.TOPLEFT, pos=(x * self.swatchsize,
             y * self.swatchsize,
             self.swatchsize,
             self.swatchsize), state=uiconst.UI_NORMAL, padding=(padding,
             padding,
             padding,
             padding))
            sc.OnClick = (self.OnPickColor, sc)
            sc.swatchID = swatchID
            Frame(parent=sc, color=frameColor)
            color = self.hex_to_rgb(hex)
            Fill(parent=sc, color=color)
            x += 1
            if x == swatchesperrow:
                x = 0
                y += 1

    def OnPickColor(self, obj, *args):
        fill = obj.FindChild('fill')
        if fill and self.sr.dad is not None:
            if hasattr(self.sr.dad, 'SetHSV'):
                self.sr.dad.SetHSV(fill.color.GetHSV())


class ColorPreview(Container):
    expanding = 0
    expanded = 0

    def Startup(self):
        self.sr.preview = preview = Container(parent=self, align=uiconst.TOALL, pos=(0, 0, 0, 0), state=uiconst.UI_NORMAL)
        self.sr.preview.OnClick = self.OnPickColor
        self.sr.colorfill = Fill(parent=preview, color=(0.0, 1.0, 0.0, 1.0))

    def OnPickColor(self, *args):
        if not self.expanding and not self.expanded:
            self.Expand()

    def Expand(self, *args):
        self.expanding = 1
        if sm.GetService('connection').IsConnected():
            eve.Message('ComboExpand')
        log.LogInfo('ColorPreview', self.name, 'expanding')
        colorpar = Container(name='colors', align=uiconst.TOPLEFT, width=112, height=62)
        uicore.layer.menu.children.insert(0, colorpar)
        colorSwatch = ColorSwatch(name='colorSwatch', align=uiconst.TOALL, parent=colorpar)
        colorSwatch.Startup()
        colorSwatch.sr.dad = self
        self.sr.wndUnderlay = WindowUnderlay(parent=colorpar)
        self.sr.wndUnderlay.padding = -6
        l, t, w, h = self.sr.preview.GetAbsolute()
        colorpar.left = [l + w, l - colorpar.width][l + w + colorpar.width > uicore.desktop.width]
        colorpar.top = [t + h, t - colorpar.height][t + h + colorpar.height > uicore.desktop.height]
        colorpar.state = uiconst.UI_NORMAL
        self.colorpar = colorpar
        self.sr.cookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEUP, self.OnGlobalClick)
        self.expanding = 0
        self.expanded = 1
        log.LogInfo('ColorPreview', self.name, 'expanded')

    def OnGlobalClick(self, fromwhere, *etc):
        if self.colorpar:
            if uicore.uilib.mouseOver == self.colorpar or fromwhere.IsUnder(self.colorpar):
                log.LogInfo('ColorPreview.OnGlobalClick Ignoring all clicks from colorpar')
                return 1
            self.Cleanup()
        return 0

    def Cleanup(self, setfocus = 1):
        if self.sr.cookie:
            uicore.event.UnregisterForTriuiEvents(self.sr.cookie)
            self.sr.cookie = None
            self.colorpar = None
            ClearMenuLayer()
            self.expanded = 0
        if setfocus:
            uicore.registry.SetFocus(self)

    def OnGlobalMouseDown(self, downOn):
        if not downOn.IsUnder(self.colorpar):
            ClearMenuLayer()

    def SetHSV(self, hsv):
        self.sr.colorfill.color.SetHSV(*hsv)
        if self.sr.dad and hasattr(self.sr.dad, 'SetHSV'):
            if self.sr.layerid is not None:
                self.sr.dad.SetHSV(self.sr.layerid, self.sr.colorfill.color.GetHSV())
            else:
                self.sr.dad.SetHSV(self.sr.colorfill.color.GetHSV())

    def FromInt(self, val):
        c = trinity.TriColor()
        c.FromInt(val)
        self.sr.colorfill.SetRGBA(c.r, c.g, c.b, c.a)
        self.SetHSV(c.GetHSV())

    def AsInt(self):
        self.sr.colorfill.color.AsInt()

    def FromSwatch(self, swatch):
        cswatch = ColorSwatch()
        ccolor = cswatch.hex_to_rgb(cswatch.swatches[swatch])
        self.sr.colorfill.SetRGBA(*ccolor)
