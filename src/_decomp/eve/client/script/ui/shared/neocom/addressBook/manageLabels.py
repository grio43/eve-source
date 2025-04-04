#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\addressBook\manageLabels.py
import localization
from carbonui import uiconst
from eve.client.script.ui.control import eveLabel
from carbonui.button.group import ButtonGroup
from eve.client.script.ui.shared.neocom.corporation.corpPanelConst import CorpPanel
from eve.client.script.ui.shared.neocom.evemail import ManageLabelsBase
from eveexceptions import UserError
__author__ = 'aevar'

class ManageLabels(ManageLabelsBase):
    __guid__ = 'form.ManageLabels'

    def ApplyAttributes(self, attributes):
        ManageLabelsBase.ApplyAttributes(self, attributes)
        labelType = attributes.labelType
        self.storedSelection = []
        if labelType == 'contact':
            labelText = localization.GetByLabel('UI/PeopleAndPlaces/LabelsTextContacts')
        elif labelType == 'corpcontact':
            labelText = localization.GetByLabel('UI/PeopleAndPlaces/LabelsTextCorpContacts')
        else:
            labelText = localization.GetByLabel('UI/PeopleAndPlaces/LabelsTextAllianceContacts')
        self.labelType = labelType
        self.sr.textCont.state = uiconst.UI_DISABLED
        eveLabel.EveLabelMedium(text=labelText, parent=self.sr.textCont, padLeft=10, state=uiconst.UI_DISABLED, align=uiconst.TOTOP)
        ButtonGroup(btns=[[localization.GetByLabel('UI/Mail/AssignLabel'),
          self.AssignLabelFromBtn,
          None,
          81], [localization.GetByLabel('UI/Mail/LabelRemove'),
          self.RemoveLabelFromBtn,
          None,
          81]], parent=self.sr.bottom, idx=0, padTop=4)
        self.LoadScroll()

    def AssignLabelFromBtn(self, *args):
        self.ManageLabel(assign=1)

    def RemoveLabelFromBtn(self, *args):
        self.ManageLabel(assign=0)

    def ManageLabel(self, assign = 1):
        labelsChecked = self.FindLabelsChecked()
        numLabels = len(labelsChecked)
        scroll = None
        if numLabels < 1:
            raise UserError('CustomNotify', {'notify': localization.GetByLabel('UI/PeopleAndPlaces/NoLabelsSelected')})
        if self.labelType == 'contact':
            wnd = sm.GetService('addressbook').GetWnd()
            if wnd:
                scroll = wnd.FindChild('rightScroll')
        else:
            wnd = sm.GetService('corpui').GetWnd()
            if wnd:
                if self.labelType == 'corpcontact':
                    scroll = wnd.FindChild('corpcontactsform', 'rightScroll')
                elif self.labelType == 'alliancecontact':
                    scroll = wnd.FindChild(CorpPanel.ALLIANCES_CONTACTS, 'rightScroll')
        if not wnd:
            raise UserError('CustomNotify', {'notify': localization.GetByLabel('UI/PeopleAndPlaces/NoContactsSelected')})
        if scroll is None:
            selectedContacts = []
        else:
            selectedContacts = scroll.GetSelected()
        try:
            contactIDs = [ selIDs.charID for selIDs in selectedContacts ]
        except:
            raise UserError('CustomNotify', {'notify': localization.GetByLabel('UI/PeopleAndPlaces/NoContactsSelected')})

        sum = 0
        for labelID in labelsChecked:
            sum = sum + labelID

        numLabels = len(labelsChecked)
        numContacts = len(contactIDs)
        if numContacts > 0:
            if assign:
                text = localization.GetByLabel('UI/PeopleAndPlaces/LabelsAssigned', numLabels=numLabels, numContacts=numContacts)
            else:
                text = localization.GetByLabel('UI/PeopleAndPlaces/LabelsRemoved', numLabels=numLabels, numContacts=numContacts)
            eve.Message('CustomNotify', {'notify': text})
        else:
            raise UserError('CustomNotify', {'notify': localization.GetByLabel('UI/PeopleAndPlaces/NoContactsSelected')})
        if assign == 1:
            sm.StartService('addressbook').AssignLabelFromWnd(contactIDs, sum, displayNotify=0)
        else:
            sm.StartService('addressbook').RemoveLabelFromWnd(contactIDs, sum)
