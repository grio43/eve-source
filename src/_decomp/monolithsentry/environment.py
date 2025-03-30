#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\monolithsentry\environment.py
import monolithconfig

def get_environment():
    if monolithconfig.on_server():
        return get_server_environment()
    if monolithconfig.on_proxy():
        return get_proxy_environment()
    return get_client_environment()


def get_server_environment():
    cluster_name = monolithconfig.get_value('clusterName', 'prefs')
    if not cluster_name:
        return 'localhost'
    if '@' in cluster_name:
        return 'localhost'
    return cluster_name.lower()


def get_proxy_environment():
    return get_server_environment()


def get_client_environment():
    from utillib import GetServerName
    server_name = GetServerName()
    if not server_name:
        return 'localhost'
    server_name = server_name.split('.')
    server_name = server_name[0]
    if str.isdigit(str(server_name)):
        return 'manual ip'
    return server_name.lower()
