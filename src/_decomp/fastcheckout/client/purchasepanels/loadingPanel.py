#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fastcheckout\client\purchasepanels\loadingPanel.py
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel

class LoadingPanel(Container):
    default_opacity = 0.0

    def ApplyAttributes(self, attributes):
        super(LoadingPanel, self).ApplyAttributes(attributes)
        self.construct_layout()

    def construct_layout(self):
        main_cont = ContainerAutoSize(parent=self, align=uiconst.CENTER, alignMode=uiconst.TOTOP, width=1)
        wheel_wrap = ContainerAutoSize(parent=main_cont, align=uiconst.TOTOP)
        LoadingWheel(parent=wheel_wrap, align=uiconst.CENTER)

    def AnimEntry(self):
        animations.FadeIn(self, duration=0.5, timeOffset=0.5)

    def AnimExit(self):
        animations.FadeOut(self, callback=self.Close, duration=0.2)
