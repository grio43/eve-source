#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\util\utilWindows.py


def NamePopup(caption = None, label = None, setvalue = '', maxLength = None, passwordChar = None, validator = None, fixedPrefix = None):
    from eve.client.script.ui.util.namedPopup import NamePopupWnd
    wnd = NamePopupWnd.Open(caption=caption, label=label, setvalue=setvalue, maxLength=maxLength, passwordChar=passwordChar, validator=validator, prefix=fixedPrefix)
    if wnd.ShowModal() == 1:
        return wnd.result
