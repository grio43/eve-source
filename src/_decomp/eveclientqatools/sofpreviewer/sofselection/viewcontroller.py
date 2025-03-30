#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveclientqatools\sofpreviewer\sofselection\viewcontroller.py
from eveclientqatools.sofpreviewer.sofselection.view import SofSelectionView
from shipskins.static import SkinMaterialStorage
from sofDnaLibrary.query import GetDnaStringsMatchingQuery
from viewmodel import SofSelectionViewModel
from eveclientqatools.sofpreviewer import viewhelper as ViewHelper
import fsdBuiltData.common.graphicMaterialSets as graphicMaterialSets
from constraints import Constraints

class SofSelectionViewController(object):

    def __init__(self, model, parentController, parentView):
        self.parentController = parentController
        self.parentView = parentView
        self.model = model
        self.viewModel = SofSelectionViewModel(self.model)
        self.view = None
        self.constraints = None
        self.currentFaction = None

    def ShowUI(self, parentContainer):
        self.view = SofSelectionView(self)
        self.view.Setup(parentContainer, self.viewModel)
        self.constraints = Constraints(self.view)
        self.UpdateIcon()
        return self.view

    def ConstrainDnaSelection(self):
        raceQuery = '.*'
        factionQuery = '.*'
        hullQuery = '.*'
        if self.constraints.faction:
            factionQuery = self.view.factionCombo.GetKey()
        if self.constraints.hull:
            hullQuery = self.view.hullCombos[0].GetKey()
        if self.constraints.race:
            raceQuery = self.view.raceCombo.GetKey()
        if self.constraints.pattern and self.viewModel.currentPattern != 'None':
            self.viewModel.currentHulls[0] = ViewHelper.TrySettingComboOptions(self.view.hullCombos[0], self.model.patternToHulls[self.viewModel.currentPattern], self.viewModel.currentHulls[0])
        if self.constraints.HasNoConstraints():
            self.RestoreDefaultCurrentValues()
        else:
            self.ConstrainDnaWithConstrains(factionQuery, hullQuery, raceQuery)
        self.parentController.UpdatePreviewShip()

    def ConstrainDnaWithConstrains(self, factionQuery, hullQuery, raceQuery):
        dnaList = GetDnaStringsMatchingQuery(hullQuery, factionQuery, raceQuery)
        selectableRaces = []
        selectableFactions = []
        selectableHulls = []
        self.FilterSelectables(dnaList, selectableFactions, selectableHulls, selectableRaces)
        if not self.constraints.pattern:
            selectablePatterns = [ patternName for patternName, hulls in self.model.patternToHulls.iteritems() for hullName in selectableHulls if hullName in hulls ]
            selectablePatterns = list(set(selectablePatterns))
            selectablePatterns.insert(0, 'None')
            self.viewModel.currentPattern = ViewHelper.TrySettingComboOptions(self.view.patternCombo, selectablePatterns, self.viewModel.currentPattern)
        elif self.viewModel.currentPattern != 'None':
            selectableHullsBasedOfPattern = set(self.model.patternToHulls[self.viewModel.currentPattern])
            selectableHulls = list(set(selectableHulls).intersection(selectableHullsBasedOfPattern))
        if not self.constraints.hull:
            self.viewModel.currentHulls[0] = ViewHelper.TrySettingComboOptions(self.view.hullCombos[0], selectableHulls, self.viewModel.currentHulls[0])
            self.ShowMultiHullComboBoxes(self.viewModel.currentHulls[0])
        if not self.constraints.faction:
            self.currentFaction = ViewHelper.TrySettingComboOptions(self.view.factionCombo, selectableFactions, self.GetDefaultFactionForHull())
        if not self.constraints.race:
            self.viewModel.currentRace = ViewHelper.TrySettingComboOptions(self.view.raceCombo, selectableRaces, self.viewModel.currentRace)
        if not self.constraints.pattern and self.constraints.hull:
            availablePatterns = [ pattern for pattern, hulls in self.model.patternToHulls.iteritems() if self.viewModel.currentHulls[0] in hulls ]
            availablePatterns.insert(0, 'None')
            self.viewModel.currentPattern = ViewHelper.TrySettingComboOptions(self.view.patternCombo, availablePatterns, self.viewModel.currentPattern)

    def FilterSelectables(self, dnaList, selectableFactions, selectableHulls, selectableRaces):
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

    def RestoreDefaultCurrentValues(self):
        self.currentFaction = ViewHelper.TrySettingComboOptions(self.view.factionCombo, self.model.sofFactions, self.GetDefaultFactionForHull())
        self.viewModel.currentRace = ViewHelper.TrySettingComboOptions(self.view.raceCombo, self.model.sofRaces, self.viewModel.currentRace)
        self.viewModel.currentHulls[0] = ViewHelper.TrySettingComboOptions(self.view.hullCombos[0], self.model.sofHulls, self.viewModel.currentHulls[0])
        self.viewModel.currentPattern = ViewHelper.TrySettingComboOptions(self.view.patternCombo, self.model.sofPatterns, self.viewModel.currentPattern)

    def ShowMultiHullComboBoxes(self, hull):
        isMultiHull = self.model.IsMultiHull(hull)
        self.view.multiHullContainer.display = isMultiHull
        if isMultiHull:
            baseHullName = self.model.GetMultiHullBaseName(hull)
            for i in xrange(1, self.model.const.MAX_MULTI_HULLS):
                availableHulls = [ hull for hull, specification, variation in sorted(self.model.multihulls[baseHullName], key=lambda x: x[2]) if specification == i + 1 ]
                ViewHelper.TrySettingComboOptions(self.view.hullCombos[i], availableHulls, self.viewModel.currentPattern)
                self.viewModel.currentHulls[i] = availableHulls[0]

        else:
            for i in xrange(1, self.model.const.MAX_MULTI_HULLS):
                self.viewModel.currentHulls[i] = None

    def GetCurrentHull(self):
        currentHull = self.viewModel.currentHulls[0]
        if self.model.IsMultiHull(currentHull):
            currentHull += ';' + ';'.join((hull for hull in self.viewModel.currentHulls[1:] if hull is not None))
        return currentHull

    def GetDefaultFactionForHull(self):
        if self.viewModel.currentHulls[0].endswith('t2'):
            return self.model._GetDefaultFactionForT2Hull(self.viewModel.currentHulls[0])
        else:
            return self.model._GetDefaultFactionForT1Hull(self.viewModel.currentHulls[0])

    def UpdateIcon(self):
        path = None
        id = self.parentController.GetCurrentMaterialSetID()
        for mid, m in SkinMaterialStorage().iteritems():
            if m.materialSetID == id:
                path = 'res:/UI/Texture/classes/skins/icons/%s.png' % mid
                break

        self.view.skinUnavailableLabel.display = path is None
        if path is None:
            path = 'res:/UI/Texture/notavailable.dds'
        self.view.previewImage.texture.resPath = path

    def FilterMaterialSet(self, filterByRace, materialSets, availableMaterialSets):
        for materialSetID, materialSet in materialSets.iteritems():
            if filterByRace:
                raceHint = graphicMaterialSets.GetSofRaceHint(materialSet)
                if raceHint and raceHint == self.view.raceCombo.GetKey():
                    availableMaterialSets.append((materialSetID, materialSet.description))
            else:
                availableMaterialSets.append((materialSetID, materialSet.description))

    @property
    def currentPattern(self):
        return self.viewModel.currentPattern

    def OnPatternComboChange(self, comboBox, pattern, value):
        self.viewModel.currentPattern = pattern
        if self.constraints.pattern:
            self.ConstrainDnaSelection()
        self.parentController.UpdatePreviewShip()

    def OnMaterialSetIDChange(self, materialSet):
        faction = graphicMaterialSets.GetSofFactionName(materialSet)
        if not faction:
            dna = self.model.GetDnaFromPlayerShip()
            if dna.split(':')[0] == self.GetCurrentHull():
                faction = dna.split(':')[1]
        if faction:
            try:
                self.view.factionCombo.SelectItemByLabel(faction)
            except RuntimeError:
                if materialSet is not None:
                    print "Removing constraints because '%s' is not in the constrained faction list" % materialSet.sofFactionName
                self.constraints.SetAll(False)
                self.ConstrainDnaSelection()

            self.view.factionCombo.SelectItemByLabel(faction)
            self.OnFactionComboChange(self.view.factionCombo, faction, None)
        sofPatternName = graphicMaterialSets.GetSofPatternName(materialSet, 'None')
        idx = ViewHelper.GetComboListIndex(self.model.sofPatterns, sofPatternName)
        self.view.patternCombo.SelectItemByValue(idx)
        self.OnPatternComboChange(self.view.patternCombo, sofPatternName, idx)

    def OnRaceComboChange(self, comboBox, race, value):
        self.viewModel.currentRace = race
        if self.constraints.race:
            self.ConstrainDnaSelection()
        if self.parentController.isMaterialSetFilteredByRace:
            self.parentController.FilterMaterialSet(self.viewModel.currentRace)
        self.parentController.UpdatePreviewShip()

    def OnConstraintChanged(self, checkbox):
        self.ConstrainDnaSelection()

    def OnFactionComboChange(self, comboBox, faction, value):
        self.viewModel.currentFaction = faction
        if self.constraints.faction:
            self.ConstrainDnaSelection()
        self.parentController.UpdatePreviewShip()

    def OnHullComboChange(self, comboBox, hull, value):
        self.viewModel.currentHulls[0] = hull
        self.ShowMultiHullComboBoxes(hull)
        if self.constraints.hull:
            self.ConstrainDnaSelection()
        self.parentController.UpdatePreviewShip()

    def OnSpecificationChanges(self, comboBox, hull, value):
        specification = self.model.GetMultiHullSpecification(hull)
        self.viewModel.currentHulls[specification - 1] = hull
        self.parentController.UpdatePreviewShip()
