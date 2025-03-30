#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\monolithconfig\secrets.py
import logging
import uthread2
import monolithconfig
import hvac
from hvac.exceptions import InvalidRequest, Forbidden
log = logging.getLogger(__name__)
vault_client = None
rabbitmq_credentials = None
leases = []
new_client_authing = True
KV_MOUNT_POINT = 'eve-monolith-server-kv'

def _renewals():
    while True:
        uthread2.sleep(60)
        client = _get_secret_client()
        if client is None:
            continue
        reauth_client = _renew_token(client)
        if reauth_client:
            continue
        for lease in leases:
            remove_lease = _renew_lease(client, lease['id'], lease['duration'], lease['on_lease_not_found'])
            if remove_lease:
                leases.remove(lease)


def _renew_lease(client, lease_id, extension, on_lease_not_found):
    try:
        lease_info = client.sys.read_lease(lease_id)
        if lease_info['data']['ttl'] < extension / 2:
            client.sys.renew_lease(lease_id, extension)
    except (InvalidRequest, Forbidden) as err:
        log.warn('Failed to read/renew lease (%s): %s', lease_id, err)
        on_lease_not_found()
        return True
    except Exception:
        log.exception('Failed to read/renew lease (%s)', lease_id)

    return False


def _renew_token(client):
    try:
        token_info = client.lookup_token()
        extension = token_info['data']['creation_ttl']
        ttl = token_info['data']['ttl']
        if ttl < extension / 2:
            client.renew_token(increment=extension)
    except (InvalidRequest, Forbidden) as err:
        log.warn('Failed to read/renew token: %s', err)
        _reset_secret_client()
        return True
    except Exception:
        log.exception('Failed to read/renew token')

    return False


def _reset_secret_client():
    global vault_client
    vault_client = None


def _get_secret_client():
    global vault_client
    global new_client_authing
    if vault_client is not None:
        while new_client_authing:
            uthread2.sleep(1)

        return vault_client
    vault_address = monolithconfig.get_value('vault_address', 'prefs')
    if vault_address is None:
        vault_address = 'https://vault.evetech.net'
    timeout = 300
    vault_client = hvac.Client(url=vault_address, timeout=timeout)
    vault_role_id = monolithconfig.get_value('vault_role_id', 'prefs')
    if not vault_role_id:
        vault_role_id = '44df5a58-8475-b0e8-1eee-57437f2fe5d3'
    vault_secret_id = monolithconfig.get_value('vault_secret_id', 'prefs')
    if not vault_secret_id:
        vault_secret_id = '7e8354d4-4d86-f2d4-a7e5-4820342e95d3'
    try:
        _auth(vault_client, vault_role_id, vault_secret_id)
        log.info('Vault authorized')
        new_client_authing = False
    except Exception:
        log.exception('Vault authorization failed')
        return

    return vault_client


def _auth(client, role, secret):
    try:
        client.auth_approle(role, secret, 'eve-monolith-server')
    except Exception:
        log.exception('Failed to auth approle (%s) with Vault', role)
        return None


def get_secret(path):
    client = _get_secret_client()
    if client is None:
        return
    try:
        return client.read(path)
    except Exception:
        log.exception('Failed to get secret (%s)', path)
        return


def get_kv_secret(tier, key):
    client = _get_secret_client()
    path = '{}/{}'.format(tier, key)
    try:
        response = client.secrets.kv.v2.read_secret_version(mount_point=KV_MOUNT_POINT, path=path)
        return response['data']['data']
    except Exception:
        log.exception('failed to read kv secret store', extra={'tier': tier,
         'key': key})
        return None


def get_rabbitmq_credentials(on_credentials_expired):
    global rabbitmq_credentials
    if rabbitmq_credentials is not None:
        return rabbitmq_credentials
    path = 'rabbitmq-eve-{0}/creds/eve-monolith-server'.format(monolithconfig.get_tier())
    rabbitmq_credentials = get_secret(path)
    if rabbitmq_credentials is None:
        return (None, None)

    def _reset_rabbit_credentials():
        global rabbitmq_credentials
        rabbitmq_credentials = None
        on_credentials_expired()

    lease_id = rabbitmq_credentials['lease_id']
    lease_duration = rabbitmq_credentials['lease_duration']
    leases.append({'id': lease_id,
     'duration': lease_duration,
     'on_lease_not_found': _reset_rabbit_credentials})
    return (rabbitmq_credentials['data']['username'], rabbitmq_credentials['data']['password'])


def get_service_gateway_certificate_location():
    tier = monolithconfig.get_tier()
    cluster_name = monolithconfig.get_value('clusterName')
    return '{}/{}/grpc-certificates'.format(tier, cluster_name)


def get_service_gateway_certificates():
    client = _get_secret_client()
    path = get_service_gateway_certificate_location()
    try:
        response = client.secrets.kv.v2.read_secret_version(mount_point=KV_MOUNT_POINT, path=path)
        certificate = response['data']['data']['certificate']
        private_key = response['data']['data']['private_key']
        issuing_ca = response['data']['data']['issuing_ca']
        return (certificate, private_key, issuing_ca)
    except Exception:
        log.exception('Failed to read server gateway certificates')
        return None


def issue_service_gateway_certificates():
    eve_domain = monolithconfig.get_value('eve_domain', 'prefs')
    if eve_domain is None:
        eve_domain = 'evetech.net'
    tier = monolithconfig.get_tier()
    mount_point = 'eve-internal-services-{}-intermediate'.format(tier)
    common_name = '{}-service-gateway-client.{}'.format(tier, eve_domain)
    client = _get_secret_client()
    try:
        certs = client.secrets.pki.generate_certificate(name='service-gateway-client', common_name=common_name, mount_point=mount_point)
    except Exception:
        log.exception('Failed to server gateway certificates')
        return

    certficate = certs.json()['data']['certificate']
    private_key = certs.json()['data']['private_key']
    issuing_ca = certs.json()['data']['issuing_ca']
    return (certficate, private_key, issuing_ca)


def upload_service_gateway_certificates(certificate, private_key, issuing_ca):
    client = _get_secret_client()
    path = get_service_gateway_certificate_location()
    try:
        client.secrets.kv.v2.create_or_update_secret(mount_point=KV_MOUNT_POINT, path=path, secret=dict(certificate=certificate, private_key=private_key, issuing_ca=issuing_ca))
    except Exception:
        log.exception('Failed to upload server gateway certificates')
        return


uthread2.StartTasklet(_renewals)
