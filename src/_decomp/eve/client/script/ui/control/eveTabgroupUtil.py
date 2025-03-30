#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\eveTabgroupUtil.py
import localization

def FixedTabName(tabNamePath):
    enText = localization.GetByLabel(tabNamePath, localization.const.LOCALE_SHORT_ENGLISH)
    text = localization.GetByLabel(tabNamePath)
    return (enText, text)
