#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\facilityTaxWindow.py
import localization
from carbonui import ButtonVariant, uiconst
from carbonui.control.button import Button
from carbonui.control.singlelineedits.singleLineEditFloat import SingleLineEditFloat
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.button.group import ButtonGroup
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelSmall
from carbonui.control.window import Window
from utillib import KeyVal

class FacilityTaxWindow(Window):
    __guid__ = 'form.FacilityTaxWindow'
    default_windowID = 'FacilityTaxWindow'
    default_clipChildren = 1
    HOVER_ALPHA = 1.0
    NORMAL_ALPHA = 0.8
    default_iconNum = 'res:/ui/Texture/WindowIcons/settings.png'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.facilityName = attributes.facilityName
        self.facilityID = attributes.facilityID
        self.facilitySvc = sm.GetService('facilitySvc')
        self.taxRate = KeyVal(value=self.facilitySvc.GetFacilityTaxes(self.facilityID).taxCorporation)
        self.scope = uiconst.SCOPE_INGAME
        self.width = 270
        self.height = 130
        self.SetCaption(localization.GetByLabel('UI/Menusvc/ConfigureFacility'))
        self.MakeUnResizeable()
        self.Layout()

    def Layout(self):
        self.corporationContainer = Container(align=uiconst.TOPLEFT, parent=self.sr.main, width=self.width, height=25, top=20)
        self.nameLabel = EveLabelSmall(text=self.facilityName, parent=self.corporationContainer, state=uiconst.UI_NORMAL, left=15, top=-15)
        self.corporationLabel = EveLabelSmall(text=localization.GetByLabel('UI/Industry/FacilityTax'), parent=self.corporationContainer, state=uiconst.UI_NORMAL, left=15, top=8)
        self.LayoutTaxInput(self.taxRate, self.corporationContainer, 15, 30)
        self.footer = ContainerAutoSize(name='footer', parent=self.content, align=uiconst.TOBOTTOM)
        ButtonGroup(parent=self.footer, align=uiconst.TOBOTTOM, buttons=[Button(label=localization.GetByLabel('UI/Common/Submit'), func=self.Submit, variant=ButtonVariant.PRIMARY), Button(label=localization.GetByLabel('UI/Common/Cancel'), func=self.Cancel)], line=True)

    def LayoutTaxInput(self, taxRate, parent, left = 0, top = 0):
        taxRateValue = taxRate.value
        taxRateInput = SingleLineEditFloat(parent=parent, name='taxRateEdit', align=uiconst.TOPLEFT, setvalue='0.0' if taxRateValue is None else str(100 * taxRateValue), width=90, left=left, top=top, idx=0, maxValue=10000)
        EveLabelMedium(align=uiconst.TOPLEFT, text='%', parent=parent, left=left + 97, top=top + 2)
        taxRate.input = taxRateInput

    def OnMouseEnterInteractable(self, obj, *args):
        obj.SetOpacity(self.HOVER_ALPHA)

    def OnMouseExitInteractable(self, obj, *args):
        obj.SetOpacity(self.NORMAL_ALPHA)

    def Submit(self, *args):
        taxRateValues = {'taxCorporation': self.taxRate.input.GetValue() / 100,
         'taxAlliance': None,
         'taxStandingsHorrible': None,
         'taxStandingsBad': None,
         'taxStandingsNeutral': None,
         'taxStandingsGood': None,
         'taxStandingsHigh': None}
        self.facilitySvc.SetFacilityTaxes(self.facilityID, taxRateValues)
        self.CloseByUser()

    def Cancel(self, *args):
        self.CloseByUser()
