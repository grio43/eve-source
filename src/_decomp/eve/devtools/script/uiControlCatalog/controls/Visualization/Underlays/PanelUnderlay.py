#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Visualization\Underlays\PanelUnderlay.py
from carbonui import uiconst
from carbonui.decorative.panelUnderlay import PanelUnderlay
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from eve.client.script.ui import eveColor
from eve.client.script.ui.control import eveLabel
from eve.devtools.script.uiControlCatalog.sample import Sample

class Sample1(Sample):
    name = 'Basic'
    description = PanelUnderlay.__doc__

    def construct_sample(self, parent):
        cont = Container(parent=parent, align=uiconst.TOPLEFT, pos=(0, 0, 500, 300))
        Frame(bgParent=cont, padding=-8, color=eveColor.MATTE_BLACK)
        self.sample_code(cont)

    def sample_code(self, parent):
        from carbonui.decorative.panelUnderlay import PanelUnderlay
        leftCont = Container(name='leftCont', align=uiconst.TOLEFT_PROP, width=0.33, parent=parent)
        PanelUnderlay(bgParent=leftCont)
        eveLabel.EveLabelMedium(parent=leftCont, text='PanelUnderlay\n\nNavigation or secondary content', align=uiconst.CENTER, width=120)
        content = Container(name='content', parent=parent)
        eveLabel.EveLabelMedium(parent=content, text='Content', align=uiconst.CENTER)
