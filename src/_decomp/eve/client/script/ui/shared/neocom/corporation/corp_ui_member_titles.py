#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\corp_ui_member_titles.py
import sys
import types
import blue
import eveformat
import uthread
import carbon.client.script.util.lg as lg
import log
import carbonui.const as uiconst
import localization
from carbon.common.script.util.commonutils import StripTags
from carbonui.control.combo import Combo
from carbonui.control.label import LabelCore
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbon.common.script.sys.row import Row
from carbonui.primitives.container import Container
from carbonui.util.various_unsorted import SortListOfTuples
from eve.client.script.ui.control import eveLabel, eveScroll
from carbonui.button.group import ButtonGroup
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.checkbox import Checkbox
from carbonui.control.radioButton import RadioButton
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.header import Subheader
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.listgroup import ListGroup
from eve.client.script.ui.services.corporation.corp_util import VIEW_GRANTABLE_ROLES, VIEW_ROLES, VIEW_TITLES
from eve.client.script.ui.shared.neocom.corporation import corpUISignals
from eve.client.script.ui.shared.neocom.corporation.corp_ui_member_tracking import MemberTracking
from eve.common.script.sys.rowset import Rowset
from carbonui.uicore import uicore
from globalConfig.getFunctions import IsContentComplianceControlSystemActive
from eve.common.lib import appConst as const

class CorpTitles(Container):
    __guid__ = 'form.CorpTitles'
    __nonpersistvars__ = []

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.sr.titles = sm.GetService('corp').GetTitles()
        self.sr.viewType = 0
        self.sr.viewRoleGroupingID = 1
        self.sr.roleGroupings = sm.GetService('corp').GetRoleGroupings(1)
        self.sr.progressCurrent = 0
        self.sr.progressTotal = 0
        self.sr.scroll = None
        self.sr.crits = {}
        self.sr.debug = False
        self.sr.ignoreDirtyFlag = False
        corpUISignals.on_title_changed.connect(self.OnTitleChanged)

    def LogInfo(self, *args):
        lg.Info(self.__guid__, *args)

    def __EnterCriticalSection(self, k, v = None):
        if (k, v) not in self.sr.crits:
            self.sr.crits[k, v] = uthread.CriticalSection((k, v))
        self.sr.crits[k, v].acquire()

    def __LeaveCriticalSection(self, k, v = None):
        self.sr.crits[k, v].release()
        if (k, v) in self.sr.crits and self.sr.crits[k, v].IsCool():
            del self.sr.crits[k, v]

    def _OnClose(self, *args):
        self.OnTabDeselect()

    def OnTabDeselect(self):
        if not self.sr.ignoreDirtyFlag and self.IsDirty():
            if eve.Message('CrpTitlesSaveChanges', {}, uiconst.YESNO) == uiconst.ID_YES:
                self.SaveChanges()
            else:
                self.sr.ignoreDirtyFlag = True

    def OnTitleChanged(self, corpID, titleID, change):
        if self.sr.debug:
            self.LogInfo('----------------------------------------------')
            self.LogInfo('OnTitleChanged')
            self.LogInfo('corpID:', corpID)
            self.LogInfo('titleID:', titleID)
            self.LogInfo('change:', change)
            self.LogInfo('----------------------------------------------')
        if not (self and not self.destroyed):
            return
        if self.sr.progressTotal == 0:
            self.sr.progressCurrent = 0
            self.sr.progressTotal = 1
        self.sr.progressCurrent += 1
        sm.GetService('loading').ProgressWnd(self.sr.titles[titleID].titleName, 'Updated', self.sr.progressCurrent, self.sr.progressTotal)
        blue.pyos.synchro.Yield()
        if self.sr.scroll is None:
            return
        for entry in self.sr.scroll.GetNodes():
            if entry is None or entry.rec is None:
                continue
            if entry.panel is None or entry.panel.destroyed:
                continue
            if entry.rec.titleID == titleID:
                entry.panel.OnTitleChanged(corpID, titleID, change)
                break

        if self.sr.progressCurrent >= self.sr.progressTotal:
            self.sr.progressCurrent = 0
            self.sr.progressTotal = 0

    def CreateWindow(self):
        optionsParent = Container(name='optionsParent', parent=self, align=uiconst.TOTOP, height=36, padBottom=8)
        self.collapseIconCont = Container(name='collapseIconCont', parent=optionsParent, width=20, align=uiconst.TOLEFT)
        ButtonIcon(name='collapse', parent=self.collapseIconCont, align=uiconst.CENTERBOTTOM, pos=(4, 4, 12, 12), iconSize=12, texturePath='res:/UI/Texture/classes/Scroll/Collapse.png', func=self.CollapseAll, hint=localization.GetByLabel('UI/Common/Buttons/CollapseAll'))
        self.collapseIconCont.display = False
        toppar = Container(name='options', parent=optionsParent, align=uiconst.TOTOP, height=36)
        Container(name='push', parent=toppar, align=uiconst.TOTOP, height=6)
        viewOptionsList1 = [[localization.GetByLabel('UI/Corporations/Common/Roles'), VIEW_ROLES], [localization.GetByLabel('UI/Corporations/Common/GrantableRoles'), VIEW_GRANTABLE_ROLES], [localization.GetByLabel('UI/Corporations/Common/TitleSummary'), VIEW_TITLES]]
        viewOptionsList2 = []
        for roleGrouping in self.sr.roleGroupings.itervalues():
            viewOptionsList2.append([localization.GetByMessageID(roleGrouping.roleGroupNameID), roleGrouping.roleGroupID])

        i = 0
        viewTypeCombo = Combo(label=localization.GetByLabel('UI/Common/View'), parent=toppar, options=viewOptionsList1, name='viewtype', callback=self.OnComboChange, width=146, pos=(5, 0, 0, 0), align=uiconst.BOTTOMLEFT)
        left = 5 + viewTypeCombo.left + viewTypeCombo.width
        self.roleGroupCombo = Combo(label=localization.GetByLabel('UI/Common/Type'), parent=toppar, options=viewOptionsList2, name='rolegroup', callback=self.OnComboChange, width=146, pos=(left,
         0,
         0,
         0), align=uiconst.BOTTOMLEFT)
        self.titleCombo = Combo(label=localization.GetByLabel('UI/Corporations/EditMemberDialog/CorpMemberTitleCaption'), parent=toppar, options=[], name='titleCombo', callback=self.OnTitleComboChanged, width=146, pos=(left,
         0,
         0,
         0), align=uiconst.BOTTOMLEFT)
        self.titleCombo.display = False
        toppar.height = optionsParent.height = max(viewTypeCombo.height + 14, 36)
        self.sr.scroll = eveScroll.Scroll(name='journal', parent=self, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.sr.summaryScroll = eveScroll.Scroll(name='summaryScroll', parent=self, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.sr.summaryScroll.display = False
        self.sr.scroll.OnColumnChanged = self.OnColumnChanged
        self.btnGroup = ButtonGroup(parent=self, idx=0)
        self.btnGroup.AddButton(localization.GetByLabel('UI/Common/Buttons/SaveChanges'), self.SaveChanges)

    def Load(self, panel_id, *args):
        if not self.sr.Get('inited', 0):
            self.sr.inited = 1
            self.CreateWindow()
        if not const.corpRoleDirector & eve.session.corprole == const.corpRoleDirector:
            self.SetHint(localization.GetByLabel('UI/Corporations/CorporationWindow/Members/AccessDeniedDirectorRoleRequired'))
            sm.GetService('corpui').HideLoad()
            return
        self.PopulateView()

    def SetHint(self, hintstr = None):
        if self.sr.scroll:
            self.sr.scroll.ShowHint(hintstr)

    def PopulateView(self):
        self.ShowOrHideElements(self.sr.viewType)
        if self.sr.viewType == VIEW_TITLES:
            return self.LoadTitleSummary()
        return self._PopulateRoleView()

    def ShowOrHideElements(self, view):
        isShowingSummary = view == VIEW_TITLES
        isShowingRoles = not isShowingSummary
        self.sr.scroll.display = isShowingRoles
        self.sr.summaryScroll.display = isShowingSummary
        self.btnGroup.display = isShowingRoles
        self.titleCombo.display = isShowingSummary
        self.roleGroupCombo.display = isShowingRoles
        self.collapseIconCont.display = isShowingSummary

    def _PopulateRoleView(self):
        nIndex = 0
        scrolllist = []
        strings = []
        headers = self.GetHeaderValues(self.sr.viewRoleGroupingID)
        roleGroup = self.sr.roleGroupings[self.sr.viewRoleGroupingID]
        hintsByColumnText = {}
        for titleID, title in self.sr.titles.iteritems():
            nIndex += 1
            rec = title
            text = '%s' % rec.titleName
            roles = getattr(rec, roleGroup.appliesTo)
            grantableRoles = getattr(rec, roleGroup.appliesToGrantable)
            params = {'rec': None,
             'srcRec': rec,
             'viewtype': self.sr.viewType,
             'rolegroup': self.sr.viewRoleGroupingID,
             'parent': self,
             'sort_%s' % headers[0]: text}
            for column in roleGroup.columns:
                columnName, subColumns = column
                newtext = '<t>'
                sortmask = ''
                for subColumnName, role in subColumns:
                    isChecked = [roles, grantableRoles][self.sr.viewType] & role.roleID == role.roleID
                    if isChecked:
                        checkedText = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/TitleHasRole', corpRole=subColumnName)
                    else:
                        checkedText = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/TitleDoesNotHaveRole', corpRole=subColumnName)
                    newtext += checkedText
                    sortmask += [' ', 'X'][not not isChecked]
                    if role.shortDescription == columnName:
                        hintsByColumnText[columnName] = role.description
                        break

                params['sort_%s' % columnName] = sortmask
                text += newtext

            params['label'] = text
            if self.sr.debug:
                self.LogInfo(params)
            scrolllist.append(GetFromClass(CorpTitleEntry, params))
            strings.append((text,
             9,
             2,
             0))

        self.tabstops = uicore.font.MeasureTabstops(strings + [('<t>'.join(headers),
          9,
          2,
          0)])
        self.sr.scroll.adjustableColumns = 1
        self.sr.scroll.sr.id = 'CorporationTitles'
        self.sr.scroll.Load(None, scrolllist, self.sr.scroll.GetSortBy(), reversesort=1, headers=headers)
        self.UpdateHeaderHints(hintsByColumnText)
        self.OnColumnChanged(self.sr.scroll.sr.tabs)
        self.sr.ignoreDirtyFlag = False

    def UpdateHeaderHints(self, hintsByColumnText):
        for eachHeaderChild in self.sr.scroll.GetHeadersChildren():
            headerName = eachHeaderChild.name.replace('<br>', ' ')
            if headerName in hintsByColumnText:
                eachHeaderChild.hint = '%s<br>%s' % (headerName, hintsByColumnText[headerName])

    def OnColumnChanged(self, tabstops):
        if self.sr.debug:
            self.LogInfo('ENTRIES [', len(self.sr.scroll.GetNodes()), ']:', self.sr.scroll.GetNodes())
        for node in self.sr.scroll.GetNodes():
            if self.sr.debug:
                self.LogInfo('>>> ENTRY:', node)
            if node.panel is None or node.panel.destroyed or node is None:
                continue
            panel = node.panel
            try:
                panel.Lock()
                panel.sr.loadingTitleID = [node.srcRec.titleID]
                panel.OnUpdateTabstops(tabstops)
            finally:
                panel.Unlock()

    def OnTitleComboChanged(self, *args):
        self.LoadTitleSummary()

    def OnComboChange(self, entry, header, value, *args):
        newView = value
        if entry.name == 'viewtype':
            self.ShowOrHideElements(newView)
        if entry.name == 'viewtype' and newView == VIEW_TITLES:
            self.sr.viewType = newView
            return self.LoadTitleSummary()
        uthread.new(self.OnComboChangeImpl, entry.name, newView)

    def OnComboChangeImpl(self, entryName, value):
        self.__EnterCriticalSection('corp_ui_titles')
        try:
            if entryName == 'viewtype':
                self.sr.viewType = value
            elif entryName == 'rolegroup':
                self.sr.viewRoleGroupingID = value
            strings = []
            headers = self.GetHeaderValues(self.sr.viewRoleGroupingID)
            headertabs = []
            sortvalues = {}
            roleGroup = self.sr.roleGroupings[self.sr.viewRoleGroupingID]
            for entry in self.sr.scroll.GetNodes():
                rec = entry.rec
                if not rec:
                    continue
                text = rec.titleName
                titleID = rec.titleID
                sortvalues[titleID] = {localization.GetByLabel('UI/Corporations/CorporationWindow/Members/CorpMemberName'): text}
                roles = getattr(rec, roleGroup.appliesTo)
                grantableRoles = getattr(rec, roleGroup.appliesToGrantable)
                for column in roleGroup.columns:
                    columnName, subColumns = column
                    newtext = '<t>'
                    for subColumnName, role in subColumns:
                        rolesInUse = grantableRoles if self.sr.viewType == VIEW_GRANTABLE_ROLES else roles
                        isChecked = rolesInUse & role.roleID == role.roleID
                        if isChecked:
                            checkedText = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/TitleHasRole', corpRole=subColumnName)
                        else:
                            checkedText = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/TitleDoesNotHaveRole', corpRole=subColumnName)
                        newtext += checkedText

                    text += newtext

                strings.append((text,
                 9,
                 2,
                 0))
                entry.label = text

            self.tabstops = uicore.font.MeasureTabstops(strings + [('<t>'.join(headers),
              9,
              2,
              0)])
            self.sr.scroll.adjustableColumns = 1
            for entry in self.sr.scroll.GetNodes():
                if entry is None or entry.rec is None:
                    continue
                titleID = entry.rec.titleID
                entry.viewtype = self.sr.viewType
                entry.rolegroup = self.sr.viewRoleGroupingID
                for columnName, sortvalue in sortvalues[titleID].iteritems():
                    entry.Set('sort_%s' % columnName, sortvalue)

                if entry.panel is None or entry.panel.destroyed:
                    continue
                entry.panel.sr.loadingTitleID = [titleID]
                entry.panel.LoadColumns(titleID)
                entry.panel.UpdateLabelText()

            self.sr.scroll.LoadHeaders(headers)
        finally:
            self.__LeaveCriticalSection('corp_ui_titles')

    def GetHeaderValues(self, roleGroupingID):
        roleGroup = self.sr.roleGroupings[roleGroupingID]
        headers = [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/CorpMemberName')]
        for column in roleGroup.columns:
            columnName, subColumns = column
            colName = eveformat.replace_text_ignoring_tags(columnName, old=' ', new='<br>')
            headers.append(colName)

        return headers

    def IsDirty(self):
        try:
            sm.GetService('loading').Cycle('Please wait')
            if self and not self.destroyed and self.sr and self.sr.scroll is not None:
                nodes = self.sr.scroll.GetNodes()
                for node in nodes:
                    if node is None or node is None or node.rec is None:
                        continue
                    changed = 0
                    if node.rec.titleName != node.rec.oldTitleName:
                        changed = 1
                    elif node.rec.roles != node.rec.oldRoles:
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
                    if not changed:
                        continue
                    return 1

            return 0
        finally:
            sm.GetService('loading').StopCycle()

    def SaveChanges(self, *args):
        nodesToUpdate = []
        try:
            sm.GetService('loading').Cycle('Preparing to update')
            for node in self.sr.scroll.GetNodes():
                if not node or not node or not node.rec:
                    continue
                changed = 0
                if node.rec.titleName != node.rec.oldTitleName:
                    changed = 1
                elif node.rec.roles != node.rec.oldRoles:
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
                if not changed:
                    continue
                nodesToUpdate.append(node)

        finally:
            sm.GetService('loading').StopCycle()

        nCount = len(nodesToUpdate)
        if nCount == 0:
            if self.sr.debug:
                self.LogWarn('Nothing to save')
            sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Common/PleaseWait'), '', 0, 1)
            blue.pyos.synchro.SleepWallclock(500)
            sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Common/PleaseWait'), '', 1, 1)
            blue.pyos.synchro.Yield()
            return
        self.sr.progressCurrent = 0
        self.sr.progressTotal = nCount
        nIndex = 0
        try:
            sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Common/Updating'), '', nIndex, nCount)
            blue.pyos.synchro.Yield()
            rows = None
            for node in nodesToUpdate:
                entry = node.rec
                src = node.srcRec
                titleID = src.titleID
                titleName = entry.titleName
                roles = entry.roles
                grantableRoles = entry.grantableRoles
                rolesAtHQ = entry.rolesAtHQ
                grantableRolesAtHQ = entry.grantableRolesAtHQ
                rolesAtBase = entry.rolesAtBase
                grantableRolesAtBase = entry.grantableRolesAtBase
                rolesAtOther = entry.rolesAtOther
                grantableRolesAtOther = entry.grantableRolesAtOther
                roles &= ~const.corpRoleDirector
                grantableRoles &= ~const.corpRoleDirector
                rolesAtHQ &= ~const.corpRoleDirector
                grantableRolesAtHQ &= ~const.corpRoleDirector
                rolesAtBase &= ~const.corpRoleDirector
                grantableRolesAtBase &= ~const.corpRoleDirector
                rolesAtOther &= ~const.corpRoleDirector
                grantableRolesAtOther &= ~const.corpRoleDirector
                if rows is None:
                    rows = Rowset(['titleID',
                     'titleName',
                     'roles',
                     'grantableRoles',
                     'rolesAtHQ',
                     'grantableRolesAtHQ',
                     'rolesAtBase',
                     'grantableRolesAtBase',
                     'rolesAtOther',
                     'grantableRolesAtOther'])
                rows.append([titleID,
                 titleName,
                 roles,
                 grantableRoles,
                 rolesAtHQ,
                 grantableRolesAtHQ,
                 rolesAtBase,
                 grantableRolesAtBase,
                 rolesAtOther,
                 grantableRolesAtOther])

            if rows is not None:
                sm.GetService('corp').UpdateTitles(rows)
        finally:
            if nCount:
                sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Common/Updated'), '', nCount - 1, nCount)
                blue.pyos.synchro.SleepWallclock(500)
                sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Common/Updated'), '', nCount, nCount)
                blue.pyos.synchro.Yield()

        self.PopulateView()

    def LoadTitleSummary(self):
        self.ShowOrHideElements(self.sr.viewType)
        titleOptions = []
        for titleID, title in self.sr.titles.iteritems():
            titleOptions.append((title.titleName, titleID))

        selected = self.titleCombo.GetValue()
        self.titleCombo.LoadOptions(titleOptions, select=selected)
        entries = []
        groupEntry = GetFromClass(ListGroup, {'label': localization.GetByLabel('UI/Corporations/CorporationWindow/Members/MembersWithTitle'),
         'GetSubContent': self.GetMemberWithTitle,
         'groupItems': None,
         'id': ('titleSummary', 'members'),
         'state': 'locked',
         'showicon': 'hide'})
        entries.append(groupEntry)
        groupEntry = GetFromClass(ListGroup, {'label': localization.GetByLabel('UI/Corporations/CorporationWindow/Members/RolesInTitle'),
         'GetSubContent': self.GetAllRolesForTitle,
         'groupItems': None,
         'id': ('titleSummary', 'roles'),
         'state': 'locked',
         'showicon': 'hide'})
        entries.append(groupEntry)
        self.sr.summaryScroll.Load(None, contentList=entries)

    def GetMemberWithTitle(self, *args):
        selectedTitleID = self.titleCombo.GetValue()
        allMembers = sm.GetService('corp').GetMembers()
        memberIDs = set()
        for member in allMembers:
            if member.titleMask & selectedTitleID:
                memberIDs.add(member.characterID)

        cfg.eveowners.Prime(memberIDs)
        scrollList = []
        for eachCharID in memberIDs:
            entry = GetFromClass(MemberTracking, {'charID': eachCharID,
             'showinfo': True,
             'typeID': const.typeCharacter,
             'itemID': eachCharID,
             'slimuser': True,
             'sublevel': 1})
            scrollList.append((cfg.eveowners.Get(eachCharID).name.lower(), entry))

        scrollList = SortListOfTuples(scrollList)
        return scrollList

    def GetAllRolesForTitle(self, *args):
        titleID = self.titleCombo.GetValue()
        titleInfo = self.sr.titles.get(titleID, None)
        roleGroupings = sm.GetService('corp').GetRoleGroupings()
        roleText = localization.GetByLabel('UI/Corporations/Common/Role')
        grantableRoleText = localization.GetByLabel('UI/Corporations/EditMemberDialog/GrantableRole').strip()
        scrollList = []
        for roleGroup in roleGroupings.itervalues():
            scrollListForGroup = []
            rolesMask = getattr(titleInfo, roleGroup.appliesTo)
            grantableRolesMask = getattr(titleInfo, roleGroup.appliesToGrantable)
            for columnName, subColumns in roleGroup.columns:
                for subColumn in subColumns:
                    name, role = subColumn
                    isRoleInTitle = rolesMask & role.roleID == role.roleID
                    isGrantableRoleInTitle = grantableRolesMask & role.roleID == role.roleID
                    if not isRoleInTitle and not isGrantableRoleInTitle:
                        continue
                    extraText = localization.formatters.FormatGenericList([ x for x, y in ((roleText, isRoleInTitle), (grantableRoleText, isGrantableRoleInTitle)) if y ])
                    roleName = role.shortDescription
                    nameForRole = roleName
                    if nameForRole != columnName:
                        nameForRole += ' - %s' % columnName
                    label = nameForRole + ' <color=grey>(%s)</color>' % extraText
                    entry = GetFromClass(Generic, {'label': label,
                     'sublevel': 2})
                    scrollListForGroup.append(entry)

            if scrollListForGroup:
                entry = GetFromClass(Subheader, {'label': '<b>%s<b>' % localization.GetByMessageID(roleGroup.roleGroupNameID),
                 'sublevel': 1})
                scrollList.append(entry)
                scrollList += scrollListForGroup

        return scrollList

    def CollapseAll(self, *args):
        self.sr.summaryScroll.CollapseAll()


class CorpTitleEntry(Generic):
    __guid__ = 'listentry.CorpTitleEntry'
    __nonpersistvars__ = []
    __params__ = ['rec',
     'srcRec',
     'viewtype',
     'rolegroup']

    def Startup(self, *etc):
        self.sr.loadingTitleID = []
        self.sr.lock = None
        self.sr.originalChildren = []
        Generic.Startup(self, *etc)
        self.sr.columns = []
        self.sr.roleGroupings = sm.GetService('corp').GetRoleGroupings(1)
        for childControl in self.children:
            self.sr.originalChildren.append(childControl)

        self.sr.label.state = uiconst.UI_HIDDEN
        self.sr.rowHeader = ['titleID',
         'titleName',
         'oldTitleName',
         'roles',
         'oldRoles',
         'grantableRoles',
         'oldGrantableRoles',
         'rolesAtHQ',
         'oldRolesAtHQ',
         'grantableRolesAtHQ',
         'oldGrantableRolesAtHQ',
         'rolesAtBase',
         'oldRolesAtBase',
         'grantableRolesAtBase',
         'oldGrantableRolesAtBase',
         'rolesAtOther',
         'oldRolesAtOther',
         'grantableRolesAtOther',
         'oldGrantableRolesAtOther',
         'isCEO',
         'isDirector',
         'IAmCEO',
         'IAmDirector']

    def Lock(self):
        if self.sr.lock is None:
            self.sr.lock = uthread.Semaphore()
        self.sr.lock.acquire()

    def Unlock(self):
        self.sr.lock.release()
        if self.sr.lock.IsCool():
            self.sr.lock = None

    def GetViewRoleGroupingID(self):
        return self.sr.node.parent.sr.viewRoleGroupingID

    def GetRelevantRoles(self):
        viewRoleGroupingID = self.GetViewRoleGroupingID()
        roleGroup = self.sr.roleGroupings[viewRoleGroupingID]
        if self.sr.node.viewtype == VIEW_GRANTABLE_ROLES:
            return getattr(self.GetRec(), roleGroup.appliesToGrantable)
        return getattr(self.GetRec(), roleGroup.appliesTo)

    def GetRelevantChange(self, change):
        viewRoleGroupingID = self.GetViewRoleGroupingID()
        roleGroup = self.sr.roleGroupings[viewRoleGroupingID]
        return change[[roleGroup.appliesTo, roleGroup.appliesToGrantable][self.sr.node.viewtype == VIEW_GRANTABLE_ROLES]]

    def GetHeight(self, *args):
        node, width = args
        node.height = 36
        return node.height

    def GetRec(self):
        return self.sr.node.rec

    def LogInfo(self, *args):
        lg.Info(self.__guid__, *args)

    def Load(self, node):
        try:
            self.Lock()
            s = blue.os.GetWallclockTimeNow()
            Generic.Load(self, node)
            loadingTitleID = node.srcRec.titleID
            self.sr.loadingTitleID.append(loadingTitleID)
            self.state = uiconst.UI_DISABLED
            self.LogInfo('Load 0 took %s ms.' % blue.os.TimeDiffInMs(s, blue.os.GetWallclockTimeNow()))
        finally:
            self.Unlock()

        try:
            try:
                self.Lock()
                s = blue.os.GetWallclockTimeNow()
                if self.sr.node is None:
                    return
                if self.sr.node.rec is None or self.sr.node.rec.titleID != node.srcRec.titleID:
                    self.sr.node = node
                    self.GetTitlesListData()
                if 0 == len(self.sr.loadingTitleID) or loadingTitleID != self.sr.loadingTitleID[-1]:
                    return
            finally:
                self.LogInfo('Load 1 took %s ms.' % blue.os.TimeDiffInMs(s, blue.os.GetWallclockTimeNow()))
                self.Unlock()

            try:
                self.Lock()
                s = blue.os.GetWallclockTimeNow()
                if self.sr.node is None:
                    return
                self.LoadColumns(loadingTitleID)
                if 0 == len(self.sr.loadingTitleID) or loadingTitleID != self.sr.loadingTitleID[-1]:
                    return
            finally:
                self.LogInfo('Load 2 took %s ms.' % blue.os.TimeDiffInMs(s, blue.os.GetWallclockTimeNow()))
                self.Unlock()

            try:
                self.Lock()
                s = blue.os.GetWallclockTimeNow()
                if self.sr.node is None:
                    return
                self.UpdateLabelText()
            finally:
                self.LogInfo('Load 3 took %s ms.' % blue.os.TimeDiffInMs(s, blue.os.GetWallclockTimeNow()))
                self.Unlock()

        except:
            log.LogException()
            sys.exc_clear()
        finally:
            if loadingTitleID in self.sr.loadingTitleID:
                self.sr.loadingTitleID.remove(loadingTitleID)

        self.state = uiconst.UI_NORMAL
        self.sr.label.Update()
        self.sr.label.state = uiconst.UI_HIDDEN

    def OnTitleChanged(self, corpID, titleID, change):
        self.LogInfo('----------------------------------------------')
        self.LogInfo('OnTitleChanged')
        self.LogInfo('corpID:', corpID)
        self.LogInfo('titleID:', titleID)
        self.LogInfo('change:', change)
        self.LogInfo('----------------------------------------------')
        self.GetTitlesListData()
        self.UpdateLabelText()
        viewRoleGroupingID = self.GetViewRoleGroupingID()
        roleGroup = self.sr.roleGroupings[viewRoleGroupingID]
        if not (change.has_key('roles') and const.corpRoleDirector & change['roles'][0] != const.corpRoleDirector & change['roles'][1]):
            if self.sr.node.viewtype == VIEW_GRANTABLE_ROLES:
                if not change.has_key(roleGroup.appliesToGrantable):
                    return
            elif not change.has_key(roleGroup.appliesTo):
                return
        i = -1
        previousTabPosition = 0
        self.LogInfo('change:', change)
        old, new = self.GetRelevantChange(change)
        for tabstop in self.sr.node.parent.tabstops:
            i += 1
            if i == 0:
                if change.has_key('titleName'):
                    column = self.sr.columns[i][0]
                    column.SetValue(change['titleName'][1])
                continue
            columnNumber = i - 1
            column = roleGroup.columns[columnNumber]
            columnName, subColumns = column
            controlNumber = -1
            for subColumn in subColumns:
                controlNumber += 1
                subColumnName, role = subColumn
                roleID = role.roleID
                if (old & roleID == roleID) == (new & roleID == roleID):
                    continue
                control = self.sr.columns[i][controlNumber]
                value = self.GetRelevantRoles() & roleID == roleID
                if value:
                    text = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/TitleHasRoleYShort')
                else:
                    text = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/TitleDoesNotHaveRoleNShort')
                if isinstance(column, Checkbox):
                    checked = column.GetValue()
                    if checked == value:
                        control.SetLabelText(subColumnName)
                        continue
                    label.text = subColumnName + ' ' + text
                else:
                    control.text = text + ' ' + subColumnName

    def GetTitlesListData(self):
        corporation = sm.GetService('corp').GetCorporation()
        IAmCEO = corporation.ceoID == eve.session.charid
        IAmDirector = [eve.session.corprole & const.corpRoleDirector, 0][IAmCEO]
        title = self.sr.node.srcRec
        roles = title.roles
        grantableRoles = title.grantableRoles
        rolesAtHQ = title.rolesAtHQ
        grantableRolesAtHQ = title.grantableRolesAtHQ
        rolesAtBase = title.rolesAtBase
        grantableRolesAtBase = title.grantableRolesAtBase
        rolesAtOther = title.rolesAtOther
        grantableRolesAtOther = title.grantableRolesAtOther
        isCEO = 0
        isDirector = 0
        grantableRoles = grantableRoles & ~const.corpRoleDirector
        roles = roles & ~const.corpRoleDirector
        line = [title.titleID,
         title.titleName,
         '%s' % title.titleName,
         roles,
         long(roles),
         grantableRoles,
         long(grantableRoles),
         rolesAtHQ,
         long(rolesAtHQ),
         grantableRolesAtHQ,
         long(grantableRolesAtHQ),
         rolesAtBase,
         long(rolesAtBase),
         grantableRolesAtBase,
         long(grantableRolesAtBase),
         rolesAtOther,
         long(rolesAtOther),
         grantableRolesAtOther,
         long(grantableRolesAtOther),
         isCEO,
         isDirector,
         IAmCEO,
         IAmDirector]
        self.sr.node.rec = Row(self.sr.rowHeader, line)
        self.LogInfo(self.sr.node.rec)

    def OnUpdateTabstops(self, tabstops):
        data = self.sr.node
        data.parent.tabstops = tabstops
        rec = self.GetRec()
        if rec is None:
            return
        self.LoadColumns(rec.titleID)

    def LoadColumns(self, loadingTitleID):
        if len(self.sr.loadingTitleID) and loadingTitleID != self.sr.loadingTitleID[-1]:
            return
        data = self.sr.node
        tabstops = data.parent.tabstops
        rec = self.GetRec()
        viewtype = data.viewtype
        viewRoleGroupingID = self.GetViewRoleGroupingID()
        roleGroup = self.sr.roleGroupings[viewRoleGroupingID]
        nMaxColumnIndex = len(roleGroup.columns)
        oldColumns = []
        if self.sr.columns:
            oldColumns.extend(self.sr.columns)
        self.sr.columns = [None] * (1 + nMaxColumnIndex)
        i = -1
        previousTabPosition = 0
        relevantRoles = self.GetRelevantRoles()
        try:
            for tabstop in tabstops:
                if len(self.sr.loadingTitleID) and loadingTitleID != self.sr.loadingTitleID[-1]:
                    return
                i += 1
                text, column, columnContents = '', None, []
                left = previousTabPosition + 8
                width = tabstop - previousTabPosition - 4
                if i == 0:
                    if not oldColumns or oldColumns[i] is None:
                        column = SingleLineEditText(name='titleName', parent=self, setvalue=rec.titleName, width=width - 1, left=left - 3, top=0, align=uiconst.CENTERLEFT, maxLength=100)
                        if IsContentComplianceControlSystemActive(sm.GetService('machoNet')):
                            column.SetReadOnly(True)
                            column.Disable()
                        column.OnChange = self.OnEditChange
                        columnContents.append(column)
                    else:
                        oldColumn = oldColumns[i]
                        column = oldColumn[0]
                        column.SetValue(rec.titleName)
                        column.left = left - 3
                        column.width = width - 1
                        columnContents = [column]
                        oldColumns[i] = []
                else:
                    columnNumber = i - 1
                    column = roleGroup.columns[columnNumber]
                    columnName, subColumns = column
                    controlNumber = -1
                    controlWidth = width / len(subColumns)
                    for subColumn in subColumns:
                        controlNumber += 1
                        subColumnName, role = subColumn
                        roleID = role.roleID
                        value = relevantRoles & roleID == roleID
                        if value:
                            text = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/TitleHasRoleY', corpRole=subColumnName)
                        else:
                            text = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/TitleDoesNotHaveRoleN', corpRole=subColumnName)
                        canEditRole = self.GetCanEditRole(roleID)
                        canRecycle = 0
                        checkBoxes = []
                        textControls = []
                        if oldColumns and len(oldColumns) > i and oldColumns[i] is not None and len(oldColumns[i]):
                            for column in oldColumns[i]:
                                if isinstance(column, Checkbox):
                                    checkBoxes.append(column)
                                elif isinstance(column, LabelCore):
                                    textControls.append(column)

                            checkBoxesRequired = 0
                            textControlsRequired = 0
                            if canEditRole:
                                checkBoxesRequired += 1
                            else:
                                textControlsRequired += 1
                            if checkBoxesRequired == len(checkBoxes) and textControlsRequired == len(textControls):
                                canRecycle = 1
                        if not canRecycle:
                            if canEditRole:
                                column = self.AddCheckBox(['%s' % i,
                                 roleID,
                                 subColumnName,
                                 value], self, uiconst.CENTERLEFT, controlWidth, 12, left, None)
                            else:
                                column = eveLabel.EveLabelSmall(text=text, parent=self, width=controlWidth, height=12, left=left, state=uiconst.UI_NORMAL)
                            columnContents.append(column)
                            left += controlWidth
                        else:
                            if canEditRole:
                                checkbox = checkBoxes.pop()
                                self.UpdateCheckBox(checkbox, ['%s' % i,
                                 roleID,
                                 subColumnName,
                                 value], controlWidth, 12, left)
                                columnContents.append(checkbox)
                            else:
                                textControl = textControls.pop()
                                self.UpdateTextControl(textControl, text, controlWidth, left)
                                columnContents.append(textControl)
                            left += controlWidth
                            oldColumns[i] = []
                            oldColumns[i].extend(checkBoxes)
                            oldColumns[i].extend(textControls)

                self.sr.columns[i] = columnContents
                previousTabPosition = tabstop

        finally:
            if oldColumns:
                for column in oldColumns:
                    if column is None:
                        continue
                    for control in column:
                        if control and not control.destroyed:
                            control.Close()

    def UpdateLabelText(self):
        viewRoleGroupingID = self.GetViewRoleGroupingID()
        roleGroup = self.sr.roleGroupings[viewRoleGroupingID]
        relevantRoles = self.GetRelevantRoles()
        rec = self.GetRec()
        label = rec.titleName
        headers = self.sr.node.parent.GetHeaderValues(self.GetViewRoleGroupingID())
        self.sr.node.Set('sort_%s' % headers[0], rec.titleName)
        hintList = [rec.titleName]
        for column in roleGroup.columns:
            columnName, subColumns = column
            newtext = '<t>'
            sortmask = ''
            roles = getattr(rec, roleGroup.appliesTo)
            grantableRoles = getattr(rec, roleGroup.appliesToGrantable)
            for subColumnName, role in subColumns:
                if subColumnName:
                    hintRole = '%s - %s' % (subColumnName, columnName)
                else:
                    hintRole = columnName
                isChecked = [roles, grantableRoles][self.sr.node.viewtype] & role.roleID == role.roleID
                if isChecked:
                    checkedText = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/TitleHasRole', corpRole=subColumnName)
                    hintText = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/TitleHasRoleHint', corpRole=hintRole)
                else:
                    checkedText = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/TitleDoesNotHaveRole', corpRole=subColumnName)
                    hintText = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/TitleDoesNotHaveRoleHint', corpRole=hintRole)
                newtext += checkedText
                sortmask += [' ', 'X'][not not isChecked]
                hintList.append(hintText)

            self.sr.node.Set('sort_%s' % columnName, '%s' % sortmask)
            label += newtext

        hint = '<br>'.join(hintList)
        self.hint = hint
        self.sr.node.label = label

    def GetCanEditRole(self, roleID):
        if type(roleID) == types.TupleType:
            return (self.GetCanEditRole(roleID[0]), self.GetCanEditRole(roleID[1]))
        if roleID == const.corpRoleDirector:
            return 0
        return 1

    def UpdateTextControl(self, textControl, text, width, left):
        textControl.text = text
        textControl.width = width
        textControl.left = left

    def UpdateCheckBox(self, checkbox, config, width, height, left):
        cfgname, retval, desc, default = config
        checkbox.left = left
        checkbox.width = width
        if isinstance(checkbox, RadioButton):
            checkbox.SetReturnValue(retval)
        else:
            checkbox.roleID = retval
        checkbox.SetLabel(desc)
        checkbox.SetChecked(default, report=False)
        checkbox.SetCallback(self.CheckBoxChange)
        checkbox.clipChildren = True

    def AddCheckBox(self, config, where, align, width, height, left, group):
        cfgname, retval, desc, default = config
        if group:
            return RadioButton(parent=where, text=desc, align=align, pos=(left,
             0,
             width,
             height), checked=default, callback=self.CheckBoxChange, wrapLabel=False, settingsKey=cfgname, groupname=group, retval=retval)
        else:
            cbox = Checkbox(parent=where, text=desc, align=align, pos=(left,
             0,
             width,
             height), checked=default, callback=self.CheckBoxChange, wrapLabel=False, settingsKey=cfgname)
            cbox.roleID = retval
            return cbox

    def CheckBoxChange(self, cbox, *args):
        roles = self.GetRelevantRoles()
        rec = self.GetRec()
        viewRoleGroupingID = self.GetViewRoleGroupingID()
        roleGroup = self.sr.roleGroupings[viewRoleGroupingID]
        if isinstance(cbox, RadioButton):
            roleID = cbox.GetReturnValue()
        else:
            roleID = cbox.roleID
        if cbox.GetValue():
            log.LogInfo('CheckBoxChange adding role', roleID)
            if self.sr.node.viewtype == VIEW_GRANTABLE_ROLES:
                setattr(rec, roleGroup.appliesToGrantable, getattr(rec, roleGroup.appliesToGrantable) | roleID)
            elif roleID == const.corpRoleDirector:
                raise RuntimeError('RoleDirectorInTitleMakesNoSense')
            else:
                setattr(rec, roleGroup.appliesTo, getattr(rec, roleGroup.appliesTo) | roleID)
        else:
            self.LogInfo('CheckBoxChange removing role', roleID)
            if self.sr.node.viewtype == VIEW_GRANTABLE_ROLES:
                setattr(rec, roleGroup.appliesToGrantable, getattr(rec, roleGroup.appliesToGrantable) & ~roleID)
            elif roleID == const.corpRoleDirector:
                raise RuntimeError('RoleDirectorInTitleMakesNoSense')
            else:
                setattr(rec, roleGroup.appliesTo, getattr(rec, roleGroup.appliesTo) & ~roleID)
        self.UpdateLabelText()

    def OnEditChange(self, updatedText):
        self.LogInfo('OnEditChange', updatedText)
        if self.sr.columns:
            if len(self.sr.columns):
                if self.sr.columns[0] is not None and len(self.sr.columns[0]):
                    rec = self.GetRec()
                    rec.titleName = StripTags(updatedText, stripOnly=['font', 'fontsize', 'br'])
