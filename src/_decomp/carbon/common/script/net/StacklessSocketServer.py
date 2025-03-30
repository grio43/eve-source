#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\script\net\StacklessSocketServer.py
import SocketServer
import uthread

class UThreadingMixIn:

    def process_request_tasklet(self, request, client_address):
        try:
            self.finish_request(request, client_address)
            self.close_request(request)
        except:
            self.handle_error(request, client_address)
            self.close_request(request)

    def process_request(self, request, client_address):
        t = uthread.new(self.process_request_tasklet, request, client_address)
        t.run()


class UThreadingTCPServer(UThreadingMixIn, SocketServer.TCPServer):
    pass
