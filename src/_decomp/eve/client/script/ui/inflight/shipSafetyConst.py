#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\shipSafetyConst.py
from collections import namedtuple
from eve.client.script.ui.crimewatch import crimewatchConst
from eve.common.script.sys.idCheckers import IsZarzakh

class SafetyLevelData(object):

    def __init__(self, color, safetySelectionHint, safetySelectionHintLocked, hintText, buttonText, audioEvent, safetySelectionHintRetribution = None, safetySelectionHintLockedRetribution = None):
        self.color = color
        self.safetySelectionHint = safetySelectionHint
        self.safetySelectionHintLocked = safetySelectionHintLocked
        self.hintText = hintText
        self.buttonText = buttonText
        self.audioEvent = audioEvent
        self.safetySelectionHintRetribution = safetySelectionHintRetribution
        self.safetySelectionHintLockedRetribution = safetySelectionHintLockedRetribution

    def GetSafetySelectionHint(self):
        return self.safetySelectionHint

    def GetSafetySelectionHintLocked(self):
        return self.safetySelectionHintLocked


BUTTON_FILL_NORMAL = (0.15, 0.15, 0.15, 1)
BUTTON_FILL_HILIGHT = (0.25, 0.25, 0.25, 1)
OPACITY_BG = 0.8
TEXT_PADDING = 8
DOCK_POINTER_LENGTH = 15
DOCK_MARGIN = 8
DESELECTED_BUTTON_OPACITY = 0.3
HINT_DELAY = 800
SAFETY_LEVEL_DATA_MAP = {const.shipSafetyLevelFull: SafetyLevelData(crimewatchConst.Colors.Green, 'UI/Crimewatch/SafetyLevel/SafetyButtonFullOptionHint', 'UI/Crimewatch/SafetyLevel/SafetyButtonFullOptionHintLocked', 'UI/Crimewatch/SafetyLevel/SafetyButtonFullHint', 'UI/Crimewatch/SafetyLevel/SafetyButtonFull', 'crimewatch_on_play'),
 const.shipSafetyLevelPartial: SafetyLevelData(crimewatchConst.Colors.Yellow, 'UI/Crimewatch/SafetyLevel/SafetyButtonPartialOptionHint', 'UI/Crimewatch/SafetyLevel/SafetyButtonPartialOptionHintLocked', 'UI/Crimewatch/SafetyLevel/SafetyButtonPartialHint', 'UI/Crimewatch/SafetyLevel/SafetyButtonPartial', 'crimewatch_partial_play', 'UI/Crimewatch/SafetyLevel/SafetyButtonPartialOptionRetributionHint', 'UI/Crimewatch/SafetyLevel/SafetyButtonPartialOptionRetributionHintLocked'),
 const.shipSafetyLevelNone: SafetyLevelData(crimewatchConst.Colors.Red, 'UI/Crimewatch/SafetyLevel/SafetyButtonNoneOptionHint', 'UI/Crimewatch/SafetyLevel/SafetyButtonNoneOptionHintLocked', 'UI/Crimewatch/SafetyLevel/SafetyButtonNoneHint', 'UI/Crimewatch/SafetyLevel/SafetyButtonNone', 'crimewatch_off_play', 'UI/Crimewatch/SafetyLevel/SafetyButtonNoneOptionRetributionHint')}
