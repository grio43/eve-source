#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\avatardisplay\avatar_command.py
import log

def avcmd_restart(container, *args):
    if args:
        log.LogError('restart command does not accept any arguments')
        return
    container.Reload()


def avcmd_play_scene_anim(container, *args):
    if len(args) != 1 and len(args) != 2:
        log.LogError('play_scene_anim accepts one required argument, a behavior name, and an optional character index. %s %s' % (len(args), args))
        return
    container.PlaySceneBehavior(args[0])
