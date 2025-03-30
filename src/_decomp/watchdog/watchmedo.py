#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\watchdog\watchmedo.py
import errno
import os
import os.path
import sys
import yaml
import time
import logging
try:
    from cStringIO import StringIO
except ImportError:
    try:
        from StringIO import StringIO
    except ImportError:
        from io import StringIO

from argh import arg, aliases, ArghParser, expects_obj
from watchdog.version import VERSION_STRING
from watchdog.utils import WatchdogShutdown, load_class
logging.basicConfig(level=logging.INFO)
CONFIG_KEY_TRICKS = 'tricks'
CONFIG_KEY_PYTHON_PATH = 'python-path'

def path_split(pathname_spec, separator = os.pathsep):
    return list(pathname_spec.split(separator))


def add_to_sys_path(pathnames, index = 0):
    for pathname in pathnames[::-1]:
        sys.path.insert(index, pathname)


def load_config(tricks_file_pathname):
    with open(tricks_file_pathname, 'rb') as f:
        return yaml.safe_load(f.read())


def parse_patterns(patterns_spec, ignore_patterns_spec, separator = ';'):
    patterns = patterns_spec.split(separator)
    ignore_patterns = ignore_patterns_spec.split(separator)
    if ignore_patterns == ['']:
        ignore_patterns = []
    return (patterns, ignore_patterns)


def observe_with(observer, event_handler, pathnames, recursive):
    for pathname in set(pathnames):
        observer.schedule(event_handler, pathname, recursive)

    observer.start()
    try:
        while True:
            time.sleep(1)

    except WatchdogShutdown:
        observer.stop()

    observer.join()


def schedule_tricks(observer, tricks, pathname, recursive):
    for trick in tricks:
        for name, value in list(trick.items()):
            TrickClass = load_class(name)
            handler = TrickClass(**value)
            trick_pathname = getattr(handler, 'source_directory', None) or pathname
            observer.schedule(handler, trick_pathname, recursive)


@aliases('tricks')
@arg('files', nargs='*', help='perform tricks from given file')
@arg('--python-path', default='.', help='paths separated by %s to add to the python path' % os.pathsep)
@arg('--interval', '--timeout', dest='timeout', default=1.0, help='use this as the polling interval/blocking timeout (in seconds)')
@arg('--recursive', default=True, help='recursively monitor paths')
@expects_obj
def tricks_from(args):
    from watchdog.observers import Observer
    add_to_sys_path(path_split(args.python_path))
    observers = []
    for tricks_file in args.files:
        observer = Observer(timeout=args.timeout)
        if not os.path.exists(tricks_file):
            raise OSError(errno.ENOENT, os.strerror(errno.ENOENT), tricks_file)
        config = load_config(tricks_file)
        try:
            tricks = config[CONFIG_KEY_TRICKS]
        except KeyError:
            raise KeyError('No %r key specified in %s.' % (CONFIG_KEY_TRICKS, tricks_file))

        if CONFIG_KEY_PYTHON_PATH in config:
            add_to_sys_path(config[CONFIG_KEY_PYTHON_PATH])
        dir_path = os.path.dirname(tricks_file)
        if not dir_path:
            dir_path = os.path.relpath(os.getcwd())
        schedule_tricks(observer, tricks, dir_path, args.recursive)
        observer.start()
        observers.append(observer)

    try:
        while True:
            time.sleep(1)

    except WatchdogShutdown:
        for o in observers:
            o.unschedule_all()
            o.stop()

    for o in observers:
        o.join()


@aliases('generate-tricks-yaml')
@arg('trick_paths', nargs='*', help='Dotted paths for all the tricks you want to generate')
@arg('--python-path', default='.', help='paths separated by %s to add to the python path' % os.pathsep)
@arg('--append-to-file', default=None, help='appends the generated tricks YAML to a file; if not specified, prints to standard output')
@arg('-a', '--append-only', dest='append_only', default=False, help='if --append-to-file is not specified, produces output for appending instead of a complete tricks yaml file.')
@expects_obj
def tricks_generate_yaml(args):
    python_paths = path_split(args.python_path)
    add_to_sys_path(python_paths)
    output = StringIO()
    for trick_path in args.trick_paths:
        TrickClass = load_class(trick_path)
        output.write(TrickClass.generate_yaml())

    content = output.getvalue()
    output.close()
    header = yaml.dump({CONFIG_KEY_PYTHON_PATH: python_paths})
    header += '%s:\n' % CONFIG_KEY_TRICKS
    if args.append_to_file is None:
        if not args.append_only:
            content = header + content
        sys.stdout.write(content)
    else:
        if not os.path.exists(args.append_to_file):
            content = header + content
        with open(args.append_to_file, 'ab') as output:
            output.write(content)


@arg('directories', nargs='*', default='.', help='directories to watch.')
@arg('-p', '--pattern', '--patterns', dest='patterns', default='*', help='matches event paths with these patterns (separated by ;).')
@arg('-i', '--ignore-pattern', '--ignore-patterns', dest='ignore_patterns', default='', help='ignores event paths with these patterns (separated by ;).')
@arg('-D', '--ignore-directories', dest='ignore_directories', default=False, help='ignores events for directories')
@arg('-R', '--recursive', dest='recursive', default=False, help='monitors the directories recursively')
@arg('--interval', '--timeout', dest='timeout', default=1.0, help='use this as the polling interval/blocking timeout')
@arg('--trace', default=False, help='dumps complete dispatching trace')
@arg('--debug-force-polling', default=False, help='[debug] forces polling')
@arg('--debug-force-kqueue', default=False, help='[debug] forces BSD kqueue(2)')
@arg('--debug-force-winapi', default=False, help='[debug] forces Windows API')
@arg('--debug-force-winapi-async', default=False, help='[debug] forces Windows API + I/O completion')
@arg('--debug-force-fsevents', default=False, help='[debug] forces Mac OS X FSEvents')
@arg('--debug-force-inotify', default=False, help='[debug] forces Linux inotify(7)')
@expects_obj
def log(args):
    from watchdog.utils import echo
    from watchdog.tricks import LoggerTrick
    if args.trace:
        echo.echo_class(LoggerTrick)
    patterns, ignore_patterns = parse_patterns(args.patterns, args.ignore_patterns)
    handler = LoggerTrick(patterns=patterns, ignore_patterns=ignore_patterns, ignore_directories=args.ignore_directories)
    if args.debug_force_polling:
        from watchdog.observers.polling import PollingObserver as Observer
    elif args.debug_force_kqueue:
        from watchdog.observers.kqueue import KqueueObserver as Observer
    elif args.debug_force_winapi_async:
        from watchdog.observers.read_directory_changes_async import WindowsApiAsyncObserver as Observer
    elif args.debug_force_winapi:
        from watchdog.observers.read_directory_changes import WindowsApiObserver as Observer
    elif args.debug_force_inotify:
        from watchdog.observers.inotify import InotifyObserver as Observer
    elif args.debug_force_fsevents:
        from watchdog.observers.fsevents import FSEventsObserver as Observer
    else:
        from watchdog.observers import Observer
    observer = Observer(timeout=args.timeout)
    observe_with(observer, handler, args.directories, args.recursive)


@arg('directories', nargs='*', default='.', help='directories to watch')
@arg('-c', '--command', dest='command', default=None, help='shell command executed in response to matching events.\nThese interpolation variables are available to your command string::\n\n    ${watch_src_path}    - event source path;\n    ${watch_dest_path}   - event destination path (for moved events);\n    ${watch_event_type}  - event type;\n    ${watch_object}      - ``file`` or ``directory``\n\nNote::\n    Please ensure you do not use double quotes (") to quote\n    your command string. That will force your shell to\n    interpolate before the command is processed by this\n    subcommand.\n\nExample option usage::\n\n    --command=\'echo "${watch_src_path}"\'\n')
@arg('-p', '--pattern', '--patterns', dest='patterns', default='*', help='matches event paths with these patterns (separated by ;).')
@arg('-i', '--ignore-pattern', '--ignore-patterns', dest='ignore_patterns', default='', help='ignores event paths with these patterns (separated by ;).')
@arg('-D', '--ignore-directories', dest='ignore_directories', default=False, help='ignores events for directories')
@arg('-R', '--recursive', dest='recursive', default=False, help='monitors the directories recursively')
@arg('--interval', '--timeout', dest='timeout', default=1.0, help='use this as the polling interval/blocking timeout')
@arg('-w', '--wait', dest='wait_for_process', action='store_true', default=False, help='wait for process to finish to avoid multiple simultaneous instances')
@arg('-W', '--drop', dest='drop_during_process', action='store_true', default=False, help='Ignore events that occur while command is still being executed to avoid multiple simultaneous instances')
@arg('--debug-force-polling', default=False, help='[debug] forces polling')
@expects_obj
def shell_command(args):
    from watchdog.tricks import ShellCommandTrick
    if not args.command:
        args.command = None
    if args.debug_force_polling:
        from watchdog.observers.polling import PollingObserver as Observer
    else:
        from watchdog.observers import Observer
    patterns, ignore_patterns = parse_patterns(args.patterns, args.ignore_patterns)
    handler = ShellCommandTrick(shell_command=args.command, patterns=patterns, ignore_patterns=ignore_patterns, ignore_directories=args.ignore_directories, wait_for_process=args.wait_for_process, drop_during_process=args.drop_during_process)
    observer = Observer(timeout=args.timeout)
    observe_with(observer, handler, args.directories, args.recursive)


@arg('command', help='Long-running command to run in a subprocess.\n')
@arg('command_args', metavar='arg', nargs='*', help='Command arguments.\n\nNote: Use -- before the command arguments, otherwise watchmedo will\ntry to interpret them.\n')
@arg('-d', '--directory', dest='directories', metavar='directory', action='append', help='Directory to watch. Use another -d or --directory option for each directory.')
@arg('-p', '--pattern', '--patterns', dest='patterns', default='*', help='matches event paths with these patterns (separated by ;).')
@arg('-i', '--ignore-pattern', '--ignore-patterns', dest='ignore_patterns', default='', help='ignores event paths with these patterns (separated by ;).')
@arg('-D', '--ignore-directories', dest='ignore_directories', default=False, help='ignores events for directories')
@arg('-R', '--recursive', dest='recursive', default=False, help='monitors the directories recursively')
@arg('--interval', '--timeout', dest='timeout', default=1.0, help='use this as the polling interval/blocking timeout')
@arg('--signal', dest='signal', default='SIGINT', help='stop the subprocess with this signal (default SIGINT)')
@arg('--debug-force-polling', default=False, help='[debug] forces polling')
@arg('--kill-after', dest='kill_after', default=10.0, help='when stopping, kill the subprocess after the specified timeout (default 10)')
@expects_obj
def auto_restart(args):
    if args.debug_force_polling:
        from watchdog.observers.polling import PollingObserver as Observer
    else:
        from watchdog.observers import Observer
    from watchdog.tricks import AutoRestartTrick
    import signal
    if not args.directories:
        args.directories = ['.']
    if args.signal.startswith('SIG'):
        stop_signal = getattr(signal, args.signal)
    else:
        stop_signal = int(args.signal)
    termination_signals = {signal.SIGTERM, signal.SIGINT}

    def handler_termination_signal(_signum, _frame):
        for signum in termination_signals:
            signal.signal(signum, signal.SIG_IGN)

        raise WatchdogShutdown

    for signum in termination_signals:
        signal.signal(signum, handler_termination_signal)

    patterns, ignore_patterns = parse_patterns(args.patterns, args.ignore_patterns)
    command = [args.command]
    command.extend(args.command_args)
    handler = AutoRestartTrick(command=command, patterns=patterns, ignore_patterns=ignore_patterns, ignore_directories=args.ignore_directories, stop_signal=stop_signal, kill_after=args.kill_after)
    handler.start()
    observer = Observer(timeout=args.timeout)
    try:
        observe_with(observer, handler, args.directories, args.recursive)
    except WatchdogShutdown:
        pass
    finally:
        handler.stop()


epilog = 'Copyright 2011 Yesudeep Mangalapilly <yesudeep@gmail.com>.\nCopyright 2012 Google, Inc & contributors.\n\nLicensed under the terms of the Apache license, version 2.0. Please see\nLICENSE in the source code for more information.'
parser = ArghParser(epilog=epilog)
parser.add_commands([tricks_from,
 tricks_generate_yaml,
 log,
 shell_command,
 auto_restart])
parser.add_argument('--version', action='version', version='%(prog)s ' + VERSION_STRING)

def main():
    parser.dispatch()


if __name__ == '__main__':
    main()
