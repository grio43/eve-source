#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\osutils\outofprockiller.py
import os
import subprocess
import sys
import traceback
packagesdir = os.path.join(os.path.dirname(__file__), '..')
if packagesdir not in sys.path:
    sys.path.append(packagesdir)
import devenv
import osutils
DEFAULT_SEC = 3

def watch_and_kill(svcpid):
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    args = [devenv.PYTHON27EXE,
     __file__,
     str(os.getpid()),
     str(svcpid)]
    subprocess.Popen(args, startupinfo=startupinfo)


WatchAndKill = watch_and_kill

def Main():
    try:
        watchpid = int(sys.argv[1])
        killpid = int(sys.argv[2])
        if len(sys.argv) == 4:
            poll = float(sys.argv[3])
        else:
            poll = DEFAULT_SEC
    except Exception:
        print 'Usage: watchpid killpid <poll interval: %s sec>' % DEFAULT_SEC
        traceback.print_exc()
        sys.exit(1)

    def cb():
        osutils.kill(killpid)

    t = osutils.watch_process(watchpid, cb, sleepS=poll)
    t.join()


if __name__ == '__main__':
    Main()
