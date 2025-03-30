#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\monolith_converters\strings.py


def sanitize_text(text):
    try:
        return text.decode('utf-8')
    except Exception:
        if isinstance(text, str):
            return str(repr(text))[1:-1]
        return str(repr(text))
