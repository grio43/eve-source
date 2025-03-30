#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dynamicresources\client\ess\bracket\debug\reload.py
import uthread2

@uthread2.debounce
def reload_ess_bracket():
    import gc
    from dynamicresources.client.ess.bracket.root import EssBracket
    for obj in gc.get_objects():
        if isinstance(obj, EssBracket):
            obj.close()
            obj.__init__(obj.item_id)


def __reload_update__(old_namespace):
    reload_ess_bracket()
