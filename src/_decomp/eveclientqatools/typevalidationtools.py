#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveclientqatools\typevalidationtools.py
import evetypes
from carbonui import fontconst, uiconst
from carbonui.control.combo import Combo
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveLabel import Label
from carbonui.control.checkbox import Checkbox
from carbonui.button.group import ButtonGroup
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from eve.client.script.ui.control.eveLabel import EveHeaderSmall
from eve.common.lib.appConst import defaultPadding
from eveclientqatools.typevalidationscripts import OPTION_BOOLEAN, OPTION_FLOAT, OPTION_STRING, validTestScripts
from eveclientqatools.typevalidationutils import RunTests, SplitStringIntoList, FilterPublished, RESULTMODE_FULL, RESULTMODE_FAILURES

class TypeValidationWindow(Window):
    default_caption = 'Type Validation Tools'
    default_windowID = 'TypeValidationWindow'
    default_width = 480
    default_height = 610
    default_minSize = (default_width, default_height)
    NONE_COMBO = ('Not used', None)

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.myPadding = (defaultPadding,
         8,
         150,
         0)
        self.LoadScripts()
        self.LoadCategories()
        self.resultOptions = [('Full Report', RESULTMODE_FULL), ('Only Failures', RESULTMODE_FAILURES)]
        self.activeResultMode = self.resultOptions[0][1]
        self.AddHeader('Select the types to be tested')
        self.SetupTypeSelectionPanel()
        self.AddHeader('Select the test script and options')
        self.SetupTestSelectionPanel()
        self.SetupTestOptionsPanel()
        self.LoadScriptOptions()
        self.SetupStartButton()
        self.SetInitialValues()

    def LoadScripts(self):
        self.testScripts = [ (script.displayName, script) for script in validTestScripts ]
        self.activeScript = self.testScripts[0][1]

    def LoadCategories(self):
        self.categories = [ (evetypes.GetCategoryNameByCategory(categoryID), categoryID) for categoryID in evetypes.IterateCategories() if categoryID is not 0 ]
        self.categories.sort()
        self.categories.insert(0, self.NONE_COMBO)
        self.activeCategory = None
        self.groups = [self.NONE_COMBO]
        self.activeGroup = None
        self.useOnlyPublished = 1

    def LoadScriptOptions(self):
        self.options = self.activeScript.options
        self.floatOptionEdit = {}
        self.stringOptionEdit = {}
        self.booleanOption = {}
        self.optionsCont.Flush()
        for optionKey, optionLabel, optionType, defaultValue in self.options:
            if optionType == OPTION_BOOLEAN:
                self.AddBooleanOptionField(optionKey, optionLabel, defaultValue)
            elif optionType == OPTION_FLOAT:
                self.AddFloatOptionField(optionKey, optionLabel, defaultValue)
            elif optionType == OPTION_STRING:
                self.AddStringOptionField(optionKey, optionLabel, defaultValue)

        self.AddResultOptions()
        self.resultOptionsCombo.SetValue(self.activeResultMode)

    def SetInitialValues(self):
        initialString = '34, 587'
        self.typeListEdit.SetValue(initialString)
        self.ChangeTypeList(initialString)

    def AddHeader(self, text):
        EveHeaderSmall(parent=self.sr.main, text=text, align=uiconst.TOTOP, padding=(8, 6, 0, 3))

    def SetupTypeSelectionPanel(self):
        typesCont = ContainerAutoSize(name='typesCont', parent=self.sr.main, align=uiconst.TOTOP, padLeft=4, padRight=4)
        self.typeListEdit = SingleLineEditText(parent=typesCont, name='typesEdit', align=uiconst.TOTOP, top=12, padding=(defaultPadding,
         defaultPadding,
         defaultPadding,
         0), label='Types', setvalue='', OnChange=self.ChangeTypeList, hint='Comma separated list of types, only used if no category selected. Non-existent types are filtered out')
        self.categoryCombo = Combo(label='Select Category', parent=typesCont, name='categoryCombo', align=uiconst.TOTOP, top=12, padding=self.myPadding, options=self.categories, callback=self.ChangeCategory, hint='Overrides the comma separated list.')
        self.groupCombo = Combo(label='Select Group', parent=typesCont, name='groupCombo', align=uiconst.TOTOP, top=12, padding=self.myPadding, options=self.groups, callback=self.ChangeGroup)
        self.publishedCheckbox = Checkbox(text='Use only published types', parent=typesCont, settingsKey='publishedCheckbox', checked=self.useOnlyPublished, align=uiconst.TOTOP, padding=self.myPadding, callback=self.ChangePublished)
        self.countHint = Label(text='Currently selected types: 0', parent=typesCont, align=uiconst.TOTOP, padding=self.myPadding, fontsize=fontconst.EVE_SMALL_FONTSIZE)

    def SetupTestSelectionPanel(self):
        testCont = ContainerAutoSize(name='testCont', parent=self.sr.main, align=uiconst.TOTOP, padLeft=4, padRight=4)
        testCombo = Combo(label='Select Test', parent=testCont, name='testCombo', left=15, top=12, width=200, options=self.testScripts, callback=self.ChangeScript)

    def SetupTestOptionsPanel(self):
        self.optionsCont = ContainerAutoSize(name='optionsCont', parent=self.sr.main, align=uiconst.TOTOP, padLeft=4, padRight=4)

    def AddFloatOptionField(self, optionKey, optionLabel, defaultValue):
        floatEdit = SingleLineEditText(parent=self.optionsCont, name=optionKey, align=uiconst.TOTOP, top=12, height=20, padding=self.myPadding, label=optionLabel, setvalue=str(defaultValue), floats=(None, None))
        self.floatOptionEdit[optionKey] = floatEdit

    def AddStringOptionField(self, optionKey, optionLabel, defaultValue):
        stringEdit = SingleLineEditText(parent=self.optionsCont, name=optionKey, align=uiconst.TOTOP, top=12, height=20, padding=self.myPadding, label=optionLabel, setvalue=str(defaultValue))
        self.stringOptionEdit[optionKey] = stringEdit

    def AddBooleanOptionField(self, optionKey, optionLabel, defaultValue):
        checkbox = Checkbox(parent=self.optionsCont, text=optionLabel, settingsKey=optionKey, checked=defaultValue, align=uiconst.TOTOP, padding=self.myPadding)
        self.booleanOption[optionKey] = checkbox

    def AddResultOptions(self):
        self.resultOptionsCombo = Combo(label='Select result mode', parent=self.optionsCont, name='resultOptionsCombo', align=uiconst.TOTOP, top=12, padding=self.myPadding, options=self.resultOptions, callback=self.ChangeResultMode)

    def SetupStartButton(self):
        ButtonGroup(btns=[('Start', self.ExecuteTest, ())], parent=self.sr.main)

    def ChangeTypeList(self, value):
        typeListString = value.strip()
        self.typeList = SplitStringIntoList(typeListString)
        self.UpdateCountHint()
        if self.typeList and self.activeCategory:
            self.ResetCategory()

    def ChangeCategory(self, combo, text, category):
        self.activeCategory = category
        if category is None:
            self.groups = [self.NONE_COMBO]
        else:
            self.groups = [ (evetypes.GetGroupNameByGroup(groupID), groupID) for groupID in evetypes.IterateGroups() if evetypes.GetCategoryIDByGroup(groupID) == category ]
            self.groups.sort()
            self.groups.insert(0, self.NONE_COMBO)
        self.ResetGroup()
        self.groupCombo.entries = self.groups
        self.ResetTypeString()
        self.typeList = list(evetypes.GetTypeIDsByCategory(category))
        self.UpdateCountHint()

    def ChangeGroup(self, combo, text, groupID):
        self.activeGroup = groupID
        if self.activeGroup:
            self.typeList = list(evetypes.GetTypeIDsByGroup(groupID))
        elif self.activeCategory:
            self.typeList = list(evetypes.GetTypeIDsByCategory(self.activeCategory))
        self.UpdateCountHint()

    def ChangePublished(self, cb):
        self.useOnlyPublished = cb.GetValue()
        self.UpdateCountHint()

    def ResetTypeString(self):
        self.typeListEdit.SetValue('')

    def ResetGroup(self):
        self.groupCombo.SetValue(None)
        self.activeGroup = None

    def ResetCategory(self):
        self.categoryCombo.SetValue(None)
        self.activeCategory = None
        self.ResetGroup()
        self.groupCombo.entries = [self.NONE_COMBO]

    def UpdateCountHint(self):
        count = len(FilterPublished(self.typeList, self.useOnlyPublished))
        text = 'Currently selected types: %s' % count
        if count > 50:
            text = '<color=0xffff8080>WARNING! MANY TYPES SELECTED! %s</color>' % text
        self.countHint.text = text

    def ChangeScript(self, combo, text, value):
        self.activeScript = value
        self.LoadScriptOptions()

    def ChangeResultMode(self, combo, text, value):
        self.activeResultMode = value

    def GetOptions(self):
        vars = {}
        for optionKey, optionLabel, optionType, defaultValue in self.options:
            if optionType == OPTION_BOOLEAN:
                vars[optionKey] = self.booleanOption[optionKey].GetValue()
            elif optionType == OPTION_FLOAT:
                vars[optionKey] = self.floatOptionEdit[optionKey].GetValue()
            elif optionType == OPTION_STRING:
                vars[optionKey] = self.stringOptionEdit[optionKey].GetValue()

        return vars

    def ExecuteTest(self):
        finalTypeList = FilterPublished(self.typeList, self.useOnlyPublished)
        vars = self.GetOptions()
        script = self.activeScript()
        testFunc = script.Validate
        formattedResult = RunTests(testFunc, finalTypeList, self.activeResultMode, **vars)
        ResultDialog(result=formattedResult)


class ResultDialog(Window):
    default_caption = 'Type Validation Results'
    default_windowID = 'TypeValidationResults'
    default_width = 480
    default_height = 300
    default_minSize = (default_width, default_height)

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.AddHeader('Results')
        self.SetupResultPanel(attributes.result)
        self.SetupCloseButton()

    def AddHeader(self, text):
        EveHeaderSmall(parent=self.sr.main, text=text, align=uiconst.TOTOP, padding=(8, 6, 0, 3))

    def SetupResultPanel(self, result):
        resCont = Container(name='resCont', parent=self.sr.main, align=uiconst.TOALL, padLeft=4, padRight=4, height=50)
        self.resultsText = EditPlainText(name='resultsText', setvalue=result, parent=resCont, readonly=True)

    def SetupCloseButton(self):
        ButtonGroup(btns=[('Close', self.Close, ())], parent=self.sr.main)
