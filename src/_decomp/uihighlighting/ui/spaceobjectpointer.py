#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uihighlighting\ui\spaceobjectpointer.py
from collections import namedtuple
import blue
import carbonui.const as uiconst
from carbonui.primitives.bracket import Bracket
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite, StreamingVideoSprite
from carbonui.primitives.vectorline import VectorLine
from eve.client.script.ui.control.eveIcon import Icon
from evetypes import GetName
from geo2 import Vec2Length, Vec2Add, Vec2Subtract, Scale
from localization import GetByLabel, GetByMessageID
from trinity import CreateBinding, TR2_SFX_COPY, TR2_SFX_COLOROVERLAY, TR2_SBM_BLEND, TR2_SBM_ADD
import uthread2
from uihighlighting import uihighlightaudio
from uihighlighting.ui.uipointer import UiPointer, UIPOINTER_HEIGHT
from carbonui.uicore import uicore
UIPOINTER_WIDTH = 220
ICON_SIZE = 48
ICON_PADDING = 8
FLOATING_DISTANCE = 48
ACCELERATION = 6.0
MAX_SPEED = 10.0
SLOWDOWN_DISTANCE = 100
MAX_ELAPSED_TIME = 0.1
DOCK_MARGIN = 20
CASE1 = 1 << 0
CASE2 = 1 << 1
CASE3 = 1 << 2
CASE4 = 1 << 3
CASE5 = 1 << 4
CASE6 = 1 << 5
CASE7 = 1 << 6
CASE8 = 1 << 7
CASE9 = 1 << 8
X_LEFT = CASE1 | CASE4 | CASE6
X_MIDDLE = CASE2 | CASE9 | CASE7
X_RIGHT = CASE3 | CASE5 | CASE8
Y_TOP = CASE1 | CASE2 | CASE3
Y_MIDDLE = CASE4 | CASE9 | CASE5
Y_BOTTOM = CASE6 | CASE7 | CASE8
BRACKET_TO_BOX_LINE_COLOR = (172 / 255.0,
 213 / 255.0,
 241 / 255.0,
 1.0)
BRACKET_TO_BOX_LINE_WIDTH = 0.8
BRACKET_SIZE = 16
BRACKET_SPRITE_SIZE = 100
BRACKET_INTRO_VIDEO = 'res:/UI/Texture/classes/HighlightTool/HighlightRing_Intro.webm'
BRACKET_LOOP_VIDEO = 'res:/UI/Texture/classes/HighlightTool/HighlightRing_Loop.webm'
BRACKET_GLOW_TEXTURE = 'res:/UI/Texture/classes/HighlightTool/highlightRingGlow.png'
SpaceObjectUiPointerData = namedtuple('SpaceObjectUiPointerData', 'typeID, groupID, itemID, message, hint, audioSetting, localize, showBox, highlightBracket')

class SpaceObjectPointer(object):

    def __init__(self, slimItem, pointerData):
        dunObjectNameID = getattr(slimItem, 'dunObjectNameID', None)
        targetBall = sm.GetService('michelle').GetBallpark().GetBall(slimItem.itemID)
        self.typeID = slimItem.typeID
        self.groupID = slimItem.groupID
        self.itemID = targetBall.id
        self.dunObjectID = getattr(slimItem, 'dunObjectID', None)
        self.dunEntityGroupID = getattr(slimItem, 'entityGroupID', None)
        self.destroyed = False
        localize = getattr(pointerData, 'localize', True)
        title = self._GetTitleLabelText(self.typeID, dunObjectNameID)
        message = self._ReadMessage(pointerData.message, localize) or ''
        hint = self._ReadMessage(pointerData.hint, localize)
        audioSetting = pointerData.audioSetting
        if audioSetting and sm.GetService('michelle').GetBall(self.itemID) is not None:
            uihighlightaudio.manager.play_highlight_appeared_sound()
        self.showBox = pointerData.showBox and message
        self.showBracket = pointerData.highlightBracket
        if self.showBracket:
            self._CreateBracket(targetBall)
        if self.showBox and self.showBracket:
            self._CreateBox(title, message, hint)
            self._CreateBoxToBracketLine()
            self._CreateBindings()
        else:
            self.floatingBox = None

    def _ReadMessage(self, message, localize):
        if localize:
            if message:
                return GetByLabel(message)
            return None
        return message

    def _GetTitleLabelText(self, typeID, dunObjectNameID):
        if dunObjectNameID:
            return GetByMessageID(dunObjectNameID)
        return GetName(typeID)

    def _CreateBracket(self, targetBall):
        self.bracket = SpaceObjectUiPointerBracket(parent=uicore.layer.bracket, name='SpaceObjectUiPointerBracket')
        self.bracket.trackBall = targetBall
        blue.pyos.synchro.Yield()

    def _CreateBox(self, title, message, hint):
        self.floatingBox = SpaceObjectFloatingBox(name='SpaceObjectUiPointerBox', parent=uicore.layer.abovemain, align=uiconst.TOPLEFT, title=title, text=message, hint=hint, pos=(0,
         0,
         UIPOINTER_WIDTH,
         UIPOINTER_HEIGHT), state=uiconst.UI_DISABLED, itemID=self.itemID, typeID=self.typeID)
        self.floatingBox.ConstructContent()
        self.floatingBox.onOpacityChanged.connect(self.OnOpacityChanged)

    def _CreateBoxToBracketLine(self):
        self.line = VectorLine(widthFrom=BRACKET_TO_BOX_LINE_WIDTH, widthTo=BRACKET_TO_BOX_LINE_WIDTH, translationFrom=(0, 0), translationTo=(10, 10), parent=self.floatingBox, name='spaceObjectBracketPointer', left=self.floatingBox.width / 2, top=self.floatingBox.height / 2, color=BRACKET_TO_BOX_LINE_COLOR, align=uiconst.TOPLEFT)

    def _CreateBindings(self):
        cs = uicore.uilib.bracketCurveSet
        self.bindings = []
        self.bindings.append(CreateBinding(cs, self.bracket.renderObject, 'displayX', None, ''))
        self.bindings.append(CreateBinding(cs, self.bracket.renderObject, 'displayY', None, ''))
        self.bindings.append(CreateBinding(cs, self.floatingBox.renderObject, 'displayX', None, ''))
        self.bindings.append(CreateBinding(cs, self.floatingBox.renderObject, 'displayY', None, ''))
        for binding in self.bindings:
            binding.copyValueCallable = self.Update

        self.lastUpdateTime = blue.os.GetSimTime()
        self.speed = 0.0

    def CalcVectorTo(self, contA, contB):
        x0, y0 = self.GetContainerPosition(contA)
        x1, y1 = self.GetContainerPosition(contB)
        return (x1 - x0, y1 - y0)

    def GetContainerPosition(self, cont):
        x = cont.left + cont.width / 2
        y = cont.top + cont.height / 2
        if cont is self.bracket:
            l, r = uicore.layer.sidePanels.GetSideOffset()
            x += l
        return (x, y)

    def UpdateBoxPosition(self):
        t = blue.os.GetSimTime()
        vx, vy = self.CalcVectorTo(self.floatingBox, self.bracket)
        distToBox = self.DistanceFromPointToBox(self.GetContainerPosition(self.bracket), self.floatingBox)
        diff = distToBox - FLOATING_DISTANCE
        absDiff = abs(diff)
        ratio = 1.0
        if absDiff < 15.0:
            self.speed = 0
            return
        if absDiff < SLOWDOWN_DISTANCE:
            ratio = absDiff / SLOWDOWN_DISTANCE
        elapsedTime = min(MAX_ELAPSED_TIME, float(t - self.lastUpdateTime) / const.SEC)
        change = ACCELERATION * elapsedTime
        self.speed = min(self.speed + change, MAX_SPEED * ratio)
        x = vx / diff * self.speed
        y = vy / diff * self.speed
        box = self.floatingBox
        box.left += x
        box.top += y
        left, top, width, height = uicore.layer.bracket.GetAbsolute()
        xMin, xMax = left + DOCK_MARGIN, left + width - box.width - DOCK_MARGIN
        yMin, yMax = top + DOCK_MARGIN, height - box.height - top - DOCK_MARGIN
        if box.left < xMin:
            box.left = xMin
        elif box.left > xMax:
            box.left = xMax
        if box.top < yMin:
            box.top = yMin
        elif box.top > yMax:
            box.top = yMax
        self.lastUpdateTime = t

    def Update(self, *args):
        if not self.showBracket:
            return
        t = blue.os.GetSimTime()
        if t == self.lastUpdateTime or self.destroyed:
            return
        if sm.GetService('michelle').GetBall(self.itemID) is None:
            uthread2.start_tasklet(self.FlushPointer)
            return
        if self.showBox:
            self.UpdateBoxPosition()
        bracketPos = self.GetContainerPosition(self.bracket)
        boxPos = self.GetContainerPosition(self.floatingBox)
        lineTo = self.GetLineConnectionPointOnBox(bracketPos, self.floatingBox)
        cornerPos = Vec2Add(boxPos, lineTo)
        vec = Vec2Subtract(bracketPos, cornerPos)
        length = Vec2Length(vec)
        vec = Scale(vec, (length - ICON_SIZE / 2) / length)
        self.line.translationTo = Vec2Add(vec, lineTo)
        self.line.translationFrom = lineTo

    def GetAABB(self, box):
        xMin = box.left
        xMax = xMin + box.width
        yMin = box.top
        yMax = yMin + box.height
        return (xMin,
         xMax,
         yMin,
         yMax)

    def ClassifyPointNearBox(self, point, box):
        x, y = point
        xMin, xMax, yMin, yMax = self.GetAABB(box)
        if x < xMin:
            case = X_LEFT
        elif xMax < x:
            case = X_RIGHT
        else:
            case = X_MIDDLE
        if y < yMin:
            case &= Y_TOP
        elif yMax < y:
            case &= Y_BOTTOM
        else:
            case &= Y_MIDDLE
        return case

    def DistanceFromPointToBox(self, point, box):
        case = self.ClassifyPointNearBox(point, box)
        x, y = point
        xMin, xMax, yMin, yMax = self.GetAABB(box)
        if case == CASE1:
            boxPoint = (xMin, yMin)
        elif case == CASE2:
            boxPoint = (x, yMin)
        elif case == CASE3:
            boxPoint = (xMax, yMin)
        elif case == CASE4:
            boxPoint = (xMin, y)
        elif case == CASE5:
            boxPoint = (xMax, y)
        elif case == CASE6:
            boxPoint = (xMin, yMax)
        elif case == CASE7:
            boxPoint = (x, yMax)
        elif case == CASE8:
            boxPoint = (xMax, yMax)
        elif case == CASE9:
            return 0.0
        return Vec2Length(Vec2Subtract(point, boxPoint))

    def GetLineConnectionPointOnBox(self, point, box):
        case = self.ClassifyPointNearBox(point, box)
        xMax, yMax = box.width * 0.5, box.height * 0.5
        xMin, yMin = -xMax, -yMax
        if case == CASE1:
            boxPoint = (xMin, yMin)
        elif case == CASE2:
            boxPoint = (0, yMin)
        elif case == CASE3:
            boxPoint = (xMax, yMin)
        elif case == CASE4:
            boxPoint = (xMin, 0)
        elif case == CASE5:
            boxPoint = (xMax, 0)
        elif case == CASE6:
            boxPoint = (xMin, yMax)
        elif case == CASE7:
            boxPoint = (0, yMax)
        elif case == CASE8:
            boxPoint = (xMax, yMax)
        elif case == CASE9:
            x = (xMin + xMax) * 0.5
            y = (yMin + yMax) * 0.5
            point2 = Vec2Subtract(point, (x, y))
            boxPoint = sorted(((xMin, yMin),
             (xMin, yMax),
             (xMax, yMin),
             (xMax, yMax)), key=lambda x: Vec2Length(Vec2Subtract(point2, x)))[0]
        return boxPoint

    def _CloseBox(self):
        self.floatingBox.onOpacityChanged.disconnect(self.OnOpacityChanged)
        cs = uicore.uilib.bracketCurveSet
        if cs:
            for binding in self.bindings:
                if binding in cs.bindings:
                    cs.bindings.remove(binding)

        self.floatingBox.Close()
        self.line.Close()

    def Close(self):
        if self.destroyed:
            return
        self.destroyed = True
        if self.showBracket:
            if self.showBox:
                self._CloseBox()
            self.bracket.Close()

    def FlushPointer(self):
        sm.GetService('uipointerSvc').FlushSpaceObjectPointer(self.itemID)

    def OnOpacityChanged(self, opacity):
        if self.bracket and not self.bracket.destroyed:
            self.bracket.opacity = opacity


class SpaceObjectFloatingBox(UiPointer):
    __guid__ = 'SpaceObjectFloatingBox'

    def ApplyAttributes(self, attributes):
        self.itemID = attributes.get('itemID')
        self.typeID = attributes.get('typeID')
        self.hint = attributes.get('hint')
        attributes.title = '<url=showinfo:%s//%s>%s</url>' % (self.typeID, self.itemID, attributes.get('title'))
        UiPointer.ApplyAttributes(self, attributes)
        iconContainer = Container(parent=self.contentCont, align=uiconst.TOLEFT, name='iconContainer', width=ICON_SIZE, height=ICON_SIZE, padRight=ICON_PADDING)
        iconWrapper = Container(parent=iconContainer, align=uiconst.TOTOP, name='iconContainer', width=ICON_SIZE, height=ICON_SIZE)
        self.icon = Icon(typeID=self.typeID, parent=iconWrapper, width=ICON_SIZE, height=ICON_SIZE, ignoreSize=True, align=uiconst.TOLEFT, OnClick=lambda : sm.GetService('info').ShowInfo(typeID=self.typeID, itemID=self.itemID))

    def ConstructContent(self):
        UiPointer.ConstructContent(self)

    def CorrectSize(self, contentWidth = None, contentHeight = None):
        contentWidthWithIconCorrection = self.textContainer.width + ICON_SIZE + ICON_PADDING
        contentHeightWithIconCorrection = max(self.textContainer.height, ICON_SIZE)
        UiPointer.CorrectSize(self, contentWidthWithIconCorrection, contentHeightWithIconCorrection)
        self.top = (uicore.desktop.height - self.height) / 2.0
        self.left = (uicore.desktop.width - self.width) / 2.0


class SpaceObjectUiPointerBracket(Bracket):
    __guid__ = 'SpaceObjectUiPointerBracket'
    default_width = BRACKET_SIZE
    default_height = BRACKET_SIZE
    default_align = uiconst.NOALIGN
    default_state = uiconst.UI_DISABLED

    def ApplyAttributes(self, attributes):
        Bracket.ApplyAttributes(self, attributes)
        self.dock = True
        self._CreateVideoSprites()
        self._PlayIntro()
        self.projectBracket.marginRight = self.projectBracket.marginLeft + self.width
        self.projectBracket.marginBottom = self.projectBracket.marginTop + self.height
        self.projectBracket.parent = uicore.layer.inflight.GetRenderObject()
        self.inflight = True

    def _CreateVideoSprites(self):
        self.bracketSpriteLoop = StreamingVideoSprite(parent=self, name='spaceObjectHighlightBracketLoopVideo', videoPath=BRACKET_LOOP_VIDEO, videoLoop=True, align=uiconst.CENTER, width=BRACKET_SPRITE_SIZE, height=BRACKET_SPRITE_SIZE, state=uiconst.UI_DISABLED, blendMode=TR2_SBM_BLEND, spriteEffect=TR2_SFX_COLOROVERLAY, opacity=0.0, disableAudio=True)
        self.bracketSpriteLoop.Pause()
        self.bracketSpriteIntro = StreamingVideoSprite(parent=self, name='spaceObjectHighlightBracketIntroVideo', videoPath=BRACKET_INTRO_VIDEO, videoLoop=False, align=uiconst.CENTER, width=BRACKET_SPRITE_SIZE, height=BRACKET_SPRITE_SIZE, state=uiconst.UI_DISABLED, blendMode=TR2_SBM_BLEND, spriteEffect=TR2_SFX_COLOROVERLAY, opacity=0.0, disableAudio=True)
        self.bracketSpriteIntro.Pause()
        self.bracketSpriteIntro.OnVideoFinished = self._PlayLoop
        Sprite(parent=self, name='spaceObjectHighlightBracketGlow', align=uiconst.CENTER, texturePath=BRACKET_GLOW_TEXTURE, width=BRACKET_SPRITE_SIZE, height=BRACKET_SPRITE_SIZE, state=uiconst.UI_DISABLED, blendMode=TR2_SBM_ADD)

    def _PlayIntro(self):
        self.bracketSpriteIntro.opacity = 1.0
        self.bracketSpriteIntro.Play()

    def _PlayLoop(self):
        self.bracketSpriteIntro.opacity = 0.0
        self.bracketSpriteLoop.opacity = 1.0
        self.bracketSpriteLoop.Play()
