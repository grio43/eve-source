#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\mercenaryden\client\ui\containers\cargo_item.py
from carbon.common.script.util.format import FmtAmt
from carbonui import Align, TextBody, TextColor, TextDetail, PickState
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui import eveColor
from localization import GetByLabel
from sovereignty.mercenaryden.client.ui.containers.cargo_item_icon import CargoItemIcon

class CargoItem(ContainerAutoSize):
    LABEL_PATH_AMOUNT_AVAILABLE = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/CargoItemAmountAvailableLabel'
    PADDING_ICON_TO_TEXT = 8
    PADDING_TYPE_NAME_TO_AVAILABLE = 8
    PADDING_AVAILABLE_TO_AMOUNT = 2
    COLOR_BACKGROUND = eveColor.BLACK
    OPACITY_BACKGROUND = 0.0
    default_bgColor = (COLOR_BACKGROUND[0],
     COLOR_BACKGROUND[1],
     COLOR_BACKGROUND[2],
     OPACITY_BACKGROUND)
    default_alignMode = Align.TOTOP

    def __init__(self, controller, form, *args, **kwargs):
        self.amount_available = 0
        self._controller = controller
        self._form = form
        super(CargoItem, self).__init__(*args, **kwargs)
        self._construct_icon()
        self._construct_input()
        self._construct_texts()

    def _construct_icon(self):
        self._icon_container = CargoItemIcon(name='icon_container', parent=self, align=Align.TOLEFT, pickState=PickState.ON, controller=self._controller)

    def _construct_input(self):
        self.input_container = ContainerAutoSize(name='input_container', parent=self, align=Align.TORIGHT)

    def _construct_texts(self):
        self._texts_container = ContainerAutoSize(name='texts_container', parent=self, align=Align.TOTOP, padLeft=self.PADDING_ICON_TO_TEXT)
        self._construct_type_name()
        self._construct_available_text()
        self._construct_available_amount()

    def _construct_type_name(self):
        space_available_for_text = ContainerAutoSize(name='space_available_for_text', parent=self._texts_container, align=Align.TOTOP)
        self.type_name_text = TextBody(name='type_name_text', parent=space_available_for_text, align=Align.CENTERLEFT, pickState=PickState.ON, maxLines=1, autoFadeSides=16)

    def _construct_available_text(self):
        TextDetail(name='available_text', parent=self._texts_container, align=Align.TOTOP, color=TextColor.SECONDARY, text=GetByLabel(self.LABEL_PATH_AMOUNT_AVAILABLE), padTop=self.PADDING_TYPE_NAME_TO_AVAILABLE, padBottom=self.PADDING_AVAILABLE_TO_AMOUNT, maxLines=1)

    def _construct_available_amount(self):
        self.amount_available_text = TextBody(name='amount_available_text', parent=self._texts_container, align=Align.TOTOP, maxLines=1)

    def load(self, amount):
        self.amount_available = amount
        self.type_name_text.text = self._controller.get_infomorph_type_name()
        self.amount_available_text.text = FmtAmt(self.amount_available)
        if self._controller.is_cargo_extraction_enabled():
            self.type_name_text.color = TextColor.NORMAL
            self.amount_available_text.color = TextColor.NORMAL
        else:
            self.type_name_text.color = TextColor.DISABLED
            self.amount_available_text.color = TextColor.DISABLED
        self._icon_container.load(amount)
