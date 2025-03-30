#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\scannerFiles\scannerToolsUIComponents.py
import weakref
import localization
import probescanning
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui import fontconst, uiconst
from carbonui.button.const import HEIGHT_COMPACT
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.combo import ComboUnderlay
from carbonui.primitives.container import Container
from carbonui.primitives.layoutGrid import LayoutGridRow
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from carbonui.control.button import Button
from carbonui.control.checkbox import Checkbox
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from eve.client.script.ui.control.themeColored import FillThemeColored, LabelThemeColored, FrameThemeColored, SpriteThemeColored
from eve.client.script.ui.control.tooltips import ShortcutHint
from eve.client.script.ui.tooltips.tooltipHandler import TOOLTIP_DELAY_GAMEPLAY
from eve.client.script.ui.util.utilWindows import NamePopup

class ProbeTooltipButtonBase(LayoutGridRow):
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        LayoutGridRow.ApplyAttributes(self, attributes)
        self.func = attributes.func
        self.funcArgs = attributes.funcArgs
        self.highlight = FillThemeColored(bgParent=self, padding=(1, 0, 1, 0), opacity=0.25, colorType=uiconst.COLORTYPE_UIHILIGHT)
        self.highlight.display = False

    def OnClick(self, *args):
        if self.func:
            if self.funcArgs:
                self.func(*self.funcArgs)
            else:
                self.func()

    def OnMouseEnter(self, *args):
        self.highlight.display = True

    def OnMouseExit(self, *args):
        self.highlight.display = False

    def Disable(self):
        self.state = uiconst.UI_DISABLED
        self.opacity = 0.3

    def Enable(self):
        self.state = uiconst.UI_NORMAL
        self.opacity = 1.0


class FilterBox(Container):
    default_align = uiconst.TOPLEFT

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        labelCont = Container(parent=self, padRight=16, clipChildren=True)
        self.label = eveLabel.EveLabelSmall(parent=labelCont, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT, left=5)
        Sprite(parent=self, texturePath='res:/UI/Texture/classes/Neocom/arrowDown.png', pos=(5, -1, 7, 7), align=uiconst.CENTERRIGHT, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW, opacity=0.5, state=uiconst.UI_DISABLED)
        ComboUnderlay(parent=self, align=uiconst.TOALL)
        self.SetText(attributes.text)

    def SetText(self, text):
        self.label.text = text
        self.width = self.label.textwidth + self.label.left * 2 + 12
        if self.maxWidth:
            self.width = min(self.width, self.maxWidth)
        self.height = max(HEIGHT_COMPACT, self.label.textheight + 2)

    def OnMouseEnter(self, *args):
        uicore.animations.FadeTo(self, startVal=self.opacity, endVal=1.5, duration=0.1)

    def OnMouseExit(self, *args):
        uicore.animations.FadeTo(self, startVal=self.opacity, endVal=1.0, duration=0.3)

    def GetTooltipPointer(self):
        return uiconst.POINT_TOP_2

    def GetTooltipDelay(self):
        return TOOLTIP_DELAY_GAMEPLAY


class IgnoredBox(Container):
    default_align = uiconst.TOPLEFT
    noIgnored = 0

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.scanSvc = sm.GetService('scanSvc')
        self.label = eveLabel.EveLabelSmall(parent=self, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT, left=5)
        self.clearIcon = Sprite(parent=self, texturePath='res:/UI/Texture/classes/Neocom/arrowDown.png', pos=(5, -1, 7, 7), align=uiconst.CENTERRIGHT, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW, opacity=0.5, state=uiconst.UI_DISABLED)
        ComboUnderlay(parent=self, align=uiconst.TOALL)
        self.SetText(attributes.text)

    def OnClick(self):
        pass

    def UpdateIgnoredAmount(self, noIgnored):
        self.noIgnored = noIgnored
        if noIgnored:
            self.hint = localization.GetByLabel('UI/Inflight/Scanner/ResetIgnoredResults')
            self.Show()
        else:
            self.Hide()
        self.SetText(localization.GetByLabel('UI/Inflight/Scanner/Ignored', noIgnored=noIgnored))

    def SetText(self, text):
        self.label.text = text
        self.width = self.label.textwidth + self.label.left * 2 + 12
        self.height = self.label.textheight + 2

    def OnMouseEnter(self, *args):
        if self.noIgnored:
            uicore.animations.FadeTo(self, startVal=self.opacity, endVal=1.5, duration=0.1)

    def OnMouseExit(self, *args):
        uicore.animations.FadeTo(self, startVal=self.opacity, endVal=1.0, duration=0.3)

    def GetTooltipPointer(self):
        return uiconst.POINT_TOP_2


class ProbeTooltipButtonRow(ProbeTooltipButtonBase):

    def ApplyAttributes(self, attributes):
        ProbeTooltipButtonBase.ApplyAttributes(self, attributes)
        width = attributes.width or 128
        icon = Sprite(texturePath=attributes.texturePath, pos=(0, 0, 17, 17), align=uiconst.CENTER, state=uiconst.UI_DISABLED)
        self.AddCell(icon, cellPadding=(5, 3, 4, 3))
        self.label = eveLabel.EveLabelMedium(text=attributes.text, bold=True, align=uiconst.CENTERLEFT, autoFitToText=True, width=width)
        self.AddCell(self.label, colSpan=self.columns - 1, cellPadding=(0, 2, 10, 2))


class ProbeTooltipCheckboxRow(ProbeTooltipButtonBase):
    deleteFunction = None
    editFunction = None

    def ApplyAttributes(self, attributes):
        ProbeTooltipButtonBase.ApplyAttributes(self, attributes)
        self.checkBox = Checkbox(groupname=attributes.groupName, align=uiconst.CENTER, checked=attributes.checked, wrapLabel=True, settingsPath=None, width=16, height=16, state=uiconst.UI_DISABLED)
        self.settingsKey = attributes.settingsKey
        self.AddCell(self.checkBox, cellPadding=(5, 1, 4, 1))
        self.deleteFunction = attributes.deleteFunc
        self.editFunction = attributes.editFunc
        self.label = EveLabelSmall(text=attributes.text, bold=True, align=uiconst.CENTERLEFT, autoFitToText=True, width=128)
        self.AddCell(self.label, colSpan=1 if attributes.filterIndex is not None else 2, cellPadding=(0, 2, 6, 2))
        if attributes.filterIndex is not None:
            shortcutObj = ShortcutHint(text=str(attributes.filterIndex))
            self.AddCell(shortcutObj, cellPadding=(2, 2, 2, 0))
            return shortcutObj

    def OnDelete(self, *args):
        if self.deleteFunction:
            self.state = uiconst.UI_DISABLED
            if callable(self.deleteFunction):
                self.deleteFunction()
            elif isinstance(self.deleteFunction, tuple):
                func, args = self.deleteFunction
                func(*args)
            uicore.animations.FadeOut(self, duration=0.5, callback=self.Close)

    def OnEdit(self, *args):
        if callable(self.editFunction):
            self.editFunction()
        elif isinstance(self.editFunction, tuple):
            func, args = self.editFunction
            func(*args)

    def OnClick(self, *args):
        self.checkBox.ToggleState()
        if self.func:
            self.func(self.settingsKey, self.checkBox.GetValue())

    def GetMenu(self):
        m = []
        if self.editFunction:
            m.append((localization.GetByLabel('UI/Inventory/Filters/Edit'), self.OnEdit))
        if self.deleteFunction:
            m.append((localization.GetByLabel('UI/Common/Delete'), self.OnDelete))
        return m


class ProbeTooltipButton_CustomFormation(ProbeTooltipButtonBase):

    def ApplyAttributes(self, attributes):
        ProbeTooltipButtonBase.ApplyAttributes(self, attributes)
        self.formation = attributes.formation
        self.OnChangeCallback = attributes.OnChangeCallback
        self.launchFunc = attributes.launchFunc
        self.AddCell()
        self.label = EveLabelSmall(parent=self, text=attributes.text, bold=True, align=uiconst.CENTERLEFT)
        deleteButton = Sprite(texturePath='res:/UI/Texture/Icons/38_16_111.png', pos=(0, 0, 16, 16), align=uiconst.CENTERRIGHT, hint=localization.GetByLabel('UI/Inflight/Scanner/DeleteFormation'))
        self.AddCell(deleteButton, cellPadding=(5, 3, 4, 3))
        deleteButton.OnClick = self.DeleteFormation

    def Close(self, *args):
        ProbeTooltipButtonBase.Close(self, *args)
        self.OnChangeCallback = None

    def OnClick(self, *args):
        probescanning.customFormations.SelectFormation(self.formation[0])
        self.launchFunc(self.formation[0])
        if self.OnChangeCallback:
            self.OnChangeCallback()

    def DeleteFormation(self, *args):
        response = uicore.Message('DeleteFormation', {'formationName': '%s' % self.formation[1]}, uiconst.YESNO, suppress=uiconst.ID_YES)
        if response != uiconst.ID_YES:
            return
        formation = self.formation
        probescanning.customFormations.DeleteFormation(formation[0])
        self.state = uiconst.UI_DISABLED
        uicore.animations.FadeOut(self, duration=0.5, callback=self.Close)
        if self.OnChangeCallback:
            self.OnChangeCallback()


class FormationButton(ButtonIcon):
    default_texturePath = 'res:/UI/Texture/classes/ProbeScanner/32/customFormation.png'
    default_soundClick = 'msg_newscan_probe_formation_play'

    def __init__(self, launchFunc, **kwargs):
        self.scanSvc = sm.GetService('scanSvc')
        self.launchFunc = launchFunc
        super(FormationButton, self).__init__(func=self._LaunchFormation, args=(), **kwargs)
        self.UpdateButton()

    @property
    def selectedFormationID(self):
        return probescanning.customFormations.GetSelectedFormationID()

    @property
    def selectedFormationName(self):
        return probescanning.customFormations.GetSelectedFormationName() or localization.GetByLabel('UI/Inflight/Scanner/ProbeFormation')

    def UpdateButton(self):
        selectedFormationID = probescanning.customFormations.GetSelectedFormationID()
        if selectedFormationID is not None:
            if self.scanSvc.CanLaunchFormation(selectedFormationID):
                self.Enable()
            else:
                self.Disable()
        elif self.scanSvc.HasAvailableProbes():
            self.Enable()
        else:
            self.Disable()
        self.hint = self.selectedFormationName

    def _LaunchFormation(self):
        selectedFormationID = probescanning.customFormations.GetSelectedFormationID()
        if selectedFormationID is not None:
            self.launchFunc(selectedFormationID)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.Flush()
        tooltipPanel.LoadStandardSpacing()
        tooltipPanel.columns = 3
        tooltipPanel.state = uiconst.UI_NORMAL
        formationsInfo = probescanning.customFormations.GetCustomFormationsInfo()
        buttonRow = tooltipPanel.AddRow()
        saveBtn = Button(align=uiconst.CENTER, label=localization.GetByLabel('UI/Inflight/Scanner/SaveCurrentFormation'), func=self.OnClickSaveFormation)
        buttonRow.AddCell(cellObject=saveBtn, colSpan=tooltipPanel.columns)
        if not self.scanSvc.GetActiveProbes() or len(formationsInfo) >= 10:
            saveBtn.Disable()
        selectedFormationID = probescanning.customFormations.GetSelectedFormationID()
        self.formationButtonsByID = {}
        for formationInfo in formationsInfo:
            formationID = formationInfo[0]
            isActiveFormation = formationID == selectedFormationID
            formationName = '%s (%i)' % (formationInfo[1], formationInfo[2])
            button = tooltipPanel.AddRow(rowClass=ProbeTooltipButton_CustomFormation, text=formationName, formation=formationInfo, OnChangeCallback=self.OnCustomFormationsChanged, launchFunc=self.launchFunc)
            if isActiveFormation:
                FillThemeColored(bgParent=button, padding=(3, 2, 3, 2), opacity=0.5, colorType=uiconst.COLORTYPE_UIHILIGHT)
            self.formationButtonsByID[formationInfo[0]] = button

        self.customFormationTooltip = weakref.ref(tooltipPanel)
        self.UpdateTooltipPanel(tooltipPanel)
        self.tooltipUpdateTimer = AutoTimer(100, self.UpdateTooltipPanel, tooltipPanel)

    def OnClickSaveFormation(self, *args):
        formationName = NamePopup(caption=localization.GetByLabel('UI/Inflight/Scanner/SaveCurrentFormation'), label=localization.GetByLabel('UI/Inflight/Scanner/FormationName'), maxLength=16)
        if formationName:
            sm.GetService('scanSvc').PersistCurrentFormation(formationName)

    def ReloadCustomFormationTooltip(self):
        if not self.customFormationTooltip or self.destroyed:
            return
        customFormationTooltip = self.customFormationTooltip()
        if customFormationTooltip is not None:
            self.LoadTooltipPanel(customFormationTooltip)

    def OnCustomFormationsChanged(self, *args):
        self.ReloadCustomFormationTooltip()
        self.UpdateButton()

    def UpdateTooltipPanel(self, tooltipPanel):
        if tooltipPanel.destroyed:
            self.tooltipUpdateTimer = None
            return
        for formationID, button in self.formationButtonsByID.iteritems():
            if button.destroyed:
                continue
            try:
                canLaunch = self.scanSvc.CanLaunchFormation(formationID)
            except KeyError:
                continue

            if canLaunch:
                button.Enable()
            else:
                button.Disable()
