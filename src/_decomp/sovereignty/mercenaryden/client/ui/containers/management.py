#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\mercenaryden\client\ui\containers\management.py
from carbonui import Align
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.toggleButtonGroup import ToggleButtonGroup
from localization import GetByLabel
from sovereignty.mercenaryden.client.ui.containers.activities import ActivitiesContainer
from sovereignty.mercenaryden.client.ui.containers.evolution import EvolutionContainer

class ManagementContainer(ContainerAutoSize):
    PADDING_EVOLUTION_TO_ACTIVITIES = 24

    def __init__(self, controller, *args, **kwargs):
        self._controller = controller
        super(ManagementContainer, self).__init__(*args, **kwargs)
        self._construct_content()

    def _construct_content(self):
        self._construct_evolution()
        self._construct_activities()

    def _construct_evolution(self):
        self._evolution = EvolutionContainer(name='evolution_container', parent=self, align=Align.TOTOP, controller=self._controller)

    def _construct_activities(self):
        self._activities = ActivitiesContainer(name='activities_container', parent=self, align=Align.TOTOP, controller=self._controller, padTop=self.PADDING_EVOLUTION_TO_ACTIVITIES)

    def load_controller(self, controller):
        self._controller = controller
        self._evolution.load_controller(self._controller)
        self._activities.load_controller(self._controller)
        self.SetSizeAutomatically()

    def set_width(self, width):
        self.width = width
        self._evolution.set_width(width)
        self._activities.set_width(width)
        self.SetSizeAutomatically()


class ManagementTab(object):
    TAB_EVOLUTION = 'tab_evolution'
    TAB_ACTIVITIES = 'tab_activities'


class ManagementContainerWithTabs(ManagementContainer):
    LABEL_PATH_TAB_EVOLUTION = 'UI/Sovereignty/MercenaryDen/MyMercenaryDensWindow/TabEvolution'
    LABEL_PATH_TAB_ACTIVITIES = 'UI/Sovereignty/MercenaryDen/MyMercenaryDensWindow/TabActivities'
    PADDING_BOTTOM_TAB_GROUP = 16
    PADDING_EVOLUTION_TO_ACTIVITIES = 0

    def _construct_content(self):
        self._construct_tab_group()
        self._construct_evolution()
        self._construct_activities()
        self._construct_tabs()

    def _construct_tab_group(self):
        self._tab_group = ToggleButtonGroup(name='tab_group', parent=self, groupID='tab_group_management', align=Align.TOTOP, callback=self._on_tab_selected, padBottom=self.PADDING_BOTTOM_TAB_GROUP)

    def _construct_tabs(self):
        self._tab_group.AddButton(label=GetByLabel(self.LABEL_PATH_TAB_EVOLUTION), panel=self._evolution, btnID=ManagementTab.TAB_EVOLUTION)
        self._tab_group.AddButton(label=GetByLabel(self.LABEL_PATH_TAB_ACTIVITIES), panel=self._activities, btnID=ManagementTab.TAB_ACTIVITIES)

    def _get_last_selected_tab(self):
        return settings.char.ui.Get('MercenaryDen_MyMercenaryDensWindow_LastSelectedTab', ManagementTab.TAB_EVOLUTION)

    def _set_last_selected_tab(self, tab_id):
        settings.char.ui.Set('MercenaryDen_MyMercenaryDensWindow_LastSelectedTab', tab_id)

    def _on_tab_selected(self, tab_id, *args):
        if tab_id == ManagementTab.TAB_EVOLUTION:
            self._evolution.display = True
            self._activities.display = False
        elif tab_id == ManagementTab.TAB_ACTIVITIES:
            self._evolution.display = False
            self._activities.display = True
        self._set_last_selected_tab(tab_id)

    def load_controller(self, controller):
        super(ManagementContainerWithTabs, self).load_controller(controller)
        last_selected_tab = self._get_last_selected_tab()
        self._tab_group.SetSelectedByID(last_selected_tab, animate=False)
        self._on_tab_selected(last_selected_tab)
