#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\stdlib\xml\__init__.py
__all__ = ['dom',
 'parsers',
 'sax',
 'etree']
_MINIMUM_XMLPLUS_VERSION = (0, 8, 4)
try:
    import _xmlplus
except ImportError:
    pass
else:
    try:
        v = _xmlplus.version_info
    except AttributeError:
        pass
    else:
        if v >= _MINIMUM_XMLPLUS_VERSION:
            import sys
            _xmlplus.__path__.extend(__path__)
            sys.modules[__name__] = _xmlplus
        else:
            del v
