#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\spiffy.py
import sys
import log
import types
import uthread
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.util import timerstuff
from carbonui import uiconst
from carbonui.control.contextMenu.menuUtil import ClearMenuLayer
from carbonui.window.underlay import WindowUnderlay
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from eve.client.script.ui.control import eveIcon, eveLabel
from eve.client.script.ui.util import uix
ENTRY_HASSUBMENU = 1L
ENTRY_ISDYNAMIC = 2L
ENTRY_VADJUST = 4L
ADDTOP = 2
MENUWIDTH = 64
BARWIDTH = 24
TRACEWIDTH = 7
HILITEALPHA = 0.25
GHOSTALPHA = 0.5
SPACER = 4

def MenuHeader(label, **kw):
    entry = {'label': label,
     'flags': ENTRY_VADJUST,
     'height': 16,
     'hilited': 2,
     'disabled': True}
    entry.update(kw)
    return entry


class MenuEntry(Container):
    default_height = 14
    default_name = 'entry'
    default_align = uiconst.TOTOP
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        triangleRight = Sprite(parent=self, name='TriangleRight', pos=(3, 3, 10, 10), align=uiconst.TOPRIGHT, state=uiconst.UI_HIDDEN, texturePath='res:/UI/Texture/Shared/triangleRight.png')

    def Setup(self, entry, menuobj = None, fontsize = None, addleft = 3):
        self.hilited = self.ghosted = self.disabled = False
        self.flags = 0L
        self.action = self.args = self.iconmap = None
        self.iconmapscaling = 0.25
        self.fontsize = fontsize
        self.menuobj = menuobj
        if type(entry) == types.DictType:
            for k, v in entry.iteritems():
                setattr(self, k, v)

        elif type(entry) == types.TupleType:
            label = entry[0]
            if type(label) == types.TupleType:
                self.label = label[0]
                if len(label) > 1:
                    self.iconmap = label[1]
                    if len(label) > 2:
                        self.iconmapscaling = label[2]
                else:
                    self.iconmap = 'ui_9_64_14'
            else:
                self.label = label
                self.iconmap = None
            action = entry[1]
            if type(action) == types.TupleType:
                if action[0] == 'isDynamic':
                    self.flags |= ENTRY_HASSUBMENU | ENTRY_ISDYNAMIC
                    self.action = action[1]
                    if len(action) > 2:
                        self.args = action[2]
                else:
                    raise TypeError, 'Unsupported submenu type'
            elif type(action) == types.ListType:
                self.flags |= ENTRY_HASSUBMENU
                self.action = action
            elif callable(action) and not self.disabled:
                self.action = action
                if len(entry) >= 3:
                    self.args = entry[2]
            else:
                self.action = None
        else:
            raise TypeError, 'Unsupported entry definition type'
        if self.fontsize:
            self.hspace = 0
        elif self.height <= 16:
            self.fontsize = 10
            self.hspace = 1
        else:
            self.fontsize = 12
            self.hspace = 1
        self.name = self.label
        if not self.action:
            self.disabled = True
        if self.disabled and not self.hilited:
            self.ghosted = True
        if hasattr(self, 'OnPreCreate'):
            self.OnPreCreate(self)
        self.sr.leftedge = Container(name='push', parent=self, width=addleft, state=uiconst.UI_DISABLED, align=uiconst.TOLEFT)
        if self.iconmap:
            self.sr.icon = icon = eveIcon.Icon(parent=self, align=uiconst.TOLEFT, state=uiconst.UI_DISABLED)
            icon.LoadIcon(self.iconmap, ignoreSize=True)
            icon.SetSize(self.height, self.height)
            icon.left = addleft
            if self.ghosted:
                icon.opacity = GHOSTALPHA
        SPACER = 4
        Container(name='push', parent=self, width=SPACER, state=uiconst.UI_DISABLED, align=uiconst.TOLEFT)
        indent = self.sr.leftedge.width + (self.height, 0)[not self.iconmap] + SPACER
        self.sr.label = eveLabel.Label(text=self.label, parent=self, fontsize=self.fontsize, letterspace=self.hspace, state=uiconst.UI_DISABLED, left=indent)
        self.sr.label.top = (self.height - self.sr.label.textheight) / 2 + 1
        if self.ghosted:
            self.sr.label.opacity = GHOSTALPHA
        self.width = indent + self.sr.label.textwidth + SPACER + SPACER + 3
        if self.flags & ENTRY_HASSUBMENU:
            self.triangle = triangle = self.GetChild('TriangleRight')
            triangle.state = uiconst.UI_DISABLED
            triangle.top = (self.height - 10) / 2
            triangle.left += 2
        self.children[1].state = uiconst.UI_HIDDEN
        self.sr.selection2 = self.children[2]
        if self.hilited == 2:
            c = (0.0, 0.0, 0.0, 0.2)
        else:
            c = (1.0, 1.0, 1.0, 0.25)
        self.sr.selection = Fill(parent=self, idx=0, color=c)
        self.sr.selection.state = uiconst.UI_HIDDEN
        if self.iconmap:
            self.sr.iconbg = Fill(parent=self, idx=-1, color=(0, 0, 0, 0.2), left=addleft, top=0, width=self.height, height=self.height, align=uiconst.RELATIVE)
        if hasattr(self, 'OnPostCreate'):
            self.OnPostCreate(self)
        if self.hilited:
            self.OnMouseEnter()

    def OnMouseEnter(self, *args):
        if self.hilited or not self.disabled:
            self.sr.selection.state = uiconst.UI_DISABLED
            if self.iconmap:
                self.sr.iconbg.state = uiconst.UI_HIDDEN

    def OnMouseExit(self, *args):
        if not self.hilited:
            self.sr.selection.state = uiconst.UI_HIDDEN
            if self.iconmap:
                self.sr.iconbg.state = uiconst.UI_DISABLED

    def OnMouseUp(self, *args):
        if self.disabled:
            return
        if not self.flags & ENTRY_HASSUBMENU:
            uthread.new(ClearMenuLayer)
            if self.args:
                uthread.new(self.action, *self.args)
            else:
                uthread.new(self.action)

    def GetSubContent(self):
        if self.flags & ENTRY_ISDYNAMIC:
            try:
                if self.args:
                    m = self.action(*self.args)
                else:
                    m = self.action()
            except Exception as e:
                log.LogException()
                print str(e)
                m = [{'label': 'ERROR',
                  'disabled': True,
                  'ghosted': True,
                  'action': None,
                  'iconmap': '44_8',
                  'iconmapscaling': 0.125}]
                sys.exc_clear()

        else:
            m = self.action
        return m


class Menu(Container):
    default_name = 'contextualmenu'
    default_width = 80
    default_height = 64
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.submenu = None
        self.hilitedentry = None
        entries = Container(parent=self, name='entries', padding=(2, 2, 2, 2), align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN)
        underlay = WindowUnderlay(parent=self)

    def Setup(self, menu, entryheight = 16, position = None, origin = 'topleft', caption = None, fromentry = None, reverse = False):
        self.reverse = reverse
        self.origin = origin
        self.entryheight = entryheight
        self.fromentry = fromentry
        if fromentry:
            self.parentmenu = self.fromentry.menuobj
        self.state = uiconst.UI_HIDDEN
        self.align = uiconst.RELATIVE
        container = Container(name='SpiffyEntryList', parent=self, idx=0, pos=(0, 0, 0, 0))
        height = 0
        width = 0
        Container(name='push', parent=container, align=uiconst.TOTOP, height=2)
        allflags = 0
        wasline = 1
        if caption or fromentry:
            margin = (0, 1)[not fromentry]
        else:
            margin = 5
        if not menu:
            menu = [{'label': 'No items',
              'disabled': True,
              'ghosted': True,
              'action': None,
              'iconmap': '44_8',
              'iconmapscaling': 0.125}]
        while menu[-1] is None:
            menu.pop()

        addtop = 0
        for entry in menu:
            if entry:
                item = MenuEntry(parent=container, height=entryheight)
                item.Setup(entry, addleft=margin, menuobj=self)
                item.OnMouseEnter = (self.OnEntryEnter, item)
                item.OnMouseExit = (self.OnEntryExit, item)
                width = max(width, item.width)
                if item.flags & ENTRY_VADJUST and fromentry and not height:
                    addtop = item.height
                allflags |= item.flags
                wasline = 0
            else:
                if wasline:
                    continue
                item = Line(parent=container, align=uiconst.TOTOP)
                wasline = 1
            height += item.height

        if fromentry and item and item.flags & ENTRY_VADJUST:
            subbottom = item.height
        else:
            subbottom = 0
        if allflags & ENTRY_HASSUBMENU:
            addwidth = 8
        else:
            addwidth = 0
        self.height = ADDTOP + height + ADDTOP
        if fromentry and not caption:
            addwidth += TRACEWIDTH
            edge = Container(name='SpiffyBar', parent=container, align=uiconst.TOLEFT, width=TRACEWIDTH, idx=0)
            self.sr.trace = side = Fill(parent=self, align=uiconst.RELATIVE, left=0, top=0, width=TRACEWIDTH, idx=0)
        else:
            edge = None
            if caption:
                raise RuntimeError('SpiffyBar is still broken and needs fixing')
                addwidth += BARWIDTH
                side = uix.GetFill(name='SpiffyBar', parent=container, align=uiconst.TOLEFT, width=BARWIDTH, idx=0)
                t = eveLabel.Label(text=caption, parent=side, width=self.height, height=BARWIDTH, state=uiconst.UI_NORMAL)
                sm.GetService('textmetr').RefreshHeight(t)
                t.left = (BARWIDTH - self.height + t.height) / 2 + 1
                t.height = BARWIDTH
                t.top = (self.height - BARWIDTH) / 2 - 1 - 12
                t.rotation = 90.0
                t.control.model.areas[0].areaMaterials[0].diffuse.a = 0.66
            else:
                side = None
        if side:
            side.SetRGBA(1.0, 1.0, 1.0, HILITEALPHA)
        self.width = max(MENUWIDTH, width) + addwidth
        if fromentry:
            p = self.parentmenu
            while True:
                if self.reverse:
                    left = p.absoluteLeft - self.width + 3
                else:
                    left = p.absoluteRight - 5
                if left < 0 or left + self.width > uicore.desktop.absoluteRight:
                    self.reverse = not self.reverse
                else:
                    break

            fl, ft, fw, fh = fromentry.GetAbsolute()
            top = ft - ADDTOP - addtop
            if top + self.height > uicore.desktop.absoluteBottom:
                top = ft + fh + ADDTOP + subbottom - self.height
            if self.reverse and side:
                side.width = 10
                side.left = self.width - side.width
        else:
            if position:
                x, y = position
            else:
                x, y = uicore.uilib.x, uicore.uilib.y
            if origin == 'topleft':
                left = x
                top = y - addtop
            elif origin == 'bottomleft':
                left = x
                top = y - self.height + subbottom
            elif origin == 'bottomright':
                left = x - self.width
                top = y - self.height + subbottom
            elif origin == 'topright':
                left = x - self.width
                top = y - addtop
            else:
                raise ValueError, "origin must be one of 'topleft', 'topright', 'bottomleft', 'bottomright'"
            if left < 0:
                left = 0
            elif left + self.width > uicore.desktop.absoluteRight:
                left = uicore.desktop.absoluteRight - self.width
        if top < 0:
            top = 0
        elif top + self.height > uicore.desktop.absoluteBottom:
            top = uicore.desktop.absoluteBottom - self.height
        if edge:
            if left < p.left:
                edge.width = 4
        self.left = left
        self.top = top
        self.state = uiconst.UI_NORMAL

    def OnEntryEnter(self, entry):
        MenuEntry.OnMouseEnter(entry)
        PlaySound(uiconst.SOUND_ENTRY_HOVER)
        if self.fromentry:
            self.DoEntryTrace(entry)
        if entry != self.hilitedentry:
            self.hilitedentry = entry
            if self.submenu:
                self.DoSubmenuCollapse()
            if entry.flags & ENTRY_HASSUBMENU:
                self.submenuTimer = timerstuff.AutoTimer(settings.user.ui.Get('menuExpandTime', 10), self.DoSubmenuExpand, entry)

    def OnEntryExit(self, entry):
        if not (self.submenu and self.submenu.fromentry == entry):
            MenuEntry.OnMouseExit(entry)
            if self.fromentry:
                if self.submenu:
                    self.DoEntryTrace(entry)
                else:
                    self.sr.trace.top = 99999

    def DoSubmenuExpand(self, entry):
        self.submenuTimer = None
        self.DoSubmenuCollapse()
        if entry == self.hilitedentry:
            entry.OnMouseEnter()
            if self.fromentry:
                self.DoEntryTrace(entry)
            self.submenu = Menu(parent=uicore.layer.menu, idx=0)
            self.submenu.Setup(entry.GetSubContent(), fromentry=entry, reverse=self.reverse, entryheight=self.entryheight)

    def DoSubmenuCollapse(self):
        if self.submenu:
            self.submenu.KillMe()
            self.submenu = None

    def DoEntryTrace(self, entry):
        fl, ft, fw, fh = self.fromentry.GetAbsolute()
        el, et, ew, eh = entry.GetAbsolute()
        if et + eh / 2 > ft + fh / 2:
            top = ft
            if self.reverse:
                bottom = et
            else:
                bottom = et + eh
        else:
            bottom = ft + fh
            if self.reverse:
                top = et + eh
            else:
                top = et
        self.sr.trace.top = top - self.absoluteTop
        self.sr.trace.height = bottom - top

    def KillMe(self):
        self.submenuTimer = None
        if self.submenu:
            self.submenu.KillMe()
            self.submenu = None
        if self.fromentry:
            self.fromentry.OnMouseExit()
        if not self.destroyed:
            self.Close()


def CreateMenu(menu = None, *args, **kwargs):
    if not menu:
        return None
    ClearMenuLayer()
    obj = Menu(parent=uicore.layer.menu)
    obj.Setup(menu, *args, **kwargs)
    return obj
