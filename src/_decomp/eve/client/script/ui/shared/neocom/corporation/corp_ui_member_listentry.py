#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\corp_ui_member_listentry.py
import sys
import types
import blue
import uthread
import carbon.client.script.util.lg as lg
import log
from carbon.common.script.sys.row import Row
from carbonui import uiconst
from carbonui.control.combo import Combo
from carbonui.control.label import LabelCore
from eve.client.script.ui.control import eveLabel
from carbonui.control.checkbox import Checkbox
from carbonui.control.radioButton import RadioButton
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.services.corporation import corp_util
from eve.client.script.ui.services.corporation.corp_util import VIEW_GRANTABLE_ROLES, VIEW_ROLES, VIEW_TITLES
from eve.common.lib import appConst as const
from eve.common.script.sys import idCheckers
from eveservices.menu import GetMenuService

class CorpMemberRoleEntry(Generic):
    __guid__ = 'listentry.CorpMemberRoleEntry'
    __nonpersistvars__ = []
    __params__ = ['rec',
     'srcRec',
     'viewtype',
     'rolegroup']

    def Startup(self, *etc):
        self.sr.originalChildren = []
        Generic.Startup(self, *etc)
        self.sr.columns = []
        self.sr.roleGroupings = sm.GetService('corp').GetRoleGroupings()
        for childControl in self.children:
            self.sr.originalChildren.append(childControl)

        self.sr.loadingCharacterID = []
        self.sr.lock = None
        self.sr.rowHeader = ['characterID',
         'name',
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
         'baseID',
         'oldBaseID',
         'titleMask',
         'oldTitleMask',
         'isCEO',
         'isDirector',
         'IAmCEO',
         'IAmDirector']
        self.sr.bases = [('-', None)]
        for office in sm.GetService('officeManager').GetMyCorporationsOffices():
            if idCheckers.IsStation(office.stationID):
                self.sr.bases.append((cfg.evelocations.Get(office.stationID).locationName, office.stationID))

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

    def GetViewType(self):
        return self.sr.node.parent.sr.viewType

    def GetTabStops(self):
        return self.sr.node.parent.tabstops

    def GetRelevantRoles(self):
        viewRoleGroupingID = self.GetViewRoleGroupingID()
        if self.GetViewType() == VIEW_ROLES:
            roleGroup = self.sr.roleGroupings[viewRoleGroupingID]
            return getattr(self.GetRec(), roleGroup.appliesTo)
        if self.GetViewType() == VIEW_GRANTABLE_ROLES:
            roleGroup = self.sr.roleGroupings[viewRoleGroupingID]
            return getattr(self.GetRec(), roleGroup.appliesToGrantable)
        if self.GetViewType() == VIEW_TITLES:
            return self.GetRec().titleMask
        raise RuntimeError('NoSuchRoleType')

    def GetRelevantChange(self, change):
        viewRoleGroupingID = self.GetViewRoleGroupingID()
        if self.GetViewType() == VIEW_ROLES:
            roleGroup = self.sr.roleGroupings[viewRoleGroupingID]
            return change[roleGroup.appliesTo]
        if self.GetViewType() == VIEW_GRANTABLE_ROLES:
            roleGroup = self.sr.roleGroupings[viewRoleGroupingID]
            return change[roleGroup.appliesToGrantable]
        if self.GetViewType() == VIEW_TITLES:
            return change['titleMask']
        raise RuntimeError('NoSuchRoleType')

    def GetHeight(self, *args):
        node, width = args
        node.height = 34
        return node.height

    def GetRec(self):
        return self.sr.node.rec

    def LogInfo(self, *args):
        lg.Info('listentry.CorpMemberRoleEntry', *args)

    def LogError(self, *args):
        lg.Error('listentry.CorpMemberRoleEntry', *args)

    def Load(self, node):
        try:
            self.Lock()
            s = blue.os.GetWallclockTimeNow()
            Generic.Load(self, node)
            grantableRoles, grantableRolesAtHQ, grantableRolesAtBase, grantableRolesAtOther = sm.GetService('corp').GetMyGrantableRoles()
            self.sr.grantableRoles = grantableRoles
            self.sr.grantableRolesAtHQ = grantableRolesAtHQ
            self.sr.grantableRolesAtBase = grantableRolesAtBase
            self.sr.grantableRolesAtOther = grantableRolesAtOther
            self.sr.baseID = sm.GetService('corp').GetMember(eve.session.charid).baseID
            loadingCharacterID = node.srcRec.characterID
            self.sr.loadingCharacterID.append(loadingCharacterID)
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
                if self.sr.node.rec is None or self.sr.node.rec.characterID != node.srcRec.characterID:
                    self.sr.node = node
                    self.GetMembersListData()
                if 0 == len(self.sr.loadingCharacterID) or loadingCharacterID != self.sr.loadingCharacterID[-1]:
                    return
            finally:
                self.LogInfo('Load 1 took %s ms.' % blue.os.TimeDiffInMs(s, blue.os.GetWallclockTimeNow()))
                self.Unlock()

            try:
                self.Lock()
                s = blue.os.GetWallclockTimeNow()
                if self.sr.node is None:
                    return
                self.LoadColumns(loadingCharacterID)
                if 0 == len(self.sr.loadingCharacterID) or loadingCharacterID != self.sr.loadingCharacterID[-1]:
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
            if loadingCharacterID in self.sr.loadingCharacterID:
                self.sr.loadingCharacterID.remove(loadingCharacterID)

        self.state = uiconst.UI_NORMAL
        self.sr.label.Update()
        self.sr.label.Hide()

    def DataChanged(self, primaryKey, change):
        self.LogInfo('----------------------------------------------')
        self.LogInfo('DataChanged')
        self.LogInfo('primaryKey:', primaryKey)
        self.LogInfo('change:', change)
        self.LogInfo('----------------------------------------------')
        if change.has_key('corporationID') and change['corporationID'][1] == None:
            self.LogError('memberListEntry should have been removed for charID:', primaryKey)
            return
        self.GetMembersListData()
        self.UpdateLabelText()
        viewRoleGroupingID = self.GetViewRoleGroupingID()
        viewType = self.GetViewType()
        if not (change.has_key('roles') and None not in change['roles'] and const.corpRoleDirector & change['roles'][0] != const.corpRoleDirector & change['roles'][1]):
            if viewType == VIEW_ROLES:
                roleGroup = self.sr.roleGroupings[viewRoleGroupingID]
                if not change.has_key(roleGroup.appliesTo):
                    self.LogInfo('DataChanged returning. Viewing roles have not changed')
                    return
            elif viewType == VIEW_GRANTABLE_ROLES:
                roleGroup = self.sr.roleGroupings[viewRoleGroupingID]
                if not change.has_key(roleGroup.appliesToGrantable):
                    self.LogInfo('DataChanged returning. Viewing grantable roles have not changed')
                    return
            elif viewType == VIEW_TITLES:
                if not change.has_key('titleMask'):
                    self.LogInfo('DataChanged returning. Viewing titles have not changed')
                    return
        else:
            return self.Load(self.sr.node)
        i = -1
        self.LogInfo('change:', change)
        old, new = self.GetRelevantChange(change)
        if old is None:
            old = 0
        if new is None:
            new = 0
        for tabstop in self.GetTabStops():
            i += 1
            if i == 0:
                continue
            if i == 1:
                if not change.has_key('baseID'):
                    continue
                column = self.sr.columns[i][0]
                baseID = change['baseID'][1]
                if isinstance(column, Combo):
                    self.UpdateComboControl(column, baseID)
                else:
                    text = '-'
                    if baseID is not None:
                        text = cfg.evelocations.Get(baseID).locationName
                    self.UpdateTextControl(column, text, column.width, column.left)
                continue
            columnNumber = i - 2
            if viewType in (VIEW_ROLES, VIEW_GRANTABLE_ROLES):
                roleGroup = self.sr.roleGroupings[viewRoleGroupingID]
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
                    text = '[%s]' % ['N', 'Y'][value]
                    if isinstance(control, Checkbox):
                        self.LogInfo('Updating checkbox')
                        checked = control.GetValue()
                        if checked == value:
                            control.SetLabelText(subColumnName)
                            continue
                        control.SetLabelText(subColumnName + ' ' + text)
                    else:
                        self.LogInfo('Updating text control')
                        control.text = text + ' ' + subColumnName

            elif viewType == VIEW_TITLES:
                titlesByID = sm.GetService('corp').GetTitles()
                nextTitleID = 1
                for ix in range(0, len(titlesByID)):
                    titleID = nextTitleID
                    title = titlesByID[titleID]
                    nextTitleID = nextTitleID << 1
                    if ix != columnNumber:
                        continue
                    if (old & titleID == titleID) == (new & titleID == titleID):
                        continue
                    control = self.sr.columns[i][0]
                    value = self.GetRelevantRoles() & titleID == titleID
                    text = '[%s]' % ['N', 'Y'][value]
                    if isinstance(control, Checkbox):
                        checked = control.GetValue()
                        if checked != value:
                            control.SetValue(value)
                    else:
                        control.text = text

            else:
                raise RuntimeError('UnknownViewType')

    def GetMembersListData(self):
        corporation = sm.GetService('corp').GetCorporation()
        IAmCEO = corporation.ceoID == eve.session.charid
        IAmDirector = [eve.session.corprole & const.corpRoleDirector, 0][IAmCEO]
        member = self.sr.node.srcRec
        roles = member.roles
        grantableRoles = member.grantableRoles
        rolesAtHQ = member.rolesAtHQ
        grantableRolesAtHQ = member.grantableRolesAtHQ
        rolesAtBase = member.rolesAtBase
        grantableRolesAtBase = member.grantableRolesAtBase
        rolesAtOther = member.rolesAtOther
        grantableRolesAtOther = member.grantableRolesAtOther
        baseID = member.baseID
        titleMask = member.titleMask
        isCEO = 0
        isDirector = 0
        isCEO = member.characterID == corporation.ceoID
        isDirector = roles & const.corpRoleDirector == const.corpRoleDirector
        if isCEO or isDirector:
            roles = 0
            for roleGrouping in self.sr.roleGroupings.itervalues():
                appliesTo = roleGrouping.appliesTo
                appliesToGrantable = roleGrouping.appliesToGrantable
                if appliesTo == 'roles':
                    roles |= roleGrouping.roleMask
                elif appliesTo == 'rolesAtHQ':
                    rolesAtHQ |= roleGrouping.roleMask
                elif appliesTo == 'rolesAtBase':
                    rolesAtBase |= roleGrouping.roleMask
                elif appliesTo == 'rolesAtOther':
                    rolesAtOther |= roleGrouping.roleMask
                if appliesToGrantable == 'grantableRoles':
                    grantableRoles |= roleGrouping.roleMask
                elif appliesToGrantable == 'grantableRolesAtHQ':
                    grantableRolesAtHQ |= roleGrouping.roleMask
                elif appliesToGrantable == 'grantableRolesAtBase':
                    grantableRolesAtBase |= roleGrouping.roleMask
                elif appliesToGrantable == 'grantableRolesAtOther':
                    grantableRolesAtOther |= roleGrouping.roleMask

            if isDirector:
                grantableRoles = grantableRoles & ~const.corpRoleDirector
        oldBaseID = baseID
        if oldBaseID is not None:
            oldBaseID = long(baseID)
        line = [member.characterID,
         cfg.eveowners.Get(member.characterID).ownerName,
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
         baseID,
         oldBaseID,
         titleMask,
         int(titleMask),
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
        self.LoadColumns(rec.characterID)

    def LoadColumns(self, loadingCharacterID):
        if len(self.sr.loadingCharacterID) and loadingCharacterID != self.sr.loadingCharacterID[-1]:
            return
        data = self.sr.node
        tabstops = self.GetTabStops()
        viewtype = self.GetViewType()
        nMaxColumnIndex = 0
        rec = self.GetRec()
        viewRoleGroupingID = self.GetViewRoleGroupingID()
        if viewtype in (VIEW_ROLES, VIEW_GRANTABLE_ROLES):
            roleGroup = self.sr.roleGroupings[viewRoleGroupingID]
            nMaxColumnIndex = len(roleGroup.columns)
        else:
            titles = sm.GetService('corp').GetTitles()
            nMaxColumnIndex = len(titles)
        oldColumns = []
        if self.sr.columns:
            oldColumns.extend(self.sr.columns)
        self.sr.columns = [None] * (2 + nMaxColumnIndex)
        align = uiconst.CENTERLEFT
        height = 16
        maxHeight = 0
        i = -1
        previousTabPosition = 0
        relevantRoles = self.GetRelevantRoles()
        try:
            for tabstop in tabstops:
                if len(self.sr.loadingCharacterID) and loadingCharacterID != self.sr.loadingCharacterID[-1]:
                    return
                i += 1
                text, column, columnContents = '', None, []
                left = previousTabPosition + 4
                width = tabstop - previousTabPosition - 4
                if i == 0:
                    if not oldColumns or oldColumns[i] is None:
                        column = eveLabel.EveLabelMedium(text=rec.name, parent=self, width=width, left=left, state=uiconst.UI_DISABLED, maxLines=1, align=align)
                        maxHeight = max(maxHeight, column.textheight)
                        columnContents.append(column)
                    else:
                        oldColumn = oldColumns[i]
                        column = oldColumn[0]
                        self.UpdateTextControl(column, rec.name, width, left)
                        columnContents = [column]
                        oldColumns[i] = []
                elif i == 1:
                    canEditBase = corp_util.CanEditBase(rec.isCEO, rec.IAmCEO, rec.IAmDirector)
                    canRecycle = 0
                    comboBoxes = []
                    textControls = []
                    if oldColumns and len(oldColumns) > i and oldColumns[i] is not None and len(oldColumns[i]):
                        for column in oldColumns[i]:
                            if isinstance(column, Combo):
                                comboBoxes.append(column)
                            elif isinstance(column, LabelCore):
                                textControls.append(column)

                        comboBoxesRequired = 0
                        textControlsRequired = 0
                        if canEditBase:
                            comboBoxesRequired += 1
                        else:
                            textControlsRequired += 1
                        if comboBoxesRequired == len(comboBoxes) and textControlsRequired == len(textControls):
                            canRecycle = 0
                    if not canRecycle:
                        if canEditBase:
                            s = blue.os.GetWallclockTimeNow()
                            bFound = 0
                            bases = []
                            bases.extend(self.sr.bases)
                            for locationName, locationID in self.sr.bases:
                                if locationID == rec.baseID:
                                    bFound = 1

                            if bFound == 0:
                                bases.append(('! ' + cfg.evelocations.Get(rec.baseID).locationName, rec.baseID))
                            column = Combo(label='', parent=self, options=bases, name='baseID', select=rec.baseID, width=width - 7, pos=(left,
                             0,
                             0,
                             0), align=align, callback=self.OnComboChange)
                            self.LogInfo('Combo took %s ms.' % blue.os.TimeDiffInMs(s, blue.os.GetWallclockTimeNow()))
                            column.z = 1
                        else:
                            text = '-'
                            if rec.baseID is not None:
                                text = cfg.evelocations.Get(rec.baseID).locationName
                            column = eveLabel.EveLabelMedium(text=text, parent=self, width=width, left=left, state=uiconst.UI_DISABLED, maxLines=1, align=align)
                            maxHeight = max(maxHeight, column.textheight)
                        columnContents.append(column)
                    else:
                        if canEditBase:
                            combobox = comboBoxes.pop()
                            self.UpdateComboControl(combobox, rec.baseID, width, left)
                            columnContents.append(combobox)
                        else:
                            textControl = textControls.pop()
                            text = '-'
                            if rec.baseID is not None:
                                text = cfg.evelocations.Get(rec.baseID).locationName
                            self.UpdateTextControl(textControl, text, width, left)
                            columnContents.append(textControl)
                        oldColumns[i] = []
                        oldColumns[i].extend(comboBoxes)
                        oldColumns[i].extend(textControls)
                else:
                    columnNumber = i - 2
                    if viewtype in (VIEW_ROLES, VIEW_GRANTABLE_ROLES):
                        roleGroup = self.sr.roleGroupings[viewRoleGroupingID]
                        column = roleGroup.columns[columnNumber]
                        columnName, subColumns = column
                        controlNumber = -1
                        controlWidth = width / len(subColumns)
                        for subColumn in subColumns:
                            controlNumber += 1
                            subColumnName, role = subColumn
                            roleID = role.roleID
                            value = relevantRoles & roleID == roleID
                            text = '[%s] %s' % (['N', 'Y'][value], subColumnName)
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
                                     value], self, align, controlWidth, height, left, None)
                                    self.AddMenuDelegator(column)
                                else:
                                    column = eveLabel.EveLabelMedium(text=text, parent=self, width=controlWidth, left=left, state=uiconst.UI_DISABLED, maxLines=1, align=align)
                                    maxHeight = max(maxHeight, column.textheight)
                                columnContents.append(column)
                                left += controlWidth
                            else:
                                if canEditRole:
                                    checkbox = checkBoxes.pop()
                                    self.UpdateCheckBox(checkbox, ['%s' % i,
                                     roleID,
                                     subColumnName,
                                     value], controlWidth, height, left)
                                    columnContents.append(checkbox)
                                else:
                                    textControl = textControls.pop()
                                    self.UpdateTextControl(textControl, text, controlWidth, left)
                                    columnContents.append(textControl)
                                left += controlWidth
                                oldColumns[i] = []
                                oldColumns[i].extend(checkBoxes)
                                oldColumns[i].extend(textControls)

                    else:
                        titlesByID = sm.GetService('corp').GetTitles()
                        subColumnName = ''
                        controlWidth = width
                        titleID = 1 << columnNumber
                        title = titlesByID[titleID]
                        value = relevantRoles & titleID == titleID
                        text = '[%s] %s' % (['N', 'Y'][value], subColumnName)
                        canEditRole = self.GetCanEditRole(titleID)
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
                                 titleID,
                                 subColumnName,
                                 value], self, align, controlWidth, height, left, None)
                            else:
                                column = eveLabel.EveLabelMedium(text=text, parent=self, width=controlWidth, left=left, state=uiconst.UI_DISABLED, maxLines=1, align=align)
                                maxHeight = max(maxHeight, column.textheight)
                            columnContents.append(column)
                            left += controlWidth
                        else:
                            if canEditRole:
                                checkbox = checkBoxes.pop()
                                self.UpdateCheckBox(checkbox, ['%s' % i,
                                 titleID,
                                 subColumnName,
                                 value], controlWidth, height, left)
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
        relevantRoles = self.GetRelevantRoles()
        rec = self.GetRec()
        label = cfg.eveowners.Get(rec.characterID).ownerName
        baseID = rec.baseID
        baseName = '-'
        if baseID is not None:
            baseName = cfg.evelocations.Get(baseID).locationName
        label += '<t>%s' % baseName
        headers = self.sr.node.parent.GetHeaderValues()
        self.sr.node.Set('sort_%s' % headers[0], cfg.eveowners.Get(rec.characterID).ownerName)
        self.sr.node.Set('sort_%s' % headers[1], baseName)
        viewtype = self.GetViewType()
        viewRoleGroupingID = self.GetViewRoleGroupingID()
        if viewtype in (VIEW_ROLES, VIEW_GRANTABLE_ROLES):
            roleGroup = self.sr.roleGroupings[viewRoleGroupingID]
            for column in roleGroup.columns:
                columnName, subColumns = column
                newtext = '<t>'
                sortmask = ''
                roles = getattr(rec, roleGroup.appliesTo)
                grantableRoles = getattr(rec, roleGroup.appliesToGrantable)
                for subColumnName, role in subColumns:
                    isChecked = [roles, grantableRoles][viewtype] & role.roleID == role.roleID
                    if isChecked:
                        newtext += ' [X] %s' % subColumnName
                    else:
                        newtext += ' [ ] %s' % subColumnName
                    sortmask += [' ', 'X'][not not isChecked]

                self.sr.node.Set('sort_%s' % columnName, sortmask)
                label += newtext

        else:
            subColumnName = ''
            for title in sorted(sm.GetService('corp').GetTitles().itervalues(), key=lambda x: x.titleID):
                columnName = title.titleName
                newtext = '<t>'
                sortmask = ''
                isChecked = relevantRoles & title.titleID == title.titleID
                if isChecked:
                    newtext += ' [X] %s' % subColumnName
                else:
                    newtext += ' [ ] %s' % subColumnName
                sortmask += [' ', 'X'][not not isChecked]
                self.sr.node.Set('sort_%s' % columnName, sortmask)
                label += newtext

        self.sr.node.label = label

    def GetCanEditRole(self, roleID):
        if type(roleID) == types.TupleType:
            return (self.GetCanEditRole(roleID[0]), self.GetCanEditRole(roleID[1]))
        else:
            rec = self.GetRec()
            viewtype = self.GetViewType()
            if viewtype == VIEW_TITLES:
                if eve.session.corprole & const.corpRoleDirector == const.corpRoleDirector:
                    if rec.isCEO:
                        return rec.IAmCEO
                    if rec.isDirector:
                        return rec.IAmCEO
                    return 1
                return 0
            viewRoleGroupingID = self.GetViewRoleGroupingID()
            return corp_util.CanEditRole(roleID, viewtype == VIEW_GRANTABLE_ROLES, rec.isCEO, rec.isDirector, rec.IAmCEO, viewRoleGroupingID, self.sr.baseID, rec.baseID, self.sr.grantableRoles, self.sr.grantableRolesAtHQ, self.sr.grantableRolesAtBase, self.sr.grantableRolesAtOther)

    def UpdateTextControl(self, textControl, text, width, left):
        textControl.text = text
        textControl.width = width
        textControl.left = left

    def UpdateCheckBox(self, checkbox, config, width, height, left):
        cfgname, retval, desc, default = config
        checkbox.left = left
        checkbox.width = width
        checkbox.height = height
        checkbox.SetSettingsKey(cfgname)
        if isinstance(checkbox, RadioButton):
            checkbox.SetReturnValue(retval)
        else:
            checkbox.roleID = retval
        checkbox.label.width = width - checkbox.checkboxCont.width
        checkbox.label.text = desc
        checkbox.SetChecked(default, report=False)

    def AddCheckBox(self, config, where, align, width, height, left, group):
        cfgname, retval, desc, default = config
        if group:
            cbox = RadioButton(text=desc, parent=where, state=uiconst.UI_NORMAL, settingsKey=cfgname, retval=retval, checked=default, groupname=group, callback=self.CheckBoxChange, align=align, pos=(left,
             2,
             width,
             0))
        else:
            cbox = Checkbox(text=desc, parent=where, state=uiconst.UI_NORMAL, settingsKey=cfgname, checked=default, callback=self.CheckBoxChange, align=align, pos=(left,
             2,
             width,
             0))
            cbox.roleID = retval
        cbox.height = max(height, cbox.label.textheight + cbox.label.top)
        return cbox

    def UpdateComboControl(self, comboControl, value, width = None, left = None):
        self.LogInfo('comboControl:', comboControl)
        self.LogInfo('value:', value)
        comboControl.SelectItemByValue(value)
        if width is not None:
            comboControl.width = width
        if left is not None:
            comboControl.left = left - 4

    def OnComboChange(self, combo, header, value, *args):
        self.LogInfo('combo:', combo)
        self.LogInfo('header:', header)
        self.LogInfo('value:', value)
        if combo.name == 'baseID':
            self.GetRec().baseID = value
            self.LogInfo('Combo changed to:', value)

    def CheckBoxChange(self, cbox, *args):
        roles = self.GetRelevantRoles()
        rec = self.GetRec()
        viewtype = self.GetViewType()
        if isinstance(cbox, RadioButton):
            roleID = cbox.GetReturnValue()
        else:
            roleID = cbox.roleID
        if viewtype == VIEW_TITLES:
            titleID = roleID
            if cbox.GetValue():
                rec.titleMask |= titleID
            else:
                rec.titleMask &= ~titleID
            self.UpdateLabelText()
        else:
            viewRoleGroupingID = self.GetViewRoleGroupingID()
            roleGroup = self.sr.roleGroupings[viewRoleGroupingID]
            roleID = roleID
            if cbox.GetValue():
                if self.GetViewType() == VIEW_GRANTABLE_ROLES:
                    self.LogInfo('CheckBoxChange adding grantable role: ', roleID)
                    self.LogInfo('CheckBoxChange applies to: ', roleGroup.appliesToGrantable)
                    self.LogInfo('CheckBoxChange val before: ', getattr(rec, roleGroup.appliesToGrantable))
                    setattr(rec, roleGroup.appliesToGrantable, getattr(rec, roleGroup.appliesToGrantable) | roleID)
                    self.LogInfo('CheckBoxChange val after: ', getattr(rec, roleGroup.appliesToGrantable))
                else:
                    self.LogInfo('CheckBoxChange adding role: ', roleID)
                    self.LogInfo('CheckBoxChange applies to: ', roleGroup.appliesTo)
                    if roleID != const.corpRoleDirector:
                        self.LogInfo('CheckBoxChange val before: ', getattr(rec, roleGroup.appliesTo))
                        setattr(rec, roleGroup.appliesTo, getattr(rec, roleGroup.appliesTo) | roleID)
                        self.LogInfo('CheckBoxChange val after: ', getattr(rec, roleGroup.appliesTo))
                    else:
                        for roleGrouping in self.sr.roleGroupings.itervalues():
                            appliesTo = roleGrouping.appliesTo
                            appliesToGrantable = roleGrouping.appliesToGrantable
                            setattr(rec, appliesTo, getattr(rec, appliesTo) | roleGrouping.roleMask)
                            setattr(rec, appliesToGrantable, getattr(rec, appliesToGrantable) | roleGrouping.roleMask)

                        rec.grantableRoles = rec.grantableRoles & ~const.corpRoleDirector
            elif self.GetViewType() == VIEW_GRANTABLE_ROLES:
                self.LogInfo('CheckBoxChange removing grantable role: ', roleID)
                self.LogInfo('CheckBoxChange applies to: ', roleGroup.appliesToGrantable)
                self.LogInfo('CheckBoxChange val before: ', getattr(rec, roleGroup.appliesToGrantable))
                setattr(rec, roleGroup.appliesToGrantable, getattr(rec, roleGroup.appliesToGrantable) & ~roleID)
                self.LogInfo('CheckBoxChange val after: ', getattr(rec, roleGroup.appliesToGrantable))
            else:
                self.LogInfo('CheckBoxChange removing role: ', roleID)
                self.LogInfo('CheckBoxChange applies to: ', roleGroup.appliesTo)
                if roleID == const.corpRoleDirector:
                    rec.roles = 0
                    rec.grantableRoles = 0
                    rec.rolesAtHQ = 0
                    rec.grantableRolesAtHQ = 0
                    rec.rolesAtBase = 0
                    rec.grantableRolesAtBase = 0
                    rec.rolesAtOther = 0
                    rec.grantableRolesAtOther = 0
                else:
                    self.LogInfo('CheckBoxChange val before: ', getattr(rec, roleGroup.appliesTo))
                    setattr(rec, roleGroup.appliesTo, getattr(rec, roleGroup.appliesTo) & ~roleID)
                    self.LogInfo('CheckBoxChange val after: ', getattr(rec, roleGroup.appliesTo))
            self.UpdateLabelText()
            if roleID == const.corpRoleDirector:
                rec.isDirector = rec.roles & const.corpRoleDirector
                uthread.new(self.LoadColumns, rec.characterID)

    def AddMenuDelegator(self, control):
        if control is None or control.destroyed:
            return
        setattr(control, 'GetMenu', self.GetMenu)

    def GetMenu(self, *args):
        self.OnClick()
        return GetMenuService().CharacterMenu(self.GetRec().characterID)
