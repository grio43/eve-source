#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\actions\other.py
from .base import Action

class Screenshot(Action):
    atom_id = 314

    def __init__(self, directory = None, file_name = None, **kwargs):
        super(Screenshot, self).__init__(**kwargs)
        self.directory = self.get_atom_parameter_value('directory', directory)
        self.file_name = self.get_atom_parameter_value('file_name', file_name)

    def start(self, **kwargs):
        super(Screenshot, self).start(**kwargs)
        from carbonui.uicore import uicore
        uicore.commandHandler.PrintScreen(self.directory, self.file_name)
