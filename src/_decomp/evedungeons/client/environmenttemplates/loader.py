#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evedungeons\client\environmenttemplates\loader.py
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import dungeonEnvironmentTemplatesLoader
except ImportError:
    dungeonEnvironmentTemplatesLoader = None

class DungeonEnvironmentTemplateLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticData/dungeonEnvironmentTemplates.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/dungeonEnvironmentTemplates.fsdbinary'
    __loader__ = dungeonEnvironmentTemplatesLoader


class BaseDungeonEnvironmentTemplateLoader(object):

    def get_system_wide_templates(self, dungeon_id):
        raise NotImplemented()

    def get_dungeon_wide_templates(self, dungeon_id):
        raise NotImplemented()

    def get_room_templates(self, dungeon_id, room_id):
        raise NotImplemented()


class DungeonEnvironmentTemplateData(BaseDungeonEnvironmentTemplateLoader):

    def __init__(self):
        self.__loader = DungeonEnvironmentTemplateLoader()

    def get_system_wide_templates(self, dungeon_id):
        data = self.__loader.GetData().get(dungeon_id, None)
        if data is not None:
            return data.systemWideTemplates
        return []

    def get_dungeon_wide_templates(self, dungeon_id):
        data = self.__loader.GetData().get(dungeon_id, None)
        if data is not None:
            return data.dungeonWideTemplates
        return []

    def get_room_templates(self, dungeon_id, room_id):
        data = self.__loader.GetData().get(dungeon_id, None)
        if data is not None:
            return data.roomTemplates.get(room_id, [])
        return []


class FakeDataLoader(BaseDungeonEnvironmentTemplateLoader):

    def __init__(self):
        self._room_templates = {}
        self._dungeon_wide_templates = {}
        self._system_wide_templates = {}

    def add_room_template(self, dungeon_id, room_id, template_id):
        if (dungeon_id, room_id) in self._room_templates:
            self._room_templates[dungeon_id, room_id].append(template_id)
        else:
            self._room_templates[dungeon_id, room_id] = [template_id]

    def get_room_templates(self, dungeon_id, room_id):
        return self._room_templates.get((dungeon_id, room_id), [])

    def add_dungeon_wide_template(self, dungeon_id, template_id):
        if dungeon_id in self._dungeon_wide_templates:
            self._dungeon_wide_templates[dungeon_id].append(template_id)
        else:
            self._dungeon_wide_templates[dungeon_id] = [template_id]

    def get_dungeon_wide_templates(self, dungeon_id):
        return self._dungeon_wide_templates.get(dungeon_id, [])

    def add_system_wide_template(self, dungeon_id, template_id):
        if dungeon_id in self._system_wide_templates:
            self._system_wide_templates[dungeon_id].append(template_id)
        else:
            self._system_wide_templates[dungeon_id] = [template_id]

    def get_system_wide_templates(self, dungeon_id):
        return self._system_wide_templates.get(dungeon_id, [])
