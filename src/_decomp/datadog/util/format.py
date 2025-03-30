#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\datadog\util\format.py
from datadog.util.compat import json

def pretty_json(obj):
    return json.dumps(obj, sort_keys=True, indent=2)
