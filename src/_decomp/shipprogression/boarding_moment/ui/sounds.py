#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipprogression\boarding_moment\ui\sounds.py
from carbon.client.script.environment.AudioUtil import PlaySound
CINEMATIC_SHIP_INTRO_TEXT_1 = 'cinematic_ship_intro_text_1'
CINEMATIC_SHIP_INTRO_TEXT_2 = 'cinematic_ship_intro_text_2'
typing_sound_service = None

def get_typing_sound_service():
    global typing_sound_service
    if not typing_sound_service:
        typing_sound_service = TypingSoundService()
    return typing_sound_service


class TypingSoundService(object):
    SOUNDS = {CINEMATIC_SHIP_INTRO_TEXT_1: ('cinematic_ship_intro_text_1_play', 'cinematic_ship_intro_text_1_stop'),
     CINEMATIC_SHIP_INTRO_TEXT_2: ('cinematic_ship_intro_text_2_play', 'cinematic_ship_intro_text_2_stop')}

    def __init__(self):
        self._stopped = False
        self.active_sounds_by_id = {}

    def initialize(self):
        self._stopped = False
        self.active_sounds_by_id = {}

    def play_sound(self, soundID):
        if self._stopped:
            return
        if soundID not in self.SOUNDS:
            return
        if soundID not in self.active_sounds_by_id:
            self.active_sounds_by_id[soundID] = 0
        if self.active_sounds_by_id[soundID] == 0:
            self._play(soundID)
        self.active_sounds_by_id[soundID] += 1

    def stop_sound(self, soundID):
        if soundID not in self.SOUNDS:
            return
        if soundID not in self.active_sounds_by_id:
            return
        if self.active_sounds_by_id[soundID] == 0:
            return
        self.active_sounds_by_id[soundID] -= 1
        if self.active_sounds_by_id[soundID] == 0:
            self._stop(soundID)

    def _play(self, soundID):
        PlaySound(self.SOUNDS[soundID][0])

    def _stop(self, soundID):
        PlaySound(self.SOUNDS[soundID][1])

    def force_stop_all(self):
        self._stopped = True
        for soundID in self.SOUNDS.iterkeys():
            self._stop(soundID)

        self.active_sounds_by_id = {}
