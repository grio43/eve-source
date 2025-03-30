#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\statscapture\camerapresets.py
import json
CAMERA_PRESETS_URL = 'http://trilambda-ws:8088/camerapresets'

def GetAllPresets():
    import requests
    try:
        return [ (x['id'], x['preset']) for x in requests.request('GET', CAMERA_PRESETS_URL).json().values() ]
    except:
        return []


def SavePreset(preset, name):
    import requests
    requests.request('POST', CAMERA_PRESETS_URL, data={'preset': json.dumps({'id': name,
                'preset': preset})})


def DeletePreset(name):
    import requests
    requests.request('DELETE', CAMERA_PRESETS_URL, data={'name': name})
