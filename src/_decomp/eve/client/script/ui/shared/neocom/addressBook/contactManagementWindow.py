#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\addressBook\contactManagementWindow.py
import localization
from carbonui import ButtonVariant, uiconst
from carbonui.button.group import ButtonGroup
from carbonui.control.button import Button
from carbonui.control.combo import Combo
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uicore import uicore
from carbonui.util import various_unsorted
from eve.client.script.ui.shared.standings.levelSelector import StandingLevelSelector
from eve.client.script.ui.control import eveEditPlainText, eveIcon, eveLabel
from carbonui.control.checkbox import Checkbox
from eve.common.lib import appConst
from eve.common.script.sys import idCheckers
from localization import GetByLabel
STANDING_DESCRIPTION = {appConst.contactHighStanding: localization.GetByLabel('UI/PeopleAndPlaces/ExcellentStanding'),
 appConst.contactGoodStanding: localization.GetByLabel('UI/PeopleAndPlaces/GoodStanding'),
 appConst.contactNeutralStanding: localization.GetByLabel('UI/PeopleAndPlaces/NeutralStanding'),
 appConst.contactBadStanding: localization.GetByLabel('UI/PeopleAndPlaces/BadStanding'),
 appConst.contactHorribleStanding: localization.GetByLabel('UI/PeopleAndPlaces/TerribleStanding')}

class ContactManagementWnd(Window):
    default_captionLabelPath = 'UI/PeopleAndPlaces/ContactManagement'
    default_fixedWidth = 280

    def ApplyAttributes(self, attributes):
        super(ContactManagementWnd, self).ApplyAttributes(attributes)
        entityID = attributes.entityID
        level = attributes.level
        if level is None:
            level = appConst.contactNeutralStanding
        watchlist = attributes.watchlist
        isContact = attributes.isContact
        self.labelID = attributes.get('labelID', None)
        self.result = None
        self.entityID = entityID
        self.level = level
        self.watchlist = watchlist
        self.isContact = isContact
        self.notify = False
        self.ConstructLayout()

    def OnMainContainerSizeChanged(self, *args, **kwds):
        _, height = self.GetWindowSizeForContentSize(height=self.mainCont.height)
        self.SetFixedHeight(height)

    def ConstructLayout(self):
        self.mainCont = ContainerAutoSize(name='topCont', parent=self.sr.main, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, callback=self.OnMainContainerSizeChanged)
        self.ConstructImage()
        self.ConstructNameLabel()
        self.ConstructLevelSelector()
        self.ConstructLabelsCombo()
        if idCheckers.IsCharacter(self.entityID):
            self.ConstructCharacterOptions()
        self.ConstructBottomButtons()

    def ConstructNameLabel(self):
        charName = self._GetCharName()
        label = eveLabel.EveLabelLargeBold(text=charName, parent=self.mainCont, align=uiconst.TOTOP)

    def _GetCharName(self):
        charName = cfg.eveowners.Get(self.entityID).name
        return charName

    def ConstructImage(self):
        imgCont = Container(name='imgCont', parent=self.mainCont, align=uiconst.TOLEFT, width=64, padRight=uiconst.defaultPadding)
        eveIcon.GetOwnerLogo(imgCont, self.entityID, size=64, noServerCall=True)

    def ConstructBottomButtons(self):
        if self.isContact:
            confirmText = localization.GetByLabel('UI/PeopleAndPlaces/EditContact')
        else:
            confirmText = localization.GetByLabel('UI/PeopleAndPlaces/AddContact')
        self.btnGroup = ButtonGroup(parent=self.mainCont, align=uiconst.TOTOP, padTop=16, padLeft=-64)
        confirm_button = Button(parent=self.btnGroup, label=confirmText, func=self.Confirm, args=(), btn_modalresult=1, btn_default=1, variant=ButtonVariant.PRIMARY)
        Button(parent=self.btnGroup, label=GetByLabel('UI/Common/Buttons/Cancel'), func=self.Cancel, args=())
        uicore.registry.SetFocus(confirm_button)

    def ConstructCharacterOptions(self):
        self.inWatchlistCb = Checkbox(text=localization.GetByLabel('UI/PeopleAndPlaces/AddContactToWatchlist'), parent=self.mainCont, settingsKey='inWatchlistCb', checked=self.watchlist, align=uiconst.TOTOP, hint=localization.GetByLabel('UI/PeopleAndPlaces/BuddyListHint'), padTop=16)
        charName = self._GetCharName()
        self.sendNotificationCb = Checkbox(text=localization.GetByLabel('UI/PeopleAndPlaces/SendNotificationTo', contactName=charName), parent=self.mainCont, settingsKey='sendNotificationCb', checked=0, align=uiconst.TOTOP, callback=self.OnNotificationChange)
        self.message = eveEditPlainText.EditPlainText(setvalue='', parent=self.mainCont, align=uiconst.TOTOP, height=70, state=uiconst.UI_DISABLED, opacity=0.3, maxLength=120, padBottom=uiconst.defaultPadding, hintText=GetByLabel('UI/PeopleAndPlaces/MessageTo', charName=charName))

    def ConstructLabelsCombo(self):
        labels = sm.GetService('addressbook').GetContactLabels('contact').values()
        if not self.isContact and len(labels):
            options = self._GetLabelComboOptions(labels)
            self.labelsCombo = Combo(name='labelscombo', label='', parent=self.mainCont, align=uiconst.TOTOP, options=options, padTop=8)
            if self.labelID:
                self.labelsCombo.SetValue(self.labelID)
        else:
            self.labelsCombo = None

    def _GetLabelComboOptions(self, labels):
        options = []
        for label in labels:
            options.append((label.name.lower(), (label.name, label.labelID)))

        options = various_unsorted.SortListOfTuples(options)
        assignLabelText = '-- %s --' % localization.GetByLabel('UI/Mail/AssignLabel')
        options.insert(0, (assignLabelText, None))
        return options

    def ConstructLevelSelector(self):
        self.levelText = eveLabel.EveLabelMedium(text=self._GetLevelText(), parent=self.mainCont, align=uiconst.TOTOP, state=uiconst.UI_DISABLED, padTop=4)
        self.levelSelector = StandingLevelSelector(name='levelCont', parent=self.mainCont, align=uiconst.TOTOP, height=20, padTop=4, level=self.level)
        self.levelSelector.OnStandingLevelSelected = self.OnStandingLevelSelected

    def _GetLevelText(self):
        if self.level is None:
            levelText = localization.GetByLabel('UI/PeopleAndPlaces/SelectStanding')
        else:
            levelText = STANDING_DESCRIPTION.get(self.level, u'')
        return levelText

    def OnNotificationChange(self, cb):
        if cb.GetValue():
            self.message.opacity = 1.0
            self.message.Enable()
        else:
            self.message.opacity = 0.3
            self.message.Disable()

    def OnStandingLevelSelected(self, level):
        self.level = level
        self.levelText.text = STANDING_DESCRIPTION.get(self.level, u'')

    def Confirm(self):
        relationshipID = self.level
        inWatchlist = False
        sendNotification = False
        message = None
        contactLabel = None
        if self.labelsCombo:
            contactLabel = self.labelsCombo.GetValue()
        if idCheckers.IsCharacter(self.entityID):
            inWatchlist = self.inWatchlistCb.checked
            sendNotification = self.sendNotificationCb.checked
            message = self.message.GetValue()
        self.result = (relationshipID,
         inWatchlist,
         sendNotification,
         message,
         contactLabel)
        if getattr(self, 'isModal', None):
            self.SetModalResult(1)

    def Cancel(self):
        self.result = None
        if getattr(self, 'isModal', None):
            self.SetModalResult(0)
