#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\Alliances\all_ui_members.py
import localization
import log
from carbon.common.script.util.format import FmtDate
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.uicore import uicore
from carbonui.button.group import ButtonGroup
from carbonui.control.button import Button
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control import eveIcon, eveLabel, eveScroll
from eve.client.script.ui.shared.neocom.corporation import corpUISignals
from eve.client.script.ui.util import uix
from eveservices.menu import GetMenuService

class FormAlliancesMembers(Container):
    is_loaded = False

    def Load(self, *args):
        if self.is_loaded:
            return
        self.is_loaded = True
        logoLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Members/Logo')
        nameLabel = localization.GetByLabel('UI/Common/Name')
        chosenExecLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Members/ChosenExecutor')
        joinedLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Tracking/JoinedColumnHeader')
        self.sr.headers = [logoLabel,
         nameLabel,
         chosenExecLabel,
         joinedLabel]
        if eve.session.allianceid is not None:
            if eve.session.corprole & const.corpRoleDirector == const.corpRoleDirector:
                buttonGroup = ButtonGroup(parent=self)
                buttonGroup.AddButton(localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Members/DeclareSupport'), self.DeclareSupportForm)
            else:
                hintLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Members/DirectorDeclareWarHint')
                eveLabel.EveLabelMedium(text=hintLabel, parent=self, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        self.sr.scroll = eveScroll.Scroll(parent=self)
        self.sr.scroll.sr.id = 'FormAlliancesMembersScroll'
        if eve.session.allianceid is None:
            notInAllianceLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/CorpNotInAlliance', corpName=cfg.eveowners.Get(eve.session.corpid).ownerName)
            self.sr.scroll.Load(fixedEntryHeight=19, contentList=[], noContentHint=notInAllianceLabel)
            return
        self.ShowMembers()
        corpUISignals.on_alliance_member_changed.connect(self.OnAllianceMemberChanged)

    def SetHint(self, hintstr = None):
        if self.sr.scroll:
            self.sr.scroll.ShowHint(hintstr)

    def ShowMembers(self):
        log.LogInfo('ShowMembers')
        try:
            sm.GetService('corpui').ShowLoad()
            scrolllist = []
            headers = []
            hint = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Members/NoMembersFound')
            if self is None or self.destroyed:
                log.LogInfo('ShowAllianceApplications Destroyed or None')
                hint = '\xef\xbf\xbd\xef\xbf\xbd s\xef\xbf\xbdst mig ekki.'
            elif eve.session.allianceid is None:
                hint = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Members/CorporationNotInAllianceATM', corpName=cfg.eveowners.Get(eve.session.corpid).ownerName)
            else:
                members = sm.GetService('alliance').GetMembers()
                log.LogInfo('ShowMembers len(members):', len(members))
                owners = set()
                for member in members.itervalues():
                    owners.add(member.corporationID)

                if len(owners):
                    cfg.eveowners.Prime(owners)
                    cfg.corptickernames.Prime(owners)
                for member in members.itervalues():
                    self.__AddToList(member, scrolllist)

            self.sr.scroll.adjustableColumns = 1
            self.sr.scroll.Load(contentList=scrolllist, headers=self.sr.headers, noContentHint=hint)
        finally:
            sm.GetService('corpui').HideLoad()

    def __AddToList(self, member, scrolllist):
        scrolllist.append(GetFromClass(Corporation, {'label': self.__GetLabel(member.corporationID),
         'charIndex': cfg.eveowners.Get(member.corporationID).name,
         'member': member,
         'GetMenu': self.GetMemberMenu,
         'corporationID': member.corporationID}))

    def GetMemberMenu(self, entry):
        corpID = entry.sr.node.corporationID
        res = GetMenuService().GetMenuFromItemIDTypeID(corpID, const.typeCorporation)
        if eve.session.corpid == corpID:
            quitAllianceLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Members/QuitAlliance')
            res.append([quitAllianceLabel, [[quitAllianceLabel, self.DeleteMember, [corpID]]]])
        else:
            kickMemberLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Members/KickMember')
            res.append([kickMemberLabel, [[kickMemberLabel, self.DeleteMember, [corpID]]]])
        declareSupportLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Members/DeclareSupport')
        res.append([declareSupportLabel, [[declareSupportLabel, self.DeclareSupport, [corpID]]]])
        return res

    def __GetLabel(self, corporationID):
        member = sm.GetService('alliance').GetMembers()[corporationID]
        corpName = cfg.eveowners.Get(corporationID).ownerName
        chosenExecutor = member.chosenExecutorID
        if member.chosenExecutorID is None:
            chosenExecutor = localization.GetByLabel('UI/Common/Secret')
        else:
            chosenExecutor = cfg.eveowners.Get(member.chosenExecutorID).ownerName
        joinedDate = FmtDate(member.startDate)
        return '<t>%s<t>%s<t>%s' % (corpName, chosenExecutor, joinedDate)

    def GetEntry(self, allianceID, corporationID):
        for entry in self.sr.scroll.GetNodes():
            if entry is None or entry is None:
                continue
            if entry.panel is None or entry.panel.destroyed:
                continue
            if entry.member.allianceID == allianceID and entry.member.corporationID == corporationID:
                return entry

    def OnAllianceMemberChanged(self, allianceID, corporationID, change):
        log.LogInfo('OnAllianceMemberChanged allianceID', allianceID, 'corporationID', corporationID, 'change', change)
        if eve.session.allianceid != allianceID:
            return
        if self.state not in (uiconst.UI_NORMAL, uiconst.UI_PICKCHILDREN):
            log.LogInfo('OnAllianceMemberChanged state != UI_NORMAL', self.state)
            return
        if self.sr.scroll is None:
            log.LogInfo('OnAllianceMemberChanged no scroll')
            return
        bAdd = 1
        bRemove = 1
        for old, new in change.itervalues():
            if old is not None:
                bAdd = 0
            if new is not None:
                bRemove = 0

        if bAdd and bRemove:
            raise RuntimeError('members::OnAllianceMemberChanged WTF')
        if bAdd:
            log.LogInfo('OnAllianceMemberChanged adding member')
            member = sm.GetService('alliance').GetMembers()[corporationID]
            self.SetHint()
            scrolllist = []
            self.__AddToList(member, scrolllist)
            if len(self.sr.scroll.sr.headers) > 0:
                self.sr.scroll.AddEntries(-1, scrolllist)
            else:
                self.sr.scroll.Load(contentList=scrolllist, headers=self.sr.headers)
        elif bRemove:
            log.LogInfo('OnAllianceMemberChanged removing member')
            entry = self.GetEntry(allianceID, corporationID)
            if entry is not None:
                self.sr.scroll.RemoveEntries([entry])
            else:
                log.LogWarn('OnAllianceMemberChanged member not found')
        else:
            log.LogInfo('OnAllianceMemberChanged updating member')
            entry = self.GetEntry(allianceID, corporationID)
            if entry is None:
                log.LogWarn('OnAllianceMemberChanged member not found')
            if entry is not None:
                label = self.__GetLabel(corporationID)
                entry.panel.sr.node.label = label
                entry.panel.sr.label.text = label

    def DeclareSupportForm(self, *args):
        format = []
        stati = {}
        pledgeLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Members/PledgeSupportTo')
        format.append({'type': 'header',
         'text': pledgeLabel,
         'frame': 0})
        format.append({'type': 'push'})
        format.append({'type': 'btline'})
        members = sm.GetService('alliance').GetMembers()
        myCorp = members[eve.session.corpid]
        for member in members.itervalues():
            text = cfg.eveowners.Get(member.corporationID).ownerName
            format.append({'type': 'checkbox',
             'setvalue': member.corporationID == myCorp.chosenExecutorID,
             'key': member.corporationID,
             'text': text,
             'frame': 0,
             'group': 'members'})

        format.append({'type': 'btline'})
        left = uicore.desktop.width / 2 - 500 / 2
        top = uicore.desktop.height / 2 - 400 / 2
        declareLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Members/DeclarationExecutorSupport')
        retval = uix.HybridWnd(format, declareLabel, 'declareSupport', 1, uiconst.OKCANCEL, [left, top], 500)
        if retval is not None:
            corpID = retval['members']
            sm.GetService('alliance').DeclareExecutorSupport(corpID)

    def DeleteMember(self, corpID):
        if corpID == eve.session.corpid:
            message = 'AllComfirmKickSelf'
        else:
            message = 'AllComfirmKickMember'
        res = eve.Message(message, {}, uiconst.YESNO)
        if res == uiconst.ID_YES:
            sm.GetService('alliance').DeleteMember(corpID)

    def DeclareSupport(self, corpID):
        sm.GetService('alliance').DeclareExecutorSupport(corpID)


class Corporation(Generic):
    __guid__ = 'listentry.Corporation'
    __params__ = ['corporationID', 'label']

    def Startup(self, *args):
        self.sr.label = eveLabel.EveLabelMedium(text='', parent=self, left=5, state=uiconst.UI_DISABLED, maxLines=1)
        self.sr.icon = Container(parent=self, width=24, height=24, left=2, top=1, align=uiconst.TOPLEFT)
        self.sr.events = ('OnClick', 'OnMouseDown', 'OnMouseUp', 'OnDblClick', 'OnMouseHover')
        for eventName in self.sr.events:
            setattr(self.sr, eventName, None)

    def Load(self, node):
        self.sr.node = node
        data = node
        self.corporationID = data.corporationID
        self.confirmOnDblClick = data.Get('confirmOnDblClick', 0)
        self.sr.label.text = data.label
        self.hint = data.Get('hint', '')
        self.sr.icon.state = uiconst.UI_NORMAL
        self.sr.icon.Flush()
        eveIcon.GetLogoIcon(itemID=data.corporationID, parent=self.sr.icon, acceptNone=False, align=uiconst.TOALL)
        for eventName in self.sr.events:
            if data.Get(eventName, None):
                self.sr.Set(eventName, data.Get(eventName, None))

        if node.Get('selected', 0):
            self.Select()
        else:
            self.Deselect()
        self.sr.label.top = int((self.height - self.sr.label.textheight) / 2)
        if data.Get('button', None):
            caption, size, function, args = data.button
            if self.sr.Get('button%s' % size, None) is None:
                btn = self.sr.Get('button%s' % size, Button(parent=self, label=caption, func=function, align=uiconst.TOPRIGHT))
                btn.top = (node.height - btn.height) / 2 - 3
                setattr(self.sr, 'button%s' % size, btn)
            btn = self.sr.Get('button%s' % size, None)
            btn.text = '<center>%s' % caption
            btn.OnClick = (function, args)
            btn.state = uiconst.UI_NORMAL
            btn.left = -size + 6
        else:
            for size in [51, 66, 81]:
                if self.sr.Get('button%s' % size, None):
                    self.sr.Get('button%s' % size, None).state = uiconst.UI_HIDDEN

    def GetHeight(self, *args):
        node, width = args
        node.height = 27
        return node.height

    def ShowInfo(self, *args):
        sm.GetService('info').ShowInfo(const.typeCorporation, self.sr.node.corporationID)

    def OnDblClick(self, *args):
        self.ShowInfo()
