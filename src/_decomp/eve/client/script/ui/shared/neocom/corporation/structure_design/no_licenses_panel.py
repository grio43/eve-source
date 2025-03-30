#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\structure_design\no_licenses_panel.py
from carbonui import uiconst, ButtonVariant, TextAlign
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from eve.client.script.ui.control.eveLabel import EveCaptionLarge, EveLabelMedium
from localization import GetByLabel

class CorpStructureDesignNoLicensesPanel(Container):
    default_clipChildren = True
    BACKGROUND_WIDTH = 1600
    BACKGROUND_HEIGHT = 900

    def __init__(self, *args, **kwargs):
        super(CorpStructureDesignNoLicensesPanel, self).__init__(*args, **kwargs)
        self._background = None
        self._construct_layout()

    def _construct_layout(self):
        content_container = ContainerAutoSize(name='content_container', parent=self, align=uiconst.TOBOTTOM, bgColor=(0.0, 0.0, 0.0, 0.7))
        button_container = ContainerAutoSize(name='button_container', parent=content_container, align=uiconst.TOBOTTOM, padBottom=50)
        Button(name='skinr_button', parent=button_container, align=uiconst.CENTER, label=GetByLabel('UI/Personalization/PaintTool/OpenSKINR'), texturePath='res:/UI/Texture/WindowIcons/paint_tool.png', variant=ButtonVariant.PRIMARY, func=self._on_skinr_button_click)
        description_container = ContainerAutoSize(name='description_container', parent=content_container, align=uiconst.TOBOTTOM, padBottom=40)
        EveLabelMedium(name='cta_description', parent=description_container, align=uiconst.TOTOP, text=GetByLabel('UI/Personalization/PaintTool/TrySKINRDescription'), textAlign=TextAlign.CENTER)
        caption_container = ContainerAutoSize(name='caption_container', parent=content_container, align=uiconst.TOBOTTOM, padBottom=10, padTop=50)
        EveCaptionLarge(name='cta_caption', parent=caption_container, align=uiconst.TOTOP, text=GetByLabel('UI/Personalization/PaintTool/TrySKINRTitle'), textAlign=TextAlign.CENTER)
        self._background = Sprite(name='background', parent=self, align=uiconst.CENTER, texturePath='res:/UI/Texture/classes/StructureDesign/background/skinr.png', state=uiconst.UI_DISABLED)
        self._OnResize()

    def _on_skinr_button_click(self, _buttton):
        uicore.cmd.OpenPaintToolWindow()

    def _OnResize(self, *args):
        super(CorpStructureDesignNoLicensesPanel, self)._OnResize(*args)
        if self.destroyed:
            return
        if self._background:
            scale_ratio = float(self.displayHeight) / float(self.BACKGROUND_HEIGHT)
            self._background.width = float(self.BACKGROUND_WIDTH) * scale_ratio
            self._background.height = float(self.BACKGROUND_HEIGHT) * scale_ratio
