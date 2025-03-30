#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fastcheckout\client\purchasepanels\purchaseButton.py
from carbonui.fontconst import STYLE_SMALLTEXT
from carbonui.uianimations import animations
from eve.client.script.ui.control.buttons import TextButtonWithBackgrounds, ButtonTextBoldness
from uthread2 import call_after_wallclocktime_delay
BUTTON_HOVER_SOUND = 'ui_icc_button_mouse_over_play'
BUTTON_SELECT_SOUND = 'ui_icc_button_select_play'

class PurchaseButton(TextButtonWithBackgrounds):
    default_mouseUpBGTexture = 'res:/UI/Texture/classes/FastCheckout/buttonAccent_Up.png'
    default_mouseEnterBGTexture = 'res:/UI/Texture/classes/FastCheckout/buttonAccent_Over.png'
    default_mouseDownBGTexture = 'res:/UI/Texture/classes/FastCheckout/buttonAccent_Down.png'
    default_disabledBGTexture = 'res:/UI/Texture/classes/FastCheckout/buttonAccent_Disabled.png'
    default_mouseUpBGColor = None
    default_mouseEnterBGColor = None
    default_mouseDownBGColor = None
    default_disabledBGColor = None
    default_mouseUpTextColor = (0.95, 0.95, 0.95, 1.0)
    default_mouseEnterTextColor = (0.95, 0.95, 0.95, 1.0)
    default_mouseDownTextColor = (0.95, 0.95, 0.95, 1.0)
    default_disabledTextColor = (0.95, 0.95, 0.95, 1.0)
    default_hoverSound = 'ui_icc_button_mouse_over_play'
    default_selectedSound = 'ui_icc_button_select_play'
    default_frameCornerSize = 10
    default_bgFadeInDuration = 0.0
    default_bgFadeOutDuration = 0.0
    default_fontsize = 18
    default_fontStyle = STYLE_SMALLTEXT
    default_boldText = ButtonTextBoldness.ALWAYS_BOLD
    default_isCapitalized = True
    default_letterspace = 1

    def ApplyAttributes(self, attributes):
        super(PurchaseButton, self).ApplyAttributes(attributes)
        self.AdaptWidthToText()

    def AdaptWidthToText(self):
        self.width = max(self.width, self.label.width + 10)


class AnimatedPurchaseButton(PurchaseButton):

    def ApplyAttributes(self, attributes):
        self._is_enabled = False
        self.delayed_hint = attributes.get('delayedHint', None)
        super(PurchaseButton, self).ApplyAttributes(attributes)

    def IsEnabled(self):
        return self._is_enabled and super(AnimatedPurchaseButton, self).IsEnabled()

    def Enable(self, *args):
        super(PurchaseButton, self).Enable(*args)
        self.EnableHint()
        self._is_enabled = True

    def EnableHint(self):
        if self.delayed_hint:
            self.SetHint(self.delayed_hint)

    def FadeIn(self):
        time_offset = 1.5
        call_after_wallclocktime_delay(self.Enable, time_offset)
        animations.FadeIn(self, timeOffset=time_offset)


class SecondaryPurchaseButton(AnimatedPurchaseButton):
    default_mouseUpBGTexture = 'res:/UI/Texture/classes/FastCheckout/buttonStroke_Up.png'
    default_mouseEnterBGTexture = 'res:/UI/Texture/classes/FastCheckout/buttonStroke_Over.png'
    default_mouseDownBGTexture = 'res:/UI/Texture/classes/FastCheckout/buttonStroke_Down.png'
    default_disabledBGTexture = 'res:/UI/Texture/classes/FastCheckout/buttonStroke_Disabled.png'
