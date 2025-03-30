#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\shipNameDialog.py
import localization
import carbonui
import carbonui.const as uiconst
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.control.button import Button
from carbonui.button.group import ButtonGroup, ButtonSizeMode
from carbonui.control.checkbox import Checkbox
from carbonui.control.window import Window
from carbon.client.script.environment.AudioUtil import PlaySound
from eve.client.script.ui.control.infoIcon import QuestionMarkGlyphIcon
from eve.client.script.ui.control.themeColored import FrameThemeColored, SpriteThemeColored
from carbonui.services.setting import SuppressSettingBool

def prompt_rename_ship(ship_type_id, name = '', show_suppress = False):
    wnd = ShipNameDialog.Open(ship_type_id=ship_type_id, current_name=name, show_suppress=show_suppress)
    if wnd.ShowModal() == 1:
        return wnd.result
    else:
        return None


class ShipNameDialog(Window):
    default_name = 'ShipNameDialog'
    default_windowID = 'ship_name_dialog'
    default_captionLabelPath = 'UI/Ship/NameChange/WindowTitle'
    default_width = 360
    default_height = 160
    default_minSize = (default_width, default_height)
    default_isStackable = False
    result = None

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.show_window_controls = False
        self.MakeUnResizeable()
        current_name = attributes.get('current_name', '')
        show_suppress = attributes.get('show_suppress', False)
        self._hint_text = localization.GetByLabel('UI/Inflight/OwnerAndShip', session.languageID, charID=session.charid, shipTypeID=attributes.get('ship_type_id'))
        self._main_container = main = ContainerAutoSize(parent=self.content, align=carbonui.Align.TOTOP, callback=self._on_content_size_changed)
        self._input_field = SingleLineEditText(parent=main, align=carbonui.Align.TOTOP, label=localization.GetByLabel('UI/Ship/NameChange/InputFieldLabel'), setvalue=current_name, hintText=self._hint_text, maxLength=32, autoselect=True, showLetterCounter=True, OnReturn=self._confirm, padTop=16)
        MoreInfoContainer(parent=main, align=carbonui.Align.TOTOP, padTop=8, text=localization.GetByLabel('UI/Ship/NameChange/InfoLabel'), hint=localization.GetByLabel('UI/Ship/NameChange/InfoTooltip'))
        if show_suppress:
            suppress_setting = SuppressSettingBool('suppress.ShipNameChangeOnAssemble', False)
            Checkbox(parent=main, align=carbonui.Align.TOTOP, text=localization.GetByLabel('/Carbon/UI/Common/DoNotAskAgain'), setting=suppress_setting, padTop=8)
        button_group = ButtonGroup(parent=main, align=uiconst.TOTOP, button_size_mode=ButtonSizeMode.STRETCH, padTop=8)
        Button(parent=button_group, label=localization.GetByLabel('UI/Common/Confirm'), func=self._confirm, variant=carbonui.ButtonVariant.PRIMARY)
        Button(parent=button_group, label=localization.GetByLabel('UI/Common/Later'), func=self._cancel)

    def _confirm(self, *args, **kwargs):
        self.result = (self._input_field.GetValue() or self._hint_text).replace('\n', ' ').strip()
        PlaySound('ship_goals_name_ship_play')
        self.SetModalResult(1)

    def _cancel(self, *args, **kwargs):
        self.result = None
        self.SetModalResult(0)

    def _on_content_size_changed(self):
        _, self.height = self.GetWindowSizeForContentSize(height=self._main_container.height)


class MoreInfoContainer(ContainerAutoSize):
    default_alignMode = carbonui.Align.CENTERLEFT

    def __init__(self, text, hint, *args, **kwargs):
        super(MoreInfoContainer, self).__init__(*args, **kwargs)
        QuestionMarkGlyphIcon(parent=self, align=carbonui.Align.CENTERLEFT, hint=hint, left=8)
        carbonui.TextDetail(parent=self, align=carbonui.Align.CENTERLEFT, padding=(32, 8, 8, 8), text=text)
        SpriteThemeColored(name='cornerSprite', parent=self, align=carbonui.Align.TOPLEFT, texturePath='res:/UI/Texture/Shared/DarkStyle/cornerTriSmall.png', pos=(0, 0, 8, 8))
        FrameThemeColored(bgParent=self, texturePath='res:/UI/Texture/classes/Agency/fleetup/solidFrame_12corner.png', cornerSize=12, colorType=carbonui.uiconst.COLORTYPE_ACCENT, opacity=0.3)
