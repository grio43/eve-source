#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\orbitalConfiguration.py
import carbonui.control.checkbox
import localization
import utillib
from carbonui import ButtonVariant, uiconst
from carbonui.button.group import ButtonGroup
from carbonui.control.button import Button
from carbonui.control.combo import Combo
from carbonui.control.singlelineedits.singleLineEditFloat import SingleLineEditFloat
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.line import Line
from carbonui.util.effect import UIEffects
from eve.client.script.ui.shared.bookmarks.bookmarkContainerWindow import DropCombo
from eve.client.script.ui.shared.standings.levelSelector import StandingLevelSelector
from eve.client.script.ui.control import eveLabel
from eve.common.lib import appConst as const
from eve.common.script.net import eveMoniker
from eve.common.script.sys import idCheckers
from eve.common.script.sys.idCheckers import IsNPCCorporation, IsSkyhook
from mathext import clamp

class OrbitalConfigurationWindow(Window):
    __guid__ = 'form.OrbitalConfigurationWindow'
    default_windowID = 'configureOrbital'
    default_clipChildren = 1
    default_iconNum = 'res:/ui/Texture/WindowIcons/settings.png'
    WIDTH_COLLAPSED = 270
    WIDTH_EXPANDED = 445
    HEIGHT = 190
    HOVER_ALPHA = 1.0
    NORMAL_ALPHA = 0.8

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.aclCombo = None
        self._accessGroupOptions = None
        orbitalItem = attributes.get('orbitalItem')
        if not idCheckers.IsOrbital(orbitalItem.categoryID):
            raise RuntimeError('Cannot open an orbital configuration window for a non-orbital')
        self.locationID = orbitalItem.locationID
        self.orbitalID = orbitalItem.itemID
        self.typeID = orbitalItem.typeID
        self.isSkyhook = IsSkyhook(self.typeID)
        self.remoteOrbitalRegistry = eveMoniker.GetPlanetOrbitalRegistry(self.locationID)
        self.orbitalData = self.remoteOrbitalRegistry.GetSettingsInfo(self.orbitalID)
        self.selectedHour, self.taxRateValues, self.standingLevel, self.allowAlliance, self.allowStandings, self.selectedAcl = self.orbitalData
        self.taxRates = [utillib.KeyVal(key='corporation'),
         utillib.KeyVal(key='alliance'),
         utillib.KeyVal(key='standingHorrible', standing=const.contactHorribleStanding),
         utillib.KeyVal(key='standingBad', standing=const.contactBadStanding),
         utillib.KeyVal(key='standingNeutral', standing=const.contactNeutralStanding),
         utillib.KeyVal(key='standingGood', standing=const.contactGoodStanding),
         utillib.KeyVal(key='standingHigh', standing=const.contactHighStanding)]
        for taxRate in self.taxRates:
            taxRate.value = getattr(self.taxRateValues, taxRate.key)

        self.variance = sm.GetService('clientDogmaStaticSvc').GetTypeAttribute(self.typeID, const.attributeReinforcementVariance)
        self.reinforceHours = [ ('%.2d:00 - %.2d:00' % ((x - self.variance / 3600) % 24, (x + self.variance / 3600) % 24), x) for x in xrange(0, 24) ]
        caption = self._GetCaption()
        self.effects = UIEffects()
        self.scope = uiconst.SCOPE_INFLIGHT
        self.SetMinSize([self.WIDTH_COLLAPSED, self.HEIGHT])
        self.SetCaption(caption)
        self.MakeUnResizeable()
        self.ConstructLayout()
        self.Redraw()

    def _GetCaption(self):
        ballpark = sm.GetService('michelle').GetBallpark()
        planetName = None
        if ballpark is not None and self.orbitalID in ballpark.slimItems:
            planetName = cfg.evelocations.Get(ballpark.slimItems[self.orbitalID].planetID).name
        if planetName:
            if self.isSkyhook:
                caption = localization.GetByLabel('UI/OrbitalSkyhook/ConfigWnd/SkyhookNameWithPlanet', planetName=planetName)
            else:
                caption = localization.GetByLabel('UI/PI/Common/PlanetaryCustomsOfficeName', planetName=planetName)
        elif self.isSkyhook:
            caption = localization.GetByLabel('UI/OrbitalSkyhook/ConfigWnd/SkyhookConfig')
        else:
            caption = localization.GetByLabel('UI/DustLink/OrbitalConfiguration')
        return caption

    def ConstructLayout(self):
        self.main_container = ContainerAutoSize(parent=self.content, align=uiconst.TOPLEFT, callback=self._on_main_cont_size_changed, only_use_callback_when_size_changes=True)
        layout_container = LayoutGrid(parent=self.main_container, columns=2, align=uiconst.TOPLEFT, cellSpacing=(8, 8))
        if self.isSkyhook:
            self._skyhook_container(layout_container)
        self._left_container(layout_container)
        self._right_container(layout_container)
        self._footer_container(layout_container)

    def _on_main_cont_size_changed(self):
        width, height = self.GetWindowSizeForContentSize(height=self.main_container.height, width=self.main_container.width)
        self.SetMinSize(size=(width, height), refresh=True)

    def _skyhook_container(self, parent):
        header = carbonui.TextHeader(text=localization.GetByLabel('UI/OrbitalSkyhook/ConfigWnd/SkyhookSettings'), align=uiconst.TOPLEFT, top=8)
        parent.AddCell(cellObject=header, colSpan=2)
        self.AddReinforceDropDown(parent)
        label = eveLabel.EveLabelSmall(text=localization.GetByLabel('UI/OrbitalSkyhook/ConfigWnd/TakeAccess'), parent=parent, align=uiconst.CENTERLEFT)
        self.aclCombo = DropCombo(parent=parent, name='aclCombo', align=uiconst.TOPLEFT, options=self.accessGroupOptions, select=self.selectedAcl, dropped=self.OnDroppedGroup, emptyTooltip=localization.GetByLabel('UI/OrbitalSkyhook/ConfigWnd/TakeAccessComboHint'))
        comboWidth = clamp(max(self.aclCombo.width, self.reinforceHourCombo.width), 140, 200)
        self.aclCombo.width = self.reinforceHourCombo.width = comboWidth

    def _left_container(self, parent):
        if self.isSkyhook:
            parent.AddCell(cellObject=Line(top=8, padBottom=8), colSpan=2)
            header = carbonui.TextHeader(text=localization.GetByLabel('UI/OrbitalSkyhook/ConfigWnd/CustomsOfficeSettings'), align=uiconst.TOPLEFT)
            parent.AddCell(header, colSpan=3)
        self.left_container = LayoutGrid(name='left_container', parent=parent, align=uiconst.TOPLEFT, columns=3, cellSpacing=(8, 8), padRight=32)
        if not self.isSkyhook:
            self.AddReinforceDropDown(self.left_container)
        self.corporationLabel = eveLabel.EveLabelSmall(text=localization.GetByLabel('UI/PI/OrbitalConfigurationWindow/CorporationTax'), parent=self.left_container, state=uiconst.UI_NORMAL, align=uiconst.CENTERLEFT, hint=localization.GetByLabel('UI/PI/OrbitalConfigurationWindow/StandingTooltip', typeID=self.typeID))
        taxRateValue = self.taxRates[0].value
        taxRateInput = SingleLineEditFloat(parent=self.left_container, name='taxRateEdit', align=uiconst.TOPLEFT, setvalue='' if taxRateValue is None else str(100 * taxRateValue), idx=0, width=90, maxValue=100)
        eveLabel.EveLabelMedium(align=uiconst.CENTERLEFT, text='%', parent=self.left_container)
        self.taxRates[0].input = taxRateInput
        self.allianceCheckbox = carbonui.control.checkbox.Checkbox(parent=self.left_container, align=uiconst.CENTERLEFT, text=localization.GetByLabel('UI/PI/OrbitalConfigurationWindow/AllianceTax'), checked=self.allowAlliance, callback=self.Redraw)
        taxRateValue = self.taxRates[1].value
        taxRateInput = SingleLineEditFloat(parent=self.left_container, name='taxRateEdit', align=uiconst.TOPLEFT, setvalue='' if taxRateValue is None else str(100 * taxRateValue), idx=0, width=90, maxValue=100)
        eveLabel.EveLabelMedium(align=uiconst.CENTERLEFT, text='%', parent=self.left_container)
        self.taxRates[1].input = taxRateInput
        self.standingsCheckbox = carbonui.control.checkbox.Checkbox(text=localization.GetByLabel('UI/PI/OrbitalConfigurationWindow/Standing'), checked=self.allowStandings, callback=self.Redraw)
        self.left_container.AddCell(self.standingsCheckbox, colSpan=3)

    def AddReinforceDropDown(self, parent):
        self.reinforcementLabel = eveLabel.EveLabelSmall(text=localization.GetByLabel('UI/PI/OrbitalConfigurationWindow/ReinforcementExit'), align=uiconst.CENTERLEFT, parent=parent, state=uiconst.UI_NORMAL, hint=localization.GetByLabel('UI/PI/OrbitalConfigurationWindow/ReinforcementExitTooltip', typeID=self.typeID))
        self.reinforceHourCombo = Combo(name='orbitalReinforceHourCombo', align=uiconst.TOPLEFT, select=self.selectedHour, options=self.reinforceHours, nothingSelectedText=localization.GetByLabel('UI/OrbitalSkyhook/ConfigWnd/NothingSelected'))
        parent.AddCell(self.reinforceHourCombo, colSpan=2)

    def _right_container(self, parent):
        self.standingsContainer = ContainerAutoSize(name='standingsContainer', parent=parent, align=uiconst.TOPLEFT, left=24)
        self.standingLevelSelector = StandingLevelSelector(name='standingLevelSelector', parent=self.standingsContainer, align=uiconst.TOPLEFT, level=self.standingLevel, vertical=True, callback=self.Redraw, width=90, height=100 + 4 * (Combo.default_height - 12), top=(Combo.default_height - 20) / 2, iconPadding=Combo.default_height - 12)
        for i, taxRate in enumerate(self.taxRates[2:]):
            self.LayoutTaxInput(taxRate, self.standingsContainer, 28, i * (Combo.default_height + 8))

    def _footer_container(self, parent):
        parent.AddCell(ButtonGroup(align=uiconst.TOTOP, top=16, buttons=[Button(label=localization.GetByLabel('UI/Common/Submit'), func=self.Submit, variant=ButtonVariant.PRIMARY), Button(label=localization.GetByLabel('UI/Common/Cancel'), func=self.Cancel)]), colSpan=2)

    def LayoutTaxInput(self, taxRate, parent, left = 0, top = 0):
        taxRateValue = taxRate.value
        taxRateInput = SingleLineEditFloat(parent=parent, name='taxRateEdit', align=uiconst.TOPLEFT, setvalue='' if taxRateValue is None else str(100 * taxRateValue), width=90, left=left, top=top, idx=0, maxValue=100)
        eveLabel.EveLabelMedium(align=uiconst.TOPLEFT, text='%', parent=parent, left=left + 97, top=top + taxRateInput.default_height / 2 - 8)
        taxRate.input = taxRateInput

    def OnMouseEnterInteractable(self, obj, *args):
        obj.SetOpacity(self.HOVER_ALPHA)

    def OnMouseExitInteractable(self, obj, *args):
        obj.SetOpacity(self.NORMAL_ALPHA)

    def Redraw(self, *args):
        level = self.standingLevelSelector.GetValue()
        taxRateVisible = True
        for taxRate in self.taxRates[2:]:
            if taxRate.standing == level:
                taxRateVisible = False
            self.SetTaxRateVisible(taxRate.input, taxRateVisible)

        self.SetTaxRateVisible(self.taxRates[1].input, not self.allianceCheckbox.GetValue())
        if self.standingsCheckbox.GetValue():
            self.standingsContainer.EnableAutoSize()
        else:
            self.standingsContainer.DisableAutoSize()
            self.standingsContainer.width = 0

    def ResizeWindowWidth(self, width):
        self.effects.MorphUIMassSpringDamper(self, 'width', width, newthread=True, float=0, dampRatio=0.99, frequency=15.0)

    def HideElement(self, element):
        self.effects.MorphUIMassSpringDamper(element, 'opacity', 0, dampRatio=0.99, frequency=30.0)

    def ShowElement(self, element):
        self.effects.MorphUIMassSpringDamper(element, 'opacity', 1, dampRatio=0.99, frequency=30.0)

    def SetTaxRateVisible(self, field, visible):
        if visible and field.state == uiconst.UI_NORMAL:
            field.hiddenValue = field.GetValue()
            field.SetText(localization.GetByLabel('UI/PI/Common/CustomsOfficeAccessDenied'))
            field.SelectNone()
            field.state = uiconst.UI_DISABLED
            field.textLabel.SetAlpha(0.5)
            self.effects.MorphUIMassSpringDamper(field, 'opacity', 0.5, dampRatio=0.99)
        elif not visible and field.state == uiconst.UI_DISABLED:
            field.SetValue(field.hiddenValue)
            field.hiddenValue = None
            field.state = uiconst.UI_NORMAL
            field.textLabel.SetAlpha(1)
            self.effects.MorphUIMassSpringDamper(field, 'opacity', 1, dampRatio=0.99)

    def GetTaxRateValue(self, field):
        value = getattr(field, 'hiddenValue', None)
        if value is None:
            value = field.GetValue()
        return value / 100

    def OnDroppedGroup(self, newGroupID):
        for groupName, groupID in self.accessGroupOptions:
            if groupID == newGroupID:
                self.aclCombo.SetValue(newGroupID)
                return

        self.AddGroup(newGroupID)
        self.aclCombo.entries = self.accessGroupOptions
        self.aclCombo.SetValue(newGroupID)

    def AddGroup(self, newGroupID):
        if newGroupID:
            newGroup = sm.GetService('structureControllers').GetAccessGroupController().GetGroupInfoFromID(newGroupID, fetchToServer=True)
            groupDisplayName = cfg.eveowners.Get(newGroup.creatorID).name if IsNPCCorporation(newGroup.creatorID) else newGroup.name
            self.accessGroupOptions.append((groupDisplayName, newGroupID))

    @property
    def accessGroupOptions(self):
        if self._accessGroupOptions is None:
            self._accessGroupOptions = GetAccessGroupOptions()
        return self._accessGroupOptions

    def Submit(self, *args):
        reinforcementHour = self.reinforceHourCombo.GetValue()
        if reinforcementHour is None:
            raise UserError('CustomNotify', {'notify': localization.GetByLabel('UI/OrbitalSkyhook/ConfigWnd/NoReinforcementTimeSelected')})
        reinforceValue = int(reinforcementHour)
        standingValue = self.standingLevelSelector.GetValue()
        allowAllianceValue = self.allianceCheckbox.GetValue()
        allowStandingsValue = self.standingsCheckbox.GetValue()
        taxRateValues = utillib.KeyVal({taxRate.key:self.GetTaxRateValue(taxRate.input) for taxRate in self.taxRates})
        aclGroupID = None
        if self.aclCombo:
            aclValue = self.aclCombo.GetValue()
            aclGroupID = aclValue if aclValue > 0 else None
        remoteOrbitalRegistry = eveMoniker.GetPlanetOrbitalRegistry(self.locationID)
        remoteOrbitalRegistry.UpdateSettings(self.orbitalID, reinforceValue, taxRateValues, standingValue, allowAllianceValue, allowStandingsValue, aclGroupID)
        self.CloseByUser()

    def Cancel(self, *args):
        self.CloseByUser()


def GetAccessGroupOptions():
    accessGroupsController = sm.GetService('structureControllers').GetAccessGroupController()
    accessGroups = accessGroupsController.GetMyGroups()
    accessGroupOptions = []
    for accessGroupID, accessGroup in accessGroups.iteritems():
        groupDisplayName = cfg.eveowners.Get(accessGroup.creatorID).name if IsNPCCorporation(accessGroup.creatorID) else accessGroup.name
        accessGroupOptions.append((groupDisplayName, accessGroupID))

    accessGroupOptions.sort()
    accessGroupOptions.insert(0, (localization.GetByLabel('UI/AclBookmarks/NoAccessList'), None))
    return accessGroupOptions
