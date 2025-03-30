#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\factionalWarfare\enlistmentFlow\infoPicker.py
from carbonui import TextBody, TextColor
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
import carbonui.const as uiconst
from carbonui.primitives.layoutGrid import LayoutGrid
import eve.client.script.ui.shared.factionalWarfare.enlistmentFlow.enlistmentUtil as enlistmentUtil
from eve.client.script.ui.control.toggleButtonGroupCircular import ToggleButtonGroupCircular
from eve.client.script.ui.shared.factionalWarfare.enlistmentFlow.enlistmentConst import INFO_MAX_WIDTH
from localization import GetByLabel
BUTTON_SIZE = 32

class InfoPickerCont(ContainerAutoSize):
    default_align = uiconst.TOTOP
    default_name = 'infoPicker'
    default_maxWidth = INFO_MAX_WIDTH

    def ApplyAttributes(self, attributes):
        super(InfoPickerCont, self).ApplyAttributes(attributes)
        self.factionID = None
        self.selectedInfo = enlistmentUtil.INFO_1
        self.grid = LayoutGrid(parent=self, align=uiconst.TOTOP, columns=2, padTop=24)
        self.grid.AddCell(cellObject=Container(name='spacer', align=uiconst.TOPLEFT, width=0))
        self.grid.AddCell(cellObject=Container(name='spacer', align=uiconst.TOPLEFT, width=INFO_MAX_WIDTH))
        self.textHeightSpacer = Container(parent=self.grid, name='spacer', align=uiconst.TOPLEFT, width=0)
        self.infoLabel = TextBody(parent=self.grid, align=uiconst.TOPLEFT, text='', maxWidth=INFO_MAX_WIDTH, color=TextColor.SECONDARY)
        self.buttonCont = ContainerAutoSize(align=uiconst.CENTER)
        self.grid.AddCell(self.buttonCont, colSpan=2)
        self.toggleBtnGroup = ToggleButtonGroupCircular(name='toggleBtnGroup', parent=self.buttonCont, align=uiconst.TOPLEFT, callback=self.OnToggleBtnClicked)
        self.LoadIcons()
        btnID = enlistmentUtil.INFO_ICONS[0][0]
        self.toggleBtnGroup.SelectByID(btnID)

    def LoadIcons(self):
        for infoConst, texturePath, hintLabelPath in enlistmentUtil.INFO_ICONS:
            self.toggleBtnGroup.AddButton(btnID=infoConst, iconPath=texturePath, iconSize=16, btnSize=32, hint=GetByLabel(hintLabelPath))

    def OnToggleBtnClicked(self, btnID, oldBtnID):
        self.ClickIcon(btnID)

    def ClickIcon(self, infoConst):
        self.selectedInfo = infoConst
        self.LoadInfo()

    def UpdateFaction(self, factionID):
        self.factionID = factionID
        self.LoadInfo()

    def LoadInfo(self):
        infoLabelPath = enlistmentUtil.GetInfoLabelPath(self.factionID, self.selectedInfo)
        self.textHeightSpacer.height = self.FindMaxTextHeight(self.factionID)
        text = GetByLabel(infoLabelPath) if infoLabelPath else ''
        self.infoLabel.text = text

    def FindMaxTextHeight(self, factionID):
        if not factionID:
            return 0
        maxHeight = 0
        for labelPath in enlistmentUtil.INFO_BY_FACTION_ID[factionID].itervalues():
            textwidth, textHeight = TextBody.MeasureTextSize(GetByLabel(labelPath), maxWidth=INFO_MAX_WIDTH)
            maxHeight = max(maxHeight, textHeight)

        return maxHeight + 2
