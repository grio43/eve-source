#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fleet\fleetFormations.py
import localization
from carbonui import uiconst
from carbonui.control.combo import Combo
from carbonui.control.comboEntries import ComboEntry
from carbonui.window.widget import WidgetWindow
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.line import Line
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.window import Window
from eve.client.script.ui.control.toggleButtonGroup import ToggleButtonGroup
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelMediumBold
from eve.client.script.ui.control.toggleButtonGroupButton import ToggleButtonGroupButtonIcon
from eve.client.script.ui.shared.tooltip.skill import LoadSkillEntryTooltip
from evefleet import FLEET_FORMATIONS, FLEET_FORMATION_SETTING, FLEET_FORMATION_SIZE, FLEET_FORMATION_SIZE_SETTING, FLEET_FORMATION_SPACING, FLEET_FORMATION_SPACING_SETTING, FORMATION_DISTANCE_SKILL, FORMATION_ICONS, FORMATION_SKILL, FORMATION_USES_SIZE, FORMATION_USES_SPACING, LOCALIZED_FORMATIONS, LOCALIZED_FORMATION_DESCRIPTIONS
from evefleet.client.util import GetFormationSizeSelected, GetFormationSpacingSelected, GetFormationSelected
ORANGE = (1.0, 0.5, 0.0, 1)
SKILL_BOOK_ORANGE = (0.6, 0.3, 0.0, 1.0)
LIGHT_GREY = (1.0, 1.0, 1.0, 0.3)
COMBO_TOP = 20

class FleetFormationsPanel(Container):
    __notifyevents__ = ['OnSkillsChanged']
    default_clipChildren = True
    hasDetachBtn = True

    def ApplyAttributes(self, attributes):
        self.inited = False
        super(FleetFormationsPanel, self).ApplyAttributes(attributes)

    def LoadPanel(self):
        if not self.inited:
            self.ContructContainer()

    def ContructContainer(self):
        self.skillsSvc = sm.GetService('skills')
        sm.RegisterNotify(self)
        if self.hasDetachBtn:
            self.ConstructDetachIcon()
        self.ConstructFormationSettings()
        self.inited = True

    def ConstructDetachIcon(self):
        iconCont = Container(name='iconCont', parent=self, height=20, align=uiconst.TOTOP, opacity=0.6)
        ButtonIcon(name='openInWindow', parent=iconCont, iconSize=16, pos=(0, 0, 16, 16), texturePath='res:/UI/Texture/classes/DockPanel/floatButton.png', align=uiconst.CENTERRIGHT, func=self.DetachPanel, hint=localization.GetByLabel('UI/Inflight/Scanner/OpenInWindow'))

    def ConstructFormationSettings(self):
        selectedFormation = self.ConstructFormationButtonGroup()
        self.ConstructFormationSize(selectedFormation)
        self.ConstructFormationSpacing(selectedFormation)

    def ConstructFormationButtonGroup(self):
        skillLevel = self.GetSkillLevel(FORMATION_SKILL)
        selectedFormationValue = GetFormationSelected(skillLevel)
        self.formationSelection = FormationSelectionButtons(parent=self, align=uiconst.TOTOP, callback=self.OnFormationSelected, selected=selectedFormationValue, skillLevel=skillLevel, autoHeight=True)
        return selectedFormationValue

    def ConstructFormationSize(self, selectedFormation, parent = None):
        skillLevel = self.GetSkillLevel(FORMATION_DISTANCE_SKILL)
        comboOptions = [ self.GetDistanceOption(i, index, skillLevel) for index, i in enumerate(FLEET_FORMATION_SIZE) ]
        parent = parent or self
        self.formationSizeSelection = FleetFormationCombo(align=uiconst.TOTOP, top=COMBO_TOP, parent=parent, state=uiconst.UI_NORMAL, label=localization.GetByLabel('UI/Fleet/FleetFormations/SetFleetFormationSize'), options=comboOptions, callback=self.OnFormationSizeSelected, select=GetFormationSizeSelected(skillLevel), padTop=4)
        self.formationSizeSelection.display = self.ShowHideSizeSelection(selectedFormation)

    def ConstructFormationSpacing(self, selectedFormation, parent = None):
        skillLevel = self.GetSkillLevel(FORMATION_DISTANCE_SKILL)
        comboOptions = [ self.GetDistanceOption(i, index, skillLevel) for index, i in enumerate(FLEET_FORMATION_SPACING) ]
        parent = parent or self
        self.formationSpacingSelection = FleetFormationCombo(align=uiconst.TOTOP, top=COMBO_TOP, parent=parent, state=uiconst.UI_NORMAL, label=localization.GetByLabel('UI/Fleet/FleetFormations/SetFleetFormationSpacing'), options=comboOptions, callback=self.OnFormationSpacingSelected, select=GetFormationSpacingSelected(skillLevel), padTop=4)
        self.formationSpacingSelection.display = self.ShowHideSpacingSelection(selectedFormation)

    def OnFormationSelected(self, formationID, *args):
        settings.char.ui.Set(FLEET_FORMATION_SETTING, formationID)
        self.formationSizeSelection.display = self.ShowHideSizeSelection(formationID)
        self.formationSpacingSelection.display = self.ShowHideSpacingSelection(formationID)

    def OnFormationSizeSelected(self, comboBox, size, sizeValue):
        settings.char.ui.Set(FLEET_FORMATION_SIZE_SETTING, sizeValue)

    def OnFormationSpacingSelected(self, comboBox, spacing, spacingValue):
        settings.char.ui.Set(FLEET_FORMATION_SPACING_SETTING, spacingValue)

    def ShowHideSizeSelection(self, formation):
        if formation not in FORMATION_USES_SIZE:
            return False
        else:
            return True

    def ShowHideSpacingSelection(self, formation):
        if formation not in FORMATION_USES_SPACING:
            return False
        else:
            return True

    def GetDistanceOption(self, distance, index, skillLevel):
        if index > skillLevel:
            resPath = 'res:/ui/Texture/classes/Fitting/warningSkills.png'
        else:
            resPath = None
        option = (self.FormatDistanceInKilometers(float(distance)),
         distance,
         None,
         resPath)
        return option

    def GetSkillLevel(self, skillTypeID):
        return self.skillsSvc.GetEffectiveLevel(skillTypeID) or 0

    def OnSkillsChanged(self, skillInfoChange):
        self.Flush()
        if FORMATION_SKILL in skillInfoChange or FORMATION_DISTANCE_SKILL in skillInfoChange:
            self.ConstructFormationSettings()

    def _OnClose(self, *args):
        sm.UnregisterNotify(self)
        Container._OnClose(self)

    def FormatDistanceInKilometers(self, dist):
        dist = long(round(dist / 1000.0))
        distStr = localization.formatters.FormatNumeric(dist, useGrouping=True, decimalPlaces=None)
        return localization.GetByLabel('/Carbon/UI/Common/FormatDistance/fmtDistInKiloMeters', distance=distStr)

    def DetachPanel(self, *args):
        settings.char.ui.Set('fleetFormationStandalone', True)
        FleetFormationWnd.Open()
        sm.ScatterEvent('OnFleetFormationWndChanged')


class FleetFormationContForWnd(FleetFormationsPanel):
    hasDetachBtn = False

    def ApplyAttributes(self, attributes):
        super(FleetFormationContForWnd, self).ApplyAttributes(attributes)
        self.ContructContainer()

    def ConstructFormationSettings(self):
        self.ConstructFormationButtonGroup()
        skillLevel = self.GetSkillLevel(FORMATION_SKILL)
        selectedFormation = GetFormationSelected(skillLevel)
        spacingParent = ContainerAutoSize(name='spacingParent', parent=self, align=uiconst.TOTOP)
        self.ConstructFormationSpacing(selectedFormation, parent=spacingParent)
        sizeParent = ContainerAutoSize(name='sizeParent', parent=self, align=uiconst.TOTOP)
        self.ConstructFormationSize(selectedFormation, parent=sizeParent)


class FleetFormationComboEntry(ComboEntry):

    def LoadTooltipPanel(self, tooltipPanel, *args):
        if self.sr.icon:
            LoadSkillEntryTooltip(tooltipPanel, FORMATION_DISTANCE_SKILL, self.sr.node.idx)

    def Load(self, node):
        super(FleetFormationComboEntry, self).Load(node)
        if self.sr.icon:
            self.sr.icon.top = -1
            self.sr.icon.color = SKILL_BOOK_ORANGE
            self.sr.label.color = LIGHT_GREY
            self.OnClick = None


class FleetFormationCombo(Combo):

    def GetEntryClass(self):
        return FleetFormationComboEntry


class FormationToggleButtonGroupButton(ToggleButtonGroupButtonIcon):

    def ApplyAttributes(self, attributes):
        super(FormationToggleButtonGroupButton, self).ApplyAttributes(attributes)
        self.formationID = attributes.formationID

    def LoadTooltipPanel(self, tooltipPanel, *args):
        if self.isDisabled:
            LoadSkillEntryTooltip(tooltipPanel, FORMATION_SKILL, skillLevel=self.formationID)
            self.constructLine(tooltipPanel)
        self.constructDescription(tooltipPanel)

    def constructLine(self, tooltipPanel):
        grid = LayoutGrid(columns=1)
        grid.AddCell(cellPadding=(256, 8, 0, 0), colSpan=1)
        grid.AddCell(Line(align=uiconst.TOTOP, height=1, opacity=0.5), cellPadding=(0, 0, 0, 0))
        tooltipPanel.AddCell(grid, cellPadding=(12, 0, 8, 8), colSpan=tooltipPanel.columns).SetOrder(idx=0)

    def constructDescription(self, panel):
        grid = LayoutGrid(columns=1)
        grid.AddCell(cellPadding=(256, 8, 0, 0), colSpan=1)
        grid.AddCell(EveLabelMediumBold(align=uiconst.TOPLEFT, text=localization.GetByLabel(LOCALIZED_FORMATIONS[self.formationID]), width=244), cellPadding=(0, 0, 0, 0))
        grid.AddCell(EveLabelMedium(align=uiconst.TOPLEFT, text=localization.GetByLabel(LOCALIZED_FORMATION_DESCRIPTIONS[self.formationID]), width=244), cellPadding=(0, 0, 0, 0))
        panel.AddCell(grid, cellPadding=(12, 0, 8, 8), colSpan=panel.columns).SetOrder(idx=0)


class FormationSelectionButtons(ToggleButtonGroup):
    default_btnClass = FormationToggleButtonGroupButton

    def ApplyAttributes(self, attributes):
        super(FormationSelectionButtons, self).ApplyAttributes(attributes)
        self.skillLevel = attributes.skillLevel
        self.ReconstructButtons()
        self.UpdateSelectedBtn(attributes.selected)

    def ReconstructButtons(self):
        self.ClearButtons()
        for formationID in FLEET_FORMATIONS:
            isDisabled = self.skillLevel < formationID
            if isDisabled:
                color = ORANGE
            else:
                color = None
            self.AddButton(formationID, iconPath=FORMATION_ICONS[formationID], iconSize=26, isDisabled=isDisabled, colorSelected=color, formationID=formationID)

    def UpdateSelectedBtn(self, formationID):
        self.SetSelectedByID(formationID)

    def OnFormationSelected(self, formationID, *args):
        self.UpdateSelectedBtn(formationID)
        self.callback(formationID)


class FleetFormationWnd(WidgetWindow):
    default_height = 250
    default_width = 350
    default_minSize = (Window.default_width, 156)
    default_windowID = 'FleetFormationWnd'
    default_captionLabelPath = 'UI/Fleet/FleetFormations/FleetFormationMenu'
    __notifyevents__ = ['OnSessionChanged']

    def ApplyAttributes(self, attributes):
        super(FleetFormationWnd, self).ApplyAttributes(attributes)
        FleetFormationContForWnd(parent=self.sr.main)

    def OnSessionChanged(self, isRemote, sess, change):
        if 'fleetid' in change and not session.fleetid:
            self.Close()

    def CloseByUser(self, *args):
        settings.char.ui.Set('fleetFormationStandalone', False)
        super(FleetFormationWnd, self).CloseByUser(*args)

    def Close(self, setClosed = False, *args, **kwds):
        super(FleetFormationWnd, self).Close(setClosed, *args, **kwds)
        sm.ScatterEvent('OnFleetFormationWndChanged')
