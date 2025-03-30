#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\systemMenu\feature_preview\panel.py
import localization
import threadutils
from carbonui import TextAlign, TextColor, uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui import eveColor
from eve.client.script.ui.control import eveLabel, eveScroll
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.shared.systemMenu.feature_preview.card import FeaturePreviewCard
from eve.client.script.ui.shared.systemMenu.feature_preview.data import get_available_feature_previews

class FeaturePreviewsPanel(Container):
    _scroll = None

    def __init__(self, parent):
        self._experiment_cards = []
        super(FeaturePreviewsPanel, self).__init__(parent=parent, align=uiconst.TOALL)
        self._load()

    @threadutils.threaded
    def _load(self):
        available_previews = get_available_feature_previews()
        if not available_previews:
            self._show_empty_state()
        else:
            self._show_feature_previews(available_previews)

    def _show_empty_state(self):
        wrap = ContainerAutoSize(parent=self, align=uiconst.CENTER, width=360)
        eveLabel.EveCaptionLarge(parent=wrap, align=uiconst.TOTOP, text=localization.GetByLabel('UI/FeaturePreview/NoFeaturePreviewsTitle'), textAlign=TextAlign.CENTER)
        eveLabel.EveLabelLarge(parent=wrap, align=uiconst.TOTOP, text=localization.GetByLabel('UI/FeaturePreview/NoFeaturePreviewsBody'), textAlign=TextAlign.CENTER, color=TextColor.SECONDARY)

    def _show_feature_previews(self, feature_previews):
        self._scroll = eveScroll.Scroll(parent=self, align=uiconst.TOLEFT, width=320, hasUnderlay=False)
        self._scroll.OnSelectionChange = self._on_scroll_selection_change
        experiment_entries = []
        for experiment in feature_previews:
            experiment_entries.append(GetFromClass(ExperimentEntry, {'experiment': experiment}))
            self._experiment_cards.append(FeaturePreviewCard(parent=self, align=uiconst.TOALL, experiment=experiment))

        self._scroll.LoadContent(contentList=experiment_entries)
        self._scroll.SelectNode(self._scroll.GetNodes()[0])

    def _on_scroll_selection_change(self, nodes):
        if not nodes:
            return
        node = nodes[0]
        experiment_id = node.experiment.id
        self._show_card(experiment_id)

    def _show_card(self, experiment_id):
        selected_card = None
        for card in self._experiment_cards:
            if card.experiment.id == experiment_id:
                selected_card = card
            elif card.display:
                card.hide()

        if selected_card:
            selected_card.show()

    def select_experiment(self, experiment_id):
        for node in self._scroll.GetNodes():
            if node.experiment.id == experiment_id:
                self._scroll.SelectNode(node)
                return


class ExperimentEntry(Generic):

    def __init__(self, **kwargs):
        self._icon = None
        self._label = None
        self._trailing = None
        self._experiment = None
        super(ExperimentEntry, self).__init__(**kwargs)

    def Startup(self, *args):
        self._icon = Sprite(parent=ContainerAutoSize(parent=self, align=uiconst.TOLEFT, padding=(16, 8, 8, 8)), align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, width=18, height=18, texturePath='res:/UI/Texture/classes/insider/visibility_on_18.png')
        self._trailing = ContainerAutoSize(parent=self, align=uiconst.TORIGHT)
        label_clipper = Container(parent=self, align=uiconst.TOALL)
        self._label = eveLabel.EveLabelLarge(parent=label_clipper, align=uiconst.CENTERLEFT, autoFadeSides=16)

    def Load(self, node):
        self.sr.node = node
        self._experiment = node.experiment
        self._label.text = self._experiment.title
        self._update_icon()
        if self._experiment.is_new:
            eveLabel.EveLabelMedium(parent=ContainerAutoSize(parent=self._trailing, align=uiconst.CENTER, padding=(8, 0, 8, 0), bgColor=eveColor.CHERRY_RED[:3]), text=localization.GetByLabel('UI/FeaturePreview/NewTag'), padding=(8, 2, 8, 2), opacity=1.0)
        self._experiment.on_toggle.connect(self._update_icon)

    def GetHeight(self, node, width):
        return 48

    def _update_icon(self):
        if self._experiment.is_enabled:
            self._icon.texturePath = 'res:/UI/Texture/classes/insider/visibility_on_18.png'
            self._icon.SetRGB(*eveColor.LEAFY_GREEN[:3])
        else:
            self._icon.texturePath = 'res:/UI/Texture/classes/insider/visibility_off_18.png'
            self._icon.SetRGB(0.5, 0.5, 0.5)
