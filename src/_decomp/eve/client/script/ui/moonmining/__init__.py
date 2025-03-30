#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\moonmining\__init__.py
import evetypes
import gametime
from carbon.common.lib.const import HOUR, SEC
from carbonui.util.color import Color
from dogma.const import attributeExtractionYieldMultiplier
from eveservices.scheduling import GetSchedulingService
from inventorycommon.typeHelpers import GetAveragePrice
from localization import GetByLabel
from moonmining.const import MAXIMUM_EXTRACTION_DURATION
DAY_NAME_TEXT = [GetByLabel('/Carbon/UI/Common/Days/Sunday'),
 GetByLabel('/Carbon/UI/Common/Days/Monday'),
 GetByLabel('/Carbon/UI/Common/Days/Tuesday'),
 GetByLabel('/Carbon/UI/Common/Days/Wednesday'),
 GetByLabel('/Carbon/UI/Common/Days/Thursday'),
 GetByLabel('/Carbon/UI/Common/Days/Friday'),
 GetByLabel('/Carbon/UI/Common/Days/Saturday')]
DAY_NAME_TEXT_SHORT = [GetByLabel('UI/Moonmining/SundayShort'),
 GetByLabel('UI/Moonmining/MondayShort'),
 GetByLabel('UI/Moonmining/TuesdayShort'),
 GetByLabel('UI/Moonmining/WednesdayShort'),
 GetByLabel('UI/Moonmining/ThursdayShort'),
 GetByLabel('UI/Moonmining/FridayShort'),
 GetByLabel('UI/Moonmining/SaturdayShort')]
COLOR_IN_PROGRESS = (0.8, 0, 0, 1.0)
COLOR_READY = (0.46, 0.85, 1.0, 1.0)
COLOR_RECALIBRATING = (0.95, 0.6, 0.14, 1.0)
COLOR_STOPPED = (1.0, 1.0, 1.0, 1.0)
COLOR_FRACTURE = (0.24, 0.67, 0.16, 1.0)
STAGE_STOPPED = 1
STAGE_CALIBRATING = 2
STAGE_IN_PROGRESS = 3
STAGE_READY = 4
STAGE_FRACTURING = 5
NUM_HOURS_IN_BLOCK = 4
NUM_HOURS_ZOOMER = 96
HOUR_WIDTH_ZOOMER = 5
PARTS_IN_HOUR = 2
VULNERABILITY_COLOR = COLOR_RECALIBRATING[:3] + (0.75,)

def GetPrice(typeID, qty):
    price = GetAveragePrice(typeID) or evetypes.GetBasePrice(typeID) or 0
    return price * qty


def GetOreColor(typeID):
    colors = [(0.1, 0.37, 0.55, 1.0),
     (0.55, 0.1, 0.1, 1.0),
     (0.45, 0.45, 0.45, 1.0),
     (0.55, 0.37, 0.1, 1.0)]
    return colors[typeID % 4]


def GetRangeTimeForSlider():
    now = gametime.GetWallclockTime()
    timeInBlcok = NUM_HOURS_IN_BLOCK * HOUR
    startTime = now + (timeInBlcok - now % timeInBlcok)
    maxTime = now + MAXIMUM_EXTRACTION_DURATION * SEC
    return (startTime, maxTime)


def GetExtractionStage(extraction):
    if not extraction:
        return STAGE_STOPPED
    if extraction.chunkAvailableTime > gametime.GetWallclockTime():
        return STAGE_IN_PROGRESS
    laserFiredTimestamp = GetSchedulingService().GetLaserFiredTimestamp()
    if laserFiredTimestamp:
        return STAGE_FRACTURING
    return STAGE_READY


def GetColorAndStatusTextForExtraction(extraction):
    currentStage = GetExtractionStage(extraction)
    if currentStage == STAGE_READY:
        text = GetByLabel('UI/Moonmining/ExtractionReadyStatus')
        helpText = GetByLabel('UI/Moonmining/ExtractionReadyStatusHint')
        statusColor = COLOR_READY
    elif currentStage == STAGE_FRACTURING:
        text = GetByLabel('UI/Moonmining/ExtractionFracturingStatus')
        helpText = GetByLabel('UI/Moonmining/ExtractionFracturingStatusHint')
        statusColor = COLOR_FRACTURE
    elif currentStage == STAGE_IN_PROGRESS:
        text = GetByLabel('UI/Moonmining/ExtractionInProgress')
        helpText = GetByLabel('UI/Moonmining/ExtractionInProgressHint')
        statusColor = COLOR_IN_PROGRESS
    else:
        text = GetByLabel('UI/Moonmining/ExtrationStoppedStatus')
        helpText = GetByLabel('UI/Moonmining/ExtrationStoppedStatusHint')
        statusColor = COLOR_STOPPED
    return (text, helpText, statusColor)


def GetTextColor(color, maximumSaturation = 0.3):
    c = Color(*color)
    currentSaturation = c.GetSaturation()
    if currentSaturation < maximumSaturation:
        return color
    return c.SetSaturation(maximumSaturation).GetRGBA()


def GetYieldMultiplier(structureID):
    dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
    yieldMultiplier = dogmaLocation.GetAttributeValue(structureID, attributeExtractionYieldMultiplier)
    return yieldMultiplier
