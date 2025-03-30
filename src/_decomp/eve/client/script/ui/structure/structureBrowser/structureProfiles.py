#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\structureBrowser\structureProfiles.py
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.util.bunch import Bunch
from carbonui.util.sortUtil import SortListOfTuples
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelLarge
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.infoIcon import MoreInfoIcon
from eve.client.script.ui.control.themeColored import FillThemeColored
from eve.client.script.ui.structure import ChangeSignalConnect
from eve.client.script.ui.structure.accessGroups.addCont import AddCont
from eve.client.script.ui.structure.structureBrowser.browserUIConst import ALL_PROFILES
from eve.client.script.ui.structure.structureBrowser.nameAndDescriptionWnd import CreateProfileWnd
from eve.client.script.ui.structure.structureBrowser.entries.structureProfileEntry import StructureProfileEntry, StructureAllProfilesEntry
from eve.client.script.ui.structure.structureSettings.controllers.slimProfileController import SlimStructureProfileController, SlimStructureAllProfilesController
from localization import GetByLabel
import log
from utillib import KeyVal
import carbonui.const as uiconst

class StructureProfiles(Container):
    explanationLabelPath = 'UI/StructureProfiles/ProfileHint'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.allStructuresProfileController = attributes.allStructuresProfileController
        self.structureBrowserController = attributes.structureBrowserController
        self.ChangeSignalConnection(connect=True)
        self.AddHeader()
        self.addCont = AddProfileCont(parent=self, padTop=4, controller=self.allStructuresProfileController, padBottom=2, height=32)
        self.scroll = Scroll(name='structureProfileScroll', parent=self, padTop=2)
        self.scroll.multiSelect = False
        self.LoadProfileList()

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.allStructuresProfileController.on_profile_saved, self.OnProfileSaved), (self.structureBrowserController.on_profile_deleted, self.OnProfileDeleted), (self.structureBrowserController.on_default_profile_set, self.OnDefaultChanged)]
        ChangeSignalConnect(signalAndCallback, connect)

    def AddHeader(self):
        headerCont = Container(name='headerCont', parent=self, align=uiconst.TOTOP, height=32, clipChildren=True)
        FillThemeColored(parent=headerCont, padBottom=1, colorType=uiconst.COLORTYPE_UIHILIGHT)
        text = GetByLabel('UI/StructureProfiles/StructureProfiles')
        cont = ContainerAutoSize(name='textCont', parent=headerCont, align=uiconst.TOLEFT)
        EveLabelLarge(text=text, parent=cont, left=8, state=uiconst.UI_DISABLED, maxLines=1, align=uiconst.CENTERLEFT)
        cont = ContainerAutoSize(name='textCont', parent=headerCont, align=uiconst.TOLEFT, padLeft=6)
        MoreInfoIcon(parent=cont, hint=GetByLabel(self.explanationLabelPath), align=uiconst.CENTERLEFT)

    def LoadProfileList(self, force = False):
        selectedProfileID = self.structureBrowserController.GetSelectedProfileID()
        profileControllers = self.allStructuresProfileController.GetProfiles(force=force)
        scrollList = []
        for profileID, eachProfileController in profileControllers.iteritems():
            nodeData = Bunch(decoClass=StructureProfileEntry, profileController=eachProfileController, allStructuresProfileController=self.allStructuresProfileController, structureBrowserController=self.structureBrowserController, isSelected=profileID == selectedProfileID)
            sortValue = eachProfileController.GetProfileName().lower()
            scrollList.append((sortValue, nodeData))

        scrollList = SortListOfTuples(scrollList)
        anyProfileText = GetByLabel('UI/Structures/Browser/AnyProfile')
        anyProfileDesc = GetByLabel('UI/StructureProfiles/AnyProfileDesc')
        controllerForShowAll = SlimStructureAllProfilesController(ALL_PROFILES, profileData=KeyVal(name=anyProfileText, description=anyProfileDesc, isDefault=None))
        nodeData = Bunch(decoClass=StructureAllProfilesEntry, profileController=controllerForShowAll, allStructuresProfileController=self.allStructuresProfileController, structureBrowserController=self.structureBrowserController, isSelected=ALL_PROFILES == selectedProfileID)
        scrollList.insert(0, nodeData)
        self.scroll.Load(contentList=scrollList)

    def OnProfileSaved(self, profileID):
        self.LoadProfileList()

    def OnProfileDeleted(self, profileID, selectedProfileChanged):
        self.LoadProfileList()

    def OnDefaultChanged(self):
        self.LoadProfileList(force=True)

    def Close(self):
        try:
            self.ChangeSignalConnection(connect=False)
        except Exception as e:
            log.LogError('Failed at closing struture profile, e = ', e)
        finally:
            Container.Close(self)


class AddProfileCont(AddCont):
    default_name = 'AddGroupCont'
    tooltipPath = 'UI/Structures/AccessGroups/CreateNewGroup'

    def ApplyAttributes(self, attributes):
        AddCont.ApplyAttributes(self, attributes)
        self.createNewLabel.text = GetByLabel('UI/StructureProfiles/NewProfile')

    def OnAddEntry(self, *args):
        CreateProfileWnd.Open(controller=self.controller)
