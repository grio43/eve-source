#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\addressBook\contactManagementMultiEditWindow.py
import localization
from carbonui import ButtonVariant, uiconst
from carbonui.button.group import ButtonGroup
from carbonui.control.button import Button
from carbonui.control.slider import Slider
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.line import Line
from carbonui.uicore import uicore
from eve.client.script.ui.shared.standings.levelSelector import StandingLevelSelector
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.util import uix

class ContactManagementMultiEditWnd(Window):
    __guid__ = 'form.ContactManagementMultiEditWnd'
    default_fixedWidth = 280
    default_fixedHeight = 100

    def ApplyAttributes(self, attributes):
        super(ContactManagementMultiEditWnd, self).ApplyAttributes(attributes)
        entityIDs = attributes.entityIDs
        contactType = attributes.contactType
        self.result = None
        self.SetCaption(localization.GetByLabel('UI/PeopleAndPlaces/ContactManagement'))
        self.entityIDs = entityIDs
        self.level = None
        self.contactType = contactType
        self.ConstructLayout()

    def ConstructLayout(self):
        self.mainContainer = ContainerAutoSize(name='topCont', parent=self.sr.main, align=uiconst.TOTOP, callback=self.OnMainContainerSizeChanged)
        charnameList = ''
        for entityID in self.entityIDs:
            charName = cfg.eveowners.Get(entityID).name
            if charnameList == '':
                charnameList = '%s' % charName
            else:
                charnameList = '%s, %s' % (charnameList, charName)

        eveLabel.EveLabelLargeBold(text=charnameList, parent=self.mainContainer, align=uiconst.TOTOP, state=uiconst.UI_DISABLED)
        Line(parent=self.mainContainer, align=uiconst.TOTOP, padding=(0, 4, 0, 4))
        self.standingList = {const.contactHighStanding: localization.GetByLabel('UI/PeopleAndPlaces/ExcellentStanding'),
         const.contactGoodStanding: localization.GetByLabel('UI/PeopleAndPlaces/GoodStanding'),
         const.contactNeutralStanding: localization.GetByLabel('UI/PeopleAndPlaces/NeutralStanding'),
         const.contactBadStanding: localization.GetByLabel('UI/PeopleAndPlaces/BadStanding'),
         const.contactHorribleStanding: localization.GetByLabel('UI/PeopleAndPlaces/TerribleStanding')}
        levelList = self.standingList.keys()
        levelList.sort()
        levelText = self.standingList.get(self.level)
        self.levelText = eveLabel.EveLabelMedium(text=levelText, parent=self.mainContainer, align=uiconst.TOTOP, state=uiconst.UI_DISABLED)
        if self.contactType != 'contact':
            bottomCont = Container(name='bottomCont', parent=self.mainContainer, align=uiconst.TOTOP, height=40, padding=uiconst.defaultPadding)
            startVal = 0.5
            sliderContainer = Container(parent=bottomCont, name='sliderContainer', align=uiconst.CENTERTOP, height=20, width=210)
            self.sr.slider = self.AddSlider(sliderContainer, startVal=startVal)
            self.sr.slider.SetValue(startVal)
            boxCont = bottomCont
            iconPadding = 28
        else:
            boxCont = Container(name='boxCont', parent=self.mainContainer, align=uiconst.TOTOP, height=55)
            iconPadding = 6
        levelSelectorContainer = Container(parent=boxCont, name='levelSelectorContainer', align=uiconst.TOTOP, pos=(0, 0, 0, 55))
        self.levelSelector = StandingLevelSelector(name='levelSelector', parent=levelSelectorContainer, align=uiconst.CENTERTOP, pos=(0,
         14,
         100 + iconPadding * 4,
         55), iconPadding=iconPadding)
        self.levelSelector.OnStandingLevelSelected = self.OnStandingLevelSelected
        self.btnGroup = ButtonGroup(parent=self.mainContainer, align=uiconst.TOTOP)
        confirm_button = Button(parent=self.btnGroup, label=localization.GetByLabel('UI/PeopleAndPlaces/EditContact'), func=self.Confirm, args=(), btn_modalresult=1, btn_default=1, variant=ButtonVariant.PRIMARY)
        Button(parent=self.btnGroup, label=localization.GetByLabel('UI/Common/Buttons/Cancel'), func=self.Cancel, args=())
        if self.level is None:
            self.levelText.text = localization.GetByLabel('UI/PeopleAndPlaces/SelectStanding')
            uicore.registry.SetFocus(confirm_button)

    def OnMainContainerSizeChanged(self, *args, **kwds):
        _, height = self.GetWindowSizeForContentSize(height=self.mainContainer.height)
        self.SetFixedHeight(height)

    def AddSlider(self, where, startVal = 0):
        return Slider(name='standing', config='standing', parent=where, on_dragging=self.OnSetValue, minValue=-10.0, maxValue=10.0)

    def OnSetValue(self, slider):
        self.levelText.text = localization.GetByLabel('UI/AddressBook/SliderLabel', value=round(slider.GetValue(), 1), standingText=uix.GetStanding(round(slider.GetValue(), 1)))

    def OnStandingLevelSelected(self, level):
        if self.contactType != 'contact':
            level = level / 20.0 + 0.5
            self.sr.slider.SetValue(level)
        else:
            self.level = level
            self.levelText.text = self.standingList.get(self.level)

    def Confirm(self):
        if self.contactType != 'contact':
            if self.levelText.text == localization.GetByLabel('UI/PeopleAndPlaces/SelectStanding'):
                eve.Message('NoStandingsSelected')
                return
            relationshipID = round(self.sr.slider.value, 1)
        else:
            if self.level is None:
                eve.Message('NoStandingsSelected')
                return
            relationshipID = self.level
        self.result = relationshipID
        if getattr(self, 'isModal', None):
            self.SetModalResult(1)

    def Cancel(self):
        self.result = None
        if getattr(self, 'isModal', None):
            self.SetModalResult(0)
