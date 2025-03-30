#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\datadog\util\hostname.py
import socket
import re
import logging
import subprocess
import types
from datadog.util.compat import url_lib, is_p3k, iteritems, json
from datadog.util.config import get_config, get_os, CfgNotFound
VALID_HOSTNAME_RFC_1123_PATTERN = re.compile('^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\\-]*[a-zA-Z0-9])\\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\\-]*[A-Za-z0-9])$')
MAX_HOSTNAME_LEN = 255
log = logging.getLogger('datadog.api')

def is_valid_hostname(hostname):
    if hostname.lower() in set(['localhost',
     'localhost.localdomain',
     'localhost6.localdomain6',
     'ip6-localhost']):
        log.warning('Hostname: %s is local' % hostname)
        return False
    if len(hostname) > MAX_HOSTNAME_LEN:
        log.warning('Hostname: %s is too long (max length is  %s characters)' % (hostname, MAX_HOSTNAME_LEN))
        return False
    if VALID_HOSTNAME_RFC_1123_PATTERN.match(hostname) is None:
        log.warning('Hostname: %s is not complying with RFC 1123' % hostname)
        return False
    return True


def get_hostname():
    hostname = None
    config = None
    try:
        config = get_config()
        config_hostname = config.get('hostname')
        if config_hostname and is_valid_hostname(config_hostname):
            return config_hostname
    except CfgNotFound:
        log.info('No agent or invalid configuration file found')

    if hostname is None:
        gce_hostname = GCE.get_hostname(config)
        if gce_hostname is not None:
            if is_valid_hostname(gce_hostname):
                return gce_hostname
    if hostname is None:

        def _get_hostname_unix():
            try:
                p = subprocess.Popen(['/bin/hostname', '-f'], stdout=subprocess.PIPE)
                out, err = p.communicate()
                if p.returncode == 0:
                    if is_p3k():
                        return out.decode('utf-8').strip()
                    else:
                        return out.strip()
            except Exception:
                return None

        os_name = get_os()
        if os_name in ('mac', 'freebsd', 'linux', 'solaris'):
            unix_hostname = _get_hostname_unix()
            if unix_hostname and is_valid_hostname(unix_hostname):
                hostname = unix_hostname
    if hostname is not None and True in [ hostname.lower().startswith(p) for p in [u'ip-', u'domu'] ]:
        instanceid = EC2.get_instance_id(config)
        if instanceid:
            hostname = instanceid
    if hostname is None:
        try:
            socket_hostname = socket.gethostname()
        except socket.error:
            socket_hostname = None

        if socket_hostname and is_valid_hostname(socket_hostname):
            hostname = socket_hostname
    if hostname is None:
        log.warning(u'Unable to reliably determine host name. You can define one in your `hosts` file, or in `datadog.conf` file if you have Datadog Agent installed.')
    return hostname


def get_ec2_instance_id():
    try:
        old_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(0.25)
        try:
            return url_lib.urlopen(url_lib.Request('http://169.254.169.254/latest/meta-data/instance-id')).read()
        finally:
            socket.setdefaulttimeout(old_timeout)

    except:
        return socket.gethostname()


class GCE(object):
    URL = 'http://169.254.169.254/computeMetadata/v1/?recursive=true'
    TIMEOUT = 0.1
    SOURCE_TYPE_NAME = 'google cloud platform'
    metadata = None

    @staticmethod
    def _get_metadata(agentConfig):
        if GCE.metadata is not None:
            return GCE.metadata
        if not agentConfig['collect_instance_metadata']:
            log.info('Instance metadata collection is disabled. Not collecting it.')
            GCE.metadata = {}
            return GCE.metadata
        socket_to = None
        try:
            socket_to = socket.getdefaulttimeout()
            socket.setdefaulttimeout(GCE.TIMEOUT)
        except Exception:
            pass

        try:
            opener = url_lib.build_opener()
            opener.addheaders = [('X-Google-Metadata-Request', 'True')]
            GCE.metadata = json.loads(opener.open(GCE.URL).read().strip())
        except Exception:
            GCE.metadata = {}

        try:
            if socket_to is None:
                socket_to = 3
            socket.setdefaulttimeout(socket_to)
        except Exception:
            pass

        return GCE.metadata

    @staticmethod
    def get_hostname(agentConfig):
        try:
            host_metadata = GCE._get_metadata(agentConfig)
            return host_metadata['instance']['hostname'].split('.')[0]
        except Exception:
            return None


class EC2(object):
    URL = 'http://169.254.169.254/latest/meta-data'
    TIMEOUT = 0.1
    metadata = {}

    @staticmethod
    def get_tags(agentConfig):
        if not agentConfig['collect_instance_metadata']:
            log.info('Instance metadata collection is disabled. Not collecting it.')
            return []
        socket_to = None
        try:
            socket_to = socket.getdefaulttimeout()
            socket.setdefaulttimeout(EC2.TIMEOUT)
        except Exception:
            pass

        try:
            iam_role = url_lib.urlopen(EC2.URL + '/iam/security-credentials').read().strip()
            iam_params = json.loads(url_lib.urlopen(EC2.URL + '/iam/security-credentials' + '/' + str(iam_role)).read().strip())
            from boto.ec2.connection import EC2Connection
            connection = EC2Connection(aws_access_key_id=iam_params['AccessKeyId'], aws_secret_access_key=iam_params['SecretAccessKey'], security_token=iam_params['Token'])
            instance_object = connection.get_only_instances([EC2.metadata['instance-id']])[0]
            EC2_tags = [ u'%s:%s' % (tag_key, tag_value) for tag_key, tag_value in iteritems(instance_object.tags) ]
        except Exception:
            log.exception('Problem retrieving custom EC2 tags')
            EC2_tags = []

        try:
            if socket_to is None:
                socket_to = 3
            socket.setdefaulttimeout(socket_to)
        except Exception:
            pass

        return EC2_tags

    @staticmethod
    def get_metadata(agentConfig):
        if not agentConfig['collect_instance_metadata']:
            log.info('Instance metadata collection is disabled. Not collecting it.')
            return {}
        socket_to = None
        try:
            socket_to = socket.getdefaulttimeout()
            socket.setdefaulttimeout(EC2.TIMEOUT)
        except Exception:
            pass

        for k in ('instance-id', 'hostname', 'local-hostname', 'public-hostname', 'ami-id', 'local-ipv4', 'public-keys', 'public-ipv4', 'reservation-id', 'security-groups'):
            try:
                v = url_lib.urlopen(EC2.URL + '/' + str(k)).read().strip()
                EC2.metadata[k] = v
            except Exception:
                pass

        try:
            if socket_to is None:
                socket_to = 3
            socket.setdefaulttimeout(socket_to)
        except Exception:
            pass

        return EC2.metadata

    @staticmethod
    def get_instance_id(agentConfig):
        try:
            return EC2.get_metadata(agentConfig).get('instance-id', None)
        except Exception:
            return None
