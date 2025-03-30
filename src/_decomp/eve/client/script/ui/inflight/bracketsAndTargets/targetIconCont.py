#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\bracketsAndTargets\targetIconCont.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore

class TargetIconCont(Container):
    default_align = uiconst.CENTERLEFT
    default_width = 18
    default_height = 18
    default_iconSize = 18
    default_name = 'targetIconCont'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.iconSize = attributes.get('iconSize', self.default_iconSize)
        self.targetSprite = None
        self.targetingSprite = None

    def HandleTargetedChanges(self, newState):
        if newState == 0 and self.targetSprite:
            self.targetSprite.Close()
        elif newState == 1:
            self.SetTargetedIcon()

    def HandleTargetingChanges(self, newState):
        print 'newState = ', newState
        if newState == 0 and self.targetingSprite:
            self.targetingSprite.Close()
        elif newState == 1:
            self.StartTargeting()

    def SetTargetedIcon(self):
        if self.targetSprite is None or self.targetSprite.destroyed:
            self.targetSprite = Sprite(parent=self, name='targetSprite', pos=(0,
             0,
             self.iconSize,
             self.iconSize), align=uiconst.CENTERLEFT, texturePath='res:/UI/Texture/classes/Bracket/activeTarget.png')
        self.targetSprite.Show()

    def StartTargeting(self):
        if self.targetSprite:
            self.targetSprite.Hide()
        if self.targetingSprite is None or self.targetingSprite.destroyed:
            self.targetingSprite = Container(name='targeting', align=uiconst.CENTER, pos=(0, 0, 22, 22), parent=self)
            Frame(parent=self.targetingSprite, texturePath='res:/UI/Texture/classes/Bracket/targetFrame.png', opacity=0.75)
            for attrName in ('width', 'height'):
                uicore.animations.MorphScalar(self.targetingSprite, attrName, startVal=22, endVal=12, duration=0.4, loops=uiconst.ANIM_REPEAT)
