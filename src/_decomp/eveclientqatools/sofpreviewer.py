#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveclientqatools\sofpreviewer.py
import re
import blue
import carbonui.fontconst
import carbonui.const as uiconst
import evegraphics.utils as gfxutils
import eveSpaceObject.spaceobjanimation as soanimation
from carbonui.control.combo import Combo
from carbonui.control.singlelineedits.singleLineEditFloat import SingleLineEditFloat
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.button.group import ButtonGroup
from carbonui.control.checkbox import Checkbox
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.control.window import Window
from carbonui.decorative.panelUnderlay import PanelUnderlay
from eve.client.script.ui.shared.preview import PreviewContainer
from carbonui.primitives.container import Container
from carbonui.primitives.gridcontainer import GridContainer
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.line import Line
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.control.slider import Slider
import fsdBuiltData.common.graphicMaterialSets as graphicMaterialSets
from shipskins.static import SkinMaterialStorage
from sofDnaLibrary.query import GetDnaStringsMatchingQuery
MAX_MULTI_HULLS = 4
MULTI_HULL_REGEX = re.compile('_s\\dv\\d')
MULTI_HULL_VARIATION_REGEX = re.compile('v\\d')
MULTI_HULL_SPECIFICATION_REGEX = re.compile('_s\\d')
DEFAULT_FACTION_FOR_T2HULLS = {'ardishapur': ['ac2_t2b',
                'ai2_t2',
                'af5_t2',
                'ab2_t2',
                'af2_t2',
                'ac4_t2'],
 'brutor': ['mf1_t2a',
            'mcb1_t2c',
            'mf5_t2a',
            'mc3_t2a',
            'mf7_t2c',
            'mc2_t2a',
            'mbc2_t2',
            'mb2_t2',
            'mf4_t2a',
            'mdh1_t2',
            'mdl1_t2',
            'mdm1_t2',
            'msd1_t2'],
 'creodron': ['gfr1_t2',
              'gbc2_t2',
              'gf5_t2',
              'gf4_t2a',
              'gc3_t2',
              'gb1_t2',
              'gdh1_t2',
              'gdl1_t2',
              'gdm1_t2',
              'gsd1_t2'],
 'development': ['oref1_t2b'],
 'duvolle': ['gc1_t2a',
             'gbc1_t2a',
             'gc4_t2a',
             'gf7_t2',
             'gb2_t2',
             'gf3_t2',
             'gf6_t2b',
             'gi4_t2'],
 'ishukone': ['cf3_t2',
              'cc2_t2b',
              'cc4_t2a',
              'cf7_t2b',
              'cfr1_t2',
              'cbc1_t2b'],
 'kaalakiota': ['ci2_t2',
                'cf2_t2a',
                'cde1_t2',
                'cbc2_t2',
                'cc2_t2a',
                'cc4_t2b',
                'cb2_t2'],
 'khanid': ['af7_t2',
            'ac1_t2a',
            'abc1_t2a',
            'ade1_t2',
            'ai1_t2',
            'af4_t2a',
            'ac2_t2a',
            'af3_t2a'],
 'laidai': ['cc1_t2',
            'ci3_t2',
            'cc3_t2',
            'cb1_t2',
            'cf7_t2a',
            'cf4_t2',
            'cf6_t2',
            'cf2_t2b',
            'cdh1_t2',
            'cdl1_t2',
            'cdm1_t2',
            'csd1_t2'],
 'orebase': ['oredh1_t2'],
 'prospecting': ['oreba3_t2', 'oreba2_t2', 'oreba1_t2'],
 'roden': ['gf6_t2a',
           'gf4_t2b',
           'gde1_t2',
           'gc1_t2b',
           'gi2_t2',
           'gc2_t2',
           'gc4_t2b'],
 'sarum': ['abc_t2',
           'afr1_t2',
           'af4_t2b',
           'ac3_t2',
           'ab1_t2',
           'ac1_t2b',
           'af3_t2b',
           'adh1_t2',
           'adl1_t2',
           'adm1_t2',
           'asd1_t2'],
 'sebiestor': ['mc2_t2c',
               'mi3_t2c',
               'mc3_t2c',
               'mde1_t2c',
               'mc4_t2c',
               'mf1_t2c'],
 'thukker': ['mf2_t2b',
             'mf4_t2b',
             'mi2_t2b',
             'mfr1_t2',
             'mb1_t2b',
             'mc1_t2b']}

def GetGenericName(label):
    return label.replace(' ', '_').replace(':', '').strip().lower()


def _CreateCheckbox(name, checkboxLabel, checkboxCallback, parent, align = uiconst.TOLEFT):
    return Checkbox(name=name + '_constraint', align=align, width=75, height=18, padLeft=10, parent=parent, text=checkboxLabel, callback=checkboxCallback)


def _CreateCombo(name, values, callback, select, label, parent, align = uiconst.TOLEFT, width = 150):
    return Combo(name=name + '_combo', align=align, width=width, height=18, parent=parent, label=label, options=[ (name, i) for i, name in enumerate(values) ], callback=callback, select=select)


def _CreateInput(name, value, callback, label, parent, align = uiconst.TOLEFT):
    return SingleLineEditText(name=name + '_input', align=align, label=label, parent=parent, width=150, height=18, setvalue=value, OnFocusLost=callback, OnReturn=callback)


def _CreateSlider(name, label, minValue, maxValue, startVal, valueChangeFunc, parent, align = uiconst.TOLEFT):
    return Slider(name=name, align=align, label=label, parent=parent, width=150, height=18, minValue=minValue, maxValue=maxValue, value=startVal, on_dragging=valueChangeFunc, callback=valueChangeFunc)


def _CreateContainer(name, parent, padTop = 16, padBottom = 0):
    return Container(name=name + '_container', parent=parent, align=uiconst.TOTOP, height=18, padTop=padTop, padBottom=padBottom, padLeft=5, padRight=5)


def CreateDropdownWithCheckbox(label, values, select, dropdownCallback, checkboxLabel, checkboxCallback, parent):
    name = GetGenericName(label)
    container = _CreateContainer(name, parent)
    dropdown = _CreateCombo(name, values, dropdownCallback, select, label, container)
    checkbox = _CreateCheckbox(name, checkboxLabel, checkboxCallback, container)
    return (dropdown, checkbox)


def CreateDropdown(label, values, callback, select, parent, align = uiconst.TOLEFT):
    name = GetGenericName(label)
    container = _CreateContainer(name, parent)
    combo = _CreateCombo(name, values, callback, select, label, container, align)
    return combo


def CreateInput(label, value, callback, parent, align = uiconst.TOLEFT):
    name = GetGenericName(label)
    container = _CreateContainer(name, parent)
    inputField = _CreateInput(name, value, callback, label, container, align)
    return inputField


def CreateSlider(label, minValue, maxValue, startValue, valueChangedFunc, parent):
    name = GetGenericName(label)
    container = _CreateContainer(name, parent, padTop=0, padBottom=16)
    slider = _CreateSlider(name, label, minValue, maxValue, startValue, valueChangedFunc, container)
    return slider


def GetMultiHullInfo(hull):
    results = MULTI_HULL_REGEX.findall(hull)
    if len(results) > 0:
        return (hull.replace(results[0], ''), GetMultiHullSpecification(hull), GetMultiHullVariation(hull))
    return (None, None, None)


def GetMultiHullVariation(hull):
    return int(MULTI_HULL_VARIATION_REGEX.findall(hull)[0].replace('v', ''))


def GetMultiHullSpecification(hull):
    return int(MULTI_HULL_SPECIFICATION_REGEX.findall(hull)[0].replace('_s', ''))


def GetMultiHullBaseName(hull):
    results = MULTI_HULL_REGEX.findall(hull)
    if len(results) > 0:
        result = results[0]
        return hull.replace(result, '')
    return ''


def IsMultiHull(hull):
    return len(MULTI_HULL_REGEX.findall(hull)) > 0


class StateMachineController:

    def __init__(self):
        self._states = {}
        self._currentStates = {}
        self._model = None
        self._variables = {}
        self._variableTypes = {}
        self._variableEnumValues = {}

    def _ClearAll(self):
        self._states = {}
        self._currentStates = {}
        self._model = None

    def SetupForHullAndModel(self, hull, model):
        self._ClearAll()
        self._model = model
        soanimation.TriggerDefaultStates(model)
        self._variables = {}
        for each in self._model.controllers:
            for var in getattr(each, 'variables', []):
                self._variables[var.name] = var.value
                self._variableTypes[var.name] = var.variableType
                self._variableEnumValues[var.name] = var.enumValues

    def GetVariables(self):
        return self._variables

    def GetVariableType(self, name):
        return self._variableTypes.get(name, 0)

    def GetEnumValues(self, name):
        if self._variableTypes.get(name, 0) != 3:
            return []
        result = []
        for each in self._variableEnumValues.get(name, '').split(','):
            try:
                k, v = each.strip().rsplit('=', 1)
                v = float(v)
            except ValueError:
                continue

            result.append((k, v))

        return result

    def SetVariable(self, name, value):
        self._variables[name] = float(value)
        self._model.SetControllerVariable(name, float(value))

    def ApplyTo(self, model):
        for name, value in self._variables.items():
            model.SetControllerVariable(name, value)


class SOFPreviewWindow:

    def __init__(self):
        self.name = 'SOF Preview Window'
        self.windowID = 'SOFPreviewWindow_ ' + self.name
        self.previewCont = None
        dna = self.GetDnaFromPlayerShip()
        multiHulls = dna.split(':')[0].split(';')
        self.currentHulls = [ (None if i >= len(multiHulls) else multiHulls[i]) for i in xrange(0, MAX_MULTI_HULLS) ]
        self.currentFaction = dna.split(':')[1]
        self.currentRace = dna.split(':')[2]
        self.currentMat = ['None',
         'None',
         'None',
         'None']
        self.currentPatternMat = ['None', 'None']
        self.currentVariant = 'None'
        self.currentPattern = 'None'
        self.currentDirtLevel = None
        self.currentResPathInsert = None
        self.constrainToFaction = False
        self.constrainToHull = False
        self.constrainToRace = False
        self.constrainToPattern = False
        self.updateShip = True
        self.stateMachineController = StateMachineController()

    def _OnApplyButton(self, *args):
        self._UpdatePlayerShip()

    def _OnCopyDnaButton(self, *args):
        blue.pyos.SetClipboardData(self.GetPreviewDna())

    def ShowUI(self):
        Window.CloseIfOpen(windowID=self.windowID)
        wnd = Window.Open(windowID=self.windowID)
        wnd.SetMinSize([800, 500])
        wnd.SetCaption(self.name)
        main = wnd.GetMainArea()
        sofDB = blue.resMan.LoadObject('res:/dx9/model/spaceobjectfactory/data.red')
        self.sofFactions = []
        for faction in sofDB.faction:
            self.sofFactions.append(faction.name)

        self.sofFactions.sort()
        self.sofHulls = []
        self.multihulls = {}
        for hull in sofDB.hull:
            hull = hull.name
            if IsMultiHull(hull):
                baseHullName, subpart, variation = GetMultiHullInfo(hull)
                if baseHullName not in self.multihulls:
                    self.multihulls[baseHullName] = []
                self.multihulls[baseHullName].append((hull, subpart, variation))
                if subpart == 1:
                    self.sofHulls.append(hull)
            else:
                self.sofHulls.append(hull)

        self.sofHulls.sort()
        self.sofRaces = []
        for race in sofDB.race:
            self.sofRaces.append(race.name)

        self.sofRaces.sort()
        self.sofMaterials = []
        for material in sofDB.material:
            self.sofMaterials.append(material.name)

        self.sofMaterials.sort()
        self.sofMaterials.insert(0, 'None')
        self.sofVariants = []
        for i in xrange(len(sofDB.generic.variants)):
            self.sofVariants.append(sofDB.generic.variants[i].name)

        self.sofVariants.sort()
        self.sofVariants.insert(0, 'None')
        self.sofPatterns = []
        self.patternToHulls = {}
        for pattern in sofDB.pattern:
            self.sofPatterns.append(pattern.name)
            self.patternToHulls[pattern.name] = [ hull.name for hull in pattern.projections ]

        self.sofPatterns.sort()
        self.sofPatterns.insert(0, 'None')
        headerCont = Container(name='headerCont', parent=main, align=uiconst.TOTOP, height=30)
        self.dnaLabel = EveLabelSmall(name='dnaLabel', align=uiconst.CENTER, parent=headerCont, text='')
        self.SetupButtonContainer(main)
        self.SetupInputContainers(main)
        self.previewCont = PreviewContainer(parent=main, align=uiconst.TOALL)
        self.previewCont.PreviewSofDna(self.GetPreviewDna())
        self._ReloadStateMachineOptions()

    def SetupButtonContainer(self, parent):
        buttonContainer = Container(name='_buttonCont', parent=parent, align=uiconst.TOBOTTOM, height=20, padBottom=10)
        buttonGroup = ButtonGroup(name='buttonGroup', parent=buttonContainer, align=uiconst.CENTER, fontsize=carbonui.fontconst.EVE_MEDIUM_FONTSIZE)
        buttonGroup.AddButton('Copy DNA', self._OnCopyDnaButton)
        buttonGroup.AddButton('Apply', self._OnApplyButton)

    def SetupInputContainers(self, parent):
        inputContainer = GridContainer(name='inputCont', parent=parent, align=uiconst.TOBOTTOM, height=250, lines=1, columns=3)
        self.SetupLeftContainer(inputContainer)
        self.SetupCenterContainer(inputContainer)
        self.SetupRightContainer(inputContainer)

    def SetupLeftContainer(self, inputContainer):
        _leftContainer = Container(name='_leftContainer', parent=inputContainer)
        leftContainer = Container(name='leftContainer', parent=_leftContainer, align=uiconst.TORIGHT, height=250, width=250)
        selectedRace = self.GetComboListIndex(self.sofRaces, self.currentRace)
        self.raceCombo, self.raceConstraint = CreateDropdownWithCheckbox('Race:', self.sofRaces, selectedRace, self.OnRaceComboChange, 'Constrained', self.OnRaceConstraintChanged, leftContainer)
        selectedHull = self.GetComboListIndex(self.sofHulls, self.currentHulls[0])
        self.hullCombos = []
        firstHullCombo, self.hullConstraint = CreateDropdownWithCheckbox('Hull:', self.sofHulls, selectedHull, self.OnHullComboChange, 'Constrained', self.OnHullConstraintChanged, leftContainer)
        self.hullCombos.append(firstHullCombo)
        self.multiHullContainer = Container(name='multiHulls', parent=leftContainer, align=uiconst.TOTOP, height=35 * (MAX_MULTI_HULLS - 1))
        for i in xrange(1, MAX_MULTI_HULLS):
            self.hullCombos.append(CreateDropdown('Hull %d:' % (i + 1), [], self.OnSpecificationChanges, self.currentHulls[i], self.multiHullContainer, align=uiconst.TOALL))

        self.multiHullContainer.display = False
        selectedFaction = self.GetComboListIndex(self.sofFactions, self.currentFaction)
        self.factionCombo, self.factionConstraint = CreateDropdownWithCheckbox('Faction:', self.sofFactions, selectedFaction, self.OnFactionComboChange, 'Constrained', self.OnFactionConstraintChanged, leftContainer)
        selectedPattern = self.GetComboListIndex(self.sofPatterns, self.currentPattern)
        self.patternCombo, self.patternConstraint = CreateDropdownWithCheckbox('Pattern:', self.sofPatterns, selectedPattern, self.OnPatternComboChange, 'Constrained', self.OnPatternConstraintChanged, leftContainer)
        previewContainer = Container(parent=leftContainer, align=uiconst.TOALL, padTop=16)
        self.previewImage = Sprite(parent=previewContainer, align=uiconst.CENTER, width=64, height=64)
        self.skinUnavailableLabel = EveLabelSmall(name='skinUnavailableLabel', align=uiconst.CENTERBOTTOM, parent=leftContainer, text='No skin license available', display=False)
        self.UpdateIcon()

    def SetupCenterContainer(self, inputContainer):
        _centerContainer = Container(name='_centerContainer', parent=inputContainer)
        centerContainer = Container(name='centerContainer', parent=_centerContainer, align=uiconst.CENTERTOP, height=250, width=250)
        self.matCombo1 = CreateDropdown('Material 1:', self.sofMaterials, self.OnMat1ComboChange, self.GetComboListIndex(self.sofMaterials, self.currentMat[0]), centerContainer, align=uiconst.CENTER)
        self.matCombo2 = CreateDropdown('Material 2:', self.sofMaterials, self.OnMat2ComboChange, self.GetComboListIndex(self.sofMaterials, self.currentMat[1]), centerContainer, align=uiconst.CENTER)
        self.matCombo3 = CreateDropdown('Material 3:', self.sofMaterials, self.OnMat3ComboChange, self.GetComboListIndex(self.sofMaterials, self.currentMat[2]), centerContainer, align=uiconst.CENTER)
        self.matCombo4 = CreateDropdown('Material 4:', self.sofMaterials, self.OnMat4ComboChange, self.GetComboListIndex(self.sofMaterials, self.currentMat[3]), centerContainer, align=uiconst.CENTER)
        self.matCombo5 = CreateDropdown('Pattern Material 1:', self.sofMaterials, self.OnPatternMat1ComboChange, self.GetComboListIndex(self.sofMaterials, self.currentPatternMat[0]), centerContainer, align=uiconst.CENTER)
        self.matCombo6 = CreateDropdown('Pattern Material 2:', self.sofMaterials, self.OnPatternMat2ComboChange, self.GetComboListIndex(self.sofMaterials, self.currentPatternMat[1]), centerContainer, align=uiconst.CENTER)

    def SetupRightContainer(self, inputContainer):
        _rightContainer = Container(name='_rightContainer', parent=inputContainer)
        rightContainer = Container(name='rightContainer', parent=_rightContainer, align=uiconst.TOLEFT, height=250, width=250)
        self.dirtSlider = CreateSlider('Dirt', 0.0, 100.0, 50.0, self.OnDirtSliderChange, rightContainer)
        self.UpdateDirtSliderLabel()
        self.materialSetIDCombo, self.materialSetFilteredByRace = CreateDropdownWithCheckbox('materialSetID', [], 0, self.OnMaterialSetIDChange, 'Filter By Race', self.OnMaterialSetFiltered, rightContainer)
        self._FilterMaterialSet(False)
        self.resPathInsertEdit = CreateInput('resPathInsert', '', self.OnResPathInsertChange, rightContainer)
        self.variantCombo = CreateDropdown('Variants:', self.sofVariants, self.OnVariantComboChange, self.GetComboListIndex(self.sofVariants, self.currentVariant), rightContainer)
        self.controllerParent = Container(parent=rightContainer, align=uiconst.TOTOP, height=68, padTop=16, padLeft=5, padRight=5)
        self.controllers = None

    @staticmethod
    def GetComboListIndex(comboContentList, name):
        for index, each in enumerate(comboContentList):
            if each.lower() == name.lower():
                return index

    def GetCurrentHull(self):
        currentHull = self.currentHulls[0]
        if IsMultiHull(currentHull):
            currentHull += ';' + ';'.join((hull for hull in self.currentHulls[1:] if hull is not None))
        return currentHull

    def GetPreviewDna(self):
        dna = self.GetCurrentHull() + ':' + self.currentFaction + ':' + self.currentRace
        if any((x != 'None' for x in self.currentMat)):
            dna += ':material?' + str(self.currentMat[0]) + ';' + str(self.currentMat[1]) + ';' + str(self.currentMat[2]) + ';' + str(self.currentMat[3])
        if self.currentResPathInsert is not None:
            dna += ':respathinsert?' + str(self.currentResPathInsert)
        if self.currentVariant != 'None':
            dna += ':variant?' + str(self.currentVariant)
        if self.currentPattern != 'None':
            dna += ':pattern?' + str(self.currentPattern) + ';' + str(self.currentPatternMat[0]) + ';' + str(self.currentPatternMat[1])
        self.dnaLabel.text = dna
        return dna

    @staticmethod
    def GetDnaFromPlayerShip():
        michelle = sm.GetService('michelle')
        ship = michelle.GetBall(session.shipid)
        if ship is None:
            return 'ab1_t1:amarrbase:amarr'
        dna = ship.GetDNA()
        if dna is None:
            return 'ab1_t1:amarrbase:amarr'
        return dna

    def UpdateDirtSliderLabel(self):
        dirtLevel = gfxutils.RemapDirtLevel(self.dirtSlider.GetValue())
        self.dirtSlider.SetLabel('Dirt level: ' + str(dirtLevel))

    def OnDirtSliderChange(self, slider):
        self.currentDirtLevel = gfxutils.RemapDirtLevel(slider.GetValue())
        self.UpdateDirtSliderLabel()
        self._UpdatePreviewShip()

    def OnFactionConstraintChanged(self, checkbox):
        self.constrainToFaction = checkbox.GetValue()
        self.ConstrainDnaSelection()

    def OnRaceConstraintChanged(self, checkbox):
        self.constrainToRace = checkbox.GetValue()
        self.ConstrainDnaSelection()

    def OnHullConstraintChanged(self, checkbox):
        self.constrainToHull = checkbox.GetValue()
        self.ConstrainDnaSelection()

    def OnPatternConstraintChanged(self, checkbox):
        self.constrainToPattern = checkbox.GetValue()
        self.ConstrainDnaSelection()

    def OnMaterialSetFiltered(self, checkbox):
        materialSetFiltered = checkbox.GetValue()
        self._FilterMaterialSet(materialSetFiltered)

    def _FilterMaterialSet(self, filterByRace):
        materialSets = graphicMaterialSets.GetGraphicMaterialSets()
        availableMaterialSets = []
        for materialSetID, materialSet in materialSets.iteritems():
            if filterByRace:
                raceHint = graphicMaterialSets.GetSofRaceHint(materialSet)
                if raceHint and raceHint == self.raceCombo.GetKey():
                    availableMaterialSets.append((materialSetID, materialSet.description))
            else:
                availableMaterialSets.append((materialSetID, materialSet.description))

        availableMaterialSets = sorted(availableMaterialSets, key=lambda x: x[0])
        options = [('None', -1)] + [ ('%s: %s' % keyAndDesc, keyAndDesc[0]) for keyAndDesc in availableMaterialSets ]
        self.materialSetIDCombo.LoadOptions(options)
        self.TrySettingComboValue(self.materialSetIDCombo, 0)

    def ConstrainDnaSelection(self):
        raceQuery = '.*'
        factionQuery = '.*'
        hullQuery = '.*'
        if self.constrainToFaction:
            factionQuery = self.factionCombo.GetKey()
        if self.constrainToHull:
            hullQuery = self.hullCombos[0].GetKey()
        if self.constrainToRace:
            raceQuery = self.raceCombo.GetKey()
        if self.constrainToPattern and self.currentPattern != 'None':
            self.currentHulls[0] = self.TrySettingComboOptions(self.hullCombos[0], self.patternToHulls[self.currentPattern], self.currentHulls[0])
        if not self.constrainToFaction and not self.constrainToHull and not self.constrainToRace and not self.constrainToPattern:
            self.currentFaction = self.TrySettingComboOptions(self.factionCombo, self.sofFactions, self.GetDefaultFactionForHull())
            self.currentRace = self.TrySettingComboOptions(self.raceCombo, self.sofRaces, self.currentRace)
            self.currentHulls[0] = self.TrySettingComboOptions(self.hullCombos[0], self.sofHulls, self.currentHulls[0])
            self.currentPattern = self.TrySettingComboOptions(self.patternCombo, self.sofPatterns, self.currentPattern)
        else:
            dnaList = GetDnaStringsMatchingQuery(hullQuery, factionQuery, raceQuery)
            selectableRaces = []
            selectableFactions = []
            selectableHulls = []
            for dna in dnaList:
                dnaElements = dna.split(':')
                hull = dnaElements[0]
                faction = dnaElements[1]
                race = dnaElements[2]
                if faction not in selectableFactions:
                    selectableFactions.append(faction)
                if race not in selectableRaces:
                    selectableRaces.append(race)
                if hull not in selectableHulls:
                    selectableHulls.append(hull)

            if not self.constrainToPattern:
                selectablePatterns = [ patternName for patternName, hulls in self.patternToHulls.iteritems() for hullName in selectableHulls if hullName in hulls ]
                selectablePatterns = list(set(selectablePatterns))
                selectablePatterns.insert(0, 'None')
                self.currentPattern = self.TrySettingComboOptions(self.patternCombo, selectablePatterns, self.currentPattern)
            elif self.currentPattern != 'None':
                selectableHullsBasedOfPattern = set(self.patternToHulls[self.currentPattern])
                selectableHulls = list(set(selectableHulls).intersection(selectableHullsBasedOfPattern))
            if not self.constrainToHull:
                self.currentHulls[0] = self.TrySettingComboOptions(self.hullCombos[0], selectableHulls, self.currentHulls[0])
                self.ShowMultiHullComboBoxes(self.currentHulls[0])
            if not self.constrainToFaction:
                self.currentFaction = self.TrySettingComboOptions(self.factionCombo, selectableFactions, self.GetDefaultFactionForHull())
            if not self.constrainToRace:
                self.currentRace = self.TrySettingComboOptions(self.raceCombo, selectableRaces, self.currentRace)
            if not self.constrainToPattern and self.constrainToHull:
                availablePatterns = [ pattern for pattern, hulls in self.patternToHulls.iteritems() if self.currentHulls[0] in hulls ]
                availablePatterns.insert(0, 'None')
                self.currentPattern = self.TrySettingComboOptions(self.patternCombo, availablePatterns, self.currentPattern)
        self._UpdatePreviewShip()

    def GetDefaultFactionForHull(self):
        if self.currentHulls[0].endswith('t2'):
            return self._GetDefaultFactionForT2Hull(self.currentHulls[0])
        else:
            return self._GetDefaultFactionForT1Hull(self.currentHulls[0])

    def UpdateIcon(self):
        path = None
        id = self.GetCurrentMaterialSetID()
        for mid, m in SkinMaterialStorage().iteritems():
            if m.materialSetID == id:
                path = 'res:/UI/Texture/classes/skins/icons/%s.png' % mid
                break

        self.skinUnavailableLabel.display = path is None
        if path is None:
            path = 'res:/UI/Texture/notavailable.dds'
        self.previewImage.texture.resPath = path

    @staticmethod
    def _GetDefaultFactionForT1Hull(hullName):
        dnaList = GetDnaStringsMatchingQuery(hullName)
        if len(dnaList) == 0:
            return ''
        race = dnaList[0].split(':')[2]
        return race + 'base'

    @staticmethod
    def _GetDefaultFactionForT2Hull(hullName):
        for factionName, hullList in DEFAULT_FACTION_FOR_T2HULLS.iteritems():
            if hullName in hullList:
                return factionName

        return ''

    def GetCurrentMaterialSetID(self):
        if not hasattr(self, 'materialSetIDCombo'):
            return -1
        return self.materialSetIDCombo.GetValue()

    def GetCurrentMaterialSet(self):
        materialSetID = self.GetCurrentMaterialSetID()
        print 'trying to find materialset for ' + str(materialSetID)
        materialSet = graphicMaterialSets.GetGraphicMaterialSet(materialSetID)
        return materialSet

    def ShowMultiHullComboBoxes(self, hull):
        isMultiHull = IsMultiHull(hull)
        self.multiHullContainer.display = isMultiHull
        if isMultiHull:
            baseHullName = GetMultiHullBaseName(hull)
            for i in xrange(1, MAX_MULTI_HULLS):
                availableHulls = [ hull for hull, specification, variation in sorted(self.multihulls[baseHullName], key=lambda x: x[2]) if specification == i + 1 ]
                self.TrySettingComboOptions(self.hullCombos[i], availableHulls, self.currentPattern)
                self.currentHulls[i] = availableHulls[0]

        else:
            for i in xrange(1, MAX_MULTI_HULLS):
                self.currentHulls[i] = None

    def TrySettingComboOptions(self, comboBox, options, selectedValue):
        options = sorted(options)
        if 'None' in options:
            o = options.pop(options.index('None'))
            options.insert(0, o)
        optionTuple = [ (name, i) for i, name in enumerate(options) ]
        comboBox.LoadOptions(optionTuple)
        return self.TrySettingComboValue(comboBox, selectedValue)

    def TrySettingComboValue(self, comboBox, selectedValue):
        try:
            comboBox.SelectItemByLabel(selectedValue)
        except RuntimeError:
            comboBox.SelectItemByIndex(0)
            print "Could not select '%s', defaulting to '%s'" % (selectedValue, comboBox.GetKey())

        return comboBox.GetKey()

    def IsMaterialSetSelected(self):
        return self.materialSetIDCombo.GetKey() != 'None'

    def OnPatternComboChange(self, comboBox, pattern, value):
        self.currentPattern = pattern
        if self.constrainToPattern:
            self.ConstrainDnaSelection()
        self._UpdatePreviewShip()

    def OnFactionComboChange(self, comboBox, faction, value):
        self.currentFaction = faction
        if self.constrainToFaction:
            self.ConstrainDnaSelection()
        self._UpdatePreviewShip()

    def OnHullComboChange(self, comboBox, hull, value):
        self.currentHulls[0] = hull
        self.ShowMultiHullComboBoxes(hull)
        if self.constrainToHull:
            self.ConstrainDnaSelection()
        self._UpdatePreviewShip()

    def OnSpecificationChanges(self, comboBox, hull, value):
        specification = GetMultiHullSpecification(hull)
        self.currentHulls[specification - 1] = hull
        self._UpdatePreviewShip()

    def OnRaceComboChange(self, comboBox, race, value):
        self.currentRace = race
        if self.constrainToRace:
            self.ConstrainDnaSelection()
        if self.materialSetFilteredByRace.GetValue():
            self._FilterMaterialSet(self.currentRace)
        self._UpdatePreviewShip()

    def OnMat1ComboChange(self, comboBox, material, value):
        self.currentMat[0] = material
        self._UpdatePreviewShip()

    def OnMat2ComboChange(self, comboBox, material, value):
        self.currentMat[1] = material
        self._UpdatePreviewShip()

    def OnMat3ComboChange(self, comboBox, material, value):
        self.currentMat[2] = material
        self._UpdatePreviewShip()

    def OnMat4ComboChange(self, comboBox, material, value):
        self.currentMat[3] = material
        self._UpdatePreviewShip()

    def OnPatternMat1ComboChange(self, comboBox, material, value):
        self.currentPatternMat[0] = material
        self._UpdatePreviewShip()

    def OnPatternMat2ComboChange(self, comboBox, material, value):
        self.currentPatternMat[1] = material
        self._UpdatePreviewShip()

    def OnVariantComboChange(self, comboBox, variant, value):
        self.currentVariant = variant
        self._UpdatePreviewShip()

    def OnMaterialSetIDChange(self, *args):
        self.updateShip = False
        materialSet = self.GetCurrentMaterialSet()
        faction = graphicMaterialSets.GetSofFactionName(materialSet)
        if not faction:
            dna = self.GetDnaFromPlayerShip()
            if dna.split(':')[0] == self.GetCurrentHull():
                faction = dna.split(':')[1]
        if faction:
            try:
                self.factionCombo.SelectItemByLabel(faction)
            except RuntimeError:
                if materialSet is not None:
                    print "Removing constraints because '%s' is not in the constrained faction list" % materialSet.sofFactionName
                self.constrainToFaction = False
                self.constrainToRace = False
                self.constrainToHull = False
                self.constrainToPattern = False
                self.factionConstraint.SetValue(False)
                self.raceConstraint.SetValue(False)
                self.hullConstraint.SetValue(False)
                self.patternConstraint.SetValue(False)
                self.ConstrainDnaSelection()

            self.factionCombo.SelectItemByLabel(faction)
            self.OnFactionComboChange(self.factionCombo, faction, None)
        material1 = graphicMaterialSets.GetMaterial1(materialSet, 'None')
        idx = self.GetComboListIndex(self.sofMaterials, material1)
        self.matCombo1.SelectItemByValue(idx)
        self.OnMat1ComboChange(self.matCombo1, material1, idx)
        material2 = graphicMaterialSets.GetMaterial2(materialSet, 'None')
        idx = self.GetComboListIndex(self.sofMaterials, material2)
        self.matCombo2.SelectItemByValue(idx)
        self.OnMat2ComboChange(self.matCombo2, material2, idx)
        material3 = graphicMaterialSets.GetMaterial3(materialSet, 'None')
        idx = self.GetComboListIndex(self.sofMaterials, material3)
        self.matCombo3.SelectItemByValue(idx)
        self.OnMat3ComboChange(self.matCombo3, material3, idx)
        material4 = graphicMaterialSets.GetMaterial4(materialSet, 'None')
        idx = self.GetComboListIndex(self.sofMaterials, material4)
        self.matCombo4.SelectItemByValue(idx)
        self.OnMat4ComboChange(self.matCombo4, material4, idx)
        patternmaterial1 = graphicMaterialSets.GetCustomMaterial1(materialSet, 'None')
        idx = self.GetComboListIndex(self.sofMaterials, patternmaterial1)
        self.matCombo5.SelectItemByValue(idx)
        self.OnPatternMat1ComboChange(self.matCombo5, patternmaterial1, idx)
        patternmaterial2 = graphicMaterialSets.GetCustomMaterial2(materialSet, 'None')
        idx = self.GetComboListIndex(self.sofMaterials, patternmaterial2)
        self.matCombo6.SelectItemByValue(idx)
        self.OnPatternMat2ComboChange(self.matCombo6, patternmaterial2, idx)
        self.resPathInsertEdit.SetValue(graphicMaterialSets.GetResPathInsert(materialSet, ''))
        self.OnResPathInsertChange()
        sofPatternName = graphicMaterialSets.GetSofPatternName(materialSet, 'None')
        idx = self.GetComboListIndex(self.sofPatterns, sofPatternName)
        self.patternCombo.SelectItemByValue(idx)
        self.OnPatternComboChange(self.patternCombo, sofPatternName, idx)
        self.updateShip = True
        self._UpdatePreviewShip()
        self.UpdateIcon()

    def OnResPathInsertChange(self, *args):
        resPathInsert = self.resPathInsertEdit.GetValue()
        print 'new respathinsert: ' + resPathInsert
        if len(resPathInsert) == 0:
            self.currentResPathInsert = None
        else:
            self.currentResPathInsert = resPathInsert
        self._UpdatePreviewShip()

    def _UpdatePreviewShip(self):
        if self.previewCont is not None and self.updateShip:
            self.previewCont.PreviewSofDna(self.GetPreviewDna(), dirt=self.currentDirtLevel)
            self._ReloadStateMachineOptions()

    def _ReloadStateMachineOptions(self):
        model = self.previewCont.context.GetModel()
        hull = self.GetCurrentHull()
        self.stateMachineController.SetupForHullAndModel(hull, model)
        self._RefreshControllerVariables()

    def _OnControllerVariable(self, edit):
        edit.SetText(edit.text, 1)
        name = edit.name
        value = float(edit.text)
        self.stateMachineController.SetVariable(name, value)

    def _OnControllerBoolVariable(self, cb):
        name = cb.name
        value = cb.GetValue()
        self.stateMachineController.SetVariable(name, 1.0 if value else 0.0)

    def _OnControllerEnumVariable(self, cb, *args):
        name = cb.name
        value = cb.GetValue()
        self.stateMachineController.SetVariable(name, value)

    def _RefreshControllerVariables(self):
        if self.controllers:
            self.controllers.Close()
        self.controllers = ScrollContainer(parent=self.controllerParent, align=uiconst.TOTOP, height=68)
        PanelUnderlay(bgParent=self.controllers)
        for name, value in self.stateMachineController.GetVariables().items():
            line = Container(parent=self.controllers, align=uiconst.TOTOP, height=20, state=uiconst.UI_NORMAL)
            EveLabelSmall(parent=line, align=uiconst.CENTERLEFT, text=name, left=4)
            varType = self.stateMachineController.GetVariableType(name)
            if varType == 1:
                SingleLineEditInteger(align=uiconst.CENTERRIGHT, name=name, parent=line, width=150, height=18, setvalue=str(int(value)), OnFocusLost=self._OnControllerVariable, OnReturn=self._OnControllerVariable, sendSelfAsArgument=True)
            elif varType == 2:
                Checkbox(align=uiconst.CENTERRIGHT, name=name, parent=line, width=150, height=18, setvalue=str(value), floats=(None, None), callback=self._OnControllerBoolVariable)
            elif varType == 3:
                Combo(align=uiconst.CENTERRIGHT, name=name, parent=line, width=150, height=18, options=self.stateMachineController.GetEnumValues(name), callback=self._OnControllerEnumVariable, select=value)
            else:
                SingleLineEditFloat(align=uiconst.CENTERRIGHT, name=name, parent=line, width=150, height=18, setvalue=str(value), OnFocusLost=self._OnControllerVariable, OnReturn=self._OnControllerVariable, sendSelfAsArgument=True)
            Line(parent=line, align=uiconst.TOBOTTOM, opacity=0.05)

    def _UpdatePlayerShip(self):
        michelle = sm.GetService('michelle')
        ship = michelle.GetBall(session.shipid)
        if ship is None:
            return
        ship.UnfitHardpoints()
        ship.Release()
        while ship.model is not None:
            blue.synchro.Yield()

        ship.released = False
        ship.GetDNA = self.GetPreviewDna
        ship.LoadModel()
        ship.Assemble()
        if self.currentDirtLevel is not None:
            ship.model.dirtLevel = self.currentDirtLevel
        self.stateMachineController.ApplyTo(ship.model)
        ship.model.StartControllers()
