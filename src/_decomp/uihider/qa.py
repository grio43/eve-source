#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uihider\qa.py
from carbon.common.script.sys.serviceConst import ROLE_QA
from carbonui.uicore import uicore

def get_command_blocker_menu():
    return ('Command Blocker', [get_toggle_entry('Toggle override', toggle_command_blocker_override, is_command_blocker_override_enabled())])


COMMAND_BLOCKER_OVERRIDE_DEFAULT = False

def is_command_blocker_override_enabled():
    is_qa = bool(session.role & ROLE_QA)
    is_enabled = _get_command_blocker_override_enabled_setting()
    return is_qa and is_enabled


def toggle_command_blocker_override():
    enabled = not _get_command_blocker_override_enabled_setting()
    _message('Command blocker override {}'.format('enabled' if enabled else 'disabled'))
    _set_command_blocker_override_enabled_setting(enabled)


def _get_command_blocker_override_enabled_setting():
    return settings.char.ui.Get('command_blocker_qa_override_enabled', COMMAND_BLOCKER_OVERRIDE_DEFAULT)


def _set_command_blocker_override_enabled_setting(enabled):
    settings.char.ui.Set('command_blocker_qa_override_enabled', enabled)


def notify_command_block_overridden(references):
    _message('<color=#ff66aaff>[QA] Command blocker override allowed the following references to be executed:<br>{}</color>'.format(', '.join([ repr(r) for r in references ])))


def _message(text):
    uicore.Message('CustomNotify', {'notify': text})


def get_toggle_entry(label, callback, enabled):
    texture = {True: 'res:/UI/Texture/classes/insider/toggle_on_18.png',
     False: 'res:/UI/Texture/classes/insider/toggle_off_18.png'}[enabled]
    return ('{} ({})'.format(label, '<color=green>on</color>' if enabled else '<color=red>off</color>'),
     callback,
     (),
     (texture, 18))
