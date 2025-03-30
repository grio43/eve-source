#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\events\dungeon.py
from .base import Event

class DungeonChanged(Event):
    atom_id = 145
    __notifyevents__ = ['OnDungeonEntered', 'OnDungeonExited']

    def OnDungeonEntered(self, dungeon_id, instance_id):
        self.invoke(dungeon_id=dungeon_id)

    def OnDungeonExited(self, dungeon_id, instance_id):
        self.invoke(dungeon_id=dungeon_id)


class DungeonEntered(Event):
    atom_id = 62
    __notifyevents__ = ['OnDungeonEntered']

    def OnDungeonEntered(self, dungeon_id, instance_id):
        self.invoke(dungeon_id=dungeon_id)


class DungeonExited(Event):
    atom_id = 144
    __notifyevents__ = ['OnDungeonExited']

    def OnDungeonExited(self, dungeon_id, instance_id):
        self.invoke(dungeon_id=dungeon_id)
