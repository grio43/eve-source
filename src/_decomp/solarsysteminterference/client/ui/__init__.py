#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\solarsysteminterference\client\ui\__init__.py
from localization import GetByLabel
from solarsysteminterference.const import INTERFERENCE_BAND_LABEL_NAMES

def GetInterferenceBandLabel(interferenceBand):
    labelName = INTERFERENCE_BAND_LABEL_NAMES.get(interferenceBand, None)
    if labelName is not None:
        return GetByLabel(labelName)
