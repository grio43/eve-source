#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\stdlib\encodings\utf_8.py
import codecs
encode = codecs.utf_8_encode

def decode(input, errors = 'strict'):
    return codecs.utf_8_decode(input, errors, True)


class IncrementalEncoder(codecs.IncrementalEncoder):

    def encode(self, input, final = False):
        return codecs.utf_8_encode(input, self.errors)[0]


class IncrementalDecoder(codecs.BufferedIncrementalDecoder):
    _buffer_decode = codecs.utf_8_decode


class StreamWriter(codecs.StreamWriter):
    encode = codecs.utf_8_encode


class StreamReader(codecs.StreamReader):
    decode = codecs.utf_8_decode


def getregentry():
    return codecs.CodecInfo(name='utf-8', encode=encode, decode=decode, incrementalencoder=IncrementalEncoder, incrementaldecoder=IncrementalDecoder, streamreader=StreamReader, streamwriter=StreamWriter)
