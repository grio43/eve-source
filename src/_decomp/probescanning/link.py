#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\probescanning\link.py
SCHEME_SCANNER_ACTION = 'scannerAction'

def register_link_handlers(registry):
    registry.register(scheme=SCHEME_SCANNER_ACTION, handler=handle_scanner_action_link)


def handle_scanner_action_link(url):
    action = url.split(':')[1]
    sm.GetService('scanSvc').ClickLink(action)
