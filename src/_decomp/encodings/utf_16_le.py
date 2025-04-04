#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\stdlib\encodings\utf_16_le.py
import codecs
encode = codecs.utf_16_le_encode

def decode(input, errors = 'strict'):
    return codecs.utf_16_le_decode(input, errors, True)


class IncrementalEncoder(codecs.IncrementalEncoder):

    def encode(self, input, final = False):
        return codecs.utf_16_le_encode(input, self.errors)[0]


class IncrementalDecoder(codecs.BufferedIncrementalDecoder):
    _buffer_decode = codecs.utf_16_le_decode


class StreamWriter(codecs.StreamWriter):
    encode = codecs.utf_16_le_encode


class StreamReader(codecs.StreamReader):
    decode = codecs.utf_16_le_decode


def getregentry():
    return codecs.CodecInfo(name='utf-16-le', encode=encode, decode=decode, incrementalencoder=IncrementalEncoder, incrementaldecoder=IncrementalDecoder, streamreader=StreamReader, streamwriter=StreamWriter)
