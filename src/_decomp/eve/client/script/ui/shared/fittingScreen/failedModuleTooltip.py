#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\failedModuleTooltip.py
import evetypes
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.util.uix import GetTechLevelIcon
from localization import GetByLabel
import carbonui.const as uiconst

def LoadGetFailedModuleTooltip(tooltipPanel, typeID):
    tooltipPanel.columns = 3
    tooltipPanel.margin = (4, 4, 4, 4)
    tooltipPanel.cellPadding = 0
    tooltipPanel.cellSpacing = 0
    tooltipPanel.labelPadding = (4, 2, 4, 2)
    tooltipPanel.SetBackgroundAlpha(0.75)
    iconSize = 26
    minRowSize = 30
    text = GetByLabel('UI/Fitting/FittingWindow/CouldNotLoadModule')
    labelObj = tooltipPanel.AddLabelMedium(text=text, align=uiconst.CENTERLEFT, cellPadding=tooltipPanel.labelPadding, colSpan=tooltipPanel.columns)
    tooltipPanel.AddSpacer(height=minRowSize, width=0)
    iconCont = Container(pos=(0,
     0,
     iconSize,
     iconSize), align=uiconst.CENTER)
    iconObj = Icon(parent=iconCont, pos=(0,
     0,
     iconSize,
     iconSize), align=uiconst.TOPLEFT, ignoreSize=True)
    iconObj.LoadIconByTypeID(typeID, size=iconSize, ignoreSize=True)
    techIcon = Icon(parent=iconCont, width=16, height=16, align=uiconst.TOPLEFT, idx=0, top=0)
    GetTechLevelIcon(techIcon, typeID=typeID)
    tooltipPanel.AddCell(iconCont, cellPadding=2)
    typeText = '<b>%s</b>' % evetypes.GetName(typeID)
    labelObj = tooltipPanel.AddLabelMedium(text=typeText, align=uiconst.CENTERLEFT, cellPadding=tooltipPanel.labelPadding)
