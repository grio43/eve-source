#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentGroups\fleetupContentGroup.py
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentGroups.baseContentGroup import BaseContentGroup
from eve.client.script.ui.shared.agencyNew.ui.contentPages.contentPageFleetUp import ContentPageFleetUp
from eve.client.script.ui.shared.agencyNew.ui.contentPages.contentPageFleetUpRegister import ContentPageFleetUpRegister

class FleetupRegisterContentGroup(BaseContentGroup):
    contentGroupID = contentGroupConst.contentGroupFleetUpRegister

    @staticmethod
    def IsContentAvailable():
        return True

    @staticmethod
    def CanLoadAsLastActive():
        return False

    @staticmethod
    def CanLoadFromHistory():
        return False

    @staticmethod
    def GetContentPageClass():
        return ContentPageFleetUpRegister


class FleetupContentGroup(BaseContentGroup):
    contentGroupID = contentGroupConst.contentGroupFleetUp
    childrenGroups = [(contentGroupConst.contentGroupFleetUpRegister, FleetupRegisterContentGroup)]

    @staticmethod
    def IsContentAvailable():
        return True

    @staticmethod
    def GetContentPageClass():
        return ContentPageFleetUp

    @staticmethod
    def IsTabGroup():
        return True
