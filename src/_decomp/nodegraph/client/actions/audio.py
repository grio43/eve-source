#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\actions\audio.py
from fsdBuiltData.client.musicTriggers import GetMusicTrigger
from .base import Action

class MusicTrigger(Action):
    atom_id = 2

    def __init__(self, music_trigger_id = None, **kwargs):
        super(MusicTrigger, self).__init__(**kwargs)
        self.music_trigger_id = music_trigger_id

    def start(self, **kwargs):
        super(MusicTrigger, self).start(**kwargs)
        if self.music_trigger_id:
            sm.GetService('dynamicMusic').ScheduleMusicTriggerByID(self.music_trigger_id)

    @classmethod
    def get_subtitle(cls, music_trigger_id = None, **kwargs):
        if not music_trigger_id:
            return
        music_trigger = GetMusicTrigger(int(music_trigger_id))
        if music_trigger:
            return u'{} ({})'.format(music_trigger.trigger, music_trigger_id)


class StopMusic(Action):
    atom_id = 440

    def start(self, **kwargs):
        super(StopMusic, self).start(**kwargs)
        sm.GetService('dynamicMusic').StopMusic()


class PlaySound(Action):
    atom_id = 3

    def __init__(self, audio_name = '', **kwargs):
        super(PlaySound, self).__init__(**kwargs)
        self.audio_name = audio_name

    def start(self, **kwargs):
        super(PlaySound, self).start(**kwargs)
        sm.GetService('audio').SendUIEvent(self.audio_name)

    @classmethod
    def get_subtitle(cls, audio_name = '', **kwargs):
        return audio_name


class PlaySoundOnItem(Action):
    atom_id = 432

    def __init__(self, item_id = None, sound_id = None, **kwargs):
        super(PlaySoundOnItem, self).__init__(**kwargs)
        self.item_id = item_id
        self.sound_id = sound_id

    def start(self, **kwargs):
        super(PlaySoundOnItem, self).start(**kwargs)
        if not self.item_id or not self.sound_id:
            return
        audio_emitter_id = sm.GetService('audio').PlaySoundOnItem(self.sound_id, self.item_id)
        if audio_emitter_id:
            return {'audio_emitter_id': audio_emitter_id}

    @classmethod
    def get_subtitle(cls, sound_id = None, **kwargs):
        from fsdBuiltData.common.soundIDs import GetSoundEventName
        return GetSoundEventName(sound_id, default='missing sound_id')


class StopSoundOnItem(Action):
    atom_id = 433

    def __init__(self, item_id = None, sound_id = None, **kwargs):
        super(StopSoundOnItem, self).__init__(**kwargs)
        self.item_id = item_id
        self.sound_id = sound_id

    def start(self, **kwargs):
        super(StopSoundOnItem, self).start(**kwargs)
        if not self.item_id or not self.sound_id:
            return
        sm.GetService('audio').StopSoundOnItem(self.sound_id, self.item_id)

    @classmethod
    def get_subtitle(cls, sound_id = None, **kwargs):
        from fsdBuiltData.common.soundIDs import GetSoundEventName
        return GetSoundEventName(sound_id, default='missing sound_id')


class SetGameParameterOnAudioEmitter(Action):
    atom_id = 434

    def __init__(self, audio_emitter_id = None, key = None, value = None, **kwargs):
        super(SetGameParameterOnAudioEmitter, self).__init__(**kwargs)
        self.audio_emitter_id = audio_emitter_id
        self.key = key
        self.value = self.get_atom_parameter_value('value', value)

    def start(self, **kwargs):
        super(SetGameParameterOnAudioEmitter, self).start(**kwargs)
        if not self.audio_emitter_id or not self.key:
            return
        sm.GetService('audio').SetGameParameterOnAudioEmitter(self.audio_emitter_id, self.key, self.value)

    @classmethod
    def get_subtitle(cls, key = None, value = None, **kwargs):
        return '{}={}'.format(key, cls.get_atom_parameter_value('value', value))
