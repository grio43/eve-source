#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\ui\underConstruction\underConstructionCont.py
import mathext
from localization import GetByLabel
from dynamicresources.client.ess.bracket.label import Header
from spacecomponents.common.componentConst import UNDER_CONSTRUCTION
from carbonui.primitives.fill import Fill
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.eveLabel import EveLabelMedium, Label
import evetypes
from carbonui.primitives.layoutGrid import LayoutGrid
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.gauge import Gauge
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from carbonui.control.button import Button

class UnderConstructionCont(ContainerAutoSize):
    default_name = 'underConstructionCont'
    __notifyevents__ = ['OnUnderConstructionUpdated']
    default_alignMode = uiconst.TOPLEFT

    def ApplyAttributes(self, attributes):
        super(UnderConstructionCont, self).ApplyAttributes(attributes)
        self._itemID = attributes.itemID
        self._typeID = attributes.typeID
        self.inputContsByTypeID = {}
        underConstructionComp = self._GetComponent()
        self.mainGrid = LayoutGrid(parent=self, columns=1, align=uiconst.TOPLEFT)
        EveLabelMedium(parent=self.mainGrid, align=uiconst.TOPLEFT, text=evetypes.GetName(self._typeID), maxLines=1)
        text = GetByLabel('UI/Inflight/UnderConstructionProgress', progress=0)
        self.constructionLabel = Header(parent=self.mainGrid, align=uiconst.TOPLEFT, text=text, color=eveColor.SAND_YELLOW)
        progressDict = underConstructionComp.progressDict
        completed = underConstructionComp.completed
        self.ConstructInput(progressDict.keys())
        Button(parent=self.mainGrid, align=uiconst.TOPLEFT, label=GetByLabel('UI/Inflight/SpaceComponents/UnderConstruction/DepositItems'), func=self.OpenConstructionWnd, args=(), top=8)
        self.UpdateProgress(progressDict)
        self.SetConstructionLabel(underConstructionComp.GetEstimatedValueProgress(), completed)
        sm.RegisterNotify(self)

    def _GetComponent(self):
        ballpark = sm.GetService('michelle').GetBallpark()
        underConstructionComp = ballpark.componentRegistry.GetComponentForItem(self._itemID, UNDER_CONSTRUCTION)
        return underConstructionComp

    def ConstructInput(self, inputTypeIDs):
        grid = LayoutGrid(parent=self.mainGrid, align=uiconst.TOPLEFT, columns=len(inputTypeIDs), cellSpacing=(8, 8), top=self.constructionLabel.top + self.constructionLabel.height)
        for typeID in sorted(inputTypeIDs):
            inputCont = InputTypeCont(parent=grid, typeID=typeID)
            self.inputContsByTypeID[typeID] = inputCont

    def OpenConstructionWnd(self, *args):
        sm.GetService('menu').OpenUnderConstruction(self._itemID)

    def OnUnderConstructionUpdated(self, itemID, progressDict, totalProgress, completed):
        if self._itemID != itemID:
            return
        self.UpdateProgress(progressDict)
        self.SetConstructionLabel(totalProgress, completed)

    def SetConstructionLabel(self, totalProgress, completed):
        rounded = round(totalProgress, 3)
        if completed:
            maxValue = 1.0
        else:
            maxValue = 0.999
        percentage = 100 * mathext.clamp(rounded, 0, maxValue)
        text = GetByLabel('UI/Inflight/UnderConstructionProgress', progress=percentage)
        self.constructionLabel.text = text

    def UpdateProgress(self, progressDict):
        for typeID, progress in progressDict.iteritems():
            inputCont = self.inputContsByTypeID.get(typeID, None)
            if not inputCont:
                continue
            inputCont.UpdateProgress(progress)


class InputTypeCont(Container):
    default_height = 32
    default_width = 32
    default_align = uiconst.CENTER
    default_state = uiconst.UI_DISABLED

    def ApplyAttributes(self, attributes):
        super(InputTypeCont, self).ApplyAttributes(attributes)
        Fill(bgParent=self, color=eveColor.TUNGSTEN_GREY, opacity=0.05)
        self._typeID = attributes.typeID
        self.ConstructUI()

    def ConstructUI(self):
        self.gauge = Gauge(parent=self, color=eveColor.CRYO_BLUE, align=uiconst.TOBOTTOM, gaugeHeight=1)
        typeIcon = Icon(parent=self, align=uiconst.CENTER, pos=(0,
         0,
         self.width,
         self.height), typeID=self._typeID)

    def UpdateProgress(self, progress):
        self.gauge.SetValue(progress)
