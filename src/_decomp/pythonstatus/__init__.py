#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\pythonstatus\__init__.py
import sys
import traceback
import cStringIO
import collections
import json
import zlib
import bluepy
SLEEPERS = ['blue.synchro.Yield',
 'blue.synchro.Sleep',
 'blue.pyos.synchro.Yield',
 'blue.synchro.SleepWallclock',
 'blue.pyos.synchro.SleepWallclock',
 'blue.synchro.SleepSim',
 'blue.pyos.synchro.SleepSim']

def getstackid(stack):
    return str(zlib.adler32(stack))


def pythonstatus():
    status = collections.OrderedDict()
    taskletlist = []
    threadlist = []
    sleepers = 0
    for t in bluepy.tasklets.keys():
        if not t.alive:
            continue
        tasklet_id = t.tasklet_id
        ctx = (getattr(t, 'context', '(unknown)'),)
        stack = traceback.extract_stack(t.frame)
        filename, lineno, name, code = stack[-1]
        if code:
            funcname = code.split('(')[0]
            if funcname in SLEEPERS:
                sleepers += 1
                continue
        stack = cStringIO.StringIO()
        traceback.print_stack(t.frame, file=stack)
        stackstr = stack.getvalue()
        item = collections.OrderedDict()
        item['id'] = tasklet_id
        item['context'] = str(ctx)
        item['repr'] = repr(t)
        item['stack'] = stackstr
        item['stackid'] = getstackid(stackstr)
        taskletlist.append(item)

    status['sleepers'] = sleepers
    for thread_id, frame in sys._current_frames().iteritems():
        item = collections.OrderedDict()
        item['id'] = thread_id
        stack = cStringIO.StringIO()
        traceback.print_stack(frame, file=stack)
        stackstr = stack.getvalue()
        item['stack'] = stackstr
        item['stackid'] = getstackid(stackstr)
        threadlist.append(item)

    import logmodule as log
    statusMsg = '!! pythonstatus\n' + json.dumps(status, indent=4, separators=(',', ': '))
    log.general.Log(statusMsg, log.LGERR)
    for thread in threadlist:
        log.general.Log('!! pythonstatus\nid=%s\nstackid=%s\nstack=%s' % (thread['id'], thread['stackid'], thread['stack']), log.LGERR)
