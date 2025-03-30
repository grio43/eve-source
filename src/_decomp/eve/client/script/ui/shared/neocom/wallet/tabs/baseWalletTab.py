#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\tabs\baseWalletTab.py
import trinity
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from carbonui.util.color import Color
from eve.client.script.ui.control.eveLabel import EveHeaderMediumBold, Label
from eve.client.script.ui.control.infoIcon import MoreInfoIcon
from carbonui.control.tab import Tab
from eve.client.script.ui.shared.neocom.wallet.walletTabUnderlay import WalletTabUnderlay
from localization import GetByLabel
ICON_CONTAINER_SIZE = 64
ICON_SIZE = 56
INFO_ICON_SIZE = 16
DEFAULT_PAD = 6

class BaseWalletTab(Tab):
    default_texturePath = None
    tabNamePath = None
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.TOLEFT_PROP
    default_width = 0.33333
    default_underlayColor = Color.GRAY
    labelColor = Color.WHITE
    iconSize = ICON_SIZE
    iconContainerSize = ICON_CONTAINER_SIZE
    amountFontSize = 17

    def ConstructLayout(self):
        self.tabName = GetByLabel(self.tabNamePath) if self.tabNamePath else ''
        self.ConstructMainContainer()
        self.ConstructIcon()
        self.ConstructDataContainer()
        self.PopulateBottomContainer()
        super(BaseWalletTab, self).ConstructLayout()

    def ConstructDataContainer(self):
        self.ConstructTopContainer()
        self.ConstructDividerLine()
        self.ConstructBottomContainer()

    def ConstructDividerLine(self):
        Line(name='dividerLine', parent=self.mainContainer, height=1, padLeft=DEFAULT_PAD, padRight=DEFAULT_PAD)

    def _ConstructUnderlay(self):
        self.selectedBG = WalletTabUnderlay(name='underlay', parent=self, fillColor=self.default_underlayColor)

    def ConstructIcon(self):
        iconContainer = Container(name='iconContainer', parent=self.mainContainer, align=uiconst.TOLEFT, width=self.iconContainerSize, idx=0)
        self.icon = Sprite(name='icon', parent=iconContainer, align=uiconst.CENTER, texturePath=self.default_texturePath, width=self.iconSize, height=self.iconSize, state=uiconst.UI_DISABLED)
        Fill(name='iconBackground', bgParent=iconContainer, color=Color.BLACK, opacity=0.25, padding=4)

    def ConstructMainContainer(self):
        self.mainContainer = Container(name='mainContainer', parent=self)

    def ConstructTopContainer(self):
        self.topContainer = Container(name='topContainer', parent=self.mainContainer, align=uiconst.TOTOP, height=32)
        self.ConstructTabNameLabel()
        self.ConstructInfoIcon(self.topContainer)

    def ConstructInfoIcon(self, container):
        self.infoIcon = MoreInfoIcon(name='infoIcon', parent=container, align=uiconst.CENTERRIGHT, width=INFO_ICON_SIZE, height=INFO_ICON_SIZE, left=DEFAULT_PAD, hint=self.default_hint)

    def ConstructTabNameLabel(self):
        self.tabNameLabel = EveHeaderMediumBold(name='tabNameLabel', parent=self.topContainer, align=uiconst.CENTERLEFT, left=DEFAULT_PAD, text=self.tabName)

    def ConstructBottomContainer(self):
        self.bottomContainer = Container(name='bottomContainer', parent=self.mainContainer)
        self.bottomLabel = Label(parent=self.bottomContainer, name='bottomLabel', state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT, left=6, blendMode=trinity.TR2_SBM_NONE, color=self.labelColor, fontsize=self.amountFontSize)

    def PopulateBottomContainer(self):
        pass

    def UpdateTabSize(self):
        pass

    def GetHeight(self):
        return 0

    def SetIcon(self, iconNo, shiftLabel = 14, hint = None, menufunc = None):
        pass

    def SetLabel(self, label, hint = None):
        pass
