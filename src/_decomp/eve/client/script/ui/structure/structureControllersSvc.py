#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\structureControllersSvc.py
from carbon.common.script.sys.service import Service
from eve.client.script.ui.structure.structureBrowser.controllers.skyhookBrowserController import SkyhookBrowserController

class StructureControllerSvc(Service):
    __guid__ = 'svc.structureControllers'
    __servicename__ = 'structureControllers'
    __displayname__ = 'Structure Controllers Service'
    __notifyevents__ = ['OnSessionChanged']

    def Run(self, memStream = None):
        self.accessGroupController = None
        self.allStructuresProfileController = None
        self.structureBrowserController = None
        self.skyhookControllers = None

    def OnSessionChanged(self, isRemote, session, change):
        if 'corpid' not in change:
            return
        if self.accessGroupController:
            self.accessGroupController.InvalidateGetMyGroups()
        if self.allStructuresProfileController:
            self.allStructuresProfileController.Reset()

    def GetAccessGroupController(self):
        if self.accessGroupController is None:
            from eve.client.script.ui.structure.accessGroups.accessGroupsController import AccessGroupsController
            self.accessGroupController = AccessGroupsController()
        return self.accessGroupController

    def GetAllStructuresProfileController(self):
        if self.allStructuresProfileController is None:
            from eve.client.script.ui.structure.structureSettings.controllers.allProfilesController import AllStructureProfileController
            allStructuresProfileController = AllStructureProfileController()
            self.allStructuresProfileController = allStructuresProfileController
        return self.allStructuresProfileController

    def GetStructureBrowserController(self):
        if self.structureBrowserController is None:
            from eve.client.script.ui.structure.structureBrowser.controllers.structureBrowserController import StructureBrowserController
            structureBrowserController = StructureBrowserController()
            self.structureBrowserController = structureBrowserController
        return self.structureBrowserController

    def GetSkyhookBrowserController(self):
        if self.skyhookControllers is None:
            self.skyhookControllers = SkyhookBrowserController()
        return self.skyhookControllers

    def GetValidProfileIDs(self):
        allStructuresProfileController = self.GetAllStructuresProfileController()
        return allStructuresProfileController.GetProfileKeys()
