#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\standings\standingLabel.py
from carbonui import uiconst, fontconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.eveLabel import Label
from eve.common.script.sys import idCheckers
from eve.common.script.util.standingUtil import OpenStandingsPanelOnOwnerByID

class StandingLabel(ContainerAutoSize):
    default_name = 'StandingLabel'
    default_state = uiconst.UI_NORMAL
    default_fontSize = fontconst.EVE_MEDIUM_FONTSIZE

    def ApplyAttributes(self, attributes):
        super(StandingLabel, self).ApplyAttributes(attributes)
        self.isRightToLeft = attributes.isRightToLeft
        standingData = attributes.standingData
        fontSize = attributes.Get('fontSize', self.default_fontSize)
        self.label = Label(name='toStandingsLabel', parent=self, fontsize=fontSize)
        if standingData:
            self.SetStandingData(standingData)

    def SetStandingData(self, standingData):
        self.standingData = standingData
        if self.isRightToLeft:
            self.label.align = uiconst.CENTERLEFT
            self.label.text = self.standingData.GetStanding2To1Formatted()
        else:
            self.label.align = uiconst.CENTERRIGHT
            self.label.text = self.standingData.GetStanding1To2Formatted()

    def OnClick(self, *args):
        if idCheckers.IsPlayerOwner(self.standingData.GetOwnerID2()):
            return
        if idCheckers.IsCorporation(self.standingData.GetOwnerID1()):
            return
        OpenStandingsPanelOnOwnerByID(self.standingData.GetOwnerID2())
