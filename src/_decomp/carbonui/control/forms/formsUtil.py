#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\forms\formsUtil.py
from eve.client.script.ui import eveColor

def FormatAsIncompleteInput(text):
    return u'{} <color={}>*</color>'.format(text, eveColor.CRYO_BLUE_HEX)
