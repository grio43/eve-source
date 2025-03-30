#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\corp_ui_member_view_role_mgt.py
import blue
import eveformat
import uthread
import carbon.client.script.util.lg as lg
import log
import localization
from carbonui import uiconst
from carbonui.control.combo import Combo
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uicore import uicore
from eve.client.script.ui.control import eveScroll
from carbonui.button.group import ButtonGroup
from carbonui.control.button import Button
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.services.corporation.corp_util import VIEW_GRANTABLE_ROLES, VIEW_ROLES, VIEW_TITLES
from eve.client.script.ui.shared.neocom.corporation.corp_dlg_edit_member import EditMemberDialog
from eve.client.script.ui.shared.neocom.corporation.corp_ui_member_listentry import CorpMemberRoleEntry
from eve.client.script.ui.util import uix
from eve.common.script.sys.rowset import Rowset
from localization import GetByLabel

class CorpMembersViewRoleManagement(Container):
    __guid__ = 'form.CorpMembersViewRoleManagement'
    __nonpersistvars__ = []

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.sr.members = sm.GetService('corp').GetMembers()
        self.sr.viewType = 0
        self.sr.viewRoleGroupingID = 1
        self.sr.viewPerPage = 10
        self.sr.viewFrom = 0
        self.sr.roleGroupings = sm.GetService('corp').GetRoleGroupings()
        self.sr.progressCurrent = 0
        self.sr.progressTotal = 0
        self.sr.memberIDs = []
        self.sr.members.AddListener(self)
        self.sr.scroll = None
        self.sr.ignoreDirtyFlag = False

    def LogInfo(self, *args):
        lg.Info(self.__guid__, *args)

    def _OnClose(self, *args):
        self.OnTabDeselect()
        self.sr.members.RemoveListener(self)

    def OnTabDeselect(self):
        if not self.sr.ignoreDirtyFlag and self.IsDirty():
            if eve.Message('CrpMembersSaveChanges', {}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
                self.SaveChanges()
            else:
                self.sr.ignoreDirtyFlag = True

    def DataChanged(self, primaryKey, change):
        if not (self and not self.destroyed):
            return
        if self.sr.progressTotal == 0:
            self.sr.progressCurrent = 0
            self.sr.progressTotal = 1
        self.sr.progressCurrent += 1
        sm.GetService('loading').ProgressWnd(cfg.eveowners.Get(primaryKey).ownerName, '', self.sr.progressCurrent, self.sr.progressTotal)
        blue.pyos.synchro.Yield()
        if self.sr.scroll is None:
            return
        for entry in self.sr.scroll.GetNodes():
            if entry is None or entry is None or entry.rec is None:
                continue
            if entry.panel is None or entry.panel.destroyed:
                continue
            if entry.rec.characterID == primaryKey:
                if change.has_key('corporationID') and change['corporationID'][1] == None:
                    self.LogInfo('removing member list entry for charID:', primaryKey)
                    self.sr.scroll.RemoveEntries([entry])
                    self.LogInfo('member list entry removed for charID:', primaryKey)
                    break
                entry.panel.DataChanged(primaryKey, change)
                break

        if self.sr.progressCurrent >= self.sr.progressTotal:
            self.sr.progressCurrent = 0
            self.sr.progressTotal = 0

    def CreateWindow(self):
        toppar = ContainerAutoSize(name='options', parent=self, align=uiconst.TOTOP, height=54, alignMode=uiconst.BOTTOMLEFT)
        buttonPar = ContainerAutoSize(parent=toppar, align=uiconst.BOTTOMRIGHT, height=Button.default_height)
        self.sr.fwdBtn = Button(parent=buttonPar, texturePath='res:/UI/Texture/Icons/77_32_41.png', iconSize=20, align=uiconst.TORIGHT, padLeft=4, func=self.Navigate, args=1, hint=localization.GetByLabel('UI/Common/Next'))
        self.sr.backBtn = Button(parent=buttonPar, texturePath='res:/UI/Texture/Icons/77_32_42.png', iconSize=20, align=uiconst.TORIGHT, func=self.Navigate, args=-1, hint=localization.GetByLabel('UI/Common/Previous'))
        numbers = (10, 25, 50, 100, 500)
        optlist = [ (GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/SimpleView/MembersPerPage', num=num), num) for num in numbers ]
        self.sr.MembersPerPage = Combo(parent=toppar, options=optlist, name='membersperpage', callback=self.OnComboChange, width=120, align=uiconst.BOTTOMLEFT)
        viewOptionsList1 = [[localization.GetByLabel('UI/Corporations/Common/Roles'), VIEW_ROLES], [localization.GetByLabel('UI/Corporations/Common/GrantableRoles'), VIEW_GRANTABLE_ROLES], [localization.GetByLabel('UI/Corporations/Common/Titles'), VIEW_TITLES]]
        self.sr.viewtypeCombo = Combo(parent=toppar, options=viewOptionsList1, name='viewtype', callback=self.OnComboChange, width=146, align=uiconst.BOTTOMLEFT, left=self.sr.MembersPerPage.left + self.sr.MembersPerPage.width + 6)
        viewOptionsList2 = []
        for roleGrouping in self.sr.roleGroupings.itervalues():
            viewOptionsList2.append([localization.GetByMessageID(roleGrouping.roleGroupNameID), roleGrouping.roleGroupID])

        self.sr.rolegroupCombo = Combo(parent=toppar, options=viewOptionsList2, name='rolegroup', callback=self.OnComboChange, width=146, align=uiconst.BOTTOMLEFT, left=self.sr.MembersPerPage.left + self.sr.MembersPerPage.width + 158)
        self.sr.scroll = eveScroll.Scroll(name='journal', parent=self, padTop=8)
        self.sr.scroll.OnColumnChanged = self.OnColumnChanged
        buttonGroup = ButtonGroup(parent=self, idx=0)
        buttonGroup.AddButton(localization.GetByLabel('UI/Common/Buttons/SaveChanges'), self.SaveChanges)

    def Navigate(self, direction, *args):
        uthread.new(self.NavigateImpl, direction)

    def NavigateImpl(self, direction):
        if not self.sr.ignoreDirtyFlag and self.IsDirty():
            if eve.Message('CrpMembersSaveChanges', {}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
                self.SaveChanges()
            else:
                self.sr.self.sr.ignoreDirtyFlag = True
        self.sr.viewFrom = self.sr.viewFrom + direction * self.sr.viewPerPage
        if self.sr.viewFrom < 0:
            self.sr.viewFrom = 0
        self.PopulateView()

    def PopulateView(self, memberIDs = None):
        nIndex = 0
        nCount = 0
        try:
            if memberIDs is not None:
                self.memberIDs = memberIDs
            cfg.eveowners.Prime(self.memberIDs)
            sortedMemberList = sorted(self.memberIDs, key=lambda x: cfg.eveowners.Get(x).name)
            nFrom = self.sr.viewFrom
            nTo = nFrom + self.sr.viewPerPage
            if nTo >= len(sortedMemberList) - 1:
                nTo = len(sortedMemberList)
                self.sr.fwdBtn.Disable()
            else:
                self.sr.fwdBtn.Enable()
            if nFrom < 0:
                nFrom = 0
            if nFrom == 0:
                self.sr.backBtn.Disable()
            else:
                self.sr.backBtn.Enable()
            nCount = nTo - nFrom
            sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Generic/Loading'), '', nIndex, nCount)
            blue.pyos.synchro.Yield()
            scrolllist = []
            strings = []
            headers = self.GetHeaderValues()
            fixed = {localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Base'): 88}
            for each in headers:
                if each.lower() in (localization.GetByLabel('UI/Common/Name'), localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Base')):
                    continue
                fixed[each] = uix.GetTextWidth(each, 9, 2) + 24 + 4

            roleGroup = self.sr.roleGroupings[self.sr.viewRoleGroupingID]
            if sortedMemberList:
                self.sr.members.PopulateByMemberIDs(sortedMemberList)
            for ix in range(nFrom, nTo):
                nIndex += 1
                currentCharID = sortedMemberList[ix]
                rec = self.sr.members.GetMember(currentCharID)
                ownerName = cfg.eveowners.Get(rec.characterID).ownerName
                sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Generic/Loading'), ownerName, nIndex, nCount)
                blue.pyos.synchro.Yield()
                baseID = rec.baseID
                base = cfg.evelocations.GetIfExists(baseID)
                if base is not None:
                    baseName = base.locationName
                else:
                    baseName = '-'
                text = '%s<t>%s' % (ownerName, baseName)
                params = {'rec': None,
                 'srcRec': rec,
                 'viewtype': self.sr.viewType,
                 'rolegroup': self.sr.viewRoleGroupingID,
                 'parent': self,
                 'sort_%s' % localization.GetByLabel('UI/Insurance/InsuranceWindow/Name'): cfg.eveowners.Get(rec.characterID).ownerName,
                 'sort_%s' % localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Base'): baseName}
                if self.sr.viewType == VIEW_TITLES:
                    for title in sorted(sm.GetService('corp').GetTitles().itervalues(), key=lambda x: x.titleID):
                        sortvalue = rec.titleMask & title.titleID == title.titleID
                        text += '<t>[%s]' % sortvalue
                        params['sort_%s' % title.titleName] = sortvalue

                else:
                    roles = getattr(rec, roleGroup.appliesTo)
                    grantableRoles = getattr(rec, roleGroup.appliesToGrantable)
                    for column in roleGroup.columns:
                        columnName, subColumns = column
                        newtext = '<t>'
                        sortmask = ''
                        for subColumnName, role in subColumns:
                            isChecked = [roles, grantableRoles][self.sr.viewType] & role.roleID == role.roleID
                            if isChecked:
                                newtext += ' [X] %s' % subColumnName
                            else:
                                newtext += ' [ ] %s' % subColumnName
                            sortmask += [' ', 'X'][not not isChecked]

                        params['sort_%s' % columnName] = sortmask
                        text += newtext

                params['label'] = text
                scrolllist.append(GetFromClass(CorpMemberRoleEntry, params))
                strings.append((text,
                 9,
                 2,
                 0))

            self.tabstops = uicore.font.MeasureTabstops(strings + [('<t>'.join(headers),
              9,
              2,
              0)])
            self.sr.scroll.adjustableColumns = 1
            self.sr.scroll.sr.id = 'CorporationMembers'
            self.sr.scroll.Load(None, scrolllist, self.sr.scroll.GetSortBy(), reversesort=1, headers=headers, noContentHint=localization.GetByLabel('UI/Wallet/WalletWindow/SearchNoResults'))
            self.OnColumnChanged(self.sr.scroll.sr.tabs)
            self.sr.ignoreDirtyFlag = False
        finally:
            sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Common/Loading'), '', nCount, nCount)
            blue.pyos.synchro.Yield()

    def OnColumnChanged(self, tabstops):
        self.LogInfo('ENTRIES [', len(self.sr.scroll.GetNodes()), ']:', self.sr.scroll.GetNodes())
        for node in self.sr.scroll.GetNodes():
            self.LogInfo('>>> ENTRY:', node)
            if node.panel is None or node.panel.destroyed or node is None:
                continue
            panel = node.panel
            try:
                panel.Lock()
                panel.sr.loadingCharacterID = [node.srcRec.characterID]
                panel.OnUpdateTabstops(tabstops)
            finally:
                panel.Unlock()

    def OnComboChange(self, entry, header, value, *args):
        uthread.new(self.OnComboChangeImpl, entry.name, value)

    def OnComboChangeImpl(self, entryName, value):
        if entryName == 'membersperpage':
            if not self.sr.ignoreDirtyFlag and self.IsDirty():
                if eve.Message('CrpMembersSaveChanges', {}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
                    self.SaveChanges()
                else:
                    self.sr.self.sr.ignoreDirtyFlag = True
            self.sr.viewPerPage = value
            self.sr.viewFrom = 0
            return self.PopulateView()
        if entryName == 'viewtype':
            self.sr.viewType = value
            if value == VIEW_TITLES:
                self.sr.rolegroupCombo.state = uiconst.UI_HIDDEN
            else:
                self.sr.rolegroupCombo.state = uiconst.UI_NORMAL
        elif entryName == 'rolegroup':
            self.sr.viewRoleGroupingID = value
        nIndex = 0
        nCount = 0
        try:
            nCount = self.sr.viewPerPage
            for entry in self.sr.scroll.GetNodes():
                if entry is None or entry.rec is None:
                    continue
                if entry.panel is None or entry.panel.destroyed:
                    continue
                nCount += 1

            strings = []
            headers = self.GetHeaderValues()
            headertabs = []
            sortvalues = {}
            roleGroup = self.sr.roleGroupings[self.sr.viewRoleGroupingID]
            for entry in self.sr.scroll.GetNodes():
                nIndex += 1
                if entry is None or entry.rec is None:
                    continue
                rec = entry.rec
                characterID = rec.characterID
                ownerName = cfg.eveowners.Get(characterID).ownerName
                sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Common/Loading'), ownerName, nIndex, nCount)
                blue.pyos.synchro.Yield()
                sortvalues[characterID] = {localization.GetByLabel('UI/Common/Name'): ownerName}
                baseID = rec.baseID
                base = cfg.evelocations.GetIfExists(baseID)
                if base is not None:
                    baseName = base.locationName
                else:
                    baseName = '-'
                text = '%s<t>%s' % (ownerName, baseName)
                sortvalues[characterID][localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Base')] = baseName.upper()
                if self.sr.viewType == VIEW_TITLES:
                    for title in sorted(sm.GetService('corp').GetTitles().itervalues(), key=lambda x: x.titleID):
                        sortvalue = rec.titleMask & title.titleID == title.titleID
                        text += '<t>[%s]' % sortvalue
                        sortvalues[characterID][title.titleName] = str(sortvalue)

                else:
                    roles = getattr(rec, roleGroup.appliesTo)
                    grantableRoles = getattr(rec, roleGroup.appliesToGrantable)
                    for column in roleGroup.columns:
                        columnName, subColumns = column
                        newtext = '<t>'
                        sortvalue = []
                        for subColumn in subColumns:
                            for subColumnName, role in subColumns:
                                isChecked = [roles, grantableRoles][self.sr.viewType] & role.roleID == role.roleID
                                if isChecked:
                                    newtext += ' [X] %s' % subColumnName
                                else:
                                    newtext += ' [ ] %s' % subColumnName
                                sortvalue.append(isChecked)

                        sortvalues[characterID][columnName] = str(sortvalue)
                        text += newtext

                strings.append((text,
                 9,
                 2,
                 0))

            self.tabstops = uicore.font.MeasureTabstops(strings + [('<t>'.join(headers),
              9,
              2,
              0)])
            for entry in self.sr.scroll.GetNodes():
                nIndex += 1
                if entry is None or entry.rec is None:
                    continue
                characterID = entry.rec.characterID
                text = cfg.eveowners.Get(characterID).ownerName
                sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Common/Loading'), text, nIndex, nCount)
                blue.pyos.synchro.Yield()
                for columnName, sortvalue in sortvalues[characterID].iteritems():
                    entry.Set('sort_%s' % columnName, sortvalue)

                if entry.panel is None or entry.panel.destroyed:
                    continue
                entry.panel.sr.loadingCharacterID = [characterID]
                entry.panel.LoadColumns(characterID)
                entry.panel.UpdateLabelText()

            self.sr.scroll.LoadHeaders(headers)
        finally:
            sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Common/Loading'), '', nCount, nCount)
            blue.pyos.synchro.Yield()

    def GetHeaderValues(self):
        viewType = self.sr.viewType
        if viewType == VIEW_TITLES:
            header = [localization.GetByLabel('UI/Common/Name'), localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Base')]
            for title in sorted(sm.GetService('corp').GetTitles().itervalues(), key=lambda x: x.titleID):
                header.append(title.titleName)

        else:
            roleGroup = self.sr.roleGroupings[self.sr.viewRoleGroupingID]
            header = [localization.GetByLabel('UI/Common/Name'), localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Base')]
            for column in roleGroup.columns:
                columnName, subColumns = column
                colName = eveformat.replace_text_ignoring_tags(columnName, old=' ', new='<br>')
                header.append(colName)

        return header

    def MemberDetails(self, charid, *args):
        log.LogInfo('members.MemberDetails charid:', charid)
        EditMemberDialog.Open(charID=charid)

    def IsDirty(self):
        try:
            sm.GetService('loading').Cycle(localization.GetByLabel('UI/Common/PleaseWait'))
            if self and not self.destroyed and self.sr.scroll is not None:
                nodes = self.sr.scroll.GetNodes()
                for node in nodes:
                    if node is None or node is None or node.rec is None:
                        continue
                    changed = 0
                    if node.rec.roles != node.rec.oldRoles:
                        changed = 1
                    elif node.rec.grantableRoles != node.rec.oldGrantableRoles:
                        changed = 1
                    elif node.rec.rolesAtHQ != node.rec.oldRolesAtHQ:
                        changed = 1
                    elif node.rec.grantableRolesAtHQ != node.rec.oldGrantableRolesAtHQ:
                        changed = 1
                    elif node.rec.rolesAtBase != node.rec.oldRolesAtBase:
                        changed = 1
                    elif node.rec.grantableRolesAtBase != node.rec.oldGrantableRolesAtBase:
                        changed = 1
                    elif node.rec.rolesAtOther != node.rec.oldRolesAtOther:
                        changed = 1
                    elif node.rec.grantableRolesAtOther != node.rec.oldGrantableRolesAtOther:
                        changed = 1
                    elif node.rec.baseID != node.rec.oldBaseID:
                        changed = 1
                    elif node.rec.titleMask != node.rec.oldTitleMask:
                        changed = 1
                    if not changed:
                        continue
                    return 1

            return 0
        finally:
            sm.GetService('loading').StopCycle()

    def SaveChanges(self, *args):
        nodesToUpdate = []
        try:
            sm.GetService('loading').Cycle(localization.GetByLabel('UI/Common/PreparingToUpdate'))
            for node in self.sr.scroll.GetNodes():
                if not node or not node or not node.rec:
                    continue
                changed = 0
                if node.rec.roles != node.rec.oldRoles:
                    changed = 1
                elif node.rec.grantableRoles != node.rec.oldGrantableRoles:
                    changed = 1
                elif node.rec.rolesAtHQ != node.rec.oldRolesAtHQ:
                    changed = 1
                elif node.rec.grantableRolesAtHQ != node.rec.oldGrantableRolesAtHQ:
                    changed = 1
                elif node.rec.rolesAtBase != node.rec.oldRolesAtBase:
                    changed = 1
                elif node.rec.grantableRolesAtBase != node.rec.oldGrantableRolesAtBase:
                    changed = 1
                elif node.rec.rolesAtOther != node.rec.oldRolesAtOther:
                    changed = 1
                elif node.rec.grantableRolesAtOther != node.rec.oldGrantableRolesAtOther:
                    changed = 1
                elif node.rec.baseID != node.rec.oldBaseID:
                    changed = 1
                elif node.rec.titleMask != node.rec.oldTitleMask:
                    changed = 1
                if not changed:
                    continue
                nodesToUpdate.append(node)

        finally:
            sm.GetService('loading').StopCycle()

        nCount = len(nodesToUpdate)
        if nCount == 0:
            log.LogWarn('Nothing to save')
        self.sr.progressCurrent = 0
        self.sr.progressTotal = nCount
        nIndex = 0
        try:
            sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Common/Updating'), '', nIndex, nCount)
            blue.pyos.synchro.Yield()
            rows = None
            myRow = None
            for node in nodesToUpdate:
                entry = node.rec
                src = node.srcRec
                characterID = entry.characterID
                title = src.title
                divisionID = src.divisionID
                squadronID = src.squadronID
                roles = entry.roles
                grantableRoles = entry.grantableRoles
                rolesAtHQ = entry.rolesAtHQ
                grantableRolesAtHQ = entry.grantableRolesAtHQ
                rolesAtBase = entry.rolesAtBase
                grantableRolesAtBase = entry.grantableRolesAtBase
                rolesAtOther = entry.rolesAtOther
                grantableRolesAtOther = entry.grantableRolesAtOther
                baseID = entry.baseID
                titleMask = entry.titleMask
                if entry.titleMask == src.titleMask:
                    titleMask = None
                if roles & const.corpRoleDirector == const.corpRoleDirector:
                    roles = const.corpRoleDirector
                    grantableRoles = 0
                    rolesAtHQ = 0
                    grantableRolesAtHQ = 0
                    rolesAtBase = 0
                    grantableRolesAtBase = 0
                    rolesAtOther = 0
                    grantableRolesAtOther = 0
                if characterID == eve.session.charid:
                    if myRow is None:
                        myRow = Rowset(['characterID',
                         'title',
                         'divisionID',
                         'squadronID',
                         'roles',
                         'grantableRoles',
                         'rolesAtHQ',
                         'grantableRolesAtHQ',
                         'rolesAtBase',
                         'grantableRolesAtBase',
                         'rolesAtOther',
                         'grantableRolesAtOther',
                         'baseID',
                         'titleMask'])
                    myRow.append([characterID,
                     None,
                     None,
                     None,
                     roles,
                     grantableRoles,
                     rolesAtHQ,
                     grantableRolesAtHQ,
                     rolesAtBase,
                     grantableRolesAtBase,
                     rolesAtOther,
                     grantableRolesAtOther,
                     baseID,
                     titleMask])
                else:
                    if rows is None:
                        rows = Rowset(['characterID',
                         'title',
                         'divisionID',
                         'squadronID',
                         'roles',
                         'grantableRoles',
                         'rolesAtHQ',
                         'grantableRolesAtHQ',
                         'rolesAtBase',
                         'grantableRolesAtBase',
                         'rolesAtOther',
                         'grantableRolesAtOther',
                         'baseID',
                         'titleMask'])
                    rows.append([characterID,
                     None,
                     None,
                     None,
                     roles,
                     grantableRoles,
                     rolesAtHQ,
                     grantableRolesAtHQ,
                     rolesAtBase,
                     grantableRolesAtBase,
                     rolesAtOther,
                     grantableRolesAtOther,
                     baseID,
                     titleMask])

            if rows is not None:
                sm.GetService('corp').UpdateMembers(rows)
            if myRow is not None:
                sm.GetService('sessionMgr').PerformSessionChange('corp.UpdateMembers', sm.GetService('corp').UpdateMembers, myRow)
        finally:
            if nCount:
                sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Common/Updated'), '', nCount - 1, nCount)
                blue.pyos.synchro.SleepWallclock(500)
                sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Common/Updated'), '', nCount, nCount)
                blue.pyos.synchro.Yield()
