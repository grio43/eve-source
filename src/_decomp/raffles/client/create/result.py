#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\create\result.py
import eveui
from carbonui import TextColor
from raffles.client import sound, texture
from raffles.client.localization import Text, get_error_message
from raffles.client.widget.dotted_progress import DottedProgress

class CreateResult(eveui.Container):

    def __init__(self, controller, navigation, **kwargs):
        super(CreateResult, self).__init__(**kwargs)
        self._navigation = navigation
        self._controller = controller
        self._controller.on_creation_success.connect(self._on_creation_success)
        self._controller.on_creation_failure.connect(self._on_creation_failure)
        self._layout()

    def Close(self):
        super(CreateResult, self).Close()
        self._controller.on_creation_success.disconnect(self._on_creation_success)
        self._controller.on_creation_failure.disconnect(self._on_creation_failure)

    def _on_creation_success(self, raffle):
        self.Flush()
        eveui.play_sound(sound.create_success)
        icon = texture.check_mark_large
        icon_color = TextColor.SUCCESS
        text_title = Text.create_success_title()
        text_message = Text.create_success_message()
        buttons = [(Text.create_another(), self._handle_create_another), (Text.view_raffle(), self._handle_view_raffle)]
        eveui.fade(self, start_value=0, end_value=1, duration=0.3)
        self._construct_message(icon, icon_color, text_title, text_message, buttons)

    def _on_creation_failure(self, error, error_kwargs):
        self.Flush()
        eveui.play_sound(sound.create_failure)
        icon = texture.exclamation_icon
        icon_color = TextColor.WARNING
        text_title = Text.create_failed_title()
        error_kwargs = error_kwargs or {}
        text_message = get_error_message(error, **error_kwargs)
        buttons = [(Text.confirm_creation_failed(), self._handle_confirm_error)]
        eveui.fade(self, start_value=0, end_value=1, duration=0.3)
        self._construct_message(icon, icon_color, text_title, text_message, buttons)

    def _handle_view_raffle(self, *args, **kwargs):
        self._navigation.open_details_page(self._controller.raffle_id)
        self._controller.item = None

    def _handle_create_another(self, *args, **kwargs):
        self._controller.item = None

    def _handle_confirm_error(self, *args, **kwargs):
        self._controller.confirm_create_error()

    def _layout(self):
        DottedProgress(parent=self, align=eveui.Align.center, top=-36, dot_size=6).Show()
        eveui.EveCaptionSmall(parent=self, align=eveui.Align.center, height=24, opacity=0.5, text=Text.creating())

    def _construct_message(self, icon, color, title, text, buttons):
        container = eveui.Container(parent=self, align=eveui.Align.center, width=350, height=100)
        left_side = eveui.Container(name='LeftSide', parent=container, align=eveui.Align.to_left, width=60)
        eveui.Fill(parent=left_side, color=color, opacity=0.15)
        eveui.Sprite(parent=left_side, align=eveui.Align.center_top, texturePath=icon, width=32, height=32, top=14, color=color)
        right_side = eveui.Container(name='RightSide', parent=container)
        eveui.Frame(bgParent=right_side, texturePath=texture.panel_1_corner, color=(0, 0, 0, 0.25), cornerSize=9)
        text_container = eveui.ContainerAutoSize(name='TextContainer', parent=right_side, align=eveui.Align.to_top, padding=(20, 6, 8, 8))
        eveui.EveCaptionSmall(parent=text_container, align=eveui.Align.to_top, text=title)
        eveui.EveLabelMedium(parent=text_container, align=eveui.Align.to_top, text=text)
        button_container = eveui.Container(name='ButtonContainer', parent=right_side, align=eveui.Align.to_bottom, height=28, padding=(0, 0, 6, 6))
        for i, button_data in enumerate(buttons):
            label, func = button_data
            eveui.Button(parent=button_container, align=eveui.Align.to_right, padRight=8 if i != 0 else 0, func=func, label=label)
