#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\shipHud\systemWideEffectButton.py
import evetypes
import infobubbles
import localization
import trinity
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from carbonui.util.color import Color
from dogma import units
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.inflight.shipHud.buffButtons import SLOT_WIDTH, ICON_SIZE
COLOR_TEXT_HILITE = (1.0, 1.0, 1.0, 1.0)
COLOR_GREEN = (0.0, 0.8, 0.0, 1.0)
COLOR_RED = (0.875, 0.102, 0.137, 1.0)
COLOR_TEXT_HILITE_HEX = Color.RGBtoHex(*COLOR_TEXT_HILITE)
COLOR_GREEN_HEX = Color.RGBtoHex(*COLOR_GREEN)
COLOR_RED_HEX = Color.RGBtoHex(*COLOR_RED)

class SystemWideEffectSlotParent(Container):
    default_align = uiconst.TOLEFT
    default_width = SLOT_WIDTH
    default_height = ICON_SIZE

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.btn = SystemWideEffectButton(parent=self, align=uiconst.CENTER, width=ICON_SIZE, height=ICON_SIZE, sourceTypeID=attributes.sourceTypeID)
        self.FadeButtonIn()

    def FadeButtonIn(self):
        uicore.animations.FadeIn(self, duration=0.25)
        uicore.animations.MorphScalar(self, 'width', startVal=0, endVal=SLOT_WIDTH, duration=0.25)


class SystemWideEffectButton(Container):
    __guid__ = 'BuffButton'
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.RELATIVE
    default_pickRadius = -1
    ICON_BASE_ALPHA = 1.0
    ICON_HIGHLIGHTED_ALPHA = 1.5
    ICON_COLOR = (1.0,
     1.0,
     1.0,
     ICON_BASE_ALPHA)
    SLOT_COLOR = (1.0, 1.0, 1.0, 1)
    SLOT_TEXTURE_PATH = 'res:/UI/Texture/classes/ShipUI/EwarBar/ewarBarUnderlayClean.png'
    SLOT_GRADIENT_TEXTURE_PATH = 'res:/UI/Texture/classes/ShipUI/EwarBar/ewarBarUnderlayGrad.png'
    SLOT_BASE_ALPHA = 0.2
    SLOT_GRADIENT_ALPHA = 0.25
    SHADOW_COLOR = (1.0, 1.0, 1.0, 0.25)
    SHADOW_TEXTURE_PATH = 'res:/UI/Texture/classes/ShipUI/EwarBar/ewarBarShadow.png'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.sourceTypeID = attributes.sourceTypeID
        iconSize = self.height
        self.icon = Icon(parent=self, name='SystemEffecticon', pos=(0,
         0,
         iconSize,
         iconSize), align=uiconst.CENTER, state=uiconst.UI_DISABLED, ignoreSize=1, color=self.ICON_COLOR)
        Sprite(parent=self, name='effect_slot_gradient', align=uiconst.TOALL, state=uiconst.UI_DISABLED, color=self.SLOT_COLOR, blendMode=trinity.TR2_SBM_ADD, texturePath=self.SLOT_GRADIENT_TEXTURE_PATH, opacity=self.SLOT_GRADIENT_ALPHA)
        Sprite(parent=self, name='effect_slot_base', align=uiconst.TOALL, state=uiconst.UI_DISABLED, color=self.SLOT_COLOR, blendMode=trinity.TR2_SBM_ADD, texturePath=self.SLOT_TEXTURE_PATH, opacity=self.SLOT_BASE_ALPHA)
        Sprite(parent=self, name='effect_shadow', align=uiconst.TOALL, state=uiconst.UI_DISABLED, color=self.SHADOW_COLOR, texturePath=self.SHADOW_TEXTURE_PATH)
        self.LoadIcon(infobubbles.get_icon_id(self.sourceTypeID))

    def LoadIcon(self, graphicID):
        self.icon.LoadIconByIconID(graphicID)

    def GetHint(self):
        return ''

    def LoadTooltipPanel(self, tooltipPanel, *args, **kwds):
        tooltipPanel.LoadGeneric1ColumnTemplate()
        tooltipPanel.cellSpacing = (10, 4)
        self._LoadTooltipPanel(tooltipPanel)
        self._tooltipUpdateTimer = AutoTimer(250, self._LoadTooltipPanel, tooltipPanel)

    def _LoadTooltipPanel(self, tooltipPanel):
        if tooltipPanel.destroyed:
            self._tooltipUpdateTimer = None
            return
        tooltipPanel.Flush()
        misc_bonus = infobubbles.get_misc_bonus(self.sourceTypeID)
        if misc_bonus:
            tooltipPanel.AddLabelLarge(text=evetypes.GetName(self.sourceTypeID), align=uiconst.CENTERLEFT, color=COLOR_TEXT_HILITE)
            for bonus in sorted(misc_bonus, key=lambda x: x['importance']):
                text = self._GetBonusText(bonus)
                tooltipPanel.AddLabelMedium(text=text, align=uiconst.CENTERLEFT)

    def OnMouseEnter(self, *args):
        self.icon.SetAlpha(self.ICON_HIGHLIGHTED_ALPHA)

    def OnMouseExit(self, *args):
        self.icon.SetAlpha(self.ICON_BASE_ALPHA)

    def _GetBonusText(self, data):
        color = COLOR_TEXT_HILITE_HEX
        if 'bonus' in data:
            bonus = float(data['bonus'])
            value = round(bonus, 1)
            if int(bonus) == bonus:
                value = int(bonus)
            if 'isPositive' in data:
                isPositive = data['isPositive']
                if isPositive:
                    color = COLOR_GREEN_HEX
                else:
                    color = COLOR_RED_HEX
            text = localization.GetByLabel('UI/SystemWideEffects/BonusWithNumber', color=color, value=value, unit=units.get_display_name(int(data['unitID'])), bonusText=localization.GetByMessageID(int(data['nameID'])))
        else:
            text = localization.GetByLabel('UI/SystemWideEffects/BonusWithoutNumber', color=color, bonusText=localization.GetByMessageID(int(data['nameID'])))
        return text
