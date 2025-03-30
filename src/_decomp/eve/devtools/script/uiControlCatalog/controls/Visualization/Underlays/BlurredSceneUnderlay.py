#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Visualization\Underlays\BlurredSceneUnderlay.py
import carbonui.const as uiconst
from eve.client.script.ui.control.eveLabel import EveLabelLarge
from eve.devtools.script.uiControlCatalog.sample import Sample

class Sample1(Sample):
    name = 'Basic'
    description = 'This underlay uses a blurred version of the background scene and is used to give Windows a see-through effect. Active state of parent window affects the brightness. Try moving the scene camera around and switch focus between windows.'

    def sample_code(self, parent):
        from carbonui.decorative.blurredSceneUnderlay import BlurredSceneUnderlay
        BlurredSceneUnderlay(name='myUnderlay', parent=parent, align=uiconst.CENTER, width=100, height=200)
        EveLabelLarge(parent=parent, align=uiconst.CENTER, text="This is some text that is partially invisible since it's overlayed by the scene underlay component")


class Sample2(Sample):
    name = 'Light Background mode'
    description = 'Same, but this mode allows color through as well'

    def sample_code(self, parent):
        from carbonui.decorative.blurredSceneUnderlay import BlurredSceneUnderlay
        BlurredSceneUnderlay(name='myUnderlay', parent=parent, align=uiconst.CENTER, width=100, height=200, isLightBackground=True)
        EveLabelLarge(parent=parent, align=uiconst.CENTER, text="This is some text that is partially invisible since it's overlayed by the scene underlay component")
