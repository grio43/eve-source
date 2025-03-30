#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\behaviortools\cluster_debugger.py
import logging
import math
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.primitives.sprite import Sprite
from carbonui.util.color import Color
from carbonui.control.button import Button
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from carbonui.control.window import Window
import uthread2
import carbonui.const as uiconst
from eve.common.script.net import eveMoniker
logger = logging.getLogger(__name__)
PHI = (1 + math.sqrt(5)) / 2.0
SATURATION = 1.0
BRIGHTNESS = 0.6
HUE_SEED = 0.2121

def get_cluster_color(index):
    c = Color()
    hue = HUE_SEED + index * PHI
    hue %= 1.0
    c.SetHSB(hue, SATURATION, BRIGHTNESS, 0.6)
    return c.GetRGBA()


def add_cluster_marker(bracket, cluster_index):
    Sprite(parent=bracket, name='cluster_marker', state=uiconst.UI_DISABLED, pos=(0, 0, 20, 20), texturePath='res:/UI/Texture/classes/Bracket/bracketBackground.png', align=uiconst.CENTER, color=get_cluster_color(cluster_index))


def color_clusters(clusters):
    for cluster_index, item_ids in enumerate(clusters):
        for item_id in item_ids:
            bracket = sm.GetService('bracket').GetBracket(item_id)
            if bracket:
                add_cluster_marker(bracket, cluster_index)


def clear_brackets():
    for bracket in sm.GetService('bracket').brackets.itervalues():
        for child in bracket.children:
            if child.name == 'cluster_marker':
                child.Close()


class ClusterDebugger(object):

    def __init__(self):
        self.is_updating = False
        self.spawn_pool_id = None

    def set_spawn_pool_id(self, spawn_pool_id):
        self.spawn_pool_id = spawn_pool_id

    def start_cluster_view(self):
        logger.debug('Cluster view debugger starting')
        if not self.is_updating:
            uthread2.start_tasklet(self._cluster_view_thread)

    def _cluster_view_thread(self):
        self.is_updating = True
        try:
            while self.is_updating:
                enemy_clusters = self.get_fleet_spawn_pool_enemy_clusters()
                enemy_clusters.sort(key=lambda c: (-len(c['item_ids']), -c['threat']))
                clusters = [ cluster['item_ids'] for cluster in enemy_clusters ]
                clear_brackets()
                color_clusters(clusters)
                uthread2.sleep_sim(10.0)

        except:
            logger.exception('Cluster view debugger failed')
        finally:
            self.stop_cluster_view()

    def stop_cluster_view(self):
        self.is_updating = False
        clear_brackets()
        logger.debug('Cluster view debugger stopped')

    def get_fleet_spawn_pool_enemy_clusters(self):
        entity_service = eveMoniker.GetEntityAccess()
        enemy_clusters = []
        if entity_service:
            enemy_clusters = entity_service.GetDebugSpawnPoolFleetEnemyClusters(self.spawn_pool_id)
        return enemy_clusters


cluster_debugger = ClusterDebugger()

class ClusterVisualizerWindow(Window):
    default_windowID = 'ClusterVisualizerWindow'
    default_width = 200
    default_height = 150
    default_minSize = (default_width, default_height)
    default_caption = 'Cluster Visualizer'
    default_fixedWidth = 200
    default_fixedHeight = 150

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.create_spawn_pool_id_selector()
        self.CreateButtons()

    def create_spawn_pool_id_selector(self):
        cont = Container(parent=self.content, height=SingleLineEditInteger.default_height, padding=0, align=uiconst.TOTOP)
        EveLabelSmall(parent=ContainerAutoSize(parent=cont, align=uiconst.TOLEFT), text='Spawn Point Pool Id', align=uiconst.CENTERLEFT, padding=0)
        self.spawn_pool_id_edit = SingleLineEditInteger(parent=cont, name='spawnPoolIdEdit', width=50, minValue=1, maxValue=999, align=uiconst.TOLEFT, padTop=0, setvalue='1', padLeft=4)

    def CreateButtons(self):
        button_cont = FlowContainer(name='ActionButtons', parent=self.content, centerContent=True, align=uiconst.TOBOTTOM, contentSpacing=(2, 1), state=uiconst.UI_PICKCHILDREN, padding=(0, 4, 0, 4))
        Button(parent=button_cont, label='Start', func=self.start_cluster_visualizer, align=uiconst.NOALIGN, padding=2)
        Button(parent=button_cont, label='Stop', func=self.stop_cluster_visualizer, align=uiconst.NOALIGN, padding=2)

    def start_cluster_visualizer(self, *args):
        spawn_pool_id = self.spawn_pool_id_edit.GetValue()
        self._start_cluster_visualizer(spawn_pool_id)

    def _start_cluster_visualizer(self, spawn_pool_id):
        self.spawn_pool_id = spawn_pool_id
        if cluster_debugger.spawn_pool_id != spawn_pool_id and cluster_debugger.is_updating:
            self._stop_cluster_visualizer(cluster_debugger.spawn_pool_id)
        cluster_debugger.set_spawn_pool_id(spawn_pool_id)
        cluster_debugger.start_cluster_view()

    def stop_cluster_visualizer(self, *args):
        spawn_pool_id = self.spawn_pool_id_edit.GetValue()
        self._stop_cluster_visualizer(spawn_pool_id)

    def _stop_cluster_visualizer(self, spawn_pool_id):
        if cluster_debugger.spawn_pool_id != spawn_pool_id:
            if cluster_debugger.spawn_pool_id is not None:
                self._stop_cluster_visualizer(cluster_debugger.spawn_pool_id)
        else:
            cluster_debugger.set_spawn_pool_id(spawn_pool_id)
            cluster_debugger.stop_cluster_view()
        cluster_debugger.stop_cluster_view()
