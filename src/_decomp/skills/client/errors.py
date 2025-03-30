#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\skills\client\errors.py


class SkillQueueOverwritten(RuntimeError):

    def __init__(self, character_id, cached_skill_queue):
        self.character_id = character_id
        self.cached_skill_queue = cached_skill_queue

    def __str__(self):
        return 'Starting a new skill queue transaction when an uncommitted skill queue transaction already existed. Overwriting the old uncommitted transaction with the new. \nCharacter ID: {character_id}, Cached Skill Queue: {cached_skill_queue}.'.format(character_id=self.character_id, cached_skill_queue=self.cached_skill_queue)
