#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uihighlighting\uihighlightaudio.py
from carbon.common.script.util.timerstuff import AutoTimer
SOUND_SEPARATION_MS = 1000
HIGHLIGHT_APPEARED_SOUND = 'npe_neocom_highlight_play'

class _HighlightAudioManager(object):
    _audio_separation_thread = None

    def play_highlight_appeared_sound(self):
        if self._audio_separation_thread:
            return
        sm.GetService('audio').SendUIEvent(HIGHLIGHT_APPEARED_SOUND)
        self._audio_separation_thread = AutoTimer(SOUND_SEPARATION_MS, self._on_audio_separation_terminated)

    def _on_audio_separation_terminated(self):
        self._audio_separation_thread = None


manager = _HighlightAudioManager()
