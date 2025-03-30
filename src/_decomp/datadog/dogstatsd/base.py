#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\datadog\dogstatsd\base.py
from random import random
import logging
import os
import socket
from datadog.dogstatsd.context import TimedContextManagerDecorator
from datadog.dogstatsd.route import get_default_route
from datadog.util.compat import imap, text
log = logging.getLogger('datadog.dogstatsd')

class DogStatsd(object):
    OK, WARNING, CRITICAL, UNKNOWN = (0, 1, 2, 3)

    def __init__(self, host = 'localhost', port = 8125, max_buffer_size = 50, namespace = None, constant_tags = None, use_ms = False, use_default_route = False):
        self.host = self.resolve_host(host, use_default_route)
        self.port = int(port)
        self.socket = None
        self.max_buffer_size = max_buffer_size
        self._send = self._send_to_server
        self.encoding = 'utf-8'
        env_tags = [ tag for tag in os.environ.get('DATADOG_TAGS', '').split(',') if tag ]
        if constant_tags is None:
            constant_tags = []
        self.constant_tags = constant_tags + env_tags
        self.namespace = namespace
        self.use_ms = use_ms

    def __enter__(self):
        self.open_buffer(self.max_buffer_size)
        return self

    def __exit__(self, type, value, traceback):
        self.close_buffer()

    @staticmethod
    def resolve_host(host, use_default_route):
        if not use_default_route:
            return host
        return get_default_route()

    def get_socket(self):
        if not self.socket:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.connect((self.host, self.port))
            self.socket = sock
        return self.socket

    def open_buffer(self, max_buffer_size = 50):
        self.max_buffer_size = max_buffer_size
        self.buffer = []
        self._send = self._send_to_buffer

    def close_buffer(self):
        self._send = self._send_to_server
        self._flush_buffer()

    def gauge(self, metric, value, tags = None, sample_rate = 1):
        return self._report(metric, 'g', value, tags, sample_rate)

    def increment(self, metric, value = 1, tags = None, sample_rate = 1):
        self._report(metric, 'c', value, tags, sample_rate)

    def decrement(self, metric, value = 1, tags = None, sample_rate = 1):
        metric_value = -value if value else value
        self._report(metric, 'c', metric_value, tags, sample_rate)

    def histogram(self, metric, value, tags = None, sample_rate = 1):
        self._report(metric, 'h', value, tags, sample_rate)

    def timing(self, metric, value, tags = None, sample_rate = 1):
        self._report(metric, 'ms', value, tags, sample_rate)

    def timed(self, metric = None, tags = None, sample_rate = 1, use_ms = None):
        return TimedContextManagerDecorator(self, metric, tags, sample_rate, use_ms)

    def set(self, metric, value, tags = None, sample_rate = 1):
        self._report(metric, 's', value, tags, sample_rate)

    def close_socket(self):
        if self.socket:
            self.socket.close()
            self.socket = None

    def _report(self, metric, metric_type, value, tags, sample_rate):
        if value is None:
            return
        if sample_rate != 1 and random() > sample_rate:
            return
        payload = []
        if self.constant_tags:
            if tags:
                tags = tags + self.constant_tags
            else:
                tags = self.constant_tags
        if self.namespace:
            payload.extend([self.namespace, '.'])
        payload.extend([metric,
         ':',
         value,
         '|',
         metric_type])
        if sample_rate != 1:
            payload.extend(['|@', sample_rate])
        if tags:
            payload.extend(['|#', ','.join(tags)])
        encoded = ''.join(imap(text, payload))
        self._send(encoded)

    def _send_to_server(self, packet):
        try:
            (self.socket or self.get_socket()).send(packet.encode(self.encoding))
        except socket.error:
            log.info('Error submitting packet, will try refreshing the socket')
            self.close_socket()
            try:
                self.get_socket().send(packet.encode(self.encoding))
            except socket.error:
                self.close_socket()
                log.exception('Failed to send packet with a newly bound socket')

    def _send_to_buffer(self, packet):
        self.buffer.append(packet)
        if len(self.buffer) >= self.max_buffer_size:
            self._flush_buffer()

    def _flush_buffer(self):
        self._send_to_server('\n'.join(self.buffer))
        self.buffer = []

    def _escape_event_content(self, string):
        return string.replace('\n', '\\n')

    def _escape_service_check_message(self, string):
        return string.replace('\n', '\\n').replace('m:', 'm\\:')

    def event(self, title, text, alert_type = None, aggregation_key = None, source_type_name = None, date_happened = None, priority = None, tags = None, hostname = None):
        title = self._escape_event_content(title)
        text = self._escape_event_content(text)
        if self.constant_tags:
            if tags:
                tags += self.constant_tags
            else:
                tags = self.constant_tags
        string = u'_e{%d,%d}:%s|%s' % (len(title),
         len(text),
         title,
         text)
        if date_happened:
            string = '%s|d:%d' % (string, date_happened)
        if hostname:
            string = '%s|h:%s' % (string, hostname)
        if aggregation_key:
            string = '%s|k:%s' % (string, aggregation_key)
        if priority:
            string = '%s|p:%s' % (string, priority)
        if source_type_name:
            string = '%s|s:%s' % (string, source_type_name)
        if alert_type:
            string = '%s|t:%s' % (string, alert_type)
        if tags:
            string = '%s|#%s' % (string, ','.join(tags))
        if len(string) > 8192:
            raise Exception(u'Event "%s" payload is too big (more that 8KB), event discarded' % title)
        self._send(string)

    def service_check(self, check_name, status, tags = None, timestamp = None, hostname = None, message = None):
        message = self._escape_service_check_message(message) if message is not None else ''
        string = u'_sc|{0}|{1}'.format(check_name, status)
        if timestamp:
            string = u'{0}|d:{1}'.format(string, timestamp)
        if hostname:
            string = u'{0}|h:{1}'.format(string, hostname)
        if tags:
            string = u'{0}|#{1}'.format(string, ','.join(tags))
        if message:
            string = u'{0}|m:{1}'.format(string, message)
        self._send(string)


statsd = DogStatsd()
