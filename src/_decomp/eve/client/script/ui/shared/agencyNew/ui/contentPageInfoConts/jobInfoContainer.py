#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPageInfoConts\jobInfoContainer.py
from carbonui import uiconst
from carbonui.button.group import ButtonGroup, ButtonSizeMode
from eve.client.script.ui.control.statefulButton import StatefulButton
from eve.client.script.ui.shared.agencyNew.ui.contentPageInfoConts.baseContentPageInfoCont import BaseContentPageInfoContainer
from jobboard.client.ui.track_button import TrackJobButton

class JobContentPageInfoContainer(BaseContentPageInfoContainer):

    def ApplyAttributes(self, attributes):
        self.trackJobButton = None
        super(JobContentPageInfoContainer, self).ApplyAttributes(attributes)

    def ConstructButtonContainer(self):
        self.buttonRowCont = ButtonGroup(name='buttonRowContainer', parent=self, align=uiconst.TOBOTTOM, button_size_mode=ButtonSizeMode.STRETCH, padTop=10)
        self.primaryActionButton = StatefulButton(parent=self.buttonRowCont)

    def OnScrollEntryClicked(self, clickedEntry):
        super(JobContentPageInfoContainer, self).OnScrollEntryClicked(clickedEntry)
        if self.trackJobButton:
            self.trackJobButton.Close()
        contentPiece = clickedEntry.contentPiece
        if hasattr(contentPiece, 'site'):
            siteDict = contentPiece.site.__dict__
            instanceID = siteDict.get('instanceID', siteDict.get('siteID'))
            if instanceID:
                job = self._GetJob(instanceID)
                if job:
                    self.trackJobButton = TrackJobButton(parent=self.buttonRowCont, job=job, idx=0)

    def _GetJob(self, instanceID):
        return None
