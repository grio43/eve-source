#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uihighlighting\ui\uipointereffect.py
from carbon.common.script.util.timerstuff import AutoTimer
import logging
from carbonui.uicore import uicore
logger = logging.getLogger(__name__)
BLINK_GAUGE_FLASH_MILLISECONDS = 6500

class UiPointerEffect(object):

    def Start(self):
        raise NotImplementedError

    def Stop(self):
        raise NotImplementedError


class BlinkGauge(UiPointerEffect):

    def __init__(self, gaugeName):
        self.timer = None
        self.gaugeName = gaugeName

    def _GetGaugeIfExists(self):
        if hasattr(uicore.layer.shipui, 'hpGauges'):
            return getattr(uicore.layer.shipui.hpGauges, self.gaugeName, None)

    def _FlashIn(self):
        gauge = self._GetGaugeIfExists()
        if gauge:
            gauge.HighlightGauge()

    def _FlashOut(self):
        gauge = self._GetGaugeIfExists()
        if gauge:
            gauge.ClearHighlight()

    def Start(self):
        self._FlashIn()
        self.timer = AutoTimer(BLINK_GAUGE_FLASH_MILLISECONDS, self._FlashIn)

    def Stop(self):
        self._FlashOut()
        self.timer = None


EFFECT_STRING_TO_EFFECT = {'blinkShieldGauge': BlinkGauge('shieldGauge'),
 'blinkArmorGauge': BlinkGauge('armorGauge'),
 'blinkStructureGauge': BlinkGauge('structureGauge')}

class EffectManager(object):

    def __init__(self):
        self.active_effects_by_element = {}

    def StartEffect(self, element, effect_str):
        effect = EFFECT_STRING_TO_EFFECT.get(effect_str, None)
        if effect is None:
            logger.warn("Could not find ui pointer effect '%s'" % str(effect_str))
            return
        if element in self.active_effects_by_element:
            self.active_effects_by_element[element].append(effect)
        else:
            self.active_effects_by_element[element] = [effect]
        effect.Start()

    def StopEffectsForElement(self, element):
        for effect in self.active_effects_by_element.get(element, []):
            effect.Stop()

        self.active_effects_by_element.pop(element, None)

    def StopAllEffects(self):
        for effect_list in self.active_effects_by_element.values():
            for effect in effect_list:
                effect.Stop()

        self.active_effects_by_element.clear()


__manager = EffectManager()
start_effect = __manager.StartEffect
stop_effects_for_element = __manager.StopEffectsForElement
clear_all_effects = __manager.StopAllEffects

def start_effects(element, effects):
    for effect_str in effects:
        start_effect(element, effect_str)
