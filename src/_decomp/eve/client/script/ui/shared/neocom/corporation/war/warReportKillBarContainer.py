#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\war\warReportKillBarContainer.py
from carbon.common.script.util.format import FmtAmt
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from eve.client.script.ui.shared.neocom.corporation.war.warReport import ATTACKER_COLOR, DEFENDER_COLOR
from eve.common.script.util.eveFormat import FmtISK
from localization import GetByLabel

class KillsBarContainer(Container):
    __guid__ = 'uicls.KillsBarContainer'
    default_height = 18
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.TOTOP

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.attackerID = attributes.get('attackerID', None)
        self.defenderID = attributes.get('defenderID', None)
        self.attackerKills = attributes.get('attackerKills', 0)
        self.defenderKills = attributes.get('defenderKills', 0)
        self.attackerKillsIsk = attributes.get('attackerKillsIsk', 0)
        self.defenderKillsIsk = attributes.get('defenderKillsIsk', 0)
        self.groupID = attributes.get('groupID', None)
        self.maxKills = attributes.get('maxKills', 0)
        self.ConstructLayout()

    def ConstructLayout(self):
        contName = 'group_%d' % self.groupID
        self.selected = Fill(bgParent=self, color=(1.0, 1.0, 1.0, 0.15), state=uiconst.UI_DISABLED)
        self.selected.display = False
        self.hilite = Fill(parent=self, color=(1.0, 1.0, 1.0, 0.1), state=uiconst.UI_DISABLED)
        self.hilite.display = False
        self.OnMouseEnter = self.BarOnMouseEnter
        self.OnMouseExit = self.BarOnMouseExit
        topbar = Container(name='topbar', parent=self, align=uiconst.TOTOP, height=5, padTop=4)
        try:
            redwith = float(self.attackerKillsIsk) / float(self.maxKills)
        except:
            redwith = 0.0

        redbar = Container(parent=topbar, align=uiconst.TOLEFT_PROP, width=redwith, height=5, bgColor=ATTACKER_COLOR)
        bottombar = Container(name='bluebar', parent=self, align=uiconst.TOBOTTOM, height=5, padBottom=4)
        try:
            bluewith = float(self.defenderKillsIsk) / float(self.maxKills)
        except:
            bluewith = 0.0

        bluebar = Container(parent=bottombar, align=uiconst.TOLEFT_PROP, width=bluewith, height=5, bgColor=DEFENDER_COLOR)

    def BarOnMouseEnter(self, *args):
        self.hilite.display = True

    def BarOnMouseExit(self, *args):
        self.hilite.display = False

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric1ColumnTemplate()
        attackerName = cfg.eveowners.Get(self.attackerID).name
        aggressorKillsText = GetByLabel('UI/Corporations/Wars/WarReportNumKills', numKills=self.attackerKills)
        aggressorKillsIsk = FmtISK(self.attackerKillsIsk, 0)
        tooltipPanel.AddLabelMedium(text=attackerName, bold=True)
        tooltipPanel.AddLabelMedium(text=aggressorKillsText)
        tooltipPanel.AddLabelMedium(text=aggressorKillsIsk)
        tooltipPanel.AddSpacer(height=10)
        defenderName = cfg.eveowners.Get(self.defenderID).name
        defenderKillsText = GetByLabel('UI/Corporations/Wars/WarReportNumKills', numKills=self.defenderKills)
        defenderKillsIsk = FmtISK(self.defenderKillsIsk, 0)
        tooltipPanel.AddLabelMedium(text=defenderName, bold=True)
        tooltipPanel.AddLabelMedium(text=defenderKillsText)
        tooltipPanel.AddLabelMedium(text=defenderKillsIsk)
