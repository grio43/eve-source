#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\comtool\focus.py
import weakref
from carbon.common.script.sys.service import Service
from carbonui import uiconst

class Focus(Service):
    __guid__ = 'svc.focus'
    __servicename__ = 'focus'
    __displayname__ = 'Focus Tool'
    __dependencies__ = []

    def Run(self, memStream = None):
        self.focusChannelWindow = None

    def SetChannelFocus(self, char = None):
        channel = self.GetFocusChannel()
        if channel is not None:
            channel.Maximize()
            stack = getattr(channel.sr, 'stack', None)
            if stack and stack.state == uiconst.UI_HIDDEN:
                return
            channel.SetCharFocus(char)

    def SetFocusChannel(self, channel = None):
        if channel is not None:
            self.focusChannelWindow = weakref.ref(channel)
        else:
            self.focusChannelWindow = None

    def GetFocusChannel(self):
        if self.focusChannelWindow:
            ch = self.focusChannelWindow()
            if ch and not ch.destroyed:
                return ch
