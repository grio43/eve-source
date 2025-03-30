#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\structure_design\confirm_revoke_wnd.py
import trinity
import uthread2
from carbonui import uiconst
from carbonui.button.group import ButtonGroup
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import StreamingVideoSprite
from carbonui.uianimations import animations
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelLarge
from eve.client.script.ui.control.loadingContainer import LoadingSpriteSize
from localization import GetByLabel

class ConfirmRevokeWnd(Window):
    default_width = 420
    default_height = 280
    default_windowID = 'confirmRevokeWnd'
    default_useDefaultPos = True
    default_caption = GetByLabel('UI/Personalization/PaintTool/CancelLicenseTitle')
    default_iconNum = 'res:/UI/Texture/classes/paintTool/low_power.png'

    def __init__(self, structure_data, license_data, *args, **kwargs):
        super(ConfirmRevokeWnd, self).__init__(*args, **kwargs)
        self._structure_data = structure_data
        self._license_data = license_data
        self._loading_thread = None
        self._loading_sprite = None
        self.show_window_controls = False
        self.MakeUnResizeable()
        self.DefineButtons(buttons=uiconst.OKCANCEL, okLabel=GetByLabel('UI/Personalization/PaintTool/RevokeLicense'), okFunc=self._on_confirm_button_click, cancelLabel=GetByLabel('UI/Common/Buttons/Cancel'), cancelFunc=self._on_cancel_button_click)
        self._construct_layout()

    def Close(self, *args, **kwargs):
        if self._loading_thread:
            self._loading_thread.kill()
            self._loading_thread = None
        super(ConfirmRevokeWnd, self).Close(*args, **kwargs)

    def _construct_layout(self):
        self._contents_cont = Container(parent=self.content, name='contentsCont')
        remaining_seconds = max(0, self._license_data.get_remaining_time())
        remaining_days = int(remaining_seconds / 86400)
        EveLabelLarge(name='descriptionLabel', parent=self._contents_cont, align=uiconst.TOTOP, text=GetByLabel('UI/Personalization/PaintTool/CancelLicenseBody', structureName=self._structure_data.structure_name, numDays=remaining_days), padTop=20)
        loading_sprite_size = LoadingSpriteSize.MEDIUM
        self._loading_sprite = StreamingVideoSprite(name='loading_sprite', parent=self.content, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=loading_sprite_size, height=loading_sprite_size, videoPath='res:/video/shared/loading_sprite_%s.webm' % loading_sprite_size, videoLoop=True, blendMode=trinity.TR2_SBM_ADD, spriteEffect=trinity.TR2_SFX_COPY, opacity=0.0)
        self._error_message = EveLabelMedium(parent=self.content, name='errorMessage', align=uiconst.TOALL, opacity=0.0, padTop=20)
        Line(parent=self._contents_cont, align=uiconst.TOBOTTOM, padBottom=20)

    def _on_confirm_button_click(self, _button):
        if self._loading_thread is None:
            self._loading_thread = uthread2.start_tasklet(self._send_revoke_request)

    def _send_revoke_request(self):
        try:
            self._on_request_begin()
            cosmetics_license_svc = sm.GetService('cosmeticsLicenseSvc')
            cosmetics_license_svc.request_revoke_license_for_structure(license_id=self._structure_data.license_id)
            self._on_request_end()
            self.SetModalResult(uiconst.ID_OK)
        except Exception:
            self._show_error_message(GetByLabel('UI/Personalization/PaintTool/RevokeRequestErrorDescription'))
        finally:
            self._on_request_end()

    def _on_request_begin(self):
        for component in self.sr.bottom.children:
            if isinstance(component, ButtonGroup):
                for btn in component.buttons:
                    btn.enabled = False

        animations.FadeTo(self._loading_sprite, self._loading_sprite.opacity, 1.0, duration=0.1)
        animations.FadeTo(self._contents_cont, self._contents_cont.opacity, 0.0, duration=0.1)
        animations.FadeTo(self._error_message, self._error_message.opacity, 0.0, duration=0.1)

    def _on_request_end(self):
        self._loading_thread = None
        for component in self.sr.bottom.children:
            if isinstance(component, ButtonGroup):
                for btn in component.buttons:
                    btn.enabled = True

    def _show_error_message(self, msg):
        self._error_message.text = msg
        animations.FadeTo(self._error_message, self._error_message.opacity, 1.0, duration=0.1)
        animations.FadeTo(self._loading_sprite, self._loading_sprite.opacity, 0.0, duration=0.1)
        animations.FadeTo(self._contents_cont, self._contents_cont.opacity, 0.0, duration=0.1)

    def _on_cancel_button_click(self, _button):
        self.SetModalResult(uiconst.ID_CANCEL)
        self.CloseByUser()
