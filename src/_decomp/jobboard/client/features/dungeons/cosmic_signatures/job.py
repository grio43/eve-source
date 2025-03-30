#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\dungeons\cosmic_signatures\job.py
from eve.client.script.ui.shared.agencyNew.contentGroups.contentGroupConst import contentGroupSignatures
from jobboard.client.features.dungeons.job import DungeonJob

class CosmicSignatureJob(DungeonJob):
    CONTENT_GROUP_ID = contentGroupSignatures

    @property
    def is_available_in_browse(self):
        return False

    @property
    def is_linkable(self):
        return False
