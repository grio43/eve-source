#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\comboEntryData.py
from eve.client.script.ui import eveColor

class BaseComboEntryData(object):

    def __init__(self, label, returnValue = None, hint = None, icon = None, indentLevel = None, iconColor = eveColor.WHITE, loadTooltipFunc = None):
        self.label = label
        self.returnValue = returnValue
        self.hint = hint
        self.icon = icon
        self.indentLevel = indentLevel
        self.iconColor = iconColor
        self.loadTooltipFunc = loadTooltipFunc

    def GetHint(self):
        return self.hint

    def GetLoadTooltipFunc(self):
        return self.loadTooltipFunc


class ComboEntryData(BaseComboEntryData):
    pass


class ComboEntryDataText(BaseComboEntryData):
    pass


class ComboEntryDataCaption(BaseComboEntryData):
    pass


class ComboEntryDataSeparator(BaseComboEntryData):

    def __init__(self):
        super(ComboEntryDataSeparator, self).__init__(label='separator')
