#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Visualization\Underlays\WindowSegmentUnderlay.py
from carbonui import uiconst, fontconst
from carbonui.decorative.panelUnderlay import PanelUnderlay
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.window.segment.underlay import WindowSegmentUnderlay
from eve.client.script.ui import eveColor
from eve.client.script.ui.control import eveLabel
from eve.devtools.script.uiControlCatalog.sample import Sample

class Sample1(Sample):
    name = 'Basic'
    description = WindowSegmentUnderlay.__doc__

    def construct_sample(self, parent):
        cont = Container(parent=parent, align=uiconst.TOPLEFT, pos=(0, 0, 500, 300))
        Frame(bgParent=cont, padding=-8, color=eveColor.MATTE_BLACK)
        self.sample_code(cont)

    def sample_code(self, parent):
        from carbonui.window.segment.underlay import WindowSegmentUnderlay
        bottomCont = Container(name='leftCont', align=uiconst.TOBOTTOM_PROP, height=0.33, parent=parent)
        WindowSegmentUnderlay(bgParent=bottomCont)
        eveLabel.EveLabelMedium(parent=bottomCont, text='WindowSegmentUnderlay\n\nButtons or secondary content', align=uiconst.CENTER)
        content = Container(name='content', parent=parent)
        eveLabel.EveLabelMedium(parent=content, text='Content', align=uiconst.CENTER)
