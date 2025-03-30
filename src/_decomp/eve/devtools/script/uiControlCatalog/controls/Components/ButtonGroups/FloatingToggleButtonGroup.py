#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Components\ButtonGroups\FloatingToggleButtonGroup.py
import carbonui.const as uiconst
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.devtools.script.uiControlCatalog.sample import Sample

class Sample1(Sample):
    name = 'Basic'

    def sample_code(self, parent):
        from eve.client.script.ui.control.floatingToggleButtonGroup import FloatingToggleButtonGroup
        ID1 = 1
        ID2 = 2
        ID3 = 3

        def OnMyToggleBtnGroup(btnID, oldBtnID):
            if btnID == ID1:
                ShowQuickMessage('Button 1 selected')
            elif btnID == ID2:
                ShowQuickMessage('Button 2 selected')
            elif btnID == ID3:
                ShowQuickMessage('Button 3 selected')

        myToggleBtnGroup = FloatingToggleButtonGroup(name='myToggleBtnGroup', parent=parent, align=uiconst.TOPLEFT, width=400, callback=OnMyToggleBtnGroup)
        myToggleBtnGroup.AddButton(ID1, 'Button 1')
        myToggleBtnGroup.AddButton(ID2, 'Button 2')
        myToggleBtnGroup.AddButton(ID3, 'Button 3')
