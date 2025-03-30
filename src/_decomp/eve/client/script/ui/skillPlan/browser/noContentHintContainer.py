#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\browser\noContentHintContainer.py
import carbonui
from carbonui import uiconst, TextAlign
from carbonui.primitives.containerAutoSize import ContainerAutoSize

class NoContentHintContainer(ContainerAutoSize):
    default_state = uiconst.UI_PICKCHILDREN

    def __init__(self, btnClass, **kw):
        self.btnClass = btnClass
        super(NoContentHintContainer, self).__init__(**kw)

    def ApplyAttributes(self, attributes):
        super(NoContentHintContainer, self).ApplyAttributes(attributes)
        self.label = carbonui.TextHeadline(parent=self, align=uiconst.TOTOP, textAlign=TextAlign.CENTER)
        self.buttonCont = ContainerAutoSize(name='buttonCont', parent=self, align=uiconst.TOTOP, height=30, padTop=16)
        self.createBtn = self.btnClass(name='createBtn', parent=self.buttonCont, align=uiconst.CENTER)

    def SetText(self, text):
        self.label.SetText(text)

    def UpdateState(self, numPlans):
        self.createBtn.UpdateState(numPlans)

    def HideCreateBtn(self):
        self.createBtn.Hide()
