#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\xmppchatclient\chatinvitewindow.py
import carbonui.const as uiconst
import localization
import uthread2
from carbonui import uiconst
from carbonui.uicore import uicore
from carbonui.primitives.container import Container
from carbonui.button.group import ButtonGroup
from carbonui.control.radioButton import RadioButton
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from carbonui.control.window import Window
from eve.client.script.ui.util.uix import GetOwnerLogo

def PresentChatInviteWindow(senderId):
    name = cfg.eveowners.Get(senderId).name
    wnd = ChatInviteWindow.Open(windowID='ChatInvitation_%s' % senderId, invitorID=senderId, invitorName=name)
    if wnd.OnScale_:
        wnd.OnScale_(wnd)
    stack = uicore.registry.GetStack('invitestack', wnd.GetStackClass(), useDefaultPos=True)
    if stack is not None:
        stack.InsertWnd(wnd, 0, 1, 1)
        stack.MakeUnResizeable()
    state = uiconst.UI_PICKCHILDREN
    if not wnd.stacked:
        state = uiconst.UI_NORMAL
    wnd.ShowDialog(modal=False, state=state)
    retval = wnd.result
    if retval:
        if retval == 'accept':
            return (True, retval)
        if retval == 'acceptadd':
            uthread2.start_tasklet(sm.GetService('addressbook').AddToPersonal, senderId, 'contact')
            return (True, retval)
        if retval == 'block':
            uthread2.start_tasklet(sm.GetService('addressbook').BlockOwner, senderId)
            return (False, retval)
    return (False, retval)


class ChatInviteWindow(Window):
    default_minSize = (350, 300)

    def ApplyAttributes(self, attributes):
        super(ChatInviteWindow, self).ApplyAttributes(attributes)
        self.invitorID = attributes.invitorID
        self.invitorName = attributes.invitorName
        self.result = None
        self.SetCaption(localization.GetByLabel('UI/Chat/ChatInvite'))
        self.MakeUnResizeable()
        self.ConstructLayout()

    def ConstructLayout(self):
        invitorCont = Container(name='topCont', parent=self.sr.main, align=uiconst.TOTOP, pos=(0, 0, 0, 64))
        invitorImgCont = Container(name='imgCont', parent=invitorCont, align=uiconst.TOLEFT, pos=(0, 0, 64, 0), padding=(0,
         0,
         uiconst.defaultPadding,
         0))
        invitorNameCont = Container(name='invitorNameCont', parent=invitorCont, align=uiconst.TOALL, padding=(uiconst.defaultPadding,
         0,
         0,
         0))
        label = localization.GetByLabel('UI/Chat/InvitedToConversation', inviter=self.invitorID)
        GetOwnerLogo(invitorImgCont, self.invitorID, size=64, noServerCall=True)
        EveLabelMedium(text=label, parent=invitorNameCont, align=uiconst.CENTERLEFT, width=240, state=uiconst.UI_NORMAL, idx=0)
        controlsCont = Container(name='controlsCont', parent=self.sr.main, align=uiconst.TOTOP, height=154, padding=(0, 8, 0, 0))
        self.buttons = []
        cb1 = RadioButton(text=localization.GetByLabel('UI/Chat/AcceptInvitation'), parent=controlsCont, retval='accept', checked=1, groupname='chatInvite', align=uiconst.TOTOP)
        self.buttons.append(cb1)
        cb2 = RadioButton(text=localization.GetByLabel('UI/Chat/AcceptInvitationAndAddContact'), parent=controlsCont, retval='acceptadd', checked=0, groupname='chatInvite', align=uiconst.TOTOP)
        self.buttons.append(cb2)
        cb3 = RadioButton(text=localization.GetByLabel('UI/Chat/RejectInvitation'), parent=controlsCont, retval='reject', checked=0, groupname='chatInvite', align=uiconst.TOTOP)
        self.buttons.append(cb3)
        cb4 = RadioButton(text=localization.GetByLabel('UI/Chat/RejectInvitationAndBlock'), parent=controlsCont, retval='block', checked=0, groupname='chatInvite', align=uiconst.TOTOP)
        self.buttons.append(cb4)
        self.btnGroup = ButtonGroup(btns=[[localization.GetByLabel('UI/Generic/OK'),
          self.Confirm,
          (),
          81,
          1,
          1,
          0]], parent=self.sr.main, idx=0)

    def Confirm(self, *args):
        self.result = self.buttons[0].GetGroupValue()
        self.SetModalResult(1)
