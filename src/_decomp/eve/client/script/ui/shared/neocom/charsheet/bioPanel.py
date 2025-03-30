#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\charsheet\bioPanel.py
import uthread
from carbon.common.script.util.commonutils import StripTags
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from globalConfig.getFunctions import IsContentComplianceControlSystemActive
from localization import GetByLabel
MAXBIOLENGTH = 2500

class BioPanel(Container):
    default_name = 'BioPanel'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.bioClient = None
        self.bioServer = None
        readOnly = IsContentComplianceControlSystemActive(sm.GetService('machoNet'))
        self.edit = EditPlainText(parent=self, maxLength=MAXBIOLENGTH, showattributepanel=1, padding=(0,
         const.defaultPadding,
         0,
         const.defaultPadding), readonly=readOnly)

    def LoadBioFromServer(self):
        if not self.bioClient:
            bio = sm.RemoteSvc('charMgr').GetCharacterDescription(session.charid)
            if bio is not None:
                self.bioClient = bio
            else:
                self.bioClient = ''
        if self.bioClient:
            self.bioServer = self.bioClient
        else:
            self.bioServer = ''

    def LoadPanel(self, *args):
        self.LoadBioFromServer()
        bio = self.bioServer or GetByLabel('UI/CharacterSheet/CharacterSheetWindow/BioEdit/HereYouCanTypeBio')
        self.edit.SetValue(bio)

    def AutoSaveBio(self):
        if not self.IsLoaded():
            return
        newbio = self.edit.GetValue()
        defaultBioString = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/BioEdit/HereYouCanTypeBio')
        newbio = newbio.replace(defaultBioString, '')
        if not len(StripTags(newbio)):
            newbio = ''
        self.bioClient = newbio
        if newbio.strip() != self.bioServer:
            uthread.new(self._AutoSaveBio, newbio)
            self.bioServer = newbio

    def _AutoSaveBio(self, newbio):
        try:
            sm.RemoteSvc('charMgr').SetCharacterDescription(newbio)
        except:
            self.ReloadBioFromServer()
            raise

    def ReloadBioFromServer(self):
        self.bioClient = None
        self.LoadBioFromServer()

    def UnloadPanel(self):
        self.AutoSaveBio()

    def Close(self):
        if self.display:
            self.AutoSaveBio()
        Container.Close(self)

    def IsLoaded(self):
        return self.bioServer is not None
