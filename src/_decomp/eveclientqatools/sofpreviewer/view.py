#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveclientqatools\sofpreviewer\view.py
import carbonui.const as uiconst
import carbonui.fontconst
from carbonui.primitives.container import Container
from carbonui.primitives.gridcontainer import GridContainer
from carbonui.button.group import ButtonGroup
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from carbonui.control.window import Window
from eve.client.script.ui.shared.preview import PreviewContainer

class SofPreviewerView(object):

    def __init__(self, controller):
        self.controller = controller
        self.name = 'SOF Preview Window'
        self.windowID = 'SOFPreviewWindow_ ' + self.name
        self.previewCont = None
        self.leftView = None
        self.centerView = None
        self.rightView = None
        self.dnaLabel = None

    def ShowUI(self, *controllers):
        Window.CloseIfOpen(windowID=self.windowID)
        wnd = Window.Open(windowID=self.windowID)
        wnd.SetMinSize([1200, 700])
        wnd.SetCaption(self.name)
        main = wnd.GetMainArea()
        headerCont = Container(name='headerCont', parent=main, align=uiconst.TOTOP, height=30)
        self.dnaLabel = EveLabelSmall(name='dnaLabel', align=uiconst.CENTER, parent=headerCont, text='')
        self.SetupButtonContainer(main)
        self.SetupInputContainers(main, controllers)
        self.previewCont = PreviewContainer(parent=main, align=uiconst.TOALL)

    def SetupButtonContainer(self, parent):
        buttonContainer = Container(name='_buttonCont', parent=parent, align=uiconst.TOBOTTOM, height=20, padBottom=10)
        buttonGroup = ButtonGroup(name='buttonGroup', parent=buttonContainer, align=uiconst.CENTER, fontsize=carbonui.fontconst.EVE_MEDIUM_FONTSIZE)
        buttonGroup.AddButton('Copy DNA', self.controller.OnCopyDnaButton)
        buttonGroup.AddButton('Apply', self.controller.OnApplyButton)

    def SetupInputContainers(self, parent, controllers):
        inputContainer = GridContainer(name='inputCont', parent=parent, align=uiconst.TOBOTTOM, height=320, lines=1, columns=len(controllers))
        for controller in controllers:
            controller.ShowUI(inputContainer)
