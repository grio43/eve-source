#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Components\ButtonGroups\ToggleButtonGroupCircular.py
import carbonui.const as uiconst
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.devtools.script.uiControlCatalog.sample import Sample

class Sample1(Sample):
    name = 'Basic'

    def sample_code(self, parent):
        from eve.client.script.ui.control.toggleButtonGroupCircular import ToggleButtonGroupCircular
        ID1 = 1
        ID2 = 2
        ID3 = 3

        def OnMyToggleBtnGroup(btnID, oldBtnID):
            ShowQuickMessage(btnID)

        myToggleBtnGroup = ToggleButtonGroupCircular(name='myToggleBtnGroup', parent=parent, align=uiconst.TOPLEFT, callback=OnMyToggleBtnGroup)
        myToggleBtnGroup.AddButton(ID1, label='1')
        myToggleBtnGroup.AddButton(ID2, label='2')
        myToggleBtnGroup.AddButton(ID3, label='3')
        myToggleBtnGroup.SelectByID(ID1)


class Sample2(Sample):
    name = 'Icons'

    def sample_code(self, parent):
        from eve.client.script.ui.control.toggleButtonGroupCircular import ToggleButtonGroupCircular
        ID1 = 1
        ID2 = 2
        ID3 = 3
        ID4 = 4

        def OnMyToggleBtnGroup(btnID, oldBtnID):
            if btnID == ID1:
                ShowQuickMessage('Amarr')
            elif btnID == ID2:
                ShowQuickMessage('Gallente')
            elif btnID == ID3:
                ShowQuickMessage('Minmatar')
            elif btnID == ID4:
                ShowQuickMessage('Caldari')

        myToggleBtnGroup = ToggleButtonGroupCircular(name='myToggleBtnGroup', parent=parent, align=uiconst.TOPLEFT, callback=OnMyToggleBtnGroup)
        myToggleBtnGroup.AddButton(btnID=ID1, iconPath='res:/UI/Texture/Classes/SkillPlan/factionButtons/iconAmarr.png')
        myToggleBtnGroup.AddButton(btnID=ID2, iconPath='res:/UI/Texture/Classes/SkillPlan/factionButtons/iconGallente.png')
        myToggleBtnGroup.AddButton(btnID=ID3, iconPath='res:/UI/Texture/Classes/SkillPlan/factionButtons/iconMinmatar.png')
        myToggleBtnGroup.AddButton(btnID=ID4, iconPath='res:/UI/Texture/Classes/SkillPlan/factionButtons/iconCaldari.png')
        myToggleBtnGroup.SelectByID(ID1)
