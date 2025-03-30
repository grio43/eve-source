#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skilltrading\skillInjectorWindow.py
import localization
import uthread
from carbon.common.script.util.format import FmtAmt
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from carbonui.button.group import ButtonGroup
from eve.client.script.ui.control.eveLabel import Label, EveLabelMedium
from carbonui.control.window import Window
from eve.client.script.ui.control.itemIcon import ItemIcon
from eve.client.script.ui.skilltrading.skillInjectorBar import SkillInjectorBar
from eveexceptions import UserError
COLOR_INJECTED = (0.871, 0.118, 0.0, 1.0)
DEFAULT_WINDOW_HEIGHT = 280
SMALL_WINDOW_HEIGHT = 250

class SkillInjectorWindow(Window):
    default_fixedHeight = DEFAULT_WINDOW_HEIGHT
    default_fixedWidth = 550
    default_windowID = 'SkillInjectorWindow'
    default_captionLabelPath = 'UI/SkillTrading/SkillInjectorWindowCaption'
    default_iconNum = 'res:/UI/Texture/WindowIcons/augmentations.png'
    default_clipChildren = True
    default_isCollapseable = False
    default_isLightBackgroundConfigurable = False
    default_isStackable = False
    default_isMinimizable = False
    default_isLockable = False
    default_isOverlayable = False
    __notifyevents__ = ['OnSessionChanged', 'OnNonDiminishingInjectionsChanged']

    def OnSessionChanged(self, isRemote, session, change):
        if 'locationid' in change:
            self.Close()

    def OnNonDiminishingInjectionsChanged(self):
        if not self.injectionStarted:
            self.Reload(self)

    @classmethod
    def OpenOrReload(cls, *args, **kwargs):
        if cls.IsOpen():
            wnd = cls.GetIfOpen()
            wnd.injectorItem = kwargs.get('injectorItem')
            wnd.quantity = kwargs.get('quantity')
            wnd.Reload(wnd)
            wnd.Maximize()
        else:
            cls.Open(*args, **kwargs)

    @classmethod
    def Reload(cls, instance):
        uthread.new(instance._Reload)

    def ApplyAttributes(self, attributes):
        super(SkillInjectorWindow, self).ApplyAttributes(attributes)
        self.injectorItem = attributes.injectorItem
        self.injectionStarted = False
        self.quantity = attributes.get('quantity', self.injectorItem.stacksize)
        self.mainArea = self.GetMainArea()
        self.ConstructLayout()
        self.CheckConstraints()
        self.totalPoints = self.GetTotalPoints()
        self.Update()

    def ConstructLayout(self):
        self.HideHeader()
        self.ConstructHeader()
        self.ConstructFooter()
        self.mainContainer = Container(name='MainContainer', parent=self.mainArea, padding=(4, 0, 4, 0))
        self.injectionMessage = Label(name='InjectionMessageLabel', parent=self.mainContainer, align=uiconst.TOTOP, top=20)
        self.ConstructErrorLabel()
        self.ConstructInjectorBar()

    def ConstructFooter(self):
        footerContainer = Container(name='footerContainer', parent=self.mainArea, align=uiconst.TOBOTTOM, height=35, bgColor=(0.133, 0.133, 0.141, 0.7), padding=(4, 0, 4, 4))
        self.buttonGroup = ButtonGroup(name='buttonGroup', parent=footerContainer, align=uiconst.CENTER)
        self.buttonGroup.AddButton(localization.GetByLabel('UI/SkillTrading/ConfirmInjectionLabel'), self.StartInjection)
        self.buttonGroup.AddButton(localization.GetByLabel('UI/SkillTrading/CancelInjectionLabel'), self.CloseByUser)

    def ConstructErrorLabel(self):
        errorLabelContainer = Container(name='ErrorLabelContainer', parent=self.mainContainer, align=uiconst.TOALL)
        self.errorLabel = EveLabelMedium(parent=errorLabelContainer, align=uiconst.CENTERTOP, top=20, opacity=0, width=self.default_fixedWidth - 50)

    def ConstructInjectorBar(self):
        self.injectorBarContainer = Container(name='InjectorBarContainer', parent=self.mainContainer, align=uiconst.TOALL)
        self.skillInjectorBar = SkillInjectorBar(name='SkillInjectorBar', parent=self.injectorBarContainer, align=uiconst.CENTER, injectorItem=self.injectorItem, onComplete=self.CloseByUser, opacity=0)

    def ConstructHeader(self):
        headerContainer = Container(name='HeaderContainer', parent=self.mainArea, align=uiconst.TOTOP, height=35, bgColor=(0.133, 0.133, 0.141, 0.7), padding=(4, 4, 4, 0))
        iconContainer = Container(name='IconContainer', parent=headerContainer, align=uiconst.TOLEFT, width=32, height=32)
        ItemIcon(name='InjectorIcon', parent=iconContainer, typeID=self.injectorItem.typeID, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED)
        labelContainer = ContainerAutoSize(name='HeaderLabelContainer', parent=headerContainer, align=uiconst.TOLEFT)
        Label(name='ConfirmInjectionLabel', parent=labelContainer, align=uiconst.CENTERLEFT, text=localization.GetByLabel('UI/SkillTrading/SkillInjectorWindowCaption'))

    def _Reload(self):
        self.mainArea.Flush()
        self.ConstructLayout()
        self.CheckConstraints()
        self.totalPoints = self.GetTotalPoints()
        self.Update()

    def Update(self):
        self.injectionMessage.SetText(localization.GetByLabel('UI/SkillTrading/InjectionMessage', amount=self.quantity, injector=self.injectorItem.typeID, charid=session.charid, totalpoints=FmtAmt(self.totalPoints)))
        self.skillInjectorBar.SetTotalPoints(self.totalPoints + sm.GetService('skills').GetFreeSkillPoints())

    def StartInjection(self, *args):
        try:
            self.injectionStarted = True
            sm.GetService('skills').ActivateSkillInjector(self.injectorItem.itemID, self.quantity)
        except UserError:
            self.injectionStarted = False
            raise

        self.skillInjectorBar.OnInjectionStarted()
        animations.FadeOut(self.buttonGroup, callback=self.ReplaceButtonGroup)

    def GetTotalPoints(self):
        try:
            return sm.GetService('skills').GetSkillPointAmountFromInjectors(self.injectorItem.typeID, self.quantity)
        except UserError as error:
            self.SetHeightToSmall()
            self.HandleException(error)

    def CheckConstraints(self):
        try:
            sm.GetService('skills').CheckInjectionConstraints(self.injectorItem.itemID, self.quantity)
        except UserError as error:
            self.SetHeightToSmall()
            self.buttonGroup.buttons[0].Disable()
            self.HandleException(error)
        else:
            animations.FadeIn(self.skillInjectorBar, duration=0.3)
            self.SetHeightToDefault()

    def HandleException(self, error):
        baseText = u'<color=#FFBC711A>%s</color>'
        errorLabel = 'UI/SkillTrading/ErrorMessages/%s' % error.msg
        if error.msg == 'InjectorSkillPointLimitReached':
            self.DisplayErrorMessage(baseText % localization.GetByLabel(errorLabel, typeID=error.dict['typeID'], limit=error.dict['limit']))
        elif error.msg == 'AlreadyInjectedToday':
            self.DisplayErrorMessage(baseText % localization.GetByLabel(errorLabel, type=self.injectorItem.typeID, time=sm.GetService('skills').GetDurationUntilNextAlphaInjection()))
        else:
            self.DisplayErrorMessage(baseText % localization.GetByLabel(errorLabel))

    def DisplayErrorMessage(self, message):
        animations.FadeOut(self.injectorBarContainer, duration=0.15, sleep=True)
        self.errorLabel.SetText(message)
        animations.FadeIn(self.errorLabel, duration=0.3)

    def ReplaceButtonGroup(self):
        self.buttonGroup.FlushButtons()
        self.buttonGroup.AddButton(localization.GetByLabel('UI/SkillTrading/CloseInjectionLabel'), self.CloseByUser)
        animations.FadeIn(self.buttonGroup)

    def SetHeightToSmall(self):
        self.SetFixedHeight(SMALL_WINDOW_HEIGHT)
        self.SetHeight(SMALL_WINDOW_HEIGHT)

    def SetHeightToDefault(self):
        self.SetFixedHeight(DEFAULT_WINDOW_HEIGHT)
        self.SetHeight(DEFAULT_WINDOW_HEIGHT)
