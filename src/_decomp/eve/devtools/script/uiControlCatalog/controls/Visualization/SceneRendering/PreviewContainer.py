#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Visualization\SceneRendering\PreviewContainer.py
import carbonui.const as uiconst
from eve.devtools.script.uiControlCatalog.sample import Sample

class Sample1(Sample):
    name = 'Type'

    def sample_code(self, parent):
        from eve.client.script.ui.shared.preview import PreviewContainer
        previewCont = PreviewContainer(parent=parent, align=uiconst.TOPLEFT, width=400, height=300)
        previewCont.PreviewType(28272)


class Sample2(Sample):
    name = 'Turret'

    def sample_code(self, parent):
        from eve.client.script.ui.shared.preview import PreviewContainer
        previewCont = PreviewContainer(parent=parent, align=uiconst.TOPLEFT, width=400, height=300)
        previewCont.PreviewTurret(22913)


class Sample3(Sample):
    name = 'Skin'

    def sample_code(self, parent):
        from eve.client.script.ui.shared.preview import PreviewContainer
        previewCont = PreviewContainer(parent=parent, align=uiconst.TOPLEFT, width=400, height=300)
        previewCont.PreviewSkin(60239)


class Sample4(Sample):
    name = 'Character'

    def sample_code(self, parent):
        from eve.client.script.ui.shared.preview import PreviewContainer
        previewCont = PreviewContainer(parent=parent, align=uiconst.TOPLEFT, width=400, height=300)
        previewCont.PreviewCharacter(session.charid)
