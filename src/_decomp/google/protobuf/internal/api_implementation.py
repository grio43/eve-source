#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\google\protobuf\internal\api_implementation.py
import os
import sys
import warnings
try:
    from google.protobuf.internal import _api_implementation
    _api_version = _api_implementation.api_version
    _proto_extension_modules_exist_in_build = True
except ImportError:
    _api_version = -1
    _proto_extension_modules_exist_in_build = False

if _api_version == 1:
    raise ValueError('api_version=1 is no longer supported.')
if _api_version < 0:
    try:
        from google.protobuf import _use_fast_cpp_protos
        if not _use_fast_cpp_protos:
            raise ImportError('_use_fast_cpp_protos import succeeded but was None')
        del _use_fast_cpp_protos
        _api_version = 2
        from google.protobuf import use_pure_python
        raise RuntimeError('Conflicting deps on both :use_fast_cpp_protos and :use_pure_python.\n go/build_deps_on_BOTH_use_fast_cpp_protos_AND_use_pure_python\nThis should be impossible via a link error at build time...')
    except ImportError:
        try:
            from google.protobuf import use_pure_python
            del use_pure_python
            _api_version = 0
        except ImportError:
            pass

_default_implementation_type = 'python' if _api_version <= 0 else 'cpp'
_implementation_type = os.getenv('PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION', _default_implementation_type)
if _implementation_type != 'python':
    _implementation_type = 'cpp'
if 'PyPy' in sys.version and _implementation_type == 'cpp':
    warnings.warn('PyPy does not work yet with cpp protocol buffers. Falling back to the python implementation.')
    _implementation_type = 'python'
_implementation_version_str = os.getenv('PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION_VERSION', '2')
if _implementation_version_str != '2':
    raise ValueError('unsupported PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION_VERSION: "' + _implementation_version_str + '" (supported versions: 2)')
_implementation_version = int(_implementation_version_str)
try:
    from google.protobuf import enable_deterministic_proto_serialization
    _python_deterministic_proto_serialization = True
except ImportError:
    _python_deterministic_proto_serialization = False

def Type():
    global _implementation_type
    return _implementation_type


def _SetType(implementation_type):
    global _implementation_type
    _implementation_type = implementation_type


def Version():
    return _implementation_version


def IsPythonDefaultSerializationDeterministic():
    return _python_deterministic_proto_serialization
