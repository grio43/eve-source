#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\ui\dialog.py
import carbonui.const as uiconst
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLabel import EveLabelMedium, Label
from carbonui.control.window import Window
from localization import GetByLabel
TEXT_WIDTH = 200
TEXT_FONTSIZE = 12
TEXT_TOP = 0
PADDING_V = 0
PADDING_LEFT_ERROR_IMAGE = 0
PADDING_RIGHT_TEXT = 0
PADDING_BETWEEN_CONTENT = 24
HEADER_HEIGHT = 22
BUTTON_WIDTH = 80
BUTTON_HEIGHT = 30
BUTTON_FONTSIZE = 12
PADDING_BETWEEN_BUTTONS = 8

class DialogPopup(Window):
    __guid__ = 'form.DialogPopup'
    default_windowID = 'ProjectDiscoveryDialogPopup'
    default_isLightBackgroundConfigurable = False
    default_isKillable = True
    default_isMinimizable = False
    default_isStackable = False
    default_isCollapseable = False
    default_isLockable = False
    default_isOverlayable = False
    default_showConfirmButton = True
    default_showCancelButton = False

    def ApplyAttributes(self, attributes):
        self.text = attributes.text
        self.image = attributes.image
        self.image_width = attributes.imageWidth
        self.image_height = attributes.imageHeight
        self.show_confirm_button = attributes.get('showConfirm', self.default_showConfirmButton)
        self.confirm_text = attributes.get('confirmText', None)
        self.confirm_function = attributes.get('confirmFunction', None)
        self.show_cancel_button = attributes.get('showCancel', self.default_showCancelButton)
        self.cancel_text = attributes.get('cancelText', None)
        self.cancel_function = attributes.get('cancelFunction', None)
        Window.ApplyAttributes(self, attributes)
        self.caption = GetByLabel(attributes.caption)
        self.buttons = None
        self.ConstructLayout()

    def ConstructLayout(self):
        self.main_container = ContainerAutoSize(parent=self.content, align=uiconst.TOPLEFT, callback=self._on_main_cont_size_changed, only_use_callback_when_size_changes=True)
        self.AddErrorImage()
        self.AddText()
        self.buttons = LayoutGrid(parent=self.text_container, align=uiconst.BOTTOMRIGHT, columns=2, cellSpacing=(8, 8))
        self.AddConfirmButton()
        self.AddCancelButton()

    def _on_main_cont_size_changed(self):
        width, height = self.GetWindowSizeForContentSize(height=self.main_container.height, width=self.main_container.width)
        self.SetFixedWidth(width)
        self.SetFixedHeight(height)

    def AddErrorImage(self):
        Sprite(name='error_image', parent=self.main_container, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, width=self.image_width, height=self.image_height, top=PADDING_V, left=PADDING_LEFT_ERROR_IMAGE, texturePath=self.image)

    def AddText(self):
        self.text_container = Container(name='text_container', parent=self.main_container, align=uiconst.TOPLEFT, top=PADDING_V, left=PADDING_LEFT_ERROR_IMAGE + self.image_width + PADDING_BETWEEN_CONTENT, width=TEXT_WIDTH, height=self.image_height)
        EveLabelMedium(name='error_text', parent=self.text_container, align=uiconst.TOTOP, text=GetByLabel(self.text), top=TEXT_TOP)

    def AddConfirmButton(self):
        if self.show_confirm_button:
            button_text = self.confirm_text if self.confirm_text else 'UI/ProjectDiscovery/Covid/Errors/ButtonOk'
            Button(name='confirm_button', parent=self.buttons, align=uiconst.BOTTOMRIGHT, label=GetByLabel(button_text), func=lambda *args: self.Confirm())

    def AddCancelButton(self):
        if self.show_cancel_button:
            button_text = self.cancel_text if self.cancel_text else 'UI/ProjectDiscovery/Covid/Errors/ButtonCancel'
            Button(name='cancel_button', parent=self.buttons, align=uiconst.BOTTOMRIGHT, label=GetByLabel(button_text), func=lambda *args: self.Cancel())

    def Confirm(self):
        if self.confirm_function:
            self.confirm_function()
        self.Close()

    def Cancel(self):
        if self.cancel_function:
            self.cancel_function()
        self.Close()
