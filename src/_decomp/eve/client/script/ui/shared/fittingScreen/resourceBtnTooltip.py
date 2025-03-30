#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\resourceBtnTooltip.py
import carbonui.const as uiconst
from carbonui.control.checkbox import Checkbox
from carbonui.control.radioButton import RadioButton
from localization import GetByLabel

def LoadFilterBtnTooltipPanel(tooltipPanel, hintLabelPath, hwSettingObject, callback, isSimulated):
    tooltipPanel.state = uiconst.UI_NORMAL
    onTotalOutput = hwSettingObject.GetFilterModeForResource()
    if onTotalOutput:
        typeOfFiltering = GetByLabel('UI/Fitting/FittingWindow/FilterResourcesTotal')
    else:
        typeOfFiltering = GetByLabel('UI/Fitting/FittingWindow/FilterResourcesRemaining')
    hintText = GetByLabel(hintLabelPath, typeOfFiltering=typeOfFiltering)
    if not isSimulated:
        hintText += '<br><br>%s' % GetByLabel('UI/Fitting/FittingWindow/OnlyAvailableInSimulation')
    tooltipPanel.LoadGeneric1ColumnTemplate()
    tooltipPanel.AddLabelMedium(text=hintText, wrapWidth=200)
    if isSimulated:
        options = [('UI/Fitting/FittingWindow/FilterResourcesTotalCb', 1), ('UI/Fitting/FittingWindow/FilterResourcesRemainingCb', 0)]

        def ToggleHardwareSetting(*args):
            currentValue = hwSettingObject.GetFilterModeForResource()
            newValue = not currentValue
            hwSettingObject.SetFilterModeForResource(newValue)
            callback()

        for optionLabelPath, optionID in options:
            checkBox = RadioButton(align=uiconst.TOPLEFT, text=GetByLabel(optionLabelPath), checked=optionID == onTotalOutput, wrapLabel=False, callback=ToggleHardwareSetting, retval=optionID, settingsPath=None, groupname='fittingResourcesFilter')
            tooltipPanel.AddCell(cellObject=checkBox, colSpan=tooltipPanel.columns)
