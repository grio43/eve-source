#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\homestation\client\ui\tooltip.py
from carbonui.primitives.sprite import Sprite
from homestation.client import text
from homestation.client.ui.const import Color, Padding

def load_error_tooltip(panel, errors):
    if not errors:
        return
    panel.LoadGeneric1ColumnTemplate()
    panel.margin = (Padding.normal,
     Padding.normal,
     Padding.normal,
     Padding.normal)
    panel.cellSpacing = (0, Padding.slim)
    for error in errors:
        label = panel.AddLabelMedium(padding=(Padding.normal,
         Padding.slim,
         Padding.normal,
         Padding.slim), wrapWidth=300, text=error, color=Color.warning)
        Sprite(bgParent=label.parent, texturePath='res:/UI/Texture/Classes/Industry/Output/hatchPattern.png', tileX=True, tileY=True, color=Color.warning, opacity=0.15)
