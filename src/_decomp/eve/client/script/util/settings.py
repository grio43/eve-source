#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\util\settings.py
SETTING_SHIP_TOP_ALIGNED = 'shipuialigntop'

def IsShipHudTopAligned():
    return settings.user.ui.Get(SETTING_SHIP_TOP_ALIGNED, False)


def SetShipHudTopAligned(isHudTopAligned):
    settings.user.ui.Set(SETTING_SHIP_TOP_ALIGNED, isHudTopAligned)


def EncodeSetting(value):
    if value is None:
        return 'None'
    if not value:
        return ''
    if isinstance(value, dict):
        return '{' + ''.join([ '{k}: {v},'.format(k=EncodeSetting(k), v=EncodeSetting(v)) for k, v in value.iteritems() ]) + '}'
    if isinstance(value, list):
        return '[' + ','.join([ EncodeSetting(each) for each in value ]) + ']'
    if hasattr(value, 'encode'):
        return value.encode('utf-8', 'ignore')
    return str(value)
