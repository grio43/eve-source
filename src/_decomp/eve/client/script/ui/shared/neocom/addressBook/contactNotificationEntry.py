#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\addressBook\contactNotificationEntry.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui.control import eveIcon, eveLabel
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.util.uix import GetTextHeight
from menu import MenuLabel

class ContactNotificationEntry(Generic):
    __guid__ = 'listentry.ContactNotificationEntry'
    isDragObject = True

    def Startup(self, *args):
        Generic.Startup(self, args)
        picCont = Container(name='picture', parent=self, align=uiconst.TOLEFT, width=32)
        textCont = Container(name='textCont', parent=self, align=uiconst.TOALL, padLeft=2)
        self.sr.picture = Container(name='picture', parent=picCont, align=uiconst.TOPLEFT, pos=(0, 0, 32, 32))
        self.sr.label = eveLabel.EveLabelMedium(text='', parent=textCont, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        self.sr.messageLabel = eveLabel.EveLabelMedium(text='', parent=textCont, align=uiconst.TOTOP, state=uiconst.UI_DISABLED, left=5)

    def Load(self, node):
        self.sr.node = node
        self.notificationID = node.id
        self.senderID = node.senderID
        Generic.Load(self, node)
        self.sr.messageLabel.text = node.label2
        self.LoadContactEntry(node)
        self.hint = node.hint

    def LoadContactEntry(self, node):
        eveIcon.GetOwnerLogo(self.sr.picture, node.senderID, size=32, noServerCall=True)

    def GetDragData(self, *args):
        return self.sr.node.scroll.GetSelectedNodes(self.sr.node)

    def OnDropData(self, dragObj, nodes):
        pass

    def GetHeight(self, node, width):
        node.height = 2 * GetTextHeight(node.label) + 2
        return node.height

    def GetMenu(self, *args):
        addressBookSvc = sm.GetService('addressbook')
        isContact = addressBookSvc.IsInAddressBook(self.senderID, 'contact')
        isBlocked = addressBookSvc.IsBlocked(self.senderID)
        m = [(MenuLabel('UI/Commands/ShowInfo'), self.ShowInfo)]
        if isContact:
            m.append((MenuLabel('UI/PeopleAndPlaces/EditContact'), addressBookSvc.AddToPersonalMulti, (self.senderID, 'contact', True)))
            m.append((MenuLabel('UI/PeopleAndPlaces/RemoveContact'), addressBookSvc.DeleteEntryMulti, ([self.senderID], 'contact')))
        else:
            m.append((MenuLabel('UI/PeopleAndPlaces/AddContact'), addressBookSvc.AddToPersonalMulti, (self.senderID, 'contact')))
        if isBlocked:
            m.append((MenuLabel('UI/PeopleAndPlaces/UnblockContact'), addressBookSvc.UnblockOwner, ([self.senderID],)))
        else:
            m.append((MenuLabel('UI/PeopleAndPlaces/BlockContact'), addressBookSvc.BlockOwner, (self.senderID,)))
        m.append((MenuLabel('UI/PeopleAndPlaces/DeleteNotification'), self.DeleteNotifications))
        return m

    def DeleteNotifications(self):
        sm.GetService('notificationSvc').DeleteNotifications([self.notificationID])
        sm.ScatterEvent('OnMessageChanged', const.mailTypeNotifications, [self.notificationID], 'deleted')
        sm.ScatterEvent('OnNotificationsRefresh')

    def ShowInfo(self, *args):
        if self.destroyed:
            return
        sm.GetService('info').ShowInfo(cfg.eveowners.Get(self.senderID).typeID, self.senderID)
