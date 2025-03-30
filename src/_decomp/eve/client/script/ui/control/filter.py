#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\filter.py
import _weakref
import telemetry
import carbonui.const as uiconst
import math
import mathext
import uthread
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui.control.button import Button
from carbonui.control.checkbox import Checkbox
from carbonui.control.contextMenu.menuUtil import ClearMenuLayer
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.eveWindowUnderlay import RaisedUnderlay
from carbonui.control.radioButton import RadioButtonUnderlay
from carbonui.decorative.menuUnderlay import MenuUnderlay
from eve.client.script.ui.shared.fitting.fittingUtil import EatSignalChangingErrors
from localization import GetByLabel
from signals import Signal
from signals.signalUtil import ChangeSignalConnect
ROOT_TYPE = -999

class Filter(Container):
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL
    default_iconSize = 16
    default_columns = 1
    default_maxSize = None
    default_height = 32

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.columns = attributes.get('columns', self.default_columns)
        self.maxSize = attributes.get('maxSize', uicore.desktop.height)
        self._expanding = False
        self._comboDropDown = None
        self.filterContoller = attributes.filterController
        self.currenEntries = []
        self.filterText = attributes.filterText
        self.filterTextShort = attributes.filterTextShort or self.filterText
        self.filterTextWidth = 100
        self.filterTextShortWidth = 100
        self.iconSize = attributes.get('iconSize', self.default_iconSize)
        self.texturePath = attributes.texturePath
        self.Prepare_()
        self.SetLabel_(self.filterText)
        self._mouseDownCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEDOWN, self.OnGlobalMouseDown)
        self.ChangeSignalConnection()

    def Prepare_(self):
        self.filterBtn = FilterButton(parent=self, label='', align=uiconst.TOALL, func=self.OnBtnClicked)
        self.filterTextWidth, _ = self.filterBtn.sr.label.MeasureTextSize(self.filterText)
        self.filterTextShortWidth, _ = self.filterBtn.sr.label.MeasureTextSize(self.filterTextShort)
        self.filterBtn.width = self.filterBtn.height = 0
        self.filterBtn.Update_Size_ = self.Update_BtnSize
        self.filterBtn.LoadTooltipPanel = self.LoadTooltipPanel
        self.filterBtn.GetTooltipPointer = self.GetTooltipPointer
        self.ChangeButtonLook()

    def SetLabel_(self, label):
        if not self or self.destroyed:
            return
        self.filterBtn.SetLabel(label)
        self.Update_Size_()

    def Update_Size_(self):
        btnLabel = self.filterBtn.sr.label
        btnLabel.align = uiconst.CENTER
        self.width = mathext.clamp(btnLabel.textwidth + 20, 64, 256)
        self.height = mathext.clamp(btnLabel.textheight + 2, self.default_height, 32)

    def Update_BtnSize(self):
        pass

    def LoadTooltipPanel(self, tooltipPanel, *args):
        if self.IsExpanded():
            return
        layoutGrid = LayoutGrid(parent=tooltipPanel, margin=4, cellSpacing=4, columns=1)
        if not self.filterContoller.IsActive():
            EveLabelMedium(parent=layoutGrid, text=GetByLabel('UI/Control/Filter/FilterInactive'), padding=4)
            return
        optionsToShow, checkedKeys, hasCheckedChildren = self.filterContoller.GetCheckedOptions()
        if not optionsToShow:
            EveLabelMedium(parent=layoutGrid, text=GetByLabel('UI/Control/Filter/NoOptionsSelected'), padding=4)
            return
        self.currenEntries = []
        for optionObject in optionsToShow:
            self.AddEntry(layoutGrid, optionObject, False, 0, checkedKeys, hasCheckedChildren)

        self.AddWidthSpacer(layoutGrid)
        return layoutGrid

    def AddWidthSpacer(self, layoutGrid):
        maxWidth = 100
        for eachEntry in self.currenEntries:
            maxWidth = max(maxWidth, eachEntry.GetMaxWidth())

        layoutGrid.FillRow()
        for x in xrange(layoutGrid.columns):
            layoutGrid.AddCell(cellObject=Fill(pos=(0,
             0,
             maxWidth + 10,
             0), align=uiconst.TOPLEFT))

    def GetTooltipPointer(self):
        return uiconst.POINT_TOP_1

    def Prepare_OptionMenu_(self):
        ClearMenuLayer()
        menu = Container(parent=uicore.layer.menu, pos=(0, 0, 200, 200), align=uiconst.RELATIVE, state=uiconst.UI_NORMAL, padding=16)
        MenuUnderlay(bgParent=menu)
        return menu

    @telemetry.ZONE_METHOD
    def Expand(self, refresh = False):
        if self._expanding:
            return
        try:
            self._expanding = True
            PlaySound(uiconst.SOUND_EXPAND)
            if self.IsExpanded():
                if refresh:
                    for eachEntry in self.currenEntries:
                        eachEntry.RefreshEntry()

                    if self._comboDropDown and self._comboDropDown():
                        self.SetMenuSizeAndPosition(self._comboDropDown())
                return
            menu = self.Prepare_OptionMenu_()
            canEdit = True
            menu.canEdit = canEdit
            layoutGrid = self.LoadMenu(menu, canEdit)
            self.SetMenuSizeAndPosition(menu)
            self._comboDropDown = _weakref.ref(menu)
        finally:
            self._expanding = False

    def SetMenuSizeAndPosition(self, menu):
        menu.layoutGrid.RefreshGridLayout()
        l, t, w, h = self.GetAbsolute()
        menu.width, totalHeight = menu.layoutGrid.GetSize()
        clearHeight = menu.clearAll.height + menu.clearAll.padTop + menu.clearAll.padBottom if menu.clearAll and menu.clearAll.display else 0
        menu.height = min(self.maxSize, totalHeight + clearHeight)
        menu.left = l
        menu.top = min(t + h + 1, uicore.desktop.height - menu.height - 8)

    def LoadMenu(self, menu, canEdit):
        scrollCont = ScrollContainer(name='scrollCont', parent=menu)
        layoutGrid = LayoutGrid(parent=scrollCont, margin=8, columns=self.columns, cellSpacing=4)
        menu.layoutGrid = layoutGrid
        menu.clearAll = None
        self.currenEntries = []
        if self.filterContoller.GetNumOptions():
            entry = SelectAllEntry(filterContoller=self.filterContoller, func=self.ToggleSelectAll, parent=menu, idx=0, padding=(0, 16, 0, 4))
            menu.clearAll = entry
            self.currenEntries.append(entry)
        else:
            EveLabelMedium(parent=layoutGrid, text=GetByLabel('UI/Control/Filter/NoOptions'))
        self.AddEntry(layoutGrid, self.filterContoller.GetRootOption(), canEdit, -1)
        self.AddWidthSpacer(layoutGrid)
        return layoutGrid

    @telemetry.ZONE_METHOD
    def AddEntry(self, parent, optionObject, canEdit, subLevel, onlyCheckedKeys = None, hasCheckedChildren = None):
        hasChildren = optionObject.HasChildrenOptions()
        if optionObject.optionType != ROOT_TYPE:
            if not self.ShouldAddEntry(optionObject, onlyCheckedKeys, hasCheckedChildren):
                return
            colSpan = self.columns if hasChildren else 1
            self.FillRowIfNeeded(parent, hasChildren)
            entry = FilterEntry(optionObject=optionObject, canEdit=canEdit, subLevel=subLevel, func=self.OnOptionClicked)
            parent.AddCell(cellObject=entry, colSpan=colSpan)
            self.FillRowIfNeeded(parent, hasChildren)
            self.currenEntries.append(entry)
        for eachOption in optionObject.childrenOptions:
            self.AddEntry(parent=parent, optionObject=eachOption, canEdit=canEdit, subLevel=subLevel + 1, onlyCheckedKeys=onlyCheckedKeys, hasCheckedChildren=hasCheckedChildren)

        self.FillRowIfNeeded(parent, hasChildren)

    def FillRowIfNeeded(self, parent, hasChildren):
        if hasChildren:
            parent.FillRow()

    def ShouldAddEntry(self, optionObject, onlyCheckedKeys, hasCheckedChildrenKeys):
        if not onlyCheckedKeys:
            return True
        key = optionObject.optionKey
        if key not in onlyCheckedKeys and (not hasCheckedChildrenKeys or key not in hasCheckedChildrenKeys):
            return False
        return True

    def OnOptionClicked(self, optionObject, isChecked, *args):
        self.filterContoller.SetCheckedValueManually(optionObject, isChecked)
        self.Refresh()

    def ToggleSelectAll(self):
        allSelected = self.filterContoller.AreAllSelected()
        self.filterContoller.ChangeSelectionOfAll(not allSelected)
        self.Refresh()

    def Refresh(self, *args):
        self.Expand(True)

    def OnFiltersChanged(self, *args):
        self.ChangeButtonLook()

    def ChangeButtonLook(self):
        isActive = self.filterContoller.IsActive()
        self.filterBtn.selectedUnderlay.display = isActive

    def IsExpanded(self):
        return bool(self._comboDropDown and self._comboDropDown())

    def OnBtnClicked(self, *args):
        if self.IsExpanded():
            if self._comboDropDown().canEdit:
                self.Cleanup()
                return
        uthread.new(self.Expand)

    def OnGlobalMouseDown(self, *args):
        currentMouseOver = uicore.uilib.mouseOver
        if currentMouseOver != self and not currentMouseOver.IsUnder(self):
            if not self._comboDropDown:
                self.Cleanup()
                return 1
            menu = self._comboDropDown()
            if currentMouseOver != menu and not currentMouseOver.IsUnder(menu):
                self.Cleanup()
        return 1

    def ChangeLabelIfNeeded(self):
        if self.width - 4 < self.filterTextWidth:
            text = self.filterTextShort
        else:
            text = self.filterText
        self.filterBtn.ChangeLabelIfNeeded(text)

    def ResetLabel(self):
        self.filterBtn.SetLabel(self.filterText)

    def Cleanup(self):
        if self._comboDropDown:
            ClearMenuLayer()
        self.currenEntries = []
        self._comboDropDown = None

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.filterContoller.on_filter_changed, self.OnFiltersChanged)]
        ChangeSignalConnect(signalAndCallback, connect)

    def Close(self):
        if getattr(self, '_mouseDownCookie', None):
            uicore.event.UnregisterForTriuiEvents(self._mouseDownCookie)
            self._mouseDownCookie = None
        with EatSignalChangingErrors(errorMsg='Filter'):
            self.ChangeSignalConnection(connect=False)
        Container.Close(self)


class FilterWithCheckbox(Filter):

    def ApplyAttributes(self, attributes):
        Filter.ApplyAttributes(self, attributes)

    def Prepare_(self):
        Filter.Prepare_(self)
        self.filterBtn.padLeft = 18
        self.cbox = Checkbox(text='', parent=self, settingsKey='cb', checked=self.filterContoller.IsActive(), align=uiconst.CENTERLEFT, pos=(0, 4, 0, 0), callback=self.OnMainCheckboxChange)
        self.cbox.left = 0
        self.cbox.top = 0
        self.cbox.width = self.cbox.checkboxCont.width
        self.cbox.height = self.cbox.checkboxCont.height
        self.cbox.checkboxCont.left = 0
        self.cbox.checkboxCont.top = 0
        self.SetCheckboxHint()

    def SetCheckboxHint(self):
        if self.filterContoller.IsActive():
            hintPath = 'UI/Control/Filter/DeactivateFilter'
        else:
            hintPath = 'UI/Control/Filter/ActivateFilter'
        self.cbox.hint = GetByLabel(hintPath)

    def OnMainCheckboxChange(self, *args):
        self.filterContoller.ChangeIsActive()
        if self.IsExpanded():
            self.Refresh()
        self.SetCheckboxHint()

    def OnFiltersChanged(self, *args):
        isActive = self.filterContoller.IsActive()
        if self.cbox.GetValue() != isActive:
            self.cbox.SetChecked(isActive, report=False)

    def Update_Size_(self):
        btnLabel = self.filterBtn.sr.label
        btnLabel.align = uiconst.CENTERLEFT
        btnLabel.left = 8
        self.width = mathext.clamp(btnLabel.textwidth + 40, 64, 256)
        self.height = mathext.clamp(btnLabel.textheight + 2, self.default_height, 32)


class FilterButton(Button):

    def ApplyAttributes(self, attributes):
        Button.ApplyAttributes(self, attributes)
        self.selectedUnderlay = Sprite(name='cornerTriSmall', parent=self, align=uiconst.BOTTOMRIGHT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Shared/DarkStyle/cornerTriSmall.png', width=5, height=5, rotation=math.pi, opacity=0.9, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW)

    def ChangeLabelIfNeeded(self, text):
        if self.sr.label.text != text:
            self.sr.label.text = text


class FilterCheckbox(Checkbox):

    def ConstructCheckboxCont(self):
        if self.checkboxCont:
            self.checkboxCont.Close()
        self.checkboxCont = Container(parent=self, pos=(-1, 1, 16, 16), name='checkboxCont', state=uiconst.UI_DISABLED, align=uiconst.RELATIVE)
        self.sr.active = Sprite(parent=self.checkboxCont, pos=(0, 0, 16, 16), name='active', state=uiconst.UI_HIDDEN, texturePath='res:/UI/Texture/classes/UtilMenu/checkBoxInactive.png', opacity=0.1)
        self.checkMark = Sprite(parent=self.checkboxCont, pos=(0, 0, 16, 16), name='self_ok', state=uiconst.UI_HIDDEN, texturePath='res:/UI/Texture/classes/UtilMenu/checkBoxActive.png')
        self.underlay = FilterCheckboxUnderlay(parent=self.checkboxCont, padding=2)


class FilterCheckboxUnderlay(RaisedUnderlay):
    default_fixedColor = (1, 1, 1, 0.1)
    OPACITY_IDLE = 0.1
    OPACITY_HOVER = 0.2
    OPACITY_SELECTED = 0.1
    OPACITY_MOUSEDOWN = 0.2

    def ConstructLayout(self):
        RaisedUnderlay.ConstructLayout(self)
        self.innerGlow.opacity = 0.0
        self.frame.opacity = 0.1


class FilterRadioButtonUnderlay(RadioButtonUnderlay):
    default_fixedColor = (1, 1, 1, 0.1)
    OPACITY_IDLE = 0.1
    OPACITY_HOVER = 0.1
    OPACITY_SELECTED = 0.1
    OPACITY_MOUSEDOWN = 0.2

    def ConstructLayout(self):
        RadioButtonUnderlay.ConstructLayout(self)
        self.innerGlow.opacity = 0.0
        self.frame.opacity = 0.1


class SelectAllEntry(Container):
    default_name = 'SelectAllEntry'
    default_height = 32
    default_align = uiconst.TOTOP

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.func = attributes.func
        self.filterContoller = attributes.filterContoller
        isChecked = self.filterContoller.AreAllSelected()
        self.selectAllBtn = Button(parent=self, label=GetByLabel('UI/Common/SelectAll'), align=uiconst.CENTER, func=self.OnBtnClicked)
        self.SetTextBasedOnState(isChecked)

    def OnBtnClicked(self, *args):
        self.func()

    def SetTextBasedOnState(self, allSelected = False):
        if allSelected:
            text = GetByLabel('UI/Common/DeselectAll')
        else:
            text = GetByLabel('UI/Common/SelectAll')
        self.selectAllBtn.SetLabel(text)

    def RefreshEntry(self):
        self.SetTextBasedOnState(self.filterContoller.AreAllSelected())

    def GetMaxWidth(self):
        return self.selectAllBtn.width + 20


class FilterEntry(Container):
    default_name = 'FilterEntry'
    default_height = 20
    default_align = uiconst.TOTOP
    default_canEdit = False

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.canEdit = attributes.get('canEdit', self.default_canEdit)
        self.func = attributes.func
        self.optionObject = attributes.optionObject
        self.labelObject = None
        text = self.optionObject.name
        subLevel = attributes.subLevel or 0
        isChecked = self.optionObject.isChecked
        self.AddCheckboxes(text, isChecked, subLevel)

    def AddCheckboxes(self, text, isChecked, subLevel):
        indent = subLevel * 16
        if self.canEdit:
            self.cbox = Checkbox(text=text, parent=self, configName='cb', retval=None, checked=isChecked, align=uiconst.TOPLEFT, callback=self.OnCheckboxClicked, wrapLabel=False)
            self.cbox.left = 4 + indent
            self.labelObject = self.cbox.label
            self.cbox.width = self.GetMaxWidth()
        else:
            if isChecked:
                Sprite(parent=self, texturePath='res:/UI/Texture/classes/UtilMenu/checkmark.png', align=uiconst.CENTERLEFT, pos=(4 + indent,
                 0,
                 16,
                 16))
            self.labelObject = EveLabelMedium(parent=self, align=uiconst.CENTERLEFT, left=24 + indent, text=text)

    def OnCheckboxClicked(self, cb, *args):
        self.func(self.optionObject, cb.GetValue())

    def RefreshEntry(self):
        self.cbox.SetChecked(self.optionObject.isChecked, report=False)

    def GetMaxWidth(self):
        label = self.labelObject
        textWidth = self.GetTextWidth(label)
        if self.canEdit:
            left = self.cbox.left + label.padLeft
        else:
            left = label.left
        return max(20, left + textWidth + label.padRight) + 16

    def GetTextWidth(self, label):
        return uicore.font.GetTextWidth(label.text, fontsize=label.fontsize, fontFamily=label.fontFamily, fontStyle=label.fontStyle, fontPath=label.fontPath)


class FilterController(object):

    def __init__(self, settingsConfig, options, defaultIsActive = False, doSortChildren = True):
        self.on_filter_changed = Signal(signalName='on_filter_changed')
        self.settingsConfig = settingsConfig
        self._isActive = settings.user.ui.Get(self._GetActiveSettingKey(), defaultIsActive)
        self.root = OptionObject('root', -1, ROOT_TYPE, childrenOptions=options, doSortChildren=doSortChildren)
        self.optionsDict = {}
        self.SetOptions(options)

    def SetOptions(self, options):
        optionsToLoad = self._FindOptions(options)
        self.root.SetChildren(optionsToLoad)
        self.options = optionsToLoad
        self.optionsDict = {}
        self.BuildOptionsDict()
        self.SetCheckedStateOfOptionsBasedOnSettings()
        if self.AreAllOrNoneSelected() and self.IsActive():
            self.ChangeIsActive(sendSignal=False)

    def _FindOptions(self, optionsToLoad):
        options = []
        for eachOption in optionsToLoad:
            options.append(eachOption)

        return options

    def _GetActiveSettingKey(self):
        return '%s_IsActive' % self.settingsConfig

    def BuildOptionsDict(self):

        def AddOption(option):
            self.optionsDict[option.optionKey] = option
            for child in option.childrenOptions:
                AddOption(child)

        for each in self.options:
            AddOption(each)

    def GetSelectedOptions(self):
        optionFinder = SelectedOptionsFinder(self.options)
        _, checked, _ = optionFinder.FindSelected()
        ret = [ (x.optionType, x.value) for x in checked ]
        return ret

    def GetCheckedOptions(self):
        return self.CollectSelectedOptions()

    def CollectSelectedOptions(self):
        optionFinder = SelectedOptionsFinder(self.options)
        optionsToShow, checked, hasCheckedAncestors = optionFinder.FindSelected()
        checkedKeys = [ x.optionKey for x in checked ]
        isParentKeys = [ x.optionKey for x in hasCheckedAncestors ]
        return (optionsToShow, checkedKeys, isParentKeys)

    def GetOptions(self):
        return self.options[:]

    def GetRootOption(self):
        return self.root

    def SetCheckedValueManually(self, optionObject, isChecked):
        self.SetCheckedValue(optionObject, isChecked)
        areAllOrNoneSelected = self.AreAllOrNoneSelected()
        if areAllOrNoneSelected and self.IsActive():
            self.ChangeIsActive(sendSignal=False)
        self.on_filter_changed(self)

    def SetCheckedValue(self, optionObject, checkedValue, setChildren = True):
        if not self.IsActive():
            self.ChangeIsActive(sendSignal=False)
        optionObject.SetCheckedState(checkedValue)
        if setChildren:
            for each in optionObject.childrenOptions:
                self.SetCheckedValue(each, checkedValue)

        self.ChangeSettingsForOption(optionObject, checkedValue)
        self.UpdateParentCheckedIfNeeded(optionObject)

    def ChangeSettingsForOption(self, optionObject, checkedValue):
        settingKey = self._GetOptionSettingKey(optionObject)
        settings.user.ui.Set(settingKey, checkedValue)

    def SetCheckedStateOfOptionsBasedOnSettings(self):
        for eachOption in self.optionsDict.values():
            if eachOption.HasChildrenOptions():
                continue
            settingKey = self._GetOptionSettingKey(eachOption)
            value = settings.user.ui.Get(settingKey, eachOption.defaultSetting)
            self.SetCheckedValue(eachOption, value)

    def _GetOptionSettingKey(self, optionObject):
        return '%s_filter_%s' % (self.settingsConfig, optionObject.optionKey)

    def IsActive(self):
        return self._isActive

    def ChangeIsActive(self, sendSignal = True):
        self._isActive = not self._isActive
        settings.user.ui.Set(self._GetActiveSettingKey(), self._isActive)
        if sendSignal:
            self.on_filter_changed(self)

    def UpdateParentCheckedIfNeeded(self, optionObject):
        parentKey = optionObject.parentKey
        if not parentKey:
            return
        parentOption = self.optionsDict.get(parentKey, None)
        if not parentOption:
            return
        areAllSelected = self.AreAllChildrenSelected(parentOption)
        if parentOption.IsChecked() != areAllSelected:
            self.SetCheckedValue(parentOption, areAllSelected, setChildren=False)

    def AreAllChildrenSelected(self, optionObject):
        for eachChild in optionObject.childrenOptions:
            if not eachChild.IsChecked():
                return False
            allSelected = self.AreAllChildrenSelected(eachChild)
            if not allSelected:
                return False

        return True

    def AreNoChildrenSelected(self, optionObject):
        for eachChild in optionObject.childrenOptions:
            if eachChild.IsChecked():
                return False
            noSelected = self.AreNoChildrenSelected(eachChild)
            if not noSelected:
                return False

        return True

    def AreNoneSelected(self):
        return self.AreNoChildrenSelected(self.root)

    def AreAllSelected(self):
        return self.AreAllChildrenSelected(self.root)

    def AreAllOrNoneSelected(self):
        return self.AreAllSelected() or self.AreNoneSelected()

    def ChangeSelectionOfAll(self, isSelected = True):
        for each in self.optionsDict.itervalues():
            self.SetCheckedValue(each, isSelected, False)

        if self.IsActive():
            self.ChangeIsActive(sendSignal=False)
        self.on_filter_changed(self)

    def GetNumOptions(self):
        return len(self.optionsDict)


class SelectedOptionsFinder(object):

    def __init__(self, options):
        self.options = options
        self.checked = []
        self.hasCheckedAncestors = []
        self.activeOptions = []

    def FindSelected(self):
        for eachOption in self.options:
            checkedOrChildChecked = self.AddCheckedAndCheckedChildren(eachOption)
            if checkedOrChildChecked:
                self.activeOptions.append(eachOption)

        return (self.activeOptions, self.checked, self.hasCheckedAncestors)

    def AddCheckedAndCheckedChildren(self, optionObject):
        anyAncestorWasChecked = False
        for child in optionObject.childrenOptions:
            ancestorWasChecked = self.AddCheckedAndCheckedChildren(child)
            anyAncestorWasChecked = anyAncestorWasChecked or ancestorWasChecked

        if anyAncestorWasChecked:
            self.hasCheckedAncestors.append(optionObject)
        if optionObject.IsChecked() and not optionObject.HasChildrenOptions():
            self.checked.append(optionObject)
        if optionObject.IsChecked() or anyAncestorWasChecked:
            return True
        return False


class OptionObject(object):

    def __init__(self, name, value, optionType, childrenOptions = None, defaultSetting = True, doSortChildren = True, *args):
        self.name = unicode(name)
        self.value = value
        self.optionType = optionType
        self.optionKey = self._GetOptionKey()
        self.isChecked = False
        self.defaultSetting = defaultSetting
        self.parentKey = None
        self.doSortChildren = doSortChildren
        self.SetChildren(childrenOptions)

    def SetChildren(self, childrenOptions):
        self.childrenOptions = childrenOptions or ()
        if self.doSortChildren:
            self.SortChildren()
        self.SetAsParentForChildren()

    def _GetOptionKey(self):
        v = self.value
        if isinstance(self.value, (tuple, list, set)):
            strValues = []
            for x in self.value:
                strValues.append(str(x))

            v = '_'.join(strValues)
        return (self.optionType, v)

    def SortChildren(self):
        if not self.HasChildrenOptions():
            return
        self.childrenOptions.sort(key=lambda x: x.name)

    def SetAsParentForChildren(self):
        for child in self.childrenOptions:
            child.SetParent(self.optionKey)

    def SetParent(self, parentKey):
        self.parentKey = parentKey

    def HasChildrenOptions(self):
        return bool(self.childrenOptions)

    def IsChecked(self):
        return self.isChecked

    def SetCheckedState(self, isChecked = True):
        self.isChecked = isChecked
