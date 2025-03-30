#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evelink\client\handlers\deprecated.py
DEPRECATED_SCHEMES = ('eve', 'cmd', 'fleetmenu', 'celestialmenu')

def register_deprecated_handlers(registry):
    for deprecated_scheme in DEPRECATED_SCHEMES:
        registry.register(deprecated_scheme, handle_deprecated_link)


def handle_deprecated_link(url):
    scheme = url[:url.index(':')]
    raise RuntimeError("Links with scheme '{}:' are no longer supported".format(scheme))
