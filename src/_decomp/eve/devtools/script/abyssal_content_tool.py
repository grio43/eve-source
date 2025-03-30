#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\abyssal_content_tool.py
import os
import blue
from carbon.common.script.net.moniker import Moniker
from carbonui import uiconst
from carbonui.control.combo import Combo
from carbonui.control.dragResizeCont import DragResizeCont
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.control.button import Button
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from carbonui.control.window import Window
from eve.client.script.ui.control.fileDialog import FileDialog
from eve.client.script.ui.util.utilWindows import NamePopup
from eve.common.script.sys.idCheckers import IsAbyssalSpaceSystem
from eve.devtools.script.abyssal_content_constants import TIER_CHOICES, DUNGEON_ID_CHOICES, NEBULA_CHOICES
from eve.devtools.script.abyssal_content_constants import WEATHER_EFFECT_CHOICES, LENS_FLARE_TYPE_IDS
from eve.devtools.script.abyssal_content_constants import NPC_SPAWN_TABLE_IDS

class AbyssalContentToolWindow(Window):
    default_windowID = 'AbyssalContentTool'
    default_width = 460
    default_height = 300
    default_minSize = (default_width, default_height)
    default_caption = 'Abyssal Content Tool'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.content_details = None
        self.create_buttons()
        self.create_generate_options()
        self.create_room_buttons()
        self.create_feedback_container()
        self.create_plan_editor()

    def create_buttons(self):
        button_container = FlowContainer(name='action_buttons', parent=self.content, centerContent=True, align=uiconst.TOTOP, contentSpacing=(2, 2), state=uiconst.UI_PICKCHILDREN, padding=(0, 0, 0, 8))
        Button(parent=button_container, label='Load from grid', func=self.load_plan_from_grid, align=uiconst.NOALIGN, padding=2)
        Button(parent=button_container, label='Load from file', func=self.load_plan_from_file, align=uiconst.NOALIGN, padding=2)
        Button(parent=button_container, label='Save to file', func=self.save_plan_to_file, align=uiconst.NOALIGN, padding=2)
        Button(parent=button_container, label='Create content', func=self.create_content, align=uiconst.NOALIGN, padding=2)
        Button(parent=button_container, label='Go to Abyssal Space', func=self.tr_to_abyss_space, align=uiconst.NOALIGN, padding=2)

    def create_generate_options(self):
        generate_options_container = FlowContainer(name='create_buttons', parent=self.content, centerContent=True, align=uiconst.TOTOP, contentSpacing=(4, 20), state=uiconst.UI_PICKCHILDREN, padding=(0, 12, 0, 8))
        self.tier_selector = Combo(name='tier_selector', parent=generate_options_container, label='Tier', options=TIER_CHOICES, select=None, align=uiconst.NOALIGN, padding=2)
        self.dungeon_selector = Combo(name='dungeon_selector', parent=generate_options_container, label='Dungeon', options=DUNGEON_ID_CHOICES, select=None, align=uiconst.NOALIGN, padding=2)
        self.nebula_selector = Combo(name='nebula_selector', parent=generate_options_container, label='Nebula', options=NEBULA_CHOICES, select=None, align=uiconst.NOALIGN, padding=2)
        self.weather_selector = Combo(name='weather_selector', parent=generate_options_container, label='Weather', options=WEATHER_EFFECT_CHOICES, select=None, align=uiconst.NOALIGN, padding=2)
        self.lensflare_selector = Combo(name='lensflare_selector', parent=generate_options_container, label='Lens Flare', options=LENS_FLARE_TYPE_IDS, select=None, align=uiconst.NOALIGN, padding=2)
        self.spawn_table_selector = Combo(name='spawn_table_selector', parent=generate_options_container, label='Spawn Table', options=NPC_SPAWN_TABLE_IDS, select=None, align=uiconst.NOALIGN, padding=2)
        Button(parent=generate_options_container, label='Create Encounter', func=self.create_abyss_encounter, align=uiconst.NOALIGN, padding=2)

    def create_room_buttons(self):
        self.room_button_container = FlowContainer(name='room_buttons', parent=self.content, centerContent=True, align=uiconst.TOBOTTOM, contentSpacing=(2, 1), state=uiconst.UI_PICKCHILDREN, padding=(0, 12, 0, 8))

    def create_plan_editor(self):
        self.plan_edit = EditPlainText(parent=self.content, align=uiconst.TOALL, readonly=True, padding=2)

    def create_feedback_container(self):
        container = DragResizeCont(parent=self.content, height=50, minSize=30, align=uiconst.TOBOTTOM, padding=2, clipChildren=True)
        self.feedback_label = EditPlainText(parent=container.mainCont, align=uiconst.TOALL, readonly=True, padTop=2, fontcolor=(0.4, 0.7, 1.0, 0.75))

    def set_room_buttons(self, entry_item_ids_by_location_id):
        for button in self.room_button_container.children[:]:
            button.Close()

        for location_id, entry_item_id in entry_item_ids_by_location_id.iteritems():
            Button(parent=self.room_button_container, label='Go to room #%s' % location_id, func=self.get_tr_func(location_id, entry_item_id), align=uiconst.NOALIGN, padding=2)

    def load_plan_from_file(self, *_):
        path = os.path.join(blue.sysinfo.GetUserDocumentsDirectory(), 'EVE', 'insider', 'abyss')
        file_dialog = FileDialog.SelectFiles(path=path, fileExtensions=['plan'], multiSelect=False)
        if file_dialog is None or len(file_dialog.files) < 1 or file_dialog.files[0] == '':
            self.set_feedback('The file requested is not valid')
            return
        file_name = file_dialog.files[0]
        with open(file_name, 'r') as content_file:
            serialized_plan = content_file.read()
        self.content_details = {'plan': serialized_plan,
         'content_id': 'unknown',
         'entry_item_ids_by_location_id': {}}
        self._load_content_ui()
        self.set_feedback('Loading content details from file: %s' % file_name)

    def load_plan_from_grid(self, *_):
        abyss_content_lm = Moniker('abyssal_content_manager', session.solarsystemid2)
        self.content_details = abyss_content_lm.GetContentDetailsForShipLocation()
        if not self.content_details:
            self.set_feedback('Unable to retrieve content details')
            return
        self._load_content_ui()
        self.set_feedback('Details loaded for content: %s' % self.content_details['content_id'])

    def save_plan_to_file(self, *_):
        if self.content_details is None:
            self.set_feedback('Unable to save content plan.  No content details found.')
            return
        default_path = os.path.join(blue.sysinfo.GetUserDocumentsDirectory(), 'EVE', 'insider', 'abyss', 'content_%s.plan' % self.content_details.get('content_id', ''))
        file_path = NamePopup(caption='Abyss Content Plan Filename', label='Path and filename', setvalue=default_path, maxLength=256)
        if not file_path:
            self.set_feedback('Unable get a valid file name so same content plan.')
            return
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(file_path, 'w') as content_file:
            content_file.write(self.content_details.get('plan', ''))
        self.set_feedback('Saving content plan to file: %s' % file_path)

    def create_content(self, *_):
        serialized_plan = self.content_details.get('plan', '')
        abyss_content_lm = Moniker('abyssal_content_manager', session.solarsystemid2)
        try:
            self.content_details = abyss_content_lm.GenerateContentFromExistingPlan(serialized_plan)
        except Exception as e:
            self.set_feedback('Create content error: %s' % e)
            return

        if not self.content_details:
            self.set_feedback('Unable to generate content!')
            return
        self._load_content_ui()
        self.set_feedback('New content generated: %s' % self.content_details['content_id'])

    def _load_content_ui(self):
        self.set_room_buttons(self.content_details['entry_item_ids_by_location_id'])
        self.plan_edit.SetValue(self.content_details['plan'])

    def get_tr_func(self, location_id, entry_item_id):

        def tr_me(*_):
            sm.GetService('slash').SlashCmd('/tr me %s' % entry_item_id)
            self.set_feedback('You have been moved to entry item %s to room %s in content %s' % (entry_item_id, location_id, self.content_details.get('content_id')))

        return tr_me

    def set_feedback(self, text):
        self.feedback_label.SetValue(text)

    def tr_to_abyss_space(self, *_):
        if IsAbyssalSpaceSystem(session.solarsystemid2):
            self.set_feedback('You are already in an abyssal space system %s' % session.solarsystemid2)
        solar_system_id = 32000001
        sm.GetService('slash').SlashCmd('/tr me %s' % solar_system_id)
        self.set_feedback('You have been moved to abyssal space system %s' % solar_system_id)

    def create_abyss_encounter(self, *_):
        if not IsAbyssalSpaceSystem(session.solarsystemid2):
            self.set_feedback('You must be in abyssal space system to create encounter')
            return
        difficulty_tier = self.tier_selector.GetValue()
        dungeon_id = self.dungeon_selector.GetValue()
        weather_effect_type_id = self.weather_selector.GetValue()
        nebula_graphics_id = self.nebula_selector.GetValue()
        lens_flare_type_id = self.lensflare_selector.GetValue()
        spawn_table_id = self.spawn_table_selector.GetValue()
        abyss_content_lm = Moniker('abyssal_content_manager', session.solarsystemid2)
        try:
            self.content_details = abyss_content_lm.GenerateAbyssEncounterContent(difficulty_tier, dungeon_id, weather_effect_type_id, nebula_graphics_id, lens_flare_type_id, spawn_table_id)
        except Exception as e:
            self.set_feedback('Create content error: %s' % e)
            return

        if not self.content_details:
            self.set_feedback('Unable to generate content!')
            return
        self._load_content_ui()
        self.set_feedback('New encounter generated: %s' % self.content_details['content_id'])
