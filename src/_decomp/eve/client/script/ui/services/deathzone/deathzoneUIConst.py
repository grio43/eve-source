#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\deathzone\deathzoneUIConst.py
from carbonui.util.color import Color
from enum import Enum
_LocalUIState = Enum('LocalUIState', ['SAFE_ZONE',
 'DEATH_ZONE',
 'DEATH_ZONE_GRACE_PERIOD',
 'UNSPECIFIED'])
DEATHZONE_VIGNETTE_PARAMS = {('VignetteColor', 'color'): Color(255, 40, 11).GetRGBA(),
 ('VignetteDetail1Scroll', 'detail1Scroll'): (0.1, -0.8),
 ('VignetteDetail1Size', 'detail1Size'): (14.0, 14.0),
 ('VignetteDetail2Scroll', 'detail2Scroll'): (0.3, -0.9),
 ('VignetteDetail2Size', 'detail2Size'): (16.0, 16.0),
 ('VignetteDetailPath', 'detailPath'): 'res:/Texture/FX/Gradients/XGrad_01a.dds',
 ('VignetteOpacity', 'opacity'): 1.0,
 ('VignetteShapePath', 'shapePath'): 'res:/Texture/FX/Gradients/BorderMask_01a.dds',
 ('VignetteSineFrequency', 'sineFrequency'): 1.0,
 ('VignetteSineMaximum', 'sineMaximum'): 1.0,
 ('VignetteSineMinimum', 'sineMinimum'): 0.33}
