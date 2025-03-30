#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\corp_ui_member_find.py
import logging
import blue
import eveicon
import uthread
from carbon.common.script.util.format import GetTimeParts
from carbonui import uiconst
from carbonui.control.combo import Combo
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.primitives.sprite import Sprite
from carbonui.services.setting import UserSettingBool
from eve.client.script.ui.control import eveScroll
from carbonui.control.button import Button
from eve.client.script.ui.control.datepicker import DatePicker
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from carbonui.button.menu import MenuButtonIcon
from eve.client.script.ui.control.toggleButtonGroup import ToggleButtonGroup
from eve.client.script.ui.shared.neocom.corporation.corp_ui_member_view_role_mgt import CorpMembersViewRoleManagement
from eve.client.script.ui.shared.neocom.corporation.corp_ui_member_view_simple import CorpMembersViewSimple
from eve.client.script.ui.shared.neocom.corporation.corp_ui_member_view_task_mgt import CorpMembersViewTaskManagement
from eve.client.script.ui.shared.neocom.corporation.entries import TwoButtons
from eve.common.script.sys import idCheckers
from evecorporation.roles import get_role_name, iter_role_names
from eveexceptions import UserError
from localization import GetByLabel
LOGICAL_OPERATOR_OR = 1
LOGICAL_OPERATOR_AND = 2
OPERATOR_EQUAL = 1
OPERATOR_GREATER = 2
OPERATOR_GREATER_OR_EQUAL = 3
OPERATOR_LESS = 4
OPERATOR_LESS_OR_EQUAL = 5
OPERATOR_NOT_EQUAL = 6
OPERATOR_HAS_BIT = 7
OPERATOR_NOT_HAS_BIT = 8
OPERATOR_STR_CONTAINS = 9
OPERATOR_STR_LIKE = 10
OPERATOR_STR_STARTS_WITH = 11
OPERATOR_STR_ENDS_WITH = 12
OPERATOR_STR_IS = 13
logger = logging.getLogger(__name__)
LOGICAL_OPERATORS = {GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/LogicalOR'): LOGICAL_OPERATOR_OR,
 GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/LogicalAND'): LOGICAL_OPERATOR_AND}
PROPERTY_LIST = ((GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Role'), 'roles'),
 (GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/RoleAtHQ'), 'rolesAtHQ'),
 (GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/RoleAtBase'), 'rolesAtBase'),
 (GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/RoleAtOther'), 'rolesAtOther'),
 (GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/GrantableRole'), 'grantableRoles'),
 (GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/GrantableRoleAtHQ'), 'grantableRolesAtHQ'),
 (GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/GrantableRoleAtBase'), 'grantableRolesAtBase'),
 (GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/GrantableRoleAtOther'), 'grantableRolesAtOther'),
 (GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Base'), 'baseID'),
 (GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/StartDate'), 'startDateTime'),
 (GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Name'), 'characterID'),
 (GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Title'), 'titleMask'))
OPTIONS_ROLES = ((GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/RolesInclude'), OPERATOR_HAS_BIT), (GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/RolesNotInclude'), OPERATOR_NOT_HAS_BIT))
OPTIONS_LOCATIONS = ((GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/AlgebraicEqualSign'), OPERATOR_EQUAL), (GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/AlgebraicNotEqualSign'), OPERATOR_NOT_EQUAL))
OPTIONS_DATETIME = ((GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/AlgebraicEqualSign'), OPERATOR_EQUAL),
 (GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/AlgebraicGreaterThanSign'), OPERATOR_GREATER),
 (GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/AlgebraicGreaterThanOrEqualSign'), OPERATOR_GREATER_OR_EQUAL),
 (GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/AlgebraicLessThanSign'), OPERATOR_LESS),
 (GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/AlgebraicLessThanOrEqualSign'), OPERATOR_LESS_OR_EQUAL),
 (GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/AlgebraicNotEqualSign'), OPERATOR_NOT_EQUAL))
OPTIONS_STR = ((GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/ContainsRelation'), OPERATOR_STR_CONTAINS),
 (GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/LikeRelation'), OPERATOR_STR_LIKE),
 (GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/StartsWithRelation'), OPERATOR_STR_STARTS_WITH),
 (GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/EndsWithRelation'), OPERATOR_STR_ENDS_WITH),
 (GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/IsRelation'), OPERATOR_STR_IS))
OPTIONS_BY_PROPERTY = {'roles': OPTIONS_ROLES,
 'rolesAtHQ': OPTIONS_ROLES,
 'rolesAtBase': OPTIONS_ROLES,
 'rolesAtOther': OPTIONS_ROLES,
 'grantableRoles': OPTIONS_ROLES,
 'grantableRolesAtHQ': OPTIONS_ROLES,
 'grantableRolesAtBase': OPTIONS_ROLES,
 'grantableRolesAtOther': OPTIONS_ROLES,
 'baseID': OPTIONS_LOCATIONS,
 'startDateTime': OPTIONS_DATETIME,
 'characterID': OPTIONS_STR,
 'titleMask': OPTIONS_ROLES}
CONTROLS_BY_PROPERTY = {'roles': 'role_picker',
 'rolesAtHQ': 'role_picker_locational',
 'rolesAtBase': 'role_picker_locational',
 'rolesAtOther': 'role_picker_locational',
 'grantableRoles': 'role_picker',
 'grantableRolesAtHQ': 'role_picker_locational',
 'grantableRolesAtBase': 'role_picker_locational',
 'grantableRolesAtOther': 'role_picker_locational',
 'baseID': 'location_picker',
 'startDateTime': 'date_picker',
 'characterID': 'edit_control',
 'titleMask': 'title_picker'}
INCLUDE_IMPLIED_SETTING = UserSettingBool('FMBQincludeImplied', False)
SEARCH_TITLES_SETTING = UserSettingBool('FMBQsearchTitles', False)

class CorpQueryMembersForm():

    def __init__(self):
        self.memberIDs = []
        self.titles = sm.GetService('corp').GetTitles()
        self.propertyControls = {}
        self.locationalRoles = sm.GetService('corp').GetLocationalRoles()
        self.currentlyEditing = None
        self.lpfnQueryCompleted = None
        SEARCH_TITLES_SETTING.on_change.connect(self.OnQuerySettingChanged)
        INCLUDE_IMPLIED_SETTING.on_change.connect(self.OnQuerySettingChanged)

    def Load(self, parentWindow, lpfnQueryCompleted = None):
        self.lpfnQueryCompleted = lpfnQueryCompleted
        self.wndForm = ContainerAutoSize(name='topCont', parent=parentWindow, align=uiconst.TOTOP)
        self.wndSearchBuilderToolbar = ContainerAutoSize(name='wndSearchBuilderToolbar', parent=self.wndForm, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, padTop=4)
        self.ConstructCriteriaButtons()
        self.criteriaComboCont = FlowContainer(name='criteriaComboCont', parent=self.wndSearchBuilderToolbar, contentSpacing=(8, 16), align=uiconst.TOTOP)
        self.ConstructCriteriaCombos()
        self.comboOperator.OnChange = self.OnComboChange
        self.ConstructCriteriaOptionsCombos()
        self.scrollQuery = eveScroll.Scroll(name='queryinput', parent=self.wndForm, height=110, align=uiconst.TOTOP, padTop=16)
        self.CheckShowScrollNoContentHint()
        self.ConstructQueryButton()
        return self.wndForm

    def ConstructQueryButton(self):
        executeQueryCont = ContainerAutoSize(name='executeQueryCont', parent=self.wndForm, align=uiconst.TOTOP, alignMode=uiconst.CENTERTOP, padTop=16)
        Button(parent=executeQueryCont, label=GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/ExecuteQuery'), func=self.ExecuteQuery, btn_default=0, align=uiconst.CENTERTOP)
        MenuButtonIcon(parent=executeQueryCont, get_menu_func=self.GetMenuForQueryOptions, align=uiconst.CENTERRIGHT, texturePath=eveicon.settings)

    def GetMenuForQueryOptions(self):
        menuData = MenuData()
        menuData.AddCheckbox(GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/SearchTitles'), setting=SEARCH_TITLES_SETTING)
        menuData.AddCheckbox(GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/IncludeImpliedRoles'), setting=INCLUDE_IMPLIED_SETTING)
        return menuData

    def OnQuerySettingChanged(self, value):
        uthread.new(self.ExecuteQuery)

    def CheckShowScrollNoContentHint(self):
        if self.scrollQuery.GetNodes():
            hint = None
        else:
            hint = GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/NoQueryCriteryAdded')
        self.scrollQuery.ShowHint(hint)

    def ConstructCriteriaCombos(self):
        optionsList = ((GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/LogicalOR'), LOGICAL_OPERATOR_OR), (GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/LogicalAND'), LOGICAL_OPERATOR_AND))
        self.comboJoinOperator = Combo(label='', parent=self.criteriaComboCont, options=optionsList, name='join_operator', callback=self.OnComboChange, width=70, align=uiconst.NOALIGN, state=uiconst.UI_HIDDEN)
        self.comboProperty = Combo(label='', parent=self.criteriaComboCont, options=PROPERTY_LIST, name='property', callback=self.OnComboChange, width=128, align=uiconst.NOALIGN)
        self.comboOperator = Combo(label='', parent=self.criteriaComboCont, options=OPTIONS_BY_PROPERTY[self.comboProperty.GetValue()], name='operator', callback=self.OnComboChange, width=80, align=uiconst.NOALIGN)

    def ConstructCriteriaButtons(self):
        criteriaButtonCont = ContainerAutoSize(parent=self.wndSearchBuilderToolbar, align=uiconst.TORIGHT)
        buttonCont = ContainerAutoSize(parent=criteriaButtonCont, align=uiconst.TOPRIGHT, height=Button.default_height)
        self.addEditButton = Button(parent=buttonCont, label=GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/AddCriteria'), func=self.AddSearchTerm, btn_default=0, align=uiconst.TORIGHT, padLeft=2)
        self.saveEditButton = Button(parent=buttonCont, label=GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Save'), func=self.SaveEditedSearchTerm, btn_default=0, align=uiconst.TORIGHT, padLeft=2)
        self.cancelEditButton = Button(parent=buttonCont, label=GetByLabel('UI/Commands/Cancel'), func=self.CancelEditedSearchTerm, btn_default=0, align=uiconst.TORIGHT, padLeft=4)
        self.saveEditButton.state = uiconst.UI_HIDDEN
        self.cancelEditButton.state = uiconst.UI_HIDDEN

    def CheckBoxChange(self, checkbox, *args):
        settings.user.ui.Set(checkbox.GetSettingsKey(), checkbox.checked)

    def ConstructCriteriaOptionsCombos(self):
        currentProperty = self.comboProperty.GetValue()
        requestedControlType = CONTROLS_BY_PROPERTY[currentProperty]
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

            requestedControl = Combo(label='', parent=self.criteriaComboCont, options=optionsList, name=requestedControlType, width=146, align=uiconst.NOALIGN)
        elif requestedControlType == 'title_picker':
            optionsList = []
            for title in self.titles.itervalues():
                optionsList.append([title.titleName, title.titleID])

            requestedControl = Combo(label='', parent=self.criteriaComboCont, options=optionsList, name=requestedControlType, width=146, align=uiconst.NOALIGN)
        elif requestedControlType == 'role_picker_locational':
            optionsList = []
            for roleID, roleName in sorted(iter_role_names(), key=lambda r: r[1]):
                if roleID in self.locationalRoles:
                    optionsList.append([roleName, roleID])

            requestedControl = Combo(label='', parent=self.criteriaComboCont, options=optionsList, name=requestedControlType, width=146, align=uiconst.NOALIGN)
        elif requestedControlType == 'location_picker':
            bases = [('-', None)]
            for office in sm.GetService('officeManager').GetMyCorporationsOffices():
                if idCheckers.IsStation(office.stationID):
                    bases.append((cfg.evelocations.Get(office.stationID).locationName, office.stationID))

            requestedControl = Combo(label='', parent=self.criteriaComboCont, options=bases, name=requestedControlType, width=146, align=uiconst.NOALIGN)
        elif requestedControlType == 'date_picker':
            nowSecs = blue.os.GetWallclockTime()
            year, month, wd, day, hour, min, sec, ms = GetTimeParts(nowSecs)
            now = [year, month, day]
            requestedControl = DatePicker(name='datepicker', parent=self.criteriaComboCont, align=uiconst.TOPLEFT, pos=(6, -2, 256, 18))
            requestedControl.Startup(now, False, 4, None, None)
        elif requestedControlType == 'edit_control':
            control = SingleLineEditText(name=requestedControlType, parent=self.criteriaComboCont, width=146, align=uiconst.NOALIGN, maxLength=37)
            requestedControl = control
        else:
            raise RuntimeError('UnexpectedControlTypeRequested')
        if currentControlType is not None and self.propertyControls.has_key(currentControlType):
            currentControl = self.propertyControls[currentControlType]
            currentControl.state = uiconst.UI_HIDDEN
        if requestedControl is None:
            raise RuntimeError('FailedToCreateControlTypeRequested')
        requestedControl.state = uiconst.UI_NORMAL
        self.propertyControls[requestedControlType] = requestedControl
        self.propertyControls['current'] = requestedControlType

    def ExecuteQuery(self, *args):
        query = []
        for entry in self.scrollQuery.GetNodes():
            joinOperator = entry.joinOperator
            property = entry.property
            operator = entry.operator
            value = entry.value
            if joinOperator is None:
                query.append([property, operator, value])
            else:
                query.append([joinOperator,
                 property,
                 operator,
                 value])

        searchTitles = SEARCH_TITLES_SETTING.is_enabled()
        includeImplied = INCLUDE_IMPLIED_SETTING.is_enabled()
        self.memberIDs = sm.GetService('corp').GetMemberIDsByQuery(query, includeImplied, searchTitles)
        if self.lpfnQueryCompleted is not None:
            self.lpfnQueryCompleted()

    def MakeLabel(self, joinOperator, property, operator, value):
        localizedJoinOperator = None
        localizedProperty = None
        localizedOperator = None
        localizedValue = None
        if joinOperator:
            for k, v in LOGICAL_OPERATORS.iteritems():
                if v == joinOperator:
                    localizedJoinOperator = k
                    break

        currentControlType = CONTROLS_BY_PROPERTY[property]
        for display_text, field_name in PROPERTY_LIST:
            if property == field_name:
                localizedProperty = display_text
                break

        if operator:
            for k, v in OPTIONS_BY_PROPERTY[property]:
                if v == operator:
                    localizedOperator = k
                    break

        if value:
            if currentControlType in ('role_picker', 'role_picker_locational'):
                localizedValue = get_role_name(value)
            elif currentControlType == 'title_picker':
                for title in self.titles.itervalues():
                    if title.titleID == value:
                        localizedValue = title.titleName
                        break

            elif currentControlType == 'location_picker':
                localizedValue = GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/SearchQueryLocation', location=value)
            elif currentControlType == 'date_picker':
                localizedValue = GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/SearchQueryDate', date=value)
            elif currentControlType == 'edit_control':
                localizedValue = value
            else:
                raise RuntimeError('UnexpectedControlTypeRequested')
        if joinOperator and operator and value:
            label = GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/FullSearchLabel', joinOperator=localizedJoinOperator, property=localizedProperty, operator=localizedOperator, value=localizedValue)
        elif joinOperator and operator:
            label = GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/JoinOperatorSearchLabel', joinOperator=localizedJoinOperator, property=localizedProperty, operator=localizedOperator)
        elif joinOperator and value:
            label = GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/JoinValueSearchLabel', joinOperator=localizedJoinOperator, property=localizedProperty, value=localizedValue)
        elif operator and value:
            label = GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/OperatorValueSearchLabel', property=localizedProperty, operator=localizedOperator, value=localizedValue)
        elif operator:
            label = GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/OperatorSearchLabel', property=localizedProperty, operator=localizedOperator)
        elif value:
            label = GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/ValueSearchLabel', property=localizedProperty, value=localizedValue)
        elif joinOperator:
            label = GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/JoinSearchLabel', joinOperator=localizedJoinOperator)
        else:
            label = GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/DefaultSearchLabel', property=localizedProperty)
        return label

    def AddSearchTerm(self, *args):
        try:
            sm.GetService('loading').Cycle('Loading')
            joinOperator = None
            if self.comboJoinOperator.state == uiconst.UI_NORMAL:
                joinOperator = self.comboJoinOperator.GetValue()
            property = self.comboProperty.GetValue()
            operator = self.comboOperator.GetValue()
            value = None
            if self.propertyControls.has_key('current'):
                currentControlType = self.propertyControls['current']
                currentControl = self.propertyControls[currentControlType]
                value = currentControl.GetValue()
            if not value:
                raise UserError('CustomInfo', {'info': GetByLabel('UI/Shared/PleaseTypeSomething')})
            label = self.MakeLabel(joinOperator, property, operator, value)
            control = GetFromClass(TwoButtons, {'label': label,
             'caption1': GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Edit'),
             'caption2': GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/Remove'),
             'OnClick1': self.OnClickEdit,
             'OnClick2': self.OnClickRemove,
             'args1': label,
             'args2': label,
             'joinOperator': joinOperator,
             'property': property,
             'operator': operator,
             'value': value})
            self.scrollQuery.AddEntries(-1, [control])
            self.CheckShowScrollNoContentHint()
            self.comboJoinOperator.state = uiconst.UI_NORMAL
        finally:
            sm.GetService('loading').StopCycle()

    def SaveEditedSearchTerm(self, *args):
        if self.currentlyEditing is None:
            return
        joinOperator = None
        if self.comboJoinOperator.state == uiconst.UI_NORMAL:
            joinOperator = self.comboJoinOperator.GetValue()
        property = self.comboProperty.GetValue()
        operator = self.comboOperator.GetValue()
        value = None
        if self.propertyControls.has_key('current'):
            currentControlType = self.propertyControls['current']
            currentControl = self.propertyControls[currentControlType]
            value = currentControl.GetValue()
        entry = self.currentlyEditing
        label = self.MakeLabel(joinOperator, property, operator, value)
        entry.panel.label = label
        entry.panel.sr.label.text = label
        entry.label = label
        entry.args1 = label
        entry.args2 = label
        entry.joinOperator = joinOperator
        entry.property = property
        entry.operator = operator
        entry.value = value
        self.currentlyEditing = None
        if len(self.scrollQuery.GetNodes()) == 0:
            self.comboJoinOperator.state = uiconst.UI_HIDDEN
        else:
            self.comboJoinOperator.state = uiconst.UI_NORMAL
        self.addEditButton.state = uiconst.UI_NORMAL
        self.saveEditButton.state = uiconst.UI_HIDDEN
        self.cancelEditButton.state = uiconst.UI_HIDDEN

    def CancelEditedSearchTerm(self, *args):
        if len(self.scrollQuery.GetNodes()) == 0:
            self.comboJoinOperator.state = uiconst.UI_HIDDEN
        else:
            self.comboJoinOperator.state = uiconst.UI_NORMAL
        self.addEditButton.state = uiconst.UI_NORMAL
        self.saveEditButton.state = uiconst.UI_HIDDEN
        self.cancelEditButton.state = uiconst.UI_HIDDEN

    def OnClickEdit(self, args, button):
        entry = self.GetEntryByLabel(args)
        if entry is None:
            raise RuntimeError('MissingEntry')
        self.currentlyEditing = entry
        joinOperator = entry.joinOperator
        property = entry.property
        operator = entry.operator
        value = entry.value
        if joinOperator is None:
            self.comboJoinOperator.state = uiconst.UI_HIDDEN
        else:
            self.comboJoinOperator.state = uiconst.UI_NORMAL
            self.comboJoinOperator.SelectItemByValue(joinOperator)
        self.comboProperty.SelectItemByValue(property)
        self.comboOperator.LoadOptions(OPTIONS_BY_PROPERTY[property])
        self.comboOperator.SelectItemByValue(operator)
        self.ConstructCriteriaOptionsCombos()
        currentControlType = self.propertyControls['current']
        currentControl = self.propertyControls[currentControlType]
        if getattr(currentControl, 'SelectItemByValue', None) is not None:
            currentControl.SelectItemByValue(value)
        elif getattr(currentControl, 'SetValue', None) is not None:
            currentControl.SetValue(value)
        self.addEditButton.state = uiconst.UI_HIDDEN
        self.saveEditButton.state = uiconst.UI_NORMAL
        self.cancelEditButton.state = uiconst.UI_NORMAL

    def OnClickRemove(self, args, button):
        entry = self.GetEntryByLabel(args)
        if entry is None:
            raise RuntimeError('MissingEntry')
        self.scrollQuery.RemoveEntries([entry])
        self.CheckShowScrollNoContentHint()
        self.RemoveJoinOperatorFromFirstEntry()
        if len(self.scrollQuery.GetNodes()) == 0:
            self.comboJoinOperator.state = uiconst.UI_HIDDEN
        self.addEditButton.state = uiconst.UI_NORMAL
        self.saveEditButton.state = uiconst.UI_HIDDEN
        self.cancelEditButton.state = uiconst.UI_HIDDEN

    def RemoveJoinOperatorFromFirstEntry(self):
        if not len(self.scrollQuery.GetNodes()):
            return
        entry = self.scrollQuery.GetNodes()[0]
        joinOperator = entry.joinOperator
        property = entry.property
        operator = entry.operator
        value = entry.value
        if joinOperator is None:
            return
        joinOperator = None
        label = self.MakeLabel(joinOperator, property, operator, value)
        entry.panel.label = label
        entry.panel.sr.label.text = label
        entry.label = label
        entry.args1 = label
        entry.args2 = label
        entry.joinOperator = joinOperator

    def GetEntryByLabel(self, label):
        for entry in self.scrollQuery.GetNodes():
            if entry.label == label:
                return entry

    def OnComboChange(self, entry, header, value, *args):
        if entry.name == 'property':
            self.comboOperator.LoadOptions(OPTIONS_BY_PROPERTY[self.comboProperty.GetValue()])
            self.ConstructCriteriaOptionsCombos()


class CorpFindMembersInRole(Container):
    __guid__ = 'form.CorpFindMembersInRole'
    __nonpersistvars__ = []
    inited = False

    def ApplyAttributes(self, attributes):
        super(CorpFindMembersInRole, self).ApplyAttributes(attributes)
        self.wndQuery = CorpQueryMembersForm()
        self.wndQueryForm = None
        self.outputScrollContainer = None
        self.showHideButton = None
        self.outputTypeButtonGroup = None
        self.outputWindow = None

    def Load(self, panel_id, *args):
        if not self.inited:
            self.inited = 1
            self.ConstructQueryHeaderCont()
            self.wndQueryForm = self.wndQuery.Load(self, self.PopulateView)
            self.wndForm = Container(name='bottomCont', parent=self)
            optlist = ((GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/SimpleList'), CorpMembersViewSimple), (GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/RoleManagementList'), CorpMembersViewRoleManagement), (GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/TaskManagementList'), CorpMembersViewTaskManagement))
            self.outputTypeButtonGroup = ToggleButtonGroup(parent=self.wndForm, align=uiconst.TOTOP, callback=self.OnTogglebuttonGroup, padTop=16)
            for label, func in optlist:
                self.outputTypeButtonGroup.AddButton(func, label)

            self.outputTypeButtonGroup.SelectFirst()
            self.outputWindowContainer = None
            viewClass = self.outputTypeButtonGroup.GetValue()
            self.SwitchToView(viewClass)

    def ConstructQueryHeaderCont(self):
        queryHeaderCont = ContainerAutoSize(name='queryHeaderCont', parent=self, align=uiconst.TOTOP, alignMode=uiconst.CENTERRIGHT, state=uiconst.UI_NORMAL, height=16, padBottom=4)
        toggleCont = ContainerAutoSize(name='toggleCont')
        self.toggleQueryLabel = EveLabelMedium(name='toggleQueryLabel', text=GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/HideQuery'), parent=queryHeaderCont, left=15, align=uiconst.CENTERRIGHT)
        self.showHideExp = Sprite(parent=queryHeaderCont, pos=(0, 0, 11, 11), name='expandericon', state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Shared/expanderUp.png', align=uiconst.CENTERRIGHT)
        queryHeaderCont.OnClick = self.ToggleQueryPanel

    def _OnClose(self, *args):
        try:
            if self.outputWindow and hasattr(self.outputWindow, '_OnClose'):
                self.outputWindow._OnClose(args)
        except Exception as e:
            logger.exception(e)

    def OnTabDeselect(self):
        if self.outputWindow and hasattr(self.outputWindow, 'OnTabDeselect'):
            self.outputWindow.OnTabDeselect()

    def ToggleQueryPanel(self, *args):
        isVisible = self.wndQueryForm.state not in (uiconst.UI_NORMAL, uiconst.UI_PICKCHILDREN)
        if isVisible:
            self.showHideExp.texturePath = 'res:/UI/Texture/Shared/expanderUp.png'
        else:
            self.showHideExp.texturePath = 'res:/UI/Texture/Shared/expanderDown.png'
        self.toggleQueryLabel.text = GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/HideQuery') if isVisible else GetByLabel('UI/Corporations/CorporationWindow/Members/FindMemberInRole/ShowQuery')
        self.wndQueryForm.state = uiconst.UI_NORMAL if isVisible else uiconst.UI_HIDDEN

    def OnTogglebuttonGroup(self, *args):
        viewClass = self.outputTypeButtonGroup.GetValue()
        uthread.new(self.SwitchToView, viewClass)

    def SwitchToView(self, viewClass, populate = 1):
        try:
            sm.GetService('loading').Cycle('Loading')
            if self.outputWindow is None or self.outputWindow.__guid__ != viewClass.__guid__:
                if self.outputWindowContainer is None:
                    self.outputWindowContainer = Container(name='outputWindow', parent=self.wndForm, align=uiconst.TOALL, pos=(0, 0, 0, 0))
                else:
                    if self.outputWindow and hasattr(self.outputWindow, 'OnTabDeselect'):
                        self.outputWindow.OnTabDeselect()
                    if self.outputWindow and hasattr(self.outputWindow, '_OnClose'):
                        self.outputWindow._OnClose(self)
                    self.outputWindowContainer.Flush()
                self.outputWindow = viewClass(parent=self.outputWindowContainer, padTop=8)
                self.outputWindow.CreateWindow()
            if populate:
                self.outputWindow.PopulateView(self.wndQuery.memberIDs)
        finally:
            sm.GetService('loading').StopCycle()

    def PopulateView(self):
        viewClass = self.outputTypeButtonGroup.GetValue()
        uthread.new(self.SwitchToView, viewClass)
