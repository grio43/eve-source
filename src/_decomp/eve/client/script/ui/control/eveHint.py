#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\eveHint.py
import log
import types
import uthread
from carbon.client.script.util.misc import GetAttrs
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from carbonui.util.various_unsorted import ParanoidDecoMethod
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelSmall

class BubbleHint(Container):
    __guid__ = 'xtriui.BubbleHint'
    default_name = 'bubblehint'
    default_left = 200
    default_top = 100
    default_width = 100
    default_height = 100
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.sr.showExtended = None
        self.extendedHint = ''
        self.collapsedHint = ''
        self.expanded = 0
        self.sr.p5 = p5 = Sprite(parent=self, name='p5', pos=(0, -14, 18, 18), align=uiconst.TOPRIGHT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Hint/pointerToTopRight.png')
        self.sr.p4 = p4 = Sprite(parent=self, name='p4', pos=(0, -14, 18, 18), align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Hint/pointerToTopCenter.png')
        self.sr.p3 = p3 = Sprite(parent=self, name='p3', pos=(0, -14, 18, 18), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Hint/pointerToTopLeft.png')
        self.sr.p2 = p2 = Sprite(parent=self, name='p2', pos=(0, -14, 18, 18), align=uiconst.BOTTOMRIGHT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Hint/pointerToBottomRight.png')
        self.sr.p1 = p1 = Sprite(parent=self, name='p1', pos=(0, -14, 18, 18), align=uiconst.CENTERBOTTOM, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Hint/pointerToBottomCenter.png')
        self.sr.p0 = p0 = Sprite(parent=self, name='p0', pos=(0, -14, 18, 18), align=uiconst.BOTTOMLEFT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Hint/pointerToBottomLeft.png')
        self.sr.frame = Frame(parent=self, texturePath='res:/UI/Texture/classes/Hint/background.png', rectWidth=18, rectHeight=18, color=(1.0, 1.0, 1.0, 0.5))
        self.content = Container(name='content', parent=self, idx=0, padding=(2, 4, 2, 4))
        Fill(parent=self, color=(0.0, 0.0, 0.0, 0.8), padding=(2, 2, 2, 2))

    def ShowHint(self, hint, pointer = 0, textMaxWidth = 200):
        self.content.Flush()
        if type(hint) != types.ListType:
            hint = [hint]
        maxWidth = 0
        for entryData in hint:
            if entryData in ('<line>', '<dotline>'):
                Line(parent=self.content, align=uiconst.TOTOP, height=1)
                continue
            entry = HintEntry(name='entryparent', parent=self.content, align=uiconst.TOTOP)
            entry.Startup(entryData, textMaxWidth)
            entry.OnMouseEnter = self.DecoEntryMouseEnter(entry, getattr(entry, 'OnMouseEnter', None))
            entry.OnMouseExit = self.DecoEntryMouseExit(entry, getattr(entry, 'OnMouseExit', None))

        self.width = max([ each.width for each in self.content.children ]) + 12
        self.height = sum([ each.height for each in self.content.children ]) + 8
        self.SetPointer(pointer)
        self.data = (hint, pointer)

    def DecoEntryMouseExit(self, entry, f):

        def OnMouseExit(entry, *args):
            sub = getattr(entry.sr, 'sub', None)
            if sub:
                if uicore.uilib.mouseOver != sub:
                    self.ClearSub(entry)
            elif type(f) in (list, tuple):
                callback, passedArgs = f
                callback(passedArgs, entry, *args)
            if f is not None:
                f(entry, *args)

        return (OnMouseExit, entry)

    def DecoEntryMouseEnter(self, entry, f):

        def OnMouseEnter(entry, *args):
            self.Expand()
            if f is None:
                pass
            elif type(f) in (list, tuple):
                callback, passedArgs = f
                callback(passedArgs, entry, *args)
            else:
                f(entry, *args)

        return (OnMouseEnter, entry)

    def OnEntryMouseExit(self, entry, *args):
        if getattr(entry, 'OnMouseExit', None) not in (None, self.OnEntryMouseExit):
            entry.OnMouseExit(entry, *args)

    def OnEntryMouseEnter(self, entry, *args):
        self.Expand()
        if getattr(entry, 'OnMouseEnter', None) not in (None, self.OnEntryMouseEnter):
            entry.OnMouseEnter(entry, *args)

    def OnMouseEnter(self, *args):
        self.Expand()

    def Expand(self):
        func = self.sr.Get('ExpandHint', None)
        if func:
            func(self, 1)

    def _ShowSubhint(self, passedArgs, entry):
        if not getattr(entry.sr, 'hilite', None):
            entry.sr.hilite = Fill(parent=entry)
        self.ClearSubs()
        self.parent.SetOrder(0)
        for each in self.content.children:
            if each != entry and getattr(each, 'sr', None) and getattr(each.sr, 'hilite', None):
                each.sr.hilite.state = uiconst.UI_HIDDEN

        entry.sr.hilite.state = uiconst.UI_DISABLED
        if len(passedArgs) == 2:
            funcName, args = passedArgs
            func = getattr(self, funcName, None)
            if not func:
                log.LogError('Unsupported dynamic function in bubblehint', funcName)
                return
            hint = func(*args)
        else:
            hint, = passedArgs
        bubble = BubbleHint(parent=self.parent, align=uiconst.TOPLEFT, width=0, height=0, idx=0, state=uiconst.UI_NORMAL)
        bubble.ShowHint(hint, None, 100)
        if not self or self.destroyed:
            return
        self.sr.sub = bubble
        if self.parent:
            pl, pt, pw, ph = self.parent.GetAbsolute()
            ll, lt, lw, lh = entry.GetAbsolute()
            bubble.left = ll - pl + lw - 6
            bubble.top = lt - pt - 2

    def SetPointer(self, pointer, reposition = 1):
        self.sr.p0.state = uiconst.UI_HIDDEN
        self.sr.p1.state = uiconst.UI_HIDDEN
        self.sr.p2.state = uiconst.UI_HIDDEN
        self.sr.p3.state = uiconst.UI_HIDDEN
        self.sr.p4.state = uiconst.UI_HIDDEN
        self.sr.p5.state = uiconst.UI_HIDDEN
        if pointer is not None:
            p = self.sr.Get('p%s' % pointer, None)
            p.state = uiconst.UI_DISABLED
            if pointer in (0, 3):
                left = self.parent.width / 2 + 2
            elif pointer in (2, 5):
                left = self.parent.width / 2 - self.width - 2
            elif pointer in (1, 4):
                left = (self.parent.width - self.width) / 2 + 1
            sidePointerIdx = pointer
            if pointer in (0, 1, 2):
                top = self.parent.height / 2 - self.height - 18
            elif pointer in (3, 4, 5):
                top = self.parent.height / 2 + 20
            if reposition:
                self.left = left
                self.top = top
        elif GetAttrs(self, 'parent') is not None:
            self.left = self.parent.width / 2 + 12
            self.top = self.parent.height / 2 - 8

    def GetEntry(self, id_):
        for each in self.content.children:
            if GetAttrs(each, 'data', 'id') == id_:
                return each

    def Offset(self, x, y, pointer):
        self.SetPointer(pointer, 0)
        self.sr.left = self.left
        self.sr.top = self.top
        self.left += x
        self.top += y

    def ResetOffset(self):
        if self.sr.Get('left', None):
            self.left = self.sr.left
            self.top = self.sr.top
        if getattr(self, 'data', None):
            self.SetPointer(self.data[1])

    def GetBubbleHint(self, *args):
        return sm.GetService('systemmap').GetBubbleHint(*args)

    def ClearSubs(self):
        if self.sr.Get('sub', None):
            self.sr.sub.Close()
            self.sr.sub = None

    def _OnClose(self):
        self.ClearSubs()


class HintEntry(Container):

    def Startup(self, data, textMaxWidth):
        self.data = data
        self.textMaxWidth = textMaxWidth
        self.Refresh()

    def Refresh(self):
        data = self.data
        self.Flush()
        textMaxWidth = self.textMaxWidth
        if isinstance(data, basestring):
            data = HintEntryData(data)
        elif isinstance(data, tuple):
            text, (event, func, args) = data
            data = HintEntryData(text, event=event, func=func, args=args)
        if data.menuGetter:
            self.state = uiconst.UI_NORMAL
            self.GetMenu = data.menuGetter
        label = EveLabelSmall(text=data.text, parent=self, left=5, top=1, state=uiconst.UI_DISABLED, idx=0)
        self.sr.label = label
        self.width = label.textwidth
        self.height = label.textheight + 1
        self.name = data.text

        def AddIcon(iconNum, left = -1):
            Icon(icon=iconNum, parent=self, pos=(left,
             -2,
             16,
             16), align=uiconst.TOPRIGHT, idx=0, state=uiconst.UI_DISABLED)
            self.width += 14

        if data.func:
            setattr(self, data.event, (getattr(self, data.func, None), data.args))
            self.state = uiconst.UI_NORMAL
            if data.func == 'ShowSubhint':
                AddIcon(iconNum='ui_38_16_127')
            elif data.func == 'ShowInfo':
                AddIcon(iconNum='ui_38_16_126')
            elif data.func == 'OpenAssets':
                AddIcon(iconNum='ui_38_16_125')
        if data.talking:
            AddIcon(iconNum='ui_38_16_91', left=0)

    def GetBubble(self):
        return self.FindParentByName('bubblehint')

    def OnMouseEnter(self, *etc):
        self.sr.label.bold = True

    OnMouseEnter = ParanoidDecoMethod(OnMouseEnter, ('sr', 'label'))

    def OnMouseExit(self, *etc):
        self.sr.label.bold = False

    OnMouseExit = ParanoidDecoMethod(OnMouseExit, ('sr',))

    def ShowInfo(self, passedArgs, *args):
        typeID, itemID = passedArgs
        sm.GetService('info').ShowInfo(typeID, itemID)

    def ShowSubhint(self, passedArgs, entry):
        bubble = self.GetBubble()
        if bubble is None:
            return
        if len(passedArgs) == 2:
            uthread.new(bubble._ShowSubhint, passedArgs, entry)
        else:
            bubble._ShowSubhint(passedArgs, entry)

    def OpenAssets(self, passedArgs, *args):
        stationID, = passedArgs
        sm.GetService('assets').Show(stationID)

    def OpenAddressbook(self, contactType, *args):
        ab = sm.GetService('addressbook')
        ab.Show()
        ab.ShowContacts(contactType)


class HintEntryData():

    def __init__(self, text, id = None, event = None, func = None, args = None, menuGetter = None, talking = False):
        self.text = text
        self.event = event
        self.func = func
        self.args = args
        self.menuGetter = menuGetter
        self.talking = talking
        self.id = id
