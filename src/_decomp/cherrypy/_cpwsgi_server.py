#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\lib\cherrypy\_cpwsgi_server.py
import sys
import cherrypy
from cherrypy import wsgiserver

class CPWSGIServer(wsgiserver.CherryPyWSGIServer):

    def __init__(self, server_adapter = cherrypy.server):
        self.server_adapter = server_adapter
        self.max_request_header_size = self.server_adapter.max_request_header_size or 0
        self.max_request_body_size = self.server_adapter.max_request_body_size or 0
        server_name = self.server_adapter.socket_host or self.server_adapter.socket_file or None
        self.wsgi_version = self.server_adapter.wsgi_version
        s = wsgiserver.CherryPyWSGIServer
        s.__init__(self, server_adapter.bind_addr, cherrypy.tree, self.server_adapter.thread_pool, server_name, max=self.server_adapter.thread_pool_max, request_queue_size=self.server_adapter.socket_queue_size, timeout=self.server_adapter.socket_timeout, shutdown_timeout=self.server_adapter.shutdown_timeout)
        self.protocol = self.server_adapter.protocol_version
        self.nodelay = self.server_adapter.nodelay
        ssl_module = self.server_adapter.ssl_module or 'pyopenssl'
        if self.server_adapter.ssl_context:
            adapter_class = wsgiserver.get_ssl_adapter_class(ssl_module)
            self.ssl_adapter = adapter_class(self.server_adapter.ssl_certificate, self.server_adapter.ssl_private_key, self.server_adapter.ssl_certificate_chain)
            self.ssl_adapter.context = self.server_adapter.ssl_context
        elif self.server_adapter.ssl_certificate:
            adapter_class = wsgiserver.get_ssl_adapter_class(ssl_module)
            self.ssl_adapter = adapter_class(self.server_adapter.ssl_certificate, self.server_adapter.ssl_private_key, self.server_adapter.ssl_certificate_chain)
