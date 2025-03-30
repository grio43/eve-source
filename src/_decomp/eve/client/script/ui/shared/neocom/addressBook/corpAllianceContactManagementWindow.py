#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\addressBook\corpAllianceContactManagementWindow.py
import localization
from carbonui import ButtonVariant, uiconst
from carbonui.button.group import ButtonGroup
from carbonui.control.button import Button
from carbonui.control.combo import Combo
from carbonui.control.slider import Slider
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uicore import uicore
from eve.client.script.ui.control import eveIcon, eveLabel
from eve.client.script.ui.shared.standings.levelSelector import StandingLevelSelector
from eve.client.script.ui.util import uix
from eve.common.lib import appConst

class CorpAllianceContactManagementWnd(Window):
    default_fixedHeight = 110
    default_fixedWidth = 280
    default_captionLabelPath = 'UI/PeopleAndPlaces/ContactManagement'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        entityID = attributes.entityID
        level = attributes.level
        if level is None:
            level = appConst.contactNeutralStanding
        isContact = attributes.isContact
        contactType = attributes.contactType
        self.result = None
        self.entityID = entityID
        self.level = level
        self.isContact = isContact
        self.notify = False
        self.contactType = contactType
        self.ConstructLayout()

    def OnMainContainerSizeChanged(self, *args, **kwds):
        _, height = self.GetWindowSizeForContentSize(height=self.mainCont.height)
        self.SetFixedHeight(height)

    def ConstructLayout(self):
        self.mainCont = ContainerAutoSize(name='mainCont', parent=self.sr.main, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, callback=self.OnMainContainerSizeChanged)
        imgCont = Container(name='imgCont', parent=self.mainCont, align=uiconst.TOLEFT, width=64, padRight=uiconst.defaultPadding)
        eveIcon.GetOwnerLogo(imgCont, self.entityID, size=64, noServerCall=True)
        self.ConstructNameCont()
        self.levelText = eveLabel.EveLabelMedium(parent=self.mainCont, align=uiconst.TOTOP, padTop=4)
        self.ConstructStandingSlider()
        self._UpdateStandingLevelText()
        self.levelSelector = StandingLevelSelector(name='levelCont', parent=self.mainCont, align=uiconst.TOTOP, height=20, padTop=4, level=self.level)
        self.levelSelector.OnStandingLevelSelected = self.OnStandingLevelSelected
        self.ConstructLabelsCombo()
        self.ConstructBottomButtons()

    def ConstructBottomButtons(self):
        if self.isContact:
            btnText = localization.GetByLabel('UI/PeopleAndPlaces/EditContact')
        else:
            btnText = localization.GetByLabel('UI/PeopleAndPlaces/AddContact')
        self.btnGroup = ButtonGroup(parent=self.mainCont, align=uiconst.TOTOP, padding=(-64, 16, 0, 0))
        confirm_button = Button(parent=self.btnGroup, label=btnText, func=self.Confirm, args=(), btn_modalresult=1, btn_default=1, variant=ButtonVariant.PRIMARY)
        Button(parent=self.btnGroup, label=localization.GetByLabel('UI/Common/Buttons/Cancel'), func=self.Cancel, args=())
        uicore.registry.SetFocus(confirm_button)

    def ConstructNameCont(self):
        charName = cfg.eveowners.Get(self.entityID).name
        label = eveLabel.EveLabelLargeBold(text=charName, parent=self.mainCont, padTop=2, align=uiconst.TOTOP)

    def ConstructLabelsCombo(self):
        labels = sm.GetService('addressbook').GetContactLabels(self.contactType).values()
        if not self.isContact and len(labels):
            options = self._GetLabelComboOptions(labels)
            self.labelsCombo = Combo(name='labelscombo', label='', parent=self.mainCont, align=uiconst.TOTOP, options=options, padTop=8)
        else:
            self.labelsCombo = None

    def _GetLabelComboOptions(self, labels):
        labelList = []
        for label in labels:
            labelList.append((label.name, label.labelID))

        assignLabelText = localization.GetByLabel('UI/PeopleAndPlaces/AssignLabel')
        labelList.insert(0, (assignLabelText, None))
        return labelList

    def ConstructStandingSlider(self):
        self.standingSlider = Slider(name='standing', parent=self.mainCont, minValue=-10.0, maxValue=10.0, value=self.level if self.isContact else 0, on_dragging=self.UpdateSizeSliderLabel, padRight=52, increments=[ x / 10.0 for x in xrange(-100, 101) ])

    def UpdateSizeSliderLabel(self, slider, *args):
        self._UpdateStandingLevelText()

    def _UpdateStandingLevelText(self):
        standing_value = self.standingSlider.GetValue()
        self.levelText.text = localization.GetByLabel('UI/AddressBook/SliderLabel', value=round(standing_value, 1), standingText=uix.GetStanding(round(standing_value, 1)))

    def OnStandingLevelSelected(self, level):
        self.standingSlider.SetValue(level)
        self._UpdateStandingLevelText()

    def Confirm(self):
        relationshipID = round(self.standingSlider.value, 1)
        contactLabel = None
        if self.labelsCombo:
            contactLabel = self.labelsCombo.GetValue()
        self.result = (relationshipID, contactLabel)
        if getattr(self, 'isModal', None):
            self.SetModalResult(1)

    def Cancel(self):
        self.result = None
        if getattr(self, 'isModal', None):
            self.SetModalResult(0)
