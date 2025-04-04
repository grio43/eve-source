#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\datadog\dogshell\wrap.py
import optparse
import subprocess
import sys
import threading
import time
from datadog import initialize, api
from datadog.util.config import get_version
SUCCESS = 'success'
ERROR = 'error'
MAX_EVENT_BODY_LENGTH = 3000

class Timeout(Exception):
    pass


class OutputReader(threading.Thread):

    def __init__(self, proc_out, fwd_out = None):
        threading.Thread.__init__(self)
        self.daemon = True
        self._out_content = u''
        self._out = proc_out
        self._fwd_out = fwd_out

    def run(self):
        for line in iter(self._out.readline, ''):
            if self._fwd_out is not None:
                self._fwd_out.write(line)
            line = line.decode('utf-8')
            self._out_content += line

        self._out.close()

    @property
    def content(self):
        return self._out_content


def poll_proc(proc, sleep_interval, timeout):
    start_time = time.time()
    returncode = None
    while returncode is None:
        returncode = proc.poll()
        if time.time() - start_time > timeout:
            raise Timeout()
        else:
            time.sleep(sleep_interval)

    return returncode


def execute(cmd, cmd_timeout, sigterm_timeout, sigkill_timeout, proc_poll_interval, buffer_outs):
    start_time = time.time()
    returncode = -1
    stdout = ''
    stderr = ''
    try:
        proc = subprocess.Popen(u' '.join(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    except Exception:
        print >> sys.stderr, u'Failed to execute %s' % repr(cmd)
        raise

    try:
        out_reader = OutputReader(proc.stdout, sys.stdout if not buffer_outs else None)
        err_reader = OutputReader(proc.stderr, sys.stderr if not buffer_outs else None)
        out_reader.start()
        err_reader.start()
        returncode = poll_proc(proc, proc_poll_interval, cmd_timeout)
        out_reader.join()
        err_reader.join()
        stdout = out_reader.content
        stderr = err_reader.content
        duration = time.time() - start_time
    except Timeout:
        duration = time.time() - start_time
        try:
            proc.terminate()
            sigterm_start = time.time()
            try:
                print >> sys.stderr, 'Command timed out after %.2fs, killing with SIGTERM' % (time.time() - start_time)
                poll_proc(proc, proc_poll_interval, sigterm_timeout)
                returncode = Timeout
            except Timeout:
                print >> sys.stderr, 'SIGTERM timeout failed after %.2fs, killing with SIGKILL' % (time.time() - sigterm_start)
                proc.kill()
                poll_proc(proc, proc_poll_interval, sigkill_timeout)
                returncode = Timeout

        except OSError as e:
            if e.errno != 3:
                raise

    return (returncode,
     stdout,
     stderr,
     duration)


def trim_text(text, max_len):
    if len(text) <= max_len:
        return text
    trimmed_text = u'{top_third}\n```\n*...trimmed...*\n```\n{bottom_two_third}\n'.format(top_third=text[:max_len / 3], bottom_two_third=text[len(text) - 2 * max_len / 3:])
    return trimmed_text


def build_event_body(cmd, returncode, stdout, stderr, notifications):
    fmt_stdout = u''
    fmt_stderr = u''
    fmt_notifications = u''
    max_length = MAX_EVENT_BODY_LENGTH / 2 if stdout and stderr else MAX_EVENT_BODY_LENGTH
    if stdout:
        fmt_stdout = u'**>>>> STDOUT <<<<**\n```\n{stdout} \n```\n'.format(stdout=trim_text(stdout, max_length))
    if stderr:
        fmt_stderr = u'**>>>> STDERR <<<<**\n```\n{stderr} \n```\n'.format(stderr=trim_text(stderr, max_length))
    if notifications:
        fmt_notifications = u'**>>>> NOTIFICATIONS <<<<**\n\n {notifications}\n'.format(notifications=notifications)
    return u'%%%\n**>>>> CMD <<<<**\n```\n{command} \n```\n**>>>> EXIT CODE <<<<**\n\n {returncode}\n\n\n{stdout}{stderr}{notifications}%%%\n'.format(command=u' '.join(cmd), returncode=returncode, stdout=fmt_stdout, stderr=fmt_stderr, notifications=fmt_notifications)


def main():
    parser = optparse.OptionParser(usage='%prog -n [event_name] -k [api_key] --submit_mode [ all | errors ] [options] "command". \n\nNote that you need to enclose your command in quotes to prevent python as soon as there is a space in your command. \n \nNOTICE: In normal mode, the whole stderr is printed before stdout, in flush_live mode they will be mixed but there is not guarantee that messages sent by the command on both stderr and stdout are printed in the order they were sent.', version='%prog {0}'.format(get_version()))
    parser.add_option('-n', '--name', action='store', type='string', help='the name of the event as it should appear on your Datadog stream')
    parser.add_option('-k', '--api_key', action='store', type='string', help='your DataDog API Key')
    parser.add_option('-m', '--submit_mode', action='store', type='choice', default='errors', choices=['errors', 'all'], help='[ all | errors ] if set to error, an event will be sent only of the command exits with a non zero exit status or if it times out.')
    parser.add_option('-p', '--priority', action='store', type='choice', choices=['normal', 'low'], help="the priority of the event (default: 'normal')")
    parser.add_option('-t', '--timeout', action='store', type='int', default=86400, help='(in seconds)  a timeout after which your command must be aborted. An event will be sent to your DataDog stream (default: 24hours)')
    parser.add_option('--sigterm_timeout', action='store', type='int', default=120, help='(in seconds)  When your command times out, the process it triggers is sent a SIGTERM. If this sigterm_timeout is reached, it will be sent a SIGKILL signal. (default: 2m)')
    parser.add_option('--sigkill_timeout', action='store', type='int', default=60, help='(in seconds) how long to wait at most after SIGKILL                               has been sent (default: 60s)')
    parser.add_option('--proc_poll_interval', action='store', type='float', default=0.5, help='(in seconds). interval at which your command will be polled (default: 500ms)')
    parser.add_option('--notify_success', action='store', type='string', default='', help='a message string and @people directives to send notifications in case of success.')
    parser.add_option('--notify_error', action='store', type='string', default='', help='a message string and @people directives to send notifications in case of error.')
    parser.add_option('-b', '--buffer_outs', action='store_true', dest='buffer_outs', default=False, help='displays the stderr and stdout of the command only once it has returned (the command outputs remains buffered in dogwrap meanwhile)')
    parser.add_option('--tags', action='store', type='string', dest='tags', default='', help='comma separated list of tags')
    options, args = parser.parse_args()
    cmd = []
    for part in args:
        cmd.extend(part.split(' '))

    returncode, stdout, stderr, duration = execute(cmd, options.timeout, options.sigterm_timeout, options.sigkill_timeout, options.proc_poll_interval, options.buffer_outs)
    initialize(api_key=options.api_key)
    host = api._host_name
    if returncode == 0:
        alert_type = SUCCESS
        event_priority = 'low'
        event_title = u'[%s] %s succeeded in %.2fs' % (host, options.name, duration)
    else:
        alert_type = ERROR
        event_priority = 'normal'
        if returncode is Timeout:
            event_title = u'[%s] %s timed out after %.2fs' % (host, options.name, duration)
            returncode = -1
        else:
            event_title = u'[%s] %s failed in %.2fs' % (host, options.name, duration)
    notifications = ''
    if alert_type == SUCCESS and options.notify_success:
        notifications = options.notify_success
    elif alert_type == ERROR and options.notify_error:
        notifications = options.notify_error
    if options.tags:
        tags = [ t.strip() for t in options.tags.split(',') ]
    else:
        tags = None
    event_body = build_event_body(cmd, returncode, stdout, stderr, notifications)
    event = {'alert_type': alert_type,
     'aggregation_key': options.name,
     'host': host,
     'priority': options.priority or event_priority,
     'tags': tags}
    if options.buffer_outs:
        print >> sys.stderr, stderr.strip()
        print >> sys.stdout, stdout.strip()
    if options.submit_mode == 'all' or returncode != 0:
        api.Event.create(title=event_title, text=event_body, **event)
    sys.exit(returncode)


if __name__ == '__main__':
    main()
