#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\__init__.py
import logging
import sys
import os
TYPE_URL = 'type.evetech.net/'
fast_native_serialization = False
grpc_module = None

def get_grpc_module_name():
    import monolithconfig
    if monolithconfig.on_client():
        return 'eve_client_grpc_client'
    else:
        return 'eve_grpc_client'


def get_proto_module_name():
    import monolithconfig
    if monolithconfig.on_client():
        return 'pyext_eve_public'
    else:
        return 'pyext_eve'


def toggle_cpp_implementation(enabled = True):
    import os
    if enabled:
        os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'cpp'
    else:
        os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'


def patch_pickle():
    import cPickle
    sys.modules['pickle'] = cPickle


def is_x64():
    return sys.maxsize > 4294967296L


def is_running_stackless():
    try:
        import stackless
        return True
    except ImportError:
        return False

    return False


def log_everywhere(msg):
    logging.info(msg)
    print msg


def import_pyd_as_message_module(module_name):
    global fast_native_serialization
    patch_pickle()
    toggle_cpp_implementation(True)
    pyd_path = __import__(module_name).__file__
    parts = os.path.split(pyd_path)
    pyd_path = os.path.join(parts[0], '.', parts[1])
    log_everywhere('...loading from: ' + os.path.realpath(pyd_path))
    import google.protobuf.pyext as pyext
    import imp
    the_pyd = imp.load_dynamic('google.protobuf.pyext._message', pyd_path)
    pyext._message = the_pyd
    fast_native_serialization = True
    log_everywhere('Loaded native protobuf serialization')


def set_grpc_dns_resolver(resolver):
    key = 'GRPC_DNS_RESOLVER'
    import os
    os.environ[key] = resolver


def get_grpc_module():
    global grpc_module
    if not is_running_stackless() or not is_x64():
        return
    set_grpc_dns_resolver('native')
    if grpc_module is not None:
        return grpc_module
    grpc_module = __import__(get_grpc_module_name())
    return grpc_module


def get_message_type_url(messageName):
    return '{}{}'.format(TYPE_URL, messageName)


if is_running_stackless() and is_x64():
    logging.info('x64 Stackless detected, loading fast native protobuf serialization.')
    try:
        import_pyd_as_message_module(get_proto_module_name())
    except Exception as proto_import_exception:
        try:
            msg = 'Failed to load proto module ({}). Trying the gRPC module.'.format(proto_import_exception)
            log_everywhere(msg)
            logging.exception(msg)
            import_pyd_as_message_module(get_grpc_module_name())
        except Exception as grpc_import_exception:
            msg = 'Failed to load grpc module ({}). Falling back to slow protobuf serialization.'.format(grpc_import_exception)
            log_everywhere(msg)
            logging.exception(msg)
            toggle_cpp_implementation(False)

else:
    logging.warn('x64 Stackless not detected. Falling back to slow protobuf serialization.')
from monolith_converters import *
