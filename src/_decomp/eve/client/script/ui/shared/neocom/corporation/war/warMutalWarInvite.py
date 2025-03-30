#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\war\warMutalWarInvite.py
from carbon.common.script.util.format import FmtDate
from carbon.common.script.util.linkUtil import GetShowInfoLink
from carbonui import uiconst
from carbonui.control.checkbox import Checkbox
from carbonui.control.combo import Combo
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.util.sortUtil import SortListOfTuples
from carbonui.control.button import Button
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveIcon import GetLogoIcon
from eve.client.script.ui.control.eveLabel import EveLabelLarge
from eve.client.script.ui.control.eveScroll import Scroll
from eve.common.lib import appConst as const
from localization import GetByLabel
from menu import MenuLabel
from utillib import KeyVal
OWNER_LOGO_SIZE = 32
ALL_INVITES = 0
OUTGOING_INVITES = 1
INCOMING_INVITES = 2

class MutualWarInvites(Container):
    __notifyevents__ = ['OnMutualWarsUpdated']
    is_loaded = False

    def Load(self, *args):
        if not self.is_loaded:
            self.is_loaded = True
            self.ConstructLayout()
            sm.RegisterNotify(self)
        self.LoadScroll()

    def ConstructLayout(self):
        self.blockInvitesCb = Checkbox(parent=self, align=uiconst.TOTOP, text=GetByLabel('UI/Corporations/Wars/BlockMutualInvites'), padding=(const.defaultPadding,
         const.defaultPadding,
         0,
         0), checked=False, callback=self.OnBlockInvitesClicked)
        self.blockInvitesCb.hint = GetByLabel('UI/Corporations/Wars/BlockMutualInvitesHint')
        self.UpdateBlockedCheckbox()
        comboCont = Container(name='comboCont', parent=self, align=uiconst.TOTOP, height=20)
        combatValues = ((GetByLabel('UI/Corporations/Wars/ShowAllMutualWarInvites'), ALL_INVITES), (GetByLabel('UI/Corporations/Wars/ShowOutgoingMutualWarInvites'), OUTGOING_INVITES), (GetByLabel('UI/Corporations/Wars/ShowIncomingMutualWarInvites'), INCOMING_INVITES))
        comboPrefsKey = ('char', 'ui', 'mutualWarsFilter')
        inviteTypesSelected = settings.char.ui.Get('mutualWarsFilter', ALL_INVITES)
        self.inviteCombo = Combo(parent=comboCont, name='combatCombo', select=inviteTypesSelected, align=uiconst.TOPLEFT, callback=self.OnInviteTypeChanged, prefskey=comboPrefsKey, options=combatValues, idx=0, adjustWidth=True, pos=(const.defaultPadding,
         const.defaultPadding,
         0,
         0))
        comboCont.height = self.inviteCombo.height + 2 * const.defaultPadding
        self.scroll = Scroll(parent=self, padding=const.defaultPadding)

    def LoadScroll(self):
        allInvitesData = sm.GetService('mutualWarInvites').GetInvites()
        inviteTypesSelected = self.inviteCombo.GetValue()
        scrollList = []
        for eachWarInfo in allInvitesData:
            data = KeyVal(fromOwnerID=eachWarInfo.fromOwnerID, toOwnerID=eachWarInfo.toOwnerID, sentDate=eachWarInfo.sentDate)
            if inviteTypesSelected == OUTGOING_INVITES:
                if data.fromOwnerID not in (session.allianceid, session.corpid):
                    continue
            elif inviteTypesSelected == INCOMING_INVITES:
                if data.toOwnerID not in (session.allianceid, session.corpid):
                    continue
            if data.fromOwnerID in (session.allianceid, session.corpid):
                entry = GetFromClass(MutualWarInviteEntryMyView, data)
            else:
                entry = GetFromClass(MutualWarInviteEntryCorpView, data=data)
            scrollList.append((-data.sentDate, entry))

        scrollList = SortListOfTuples(scrollList)
        self.scroll.Load(contentList=scrollList, noContentHint=GetByLabel('UI/Corporations/Wars/NoMutualWarInvitesFound'))

    def OnInviteTypeChanged(self, combo, *args):
        combo.UpdateSettings()
        self.LoadScroll()

    def OnMutualWarsUpdated(self):
        self.LoadScroll()

    def OnBlockInvitesClicked(self, *args):
        blocked = self.blockInvitesCb.GetValue()
        try:
            sm.GetService('mutualWarInvites').SetInvitesBlocked(blocked)
        except:
            self.UpdateBlockedCheckbox()
            raise

    def UpdateBlockedCheckbox(self):
        blocked = sm.GetService('mutualWarInvites').IsCorpInvitesBlocked()
        self.blockInvitesCb.SetChecked(blocked, report=False)
        if session.corprole & const.corpRoleDirector != const.corpRoleDirector:
            self.blockInvitesCb.Disable()


class BaseMutualWarInviteEntry(SE_BaseClassCore):
    __guid__ = 'BaseMutualWarInviteEntry'
    __notifyevents__ = []
    ENTRYHEIGHT = 55

    def Startup(self, *args):
        self.entryContainer = Container(name='entryContainer', parent=self)
        logoParentContSize = OWNER_LOGO_SIZE * 3
        logoParentsCont = Container(name='logoParentsCont', parent=self, align=uiconst.CENTERLEFT, pos=(4,
         0,
         logoParentContSize,
         48))
        self.fromLogoParent = Container(name='fromLogoParent', parent=logoParentsCont, align=uiconst.CENTERLEFT, pos=(0,
         0,
         OWNER_LOGO_SIZE,
         OWNER_LOGO_SIZE))
        swords = Sprite(name='warIcon', parent=logoParentsCont, align=uiconst.CENTER, pos=(0, 0, 20, 20), ignoreSize=True, state=uiconst.UI_DISABLED, opacity=0.3, texturePath='res:/UI/Texture/WindowIcons/wars.png')
        self.toLogoParent = Container(name='toLogoParent', parent=logoParentsCont, align=uiconst.CENTERRIGHT, pos=(0,
         0,
         OWNER_LOGO_SIZE,
         OWNER_LOGO_SIZE))
        self.buttonCont = Container(name='buttonCont', parent=self, align=uiconst.TORIGHT)
        self.nameCont = Container(name='nameCont', parent=self, align=uiconst.TOALL, padLeft=logoParentsCont.width + 10)
        self.nameLabel = EveLabelLarge(parent=self.nameCont, name='nameLabel', state=uiconst.UI_NORMAL, align=uiconst.CENTERLEFT, autoFadeSides=32)

    def Load(self, node):
        fromOwnerID = node.fromOwnerID
        toOwnerID = node.toOwnerID
        self.fromLogoParent.Flush()
        self.toLogoParent.Flush()
        fromLogo = GetLogoIcon(name='fromLogo', itemID=fromOwnerID, parent=self.fromLogoParent, acceptNone=False, align=uiconst.CENTER, pos=(0,
         0,
         OWNER_LOGO_SIZE,
         OWNER_LOGO_SIZE), state=uiconst.UI_NORMAL, hint=cfg.eveowners.Get(fromOwnerID).name, ignoreSize=True)
        fromLogo.OnClick = self.ShowFromOwnerInfo
        toLogo = GetLogoIcon(name='toLogo', itemID=toOwnerID, parent=self.toLogoParent, acceptNone=False, align=uiconst.CENTER, pos=(0,
         0,
         OWNER_LOGO_SIZE,
         OWNER_LOGO_SIZE), state=uiconst.UI_NORMAL, hint=cfg.eveowners.Get(toOwnerID).name, ignoreSize=True)
        toLogo.OnClick = self.ShowToOwnerInfo
        text = self.GetEntryText()
        text += '<br>%s' % GetByLabel('UI/Corporations/Wars/MutualInviteSentAt', timestamp=FmtDate(node.sentDate))
        self.nameLabel.text = text

    def GetEntryText(self):
        return ''

    def GetMenu(self):
        menu = [(MenuLabel('UI/Commands/ShowInfo'), self.ShowOwnerInfo)]
        return menu

    def ShowOwnerInfo(self):
        pass

    def ShowFromOwnerInfo(self):
        ownerID = self.sr.node.fromOwnerID
        ownerInfo = cfg.eveowners.Get(ownerID)
        sm.GetService('info').ShowInfo(ownerInfo.typeID, ownerInfo.ownerID)

    def ShowToOwnerInfo(self):
        ownerID = self.sr.node.toOwnerID
        ownerInfo = cfg.eveowners.Get(ownerID)
        sm.GetService('info').ShowInfo(ownerInfo.typeID, ownerInfo.ownerID)


class MutualWarInviteEntryMyView(BaseMutualWarInviteEntry):

    def Load(self, node):
        BaseMutualWarInviteEntry.Load(self, node)
        btnContWidth = const.defaultPadding
        btnText = GetByLabel('UI/Corporations/Wars/WithdrawMutualWarInvite')
        withdrawBtn = Button(name='withdrawBtn', parent=self.buttonCont, label=btnText, align=uiconst.CENTERRIGHT, left=btnContWidth, func=self.WidthDrawOffer)
        btnContWidth += withdrawBtn.width + const.defaultPadding
        self.buttonCont.width = btnContWidth

    def GetEntryText(self):
        node = self.sr.node
        toOwnerID = node.toOwnerID
        toInfo = cfg.eveowners.Get(toOwnerID)
        toLink = GetShowInfoLink(toInfo.typeID, toInfo.name, toOwnerID)
        text = GetByLabel('UI/Corporations/Wars/InvitedToMutualWar', toLink=toLink)
        return text

    def WidthDrawOffer(self, *args):
        node = self.sr.node
        toOwnerID = node.toOwnerID
        sm.GetService('mutualWarInvites').WithdrawInvite(toOwnerID)

    def ShowOwnerInfo(self):
        return self.ShowFromOwnerInfo()


class MutualWarInviteEntryCorpView(BaseMutualWarInviteEntry):

    def Load(self, node):
        BaseMutualWarInviteEntry.Load(self, node)
        btnContWidth = const.defaultPadding
        acceptButton = Button(name='acceptButton', parent=self.buttonCont, label=GetByLabel('UI/Corporations/Wars/AcceptMutualWar'), align=uiconst.CENTERRIGHT, left=btnContWidth, func=self.AcceptWarInvite)
        btnContWidth += acceptButton.width + const.defaultPadding
        rejectButton = Button(name='rejectButton', parent=self.buttonCont, label=GetByLabel('UI/Corporations/Wars/RejectMutualWar'), align=uiconst.CENTERRIGHT, left=btnContWidth, func=self.RejectInvite)
        btnContWidth += rejectButton.width + const.defaultPadding
        self.buttonCont.width = btnContWidth

    def GetEntryText(self):
        node = self.sr.node
        fromOwnerID = node.fromOwnerID
        fromInfo = cfg.eveowners.Get(fromOwnerID)
        fromLink = GetShowInfoLink(fromInfo.typeID, fromInfo.name, fromOwnerID)
        text = GetByLabel('UI/Corporations/Wars/HaveBeenInvitedToMutualWar', fromLink=fromLink)
        return text

    def AcceptWarInvite(self, *args):
        node = self.sr.node
        fromOwnerID = node.fromOwnerID
        sm.GetService('mutualWarInvites').RespondToInvite(fromOwnerID, accepts=True)

    def RejectInvite(self, *args):
        node = self.sr.node
        fromOwnerID = node.fromOwnerID
        sm.GetService('mutualWarInvites').RespondToInvite(fromOwnerID, accepts=False)

    def ShowOwnerInfo(self):
        self.ShowToOwnerInfo()
