#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\trinutils\wip.py
import json
import os
try:
    import blue, trinity
except ImportError:
    blue, trinity = (None, None)

import devenv
import preferences
import trinutils.sceneutils as sceneutils
APPNAME = 'JessicaWIP'

def _InitPrefs(appname):
    path = devenv.GetPrefsFilename(appname, prefsname='prefs.json', makedirs=True)
    prefs = preferences.Pickled(path, dump=json.dump, load=json.load)
    return (prefs, os.path.dirname(path))


PREFS, APPPATH = _InitPrefs(APPNAME)
WIP_SCENE = os.path.join(APPPATH, 'wip.red')

def _SaveScene(filename):
    s2 = sceneutils.FindScene()
    if not s2:
        raise IOError(filename)
    trinity.Save(s2, filename)


def _LoadScene(filename):
    trinity.device.scene = trinity.Load(filename, nonCached=False)
    sceneutils.CreateFisRenderJob(trinity.device.scene)
    if not trinity.device.scene:
        raise IOError(filename)


def SnapshotSave(wipscene = WIP_SCENE):
    _SaveScene(wipscene)
    print 'Scene saved... %s' % wipscene


def SnapshotLoad(wipscene = WIP_SCENE):
    _LoadScene(wipscene)
    print 'Scene loaded... %s' % wipscene


def SnapshotSetupScene(scene):
    trinity.device.scene = scene
    sceneutils.CreateFisRenderJob(trinity.device.scene)
