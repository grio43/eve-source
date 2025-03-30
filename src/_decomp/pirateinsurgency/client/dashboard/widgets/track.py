#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\pirateinsurgency\client\dashboard\widgets\track.py
import math
import carbonui
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.vectorlinetrace import DashedCircle
from eve.client.script.ui import eveColor
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.vectorline import VectorLine
from localization import GetByLabel

class FactionScoreProgressTrack(ContainerAutoSize):
    default_highlightTextColor = eveColor.BLACK
    default_trackTextColor = eveColor.WHITE
    default_trackTextBackgroundColor = eveColor.LED_GREY
    default_trackAmbitionColor = eveColor.BLACK
    default_alignMode = uiconst.TOTOP
    default_rowLength = 5

    def ApplyAttributes(self, attributes):
        super(FactionScoreProgressTrack, self).ApplyAttributes(attributes)
        self.trackColor = attributes.get('trackColor')
        self.highlightColor = attributes.get('highlightColor')
        self.trackBackgroundColor = attributes.get('trackBackgroundColor')
        self.trackAmbitionColor = attributes.get('trackAmbitionColor', self.default_trackAmbitionColor)
        self.highlightTextColor = attributes.get('highlightTextColor', self.default_highlightTextColor)
        self.trackTextColor = attributes.get('trackTextColor', self.default_trackTextColor)
        self.trackTextBackgroundColor = attributes.get('trackTextBackgroundColor', self.default_trackTextBackgroundColor)
        self.value = attributes.get('value')
        self.stages = attributes.get('stages')
        self.badgeTexturePath = attributes.get('badgeTexturePath')
        self.rowLength = attributes.get('rowLength', self.default_rowLength)
        self.ambitionModifier = attributes.get('ambitionModifier')
        if self.stages > 0:
            self.ConstructLayout()

    def ConstructLayout(self):
        spriteCont = Container(parent=self, align=uiconst.TOLEFT, width=32)
        Sprite(parent=spriteCont, align=uiconst.TOPLEFT, width=32, height=32, top=-4, texturePath=self.badgeTexturePath)
        rowsCont = ContainerAutoSize(parent=self, align=uiconst.TOTOP, padLeft=5)
        nrows = self.stages / self.rowLength
        remainder = self.stages % self.rowLength
        if remainder > 0:
            nrows += 1
        rows = [ Container(parent=rowsCont, align=uiconst.TOTOP, height=24) for _stage in range(max(1, nrows)) ]
        currentRow = rows[0]
        rowIdx = 0
        indentRow = False
        for i in range(self.stages):
            if i == 0:
                rowIdx = 0
                currentRow = rows[rowIdx]
            elif i % self.rowLength == 0:
                rowIdx += 1
                currentRow = rows[rowIdx]
                indentRow = not indentRow
                currentRow.left = 20 * indentRow
            isInAmbitionRange = i >= self.stages - self.ambitionModifier
            if self.value > i + 1:
                textColor = self.trackTextColor
                circleColor = self.trackColor
                lineColor = self.trackColor
            elif self.value == i + 1:
                textColor = self.highlightTextColor
                circleColor = self.highlightColor
                lineColor = self.trackBackgroundColor
            else:
                textColor = self.trackTextBackgroundColor
                if isInAmbitionRange:
                    circleColor = self.trackAmbitionColor
                else:
                    circleColor = self.trackBackgroundColor
                lineColor = self.trackBackgroundColor
            circleCont = Container(parent=currentRow, width=24, name='arcCont', align=uiconst.TOLEFT)
            if isInAmbitionRange:
                DashedCircle(name='OuterCircle', parent=circleCont, align=uiconst.CENTER, range=math.radians(360), lineWidth=1, radius=12, dashCount=12, startColor=textColor, endColor=textColor)
            hint = None
            if isInAmbitionRange:
                hint = GetByLabel('UI/PirateInsurgencies/ScoreAmbitionHint')
            Sprite(parent=circleCont, texturePath='res:/UI/Texture/classes/pirateinsurgencies/widgets/track/circle.png', width=24, height=24, align=uiconst.TOPLEFT, color=circleColor, hint=hint)
            carbonui.TextBody(parent=circleCont, align=uiconst.CENTER, text='{}'.format(i + 1), color=textColor, bold=True, idx=0)
            if i < self.stages - 1 and (i + 1) % self.rowLength != 0:
                lineCont = Container(parent=currentRow, name='lineCont', align=uiconst.TOLEFT, width=12)
                VectorLine(parent=lineCont, align=uiconst.TOPLEFT, top=12, translationFrom=(0, 0), translationTo=(12, 0), widthFrom=4.0, widthTo=4.0, color=lineColor)
