#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveclientqatools\sofpreviewer\sofselection\view.py
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eveclientqatools.sofpreviewer import viewhelper as ViewHelper
import carbonui.const as uiconst
from eve.client.script.ui.control.eveLabel import EveLabelSmall

class SofSelectionView(object):

    def __init__(self, controller):
        self.controller = controller
        self.raceCombo = None
        self.raceConstraint = None
        self.hullCombos = None
        self.hullConstraint = None
        self.multiHullContainer = None
        self.factionCombo = None
        self.factionConstraint = None
        self.patternCombo = None
        self.patternConstraint = None
        self.previewImage = None
        self.skinUnavailableLabel = None

    def Setup(self, parentContainer, viewModel):
        _leftContainer = Container(name='_leftContainer', parent=parentContainer)
        leftContainer = Container(name='leftContainer', parent=_leftContainer, align=uiconst.TORIGHT, height=320, width=250)
        self.raceCombo, self.raceConstraint = ViewHelper.CreateDropdownWithCheckbox('Race:', viewModel.sofRaces, ViewHelper.GetComboListIndex(viewModel.sofRaces, viewModel.currentRace), self.controller.OnRaceComboChange, 'Constrained', self.controller.OnConstraintChanged, leftContainer)
        self.hullCombos = []
        firstHullCombo, self.hullConstraint = ViewHelper.CreateDropdownWithCheckbox('Hull:', viewModel.sofHulls, ViewHelper.GetComboListIndex(viewModel.sofHulls, viewModel.currentHulls[0]), self.controller.OnHullComboChange, 'Constrained', self.controller.OnConstraintChanged, leftContainer)
        self.hullCombos.append(firstHullCombo)
        self.multiHullContainer = Container(name='multiHulls', parent=leftContainer, align=uiconst.TOTOP, height=35 * (viewModel.maxMultiHulls - 1))
        for i in xrange(1, viewModel.maxMultiHulls):
            self.hullCombos.append(ViewHelper.CreateDropdown('Hull %d:' % (i + 1), [], self.controller.OnSpecificationChanges, viewModel.currentHulls[i], self.multiHullContainer, align=uiconst.TOALL))

        self.multiHullContainer.display = False
        self.factionCombo, self.factionConstraint = ViewHelper.CreateDropdownWithCheckbox('Faction:', viewModel.sofFactions, ViewHelper.GetComboListIndex(viewModel.sofFactions, viewModel.currentFaction), self.controller.OnFactionComboChange, 'Constrained', self.controller.OnConstraintChanged, leftContainer)
        self.patternCombo, self.patternConstraint = ViewHelper.CreateDropdownWithCheckbox('Pattern:', viewModel.sofPatterns, ViewHelper.GetComboListIndex(viewModel.sofPatterns, viewModel.currentPattern), self.controller.OnPatternComboChange, 'Constrained', self.controller.OnConstraintChanged, leftContainer)
        previewContainer = Container(parent=leftContainer, align=uiconst.TOALL, padTop=16)
        self.previewImage = Sprite(parent=previewContainer, align=uiconst.CENTER, width=64, height=64)
        self.skinUnavailableLabel = EveLabelSmall(name='skinUnavailableLabel', align=uiconst.CENTERBOTTOM, parent=leftContainer, text='No skin license available', display=False)
