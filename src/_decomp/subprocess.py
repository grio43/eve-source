#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\stdlib\subprocess.py
import sys
mswindows = sys.platform == 'win32'
import os
import types
import traceback
import gc
import signal

class CalledProcessError(Exception):

    def __init__(self, returncode, cmd, output = None):
        self.returncode = returncode
        self.cmd = cmd
        self.output = output

    def __str__(self):
        return "Command '%s' returned non-zero exit status %d" % (self.cmd, self.returncode)


if mswindows:
    import threading
    import msvcrt
    import _subprocess

    class STARTUPINFO():
        dwFlags = 0
        hStdInput = None
        hStdOutput = None
        hStdError = None
        wShowWindow = 0


    class pywintypes():
        error = IOError


else:
    import select
    _has_poll = hasattr(select, 'poll')
    import errno
    import fcntl
    import pickle
    _PIPE_BUF = getattr(select, 'PIPE_BUF', 512)
__all__ = ['Popen',
 'PIPE',
 'STDOUT',
 'call',
 'check_call',
 'check_output',
 'CalledProcessError']
if mswindows:
    from _subprocess import CREATE_NEW_CONSOLE, CREATE_NEW_PROCESS_GROUP
    __all__.extend(['CREATE_NEW_CONSOLE', 'CREATE_NEW_PROCESS_GROUP'])
try:
    MAXFD = os.sysconf('SC_OPEN_MAX')
except:
    MAXFD = 256

_active = []

def _cleanup():
    for inst in _active[:]:
        res = inst._internal_poll(_deadstate=sys.maxint)
        if res is not None and res >= 0:
            try:
                _active.remove(inst)
            except ValueError:
                pass


PIPE = -1
STDOUT = -2

def _eintr_retry_call(func, *args):
    while True:
        try:
            return func(*args)
        except OSError as e:
            if e.errno == errno.EINTR:
                continue
            raise


def _args_from_interpreter_flags():
    flag_opt_map = {'debug': 'd',
     'optimize': 'O',
     'dont_write_bytecode': 'B',
     'no_user_site': 's',
     'no_site': 'S',
     'ignore_environment': 'E',
     'verbose': 'v',
     'bytes_warning': 'b',
     'py3k_warning': '3'}
    args = []
    for flag, opt in flag_opt_map.items():
        v = getattr(sys.flags, flag)
        if v > 0:
            args.append('-' + opt * v)

    for opt in sys.warnoptions:
        args.append('-W' + opt)

    return args


def call(*popenargs, **kwargs):
    return Popen(*popenargs, **kwargs).wait()


def check_call(*popenargs, **kwargs):
    retcode = call(*popenargs, **kwargs)
    if retcode:
        cmd = kwargs.get('args')
        if cmd is None:
            cmd = popenargs[0]
        raise CalledProcessError(retcode, cmd)
    return 0


def check_output(*popenargs, **kwargs):
    if 'stdout' in kwargs:
        raise ValueError('stdout argument not allowed, it will be overridden.')
    process = Popen(stdout=PIPE, *popenargs, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    if retcode:
        cmd = kwargs.get('args')
        if cmd is None:
            cmd = popenargs[0]
        raise CalledProcessError(retcode, cmd, output=output)
    return output


def list2cmdline(seq):
    result = []
    needquote = False
    for arg in seq:
        bs_buf = []
        if result:
            result.append(' ')
        needquote = ' ' in arg or '\t' in arg or not arg
        if needquote:
            result.append('"')
        for c in arg:
            if c == '\\':
                bs_buf.append(c)
            elif c == '"':
                result.append('\\' * len(bs_buf) * 2)
                bs_buf = []
                result.append('\\"')
            else:
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)

        if bs_buf:
            result.extend(bs_buf)
        if needquote:
            result.extend(bs_buf)
            result.append('"')

    return ''.join(result)


class Popen(object):

    def __init__(self, args, bufsize = 0, executable = None, stdin = None, stdout = None, stderr = None, preexec_fn = None, close_fds = False, shell = False, cwd = None, env = None, universal_newlines = False, startupinfo = None, creationflags = 0):
        _cleanup()
        self._child_created = False
        if not isinstance(bufsize, (int, long)):
            raise TypeError('bufsize must be an integer')
        if mswindows:
            if preexec_fn is not None:
                raise ValueError('preexec_fn is not supported on Windows platforms')
            if close_fds and (stdin is not None or stdout is not None or stderr is not None):
                raise ValueError('close_fds is not supported on Windows platforms if you redirect stdin/stdout/stderr')
        else:
            if startupinfo is not None:
                raise ValueError('startupinfo is only supported on Windows platforms')
            if creationflags != 0:
                raise ValueError('creationflags is only supported on Windows platforms')
        self.stdin = None
        self.stdout = None
        self.stderr = None
        self.pid = None
        self.returncode = None
        self.universal_newlines = universal_newlines
        p2cread, p2cwrite, c2pread, c2pwrite, errread, errwrite = self._get_handles(stdin, stdout, stderr)
        self._execute_child(args, executable, preexec_fn, close_fds, cwd, env, universal_newlines, startupinfo, creationflags, shell, p2cread, p2cwrite, c2pread, c2pwrite, errread, errwrite)
        if mswindows:
            if p2cwrite is not None:
                p2cwrite = msvcrt.open_osfhandle(p2cwrite.Detach(), 0)
            if c2pread is not None:
                c2pread = msvcrt.open_osfhandle(c2pread.Detach(), 0)
            if errread is not None:
                errread = msvcrt.open_osfhandle(errread.Detach(), 0)
        if p2cwrite is not None:
            self.stdin = os.fdopen(p2cwrite, 'wb', bufsize)
        if c2pread is not None:
            if universal_newlines:
                self.stdout = os.fdopen(c2pread, 'rU', bufsize)
            else:
                self.stdout = os.fdopen(c2pread, 'rb', bufsize)
        if errread is not None:
            if universal_newlines:
                self.stderr = os.fdopen(errread, 'rU', bufsize)
            else:
                self.stderr = os.fdopen(errread, 'rb', bufsize)

    def _translate_newlines(self, data):
        data = data.replace('\r\n', '\n')
        data = data.replace('\r', '\n')
        return data

    def __del__(self, _maxint = sys.maxint, _active = _active):
        if not self._child_created:
            return
        self._internal_poll(_deadstate=_maxint)
        if self.returncode is None and _active is not None:
            _active.append(self)

    def communicate(self, input = None):
        if [self.stdin, self.stdout, self.stderr].count(None) >= 2:
            stdout = None
            stderr = None
            if self.stdin:
                if input:
                    self.stdin.write(input)
                self.stdin.close()
            elif self.stdout:
                stdout = self.stdout.read()
                self.stdout.close()
            elif self.stderr:
                stderr = self.stderr.read()
                self.stderr.close()
            self.wait()
            return (stdout, stderr)
        return self._communicate(input)

    def poll(self):
        return self._internal_poll()

    if mswindows:

        def _get_handles(self, stdin, stdout, stderr):
            if stdin is None and stdout is None and stderr is None:
                return (None, None, None, None, None, None)
            p2cread, p2cwrite = (None, None)
            c2pread, c2pwrite = (None, None)
            errread, errwrite = (None, None)
            if stdin is None:
                p2cread = _subprocess.GetStdHandle(_subprocess.STD_INPUT_HANDLE)
                if p2cread is None:
                    p2cread, _ = _subprocess.CreatePipe(None, 0)
            elif stdin == PIPE:
                p2cread, p2cwrite = _subprocess.CreatePipe(None, 0)
            elif isinstance(stdin, int):
                p2cread = msvcrt.get_osfhandle(stdin)
            else:
                p2cread = msvcrt.get_osfhandle(stdin.fileno())
            p2cread = self._make_inheritable(p2cread)
            if stdout is None:
                c2pwrite = _subprocess.GetStdHandle(_subprocess.STD_OUTPUT_HANDLE)
                if c2pwrite is None:
                    _, c2pwrite = _subprocess.CreatePipe(None, 0)
            elif stdout == PIPE:
                c2pread, c2pwrite = _subprocess.CreatePipe(None, 0)
            elif isinstance(stdout, int):
                c2pwrite = msvcrt.get_osfhandle(stdout)
            else:
                c2pwrite = msvcrt.get_osfhandle(stdout.fileno())
            c2pwrite = self._make_inheritable(c2pwrite)
            if stderr is None:
                errwrite = _subprocess.GetStdHandle(_subprocess.STD_ERROR_HANDLE)
                if errwrite is None:
                    _, errwrite = _subprocess.CreatePipe(None, 0)
            elif stderr == PIPE:
                errread, errwrite = _subprocess.CreatePipe(None, 0)
            elif stderr == STDOUT:
                errwrite = c2pwrite
            elif isinstance(stderr, int):
                errwrite = msvcrt.get_osfhandle(stderr)
            else:
                errwrite = msvcrt.get_osfhandle(stderr.fileno())
            errwrite = self._make_inheritable(errwrite)
            return (p2cread,
             p2cwrite,
             c2pread,
             c2pwrite,
             errread,
             errwrite)

        def _make_inheritable(self, handle):
            return _subprocess.DuplicateHandle(_subprocess.GetCurrentProcess(), handle, _subprocess.GetCurrentProcess(), 0, 1, _subprocess.DUPLICATE_SAME_ACCESS)

        def _find_w9xpopen(self):
            w9xpopen = os.path.join(os.path.dirname(_subprocess.GetModuleFileName(0)), 'w9xpopen.exe')
            if not os.path.exists(w9xpopen):
                w9xpopen = os.path.join(os.path.dirname(sys.exec_prefix), 'w9xpopen.exe')
                if not os.path.exists(w9xpopen):
                    raise RuntimeError('Cannot locate w9xpopen.exe, which is needed for Popen to work with your shell or platform.')
            return w9xpopen

        def _execute_child(self, args, executable, preexec_fn, close_fds, cwd, env, universal_newlines, startupinfo, creationflags, shell, p2cread, p2cwrite, c2pread, c2pwrite, errread, errwrite):
            if not isinstance(args, types.StringTypes):
                args = list2cmdline(args)
            if startupinfo is None:
                startupinfo = STARTUPINFO()
            if None not in (p2cread, c2pwrite, errwrite):
                startupinfo.dwFlags |= _subprocess.STARTF_USESTDHANDLES
                startupinfo.hStdInput = p2cread
                startupinfo.hStdOutput = c2pwrite
                startupinfo.hStdError = errwrite
            if shell:
                startupinfo.dwFlags |= _subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = _subprocess.SW_HIDE
                comspec = os.environ.get('COMSPEC', 'cmd.exe')
                args = '{} /c "{}"'.format(comspec, args)
                if _subprocess.GetVersion() >= 2147483648L or os.path.basename(comspec).lower() == 'command.com':
                    w9xpopen = self._find_w9xpopen()
                    args = '"%s" %s' % (w9xpopen, args)
                    creationflags |= _subprocess.CREATE_NEW_CONSOLE
            try:
                hp, ht, pid, tid = _subprocess.CreateProcess(executable, args, None, None, int(not close_fds), creationflags, env, cwd, startupinfo)
            except pywintypes.error as e:
                raise WindowsError(*e.args)
            finally:
                if p2cread is not None:
                    p2cread.Close()
                if c2pwrite is not None:
                    c2pwrite.Close()
                if errwrite is not None:
                    errwrite.Close()

            self._child_created = True
            self._handle = hp
            self.pid = pid
            ht.Close()

        def _internal_poll(self, _deadstate = None, _WaitForSingleObject = _subprocess.WaitForSingleObject, _WAIT_OBJECT_0 = _subprocess.WAIT_OBJECT_0, _GetExitCodeProcess = _subprocess.GetExitCodeProcess):
            if self.returncode is None:
                if _WaitForSingleObject(self._handle, 0) == _WAIT_OBJECT_0:
                    self.returncode = _GetExitCodeProcess(self._handle)
            return self.returncode

        def wait(self):
            if self.returncode is None:
                _subprocess.WaitForSingleObject(self._handle, _subprocess.INFINITE)
                self.returncode = _subprocess.GetExitCodeProcess(self._handle)
            return self.returncode

        def _readerthread(self, fh, buffer):
            buffer.append(fh.read())

        def _communicate(self, input):
            stdout = None
            stderr = None
            if self.stdout:
                stdout = []
                stdout_thread = threading.Thread(target=self._readerthread, args=(self.stdout, stdout))
                stdout_thread.setDaemon(True)
                stdout_thread.start()
            if self.stderr:
                stderr = []
                stderr_thread = threading.Thread(target=self._readerthread, args=(self.stderr, stderr))
                stderr_thread.setDaemon(True)
                stderr_thread.start()
            if self.stdin:
                if input is not None:
                    self.stdin.write(input)
                self.stdin.close()
            if self.stdout:
                stdout_thread.join()
            if self.stderr:
                stderr_thread.join()
            if stdout is not None:
                stdout = stdout[0]
            if stderr is not None:
                stderr = stderr[0]
            if self.universal_newlines and hasattr(file, 'newlines'):
                if stdout:
                    stdout = self._translate_newlines(stdout)
                if stderr:
                    stderr = self._translate_newlines(stderr)
            self.wait()
            return (stdout, stderr)

        def send_signal(self, sig):
            if sig == signal.SIGTERM:
                self.terminate()
            elif sig == signal.CTRL_C_EVENT:
                os.kill(self.pid, signal.CTRL_C_EVENT)
            elif sig == signal.CTRL_BREAK_EVENT:
                os.kill(self.pid, signal.CTRL_BREAK_EVENT)
            else:
                raise ValueError('Unsupported signal: {}'.format(sig))

        def terminate(self):
            _subprocess.TerminateProcess(self._handle, 1)

        kill = terminate
    else:

        def _get_handles(self, stdin, stdout, stderr):
            p2cread, p2cwrite = (None, None)
            c2pread, c2pwrite = (None, None)
            errread, errwrite = (None, None)
            if stdin is None:
                pass
            elif stdin == PIPE:
                p2cread, p2cwrite = os.pipe()
            elif isinstance(stdin, int):
                p2cread = stdin
            else:
                p2cread = stdin.fileno()
            if stdout is None:
                pass
            elif stdout == PIPE:
                c2pread, c2pwrite = os.pipe()
            elif isinstance(stdout, int):
                c2pwrite = stdout
            else:
                c2pwrite = stdout.fileno()
            if stderr is None:
                pass
            elif stderr == PIPE:
                errread, errwrite = os.pipe()
            elif stderr == STDOUT:
                errwrite = c2pwrite
            elif isinstance(stderr, int):
                errwrite = stderr
            else:
                errwrite = stderr.fileno()
            return (p2cread,
             p2cwrite,
             c2pread,
             c2pwrite,
             errread,
             errwrite)

        def _set_cloexec_flag(self, fd):
            try:
                cloexec_flag = fcntl.FD_CLOEXEC
            except AttributeError:
                cloexec_flag = 1

            old = fcntl.fcntl(fd, fcntl.F_GETFD)
            fcntl.fcntl(fd, fcntl.F_SETFD, old | cloexec_flag)

        def _close_fds(self, but):
            if hasattr(os, 'closerange'):
                os.closerange(3, but)
                os.closerange(but + 1, MAXFD)
            else:
                for i in xrange(3, MAXFD):
                    if i == but:
                        continue
                    try:
                        os.close(i)
                    except:
                        pass

        def _execute_child(self, args, executable, preexec_fn, close_fds, cwd, env, universal_newlines, startupinfo, creationflags, shell, p2cread, p2cwrite, c2pread, c2pwrite, errread, errwrite):
            if isinstance(args, types.StringTypes):
                args = [args]
            else:
                args = list(args)
            if shell:
                args = ['/bin/sh', '-c'] + args
                if executable:
                    args[0] = executable
            if executable is None:
                executable = args[0]
            errpipe_read, errpipe_write = os.pipe()
            try:
                try:
                    self._set_cloexec_flag(errpipe_write)
                    gc_was_enabled = gc.isenabled()
                    gc.disable()
                    try:
                        self.pid = os.fork()
                    except:
                        if gc_was_enabled:
                            gc.enable()
                        raise

                    self._child_created = True
                    if self.pid == 0:
                        try:
                            if p2cwrite is not None:
                                os.close(p2cwrite)
                            if c2pread is not None:
                                os.close(c2pread)
                            if errread is not None:
                                os.close(errread)
                            os.close(errpipe_read)
                            if p2cread is not None:
                                os.dup2(p2cread, 0)
                            if c2pwrite is not None:
                                os.dup2(c2pwrite, 1)
                            if errwrite is not None:
                                os.dup2(errwrite, 2)
                            if p2cread is not None and p2cread not in (0,):
                                os.close(p2cread)
                            if c2pwrite is not None and c2pwrite not in (p2cread, 1):
                                os.close(c2pwrite)
                            if errwrite is not None and errwrite not in (p2cread, c2pwrite, 2):
                                os.close(errwrite)
                            if close_fds:
                                self._close_fds(but=errpipe_write)
                            if cwd is not None:
                                os.chdir(cwd)
                            if preexec_fn:
                                preexec_fn()
                            if env is None:
                                os.execvp(executable, args)
                            else:
                                os.execvpe(executable, args, env)
                        except:
                            exc_type, exc_value, tb = sys.exc_info()
                            exc_lines = traceback.format_exception(exc_type, exc_value, tb)
                            exc_value.child_traceback = ''.join(exc_lines)
                            os.write(errpipe_write, pickle.dumps(exc_value))

                        os._exit(255)
                    if gc_was_enabled:
                        gc.enable()
                finally:
                    os.close(errpipe_write)

                if p2cread is not None and p2cwrite is not None:
                    os.close(p2cread)
                if c2pwrite is not None and c2pread is not None:
                    os.close(c2pwrite)
                if errwrite is not None and errread is not None:
                    os.close(errwrite)
                data = _eintr_retry_call(os.read, errpipe_read, 1048576)
            finally:
                os.close(errpipe_read)

            if data != '':
                _eintr_retry_call(os.waitpid, self.pid, 0)
                child_exception = pickle.loads(data)
                for fd in (p2cwrite, c2pread, errread):
                    if fd is not None:
                        os.close(fd)

                raise child_exception

        def _handle_exitstatus(self, sts, _WIFSIGNALED = os.WIFSIGNALED, _WTERMSIG = os.WTERMSIG, _WIFEXITED = os.WIFEXITED, _WEXITSTATUS = os.WEXITSTATUS):
            if _WIFSIGNALED(sts):
                self.returncode = -_WTERMSIG(sts)
            elif _WIFEXITED(sts):
                self.returncode = _WEXITSTATUS(sts)
            else:
                raise RuntimeError('Unknown child exit status!')

        def _internal_poll(self, _deadstate = None, _waitpid = os.waitpid, _WNOHANG = os.WNOHANG, _os_error = os.error):
            if self.returncode is None:
                try:
                    pid, sts = _waitpid(self.pid, _WNOHANG)
                    if pid == self.pid:
                        self._handle_exitstatus(sts)
                except _os_error:
                    if _deadstate is not None:
                        self.returncode = _deadstate

            return self.returncode

        def wait(self):
            if self.returncode is None:
                pid, sts = _eintr_retry_call(os.waitpid, self.pid, 0)
                self._handle_exitstatus(sts)
            return self.returncode

        def _communicate(self, input):
            if self.stdin:
                self.stdin.flush()
                if not input:
                    self.stdin.close()
            if _has_poll:
                stdout, stderr = self._communicate_with_poll(input)
            else:
                stdout, stderr = self._communicate_with_select(input)
            if stdout is not None:
                stdout = ''.join(stdout)
            if stderr is not None:
                stderr = ''.join(stderr)
            if self.universal_newlines and hasattr(file, 'newlines'):
                if stdout:
                    stdout = self._translate_newlines(stdout)
                if stderr:
                    stderr = self._translate_newlines(stderr)
            self.wait()
            return (stdout, stderr)

        def _communicate_with_poll(self, input):
            stdout = None
            stderr = None
            fd2file = {}
            fd2output = {}
            poller = select.poll()

            def register_and_append(file_obj, eventmask):
                poller.register(file_obj.fileno(), eventmask)
                fd2file[file_obj.fileno()] = file_obj

            def close_unregister_and_remove(fd):
                poller.unregister(fd)
                fd2file[fd].close()
                fd2file.pop(fd)

            if self.stdin and input:
                register_and_append(self.stdin, select.POLLOUT)
            select_POLLIN_POLLPRI = select.POLLIN | select.POLLPRI
            if self.stdout:
                register_and_append(self.stdout, select_POLLIN_POLLPRI)
                fd2output[self.stdout.fileno()] = stdout = []
            if self.stderr:
                register_and_append(self.stderr, select_POLLIN_POLLPRI)
                fd2output[self.stderr.fileno()] = stderr = []
            input_offset = 0
            while fd2file:
                try:
                    ready = poller.poll()
                except select.error as e:
                    if e.args[0] == errno.EINTR:
                        continue
                    raise

                for fd, mode in ready:
                    if mode & select.POLLOUT:
                        chunk = input[input_offset:input_offset + _PIPE_BUF]
                        input_offset += os.write(fd, chunk)
                        if input_offset >= len(input):
                            close_unregister_and_remove(fd)
                    elif mode & select_POLLIN_POLLPRI:
                        data = os.read(fd, 4096)
                        if not data:
                            close_unregister_and_remove(fd)
                        fd2output[fd].append(data)
                    else:
                        close_unregister_and_remove(fd)

            return (stdout, stderr)

        def _communicate_with_select(self, input):
            read_set = []
            write_set = []
            stdout = None
            stderr = None
            if self.stdin and input:
                write_set.append(self.stdin)
            if self.stdout:
                read_set.append(self.stdout)
                stdout = []
            if self.stderr:
                read_set.append(self.stderr)
                stderr = []
            input_offset = 0
            while read_set or write_set:
                try:
                    rlist, wlist, xlist = select.select(read_set, write_set, [])
                except select.error as e:
                    if e.args[0] == errno.EINTR:
                        continue
                    raise

                if self.stdin in wlist:
                    chunk = input[input_offset:input_offset + _PIPE_BUF]
                    bytes_written = os.write(self.stdin.fileno(), chunk)
                    input_offset += bytes_written
                    if input_offset >= len(input):
                        self.stdin.close()
                        write_set.remove(self.stdin)
                if self.stdout in rlist:
                    data = os.read(self.stdout.fileno(), 1024)
                    if data == '':
                        self.stdout.close()
                        read_set.remove(self.stdout)
                    stdout.append(data)
                if self.stderr in rlist:
                    data = os.read(self.stderr.fileno(), 1024)
                    if data == '':
                        self.stderr.close()
                        read_set.remove(self.stderr)
                    stderr.append(data)

            return (stdout, stderr)

        def send_signal(self, sig):
            os.kill(self.pid, sig)

        def terminate(self):
            self.send_signal(signal.SIGTERM)

        def kill(self):
            self.send_signal(signal.SIGKILL)


def _demo_posix():
    plist = Popen(['ps'], stdout=PIPE).communicate()[0]
    print 'Process list:'
    print plist
    if os.getuid() == 0:
        p = Popen(['id'], preexec_fn=lambda : os.setuid(100))
        p.wait()
    print "Looking for 'hda'..."
    p1 = Popen(['dmesg'], stdout=PIPE)
    p2 = Popen(['grep', 'hda'], stdin=p1.stdout, stdout=PIPE)
    print repr(p2.communicate()[0])
    print
    print 'Trying a weird file...'
    try:
        print Popen(['/this/path/does/not/exist']).communicate()
    except OSError as e:
        if e.errno == errno.ENOENT:
            print "The file didn't exist.  I thought so..."
            print 'Child traceback:'
            print e.child_traceback
        else:
            print 'Error', e.errno
    else:
        print >> sys.stderr, 'Gosh.  No error.'


def _demo_windows():
    print "Looking for 'PROMPT' in set output..."
    p1 = Popen('set', stdout=PIPE, shell=True)
    p2 = Popen('find "PROMPT"', stdin=p1.stdout, stdout=PIPE)
    print repr(p2.communicate()[0])
    print 'Executing calc...'
    p = Popen('calc')
    p.wait()


if __name__ == '__main__':
    if mswindows:
        _demo_windows()
    else:
        _demo_posix()
