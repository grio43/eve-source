#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\cycleNebulaPanel.py
import fnmatch
import os
import walk
import trinity
from carbonui import uiconst
from carbonui.control.combo import Combo
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control import eveLabel
from carbonui.control.button import Button
from carbonui.control.window import Window
NEBULA_RES_PATHS = ['res:/dx9/scene/universe/',
 'res:/dx9/scene/wormholes/',
 'res:/dx9/scene/abyssal/',
 'res:/dx9/scene/event/',
 'res:/dx9/scene/preview/']
PANEL_HEIGHT = 150
PANEL_WIDTH = 250
NEBULA_REPLACEMENT = 0
SCENE_REPLACEMENT = 1

class CycleNebulaPanel(Window):
    default_width = PANEL_WIDTH
    default_height = PANEL_HEIGHT
    default_minSize = (default_width, default_height)
    default_maxSize = (default_width, default_height)
    default_fixedWidth = 300
    default_fixedHeight = 210

    def ApplyAttributes(self, attributes):
        super(CycleNebulaPanel, self).ApplyAttributes(attributes)
        self.nebulaPaths = []
        self.scenePaths = []
        self.currentMode = 0
        self.currentSelection = None
        self.sceneResourceIndex = 0
        self.realSceneRedFile = sm.GetService('sceneManager').GetScene().lower()
        self.SetupNebulas()
        self.currentIndex = self.scenePaths.index(self.realSceneRedFile)
        self.Layout()

    def LayoutOld(self):
        parent = self.GetMainArea()
        parent.SetAlign(uiconst.CENTER)
        parent.padding = 5
        parent.SetSize(PANEL_WIDTH, PANEL_HEIGHT)
        topCont = Container(parent=parent, align=uiconst.TOALL, top=20)
        self.currentNebulaPathLabel = eveLabel.Label(parent=topCont, text='Current selection: ', align=uiconst.TOTOP)
        self.comboBox = Combo(name='nebulaComboBox', parent=topCont, label='', options=[ (nebulaPath, index) for index, nebulaPath in enumerate(self.nebulaPaths) ], callback=self.ComboboxSelection, select=self.currentIndex, align=uiconst.TOTOP)
        eveLabel.Label(parent=topCont, text='Current Mode: ', align=uiconst.TOTOP)
        self.mode = Combo(name='mode', parent=topCont, label='', options=[('cubemap', NEBULA_REPLACEMENT), ('scene', SCENE_REPLACEMENT)], callback=self.ModeSelection, select=self.currentMode, align=uiconst.TOTOP)
        self.nextNebulaButton = Button(parent=topCont, label='Next', align=uiconst.BOTTOMRIGHT, func=self.IncrementIndex)
        self.prevNebulaButton = Button(parent=topCont, label='Previous', align=uiconst.BOTTOMLEFT, func=self.DecrementIndex)

    def Layout(self):
        self.main_container = ContainerAutoSize(parent=self.content, align=uiconst.TOTOP)
        self.currentNebulaPathLabel = eveLabel.Label(text='Current selection: ', align=uiconst.TOTOP, parent=self.main_container)
        self.comboBox = Combo(name='nebulaComboBox', label='', options=[ (nebulaPath, index) for index, nebulaPath in enumerate(self.nebulaPaths) ], callback=self.ComboboxSelection, select=self.currentIndex, align=uiconst.TOTOP, adjustWidth=True, parent=self.main_container, padBottom=4)
        eveLabel.Label(text='Current Mode: ', align=uiconst.TOTOP, parent=self.main_container)
        self.mode = Combo(name='mode', label='', options=[('cubemap', NEBULA_REPLACEMENT), ('scene', SCENE_REPLACEMENT)], callback=self.ModeSelection, select=self.currentMode, align=uiconst.TOTOP, parent=self.main_container)
        self.prevNebulaButton = Button(parent=self.content, label='Previous', align=uiconst.BOTTOMLEFT, func=self.DecrementIndex)
        self.nextNebulaButton = Button(parent=self.content, label='Next', align=uiconst.BOTTOMRIGHT, func=self.IncrementIndex)

    def Close(self, setClosed = False, *args, **kwds):
        self.SetScene(self.realSceneRedFile)
        super(Window, self).Close()

    def SetupNebulas(self):
        for rootPath in NEBULA_RES_PATHS:
            for dirpath, _, filenames in walk.walk(rootPath):
                for filename in fnmatch.filter(filenames, '*_cube.dds'):
                    resPath = os.path.join(dirpath, filename).replace('\\', '/')
                    self.nebulaPaths.append(str(resPath.lower()))

                for filename in fnmatch.filter(filenames, '*.red'):
                    resPath = os.path.join(dirpath, filename).replace('\\', '/')
                    self.scenePaths.append(str(resPath.lower()))

        self.nebulaPaths.sort()
        self.scenePaths.sort()

    def IncrementIndex(self, args):
        self.currentIndex = (self.currentIndex + 1) % len(self.nebulaPaths)
        self.SetNebulaOnScene()
        self.comboBox.SelectItemByIndex(self.currentIndex)

    def DecrementIndex(self, args):
        self.currentIndex = (self.currentIndex - 1) % len(self.nebulaPaths)
        self.SetNebulaOnScene()
        self.comboBox.SelectItemByIndex(self.currentIndex)

    def GetPaths(self):
        if self.currentMode == NEBULA_REPLACEMENT:
            return self.nebulaPaths
        return self.scenePaths

    def ComboboxSelection(self, boBox, key, value):
        self.currentIndex = value
        self.SetNebulaOnScene()

    def ModeSelection(self, boBox, key, value):
        self.currentMode = value
        self.comboBox.LoadOptions([ (path, index) for index, path in enumerate(self.GetPaths()) ])
        self.ComboboxSelection(None, None, 0)
        self.SetScene(self.realSceneRedFile)
        self.SetNebulaOnScene()

    def SetNebulaOnScene(self):
        if self.currentMode == NEBULA_REPLACEMENT:
            currentNebulaPath = self.nebulaPaths[self.currentIndex]
            self.comboBox.SetValue(self.currentIndex)
            scene = sm.GetService('sceneManager').GetActiveScene()
            scene.backgroundEffect.resources.FindByName('AlphaMap').resourcePath = currentNebulaPath[:-4] + '_refl.dds'
            scene.backgroundEffect.resources.FindByName('NebulaMap').resourcePath = currentNebulaPath
            scene.envMapResPath = currentNebulaPath[:-4] + '_refl.dds'
            scene.envMap1ResPath = currentNebulaPath
            scene.envMap2ResPath = currentNebulaPath[:-4] + '_blur.dds'
        elif self.currentMode == SCENE_REPLACEMENT:
            self.SetScene(self.scenePaths[self.currentIndex])

    def SetScene(self, scenePath):
        scene = sm.GetService('sceneManager').GetActiveScene()
        newScene = trinity.Load(scenePath, nonCached=True)
        for attribute in ['backgroundEffect',
         'envMapResPath',
         'envMap1ResPath',
         'envMap2ResPath',
         'ambientColor',
         'nebulaIntensity',
         'reflectionIntensity',
         'fogColor']:
            setattr(scene, attribute, getattr(newScene, attribute))
