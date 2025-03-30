#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\structureSettings\uiSettingUtil.py
from carbonui import const as uiconst
from carbonui.control.singlelineedits.singleLineEditFloat import SingleLineEditFloat
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from localization import GetByLabel
import structures
from carbon.common.script.util.format import FmtAmt

def GetUnit(settingType):
    if settingType == structures.SETTINGS_TYPE_PERCENTAGE:
        return '%'
    if settingType == structures.SETTINGS_TYPE_ISK:
        return ' %s' % GetByLabel('UI/Common/ISK')
    return ''


def AddValueEdit(parent, sgController, callback):
    settingType = sgController.GetSettingType()
    unit = GetUnit(settingType)
    hint = GetByLabel('UI/StructureSettingWnd/PerOzoneUnitConsumed') if sgController.GetSettingID() == structures.SETTING_JUMP_BRIDGE_ACTIVATION else ''
    settingInfo = sgController.GetSettingInfo()
    valueRange = settingInfo.valueRange
    minValue, maxValue = valueRange
    value = sgController.GetValue()
    if settingType in (structures.SETTINGS_TYPE_INT, structures.SETTINGS_TYPE_ISK):
        amountEdit = SinglelineEditIntegerWithUnit(name='amountEdit', parent=parent, align=uiconst.CENTERRIGHT, OnChange=callback, unit=unit, hint=hint, minValue=minValue, maxValue=maxValue, pos=(4, 0, 60, 0))
        value = int(value)
        decimals = 0
    else:
        decimals = 1
        if settingInfo.decimals is not None:
            decimals = settingInfo.decimals
        amountEdit = SinglelineEditFloatWithUnit(name='amountEdit', parent=parent, align=uiconst.CENTERRIGHT, OnChange=callback, unit=unit, hint=hint, minValue=minValue, maxValue=maxValue, pos=(4, 0, 60, 0), decimalPlaces=decimals)
        value = float(value)
    amountEdit.SetValue(value)
    labelClass = amountEdit.textLabel.__class__
    maxText = '%s %s' % (FmtAmt(float(maxValue), showFraction=decimals), unit)
    labelWidth, labelHeight = labelClass.MeasureTextSize(maxText)
    maxWidth = labelWidth + 2 * amountEdit._textClipper.padLeft + 20
    newWidth = max(maxWidth, amountEdit.width)
    amountEdit.width = newWidth
    return amountEdit


class SinglelineEditFloatWithUnit(SingleLineEditFloat):

    def ApplyAttributes(self, attributes):
        self.unit = attributes.unit
        super(SinglelineEditFloatWithUnit, self).ApplyAttributes(attributes)

    def SetText(self, text, format = True):
        super(SinglelineEditFloatWithUnit, self).SetText(text, format)
        if self.unit:
            self.textLabel.text += ' %s ' % self.unit


class SinglelineEditIntegerWithUnit(SingleLineEditInteger):

    def ApplyAttributes(self, attributes):
        self.unit = attributes.unit
        super(SinglelineEditIntegerWithUnit, self).ApplyAttributes(attributes)

    def SetText(self, text, format = True):
        super(SinglelineEditIntegerWithUnit, self).SetText(text, format)
        if self.unit:
            self.textLabel.text += '%s' % self.unit
