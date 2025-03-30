#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\tacticalNavigation\navigationBracket.py
import tacticalNavigation.ui.util as tacticalui
import carbonui.const as uiconst
from carbonui.primitives.bracket import Bracket
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
NAVIGATION_BRACKET_PATH = 'res:/ui/texture/classes/bracket/selectioncircle.png'
BRACKET_SIZE = 24

class NavigationPointBracket(Bracket):
    __guid__ = 'uicls.NavigationPointBracket'

    def ApplyAttributes(self, attributes):
        Bracket.ApplyAttributes(self, attributes)
        color = tacticalui.ColorCombination(tacticalui.COLOR_MOVE, tacticalui.ALPHA_HIGH)
        Sprite(parent=self, width=attributes.width, height=attributes.height, texturePath=NAVIGATION_BRACKET_PATH, state=uiconst.UI_DISABLED, color=color, align=uiconst.CENTER)

    @staticmethod
    def Create(trackingCurve):
        bracket = NavigationPointBracket(parent=uicore.layer.bracket, curveSet=uicore.uilib.bracketCurveSet, align=uiconst.ABSOLUTE, width=BRACKET_SIZE, height=BRACKET_SIZE, state=uiconst.UI_DISABLED)
        bracket.trackBall = trackingCurve
        return bracket
