#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\util\defaultsetting.py
from carbonui.uicore import uicore
__doc__ = "\n\n    Author:     Fridrik Haraldsson\n    Created:    September 2008\n    Project:    Core\n\n\n    Description:\n\n    This file holds default setting values for the uicore. Similar file should be\n    done in the gameroot to assing default settings for the game. This is done to prevent \n    different defaultvalues in various classes where the setting is being used.\n\n    If you think the setting you are working with doesn't require registered \n    default value then do;\n\n    myval = settings.sectionName.groupName.Get(settingKey, myDefaultValue)\n\n    (c) CCP 2008\n\n"
from itertoolsext import Bundle

class SafeBundle(Bundle):

    def __getattr__(self, item):
        try:
            return Bundle.__getattr__(self, item)
        except (KeyError, AttributeError):
            return None


user = SafeBundle(ui=SafeBundle(language=0))
user.__name__ = 'user'
public = SafeBundle(device=SafeBundle(ditherbackbuffer=1))
public.__name__ = 'public'
char = SafeBundle()
char.__name__ = 'char'
