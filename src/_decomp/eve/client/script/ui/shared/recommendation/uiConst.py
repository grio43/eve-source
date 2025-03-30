#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\recommendation\uiConst.py
from carbonui.util.color import Color
from eve.client.script.ui import eveColor
MAIN_GREEN = Color.HextoRGBA('#3a4729')
LIGHT_GREEN = Color.HextoRGBA('#6d8e43')
TREATMENT_COMPLETED_COLORS_BTN = (MAIN_GREEN, Color.HextoRGBA('#4a562d'), Color.HextoRGBA('#4a562d'))
TREATMENT_NORMAL_COLORS_BTN = (eveColor.PRIMARY_BLUE, eveColor.CRYO_BLUE, eveColor.PRIMARY_BLUE)
TREATMENT_ACTIVE_COLORS_BTN = (Color.HextoRGBA('#234051'), TREATMENT_NORMAL_COLORS_BTN[1], TREATMENT_NORMAL_COLORS_BTN[2])
MAIN_YELLOW = Color.HextoRGBA('#896807')
LIGHT_YELLOW = Color.HextoRGBA('#b9b29a')
TREATMENT_YELLOW_COLORS_BTN = (Color.HextoRGBA('#3d3412'), Color.HextoRGBA('#5c4709'), Color.HextoRGBA('#5c4709'))
HAS_ACCEPTED = 'Recommendations_hasAcceptedTreatment'
HAS_INTERACTED_WITH = 'Recommendations_HasInteractedWith'
INFO_PANEL_ICON = 'res:/UI/Texture/classes/Treatments/opportunitiesIcon_infoPanel.png'
