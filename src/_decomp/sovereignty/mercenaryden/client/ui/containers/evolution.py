#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\mercenaryden\client\ui\containers\evolution.py
from carbonui import Align
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from sovereignty.mercenaryden.client.ui.containers.evolution_progression import DevelopmentProgressionContainer, AnarchyProgressionContainer, SIZE_BIG_CIRCLE, SIZE_SMALL_CIRCLE
from sovereignty.mercenaryden.client.ui.containers.evolution_title import DevelopmentTitleContainer, AnarchyTitleContainer
from sovereignty.mercenaryden.client.ui.containers.evolution_value import DevelopmentValueContainer, AnarchyValueContainer
from sovereignty.mercenaryden.client.ui.ui_signals import on_evolution_data_changed, on_mercenary_den_data_changed

class EvolutionContainer(ContainerAutoSize):
    PADDING_V_BETWEEN_DEVELOPMENT_AND_ANARCHY = 24
    PADDING_H_BETWEEN_TEXTS_AND_PROGRESSION = 16
    PADDING_V_BETWEEN_TITLE_AND_DETAILS = 1

    def __init__(self, controller, *args, **kwargs):
        self._controller = controller
        super(EvolutionContainer, self).__init__(*args, **kwargs)
        self._construct_content()
        self._connect_signals()

    def __del__(self):
        self._disconnect_signals()

    def _connect_signals(self):
        on_evolution_data_changed.connect(self._on_evolution_simulation_changed)
        on_mercenary_den_data_changed.connect(self._on_mercenary_den_data_changed)

    def _disconnect_signals(self):
        on_evolution_data_changed.disconnect(self._on_evolution_simulation_changed)
        on_mercenary_den_data_changed.disconnect(self._on_mercenary_den_data_changed)

    def _construct_content(self):
        self._construct_development()
        self._construct_anarchy()

    def _construct_development(self):
        margin_to_allow_hover_size = (SIZE_BIG_CIRCLE - SIZE_SMALL_CIRCLE) / 2
        self._development_title = DevelopmentTitleContainer(name='development_title', parent=self, align=Align.TOTOP)
        self._development_details = ContainerAutoSize(name='development_details', parent=self, align=Align.TOTOP, alignMode=Align.TOTOP, padTop=self.PADDING_V_BETWEEN_TITLE_AND_DETAILS, minHeight=SIZE_BIG_CIRCLE - margin_to_allow_hover_size)
        self._development_progression = DevelopmentProgressionContainer(name='development_progression', parent=self._development_details, align=Align.TORIGHT, top=-margin_to_allow_hover_size)
        self._development_value = DevelopmentValueContainer(name='development_value', parent=self._development_details, align=Align.TOTOP, padRight=self.PADDING_H_BETWEEN_TEXTS_AND_PROGRESSION)

    def _construct_anarchy(self):
        margin_to_allow_hover_size = (SIZE_BIG_CIRCLE - SIZE_SMALL_CIRCLE) / 2
        self._anarchy_title = AnarchyTitleContainer(name='anarchy_title', parent=self, align=Align.TOTOP, padTop=self.PADDING_V_BETWEEN_DEVELOPMENT_AND_ANARCHY - margin_to_allow_hover_size)
        self._anarchy_details = ContainerAutoSize(name='anarchy_details', parent=self, align=Align.TOTOP, alignMode=Align.TOTOP, padTop=self.PADDING_V_BETWEEN_TITLE_AND_DETAILS, minHeight=SIZE_BIG_CIRCLE - margin_to_allow_hover_size)
        self._anarchy_progression = AnarchyProgressionContainer(name='anarchy_progression', parent=self._anarchy_details, align=Align.TORIGHT, top=-margin_to_allow_hover_size)
        self._anarchy_value = AnarchyValueContainer(name='anarchy_value', parent=self._anarchy_details, align=Align.TOTOP, padRight=self.PADDING_H_BETWEEN_TEXTS_AND_PROGRESSION)

    def load_controller(self, controller):
        self._controller = controller
        self._load_development()
        self._load_anarchy()
        self.SetSizeAutomatically()

    def set_width(self, width):
        self.width = width
        self._development_details.SetSizeAutomatically()
        self._anarchy_details.SetSizeAutomatically()
        self.SetSizeAutomatically()

    def _load_development(self):
        self._load_containers(self._development_title, self._development_value, self._development_progression)

    def _load_anarchy(self):
        self._load_containers(self._anarchy_title, self._anarchy_value, self._anarchy_progression)

    def _load_containers(self, title_container, value_container, progression_container):
        title_container.load(self._controller)
        value_container.load(self._controller)
        progression_container.load(self._controller)

    def _reload_if_controller_is_accessible(self):
        if self._controller.is_accessible:
            self.load_controller(self._controller)

    def _on_evolution_simulation_changed(self):
        self._reload_if_controller_is_accessible()

    def _on_mercenary_den_data_changed(self):
        self._reload_if_controller_is_accessible()
