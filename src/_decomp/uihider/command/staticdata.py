#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uihider\command\staticdata.py
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import commandSetsLoader
except ImportError:
    commandSetsLoader = None

class CommandSetsData(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/commandSets.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/commandSets.fsdbinary'
    __loader__ = commandSetsLoader

    @classmethod
    def get_command_set_data(cls, command_set_id):
        return cls.GetData()[command_set_id]


class CommandSet(object):

    def __init__(self, name, commands):
        self.name = name
        self.commands = commands

    @staticmethod
    def from_fsd_id(command_set_id):
        seen = set()
        return CommandSet._from_fsd_id_recursive(command_set_id, seen)

    @staticmethod
    def _from_fsd_id_recursive(command_set_id, seen):
        data = CommandSetsData.get_command_set_data(command_set_id)
        commands = set(data.commands[:])
        if data.inherit:
            command_set_ids = set(data.inherit)
            for inherited_command_set_id in command_set_ids:
                if inherited_command_set_id not in seen:
                    seen.add(inherited_command_set_id)
                    inherited_command_set = CommandSet._from_fsd_id_recursive(inherited_command_set_id, seen)
                    commands.update(inherited_command_set.commands)

        return CommandSet(data.name, commands)

    def __repr__(self):
        if len(self.commands) <= 3:
            commands = ', '.join((repr(command) for command in self.commands))
        else:
            commands = ', '.join([', '.join((repr(command) for command in sorted(self.commands)[:3])), '...'])
        return 'CommandSet(name="{}", commands=[{}])'.format(self.name, commands)
