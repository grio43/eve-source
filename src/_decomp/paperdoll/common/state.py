#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\paperdoll\common\state.py


class State(object):
    no_recustomization = 0
    resculpting = 1
    no_existing_customization = 2
    full_recustomizing = 3
    force_recustomize = 4

    @staticmethod
    def internal_name(state):
        return _STATE_INTERNAL_NAMES[state]


_STATE_INTERNAL_NAMES = {State.no_recustomization: 'No re-customization',
 State.resculpting: 'Re-sculpting',
 State.no_existing_customization: 'No existing data',
 State.full_recustomizing: 'Full bloodline, gender, sculpting',
 State.force_recustomize: 'Force re-customization'}
