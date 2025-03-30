#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dogma\identity.py


def get_safe_dogma_identity(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        if value is None:
            return
        raise
