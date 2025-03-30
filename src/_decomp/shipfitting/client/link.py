#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipfitting\client\link.py
SCHEME = 'fitting'

def register_link_handlers(registry):
    registry.register(SCHEME, handle_fitting_link, hint='UI/Fitting/ShowFitting', accept_link_text=True)


def handle_fitting_link(url, text = None):
    fitting = parse_fitting_url(url)
    sm.GetService('fittingSvc').DisplayFittingFromString(fitting, text)


def parse_fitting_url(url):
    return url[url.index(':') + 1:]


def format_fitting_url(fitting):
    return u'{}:{}'.format(SCHEME, sm.GetService('fittingSvc').GetStringForFitting(fitting))
