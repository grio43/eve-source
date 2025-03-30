#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\hybridWindow.py
import uthread
from carbonui import uiconst
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.uicore import uicore
from eve.client.script.ui.control.themeColored import SpriteThemeColored
from eve.client.script.ui.util.form import FormWnd
from eve.client.script.ui.util.uix import GetDialogIconTexturePath

class HybridWindow(Window):
    __guid__ = 'form.HybridWindow'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.ResetSelf()
        format = attributes.format
        caption = attributes.caption
        modal = attributes.modal
        buttons = attributes.buttons
        minw = attributes.get('minW', 320)
        minh = attributes.get('minH', 240)
        icon = attributes.icon
        blockconfirm = attributes.get('blockconfirm', False)
        self.name = caption
        self.result = {}
        self.isModal = modal
        self.blockconfirmonreturn = blockconfirm
        Container(name='push', parent=self.GetMainArea(), align=uiconst.TORIGHT, width=const.defaultPadding)
        Container(name='push', parent=self.GetMainArea(), align=uiconst.TOTOP, height=const.defaultPadding)
        if icon:
            self.icon = GetDialogIconTexturePath(icon)
        self.state = uiconst.UI_HIDDEN
        self.DefineButtons(buttons)
        self.MakeUnMinimizable()
        self.MakeUncollapseable()
        self.SetCaption(caption)
        self.SetMinSize([minw, minh], 1)
        self.form, self.retfields, self.reqresult, self.panels, self.errorcheck, refresh = sm.GetService('form').GetForm(format, FormWnd(name='form', align=uiconst.TOTOP, parent=self.GetMainArea()))
        self.form.OnChange = self.OnChange
        for each in self.form.sr.panels.itervalues():
            each.OnChange = self.OnChange

        self.refresh = refresh
        for each in refresh:
            for textControl in each[1:]:
                textControl.OnSizeChanged = self.UpdateTextControlSize

        self.state = self.form.state = uiconst.UI_NORMAL
        self.width = self.minsize[0]
        if self.form.sr.focus:
            uicore.registry.SetFocus(self.form.sr.focus)
        else:
            uicore.registry.SetFocus(self)
        uthread.new(self.RefreshSize_, 1)

    def UpdateTextControlSize(self, *args):
        self.RefreshSize_()

    def ResetSelf(self):
        self.scrolllist = None
        self.listentry = None
        self.reqresult = []
        self.retfields = []
        self.tabpanels = []
        self.tabparents = []
        self.result = {}
        self.tabs = []
        self.minh = 0
        self.minw = 240
        self.refreshHeight = []
        self.onconfirmargs = ()
        self.checkingtabs = 0
        self.settingheight = 0
        self.activetab = None
        self.refresh = None
        self.form = None
        self.sr.queue = None
        self.locked = 0

    def Close(self, *args, **kwds):
        if self.HasPendingModalResult():
            return Window.Close(self, *args, **kwds)
        if self.sr.queue is not None:
            self.sr.queue.send(None)
        self.form.OnChange = None
        self.form.sr.focus = None
        for each in self.form.sr.panels.itervalues():
            each.OnChange = None

        self.form.Close()
        self.form = None
        self.retfields = None
        self.reqresult = None
        self.panels = None
        self.errorcheck = None
        self.ResetSelf()
        Window.Close(self, *args, **kwds)

    def OnChange(self, *args):
        self.OnScale_(*args)

    def OnScale_(self, *args):
        self.RefreshSize_()

    def OnEndScale_(self, *args):
        self.RefreshSize_()

    def RefreshSize_(self, update = 0, *args):
        self.RefreshTextControls(self.refresh)
        if self.locked:
            return
        minformheight = 0
        notformheight = 0
        hasTab = 0
        minw = 0
        for each in self.form.children:
            if each.name == 'form':
                for each2 in each.children:
                    if each2.name == 'form':
                        self.RefreshHeight(each2)

                self.RefreshHeight(each)
                minformheight = max(minformheight, each.height + each.padTop + each.padBottom)
            elif each.name == 'tabparent':
                hasTab = 1
                if each.width > minw:
                    minw = each.width
            else:
                notformheight += each.height + each.padTop + each.padBottom

        if self.form.align in (uiconst.TOTOP, uiconst.TOBOTTOM):
            self.form.height = minformheight + notformheight
        totHeight = minformheight + sum([ each.height + each.padTop + each.padBottom for each in self.form.parent.children if each.align in (uiconst.TOTOP, uiconst.TOBOTTOM) ])
        if hasTab == 1:
            if self.minsize[0] < minw:
                self.minsize[0] = minw
        minHeight = totHeight + 70
        if self.stacked:
            minHeight += 6
        if minHeight > self.minsize[1]:
            self.SetMinSize([self.minsize[0], minHeight], 1)

    def RefreshHeight(self, w):
        w.height = sum([ x.height for x in w.children if x.state != uiconst.UI_HIDDEN and x.align in (uiconst.TOBOTTOM, uiconst.TOTOP) ])

    def RefreshTextControls(self, rlist):
        for each in rlist:
            itemToUpdate = each[0]
            m = 0
            for textcontrol in each[1:]:
                if textcontrol.GetAlign() in (uiconst.TOTOP, uiconst.TOBOTTOM, uiconst.TOALL):
                    m = max(m, textcontrol.textheight + textcontrol.padTop + textcontrol.padBottom)
                else:
                    m = max(m, textcontrol.textheight + textcontrol.top * 2)

            itemToUpdate.height = m

    def Execute(self):
        if self.sr.queue is not None:
            raise RuntimeError('already executing?')
        self.sr.queue = uthread.Channel()
        ret = self.sr.queue.receive()
        self.sr.queue = None
        return ret

    def Confirm(self, sender = None, *args):
        uicore.registry.SetFocus(uicore.desktop)
        if sender is None:
            if getattr(uicore.registry.GetFocus(), 'stopconfirm', 0):
                return
        self.result = sm.GetService('form').ProcessForm(self.retfields, self.reqresult, self.errorcheck)
        if self.result is None:
            return
        if uicore.registry.GetModalWindow() == self:
            import triui
            self.SetModalResult(triui.ID_OK)
        else:
            if self.sr.queue is not None:
                self.sr.queue.send(self.result)
            ret = self.result
            self.Close()
            return ret

    ConfirmFunction = Confirm
