#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\tooltip\blueprints.py
from carbonui import uiconst
from eve.common.lib import appConst as const
import localization
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.shared.industry.views.containersMETE import ContainerTE, ContainerME
from eve.client.script.ui.control import eveLabel
import evetypes
from eveexceptions import UserError

def AddBlueprintInfo(panel, itemID = None, typeID = None, bpData = None, spacerHeight = None):
    if not bpData:
        category = evetypes.GetCategoryID(typeID)
        if not category == const.categoryBlueprint:
            return
        bpData = None
        try:
            bpData = sm.GetService('blueprintSvc').GetBlueprintItemMemoized(itemID)
        except UserError as e:
            if e.msg == 'GenericStopSpamming':
                return

    if not bpData:
        return
    if spacerHeight:
        panel.AddSpacer(height=spacerHeight, colSpan=panel.columns)
    panel.AddSpacer(width=150, colSpan=panel.columns)
    panel.AddCell(DataEntry(align=uiconst.TOTOP, attribute=bpData), colSpan=panel.columns)


class DataEntry(ContainerAutoSize):
    default_align = uiconst.TOTOP
    default_state = uiconst.UI_DISABLED

    def ApplyAttributes(self, attributes):
        super(DataEntry, self).ApplyAttributes(attributes)
        self.bpData = attributes.attribute
        self.Layout()

    def Layout(self):
        if self.bpData.original:
            text = localization.GetByLabel('UI/Industry/OriginalInfiniteRuns')
        elif not self.bpData.runsRemaining or self.bpData.runsRemaining <= 0:
            text = localization.GetByLabel('UI/Industry/Copy')
        else:
            text = localization.GetByLabel('UI/Industry/CopyRunsRemaining', runsRemaining=self.bpData.runsRemaining)
        eveLabel.Label(parent=self, align=uiconst.TOTOP, text=text, width=32)
        if self.bpData.IsReactionBlueprint():
            return
        container = ContainerAutoSize(parent=self, align=uiconst.TOTOP, height=30)
        self.containerME = ContainerME(parent=container, align=uiconst.TOLEFT, width=71)
        self.containerME.SetValue(self.bpData.materialEfficiency)
        self.containerTE = ContainerTE(parent=container, align=uiconst.TOLEFT, width=71, padLeft=9)
        self.containerTE.SetValue(self.bpData.timeEfficiency)
