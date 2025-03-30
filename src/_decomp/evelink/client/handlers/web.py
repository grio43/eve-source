#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evelink\client\handlers\web.py
import blue
from carbonui import uiconst
from carbonui.uicore import uicore
from menu import MenuLabel
from evelink.client.color import external_link_color_info
SCHEMES = ('http', 'https')

def register_web_handlers(registry):
    for scheme in SCHEMES:
        registry.register(scheme, handle_web_link, menu=get_menu, color_info=external_link_color_info, hint=lambda url: url)


def handle_web_link(url):
    if uicore.registry.IsModalWindowOpen():
        response = uiconst.ID_OK
    else:
        response = uicore.Message('ExternalLinkWarning', {'url': url}, uiconst.OKCANCEL, suppress=uiconst.ID_OK)
    if response == uiconst.ID_OK:
        try:
            blue.os.ShellExecute(url)
        except WindowsError as error:
            if error.winerror not in ACCEPTABLE_WINDOWS_SYSTEM_ERRORS:
                raise


ACCEPTABLE_WINDOWS_SYSTEM_ERRORS = (0, 2, 5, 1223)

def get_menu(url):
    return [(MenuLabel('/Carbon/UI/Commands/CopyURL'), blue.pyos.SetClipboardData, (url,))]
