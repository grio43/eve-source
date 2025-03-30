#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\structure\pages\summaryPage.py
from carbonui import const as uiconst
from carbonui.button.const import ButtonVariant
from carbonui.button.group import ButtonGroup, ButtonSizeMode
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveCaptionLarge
from eve.client.script.ui.cosmetics.structure import paintToolSelections
from eve.client.script.ui.cosmetics.structure.components.previewScene import PreviewPanel
from eve.client.script.ui.cosmetics.structure.pages.basePage import BasePage
import eve.client.script.ui.cosmetics.structure.const as paintToolConst
import eve.client.script.ui.cosmetics.structure.paintToolSignals as paintToolSignals
from localization import GetByLabel
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 40
BUTTON_PADDING = 12

class SummaryPage(BasePage):

    def __init__(self, **kw):
        super(SummaryPage, self).__init__(**kw)
        paintToolSignals.on_paintwork_selection_changed.connect(self._on_paint_selection_changed)
        paintToolSignals.on_structure_selection_changed.connect(self._on_structure_selection_changed)
        paintToolSignals.on_duration_selection_changed.connect(self._on_duration_selection_changed)
        self._update_info_label()

    def Close(self):
        paintToolSignals.on_paintwork_selection_changed.disconnect(self._on_paint_selection_changed)
        paintToolSignals.on_structure_selection_changed.disconnect(self._on_structure_selection_changed)
        paintToolSignals.on_duration_selection_changed.disconnect(self._on_duration_selection_changed)
        super(SummaryPage, self).Close()

    def _open_page(self):
        self._live_preview.display = True
        super(SummaryPage, self)._open_page()

    def _close_page(self):
        self._live_preview.display = False
        super(SummaryPage, self)._close_page()

    def _construct_layout(self):
        self._content_cont = Container(parent=self, name='content', align=uiconst.TOALL)
        self._create_buttons()
        self._create_thank_you_message()
        self._create_live_preview()

    def _create_live_preview(self):
        self._live_preview = PreviewPanel(name='preview_panel', parent=self)
        self._live_preview.display = False

    def _create_buttons(self):
        btn_cont = Container(name='btnCont', parent=self._content_cont, align=uiconst.TOBOTTOM, height=132)
        btn_group = ButtonGroup(parent=btn_cont, align=uiconst.CENTERTOP, width=2 * BUTTON_WIDTH, button_size_mode=ButtonSizeMode.STRETCH)
        Button(name='closeBtn', parent=btn_group, label=GetByLabel('UI/Personalization/PaintTool/CloseButton'), variant=ButtonVariant.GHOST, func=self._on_close_clicked)
        Button(name='newDesignBtn', parent=btn_group, label=GetByLabel('UI/Personalization/PaintTool/NewDesignButton'), func=self._on_new_design_clicked)

    def _create_thank_you_message(self):
        EveLabelMedium(parent=ContainerAutoSize(parent=self._content_cont, name='delayLabelCont', align=uiconst.TOBOTTOM), name='activationDelayLabel', text=GetByLabel('UI/Personalization/PaintTool/ActivationProcessDelay'), align=uiconst.CENTER, padBottom=51)
        self._info_label = EveLabelMedium(parent=ContainerAutoSize(parent=self._content_cont, name='infoLabelCont', align=uiconst.TOBOTTOM), name='activationDelayLabel', align=uiconst.CENTER, padBottom=8)
        EveCaptionLarge(parent=ContainerAutoSize(parent=self._content_cont, name='thanksLabelCont', align=uiconst.TOBOTTOM), name='thankYouLabel', text=GetByLabel('UI/Personalization/PaintTool/ThankPurchase'), align=uiconst.CENTER, padBottom=8)
        Sprite(parent=Container(parent=self._content_cont, name='logoCont', align=uiconst.TOBOTTOM, height=32), align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED, pos=(0, -18, 34, 32), texturePath='res:/UI/Texture/classes/paintTool/paragon_logo.png')

    def _update_info_label(self):
        duration = paintToolSelections.SELECTED_DURATION / 86400 if paintToolSelections.SELECTED_DURATION > 0 else 0
        self._info_label.text = GetByLabel('UI/Personalization/PaintTool/ActivatedLicenseDetails', numStructures=len(paintToolSelections.SELECTED_STRUCTURES), numDays=duration)

    def _on_close_clicked(self, *args):
        paintToolSignals.on_close_window_requested()

    def _on_new_design_clicked(self, *args):
        paintToolSelections.SELECTED_PAGE.set(paintToolConst.STRUCTURE_SELECTION_PAGE_ID)

    def _on_paint_selection_changed(self, _slot_id, _paint_id):
        self._live_preview.update(paintToolSelections.SELECTED_STRUCTURE_TYPE.get(), fit_in_view=False)

    def _on_structure_selection_changed(self, *_args):
        self._update_info_label()

    def _on_duration_selection_changed(self):
        self._update_info_label()
