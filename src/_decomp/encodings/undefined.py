#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\stdlib\encodings\undefined.py
import codecs

class Codec(codecs.Codec):

    def encode(self, input, errors = 'strict'):
        raise UnicodeError('undefined encoding')

    def decode(self, input, errors = 'strict'):
        raise UnicodeError('undefined encoding')


class IncrementalEncoder(codecs.IncrementalEncoder):

    def encode(self, input, final = False):
        raise UnicodeError('undefined encoding')


class IncrementalDecoder(codecs.IncrementalDecoder):

    def decode(self, input, final = False):
        raise UnicodeError('undefined encoding')


class StreamWriter(Codec, codecs.StreamWriter):
    pass


class StreamReader(Codec, codecs.StreamReader):
    pass


def getregentry():
    return codecs.CodecInfo(name='undefined', encode=Codec().encode, decode=Codec().decode, incrementalencoder=IncrementalEncoder, incrementaldecoder=IncrementalDecoder, streamwriter=StreamWriter, streamreader=StreamReader)
