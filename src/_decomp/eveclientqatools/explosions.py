#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveclientqatools\explosions.py
import evetypes
from carbon.common.script.util.format import FmtAmt
from carbonui import uiconst
from carbonui.control.combo import Combo
from carbonui.control.scrollentries import ScrollEntryNode, SE_GenericCore
from carbonui.primitives.container import Container
from carbonui.primitives.gridcontainer import GridContainer
from eve.client.script.ui.control import eveScroll
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.window import Window
from eveclientqatools.performancebenchmark import PerformanceBenchmarkWindow
from evegraphics.explosions.spaceObjectExplosionManager import SpaceObjectExplosionManager
from fsdBuiltData.client.explosionBuckets import GetExplosionBucketIDByTypeID, GetExplosionRaces
from fsdBuiltData.client.explosionIDs import GetExplosionFilePath
SEARCH_DISTANCE = 1000000

class ExplosionDebugger(object):

    def __init__(self):
        self.name = 'Explosions'
        self.windowID = 'Explosions_ ' + self.name
        self._sceneManager = sm.GetService('sceneManager')
        self._michelle = sm.GetService('michelle')
        self.scroll = None
        self.selectedBallsToExplosionBucketID = {}
        self.ballIDToExplosion = {}

    def GetBall(self, ballID = None):
        if ballID is None:
            ballID = self.shipId
        return sm.GetService('michelle').GetBall(ballID)

    def ShowUI(self):
        wnd = Window.Open(windowID=self.windowID)
        wnd.SetMinSize([500, 250])
        wnd.SetCaption(self.name)
        main = wnd.GetMainArea()
        bottomCont = Container(name='bottomCont', parent=main, align=uiconst.TOBOTTOM, height=30, width=50, padBottom=10)
        explosionSelectionContainer = Container(name='explosionSelectionCont', parent=main, align=uiconst.TOBOTTOM, height=30, padTop=10, padBottom=10)
        explosionContainer = Container(name='explosionContainer', parent=main, align=uiconst.TOALL, padBottom=10)
        self.scroll = eveScroll.Scroll(parent=explosionContainer)
        self.scroll.sr.id = 'explosionDebugScroll'
        self.scroll.OnSelectionChange = self.OnSelectionChange
        self.explosionCombo = Combo(name='myCombo', parent=explosionSelectionContainer, label='Set explosion to selected items', options=[('None', None)], callback=self.OnExplosionSelected, align=uiconst.TOTOP, padRight=12, padLeft=12)
        buttonGrid = GridContainer(name='buttonGrid', parent=bottomCont, align=uiconst.CENTER, width=150, height=20, lines=1, columns=3)
        ButtonIcon(name='Play', parent=buttonGrid, align=uiconst.TORIGHT, width=20, height=20, iconSize=24, padRight=15, texturePath='res:/UI/Texture/Icons/play.png', func=self.Explode, hint='Play Explosions (the exploding ships will not survive)')
        ButtonIcon(name='Refresh', parent=buttonGrid, align=uiconst.CENTER, width=20, height=20, iconSize=24, texturePath='res:/UI/Texture/Icons/replay.png', func=self.UpdateTable, hint='Update table')
        ButtonIcon(name='ClearWrecks', parent=buttonGrid, align=uiconst.TOLEFT, width=20, height=20, iconSize=32, padLeft=15, texturePath='res:/UI/Texture/Icons/44_32_37.png', func=self.ClearWrecks, hint='Clear wrecks')
        self.UpdateTable()

    def UpdateTable(self):
        layout = '%s<t>%s<t>%s<t>%s<t>%s<t>%s'
        headers = ['distance (m)',
         'itemID',
         'Type Name',
         'Group Name',
         'Explosion Bucket ID',
         'Selected Explosion']
        content = []
        ballpark = sm.GetService('michelle').GetBallpark()
        balls = ballpark.GetBallsInRange(session.shipid, SEARCH_DISTANCE)
        selectedEntries = []
        for ballID in balls:
            ball = sm.GetService('michelle').GetBall(ballID)
            if not hasattr(ball, 'typeData') or getattr(ball, 'exploded', False):
                continue
            typeID = ball.typeData['typeID']
            explosionBucketID = GetExplosionBucketIDByTypeID(typeID)
            if explosionBucketID is None:
                continue
            typeName = evetypes.GetName(typeID)
            groupName = evetypes.GetGroupName(typeID)
            explosionRes = 'None'
            dist = FmtAmt(ballpark.DistanceBetween(session.shipid, ballID))
            info = (dist,
             ballID,
             typeName,
             groupName,
             explosionBucketID,
             explosionRes)
            label = layout % info
            entry = ScrollEntryNode(decoClass=SE_GenericCore, label=label)
            if ballID in self.selectedBallsToExplosionBucketID:
                selectedEntries.append(entry)
            content.append(entry)

        self.scroll.Load(contentList=content, headers=headers, fixedEntryHeight=18)
        self.scroll.SelectNodes(selectedEntries)

    def OnSelectionChange(self, selection):
        self.selectedBallsToExplosionBucketID = {}
        for item in selection:
            itemInfo = item.label.split('<t>')
            itemID = int(itemInfo[1])
            explosionBucketID = int(itemInfo[4])
            self.selectedBallsToExplosionBucketID[itemID] = explosionBucketID

        explosionBuckets = set(self.selectedBallsToExplosionBucketID.values())
        options = [('None', None)]
        for explosionBucketID in explosionBuckets:
            for race, explosions in GetExplosionRaces(int(explosionBucketID)).iteritems():
                for explosion in explosions:
                    options.append((GetExplosionFilePath(explosion.explosionID), explosion))

        self.explosionCombo.LoadOptions(options)

    def OnExplosionSelected(self, combobox, key, value):
        selectedBalls = self.selectedBallsToExplosionBucketID.keys()
        for ballID in selectedBalls:
            if value is None and ballID in self.ballIDToExplosion:
                del self.ballIDToExplosion[ballID]
            else:
                self.ballIDToExplosion[ballID] = value

        for row in self.scroll.sr.nodes:
            if not row.get('selected', 0):
                continue
            label = row.label
            splitLabel = label.split('<t>')
            splitLabel[5] = key
            row.label = '<t>'.join(splitLabel)

        self.scroll.ReloadNodes()

    def Explode(self):
        if PerformanceBenchmarkWindow.IsOpen():
            PerformanceBenchmarkWindow.GetIfOpen().ToggleBenchmark()
        if len(self.ballIDToExplosion) == 0:
            return
        for ballID, explosion in self.ballIDToExplosion.iteritems():
            SpaceObjectExplosionManager.SetPreferredExplosion(ballID, explosion)

        for ballID in self.selectedBallsToExplosionBucketID:
            sm.GetService('slash').SlashCmd('/kill %s' % ballID)
            if ballID in self.ballIDToExplosion:
                del self.ballIDToExplosion[ballID]

        self.selectedBallsToExplosionBucketID = {}

    def ClearWrecks(self):
        sm.GetService('slash').SlashCmd('/unspawn range=%s only=groupWreck' % SEARCH_DISTANCE)
        self.UpdateTable()
