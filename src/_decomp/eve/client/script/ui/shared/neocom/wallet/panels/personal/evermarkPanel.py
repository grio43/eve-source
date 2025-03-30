#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\panels\personal\evermarkPanel.py
import localization
from appConst import corpHeraldry
from carbonui import TextAlign, uiconst
from carbonui.control.tabGroup import GetTabData, TabGroup
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.flowcontainer import FlowContainer
from eve.client.script.ui.control.eveLabel import EveLabelLarge
from eve.client.script.ui.shared.agencyNew.contentGroups.contentGroupConst import contentGroupMissionAgentsHeraldry
from eve.client.script.ui.shared.agencyNew.ui.agencyWnd import AgencyWndNew
from eve.client.script.ui.shared.info.infoConst import TAB_STATIONS
from eve.client.script.ui.shared.neocom.wallet import walletConst
from eve.client.script.ui.shared.neocom.wallet.panels.personal.personalDonateEMPanel import PersonalDonateEMPanel
from eveui import Sprite
ACTIONS_PAD_TOP = 20

class EverMarkPanel(Container):
    default_name = 'EverMarkPanel'
    panelID = walletConst.PANEL_EVERMARKS

    def ApplyAttributes(self, attributes):
        super(EverMarkPanel, self).ApplyAttributes(attributes)
        self.ConstructLayout()

    def ConstructLayout(self):
        self.overviewPanel = OverviewPanel(parent=self, state=uiconst.UI_HIDDEN)
        self.donatePanel = PersonalDonateEMPanel(parent=self, state=uiconst.UI_HIDDEN)
        tabs = (GetTabData(label=localization.GetByLabel('UI/Wallet/WalletWindow/TabOverview'), panel=self.overviewPanel, tabID=walletConst.PANEL_EM_BALANCE), GetTabData(label=localization.GetByLabel('UI/Wallet/WalletWindow/TabDonate'), panel=self.donatePanel, tabID=walletConst.PANEL_EM_DONATE))
        self.tabGroup = TabGroup(name='WalletPersonalEMTabGroup', parent=self, tabs=tabs, padBottom=16, groupID='WalletPersonalEMTabs', idx=0)

    def CreateActions(self):
        self.actions = EverMarkActions(parent=self, align=uiconst.TOTOP, top=ACTIONS_PAD_TOP)


class OverviewPanel(Container):

    def __init__(self, **kwargs):
        super(OverviewPanel, self).__init__(**kwargs)
        self.CreateActions()

    def CreateActions(self):
        self.actions = EverMarkActions(parent=self, align=uiconst.TOTOP, top=ACTIONS_PAD_TOP)


class EverMarkActions(FlowContainer):
    default_name = 'EvermarkActions'

    def __init__(self, **kwargs):
        super(EverMarkActions, self).__init__(centerContent=True, contentSpacing=(16, 16), **kwargs)
        self.underlayColorHighlighted = (0.87, 0.61, 0.0, 0.2)
        EverMarkAction(parent=self, align=uiconst.NOALIGN, texturePath='res:/ui/texture/WindowIcons/evermark_64px.png', text=localization.GetByLabel('UI/Wallet/WalletWindow/EverMarkEarn'), OnClick=self.OpenAgency, state=uiconst.UI_ACTIVE)
        EverMarkAction(parent=self, align=uiconst.NOALIGN, texturePath='res:/ui/Texture/WindowIcons/lpstore.png', text=localization.GetByLabel('UI/Wallet/WalletWindow/EverMarkSpend'), OnClick=self.OpenCorpWindowOnStations, state=uiconst.UI_ACTIVE)

    def OpenAgency(self, *args, **kwargs):
        AgencyWndNew.OpenAndShowContentGroup(contentGroupMissionAgentsHeraldry)

    def OpenCorpWindowOnStations(self, *args, **kwargs):
        from inventorycommon import const as invconst
        sm.GetService('info').ShowInfo(invconst.typeCorporation, corpHeraldry, selectTabType=TAB_STATIONS)


class EverMarkAction(Container):
    default_height = 160
    default_width = 128
    contentSpacing = (16, 16)
    underlayColorHighlighted = (0.87, 0.87, 0.87, 0.2)

    def ApplyAttributes(self, attributes):
        super(EverMarkAction, self).ApplyAttributes(attributes)
        self.CreateUnderlay()
        iconContainer = Container(parent=self, align=uiconst.TOTOP, height=64)
        self.OnClick = attributes.OnClick
        self.icon = Sprite(name='icon', parent=iconContainer, align=uiconst.CENTER, texturePath=attributes.texturePath, width=64, height=64, state=uiconst.UI_DISABLED)
        textContainer = Container(parent=self, align=uiconst.TOALL)
        EveLabelLarge(parent=textContainer, align=uiconst.TOALL, text=attributes.text, textAlign=TextAlign.CENTER, padding=(4, 4, 4, 4))

    def CreateUnderlay(self):
        self.underlay = Fill(bgParent=self, color=self.underlayColorHighlighted)
