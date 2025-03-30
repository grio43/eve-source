#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Components\ButtonGroups\ToggleButtonGroup.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.devtools.script.uiControlCatalog.sample import Sample

class Sample1(Sample):
    name = 'Basic'

    def sample_code(self, parent):
        from eve.client.script.ui.control.toggleButtonGroup import ToggleButtonGroup
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

        myToggleBtnGroup = ToggleButtonGroup(name='myToggleBtnGroup', parent=parent, align=uiconst.TOPLEFT, width=240, callback=OnMyToggleBtnGroup)
        myToggleBtnGroup.AddButton(ID1, 'Button 1')
        myToggleBtnGroup.AddButton(ID2, 'Button 2')
        myToggleBtnGroup.AddButton(ID3, 'Button 3')
        myToggleBtnGroup.SelectByID(ID1)


class Sample2(Sample):
    name = 'Icons and callback'

    def sample_code(self, parent):
        from eve.client.script.ui.control.toggleButtonGroup import ToggleButtonGroup
        from eve.client.script.ui.control.toggleButtonGroupButton import ToggleButtonGroupButtonIcon
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

        myToggleBtnGroup = ToggleButtonGroup(name='myToggleBtnGroup', parent=parent, align=uiconst.TOPLEFT, width=240, callback=OnMyToggleBtnGroup, height=50, btnClass=ToggleButtonGroupButtonIcon)
        myToggleBtnGroup.AddButton(ID1, iconPath='res:/UI/Texture/Icons/53_64_12.png', iconSize=40, hint='Cow')
        myToggleBtnGroup.AddButton(ID2, iconPath='res:/UI/Texture/Icons/53_64_13.png', iconSize=40, hint='Naked corpse')
        myToggleBtnGroup.AddButton(ID3, iconPath='res:/UI/Texture/Icons/56_64_10.png', iconSize=40, hint='Doll')
        myToggleBtnGroup.SelectByID(ID1)


class Sample3(Sample):
    name = 'Using panels'

    def sample_code(self, parent):
        from eve.client.script.ui.control.toggleButtonGroup import ToggleButtonGroup
        ID1 = 1
        ID2 = 2
        ID3 = 3
        mainCont = Container(name='mainCont', parent=parent, align=uiconst.TOPLEFT, width=250, height=120)
        myToggleBtnGroup = ToggleButtonGroup(name='myToggleBtnGroup', parent=mainCont, align=uiconst.TOTOP)
        panelCont = Container(name='panelCont', parent=mainCont, padTop=4)
        panel1 = Container(name='panel1', parent=panelCont, bgColor=eveColor.MATTE_BLACK)
        panel2 = Container(name='panel2', parent=panelCont, bgColor=eveColor.SMOKE_BLUE)
        panel3 = Container(name='panel3', parent=panelCont, bgColor=eveColor.COPPER_OXIDE_GREEN)
        myToggleBtnGroup.AddButton(ID1, 'I', panel1)
        myToggleBtnGroup.AddButton(ID2, 'II', panel2)
        myToggleBtnGroup.AddButton(ID3, 'III', panel3)
        myToggleBtnGroup.SelectByID(ID1)
