#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\stdlib\stacklesslib\monkeypatch.py
import sys
import threading as real_threading
from . import main
from . import util
from .replacements import thread, threading, popen
import log
stacklessio = None

def patch_all():
    patch_misc()
    patch_thread()
    patch_threading()
    patch_select()
    patch_socket()
    patch_ssl()


def patch_misc():
    import time
    time.sleep = main.sleep
    import os
    if hasattr(os, 'popen4'):
        os.popen4 = popen.popen4


def patch_thread():
    sys.modules['thread'] = thread


def patch_threading():
    threading.real_threading = real_threading
    sys.modules['threading'] = threading


def patch_select():
    if stacklessio:
        from stacklessio import select
    else:
        from stacklesslib.replacements import select
    sys.modules['select'] = select


def patch_socket(will_be_pumped = True):
    if stacklessio:
        from stacklessio import _socket
        sys.modules['_socket'] = _socket
    else:
        from stacklesslib.replacements import socket
        socket._sleep_func = main.sleep
        socket._schedule_func = lambda : main.sleep(0)
        if will_be_pumped:
            socket._manage_sockets_func = lambda : None
        socket.install()


def patch_ssl():
    try:
        import _ssl
        import ssl
        import socket
        import errno
        from cStringIO import StringIO
    except ImportError:
        return

    class PyBio(object):
        default_bufsize = 8192

        def __init__(self, sock, rbufsize = -1):
            self.sock = sock
            self.bufsize = self.default_bufsize if rbufsize < 0 else rbufsize
            if self.bufsize:
                self.buf = StringIO()

        def write(self, data):
            return self.try_with_error_handling('write', self.sock.send, (data,))

        def read(self, want):
            if self.bufsize:
                data = self.buf.read(want)
                if not data:
                    buf = self.try_with_error_handling('read', self.sock.recv, (self.bufsize,))
                    self.buf = StringIO(buf)
                    data = self.buf.read(want)
            else:
                data = self.try_with_error_handling('read', self.sock.recv, (want,))
            return data

        def try_with_error_handling(self, name, call, args):
            try:
                return call(*args)
            except socket.timeout:
                log.LogInfo('PAT: Bio wrapped socket.timeout')
                if self.sock.gettimeout() == 0.0:
                    if name == 'read':
                        return None
                    return 0
                raise _ssl.SSLError, 'The %s operation timed out' % (name,)
            except socket.error as e:
                log.LogInfo('PAT: Bio wrapped socket.error:', e)
                if e.errno == errno.EWOULDBLOCK:
                    if name == 'read':
                        return None
                    return 0
                raise

        def __getattr__(self, attr):
            return getattr(self.sock, attr)

    original_wrap_socket = ssl.SSLContext._wrap_socket

    def wrap_socket_with_bio(SSLContext_instance, sock, *args, **kwargs):
        bio = PyBio(sock)
        fullargs = (bio,) + args
        return util.call_on_thread(original_wrap_socket, (SSLContext_instance,) + fullargs, kwargs)

    ssl.SSLContext._wrap_socket = wrap_socket_with_bio
