#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\hacking\hackingWindow.py
import random
import evetypes
import hackingcommon.hackingConstants as hackingConst
import localization
import trinity
import uthread
from carbon.common.script.sys.serviceConst import ROLE_QA
from carbonui import fontconst, uiconst
from carbonui.control.contextMenu.menuDataFactory import CreateMenuDataFromRawTuples
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import StreamingVideoSprite
from carbonui.primitives.transform import Transform
from carbonui.services.setting import UserSettingBool
from carbonui.uicore import uicore
from carbonui.util.color import Color
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.hacking import hackingLine, hackingTile, hackingUIConst, hackingUtilityElement, hackingVirusInfo
QA_SHOW_TILES_SETTING = UserSettingBool('Hacking_QA_showTiles', False)

class HackingWindow(Window):
    __guid__ = 'form.HackingWindow'
    __notifyevents__ = ['OnHackingNewTurn',
     'OnHackingWon',
     'OnHackingLost',
     'OnDefenseSoftwareUnveiled',
     'OnCoreUnveiled',
     'OnHackingTileCreated',
     'OnHackingTileChanged',
     'OnHackingStart',
     'OnHackingUEInventoryConstructed']
    default_windowID = 'HackingWindow'
    default_caption = 'Hacking'
    default_width = 898
    default_height = 647
    default_fixedWidth = default_width
    default_fixedHeight = default_height
    default_isCollapseable = False
    default_isStackable = False
    default_extend_content_into_header = True
    default_apply_content_padding = False

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.tilesByTileCoord = {}
        self.linesByTileCoords = {}
        self.utilityElements = []
        self.accessibleTiles = []
        self.hasGameEnded = False
        self.header.show_caption = False
        self.hasWindowIcon = False
        self.bottomCont = Container(name='bottomCont', parent=self.content, align=uiconst.TOBOTTOM, height=110)
        self.tileHintLabel = eveLabel.Label(name='tileHintLabel', parent=self.bottomCont, align=uiconst.BOTTOMRIGHT, pos=(15, 15, 220, 0), fontsize=fontconst.EVE_SMALL_FONTSIZE)
        self.utilityElementContainer = ContainerAutoSize(name='utilityElementContainer', parent=self.bottomCont, align=uiconst.CENTERBOTTOM, state=uiconst.UI_PICKCHILDREN, opacity=1.0, height=50, top=10)
        self.virusInfo = hackingVirusInfo.VirusInfo(parent=self.bottomCont, left=15, top=10, opacity=0.0)
        self.boardTransform = Transform(name='boardTransform', parent=self.content, align=uiconst.TOALL, padTop=32, state=uiconst.UI_NORMAL, scalingCenter=(0.5, 0.5))
        self.boardContainer = Container(name='boardContainer', parent=self.boardTransform, align=uiconst.TOPLEFT, opacity=0.0)
        self.backgroundVideo = StreamingVideoSprite(bgParent=self.sr.maincontainer, padTop=16, videoPath='res:/video/hacking/bgLoop_alpha.webm', videoLoop=True, spriteEffect=trinity.TR2_SFX_COPY, color=hackingUIConst.COLOR_WINDOW_BG, opacity=0.0)
        sm.GetService('audio').SendUIEvent('minigame_start')

    def Close(self, *args, **kw):
        Window.Close(self, *args, **kw)
        sm.GetService('audio').SendUIEvent('minigame_stop')

    def CloseByUser(self, *args):
        uthread.new(sm.GetService('hackingUI').QuitHackingAttempt)

    def EntryAnimation(self):
        uicore.animations.Tr2DScaleTo(self.boardTransform, startScale=(0.99, 0.99), endScale=(1.0, 1.0), duration=0.8)
        uicore.animations.FadeTo(self.backgroundVideo, 0.0, hackingUIConst.COLOR_WINDOW_BG[3], duration=1.6)
        uicore.animations.FadeIn(self.boardContainer, duration=0.8)
        uicore.animations.FadeIn(self.virusInfo, duration=0.8, timeOffset=0.3)
        uicore.animations.FadeIn(self.utilityElementContainer, duration=0.8, timeOffset=0.6)

    def OnHackingWon(self):
        self.EndGame(True)

    def OnHackingLost(self):
        self.EndGame(False)

    def OnHackingTileChanged(self, eventID, tileData):
        self.tilesByTileCoord[tileData.coord].UpdateTileState(eventID, tileData)
        self.UpdateLineColors()
        for neighbour in tileData.GetNeighbours():
            if neighbour.coord in self.tilesByTileCoord:
                self.tilesByTileCoord[neighbour.coord].UpdateTileState(hackingConst.EVENT_TILE_REACHABLE, tileData)

    def OnHackingTileCreated(self, tileData, objectData):
        if tileData.coord in self.tilesByTileCoord:
            self.OnHackingTileChanged(hackingConst.EVENT_TILE_CREATED, tileData)
        else:
            left, top = tileData.GetXY()
            tile = hackingTile.Tile(parent=self.boardContainer, left=left, top=top, tileData=tileData, showCoordLabel=QA_SHOW_TILES_SETTING.is_enabled())
            self.tilesByTileCoord[tileData.coord] = tile

    def OnHackingUEInventoryConstructed(self, inventoryContents):
        for i, elementData in enumerate(inventoryContents):
            elementUI = hackingUtilityElement.UtilityElement(parent=self.utilityElementContainer, utilityElementData=elementData, index=i)
            self.utilityElements.append(elementUI)

    def OnHackingStart(self, eventData):
        self.SetBoardSize()
        if eventData['moduleTypeID']:
            self.SetCaption(evetypes.GetName(eventData['moduleTypeID']))
        for tile in self.tilesByTileCoord.values():
            self.ConstructLinesForTile(tile.tileData)

        self.EntryAnimation()

    def SetBoardSize(self):
        x = y = 0
        for tile in self.tilesByTileCoord.values():
            hexX, hexY = tile.tileData.GetHexXY()
            if hexX > x:
                x = hexX
            if hexY > y:
                y = hexY

        self.boardContainer.width = x * hackingUIConst.GRID_X + hackingUIConst.TILE_SIZE
        self.boardContainer.height = y * hackingUIConst.GRID_Y + hackingUIConst.TILE_SIZE
        offsetY = int(hackingUIConst.GRID_MAX_ROWS - y - 1) / 2
        self.boardContainer.top = 16 + offsetY * hackingUIConst.GRID_Y
        offsetX = int(hackingUIConst.GRID_MAX_COLUMNS - x + 0.5) / 2
        if offsetY % 2 == 1:
            offsetX -= 0.5
        self.boardContainer.left = 15 + offsetX * hackingUIConst.GRID_X

    def OnDefenseSoftwareUnveiled(self, coord):
        uicore.animations.SpColorMorphTo(self.backgroundVideo, hackingUIConst.COLOR_WINDOW_BG_BLINK, hackingUIConst.COLOR_WINDOW_BG, duration=0.6)

    def OnCoreUnveiled(self, coord):
        uicore.animations.SpColorMorphTo(self.backgroundVideo, hackingUIConst.COLOR_WINDOW_BG_BLINK, hackingUIConst.COLOR_WINDOW_BG, duration=0.15, loops=3)

    def EndGame(self, won):
        self.boardContainer.Disable()
        text = localization.GetByLabel('UI/Hacking/HackSuccess') if won else localization.GetByLabel('UI/Hacking/HackFailed')
        label = eveLabel.Label(parent=self.content, align=uiconst.CENTER, text=text, bold=True, fontsize=30, idx=0, color=Color.WHITE)
        uicore.animations.FadeTo(self.boardContainer, 1.0, 0.5, duration=1.0)
        uicore.animations.FadeOut(self.utilityElementContainer, duration=0.6)
        uicore.animations.FadeOut(self.virusInfo, duration=0.6, timeOffset=0.3)
        uicore.animations.FadeTo(label, 0.0, 1.0, duration=0.6, timeOffset=0.2)
        color = hackingUIConst.COLOR_EXPLORED if won else hackingUIConst.COLOR_UNEXPLORED
        lines = self.linesByTileCoords.values()
        random.shuffle(lines)
        for i, line in enumerate(lines):
            line.AnimExit(i)

        tiles = self.tilesByTileCoord.values()
        random.shuffle(tiles)
        for i, tile in enumerate(tiles):
            uicore.animations.FadeTo(tile, tile.opacity, 0.0, timeOffset=0.2 + i * 0.01, duration=0.2)

        uicore.animations.Tr2DScaleOut(self.boardTransform, endScale=(0.99, 0.99), duration=10.0)
        uicore.animations.FadeOut(self, duration=1.6, callback=self.Close)

    def UpdateLineColors(self):
        for line in self.linesByTileCoords.values():
            line.UpdateState()

    def ConstructLinesForTile(self, tileData):
        for neighbour in tileData.GetNeighbours():
            lineID = [tileData.coord, neighbour.coord]
            lineID.sort()
            lineID = tuple(lineID)
            tile1 = self.tilesByTileCoord[lineID[0]]
            tile2 = self.tilesByTileCoord[lineID[1]]
            if lineID in self.linesByTileCoords:
                continue
            line = hackingLine.Line(tileFrom=tile1, tileTo=tile2, parent=self.boardContainer)
            self.linesByTileCoords[lineID] = line

    def OnKeyDown(self, key, *args):
        if key == uiconst.VK_1:
            self.utilityElements[0].OnClick()
        elif key == uiconst.VK_2:
            self.utilityElements[1].OnClick()
        elif key == uiconst.VK_3:
            self.utilityElements[2].OnClick()

    def SetTileHint(self, hint):
        if hint:
            self.tileHintLabel.text = '<right>' + hint + '</right>'
            if self.tileHintLabel.opacity < 0.01:
                uicore.animations.FadeTo(self.tileHintLabel, self.tileHintLabel.opacity, 1.0, duration=0.3, timeOffset=0.6)
            else:
                uicore.animations.FadeTo(self.tileHintLabel, self.tileHintLabel.opacity, 1.0, duration=0.3)
        else:
            uicore.animations.FadeOut(self.tileHintLabel, duration=0.1)

    def GetMenu(self, *args):
        menuData = CreateMenuDataFromRawTuples(Window.GetMenu(self, *args))
        if session.role & ROLE_QA:
            menuData.AddCheckbox('QA - Show tiles', setting=QA_SHOW_TILES_SETTING)
        return menuData
