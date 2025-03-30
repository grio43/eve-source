#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\introduction.py
import localization
from carbonui import uiconst
from carbonui.control.editPlainText import EditPlainTextCore
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.control.button import Button
from carbonui.control.checkbox import Checkbox
from carbonui.control.window import Window
from projectdiscovery.client import const

class IntroductionScreen(Window):
    default_fixedHeight = 200
    default_fixedWidth = 400
    default_isStackable = False
    default_isLockable = False
    default_isOverlayable = False

    def ApplyAttributes(self, attributes):
        super(IntroductionScreen, self).ApplyAttributes(attributes)
        caption = localization.GetByLabel('UI/ProjectDiscovery/IntroductionTextWindowCaption')
        self.SetCaption(caption)
        self.setup_layout()

    def setup_layout(self):
        main = self.GetMainArea()
        main.padding = 5
        main_container = Container(parent=main)
        text_container = Container(parent=main_container, height=120, width=250, align=uiconst.TOPRIGHT)
        EditPlainTextCore(parent=text_container, readonly=True, height=128, setvalue=localization.GetByLabel('UI/ProjectDiscovery/IntroductionText'))
        avatar_container = Container(parent=main_container, height=128, width=128, align=uiconst.TOPLEFT)
        Sprite(parent=avatar_container, name='SOE_Logo', align=uiconst.TOTOP, height=128, texturePath='res:/ui/texture/corps/14_128_1.png', ignoreSize=True)
        bottom_container = Container(parent=main_container, height=35, align=uiconst.TOBOTTOM)
        self.close_button = Button(parent=bottom_container, label=localization.GetByLabel('UI/ProjectDiscovery/IntroductionTextContinueButton'), align=uiconst.CENTER, padLeft=20, fixedwidth=100, fixedheight=25, func=lambda x: self.continue_and_check_preference())
        self.checkbox = Checkbox(parent=bottom_container, align=uiconst.CENTERLEFT, padLeft=10)
        self.checkbox.SetLabelText(localization.GetByLabel('UI/ProjectDiscovery/IntroductionScreenCheckboxText'))
        self.checkbox.SetSize(140, 20)

    def continue_and_check_preference(self):
        if self.checkbox.checked:
            settings.char.ui.Set(const.Settings.ProjectDiscoveryIntroductionShown, True)
        else:
            settings.char.ui.Set(const.Settings.ProjectDiscoveryIntroductionShown, False)
        self.CloseByUser()
