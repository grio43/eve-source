#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\dungeons\homefront_operations\job.py
from eve.client.script.ui.shared.agencyNew.contentGroups.contentGroupConst import contentGroupHomefrontSites
from jobboard.client.features.dungeons.job import DungeonJob

class HomefrontOperationJob(DungeonJob):
    CONTENT_GROUP_ID = contentGroupHomefrontSites
