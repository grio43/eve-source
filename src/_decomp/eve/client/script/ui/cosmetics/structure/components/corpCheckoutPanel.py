#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\structure\components\corpCheckoutPanel.py
import blue
from appConst import corpHeraldry
from carbon.common.script.util.format import FmtAmt
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui import const as uiconst, TextColor, TextAlign
from carbonui.uianimations import animations
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveCaptionMedium
from eve.client.script.ui.cosmetics.structure import paintToolSignals, paintToolUtils
from localization import GetByLabel
BALANCE_ICON_SIZE = 40
TOTAL_ICON_SIZE = 18

class CorpCheckoutPanel(Container):
    default_height = BALANCE_ICON_SIZE
    __notifyevents__ = ['OnCorporationLPBalanceChange_Local']

    def __init__(self, **kw):
        super(CorpCheckoutPanel, self).__init__(**kw)
        self._current_balance = 0
        self._construct_layout()
        paintToolSignals.on_structure_selection_changed.connect(self._on_structure_selection_changed)
        paintToolSignals.on_duration_selection_changed.connect(self._on_duration_selection_changed)
        sm.RegisterNotify(self)

    def Close(self):
        paintToolSignals.on_structure_selection_changed.disconnect(self._on_structure_selection_changed)
        paintToolSignals.on_duration_selection_changed.disconnect(self._on_duration_selection_changed)
        super(CorpCheckoutPanel, self).Close()

    def update(self):
        self._update_total_price()
        self._update_balance()

    def _construct_layout(self):
        left_cont = Container(parent=self, name='leftCont', align=uiconst.TOLEFT_PROP, width=0.5)
        Sprite(parent=left_cont, name='evermarksBalanceIcon', align=uiconst.TOLEFT, texturePath='res:/UI/Texture/Icons/evermarks_trimmed.png', width=BALANCE_ICON_SIZE, height=BALANCE_ICON_SIZE)
        balance_parent_cont = Container(parent=left_cont, name='balanceParentCont', align=uiconst.TOALL, padLeft=15)
        EveLabelMedium(parent=balance_parent_cont, name='balanceTitle', align=uiconst.TOTOP, text=GetByLabel('UI/Personalization/PaintTool/EvermarksBalance'))
        balance_cont = Container(parent=balance_parent_cont, name='balanceCont', align=uiconst.TOALL)
        balance_label_cont = ContainerAutoSize(parent=balance_cont, name='balanceLabelCont', align=uiconst.TOLEFT)
        self._balance_label = EveCaptionMedium(parent=balance_label_cont, name='balanceLabel', align=uiconst.CENTER, padRight=4)
        icon_center_cont = Container(parent=balance_cont, name='iconCenterCont', align=uiconst.TOLEFT, width=32)
        self._insufficient_funds_icon = Sprite(parent=icon_center_cont, name='insufficientFundsIcon', align=uiconst.CENTER, width=32, height=32, texturePath='res:/UI/Texture/classes/paintTool/insufficient_funds.png', opacity=0, state=uiconst.UI_NORMAL, hint=GetByLabel('UI/Personalization/PaintTool/InsufficientFundsTooltip'))
        self._update_balance()
        right_cont = Container(parent=self, name='rightCont', align=uiconst.TORIGHT_PROP, width=0.5)
        EveLabelMedium(parent=right_cont, name='totalTitle', align=uiconst.TOTOP, textAlign=TextAlign.RIGHT, text=GetByLabel('UI/Personalization/PaintTool/TotalCostTitle'))
        total_cont = Container(parent=right_cont, name='totalCont', align=uiconst.TOBOTTOM, height=TOTAL_ICON_SIZE)
        total_label_cont = ContainerAutoSize(parent=total_cont, name='totalLabelCont', align=uiconst.TORIGHT)
        self._total_label = EveCaptionMedium(parent=total_label_cont, name='balanceLabel', align=uiconst.CENTER, text=FmtAmt(0))
        Sprite(parent=total_cont, name='evermarksTotalIcon', align=uiconst.TORIGHT, texturePath='res:/UI/Texture/Icons/evermarks_trimmed.png', width=TOTAL_ICON_SIZE, height=TOTAL_ICON_SIZE, padRight=12)

    def _on_structure_selection_changed(self, *_args):
        self._update_total_price()

    def _on_duration_selection_changed(self):
        self._update_total_price()

    def _update_total_price(self):
        self._total_label.text = FmtAmt(paintToolUtils.get_total_price())
        self._update_balance()

    def _update_balance(self, animate = False):
        balance = paintToolUtils.get_evermark_balance()
        if animate:
            original_balance = self._current_balance if self._current_balance else 0
            self._animate_balance_change(balance, original_balance)
        else:
            self._balance_label.text = FmtAmt(balance)
        self._current_balance = balance
        insufficient_funds = not paintToolUtils.has_sufficient_funds()
        target_color = eveColor.DANGER_RED if insufficient_funds else TextColor.NORMAL
        target_opacity = 1.0 if insufficient_funds else 0.0
        animations.FadeTo(self._insufficient_funds_icon, self._insufficient_funds_icon.opacity, target_opacity, 0.25)
        animations.SpColorMorphTo(self._balance_label, self._balance_label.GetRGBA(), target_color, duration=0.25)

    def OnCorporationLPBalanceChange_Local(self, issuerCorpID):
        if issuerCorpID == corpHeraldry:
            self._update_balance(animate=True)

    def _animate_balance_change(self, balance, original_balance):
        total_iterations = 20
        difference = balance - original_balance
        for i in range(total_iterations):
            increment = (i + 1) / (1.0 * total_iterations)
            value = original_balance + difference * increment
            self._balance_label.text = FmtAmt(value)
            blue.synchro.Sleep(25)
