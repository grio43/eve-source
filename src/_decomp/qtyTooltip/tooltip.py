#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\qtyTooltip\tooltip.py
import eveformat
import mathext
from qtyTooltip import qtyConst

def LoadQtyTooltip(tooltipPanel, amount, qtyType):
    tooltipPanel.LoadGeneric1ColumnTemplate()
    text = GetQtyText(amount, qtyType)
    if text is None:
        return
    tooltipPanel.AddLabelMedium(text=text)


def GetQtyText(amount, qtyType):
    if amount < qtyConst.MIN_AMOUNT_TO_DISPLAY_FULL_TEXT:
        return
    if qtyType == qtyConst.EDIT_INPUT_TYPE_ISK:
        text = eveformat.isk_readable(amount)
    else:
        text = eveformat.number_readable(amount)
    rounded_amount = mathext.round_to_significant(amount, significant_digits=3)
    if mathext.is_close(rounded_amount, amount):
        return text
    else:
        return u'{} {}'.format(qtyConst.ABOUT_CHAR, text)


def LoadTooltipForNumber(tooltipPanel, currentHint, amount, inputType = None):
    if inputType is None:
        return
    if currentHint:
        tooltipPanel.AddLabelMedium(text=currentHint)
    if inputType in qtyConst.EDIT_INPUT_TYPES:
        LoadQtyTooltip(tooltipPanel, abs(amount), inputType)


def LoadQtyTooltipPanel(tooltipPanel, value, inputType = qtyConst.EDIT_INPUT_TYPE_FLOAT, normalHint = ''):
    return LoadTooltipForNumber(tooltipPanel, normalHint, value, inputType)
