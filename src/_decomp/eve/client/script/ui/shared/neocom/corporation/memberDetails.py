#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\memberDetails.py
from eve.client.script.ui.shared.neocom.corporation.corp_dlg_edit_member import EditMemberDialog

def OpenMemberDetails(charID, *args):
    wnd = EditMemberDialog.GetIfOpen()
    if wnd:
        if wnd.charID == charID:
            return wnd.Maximize()
        wnd.Close()
    EditMemberDialog.Open(charID=charID)
