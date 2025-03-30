#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\security\client\securityColor.py
COLORCURVE_SECURITY = [(0.553, 0.196, 0.392, 1.0),
 (0.451, 0.125, 0.125, 1.0),
 (0.737, 0.067, 0.09, 1.0),
 (0.808, 0.267, 0.059, 1.0),
 (0.863, 0.427, 0.027, 1.0),
 (0.961, 1.0, 0.514, 1.0),
 (0.447, 0.906, 0.333, 1.0),
 (0.38, 0.859, 0.643, 1.0),
 (0.306, 0.808, 0.973, 1.0),
 (0.227, 0.604, 0.922, 1.0),
 (0.173, 0.459, 0.886, 1.0)]

def get_security_status_color(security_status):
    color_index = int(max(security_status, 0.0) * 10)
    return COLORCURVE_SECURITY[color_index]
