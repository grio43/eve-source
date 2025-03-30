#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\entries\user.py
from carbonui import uiconst
from carbonui.util.various_unsorted import GetAttrs
from eve.client.script.ui.control import eveIcon
from eve.client.script.ui.shared.userentry import User

class SearchedUser(User):
    __guid__ = 'listentry.SearchedUser'
    __notifyevents__ = ['OnContactLoggedOn',
     'OnContactLoggedOff',
     'OnClientContactChange',
     'OnPortraitCreated',
     'OnContactNoLongerContact',
     'OnStateSetupChange',
     'ProcessSessionChange',
     'OnFleetJoin',
     'OnFleetLeave',
     'ProcessOnUIAllianceRelationshipChanged',
     'OnContactChange',
     'OnBlockContacts',
     'OnUnblockContacts']

    def Startup(self, *args):
        self.pictureLeft = 14
        self.labelLeft = 52
        User.Startup(self, *args)
        self.sr.picture.left = self.pictureLeft
        self.sr.namelabel.left = self.labelLeft

    def PreLoad(node):
        User.PreLoad(node)
        node.isAdded = False
        node.extraIcon = None
        node.hint = ''
        if node.Get('extraInfo', None) is not None:
            extraIconHintFlag = getattr(node.extraInfo, 'extraIconHintFlag', None)
            if extraIconHintFlag:
                extraIcon, hint, isAdded = extraIconHintFlag
                node.isAdded = isAdded
                node.extraIcon = extraIcon
                node.hint = ''

    def Load(self, node, *args):
        User.Load(self, node, *args)
        self.sr.picture.left = self.pictureLeft
        self.sr.namelabel.left = self.labelLeft
        self.extraInfo = self.sr.node.Get('extraInfo', None)
        self.configname = GetAttrs(self, 'extraInfo', 'wndConfigname')
        self.extraIconHintFlag = None
        if self.extraInfo is not None:
            if node.extraIcon:
                self.sr.extraIconCont.Flush()
                icon = eveIcon.Icon(parent=self.sr.extraIconCont, icon=node.extraIcon, pos=(0, 0, 0, 0), hint=node.hint)
                self.sr.extraIconCont.SetAlign(uiconst.CENTERLEFT)
        self.SearcedUserAddedOrRemoved(node.isAdded)

    def SearcedUserAddedOrRemoved(self, wasAdded = 0):
        if wasAdded:
            self.sr.extraIconCont.state = uiconst.UI_PICKCHILDREN
        else:
            self.sr.extraIconCont.state = uiconst.UI_HIDDEN
