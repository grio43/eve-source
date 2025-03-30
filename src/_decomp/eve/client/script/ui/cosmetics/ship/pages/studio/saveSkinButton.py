#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\studio\saveSkinButton.py
import eveicon
import uthread2
from carbonui import ButtonStyle, TextBody, TextColor, uiconst
from carbonui.control.button import Button
from cosmetics.client.ships import ship_skin_signals
from cosmetics.client.shipSkinDesignSvc import get_ship_skin_design_svc
from cosmetics.client.ships.qa.settings import should_show_popup_if_skin_name_missing
from cosmetics.client.ships.skins.errors import DESIGN_ERROR_TEXT_BY_CODE, SkinDesignManagementError
from cosmetics.client.ships.skins.live_data import current_skin_design, current_skin_design_signals
from cosmetics.common.ships.skins.static_data import saved_designs_const
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.client.script.ui.control.tooltips import TooltipPanel
from eve.client.script.ui.cosmetics.ship.pages.studio.skinNameDialogue import SkinNameDialogue
from eve.client.script.ui.shared.shipTree.infoBubble import SkillEntry
from localization import GetByLabel
from skills.client.util import get_skill_service

class SaveSkinButton(Button):
    default_texturePath = eveicon.load
    __notifyevents__ = ['OnSkillsChanged']

    def __init__(self, *args, **kwargs):
        super(SaveSkinButton, self).__init__(*args, **kwargs)
        self.func = self.on_save_button_click
        self.design_count = 0
        self.design_limit = 0
        self.has_fitted_components = False
        self.save_requirements_met = False
        self.button_state_thread = None
        self.save_design_thread = None
        self.connect_signals()
        self.update_button_state()

    def Close(self):
        try:
            self.kill_threads()
            self.disconnect_signals()
        finally:
            super(SaveSkinButton, self).Close()

    def kill_threads(self):
        if self.button_state_thread is not None:
            self.button_state_thread.kill()
            self.button_state_thread = None
        if self.save_design_thread is not None:
            self.save_design_thread.kill()
            self.save_design_thread = None

    def connect_signals(self):
        current_skin_design_signals.on_design_reset.connect(self.on_new_design_initialized)
        current_skin_design_signals.on_existing_design_loaded.connect(self.on_existing_design_loaded)
        current_skin_design_signals.on_slot_fitting_changed.connect(self.on_slot_fitting_changed)
        ship_skin_signals.on_skin_design_saved.connect(self.on_skin_design_saved)
        sm.RegisterNotify(self)

    def disconnect_signals(self):
        current_skin_design_signals.on_design_reset.disconnect(self.on_new_design_initialized)
        current_skin_design_signals.on_existing_design_loaded.disconnect(self.on_existing_design_loaded)
        current_skin_design_signals.on_slot_fitting_changed.disconnect(self.on_slot_fitting_changed)
        ship_skin_signals.on_skin_design_saved.disconnect(self.on_skin_design_saved)
        sm.UnregisterNotify(self)

    def OnSkillsChanged(self, *args):
        try:
            self.design_limit = get_ship_skin_design_svc().get_saved_designs_capacity(force_refresh=True)
        except Exception as e:
            self.design_limit = 0

        self.update_button_state()

    def update_button_state(self):
        self.button_state_thread = uthread2.StartTasklet(self.update_button_state_async)

    def update_button_state_async(self):
        self.busy = True
        try:
            self.load_data()
            self.validate_save_requirements()
            self.style = ButtonStyle.NORMAL if self.save_requirements_met else ButtonStyle.DANGER
            self.disabled = not self.has_fitted_components and self.save_requirements_met
        finally:
            self.button_state_thread = None
            self.busy = False

    def load_data(self):
        try:
            self.design_count = len(get_ship_skin_design_svc().get_all_owned_designs())
        except Exception as e:
            self.design_count = 0

        try:
            self.design_limit = get_ship_skin_design_svc().get_saved_designs_capacity()
        except Exception as e:
            self.design_limit = 0

    def validate_save_requirements(self):
        self.has_fitted_components = current_skin_design.get().has_fitted_components()
        self.save_requirements_met = not self.is_restricted_by_design_limit()

    def is_restricted_by_design_limit(self):
        skin_design = current_skin_design.get()
        if skin_design.saved_skin_design_id and skin_design.creator_character_id == session.charid:
            return False
        else:
            return self.design_count >= self.design_limit

    def on_save_button_click(self, *args):
        if not self.save_requirements_met or not self.has_fitted_components:
            return
        if should_show_popup_if_skin_name_missing.is_enabled():
            dialogue = SkinNameDialogue(window_name=self.get_dialogue_window_name())
            dialogue.on_submit.connect(self.on_submit)
            dialogue.on_submit_failed.connect(self.on_submit_failed)
            dialogue.ShowModal()
        else:
            self.on_submit()

    def get_dialogue_window_name(self):
        return GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/SaveDesign')

    def on_submit(self):
        self.save_design_thread = uthread2.StartTasklet(self._save_design_async)

    def _save_design_async(self):
        self.busy = True
        self.disabled = True
        try:
            design_id, error = self.call_save_on_service()
            if error in DESIGN_ERROR_TEXT_BY_CODE:
                label = DESIGN_ERROR_TEXT_BY_CODE[error]
                if error == SkinDesignManagementError.MAX_SAVED_DESIGNS_LIMIT_REACHED:
                    text = GetByLabel(label, current=self.design_count, limit=self.design_limit)
                else:
                    text = GetByLabel(label)
                ShowQuickMessage(text)
            else:
                current_skin_design.get().saved_skin_design_id = design_id
                current_skin_design.get().creator_character_id = session.charid
                current_skin_design.take_snapshot()
                ShowQuickMessage(GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/DesignSaved'))
        except Exception as e:
            ShowQuickMessage(e.message)
            raise
        finally:
            self.save_design_thread = None
            self.disabled = False
            self.busy = False

    def call_save_on_service(self):
        return get_ship_skin_design_svc().save_design(design=current_skin_design.get(), design_id=current_skin_design.get().saved_skin_design_id)

    def on_submit_failed(self, reason):
        ShowQuickMessage(reason)

    def on_new_design_initialized(self, *args):
        self.update_button_state()

    def on_existing_design_loaded(self, *args):
        self.update_button_state()

    def on_slot_fitting_changed(self, *args):
        self.update_button_state()

    def on_skin_design_saved(self, *args):
        self.update_button_state()

    def ConstructTooltipPanel(self):
        if self.save_requirements_met and self.has_fitted_components:
            return SaveSkinTooltip(has_fitted_components=self.has_fitted_components, design_count=self.design_count, design_limit=self.design_limit)
        else:
            return SaveSkinErrorTooltip(has_fitted_components=self.has_fitted_components, design_count=self.design_count, design_limit=self.design_limit)


class SaveAsSkinButton(SaveSkinButton):

    def get_dialogue_window_name(self):
        return GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/SaveAsNew')

    def call_save_on_service(self):
        return get_ship_skin_design_svc().save_design(current_skin_design.get())

    def is_restricted_by_design_limit(self):
        return self.design_count >= self.design_limit


class SaveSkinTooltip(TooltipPanel):
    default_state = uiconst.UI_NORMAL

    def __init__(self, has_fitted_components, design_count, design_limit, *args, **kwargs):
        super(SaveSkinTooltip, self).__init__(*args, **kwargs)
        self.has_fitted_components = has_fitted_components
        self.design_count = design_count
        self.design_limit = design_limit
        self.LoadStandardSpacing()
        self.construct_layout()

    def construct_layout(self):
        self.construct_caption()
        self.construct_save_limit()
        self.construct_skills()

    def construct_caption(self):
        self.AddCaptionSmall(text=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/SaveDesign'))
        self.AddDivider()

    def construct_save_limit(self):
        self.FillRow()
        self.AddLabelMedium(text=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/SaveLimit', current=self.design_count, limit=self.design_limit), width=300)

    def construct_skills(self):
        self.AddSpacer(height=32)
        self.FillRow()
        self.AddCell(TextBody(text=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/MaxSavedDesignsTooltipText'), color=TextColor.SECONDARY, width=300))
        for type_id in saved_designs_const.max_saved_designs_skills:
            self.FillRow()
            self.AddRow(rowClass=SkillEntry, typeID=type_id, level=get_skill_service().GetMyLevel(type_id), showLevel=False)


class SaveSkinErrorTooltip(SaveSkinTooltip):

    def construct_layout(self):
        self.construct_caption()
        if not self.has_fitted_components:
            self.construct_component_warning()
        self.construct_save_limit()
        self.construct_skills()

    def construct_component_warning(self):
        self.FillRow()
        self.AddSpriteLabel(texturePath=eveicon.block_ban, iconSize=16, iconColor=eveColor.DANGER_RED, label=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/NoComponentsSelected'), width=300)

    def construct_save_limit(self):
        if self.design_count < self.design_limit:
            super(SaveSkinErrorTooltip, self).construct_save_limit()
        else:
            self.FillRow()
            self.AddSpriteLabel(texturePath=eveicon.block_ban, iconSize=16, iconColor=eveColor.DANGER_RED, label=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/DesignErrors/SaveLimitReached', current=self.design_count, limit=self.design_limit), width=300)
