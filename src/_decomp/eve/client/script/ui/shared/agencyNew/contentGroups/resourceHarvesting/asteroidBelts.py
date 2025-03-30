#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentGroups\resourceHarvesting\asteroidBelts.py
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentGroups.baseContentGroup import BaseContentGroup
from eve.client.script.ui.shared.agencyNew.ui.contentPages.contentPageAsteroidBelts import ContentPageAsteroidBelts

class AsteroidBeltsContentGroup(BaseContentGroup):
    contentGroupID = contentGroupConst.contentGroupAsteroidBelts

    @staticmethod
    def GetContentPageClass():
        return ContentPageAsteroidBelts
