#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\corp_ui_member_view_simple.py
import uthread
from carbonui.control.combo import Combo
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control import eveScroll
from carbonui.control.button import Button
import carbonui.const as uiconst
import localization
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.shared.userentry import User
from localization import GetByLabel

class CorpMembersViewSimple(Container):
    __guid__ = 'form.CorpMembersViewSimple'
    __nonpersistvars__ = []

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.memberIDs = []
        self.viewPerPage = 10
        self.viewFrom = 0

    def CreateWindow(self):
        wndResultsBar = Container(name='results', parent=self, align=uiconst.TOTOP, height=Button.default_height)
        wndNavBtns = ContainerAutoSize(name='sidepar', parent=wndResultsBar, align=uiconst.TORIGHT)
        label = Container(name='text', parent=wndResultsBar, align=uiconst.TOLEFT, width=150, height=16)
        numbers = (10, 25, 50, 100, 500)
        optlist = [ (GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/SimpleView/MembersPerPage', num=num), num) for num in numbers ]
        countcombo = Combo(label='', parent=wndResultsBar, options=optlist, name='membersperpage', callback=self.OnComboChange, width=120)
        self.sr.MembersPerPage = countcombo
        self.backBtn = Button(parent=wndNavBtns, align=uiconst.TOLEFT, state=uiconst.UI_HIDDEN, texturePath='res:/UI/Texture/Icons/23_64_1.png', iconSize=24, hint=localization.GetByLabel('UI/Common/Previous'), func=lambda : self.Navigate(-1), args=())
        self.fwdBtn = Button(parent=wndNavBtns, align=uiconst.TOLEFT, state=uiconst.UI_HIDDEN, texturePath='res:/UI/Texture/Icons/23_64_2.png', iconSize=24, hint=localization.GetByLabel('UI/Common/ViewMore'), func=lambda : self.Navigate(1), args=())
        self.scroll = eveScroll.Scroll(parent=self, padTop=8)

    def PopulateView(self, memberIDs = None):
        if memberIDs is not None:
            self.memberIDs = memberIDs
        nFrom = self.viewFrom
        nTo = nFrom + self.viewPerPage
        scrolllist = []
        memberIDsToDisplay = []
        for memberID in self.memberIDs:
            memberIDsToDisplay.append(memberID)

        cfg.eveowners.Prime(memberIDsToDisplay)
        totalNum = len(memberIDsToDisplay)
        if totalNum is not None:
            self.ShowHideBrowse(totalNum)
        for charID in memberIDsToDisplay:
            scrolllist.append(GetFromClass(User, {'charID': charID}))

        scrolllist = scrolllist[nFrom:nTo]
        self.scroll.Load(None, scrolllist, noContentHint=GetByLabel('UI/Wallet/WalletWindow/SearchNoResults'))

    def OnComboChange(self, entry, header, value, *args):
        if entry.name == 'membersperpage':
            self.viewPerPage = value
            uthread.new(self.PopulateView)

    def Navigate(self, direction, *args):
        self.viewFrom = max(0, self.viewFrom + direction * self.viewPerPage)
        uthread.new(self.PopulateView)

    def ShowHideBrowse(self, totalNum):
        if self.viewFrom == 0:
            self.backBtn.state = uiconst.UI_HIDDEN
        else:
            self.backBtn.state = uiconst.UI_NORMAL
        if self.viewFrom + self.viewPerPage >= totalNum:
            self.fwdBtn.state = uiconst.UI_HIDDEN
        else:
            self.fwdBtn.state = uiconst.UI_NORMAL
