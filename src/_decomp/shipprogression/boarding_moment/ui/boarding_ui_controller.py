#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipprogression\boarding_moment\ui\boarding_ui_controller.py
import math
import time
import eveformat
import eveicon
import evetypes
import eveui
import uthread2
import random
import trinity
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import Align, TextBody, TextHeader, uiconst, TextHeadline, TextColor, TextAlign, TextCustom
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.primitives.sprite import Sprite, StreamingVideoSprite
from carbonui.text.const import FontSizePreset
from carbonui.text.styles import TextDisplay
from carbonui.uianimations import animations
from carbonui.uiconst import BlendMode
from carbonui.uicore import uicore
from eve.client.script.ui.control import eveIcon
from eve.common.script.util.eveFormat import FmtDist2
from localization import GetByMessageID, GetByLabel
from npcs.npccorporations import get_designer_description, get_npc_corporation_name
from raffles.client.widget.sweep_effect import SweepEffect
from shipgroup import get_ship_group_name
from shipprogression.boarding_moment import ShipShape
from shipprogression.boarding_moment import qa as boarding_moment_qa
from eve.common.lib.appConst import factionTriglavian, factionDeathless
from shipprogression.boarding_moment.ui.sounds import get_typing_sound_service, CINEMATIC_SHIP_INTRO_TEXT_2, CINEMATIC_SHIP_INTRO_TEXT_1
from shipprogression.boarding_moment.ui.steps.qa_overlay import _QAOverlay
DEFAULT_DURATION = 3
DEFAULT_DELAY = 0.2

class BoardingUIController(object):

    def __init__(self):
        super(BoardingUIController, self).__init__()
        get_typing_sound_service().initialize()
        self._active_element = None
        self._elements = []
        self._qa_overlay = None

    def SetContext(self, context):
        self._context = context

    def Close(self):
        for element in self._elements:
            if not element.destroyed:
                element.Close()

        if self._qa_overlay:
            self._qa_overlay.Close()
        get_typing_sound_service().force_stop_all()

    def TriggerStep(self, moment, animation_length):
        ui_moments = moment.get('ui_moments', None)
        if boarding_moment_qa.is_ui_overlay_enabled():
            self._update_qa_step(moment)
        if not ui_moments:
            return
        if ui_moments is None or len(ui_moments) == 0:
            return
        for ui_moment in ui_moments:
            step = ui_moment['step']
            ui_step = step(parent=self.get_layer())
            duration_offset = ui_moment.get('duration_offset', 0.0)
            ui_step.Start(self._context, duration=animation_length, delay=ui_moment.get('delay', DEFAULT_DELAY), duration_offset=duration_offset)
            self._elements.append(ui_step)

    def _update_qa_step(self, moment):
        if not self._qa_overlay:
            self._construct_qa_step()
        self._qa_overlay.update(moment)

    def _construct_qa_step(self):
        self._qa_overlay = _QAOverlay(parent=self.get_layer())
        self._qa_overlay.Start(self._context)

    def get_layer(self):
        return uicore.layer.alwaysvisible
