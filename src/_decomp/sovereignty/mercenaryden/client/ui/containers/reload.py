#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\mercenaryden\client\ui\containers\reload.py
import eveicon
from carbonui import Align, TextHeader, TextBody, TextColor
from carbonui.control.button import Button
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui import eveColor, eveThemeColor
from localization import GetByLabel

class ReloadContainer(ContainerAutoSize):
    LABEL_PATH_TITLE = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/ReloadTitle'
    LABEL_PATH_DESCRIPTION = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/ReloadDescription'
    LABEL_PATH_BUTTON = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/ReloadButton'
    PADDING_CONTENT = 16
    PADDING_TITLE_TO_DESCRIPTION = 8
    PADDING_DESCRIPTION_TO_BUTTON = 16
    COLOR_TITLE = eveThemeColor.THEME_FOCUS
    COLOR_DESCRIPTION = TextColor.NORMAL
    COLOR_BACKGROUND = eveThemeColor.THEME_FOCUSDARK
    OPACITY_BACKGROUND = 0.35
    default_bgColor = (COLOR_BACKGROUND[0],
     COLOR_BACKGROUND[1],
     COLOR_BACKGROUND[2],
     OPACITY_BACKGROUND)

    def __init__(self, reload, *args, **kwargs):
        self._reload = reload
        super(ReloadContainer, self).__init__(*args, **kwargs)
        self._construct_content()

    def _construct_content(self):
        self._content = ContainerAutoSize(name='reload_content_container', parent=self, align=Align.TOTOP, padding=self.PADDING_CONTENT)
        self._construct_title()
        self._construct_description()
        self._construct_button()
        self._content.SetSizeAutomatically()
        self.SetSizeAutomatically()

    def _construct_title(self):
        container_title = ContainerAutoSize(name='reload_title_container', parent=self._content, align=Align.TOTOP)
        TextHeader(name='reload_title', parent=container_title, align=Align.CENTER, text=GetByLabel(self.LABEL_PATH_TITLE).upper(), color=self.COLOR_TITLE)
        container_title.SetSizeAutomatically()

    def _construct_description(self):
        container_description = ContainerAutoSize(name='reload_description_container', parent=self._content, align=Align.TOTOP, padTop=self.PADDING_TITLE_TO_DESCRIPTION)
        TextBody(name='reload_description', parent=container_description, align=Align.CENTER, text=GetByLabel(self.LABEL_PATH_DESCRIPTION), color=self.COLOR_DESCRIPTION)
        container_description.SetSizeAutomatically()

    def _construct_button(self):
        container_button = ContainerAutoSize(name='reload_button_container', parent=self._content, align=Align.TOTOP, padTop=self.PADDING_DESCRIPTION_TO_BUTTON)
        self._button = Button(name='take_cargo_items_button', parent=container_button, align=Align.CENTER, func=self._on_button_clicked, label=GetByLabel(self.LABEL_PATH_BUTTON), texturePath=eveicon.arrow_rotate_right)
        container_button.SetSizeAutomatically()

    def _on_button_clicked(self, *args, **kwargs):
        self._button.Disable()
        self._button.busy = True
        try:
            self._reload()
        finally:
            self._button.Enable()
            self._button.busy = False
