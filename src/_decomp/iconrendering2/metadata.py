#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\iconrendering2\metadata.py
import os
import yamlext
from .const import IconStyle, IconViewMode
DEFAULT_SUN_DIRECTION = (-1.0, -1.0, 0.5)
DEFAULT_NEAR = 1.0
DEFAULT_FAR = 1000000.0

def BuildBaseIconMetadata():
    dict = {}
    dict['sunDirection'] = DEFAULT_SUN_DIRECTION
    dict['viewMode'] = IconViewMode.FREE
    dict['view'] = {'eye': (1000, 1000, 1000),
     'at': (0, 0, 0),
     'up': (0, 1, 0)}
    dict['projection'] = {'aspectRatio': 1.0,
     'fov': 1.0,
     'zn': DEFAULT_NEAR,
     'zf': DEFAULT_FAR,
     'left': None,
     'right': None,
     'top': None,
     'bottom': None}
    dict['stateControllerVariables'] = {}
    dict['animationOffset'] = 0
    dict['playCurveSets'] = False
    dict['scaleFactor'] = 1.0
    return dict


def BuildDefaultIconDict():
    dict = {}
    dict['skip'] = False
    dict[IconStyle.STANDARD] = BuildBaseIconMetadata()
    return dict


def CompareIconData(data1, data2):
    t1 = data1.get('sunDirection', None) == data2.get('sunDirection', None)
    t2 = True
    if 'view' in data1 and 'view' in data2:
        t2 = t2 and data1['view'].get('eye', None) == data2['view'].get('eye', None)
        t2 = t2 and data1['view'].get('at', None) == data2['view'].get('at', None)
        t2 = t2 and data1['view'].get('up', None) == data2['view'].get('up', None)
    t3 = True
    if 'view' in data1 and 'view' in data2:
        t3 = t3 and data1['projection'].get('aspectRatio', None) == data2['projection'].get('aspectRatio', None)
        t3 = t3 and data1['projection'].get('fov', None) == data2['projection'].get('fov', None)
        t3 = t3 and data1['projection'].get('zn', None) == data2['projection'].get('zn', None)
        t3 = t3 and data1['projection'].get('zf', None) == data2['projection'].get('zf', None)
        t3 = t3 and data1['projection'].get('left', None) == data2['projection'].get('left', None)
        t3 = t3 and data1['projection'].get('right', None) == data2['projection'].get('right', None)
        t3 = t3 and data1['projection'].get('bottom', None) == data2['projection'].get('bottom', None)
        t3 = t3 and data1['projection'].get('top', None) == data2['projection'].get('top', None)
    t4 = data1.get('stateControllerVariables', None) == data2.get('stateControllerVariables', None)
    t5 = data1.get('animationOffset', 0) == data2.get('animationOffset', 0)
    t6 = data1.get('playCurveSets', False) == data2.get('playCurveSets', False)
    t7 = data1.get('viewMode', IconViewMode.FREE) == data2.get('viewMode', IconViewMode.FREE)
    t8 = data1.get('scaleFactor', 1.0) == data2.get('scaleFactor', 1.0)
    return t1 and t2 and t3 and t4 and t5 and t6 and t7 and t8


def UpdateIconDataFromScene(data, scene, camera):
    if 'sunDirection' in data:
        data['sunDirection'] = scene.sunDirection
    if 'view' in data:
        data['view']['eye'] = camera.GetPosition()
        data['view']['at'] = camera.GetPointOfInterest()
        data['view']['up'] = camera.GetUpVector()
    if 'projection' in data:
        data['projection']['zn'] = DEFAULT_NEAR
        data['projection']['zf'] = DEFAULT_FAR
        poc = camera.GetPerspectiveOffCenter()
        data['projection']['left'] = poc[0]
        data['projection']['right'] = poc[1]
        data['projection']['top'] = poc[2]
        data['projection']['bottom'] = poc[3]
    return data


def UpdateSceneFromIconData(data, scene, camera):
    if 'sunDirection' not in data:
        data['sunDirection'] = (0, 0, 0)
    scene.sunDirection = data['sunDirection']
    if 'view' not in data:
        data['view'] = {}
        data['view']['eye'] = (0, 0, 0)
        data['view']['up'] = (0, 0, 0)
        data['view']['at'] = (0, 0, 0)
    camera.SetPosition(data['view']['eye'])
    camera.SetUpVector(data['view']['up'])
    camera.LookAt(data['view']['at'], data['view']['up'])
    if 'projection' not in data:
        data['projection'] = {}
        data['projection']['aspectRatio'] = 1.0
        data['projection']['fov'] = 1.0
        data['projection']['zn'] = DEFAULT_NEAR
        data['projection']['zf'] = DEFAULT_FAR
        data['projection']['left'] = None
        data['projection']['right'] = None
        data['projection']['top'] = None
        data['projection']['bottom'] = None
    camera.SetPerspectiveOffCenter(data['projection']['left'], data['projection']['right'], data['projection']['top'], data['projection']['bottom'], data['projection']['zn'], data['projection']['zf'])
    camera.Update()


def UpdateIconDataFromStateControllers(data, obj):
    ClearStateControllerVariables(data)
    try:
        variables = obj.Find('trinity.Tr2ControllerFloatVariable')
        for var in variables:
            if var.value != var.defaultValue:
                SetStateControllerVariable(data, var.name, var.value)

    except:
        print "Couldn't retrieve state controller variables for %s" % (obj.name if hasattr(obj, 'name') else obj)

    return data


def UpdateStateControllersFromIconData(data, obj):
    try:
        for key, val in data['stateControllerVariables'].iteritems():
            obj.SetControllerVariable(key, val)

        obj.StartControllers()
    except:
        pass


def ClearStateControllerVariables(data):
    data['stateControllerVariables'] = {}


def SetStateControllerVariable(data, variableName, value):
    if variableName not in data['stateControllerVariables']:
        data['stateControllerVariables'][variableName] = None
    data['stateControllerVariables'][variableName] = value


def LoadMetaDataForSpaceObject(resPath, hullName):
    metaDataPath = os.path.abspath(os.path.dirname(resPath) + '\\\\metadata\\\\%s_icon.yml' % hullName)
    if not os.path.exists(metaDataPath):
        return None
    return yamlext.loadfile(metaDataPath)


def AppendControllerOverrides(metadata, overrides):
    if 'stateControllerVariables' not in metadata:
        metadata['stateControllerVariables'] = {}
    for name, value in overrides.iteritems():
        SetStateControllerVariable(metadata, name, value)
