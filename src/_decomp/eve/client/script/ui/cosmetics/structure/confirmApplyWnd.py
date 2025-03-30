#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\structure\confirmApplyWnd.py
import trinity
import uthread2
from carbon.common.script.util.format import FmtAmt
from carbonui import uiconst, TextColor
from carbonui.button.group import ButtonGroup
from carbonui.control.button import Button
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite, StreamingVideoSprite
from carbonui.uianimations import animations
from cosmetics.common.structures.exceptions import StructurePaintError, InvalidDataError, InsufficientRolesError, InsufficientBalanceError, ForbiddenRequestError
from eve.client.script.ui.control.eveLabel import EveLabelLarge, EveLabelMedium
from eve.client.script.ui.control.loadingContainer import LoadingSpriteSize
from eve.client.script.ui.control.message import ShowQuickMessage
from localization import GetByLabel

class ConfirmApplyWnd(Window):
    default_width = 450
    default_height = 240
    default_windowID = 'confirmApplyWnd'
    default_useDefaultPos = True
    default_caption = GetByLabel('UI/Personalization/PaintTool/PurchaseSummary')
    default_iconNum = 'res:/UI/Texture/WindowIcons/paint_tool.png'

    def __init__(self, paintwork, structure_ids, duration_days = 0, total_em_cost = 0, *args, **kwargs):
        super(ConfirmApplyWnd, self).__init__(*args, **kwargs)
        self._paintwork = paintwork
        self._structure_ids = structure_ids
        self._duration_days = duration_days
        self._total_em_cost = total_em_cost
        self._loading_thread = None
        self._loading_sprite = None
        self.show_window_controls = False
        self.MakeUnResizeable()
        self.DefineButtons(buttons=uiconst.OKCANCEL, okLabel=GetByLabel('UI/Personalization/PaintTool/BuyAndActivate'), okFunc=self._on_confirm_button_click, cancelLabel=GetByLabel('UI/Common/Buttons/Cancel'), cancelFunc=self._on_cancel_button_click)
        self._construct_layout()

    def Close(self, *args, **kwargs):
        if self._loading_thread:
            self._loading_thread.kill()
            self._loading_thread = None
        super(ConfirmApplyWnd, self).Close(*args, **kwargs)

    def _construct_layout(self):
        self._contents_cont = Container(parent=self.content, name='contentsCont')
        EveLabelLarge(name='license_type_label', parent=self._contents_cont, align=uiconst.TOTOP, text=GetByLabel('UI/Personalization/PaintTool/LicenseType', description_color=TextColor.SECONDARY, duration_color=TextColor.HIGHLIGHT, duration_days=self._duration_days), padTop=20)
        EveLabelLarge(name='number_of_structures_label', parent=self._contents_cont, align=uiconst.TOTOP, text=GetByLabel('UI/Personalization/PaintTool/NumberOfStructures', description_color=TextColor.SECONDARY, amount_color=TextColor.HIGHLIGHT, amount=len(self._structure_ids)), padTop=4)
        currency_icon_size = 20
        total_cost_container = Container(name='total_cost_container', parent=self._contents_cont, align=uiconst.TOTOP, padTop=4, height=currency_icon_size)
        EveLabelLarge(name='total_cost_label', parent=total_cost_container, align=uiconst.TOLEFT, text=GetByLabel('UI/Personalization/PaintTool/TotalCost'), color=TextColor.SECONDARY)
        Sprite(name='evermarks_icon', parent=total_cost_container, align=uiconst.TOLEFT, texturePath='res:/UI/Texture/Icons/evermarks.png', width=currency_icon_size, height=currency_icon_size)
        EveLabelLarge(name='total_cost_currency', parent=total_cost_container, align=uiconst.TOLEFT, text=FmtAmt(self._total_em_cost), color=TextColor.HIGHLIGHT)
        loading_sprite_size = LoadingSpriteSize.MEDIUM
        self._loading_sprite = StreamingVideoSprite(name='loading_sprite', parent=self.content, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=loading_sprite_size, height=loading_sprite_size, videoPath='res:/video/shared/loading_sprite_%s.webm' % loading_sprite_size, videoLoop=True, blendMode=trinity.TR2_SBM_ADD, spriteEffect=trinity.TR2_SFX_COPY, opacity=0.0)
        self._error_message = EveLabelMedium(parent=self.content, name='errorMessage', align=uiconst.TOALL, opacity=0.0, padTop=20)
        Line(parent=self._contents_cont, align=uiconst.TOBOTTOM, padBottom=20)

    def _on_confirm_button_click(self, _button):
        if self._loading_thread is None:
            self._loading_thread = uthread2.start_tasklet(self._send_apply_request)

    def _send_apply_request(self):
        try:
            self._on_apply_request_begin()
            cosmetics_license_svc = sm.GetService('cosmeticsLicenseSvc')
            cosmetics_license_svc.request_license_for_structures(structure_ids=self._structure_ids, paintwork=self._paintwork, duration=self._duration_days * 86400)
            self._on_apply_request_end()
            self.SetModalResult(uiconst.ID_OK)
        except StructurePaintError:
            self._show_error_message(GetByLabel('UI/Personalization/PaintTool/IssueRequestErrorDescription'))
        except InvalidDataError:
            self._show_error_message(GetByLabel('UI/Personalization/PaintTool/IssueRequestErrorDescription'))
        except InsufficientRolesError:
            self._show_error_message(GetByLabel('UI/Personalization/PaintTool/IssueRequestRolesErrorDescription'))
        except InsufficientBalanceError:
            self._show_error_message(GetByLabel('UI/Personalization/PaintTool/IssueRequestBalanceErrorDescription'))
        except ForbiddenRequestError:
            self._show_error_message(GetByLabel('UI/Personalization/PaintTool/IssueRequestErrorDescription'))
        except Exception:
            self._show_error_message(GetByLabel('UI/Personalization/PaintTool/IssueRequestErrorDescription'))
        finally:
            self._on_apply_request_end()

    def _on_apply_request_begin(self):
        for component in self.sr.bottom.children:
            if isinstance(component, ButtonGroup):
                for btn in component.buttons:
                    btn.enabled = False

        animations.FadeTo(self._loading_sprite, self._loading_sprite.opacity, 1.0, duration=0.1)
        animations.FadeTo(self._contents_cont, self._contents_cont.opacity, 0.0, duration=0.1)
        animations.FadeTo(self._error_message, self._error_message.opacity, 0.0, duration=0.1)

    def _on_apply_request_end(self):
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
