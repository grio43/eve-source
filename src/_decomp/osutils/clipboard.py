#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\osutils\clipboard.py
try:
    import ctypes

    def get_clipboard_data():
        ctypes.windll.user32.OpenClipboard(0)
        pcontents = ctypes.windll.user32.GetClipboardData(1)
        data = ctypes.c_char_p(pcontents).value
        ctypes.windll.user32.CloseClipboard()
        return data


    def set_clipboard_text(text):
        GMEM_DDESHARE = 8192
        ctypes.windll.user32.OpenClipboard(0)
        ctypes.windll.user32.EmptyClipboard()
        hCd = ctypes.windll.kernel32.GlobalAlloc(GMEM_DDESHARE, len(bytes(text)) + 1)
        pchData = ctypes.windll.kernel32.GlobalLock(hCd)
        ctypes.cdll.msvcrt.strcpy(ctypes.c_char_p(pchData), bytes(text))
        ctypes.windll.kernel32.GlobalUnlock(hCd)
        ctypes.windll.user32.SetClipboardData(1, hCd)
        ctypes.windll.user32.CloseClipboard()


except ImportError:
    import blue
    get_clipboard_data = blue.clipboard.GetClipboardString
    set_clipboard_text = blue.clipboard.SetClipboardData

GetClipboardData = get_clipboard_data
SetClipboardText = set_clipboard_text
empty_clipboard = lambda : set_clipboard_text('')
EmptyClipboard = empty_clipboard
