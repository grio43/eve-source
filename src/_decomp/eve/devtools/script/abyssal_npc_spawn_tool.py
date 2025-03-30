#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\abyssal_npc_spawn_tool.py
import csv
import os
import blue
import evetypes
import gametime
from carbon.common.script.util.format import FmtDate
from carbonui import uiconst
from carbonui.control.combo import Combo
from carbonui.control.dragResizeCont import DragResizeCont
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.control.button import Button
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from carbonui.control.window import Window
from eve.client.script.ui.util.utilWindows import NamePopup
from eve.devtools.script.abyssal_content_constants import TIER_CHOICES, NPC_SPAWN_TABLE_IDS

class AbyssalNpcSpawnToolWindow(Window):
    default_windowID = 'AbyssalNpcSpawnTool'
    default_width = 400
    default_height = 300
    default_minSize = (default_width, default_height)
    default_caption = 'Abyssal NPC Spawn Tool'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.content_details = None
        self.create_generate_options()
        self.create_buttons()
        self.create_feedback_container()
        self.create_report_container()

    def create_buttons(self):
        button_container = FlowContainer(name='action_buttons', parent=self.sr.main, centerContent=True, align=uiconst.TOTOP, contentSpacing=(2, 2), state=uiconst.UI_PICKCHILDREN, padding=(2, 4, 2, 4))
        Button(parent=button_container, label='Save Group Summary To File', func=self.save_group_summary_csv_to_file, align=uiconst.NOALIGN, padding=2)
        Button(parent=button_container, label='Save NPC Details To File', func=self.save_npc_details_csv_to_file, align=uiconst.NOALIGN, padding=2)

    def create_generate_options(self):
        generate_options_container = FlowContainer(name='option_selectors', parent=self.sr.main, centerContent=True, align=uiconst.TOTOP, contentSpacing=(4, 20), state=uiconst.UI_PICKCHILDREN, padding=(2, 12, 2, 4))
        self.tier_selector = Combo(name='tier_selector', parent=generate_options_container, label='Tier', options=TIER_CHOICES, select=None, align=uiconst.NOALIGN, padding=2)
        self.spawn_table_selector = Combo(name='spawn_table_selector', parent=generate_options_container, label='Spawn Table', options=NPC_SPAWN_TABLE_IDS[1:], select=None, align=uiconst.NOALIGN, padding=2)
        self.repetitions_selector = Combo(name='repetitions_selector', parent=generate_options_container, label='Repetitions', options=[('1', 1),
         ('5', 5),
         ('10', 10),
         ('20', 20),
         ('50', 50)], select=None, align=uiconst.NOALIGN, padding=2)
        Button(parent=generate_options_container, label='Generate Report', func=self.generate_report, align=uiconst.NOALIGN, padding=2)

    def create_report_container(self):
        self.report_edit = EditPlainText(parent=self.sr.main, align=uiconst.TOALL, readonly=True, padding=2)

    def create_feedback_container(self):
        container = DragResizeCont(parent=self.sr.main, height=50, minSize=30, align=uiconst.TOBOTTOM, padding=2, clipChildren=True)
        self.feedback_label = EditPlainText(parent=container, align=uiconst.TOALL, readonly=True, padTop=2, fontcolor=(0.4, 0.7, 1.0, 0.75))

    def set_feedback(self, text):
        self.feedback_label.SetValue('[%s] %s' % (FmtDate(gametime.GetWallclockTime()), text))

    def generate_report(self, *_):
        try:
            difficulty_tier = self.tier_selector.GetValue()
            spawn_table_id = self.spawn_table_selector.GetValue()
            repetitions = self.repetitions_selector.GetValue()
            self.content_details = sm.RemoteSvc('abyssal_content_manager').generate_abyss_npc_spawn_report(difficulty_tier, spawn_table_id, repetitions)
        except Exception as e:
            self.report_edit.SetText('')
            self.set_feedback('Create content error: %s' % e)
            return

        if not self.content_details:
            self.report_edit.SetText('')
            self.set_feedback('Unable to generate report!')
            return
        self.report_edit.SetValue(self.format_results(self.content_details))
        self.set_feedback('Generated new report')

    def format_results(self, results):
        lines = ['Average Spawn Points: Requested %s, spent %s, leaving %s unspent' % (results['average_spawn_points'], results['average_spent_points'], results['average_remaining_points']), 'Average Number Of NPCs: %s' % results['average_number_of_npcs'], 'Unsupported Tags: %s %s' % (results['unsupported_tag_names'], results['unsupported_tags'])]
        for spawn in results['spawns']:
            lines.extend(['',
             'Npc Fleet Type: %s [%s]' % (spawn['npc_fleet_type_name'], spawn['npc_fleet_type_id']),
             'Group Behavior: %s [%s]' % (spawn['group_behavior_name'], spawn['group_behavior_id']),
             'Spawn Points: Requested %s, spent %s, leaving %s unspent' % (spawn['spawn_points'], spawn['spent_points'], spawn['remaining_points']),
             'Spawn Tags: %s %s' % (spawn['npc_fleet_spawn_tag_names'], spawn['npc_fleet_spawn_tags'])])
            for npc in spawn['npcs']:
                lines.extend(['  %s x %s [%s]' % (npc['quantity'], evetypes.GetName(npc['type_id']), npc['type_id']),
                 '    Behavior: %s [%s]' % (npc['behavior_name'], npc['behavior_id']),
                 '    Cost: %s Total Cost: %s' % (npc['cost'], npc['total_cost']),
                 '    Tags: %s %s' % (npc['npc_tag_names'], npc['npc_tags'])])

        return '<br>'.join(lines)

    def save_group_summary_csv_to_file(self, *_):
        header = ['Spawn Number',
         'NPC Fleet Type Name',
         'NPC Fleet Type ID',
         'Spawn Points Requested',
         'Spawn Points Spent',
         'Spawn Points Remaining',
         'NPCs',
         'NPC Fleet Type Tags',
         'NPC Fleet Type Tag IDs',
         'Group Behavior Name',
         'Group Behavior ID']
        data_rows = []
        for index, spawn in enumerate(self.content_details['spawns']):
            npcs = spawn['npcs']
            data_rows.append([index + 1,
             spawn['npc_fleet_type_name'],
             spawn['npc_fleet_type_id'],
             spawn['spawn_points'],
             spawn['spent_points'],
             spawn['remaining_points'],
             ', '.join([ '%sx%s [%s] %s' % (npc['quantity'],
              evetypes.GetName(npc['type_id']),
              npc['type_id'],
              npc['total_cost']) for npc in npcs ]),
             spawn['npc_fleet_spawn_tag_names'],
             spawn['npc_fleet_spawn_tags'],
             spawn['group_behavior_name'],
             spawn['group_behavior_id']])

        title = 'Group Summary CSV Filename'
        spawn_table_id = self.content_details['spawn_table_id']
        difficulty_tier = self.content_details['difficulty_tier']
        default_file_name = 'group_summary_table_%s_tier_%s.csv' % (spawn_table_id, difficulty_tier)
        self.save_csv_to_file(header, data_rows, title, default_file_name)

    def save_npc_details_csv_to_file(self, *_):
        header = ['Spawn Number',
         'Type Name',
         'Type ID',
         'Behavior Name',
         'Behavior ID',
         'Cost',
         'Tags',
         'Tag IDs',
         'Weight']
        data_rows = []
        for index, spawn in enumerate(self.content_details['spawns']):
            for npc in spawn['npcs']:
                quantity = npc['quantity']
                behavior_id = npc['behavior_id']
                behavior_name = npc['behavior_name']
                type_id = npc['type_id']
                type_name = evetypes.GetName(type_id)
                cost = npc['cost']
                tag_names = npc['npc_tag_names']
                tags = npc['npc_tags']
                weight = npc['weight']
                for n in xrange(quantity):
                    data_rows.append([index + 1,
                     type_name,
                     type_id,
                     behavior_name,
                     behavior_id,
                     cost,
                     tag_names,
                     tags,
                     weight])

        title = 'NPC Details CSV Filename'
        spawn_table_id = self.content_details['spawn_table_id']
        difficulty_tier = self.content_details['difficulty_tier']
        default_file_name = 'npc_details_table_%s_tier_%s.csv' % (spawn_table_id, difficulty_tier)
        self.save_csv_to_file(header, data_rows, title, default_file_name)

    def save_csv_to_file(self, header, data_rows, title, default_file_name):
        if self.content_details is None:
            self.set_feedback('Unable to save content.  No content details found.')
            return
        default_path = os.path.join(blue.sysinfo.GetUserDocumentsDirectory(), 'EVE', 'insider', 'abyss', default_file_name)
        file_path = NamePopup(caption=title, label='Path and filename', setvalue=default_path, maxLength=256)
        if not file_path:
            self.set_feedback('Unable get a valid file name to save content.')
            return
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(file_path, 'wb') as content_file:
            self.dump_to_csv(content_file, header, data_rows)
        self.set_feedback('Saving content to file: %s' % file_path)

    def dump_to_csv(self, csv_file, header, data_rows):
        writer = csv.writer(csv_file)
        writer.writerow(header)
        for row in data_rows:
            writer.writerow(row)
