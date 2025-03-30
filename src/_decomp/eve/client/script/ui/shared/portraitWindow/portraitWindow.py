#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\portraitWindow\portraitWindow.py
import localization
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui import uiconst
from carbonui.button.group import ButtonGroup
from eve.common.lib import appConst as const
from carbonui.control.window import Window
from menu import MenuLabel

class PortraitWindow(Window):
    __guid__ = 'form.PortraitWindow'
    default_windowID = 'PortraitWindow'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        charID = attributes.charID
        self.charID = charID
        self.photoSize = 512
        self.width = self.photoSize + 2 * const.defaultPadding
        self.height = self.width + 46
        self.SetMinSize([self.width, self.height])
        self.MakeUnResizeable()
        btnGroup = ButtonGroup(parent=self.content, idx=0, align=uiconst.TOBOTTOM)
        self.switchBtn = Button(parent=btnGroup, label=localization.GetByLabel('UI/Preview/ViewFullBody'), func=self.SwitchToFullBody, args=(), btn_modalresult=1, btn_default=1)
        self.picParent = Container(name='picpar', parent=self.content, align=uiconst.TOALL, pos=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.pic = Sprite(parent=self.picParent, align=uiconst.TOALL)
        self.pic.GetMenu = self.PicMenu
        self.Load(charID)
        from eve.client.script.ui.shared.preview import PreviewCharacterWnd
        previewWnd = PreviewCharacterWnd.GetIfOpen()
        if previewWnd:
            previewWnd.CloseByUser()

    def Load(self, charID):
        caption = localization.GetByLabel('UI/InfoWindow/PortraitCaption', character=charID)
        self.SetCaption(caption)
        sm.GetService('photo').GetPortrait(charID, self.photoSize, self.pic)

    def PicMenu(self, *args):
        m = []
        m.append((MenuLabel('UI/Commands/CapturePortrait'), sm.StartService('photo').SavePortraits, [self.charID]))
        m.append((MenuLabel('/Carbon/UI/Common/Close'), self.CloseByUser))
        return m

    def SwitchToFullBody(self):
        try:
            self.switchBtn.Disable()
            wnd = sm.GetService('preview').PreviewCharacter(self.charID)
        finally:
            self.switchBtn.Enable()

        if wnd:
            self.CloseByUser()
