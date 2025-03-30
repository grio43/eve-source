#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\maxminddb\reader.py
from __future__ import unicode_literals
try:
    import mmap
except ImportError:
    mmap = None

import struct
from maxminddb.compat import byte_from_int, compat_ip_address
from maxminddb.const import MODE_AUTO, MODE_MMAP, MODE_FILE, MODE_MEMORY
from maxminddb.decoder import Decoder
from maxminddb.errors import InvalidDatabaseError
from maxminddb.file import FileBuffer

class Reader(object):
    _DATA_SECTION_SEPARATOR_SIZE = 16
    _METADATA_START_MARKER = '\xab\xcd\xefMaxMind.com'
    _ipv4_start = None

    def __init__(self, database, mode = MODE_AUTO):
        if mode == MODE_AUTO and mmap or mode == MODE_MMAP:
            with open(database, u'rb') as db_file:
                self._buffer = mmap.mmap(db_file.fileno(), 0, access=mmap.ACCESS_READ)
                self._buffer_size = self._buffer.size()
        elif mode in (MODE_AUTO, MODE_FILE):
            self._buffer = FileBuffer(database)
            self._buffer_size = self._buffer.size()
        elif mode == MODE_MEMORY:
            with open(database, u'rb') as db_file:
                self._buffer = db_file.read()
                self._buffer_size = len(self._buffer)
        else:
            raise ValueError(u'Unsupported open mode ({0}). Only MODE_AUTO,  MODE_FILE, and MODE_MEMORY are support by the pure Python Reader'.format(mode))
        metadata_start = self._buffer.rfind(self._METADATA_START_MARKER, max(0, self._buffer_size - 131072))
        if metadata_start == -1:
            self.close()
            raise InvalidDatabaseError(u'Error opening database file ({0}). Is this a valid MaxMind DB file?'.format(database))
        metadata_start += len(self._METADATA_START_MARKER)
        metadata_decoder = Decoder(self._buffer, metadata_start)
        metadata, _ = metadata_decoder.decode(metadata_start)
        self._metadata = Metadata(**metadata)
        self._decoder = Decoder(self._buffer, self._metadata.search_tree_size + self._DATA_SECTION_SEPARATOR_SIZE)
        self.closed = False

    def metadata(self):
        return self._metadata

    def get(self, ip_address):
        address = compat_ip_address(ip_address)
        if address.version == 6 and self._metadata.ip_version == 4:
            raise ValueError(u'Error looking up {0}. You attempted to look up an IPv6 address in an IPv4-only database.'.format(ip_address))
        pointer = self._find_address_in_tree(address)
        if pointer:
            return self._resolve_data_pointer(pointer)

    def _find_address_in_tree(self, ip_address):
        packed = bytearray(ip_address.packed)
        bit_count = len(packed) * 8
        node = self._start_node(bit_count)
        for i in range(bit_count):
            if node >= self._metadata.node_count:
                break
            bit = 1 & packed[i >> 3] >> 7 - i % 8
            node = self._read_node(node, bit)

        if node == self._metadata.node_count:
            return 0
        if node > self._metadata.node_count:
            return node
        raise InvalidDatabaseError(u'Invalid node in search tree')

    def _start_node(self, length):
        if self._metadata.ip_version != 6 or length == 128:
            return 0
        if self._ipv4_start:
            return self._ipv4_start
        node = 0
        for _ in range(96):
            if node >= self._metadata.node_count:
                break
            node = self._read_node(node, 0)

        self._ipv4_start = node
        return node

    def _read_node(self, node_number, index):
        base_offset = node_number * self._metadata.node_byte_size
        record_size = self._metadata.record_size
        if record_size == 24:
            offset = base_offset + index * 3
            node_bytes = '\x00' + self._buffer[offset:offset + 3]
        elif record_size == 28:
            middle, = struct.unpack('!B', self._buffer[base_offset + 3:base_offset + 4])
            if index:
                middle &= 15
            else:
                middle = (240 & middle) >> 4
            offset = base_offset + index * 4
            node_bytes = byte_from_int(middle) + self._buffer[offset:offset + 3]
        elif record_size == 32:
            offset = base_offset + index * 4
            node_bytes = self._buffer[offset:offset + 4]
        else:
            raise InvalidDatabaseError(u'Unknown record size: {0}'.format(record_size))
        return struct.unpack('!I', node_bytes)[0]

    def _resolve_data_pointer(self, pointer):
        resolved = pointer - self._metadata.node_count + self._metadata.search_tree_size
        if resolved > self._buffer_size:
            raise InvalidDatabaseError(u"The MaxMind DB file's search tree is corrupt")
        data, _ = self._decoder.decode(resolved)
        return data

    def close(self):
        if type(self._buffer) not in (str, bytes):
            self._buffer.close()
        self.closed = True

    def __exit__(self, *args):
        self.close()

    def __enter__(self):
        if self.closed:
            raise ValueError(u'Attempt to reopen a closed MaxMind DB')
        return self


class Metadata(object):

    def __init__(self, **kwargs):
        self.node_count = kwargs[u'node_count']
        self.record_size = kwargs[u'record_size']
        self.ip_version = kwargs[u'ip_version']
        self.database_type = kwargs[u'database_type']
        self.languages = kwargs[u'languages']
        self.binary_format_major_version = kwargs[u'binary_format_major_version']
        self.binary_format_minor_version = kwargs[u'binary_format_minor_version']
        self.build_epoch = kwargs[u'build_epoch']
        self.description = kwargs[u'description']

    @property
    def node_byte_size(self):
        return self.record_size // 4

    @property
    def search_tree_size(self):
        return self.node_count * self.node_byte_size

    def __repr__(self):
        args = u', '.join((u'%s=%r' % x for x in self.__dict__.items()))
        return u'{module}.{class_name}({data})'.format(module=self.__module__, class_name=self.__class__.__name__, data=args)
