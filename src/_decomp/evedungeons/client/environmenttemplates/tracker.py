#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evedungeons\client\environmenttemplates\tracker.py


class DungeonEnvironmentTemplate(object):

    def __init__(self, template_id, position, name):
        self.template_id = template_id
        self.position = position
        self.name = name

    def __eq__(self, other):
        if not type(other) == DungeonEnvironmentTemplate:
            return False
        return self.template_id == other.template_id and self.position == other.position and self.name == other.name

    def __repr__(self):
        return '<DungeonEnvironmentTemplate name:{} template_id:{} position:{}>'.format(self.name, self.template_id, self.position)

    def __hash__(self):
        return self.__repr__().__hash__()


class DungeonEnvironmentTemplateTracker(object):

    def __init__(self, data_loader):
        self.data_loader = data_loader
        self.room_position = None
        self.dungeon_environment_template_ids = []
        self.room_environment_template_ids = []
        self.system_environment_template_ids = []

    def get_active_dungeon_environment_templates(self):
        templates = []
        for template_id in self.dungeon_environment_template_ids:
            name = 'dungeon_template_{}'.format(template_id)
            dungeon_template = DungeonEnvironmentTemplate(template_id, self.room_position, name)
            templates.append(dungeon_template)

        for template_id in self.room_environment_template_ids:
            name = 'dungeon_room_template_{}'.format(template_id)
            room_template = DungeonEnvironmentTemplate(template_id, self.room_position, name)
            templates.append(room_template)

        for template_id in self.system_environment_template_ids:
            name = 'dungeon_system_template_{}'.format(template_id)
            system_template = DungeonEnvironmentTemplate(template_id, (0.0, 0.0, 0.0), name)
            templates.append(system_template)

        return templates

    def _get_room_level_templates(self, dungeon_id, room_id):
        return self.data_loader.get_room_templates(dungeon_id, room_id)

    def _get_dungeon_level_templates(self, dungeon_id):
        return self.data_loader.get_dungeon_wide_templates(dungeon_id)

    def _get_system_level_templates(self, dungeon_id):
        return self.data_loader.get_system_wide_templates(dungeon_id)

    def change_dungeon_room(self, dungeon_id, room_id, room_position):
        self.room_position = room_position
        self.room_environment_template_ids = self._get_room_level_templates(dungeon_id, room_id)
        self.dungeon_environment_template_ids = self._get_dungeon_level_templates(dungeon_id)
        self.system_environment_template_ids = self._get_system_level_templates(dungeon_id)
