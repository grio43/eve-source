#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\actions\commands.py
from uihider import CommandBlockerService, CommandSet
from .base import Action

class CommandBlockerAction(Action):

    def __init__(self, **kwargs):
        super(CommandBlockerAction, self).__init__(**kwargs)
        self.block_token = None

    @property
    def command_blocker(self):
        return CommandBlockerService.instance()

    def stop(self):
        super(CommandBlockerAction, self).stop()
        if self.block_token is not None:
            self.block_token.dispose()
            self.block_token = None


class DisableCommand(CommandBlockerAction):
    atom_id = 271

    def __init__(self, command, **kwargs):
        super(DisableCommand, self).__init__(**kwargs)
        self.command = command

    @classmethod
    def get_subtitle(cls, command = None, **kwargs):
        if command is None:
            return '<color=orange>!! specify a command !!'
        else:
            return command

    def start(self, **kwargs):
        super(DisableCommand, self).start(**kwargs)
        self.block_token = self.command_blocker.block([self.command])


class EnableCommand(CommandBlockerAction):
    atom_id = 272

    def __init__(self, command, **kwargs):
        super(EnableCommand, self).__init__(**kwargs)
        self.command = command

    @classmethod
    def get_subtitle(cls, command = None, **kwargs):
        if command is None:
            return '<color=orange>!! specify a command !!'
        else:
            return command

    def start(self, **kwargs):
        super(EnableCommand, self).start(**kwargs)
        self.block_token = self.command_blocker.unblock([self.command])


class DisableCommandSet(CommandBlockerAction):
    atom_id = 265

    def __init__(self, command_set_id = None, **kwargs):
        super(DisableCommandSet, self).__init__(**kwargs)
        self.command_set_id = command_set_id

    @classmethod
    def get_subtitle(cls, command_set_id = None, **kwargs):
        return get_command_set_subtitle(command_set_id)

    def start(self, **kwargs):
        super(DisableCommandSet, self).start(**kwargs)
        if self.command_set_id is not None:
            command_set = CommandSet.from_fsd_id(self.command_set_id)
            self.block_token = self.command_blocker.block(command_set.commands)


class EnableCommandSet(CommandBlockerAction):
    atom_id = 266

    def __init__(self, command_set_id = None, **kwargs):
        super(EnableCommandSet, self).__init__(**kwargs)
        self.command_set_id = command_set_id

    @classmethod
    def get_subtitle(cls, command_set_id = None, **kwargs):
        return get_command_set_subtitle(command_set_id)

    def start(self, **kwargs):
        super(EnableCommandSet, self).start(**kwargs)
        if self.command_set_id is not None:
            command_set = CommandSet.from_fsd_id(self.command_set_id)
            self.block_token = self.command_blocker.unblock(command_set.commands)


def get_command_set_subtitle(command_set_id):
    if command_set_id is None:
        return '<color=orange>!! select a command set !!</color>'
    try:
        command_set = CommandSet.from_fsd_id(command_set_id)
        return u'{} ({})'.format(command_set.name, command_set_id)
    except (ImportError, KeyError):
        return '<color=orange>!! unknown command set !!</color>'
