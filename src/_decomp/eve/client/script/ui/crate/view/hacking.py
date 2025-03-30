#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\crate\view\hacking.py
import blue
import uthread2
from carbonui import const as uiconst, ButtonVariant, TextBody, TextHeadline, TextAlign, TextColor
from carbonui.button.group import ButtonGroup
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite, StreamingVideoSprite
from carbonui.primitives.vectorline import VectorLine
from carbonui.uianimations import animations
from carbonui.util import color
from crates.const import MAX_MULTI_OPEN
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveCaptionMedium
from eve.client.script.ui.control.themeColored import GradientThemeColored
from eve.client.script.ui.control.tooltips import TooltipPersistentPanel
from eve.client.script.ui.control.pointerPanel import FadeOutPanelAndClose, RefreshPanelPosition
import geo2
import itertools
import localization
import log
import math
import random
import trinity
import uthread
from carbonui.uicore import uicore
from eveexceptions import ExceptionEater
ACTIVE_CONNECTION_ANIM_DURATION = 0.15
HINT_TOOLTIP_SETTINGS_KEY = 'CrateWindowLootHintEnabled'

def res(filename):
    return 'res:/UI/Texture/classes/ItemPacks/{}'.format(filename)


def center(text):
    return u'<center>{}</center>'.format(text)


def getColorUIHighlight(alpha = 1.0):
    elementColor = sm.GetService('uiColor').GetUIColor(uiconst.COLORTYPE_UIHILIGHT)
    return color.GetColor(elementColor, alpha=alpha)


class HackingView(Container):
    default_clipChildren = True

    def ApplyAttributes(self, attributes):
        super(HackingView, self).ApplyAttributes(attributes)
        self.controller = attributes.controller
        self._claimedLootCount = 0
        self.processingMultiHackTasklet = None
        self.controller.onCrateMultiHackEnded.connect(self.OnMultiHackEnded)
        self.Layout()
        uthread.new(self.AnimEntry)

    def Layout(self):
        self.overlayCont = Container(parent=self, align=uiconst.VERTICALLY_CENTERED, padLeft=380, height=80, opacity=0.0)
        GradientThemeColored(bgParent=self.overlayCont, padding=(1, 0, 1, 0), rgbData=[(0, (0.5, 0.5, 0.5))], alphaData=[(0, 0.0), (0.4, 0.7), (0.6, 0.8)], rotation=0)
        VectorLine(parent=self.overlayCont, align=uiconst.TOPLEFT, translationTo=(0, 0), translationFrom=(600, 0), widthTo=5, widthFrom=5, colorTo=(1.0, 1.0, 1.0, 0.0), texturePath=res('Hacking_HatchPattern.png'), spriteEffect=trinity.TR2_SFX_COPY, textureWidth=8)
        VectorLine(parent=self.overlayCont, align=uiconst.BOTTOMLEFT, translationTo=(0, 0), translationFrom=(600, 0), widthTo=5, widthFrom=5, colorTo=(1.0, 1.0, 1.0, 0.0), texturePath=res('Hacking_HatchPattern.png'), spriteEffect=trinity.TR2_SFX_COPY, textureWidth=8)
        labelCont = Container(parent=self.overlayCont, align=uiconst.TOALL, padding=(180, 30, 20, 20))
        self.hackingLabel = TextHeadline(parent=self.overlayCont, align=uiconst.VERTICALLY_CENTERED, text=localization.GetByLabel('UI/Crate/HackingInProgress'), textAlign=TextAlign.CENTER)
        self.gridCont = Container(parent=self, align=uiconst.TOALL, padLeft=380)
        self.grid = HackingGrid(parent=self.gridCont, align=uiconst.TOALL, loot=self.controller.loot, specialLoot=self.controller.specialLoot, onLootClaimed=self.OnLootClaimed)
        self.back = StreamingVideoSprite(parent=self, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, width=800, height=550, top=-25, videoPath='res:/video/hacking/bgLoop_alpha.webm', spriteEffect=trinity.TR2_SFX_COPY, disableAudio=True)
        buttonGroupCont = ContainerAutoSize(parent=self, align=uiconst.BOTTOMRIGHT, minWidth=400, idx=0, top=8)
        self.buttonGroup = ButtonGroup(parent=buttonGroupCont, align=uiconst.CENTER)

    def AnimEntry(self):
        animations.FadeTo(self)
        uthread.new(self.AnimBackground)
        uthread.new(self.grid.AnimObstacles)
        uthread.new(self.grid.AnimEntry)

    def AnimBackground(self):
        animations.FadeTo(self.back, startVal=self.back.opacity, endVal=0.4, duration=0.3, sleep=True)
        animations.FadeTo(self.back, startVal=0.4, endVal=0.2, duration=6.0, loops=uiconst.ANIM_REPEAT, curveType=uiconst.ANIM_WAVE)

    def AnimBackgroundPulse(self):
        animations.FadeTo(self.back, startVal=0.6, endVal=0.4, duration=0.15, loops=3)
        blue.synchro.SleepWallclock(450)
        uthread.new(self.AnimBackground)

    def OnLootClaimed(self):
        item = None
        try:
            item = self.controller.ClaimLoot()
        except Exception:
            log.LogException('Error claiming loot item')

        if not self.controller.loot and not self.controller.specialLoot:
            self.RevealButtons()
        uthread.new(self.AnimBackgroundPulse)
        return item

    def RevealButtons(self):
        self.buttonGroup.FlushButtons()
        if self.controller.stacksize > 0:
            if self.controller.stacksize > MAX_MULTI_OPEN:
                text = localization.GetByLabel('UI/Crate/HackMultiple', quantity=MAX_MULTI_OPEN)
            else:
                text = localization.GetByLabel('UI/Crate/HackAll', quantity=self.controller.stacksize)
            Button(parent=self.buttonGroup, label=text, func=self.HackMultiple, variant=ButtonVariant.GHOST)
            text = localization.GetByLabel('UI/Crate/HackNext', quantity=self.controller.stacksize)
            Button(parent=self.buttonGroup, label=text, func=self.OpenAnotherCrate)
        else:
            Button(parent=self.buttonGroup, label=localization.GetByLabel('UI/Crate/Finish'), func=self.controller.Finish, args=())
        for button in self.buttonGroup.buttons:
            animations.FadeTo(button)

    def DisableButtons(self, *args):
        for button in self.buttonGroup.buttons:
            button.Disable()

    def OpenAnotherCrate(self, button):
        self.DisableButtons()
        self.controller.OpenCrate()

    def HackMultiple(self, button):
        self.DisableButtons()
        try:
            self._KillMultiHackTasklet()
            self.processingMultiHackTasklet = uthread.new(self.ShowProcessingMultiHack)
            self.controller.OpenMultipleCrates()
        except StandardError:
            self.RevealButtons()
            raise

        self.RevealButtons()

    def ShowProcessingMultiHack(self):
        self.hackingLabel.SetText(localization.GetByLabel('UI/Crate/HackingInProgress'))
        animations.FadeIn(self.overlayCont)
        self.gridCont.Flush()
        self.grid = HackingGrid(parent=self.gridCont, align=uiconst.TOALL, loot=[], specialLoot=[], onLootClaimed=self.OnLootClaimed)
        self.grid.ShowContiniousCellAnimation()

    def OnMultiHackEnded(self, cratesOpened, numCratesToOpen):
        self._KillMultiHackTasklet()
        self.hackingLabel.opacity = 0.0
        if cratesOpened == 0:
            text = localization.GetByLabel('UI/Crate/HackingFailed')
        elif cratesOpened != numCratesToOpen:
            text = localization.GetByLabel('UI/Crate/HackingPartiallyCompleted', numCratesOpened=cratesOpened, numCratesToOpen=numCratesToOpen)
        else:
            text = localization.GetByLabel('UI/Crate/HackingCompleted')
        self.hackingLabel.SetText(text)
        animations.FadeTo(self.hackingLabel, endVal=TextColor.NORMAL[3], timeOffset=0.1)

    def _KillMultiHackTasklet(self):
        if self.processingMultiHackTasklet:
            self.processingMultiHackTasklet.kill()
            self.processingMultiHackTasklet = None

    def Close(self):
        with ExceptionEater():
            self._KillMultiHackTasklet()
            self.controller.onCrateMultiHackEnded.disconnect(self.OnMultiHackEnded)
        super(HackingView, self).Close()


def weighted_choice(choices):
    total = sum((w for c, w in choices))
    r = random.uniform(0, total)
    upto = 0
    for c, w in choices:
        if upto + w >= r:
            return c
        upto += w


class HackingGrid(Container):
    gridWidth = 5
    gridHeight = 8
    gridTop = 55
    gridLeft = 22
    columnSpacing = 78.6
    rowSpacing = 46
    _neighborOffsetsOdd = ((-1, -1),
     (0, -1),
     (1, 0),
     (0, 1),
     (-1, 1),
     (-1, 0))
    _neighborOffsetsEven = ((0, -1),
     (1, -1),
     (1, 0),
     (1, 1),
     (0, 1),
     (-1, 0))
    _bleedHorizontalTexturePaths = ['res:/UI/Texture/classes/hacking/lineBleed/horiz01.png',
     'res:/UI/Texture/classes/hacking/lineBleed/horiz02.png',
     'res:/UI/Texture/classes/hacking/lineBleed/horiz03.png',
     'res:/UI/Texture/classes/hacking/lineBleed/horiz04.png',
     'res:/UI/Texture/classes/hacking/lineBleed/horiz05.png',
     'res:/UI/Texture/classes/hacking/lineBleed/horiz06.png',
     'res:/UI/Texture/classes/hacking/lineBleed/horiz07.png',
     'res:/UI/Texture/classes/hacking/lineBleed/horiz08.png',
     'res:/UI/Texture/classes/hacking/lineBleed/horiz09.png',
     'res:/UI/Texture/classes/hacking/lineBleed/horiz10.png',
     'res:/UI/Texture/classes/hacking/lineBleed/horiz11.png',
     'res:/UI/Texture/classes/hacking/lineBleed/horiz12.png',
     'res:/UI/Texture/classes/hacking/lineBleed/horiz13.png',
     'res:/UI/Texture/classes/hacking/lineBleed/horiz14.png',
     'res:/UI/Texture/classes/hacking/lineBleed/horiz15.png',
     'res:/UI/Texture/classes/hacking/lineBleed/horiz16.png',
     'res:/UI/Texture/classes/hacking/lineBleed/horiz17.png']
    _bleedDiagonalTexturePaths = ['res:/UI/Texture/classes/hacking/lineBleed/diag01.png',
     'res:/UI/Texture/classes/hacking/lineBleed/diag02.png',
     'res:/UI/Texture/classes/hacking/lineBleed/diag03.png',
     'res:/UI/Texture/classes/hacking/lineBleed/diag04.png',
     'res:/UI/Texture/classes/hacking/lineBleed/diag05.png',
     'res:/UI/Texture/classes/hacking/lineBleed/diag06.png',
     'res:/UI/Texture/classes/hacking/lineBleed/diag07.png',
     'res:/UI/Texture/classes/hacking/lineBleed/diag08.png',
     'res:/UI/Texture/classes/hacking/lineBleed/diag09.png',
     'res:/UI/Texture/classes/hacking/lineBleed/diag10.png',
     'res:/UI/Texture/classes/hacking/lineBleed/diag11.png']

    def ApplyAttributes(self, attributes):
        super(HackingGrid, self).ApplyAttributes(attributes)
        self.loot = attributes.loot
        self.specialLoot = attributes.specialLoot
        self.onLootClaimed = attributes.onLootClaimed
        self._showHint = settings.user.ui.Get(HINT_TOOLTIP_SETTINGS_KEY, True)
        self._hint = None
        self._lootCells = []
        self.cellObjects = {}
        self.path = self.GeneratePath()
        self.DistributeLootOnPath()
        self.SprinkleObstacles()
        self.PunchHolesInGrid()
        for cell in self.cells:
            if cell in self.cellObjects:
                continue
            x, y = self.getCellPosition(cell)
            self.cellObjects[cell] = RegularCell(parent=self, align=uiconst.RELATIVE, left=x, top=y)

        self.DrawCellConnections()

    def DistributeLootOnPath(self):
        remainingLoot = self.loot + self.specialLoot
        lootChancePerCell = len(remainingLoot) / float(len(self.path) - 2)
        accumulatedLootChance = lootChancePerCell
        for cell in self.path:
            if remainingLoot:
                if accumulatedLootChance >= 1.0:
                    remainingLoot.pop()
                    x, y = self.getCellPosition(cell)
                    self.cellObjects[cell] = ItemCell(parent=self, align=uiconst.RELATIVE, left=x - ItemCell.default_width / 2.0, top=y - ItemCell.default_height / 2.0, onClaimed=self.OnLootClaimed)
                    self._lootCells.append(cell)
                    accumulatedLootChance -= 1.0
                accumulatedLootChance += lootChancePerCell
            else:
                break

    def SprinkleObstacles(self):
        self.obstacles = []
        candidates = set(self.cells)
        candidates = list(candidates.difference(self.path))
        candidates = filter(lambda c: 0 < c[1] < self.gridHeight - 1, candidates)
        for i in xrange(random.randint(5, 7)):
            if not candidates:
                break
            cell = random.choice(candidates)
            x, y = self.getCellPosition(cell)
            obstacle = Obstacle(parent=self, align=uiconst.RELATIVE, left=x, top=y)
            self.cellObjects[cell] = obstacle
            self.obstacles.append(obstacle)
            candidates.remove(cell)
            for c in self.getCellNeighbors(cell):
                if c in candidates:
                    candidates.remove(c)

    def PunchHolesInGrid(self):
        candidates = set(self.cells)
        candidates = candidates.difference(self.path)
        candidates = list(candidates.difference(self.cellObjects.iterkeys()))
        for i in xrange(random.randint(5, 7)):
            if not candidates:
                break
            cell = random.choice(candidates)
            self.cellObjects[cell] = None
            candidates.remove(cell)

    def OnLootClaimed(self):
        item = self.onLootClaimed()
        self._showHint = False
        settings.user.ui.Set(HINT_TOOLTIP_SETTINGS_KEY, False)
        if self._hint:
            FadeOutPanelAndClose(self._hint)
        return item

    def AnimObstacles(self):

        def RevealThread(cell, timeOffset):
            blue.synchro.SleepWallclock(timeOffset * 1000)
            self.cellObjects[cell].AnimReveal()

        x_center, y_center = self.getCellPosition((0, 0))
        x_extent, y_extent = self.getCellPosition((self.gridWidth, self.gridHeight))
        extent = math.sqrt((x_extent - x_center) ** 2 + (y_extent - y_center) ** 2)
        timeFactor = 1.5 / extent
        for cell in self.cells:
            if self.cellObjects[cell] is None:
                continue
            x, y = self.getCellPosition(cell)
            x_offset = abs(x - x_center)
            y_offset = abs(y - y_center)
            timeOffset = timeFactor * math.sqrt(x_offset ** 2 + y_offset ** 2)
            uthread.new(RevealThread, cell, timeOffset)

    def AnimEntry(self):
        for i, cell in enumerate(self.path):
            if i == 0:
                self.DrawActiveFringeConnection(cell, self.getCellNeighbors(cell)[0])
            else:
                self.DrawActiveConnection(self.path[i - 1], cell)
            uthread.new(self.cellObjects[cell].AnimExplore)
            blue.synchro.SleepWallclock(ACTIVE_CONNECTION_ANIM_DURATION * 1000)

        lastCell = self.getCellNeighbors(self.path[-1])[3]
        self.DrawActiveFringeConnection(self.path[-1], lastCell, inbound=False)
        uthread.new(self.RevealHint)

    def ShowContiniousCellAnimation(self):
        x_center, y_center = self.getCellPosition((0, 0))
        x_extent, y_extent = self.getCellPosition((self.gridWidth, self.gridHeight))
        extent = math.sqrt((x_extent - x_center) ** 2 + (y_extent - y_center) ** 2)
        timeFactor = 1.5 / extent
        while True:
            if self.destroyed:
                break
            self.AnimObstacles()
            uthread2.Sleep(1.5)

    def RevealHint(self):
        blue.synchro.SleepWallclock(5000)
        if self._showHint:
            cell = random.choice(self._lootCells)
            node = self.cellObjects[cell]
            self._hint = uicore.uilib.tooltipHandler.LoadPersistentTooltip(node, customTooltipClass=HintTooltip)

    def Close(self):
        if self._hint:
            FadeOutPanelAndClose(self._hint)
        super(HackingGrid, self).Close()

    def GeneratePath(self):
        path = []

        def weight(c):
            return self.gridWidth / 2.0 - abs(c - (self.gridWidth - 1) / 2.0)

        weightedColumns = [ (c, weight(c)) for c in xrange(self.gridWidth) ]
        column = weighted_choice(weightedColumns)
        path.append((column, 0))
        while True:
            horizontalMult = 0.0 if len(path) == 1 else 2.0
            weights = (0 + max(0, 2 - path[-1][0]) * horizontalMult,
             1 + max(0, 2 - path[-1][0]) * 0.5,
             1 + max(0, path[-1][0] - 2) * 0.5,
             0 + max(0, path[-1][0] - 2) * horizontalMult)
            neighbors = self.getCellNeighbors(path[-1])[2:]
            weightedNeighbors = zip(neighbors, weights)
            candidates = filter(lambda x: self.IsCellInsideGrid(x[0]), weightedNeighbors)
            nextCell = weighted_choice(candidates)
            path.append(nextCell)
            if nextCell[1] == self.gridHeight - 1:
                break

        return path

    def DrawCellConnections(self):
        for cell in self.cells:
            if self.cellObjects[cell] is None:
                continue
            neighbors = filter(self.IsCellInsideGrid, self.getCellNeighbors(cell)[:3])
            for neighbor in neighbors:
                if self.cellObjects[neighbor] is None:
                    continue
                x_origin, y_origin = self.getCellPosition(cell)
                x, y = self.getCellPosition(neighbor)
                VectorLine(parent=self, translationFrom=(x_origin, y_origin), translationTo=(x, y), colorFrom=(1, 1, 1, 0.3), colorTo=(1, 1, 1, 0.8), widthFrom=0.3, widthTo=0.3)

        self.DrawFringePaths()

    def DrawActiveConnection(self, fromCell, toCell):
        x_origin, y_origin = self.getCellPosition(fromCell)
        x, y = self.getCellPosition(toCell)
        line = VectorLine(parent=self, translationFrom=(x_origin, y_origin), translationTo=(x, y), colorFrom=getColorUIHighlight(alpha=0.5), colorTo=getColorUIHighlight(alpha=0.5), widthFrom=1, widthTo=1, blendMode=trinity.TR2_SBM_ADDX2)
        midpoint = geo2.Vec2Lerp((x_origin, y_origin), (x, y), 0.5)
        if y_origin == y:
            texturePath = random.choice(self._bleedHorizontalTexturePaths)
            height = 50
            left = midpoint[0] - 48
            top = midpoint[1] - height / 2.0
        else:
            texturePath = random.choice(self._bleedDiagonalTexturePaths)
            height = 72
            left = midpoint[0] - 32
            top = midpoint[1] - height / 2.0
            if y_origin < y and x_origin > x or y_origin > y and x_origin < x:
                top += height
                height *= -1
        bleed = Sprite(parent=self, align=uiconst.RELATIVE, state=uiconst.UI_DISABLED, left=left, top=top, width=64, height=height, texturePath=texturePath, color=getColorUIHighlight(), blendMode=trinity.TR2_SBM_ADDX2)

        def BleedAnimation():
            animations.FadeTo(bleed, startVal=bleed.opacity, endVal=0.2, duration=5.0, loops=uiconst.ANIM_REPEAT, curveType=uiconst.ANIM_WAVE)

        animations.FadeTo(bleed, endVal=0.5, duration=0.1, loops=3, timeOffset=random.random() * 0.6, callback=BleedAnimation)
        glow = VectorLine(parent=self, translationFrom=(x_origin, y_origin), translationTo=(x, y), colorFrom=color.GetColor(getColorUIHighlight(), alpha=1.0), colorTo=color.GetColor(getColorUIHighlight(), alpha=1.0), widthFrom=30, widthTo=30, texturePath=res('Hacking_ConnectionGlow.png'), spriteEffect=trinity.TR2_SFX_COPY)
        animations.MorphVector2(line, 'translationTo', startVal=(x_origin, y_origin), endVal=(x, y), duration=ACTIVE_CONNECTION_ANIM_DURATION)
        animations.MorphVector2(glow, 'translationTo', startVal=(x_origin, y_origin), endVal=(x, y), duration=ACTIVE_CONNECTION_ANIM_DURATION)
        animations.SpColorMorphTo(line, attrName='colorTo', startColor=color.GetColor(getColorUIHighlight(), alpha=0.0), endColor=color.GetColor(getColorUIHighlight(), alpha=1.0), duration=ACTIVE_CONNECTION_ANIM_DURATION, timeOffset=ACTIVE_CONNECTION_ANIM_DURATION)
        animations.SpColorMorphTo(glow, attrName='colorTo', startColor=color.GetColor(getColorUIHighlight(), alpha=0.0), endColor=color.GetColor(getColorUIHighlight(), alpha=1.0), duration=ACTIVE_CONNECTION_ANIM_DURATION)
        animations.MorphScalar(glow, 'widthTo', endVal=30, duration=ACTIVE_CONNECTION_ANIM_DURATION)

    def DrawActiveFringeConnection(self, insideCell, outsideCell, inbound = True):
        x_origin, y_origin = self.getCellPosition(insideCell)
        x, y = self.getCellPosition(outsideCell)
        line = VectorLine(parent=self, translationFrom=(x_origin, y_origin), translationTo=(x, y), colorFrom=getColorUIHighlight(alpha=0.5), colorTo=color.GetColor(getColorUIHighlight(), alpha=0.0), widthFrom=1, widthTo=1, blendMode=trinity.TR2_SBM_ADDX2)
        VectorLine(parent=self, translationFrom=(x_origin, y_origin), translationTo=(x, y), colorFrom=getColorUIHighlight(alpha=0.5), colorTo=color.GetColor(getColorUIHighlight(), alpha=0.0), widthFrom=30, widthTo=30, texturePath=res('Hacking_ConnectionGlow.png'), spriteEffect=trinity.TR2_SFX_COPY, blendMode=trinity.TR2_SBM_ADDX2)
        if inbound:
            animations.MorphVector2(line, 'translationFrom', startVal=(x, y), endVal=(x_origin, y_origin), duration=ACTIVE_CONNECTION_ANIM_DURATION)
        else:
            animations.MorphVector2(line, 'translationTo', startVal=(x_origin, y_origin), endVal=(x, y), duration=ACTIVE_CONNECTION_ANIM_DURATION)
        animations.MorphScalar(line, 'opacity', startVal=0.0, endVal=1.0, duration=ACTIVE_CONNECTION_ANIM_DURATION)

    def IsCellOutsideGrid(self, cell):
        col, row = cell
        return col < 0 or self.gridWidth <= col or row < 0 or self.gridHeight <= row

    def IsCellInsideGrid(self, cell):
        return not self.IsCellOutsideGrid(cell)

    def DrawFringePaths(self):
        for cell in self.cells:
            if self.cellObjects[cell] is None:
                continue
            outsideCells = filter(self.IsCellOutsideGrid, self.getCellNeighbors(cell))
            for col, row in outsideCells:
                if 0 <= col < self.gridWidth and 0 <= row < self.gridHeight:
                    continue
                x_origin, y_origin = self.getCellPosition(cell)
                x, y = self.getCellPosition((col, row))
                VectorLine(parent=self, translationFrom=(x_origin, y_origin), translationTo=(x, y), colorFrom=(1, 1, 1, 0.2), colorTo=(1, 1, 1, 0.0), widthFrom=0.5, widthTo=0.5)

    @property
    def cells(self):
        return itertools.product(xrange(self.gridWidth), xrange(self.gridHeight))

    def getCellPosition(self, coord):
        x, y = coord
        rowOffset = self.columnSpacing / 2.0 if y % 2 == 0 else 0
        return (x * self.columnSpacing + rowOffset + self.gridLeft, y * self.rowSpacing + self.gridTop)

    def getCellNeighbors(self, coord):
        column, row = coord
        if row % 2 == 0:
            neighborOffsets = self._neighborOffsetsEven
        else:
            neighborOffsets = self._neighborOffsetsOdd
        return [ (column + c, row + r) for c, r in neighborOffsets ]


class RegularCell(Container):
    default_clipChildren = False
    default_state = uiconst.UI_DISABLED
    default_width = 1
    default_height = 1

    def ApplyAttributes(self, attributes):
        super(RegularCell, self).ApplyAttributes(attributes)
        self.Layout()

    def Layout(self):
        self.closed = Sprite(parent=self, align=uiconst.CENTER, width=64, height=64, texturePath='res:/UI/Texture/classes/hacking/tileUnflipped.png', color=(0.3, 0.3, 0.3))

    def AnimReveal(self):
        animations.SpGlowFadeOut(self.closed, duration=0.3)
        animations.MorphScalar(self.closed, 'glowExpand', startVal=0.5, endVal=10.0, duration=0.3)

    def AnimExplore(self):
        opened = Sprite(parent=self, align=uiconst.CENTER, width=40, height=40, texturePath='res:/UI/Texture/classes/hacking/tileExplored.png', color=getColorUIHighlight(), opacity=2.0, idx=0)
        offset = ACTIVE_CONNECTION_ANIM_DURATION / 2.0
        animations.FadeOut(self.closed, timeOffset=offset)
        animations.FadeIn(opened, duration=0.1, timeOffset=offset)
        animations.SpGlowFadeOut(opened, duration=0.3, timeOffset=offset + 0.1)
        animations.MorphScalar(opened, 'glowExpand', startVal=0.5, endVal=10.0, duration=0.3, timeOffset=offset + 0.1)


class ItemCell(Container):
    default_clipChildren = False
    default_state = uiconst.UI_DISABLED
    default_width = 64
    default_height = 64

    def ApplyAttributes(self, attributes):
        super(ItemCell, self).ApplyAttributes(attributes)
        self.onClaimed = attributes.onClaimed
        self._claimed = False
        self.Layout()

    def Layout(self):
        self.nodeSprite = Sprite(parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=64, height=64, texturePath='res:/UI/Texture/classes/hacking/tileUnflipped.png', color=(0.3, 0.3, 0.3))
        self.frame = StreamingVideoSprite(parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=72, height=72, videoPath=res('nodeIntro_R4.webm'), spriteEffect=trinity.TR2_SFX_COPY, disableAudio=True, color=getColorUIHighlight(1.5))
        self.frame.Pause()
        self.nodeSpinner = StreamingVideoSprite(parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=64, height=64, videoPath=res('baseNodeLoop.webm'), videoLoop=True, spriteEffect=trinity.TR2_SFX_COPY, blendMode=trinity.TR2_SBM_ADDX2, disableAudio=True, opacity=0.0, color=getColorUIHighlight())
        self.nodeSpinner.Pause()
        self.node = Sprite(parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=32, height=32, texturePath=res('itemNodeCenter.png'), blendMode=trinity.TR2_SBM_ADDX2, color=(0, 0, 0, 0))
        self.back = Sprite(parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=64, height=64, texturePath=res('itemNodeBack.png'), color=getColorUIHighlight(), opacity=0.0)

    def AnimReveal(self):
        animations.FadeOut(self.nodeSprite, duration=0.1)
        animations.FadeIn(self.node, endVal=1.0, duration=0.1)
        animations.SpGlowFadeOut(self.node, duration=0.3, timeOffset=0.1)
        animations.MorphScalar(self.node, 'glowExpand', startVal=0.5, endVal=10.0, duration=0.3, timeOffset=0.1)

    def AnimExplore(self):
        self.frame.Play()
        animations.FadeOut(self.nodeSprite, duration=0.1)
        animations.FadeIn(self.nodeSpinner, duration=0.5, callback=self.Enable)
        self.nodeSpinner.Play()
        animations.FadeIn(self.back, endVal=0.1, duration=0.2)
        animations.FadeIn(self.node, endVal=1.0, duration=0.25)
        animations.SpColorMorphTo(self.node, endColor=getColorUIHighlight(), duration=0.2)
        animations.MorphVector2(self.node, 'scale', startVal=(0.5, 0.5), duration=0.5, sleep=True)

        def PulseNode():
            offset = random.normalvariate(2.0, 1.0)
            animations.MorphVector2(self.node, 'scale', startVal=(1.0, 1.0), endVal=(0.8, 0.8), duration=0.15, timeOffset=offset)
            blue.synchro.SleepWallclock((offset + 0.15) * 1000)
            animations.MorphVector2(self.node, 'scale', startVal=(0.8, 0.8), endVal=(1.0, 1.0), duration=0.4)
            blue.synchro.SleepWallclock(500)
            if not self.destroyed:
                uthread.new(PulseNode)

        uthread.new(PulseNode)

    def ClaimLoot(self):
        if self._claimed:
            return
        self._claimed = True
        self.item = self.onClaimed()
        self.SetState(uiconst.UI_PICKCHILDREN)
        uthread.new(self.AnimRevealItem)

    def AddIcon(self):
        size = self.item.get_icon_size()
        icon = self.item.get_icon()
        if icon:
            self.icon = Sprite(name='LootItem_Sprite', parent=self, align=uiconst.CENTER, state=uiconst.UI_NORMAL, width=size, height=size, texturePath=self.item.get_icon(), idx=0)
        else:
            self.icon = Icon(name='LootItem_Icon', parent=self, align=uiconst.CENTER, state=uiconst.UI_NORMAL, width=size, height=size, typeID=self.item.typeID, isCopy=self.item.is_copy(), idx=0)
        self.icon.LoadTooltipPanel = self.LoadItemTooltipPanel

    def AnimRevealItem(self):
        self.frame.SetVideoPath(res('nodeHarvest_R4.webm'))
        animations.FadeOut(self.nodeSpinner, duration=0.2)
        animations.MorphVector2(self.node, 'scale', startVal=(1.0, 1.0), endVal=(2.0, 2.0), duration=0.15, sleep=True)
        animations.MorphVector2(self.node, 'scale', startVal=(2.0, 2.0), endVal=(0.5, 0.5), duration=0.1)
        animations.FadeOut(self.node, duration=0.15)
        blue.synchro.SleepWallclock(25)
        backdrop = Sprite(parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=48, height=48, texturePath=res('Hacking_NodeExploredBackground.png'), opacity=0.0)
        animations.FadeIn(backdrop, duration=0.25, timeOffset=0.1)
        self.AddIcon()
        if self.icon:
            animations.FadeTo(self.icon, duration=0.15)
            animations.MorphVector2(self.icon, 'scale', startVal=(4.0, 4.0), endVal=(0.9, 0.9), duration=0.15, sleep=True)
            animations.MorphVector2(self.icon, 'scale', startVal=(0.9, 0.9), endVal=(1.0, 1.0), duration=0.15)
            animations.SpGlowFadeOut(self.icon, duration=0.3)
            animations.MorphScalar(self.icon, 'glowExpand', startVal=0.5, endVal=10.0, duration=0.3)
        animations.SpColorMorphTo(self.frame, endColor=getColorUIHighlight(2.0), duration=0.15)

    def OnClick(self):
        self.ClaimLoot()

    def OnMouseEnter(self):
        animations.SpColorMorphTo(self.frame, endColor=getColorUIHighlight(4.0), duration=0.15)
        animations.FadeTo(self.back, startVal=self.back.opacity, endVal=0.4, duration=0.3)

    def OnMouseExit(self):
        animations.SpColorMorphTo(self.frame, endColor=getColorUIHighlight(2.0), duration=0.3)
        animations.FadeTo(self.back, startVal=self.back.opacity, endVal=0.1, duration=0.3)

    def LoadItemTooltipPanel(self, panel, owner):
        panel.LoadStandardSpacing()
        panel.AddLabelMedium(text=self.item.get_name())


class Obstacle(Container):
    default_state = uiconst.UI_DISABLED
    default_clipChildren = False
    default_width = 1
    default_height = 1
    _obstacleTexturePaths = ['res:/UI/Texture/classes/hacking/defSoftAntiVirus.png',
     'res:/UI/Texture/classes/hacking/defSoftFirewall.png',
     'res:/UI/Texture/classes/hacking/defSoftHoneyPotHealing.png',
     'res:/UI/Texture/classes/hacking/defSoftHoneyPotStrength.png',
     'res:/UI/Texture/classes/hacking/defSoftIds.png']
    _noiseTexturePaths = [res('Hacking_VirusNoise01.png'),
     res('Hacking_VirusNoise02.png'),
     res('Hacking_VirusNoise03.png'),
     res('Hacking_VirusNoise04.png')]

    def ApplyAttributes(self, attributes):
        super(Obstacle, self).ApplyAttributes(attributes)
        self.Layout()

    def Layout(self):
        self.node = Sprite(parent=self, align=uiconst.CENTER, width=64, height=64, texturePath='res:/UI/Texture/classes/hacking/tileUnflipped.png', color=(0.3, 0.3, 0.3))
        self.virus = Sprite(parent=self, align=uiconst.CENTER, width=64, height=64, texturePath=random.choice(self._obstacleTexturePaths), color=getColorUIHighlight(), opacity=0.0)
        self.frame = Sprite(parent=self, align=uiconst.CENTER, width=64, height=64, texturePath='res:/UI/Texture/classes/hacking/tileIconFrame.png', color=getColorUIHighlight(), opacity=0.0)
        self.back = Sprite(parent=self, align=uiconst.CENTER, width=48, height=48, texturePath=res('hacking_NodeExploredBackground.png'), opacity=0.0)
        self.noise = Sprite(parent=self, align=uiconst.CENTER, width=150, height=100, color=getColorUIHighlight(), opacity=0.25, textureSecondaryPath='res:/UI/Texture/classes/hacking/healRing1.png', spriteEffect=trinity.TR2_SFX_MASK, blendMode=trinity.TR2_SBM_ADD)

    def AnimReveal(self):
        animations.FadeOut(self.node, duration=0.2)
        animations.FadeIn(self.frame, endVal=0.5, duration=0.2)
        animations.FadeIn(self.back, duration=0.3)
        animations.SpGlowFadeOut(self.frame, duration=0.3, timeOffset=0.2)
        animations.MorphScalar(self.frame, 'glowExpand', startVal=0.5, endVal=10.0, duration=0.3, timeOffset=0.2)
        animations.BlinkIn(self.virus, sleep=True)
        animations.SpColorMorphTo(self.virus, endColor=(0.2, 0.2, 0.2, 1.0))
        animations.SpColorMorphTo(self.frame, endColor=(0.3, 0.3, 0.3, 0.3))
        uthread.new(self.AnimPulseNoise)

    def AnimPulseNoise(self):
        offset = 2.0 + random.random() * 12.0
        self.noise.SetTexturePath(random.choice(self._noiseTexturePaths))
        animations.MorphVector2(self.noise, 'scaleSecondary', startVal=(5.0, 5.0), endVal=(0.25, 0.25), duration=4.0, timeOffset=offset, sleep=True)
        if not self.destroyed:
            uthread.new(self.AnimPulseNoise)


class HintTooltip(TooltipPersistentPanel):
    default_pointerDirection = uiconst.POINT_LEFT_2

    def ApplyAttributes(self, attributes):
        super(HintTooltip, self).ApplyAttributes(attributes)
        self.owner = attributes.get('owner')
        self.pickState = uiconst.TR2_SPS_ON
        uicore.uilib.RegisterForTriuiEvents(uiconst.UI_MOUSEMOVEDRAG, self.OnGlobalMouseMoveDrag)

    def LoadTooltip(self, panel, owner):
        self.AddLabelMedium(text=localization.GetByLabel('UI/Crate/HackingHint'), padding=(24, 8, 24, 8))

    def ShowPanel(self, owner):
        animations.FadeTo(self, duration=1.5)

    def OnClick(self, *args):
        FadeOutPanelAndClose(self)

    def OnGlobalMouseMoveDrag(self, *args):
        if not self.destroyed:
            RefreshPanelPosition(self)
            return True
        return False
