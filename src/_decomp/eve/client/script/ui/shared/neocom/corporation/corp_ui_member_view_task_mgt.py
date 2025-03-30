#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\corp_ui_member_view_task_mgt.py
import carbon.client.script.util.lg as lg
import localization
from carbonui import TextColor, uiconst
from carbonui.control.combo import Combo
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control import eveLabel, eveScroll
from carbonui.control.button import Button
from eve.client.script.ui.control.entries.button import ButtonEntry
from eve.client.script.ui.control.entries.util import GetFromClass
from carbonui.control.tabGroup import TabGroup
from eve.client.script.ui.shared.neocom.corporation.entries import TwoButtons
from eve.common.script.sys import idCheckers
from eve.common.script.util.eveFormat import FmtISK
from evecorporation.roles import get_role_name, iter_role_names
from eve.common.lib import appConst as const

class CorpMembersViewTaskManagement(Container):
    __guid__ = 'form.CorpMembersViewTaskManagement'
    __nonpersistvars__ = []

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.memberIDs = []
        self.wndTabs = None
        self.wndAction = None
        self.wndTargets = None
        self.targetIDs = []
        self.noneTargetIDs = []
        self.scrollTargets = None
        self.scrollNoneTargets = None
        self.titles = sm.GetService('corp').GetTitles()
        self.propertyControls = {}
        self.locationalRoles = sm.GetService('corp').GetLocationalRoles()
        self.currentlyEditing = None
        self.verbList = [[localization.GetByLabel('UI/Commands/AddItem'), const.CTV_ADD],
         [localization.GetByLabel('UI/Commands/Remove'), const.CTV_REMOVE],
         [localization.GetByLabel('UI/Common/CommandSet'), const.CTV_SET],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Give'), const.CTV_GIVE]]
        self.propertyList = [[localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Role'), 'roles'],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/RoleAtHQ'), 'rolesAtHQ'],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/RoleAtBase'), 'rolesAtBase'],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/RoleAtOther'), 'rolesAtOther'],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/GrantableRole'), 'grantableRoles'],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/GrantableRoleAtHQ'), 'grantableRolesAtHQ'],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/GrantableRoleAtBase'), 'grantableRolesAtBase'],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/GrantableRoleAtOther'), 'grantableRolesAtOther'],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Base'), 'baseID'],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Cash'), const.CTPG_CASH],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Shares'), const.CTPG_SHARES],
         [localization.GetByLabel('UI/Corporations/Common/Title'), 'titleMask']]
        self.bitmaskablesList = [[localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Role'), 'roles'],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/RoleAtHQ'), 'rolesAtHQ'],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/RoleAtBase'), 'rolesAtBase'],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/RoleAtOther'), 'rolesAtOther'],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/GrantableRole'), 'grantableRoles'],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/GrantableRoleAtHQ'), 'grantableRolesAtHQ'],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/GrantableRoleAtBase'), 'grantableRolesAtBase'],
         [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/GrantableRoleAtOther'), 'grantableRolesAtOther'],
         [localization.GetByLabel('UI/Corporations/Common/Title'), 'titleMask']]
        self.setList = [[localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Base'), 'baseID']]
        self.giveList = [[localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Cash'), const.CTPG_CASH], [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Shares'), const.CTPG_SHARES]]
        self.optionsByVerb = {const.CTV_ADD: self.bitmaskablesList,
         const.CTV_REMOVE: self.bitmaskablesList,
         const.CTV_SET: self.setList,
         const.CTV_GIVE: self.giveList}
        self.controlsByProperty = {'roles': 'role_picker',
         'rolesAtHQ': 'role_picker_locational',
         'rolesAtBase': 'role_picker_locational',
         'rolesAtOther': 'role_picker_locational',
         'grantableRoles': 'role_picker',
         'grantableRolesAtHQ': 'role_picker_locational',
         'grantableRolesAtBase': 'role_picker_locational',
         'grantableRolesAtOther': 'role_picker_locational',
         'baseID': 'location_picker',
         const.CTPG_CASH: 'isk_amount_picker',
         const.CTPG_SHARES: 'share_amount_picker',
         'titleMask': 'title_picker'}

    def LogInfo(self, *args):
        lg.Info(self.__guid__, *args)

    def CreateWindow(self):
        self.LogInfo('CreateWindow')
        self.wndTabs = TabGroup(name='tabparent', parent=self, idx=0)
        self.wndTabs.Startup([[localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Actions'),
          self,
          self,
          'actions'], [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Targets'),
          self,
          self,
          'targets']], 'taskManagement')
        self.Load('actions')

    def CreateActionWindow(self):
        self.wndAction = Container(name='wndAction', parent=self, align=uiconst.TOALL)
        self.wndSearchBuilderToolbar = Container(name='searchtoolbar', parent=self.wndAction, align=uiconst.TOTOP, height=32, padTop=8)
        combo = Combo(label='', parent=self.wndSearchBuilderToolbar, options=self.verbList, name='verb', callback=self.OnComboChange, width=90, pos=(0, 0, 0, 0), align=uiconst.TOLEFT)
        self.comboVerb = combo
        combo = Combo(label='', parent=self.wndSearchBuilderToolbar, options=self.bitmaskablesList, name='property', callback=self.OnComboChange, width=146, pos=(const.defaultPadding,
         0,
         0,
         0), align=uiconst.TOLEFT)
        self.comboProperty = combo
        wndInputControlArea = Container(name='inputArea', parent=self.wndSearchBuilderToolbar, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        self.wndInputFieldArea = wndInputControlArea
        self.ShowAppropriateInputField()
        self.ConstructActionEditButtons()
        self.scrollQuery = eveScroll.Scroll(name='queryinput', parent=self.wndAction, align=uiconst.TOALL, padTop=8)
        wndButtonBar = Container(name='execute', parent=self.wndAction, align=uiconst.TOBOTTOM, height=32, idx=0)
        button = Button(parent=wndButtonBar, label=localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/CommitActionsOnTargets'), align=uiconst.CENTER, func=self.ExecuteActions, btn_default=0)
        self.UpdateActionsTabLabel()

    def UpdateQueryScrollNoContentHint(self):
        if self.scrollQuery.GetNodes():
            hint = None
        else:
            hint = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/HintActionTargetRelation')
        self.scrollQuery.ShowHint(hint)

    def ConstructActionEditButtons(self):
        wndAddButtonContainer = ContainerAutoSize(name='sidepar', parent=self.wndSearchBuilderToolbar, align=uiconst.TORIGHT, width=104)
        self.addEditButton = Button(parent=wndAddButtonContainer, label=localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/AddAction'), func=self.AddSearchTerm, btn_default=0, align=uiconst.TORIGHT, padLeft=2)
        self.saveEditButton = Button(parent=wndAddButtonContainer, label=localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Save'), func=self.SaveEditedSearchTerm, btn_default=0, align=uiconst.TORIGHT, padLeft=2)
        self.cancelEditButton = Button(parent=wndAddButtonContainer, label=localization.GetByLabel('UI/Commands/Cancel'), func=self.CancelEditedSearchTerm, btn_default=0, align=uiconst.TORIGHT)
        wndAddButtonContainer.width = self.cancelEditButton.left + self.cancelEditButton.width
        self.saveEditButton.state = uiconst.UI_HIDDEN
        self.cancelEditButton.state = uiconst.UI_HIDDEN

    def ExecuteActions(self, *args):
        self.LogInfo('ExecuteActions args:', args)
        actions = []
        for entry in self.scrollQuery.GetNodes():
            verb = entry.verb
            property = entry.property
            value = entry.value
            actions.append([verb, property, value])

        sm.GetService('corp').ExecuteActions(self.targetIDs, actions)

    def MakeLabel(self, verb, property, value):
        label = None
        labelVerb = None
        labelProperty = None
        currentControlType = self.controlsByProperty[property]
        for displayText, fieldName in self.verbList:
            if verb == fieldName:
                labelVerb = displayText
                break

        for displayText, fieldName in self.propertyList:
            if property == fieldName:
                labelProperty = displayText
                break

        if currentControlType in ('role_picker', 'role_picker_locational'):
            label = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/TaskMgt/TextRecord', verb=labelVerb, property=labelProperty, value=get_role_name(value))
        elif currentControlType == 'title_picker':
            for title in self.titles.itervalues():
                if title.titleID == value:
                    label = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/TaskMgt/TextRecord', verb=labelVerb, property=labelProperty, value=title.titleName)
                    break

        elif currentControlType == 'location_picker':
            if value is None:
                label = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/TaskMgt/LocationRecordWithNone', verb=labelVerb, property=labelProperty)
            else:
                label = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/TaskMgt/LocationRecord', verb=labelVerb, property=labelProperty, station=value)
        elif currentControlType == 'isk_amount_picker':
            label = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/TaskMgt/CashRecord', verb=labelVerb, property=labelProperty, cash=FmtISK(value))
        elif currentControlType == 'share_amount_picker':
            label = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/TaskMgt/SharesRecord', verb=labelVerb, property=labelProperty, shares=value)
        elif currentControlType == 'date_picker':
            label = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/TaskMgt/DateRecord', verb=labelVerb, property=labelProperty, dateValue=value)
        return label

    def AddSearchTerm(self, *args):
        try:
            self.LogInfo('AddSearchTerm')
            sm.GetService('loading').Cycle('Loading')
            verb = self.comboVerb.GetValue()
            property = self.comboProperty.GetValue()
            value = None
            if self.propertyControls.has_key('current'):
                currentControlType = self.propertyControls['current']
                if currentControlType is not None:
                    currentControl = self.propertyControls[currentControlType]
                    value = currentControl.GetValue()
            self.LogInfo('verb: ', verb)
            self.LogInfo('property: ', property)
            self.LogInfo('value: ', value)
            label = self.MakeLabel(verb, property, value)
            control = GetFromClass(TwoButtons, {'label': label,
             'caption1': localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Edit'),
             'caption2': localization.GetByLabel('UI/Commands/Remove'),
             'OnClick1': self.OnClickEdit,
             'OnClick2': self.OnClickRemove,
             'args1': label,
             'args2': label,
             'verb': verb,
             'property': property,
             'value': value})
            self.scrollQuery.AddEntries(-1, [control])
            self.UpdateActionsTabLabel()
        finally:
            sm.GetService('loading').StopCycle()

    def SaveEditedSearchTerm(self, *args):
        if self.currentlyEditing is None:
            return
        verb = self.comboVerb.GetValue()
        property = self.comboProperty.GetValue()
        value = None
        if self.propertyControls.has_key('current'):
            currentControlType = self.propertyControls['current']
            if currentControlType is not None:
                currentControl = self.propertyControls[currentControlType]
                value = currentControl.GetValue()
        entry = self.currentlyEditing
        label = self.MakeLabel(verb, property, value)
        entry.panel.label = label
        entry.panel.sr.label.text = label
        entry.label = label
        entry.args1 = label
        entry.args2 = label
        entry.verb = verb
        entry.property = property
        entry.value = value
        self.currentlyEditing = None
        self.addEditButton.state = uiconst.UI_NORMAL
        self.saveEditButton.state = uiconst.UI_HIDDEN
        self.cancelEditButton.state = uiconst.UI_HIDDEN

    def CancelEditedSearchTerm(self, *args):
        self.addEditButton.state = uiconst.UI_NORMAL
        self.saveEditButton.state = uiconst.UI_HIDDEN
        self.cancelEditButton.state = uiconst.UI_HIDDEN

    def OnClickEdit(self, args, button):
        entry = self.GetEntryByLabel(args)
        if entry is None:
            raise RuntimeError('MissingEntry')
        self.currentlyEditing = entry
        verb = entry.verb
        property = entry.property
        value = entry.value
        self.comboVerb.SelectItemByValue(verb)
        self.comboProperty.LoadOptions(self.optionsByVerb[verb])
        self.comboProperty.SelectItemByValue(property)
        self.ShowAppropriateInputField()
        currentControlType = self.propertyControls['current']
        if currentControlType is not None:
            currentControl = self.propertyControls[currentControlType]
            if getattr(currentControl, 'SelectItemByValue', None):
                currentControl.SelectItemByValue(value)
            elif getattr(currentControl, 'SetValue', None):
                currentControl.SetValue(value)
        self.addEditButton.state = uiconst.UI_HIDDEN
        self.saveEditButton.state = uiconst.UI_NORMAL
        self.cancelEditButton.state = uiconst.UI_NORMAL

    def OnClickRemove(self, args, button):
        entry = self.GetEntryByLabel(args)
        if entry is None:
            raise RuntimeError('MissingEntry')
        self.scrollQuery.RemoveEntries([entry])
        self.UpdateActionsTabLabel()
        self.addEditButton.state = uiconst.UI_NORMAL
        self.saveEditButton.state = uiconst.UI_HIDDEN
        self.cancelEditButton.state = uiconst.UI_HIDDEN

    def GetEntryByLabel(self, label):
        for entry in self.scrollQuery.GetNodes():
            if entry.label == label:
                return entry

    def OnComboChange(self, entry, header, value, *args):
        if entry.name == 'verb':
            self.comboProperty.LoadOptions(self.optionsByVerb[self.comboVerb.GetValue()])
            self.ShowAppropriateInputField()
        elif entry.name == 'property':
            self.ShowAppropriateInputField()

    def ShowAppropriateInputField(self):
        currentProperty = self.comboProperty.GetValue()
        requestedControlType = self.controlsByProperty[currentProperty]
        currentControlType = None
        if self.propertyControls.has_key('current'):
            currentControlType = self.propertyControls['current']
            if currentControlType == requestedControlType:
                return
        requestedControl = None
        if self.propertyControls.has_key(requestedControlType):
            requestedControl = self.propertyControls[requestedControlType]
        elif requestedControlType == 'role_picker':
            optionsList = []
            for roleID, roleName in sorted(iter_role_names(), key=lambda r: r[1]):
                if roleID not in self.locationalRoles:
                    optionsList.append([roleName, roleID])

            requestedControl = Combo(label='', parent=self.wndInputFieldArea, options=optionsList, name=requestedControlType, width=146, pos=(const.defaultPadding,
             0,
             0,
             0), align=uiconst.TOLEFT)
        elif requestedControlType == 'title_picker':
            optionsList = []
            for title in self.titles.itervalues():
                optionsList.append([title.titleName, title.titleID])

            requestedControl = Combo(label='', parent=self.wndInputFieldArea, options=optionsList, name=requestedControlType, width=146, pos=(const.defaultPadding,
             0,
             0,
             0), align=uiconst.TOLEFT)
        elif requestedControlType == 'role_picker_locational':
            optionsList = []
            for roleID, roleName in sorted(iter_role_names(), key=lambda r: r[1]):
                if roleID in self.locationalRoles:
                    optionsList.append([roleName, roleID])

            requestedControl = Combo(label='', parent=self.wndInputFieldArea, options=optionsList, name=requestedControlType, width=146, pos=(const.defaultPadding,
             0,
             0,
             0), align=uiconst.TOLEFT)
        elif requestedControlType == 'location_picker':
            bases = [('-', None)]
            for office in sm.GetService('officeManager').GetMyCorporationsOffices():
                if idCheckers.IsStation(office.stationID):
                    bases.append((cfg.evelocations.Get(office.stationID).locationName, office.stationID))

            requestedControl = Combo(label='', parent=self.wndInputFieldArea, options=bases, name=requestedControlType, width=146, pos=(const.defaultPadding,
             0,
             0,
             0), align=uiconst.TOLEFT)
        elif requestedControlType == 'isk_amount_picker':
            requestedControl = SingleLineEditInteger(name='edit', parent=self.wndInputFieldArea, minValue=1, width=146, left=8, align=uiconst.TOLEFT)
        elif requestedControlType == 'share_amount_picker':
            requestedControl = SingleLineEditInteger(name='edit', parent=self.wndInputFieldArea, minValue=1, width=146, left=8, align=uiconst.TOLEFT)
        elif requestedControlType == None:
            requestedControl = None
        else:
            raise RuntimeError('UnexpectedControlTypeRequested')
        if currentControlType is not None and self.propertyControls.has_key(currentControlType):
            currentControl = self.propertyControls[currentControlType]
            currentControl.state = uiconst.UI_HIDDEN
        if requestedControl is not None:
            requestedControl.state = uiconst.UI_NORMAL
        self.propertyControls[requestedControlType] = requestedControl
        self.propertyControls['current'] = requestedControlType

    def CreateTargetsWindow(self):
        self.wndTargets = Container(name='wndTargets', parent=self)
        eveLabel.EveLabelMedium(text=localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/SelectMembersYouWantToTarget'), parent=self.wndTargets, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        eveLabel.EveLabelMedium(text=localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/TargetTheseMembers'), parent=self.wndTargets, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, color=TextColor.HIGHLIGHT)
        self.scrollTargets = eveScroll.Scroll(name='targets', parent=self.wndTargets, height=0.4, align=uiconst.TOTOP_PROP)
        eveLabel.EveLabelMedium(text=localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/DoNotTargetTheseMembers'), parent=self.wndTargets, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, color=TextColor.HIGHLIGHT)
        self.scrollNoneTargets = eveScroll.Scroll(name='noneTargets', parent=self.wndTargets, align=uiconst.TOALL)
        self.UpdateTargetsTabLabel()

    def Load(self, panel_id, *args):
        if panel_id == 'actions':
            if self.wndAction is None:
                self.CreateActionWindow()
            self.wndAction.state = uiconst.UI_NORMAL
            if self.wndTargets is not None:
                self.wndTargets.state = uiconst.UI_HIDDEN
            self.UpdateActionsTabLabel()
        elif panel_id == 'targets':
            if self.wndTargets is None:
                self.CreateTargetsWindow()
                self.LoadTargets()
            self.wndTargets.state = uiconst.UI_NORMAL
            if self.wndAction is not None:
                self.wndAction.state = uiconst.UI_HIDDEN
            self.UpdateTargetsTabLabel()

    def PopulateView(self, memberIDs = None):
        if memberIDs is not None:
            self.memberIDs = memberIDs
            self.targetIDs = memberIDs
        if self.wndTargets is not None:
            self.LoadTargets()
        self.UpdateActionsTabLabel()
        self.UpdateTargetsTabLabel()

    def LoadTargets(self):
        self.targetIDs = []
        self.noneTargetIDs = []
        scrolllist = []
        for memberID in self.memberIDs:
            self.targetIDs.append(memberID)
            scrolllist.append(self.GetRemoveEntry(memberID))

        self.scrollTargets.Load(None, scrolllist, noContentHint=localization.GetByLabel('UI/Wallet/WalletWindow/SearchNoResults'))
        self.scrollNoneTargets.Load(None, [])
        self.UpdateTargetsTabLabel()

    def GetRemoveEntry(self, memberID):
        data = {'label': cfg.eveowners.Get(memberID).ownerName,
         'caption': localization.GetByLabel('UI/Commands/Remove'),
         'OnClick': self.OnRemove,
         'args': (memberID,)}
        return GetFromClass(ButtonEntry, data)

    def UpdateActionsTabLabel(self):
        if self.wndTabs is not None:
            actionsTabName = '%s_tab' % localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Actions')
            actionsLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/ActionsTabLabel', numberOfActions=len(self.scrollQuery.GetNodes()))
            self.wndTabs.sr.Get(actionsTabName, None).SetLabel(actionsLabel)
        self.UpdateQueryScrollNoContentHint()

    def UpdateTargetsTabLabel(self):
        if self.wndTabs is not None:
            targetsTabName = '%s_tab' % localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Targets')
            targetsLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/TargetsTabLabel', targetCount=len(self.targetIDs), nonTargetCount=len(self.noneTargetIDs))
            self.wndTabs.sr.Get(targetsTabName, None).SetLabel(targetsLabel)

    def OnRemove(self, memberID, button):
        self.LogInfo('OnRemove memberID:', memberID)
        control = GetFromClass(ButtonEntry, {'label': cfg.eveowners.Get(memberID).ownerName,
         'caption': localization.GetByLabel('UI/Commands/AddItem'),
         'OnClick': self.OnAdd,
         'args': (memberID,)})
        self.scrollNoneTargets.AddEntries(-1, [control])
        self.targetIDs.remove(memberID)
        self.noneTargetIDs.append(memberID)
        entry = self.GetEntryByArgs(self.scrollTargets, (memberID,))
        self.scrollTargets.RemoveEntries([entry])
        self.UpdateTargetsTabLabel()

    def OnAdd(self, memberID, button):
        self.LogInfo('OnAdd memberID:', memberID)
        control = self.GetRemoveEntry(memberID)
        self.scrollTargets.AddEntries(-1, [control])
        self.targetIDs.append(memberID)
        self.noneTargetIDs.remove(memberID)
        entry = self.GetEntryByArgs(self.scrollNoneTargets, (memberID,))
        self.scrollNoneTargets.RemoveEntries([entry])
        self.UpdateTargetsTabLabel()

    def GetEntryByArgs(self, scroll, args):
        for entry in scroll.GetNodes():
            if entry.args == args:
                return entry
