#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\icon\character_portrait.py
from eveui.primitive.sprite import Sprite
from eveui.constants import State
from eveui.audio import Sound
from eveui import dragdata

class CharacterPortrait(Sprite):
    default_name = 'CharacterPortrait'
    default_state = State.normal

    def __init__(self, size = 64, character_id = None, **kwargs):
        kwargs.setdefault('height', size)
        kwargs.setdefault('width', size)
        super(CharacterPortrait, self).__init__(**kwargs)
        self._character_id = None
        self.character_id = character_id

    @property
    def character_id(self):
        return self._character_id

    @character_id.setter
    def character_id(self, character_id):
        if self._character_id == character_id:
            return
        self._character_id = character_id
        self._portrait_size = None
        self.texturePath = None
        self._update_portrait()
        self._update_hint()

    def _update_portrait(self):
        if self._character_id is None:
            self.texturePath = None
            return
        size = max(self.width, self.height)
        portrait_size = sm.GetService('photo').FindBestPortraitSize(size)
        if self._portrait_size == portrait_size:
            return
        self._portrait_size = portrait_size
        sm.GetService('photo').GetPortrait(charID=self._character_id, size=portrait_size, sprite=self)

    def _update_hint(self):
        if self.character_id is None:
            self.SetHint(None)
            return
        character_info = cfg.eveowners.Get(self._character_id)
        self.SetHint(character_info.name)

    def _OnSizeChange_NoBlock(self, *args):
        self._update_portrait()

    def OnClick(self, *args):
        if self._character_id:
            Sound.button_click.play()
            character_info = cfg.eveowners.Get(self._character_id)
            sm.GetService('info').ShowInfo(character_info.typeID, self._character_id)

    def OnMouseEnter(self, *args):
        Sound.button_hover.play()

    def GetDragData(self):
        if self._character_id:
            return [dragdata.Character(self._character_id)]

    def GetMenu(self):
        if self._character_id:
            return sm.GetService('menu').GetMenuForOwner(self._character_id)
