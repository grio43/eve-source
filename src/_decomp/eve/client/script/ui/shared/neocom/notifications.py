#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\notifications.py
import eveformat
import utillib
from carbon.common.script.sys.serviceConst import ROLE_GML
from carbon.common.script.util import timerstuff
from carbon.common.script.util.commonutils import StripTags
from carbon.common.script.util.format import FmtDate
from carbonui.control.dragResizeCont import DragResizeCont
from carbonui.primitives.container import Container
from carbonui.util.various_unsorted import SortListOfTuples
from eve.client.script.ui.control import eveScroll
from carbonui.button.group import ButtonGroup
from eve.client.script.ui.control.divider import Divider
import blue
import eve.common.script.util.notificationconst as notificationConst
import uthread
import carbonui.const as uiconst
import eve.common.script.util.notificationUtil as notificationUtil
import localization
from carbonui.uicore import uicore
from eve.client.script.ui.control.entries.space import Space
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from eve.client.script.ui.control.listgroup import ListGroup
from eve.client.script.ui.shared.neocom.evemail import MailEntry
from menu import MenuLabel
from globalConfig.getFunctions import IsPlayerBountyHidden
HINTCUTOFF = 100
DELETE_INTERVAL = 0.3 * const.SEC

class NotificationForm(Container):
    __guid__ = 'form.NotificationForm'
    __notifyevents__ = ['OnNotificationsRefresh', 'OnNewNotificationReceived', 'OnNotificationReadOutside']

    def Setup(self):
        sm.RegisterNotify(self)
        self.scrollHeight = 0
        self.DrawStuff()
        self.readTimer = 0
        self.viewing = None
        self.lastDeleted = 0

    def DrawStuff(self, *args):
        btns = ButtonGroup(btns=[[localization.GetByLabel('UI/Mail/Notifications/MarkAllAsRead'),
          self.MarkAllRead,
          None,
          81], [localization.GetByLabel('UI/Mail/Notifications/DeleteAll'),
          self.DeleteAll,
          None,
          81]], parent=self, idx=0)
        leftContWidth = settings.user.ui.Get('notifications_leftContWidth', 200)
        self.sr.leftCont = Container(name='leftCont', parent=self, align=uiconst.TOLEFT, width=leftContWidth)
        self.sr.leftScroll = eveScroll.Scroll(name='leftScroll', parent=self.sr.leftCont)
        self.sr.leftScroll.multiSelect = 0
        divider = Divider(name='divider', align=uiconst.TOLEFT, width=const.defaultPadding, parent=self, state=uiconst.UI_NORMAL)
        divider.Startup(self.sr.leftCont, 'width', 'x', 180, 250)
        self.sr.rightCont = Container(name='rightCont', parent=self, align=uiconst.TOALL, pos=(0,
         0,
         const.defaultPadding,
         const.defaultPadding))
        dividerCont = DragResizeCont(name='dividerCont', settingsID='notificationsSplitSize', parent=self.sr.rightCont, align=uiconst.TOTOP_PROP, minSize=0.1, maxSize=0.9, defaultSize=0.7, clipChildren=True)
        self.sr.readingPaneCont = Container(name='readingPaneCont', parent=self.sr.rightCont, align=uiconst.TOALL)
        self.sr.readingPane = EditPlainText(setvalue='', parent=self.sr.readingPaneCont, align=uiconst.TOALL, readonly=1)
        self.sr.msgCont = Container(name='msgCont', parent=dividerCont)
        self.sr.msgScroll = eveScroll.Scroll(name='msgScroll', parent=self.sr.msgCont)
        self.sr.msgScroll.sr.id = 'notifications_msgs'
        self.sr.msgScroll.sr.fixedColumns = {localization.GetByLabel('UI/Mail/Status'): 52}
        self.sr.msgScroll.OnSelectionChange = self.MsgScrollSelectionChange
        self.sr.msgScroll.OnDelete = self.DeleteFromKeyboard
        self.inited = True

    def LoadNotificationForm(self, *args):
        self.LoadLeftSide()

    def OnClose_(self, *args):
        settings.user.ui.Set('notifications_leftContWidth', self.sr.leftCont.width)
        settings.user.ui.Set('notifications_readingContHeight', self.sr.readingPaneCont.height)
        sm.GetService('mailSvc').SaveChangesToDisk()
        sm.UnregisterNotify(self)

    def SelectGroupById(self, groupID):
        for entry in self.sr.leftScroll.GetNodes():
            if entry.groupID == groupID:
                panel = entry.panel
                if panel is not None:
                    self.UpdateCounters()
                    panel.OnClick()

    def LoadLeftSide(self):
        scrolllist = self.GetStaticLabelsGroups()
        self.sr.leftScroll.Load(contentList=scrolllist)
        lastViewedID = settings.char.ui.Get('mail_lastnotification', None)
        for entry in self.sr.leftScroll.GetNodes():
            if entry.groupID is None:
                continue
            if entry.groupID == lastViewedID:
                panel = entry.panel
                if panel is not None:
                    self.UpdateCounters()
                    panel.OnClick()
                    return

        self.UpdateCounters()
        if len(self.sr.leftScroll.GetNodes()) > 0:
            entry = self.sr.leftScroll.GetNodes()[0]
            panel = entry.panel
            if panel is not None:
                panel.OnClick()

    def GetStaticLabelsGroups(self):
        scrolllist = []
        lastViewedID = settings.char.ui.Get('mail_lastnotification', None)
        for groupID, labelPath in notificationUtil.groupNamePaths.iteritems():
            if groupID == notificationUtil.groupBounties and IsPlayerBountyHidden(sm.GetService('machoNet')):
                continue
            label = localization.GetByLabel(labelPath)
            entry = self.GetGroupEntry(groupID, label, groupID == lastViewedID)
            strippedLabel = StripTags(label, stripOnly=['localized'])
            scrolllist.append((strippedLabel.lower(), entry))

        scrolllist = SortListOfTuples(scrolllist)
        entry = self.GetGroupEntry(const.notificationGroupUnread, localization.GetByLabel('UI/Mail/Unread'), const.notificationGroupUnread == lastViewedID)
        scrolllist.insert(0, entry)
        scrolllist.insert(1, GetFromClass(Space, {'height': 12}))
        return scrolllist

    def GetGroupEntry(self, groupID, label, selected = 0):
        return GetFromClass(ListGroup, {'GetSubContent': self.GetLeftGroups,
         'label': label,
         'id': ('notification', id),
         'state': 'locked',
         'BlockOpenWindow': 1,
         'disableToggle': 1,
         'expandable': 0,
         'showicon': 'hide',
         'showlen': 0,
         'groupItems': [],
         'hideNoItem': 1,
         'hideExpander': 1,
         'hideExpanderLine': 1,
         'selectGroup': 1,
         'isSelected': selected,
         'groupID': groupID,
         'OnClick': self.LoadGroupFromEntry,
         'MenuFunction': self.StaticMenu})

    def GetLeftGroups(self, *args):
        return []

    def LoadGroupFromEntry(self, entry, *args):
        group = entry.sr.node
        self.LoadGroupFromNode(group)

    def LoadGroupFromNode(self, node, refreshing = 0, selectedIDs = [], *args):
        group = node
        settings.char.ui.Set('mail_lastnotification', group.groupID)
        notifications = []
        if group.groupID == const.notificationGroupUnread:
            notifications = sm.GetService('notificationSvc').GetFormattedUnreadNotifications()
            senders = [ value.senderID for value in sm.GetService('notificationSvc').GetUnreadNotifications() ]
        else:
            notifications = sm.GetService('notificationSvc').GetFormattedNotifications(group.groupID)
            senders = [ value.senderID for value in sm.GetService('notificationSvc').GetNotificationsByGroupID(group.groupID) ]
        sm.GetService('mailSvc').PrimeOwners(senders)
        if not self or self.destroyed:
            return
        pos = self.sr.msgScroll.GetScrollProportion()
        scrolllist = []
        for each in notifications:
            senderName = ''
            if each.senderID == -1:
                senderName = cfg.eveowners.Get(const.ownerSystem).ownerName
            elif each.senderID is not None:
                senderName = cfg.eveowners.Get(each.senderID).ownerName
            label = '<t>' + senderName + '<t>' + each.subject + '<t>' + FmtDate(each.created, 'ls')
            if group.groupID == const.notificationGroupUnread:
                typeGroup = notificationConst.GetTypeGroup(each.typeID)
                labelPath = notificationUtil.groupNamePaths.get(typeGroup, None)
                if labelPath is None:
                    typeName = ''
                else:
                    typeName = localization.GetByLabel(labelPath)
                label += '<t>' + typeName
            hint = eveformat.truncate_text_ignoring_tags(string=each.body.replace('<br>', ' '), length=HINTCUTOFF, trail=localization.GetByLabel('UI/Common/MoreTrail'))
            scrolllist.append(GetFromClass(MailEntry, {'cleanLabel': label,
             'parentNode': node,
             'label': label,
             'hint': hint.strip(),
             'id': each.notificationID,
             'typeID': each.typeID,
             'senderID': each.senderID,
             'data': utillib.KeyVal(read=each.processed),
             'info': each,
             'OnClick': self.LoadReadingPaneFromEntry,
             'OnDblClick': self.DblClickNotificationEntry,
             'GetMenu': self.GetEntryMenu,
             'ignoreRightClick': 1,
             'isSelected': each.notificationID in selectedIDs,
             'Draggable_blockDrag': 1,
             'isNotification': True}))

        scrollHeaders = [localization.GetByLabel('UI/Mail/Status'),
         localization.GetByLabel('UI/Mail/Sender'),
         localization.GetByLabel('UI/Mail/Subject'),
         localization.GetByLabel('UI/Mail/Received')]
        if group.groupID == const.notificationGroupUnread:
            scrollHeaders.append(localization.GetByLabel('UI/Mail/Notifications/GroupName'))
        if not self or self.destroyed:
            return
        self.sr.msgScroll.Load(contentList=scrolllist, headers=scrollHeaders, noContentHint=localization.GetByLabel('UI/Mail/Notifications/NoNotifications'))
        if not refreshing:
            self.ClearReadingPane()
        else:
            self.sr.msgScroll.ScrollToProportion(pos)
        self.UpdateCounters()

    def StaticMenu(self, node, *args):
        m = []
        if node.groupID != const.notificationGroupUnread:
            m.append((MenuLabel('UI/Mail/Notifications/MarkAllAsRead'), self.MarkAllReadInGroup, (node.groupID,)))
            m.append(None)
            m.append((MenuLabel('UI/Mail/Notifications/DeleteAll'), self.DeleteAllFromGroup, (node.groupID,)))
        return m

    def DeleteAll(self, *args):
        if eve.Message('EvemailNotificationsDeleteAll', {}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
            sm.GetService('notificationSvc').DeleteAll()

    def MarkAllRead(self, *args):
        if eve.Message('EvemailNotificationsMarkAllRead', {}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
            sm.GetService('notificationSvc').MarkAllRead()

    def DeleteAllFromGroup(self, groupID, *args):
        if eve.Message('EvemailNotificationsDeleteGroup', {}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
            sm.GetService('notificationSvc').DeleteAllFromGroup(groupID)

    def MarkAllReadInGroup(self, groupID, *args):
        sm.GetService('notificationSvc').MarkAllReadInGroup(groupID)

    def GetEntryMenu(self, entry, *args):
        m = []
        sel = self.sr.msgScroll.GetSelected()
        selIDs = [ x.id for x in sel ]
        msgID = entry.sr.node.id
        if msgID not in selIDs:
            selIDs = [msgID]
            sel = [entry.sr.node]
        unread = {}
        for each in sel:
            if not each.data.read:
                unread[each.id] = each

        if len(unread) > 0:
            m.append((MenuLabel('UI/Mail/Notifications/MarkAsRead'), self.MarkAsRead, (unread.values(), unread.keys())))
        m.append(None)
        if len(selIDs) > 0:
            m.append((MenuLabel('UI/Mail/Notifications/Delete'), self.DeleteNotifications, (sel, selIDs)))
        if session.role & ROLE_GML:
            m.append(('GM: MessageID=%s' % msgID, blue.pyos.SetClipboardData, (str(msgID),)))
        return m

    def MarkAsRead(self, notifications, notificationIDs, *args):
        sm.GetService('notificationSvc').MarkAsRead(notificationIDs)
        self.UpdateCounters()
        self.SetMsgEntriesAsRead(notifications)

    def DblClickNotificationEntry(self, entry):
        messageID = entry.sr.node.id
        info = entry.sr.node.info
        sm.GetService('notificationSvc').OpenNotificationReadingWnd(info)

    def LoadReadingPaneFromEntry(self, entry):
        uthread.new(self.LoadReadingPaneFromNode, entry.sr.node)

    def LoadReadingPaneFromNode(self, node):
        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        if not shift:
            self.LoadReadingPane(node)

    def LoadReadingPane(self, node):
        self.readTimer = 0
        info = node.info
        txt = sm.GetService('notificationSvc').GetReadingText(node.senderID, info.subject, info.created, info.body)
        self.sr.readingPane.SetText(txt)
        self.viewing = node.id
        if not node.data.read:
            self.MarkAsRead([node], [node.id])

    def ClearReadingPane(self):
        self.sr.readingPane.SetText('')
        self.viewing = None

    def SetMsgEntriesAsRead(self, nodes):
        for node in nodes:
            self.TryReloadNode(node)

    def TryReloadNode(self, node):
        node.data.read = 1
        panel = node.Get('panel', None)
        if panel is None:
            return
        panel.LoadMailEntry(node)

    def MsgScrollSelectionChange(self, sel = [], *args):
        if len(sel) == 0:
            return
        node = sel[0]
        if self.viewing != node.id:
            self.readTimer = timerstuff.AutoTimer(1000, self.LoadReadingPane, node)

    def DeleteFromKeyboard(self, *args):
        if blue.os.GetWallclockTime() - self.lastDeleted < DELETE_INTERVAL:
            eve.Message('uiwarning03')
            return
        sel = self.sr.msgScroll.GetSelected()
        ids = [ each.id for each in sel ]
        self.DeleteNotifications(sel, ids)
        self.lastDeleted = blue.os.GetWallclockTime()

    def DeleteNotifications(self, notificationEntries, ids):
        if len(notificationEntries) < 1:
            return
        idx = notificationEntries[0].idx
        ids = []
        for entry in notificationEntries:
            ids.append(entry.id)

        sm.GetService('notificationSvc').DeleteNotifications(ids)
        sm.ScatterEvent('OnMessageChanged', const.mailTypeNotifications, ids, 'deleted')
        self.sr.msgScroll.RemoveEntries(notificationEntries)
        if self.viewing in ids:
            self.ClearReadingPane()
        self.UpdateCounters()
        if len(self.sr.msgScroll.GetNodes()) < 1:
            self.sr.msgScroll.Load(contentList=[], headers=[], noContentHint=localization.GetByLabel('UI/Mail/Notifications/NoNotifications'))
            return
        numChildren = len(self.sr.msgScroll.GetNodes())
        newIdx = min(idx, numChildren - 1)
        newSelectedNode = self.sr.msgScroll.GetNode(newIdx)
        if newSelectedNode is not None:
            self.sr.msgScroll.SelectNode(newSelectedNode)

    def SelectNodeByNotificationID(self, notificationID):
        nodes = self.sr.msgScroll.GetNodes()
        for node in nodes:
            if node.id == notificationID:
                self.sr.msgScroll.SelectNode(node)
                break

    def OnNotificationsRefresh(self):
        self.LoadLeftSide()

    def OnNewNotificationReceived(self, *args):
        self.UpdateCounters()

    def OnNotificationReadOutside(self, notificationID):
        self.UpdateCounters()
        for node in self.sr.msgScroll.GetNodes():
            if node.id == notificationID:
                self.SetMsgEntriesAsRead([node])
                return

    def UpdateCounters(self):
        unreadCounts = sm.GetService('notificationSvc').GetAllUnreadCount()
        for each in self.sr.leftScroll.GetNodes():
            if each.groupID is None:
                continue
            count = unreadCounts.get(each.groupID, 0)
            self.TryChangePanelLabel(each, count)

    def TryChangePanelLabel(self, node, count):
        panel = node.Get('panel', None)
        if panel is None:
            return
        panelLabel = self.GetPanelLabel(node.cleanLabel, count)
        panel.sr.label.text = panelLabel

    def GetPanelLabel(self, label, count):
        if count > 0:
            return localization.GetByLabel('UI/Mail/Notifications/GroupUnreadLabel', groupName=label, unreadCount=count)
        else:
            return label
