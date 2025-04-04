#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\stdlib\encodings\hex_codec.py
import codecs, binascii

def hex_encode(input, errors = 'strict'):
    output = binascii.b2a_hex(input)
    return (output, len(input))


def hex_decode(input, errors = 'strict'):
    output = binascii.a2b_hex(input)
    return (output, len(input))


class Codec(codecs.Codec):

    def encode(self, input, errors = 'strict'):
        return hex_encode(input, errors)

    def decode(self, input, errors = 'strict'):
        return hex_decode(input, errors)


class IncrementalEncoder(codecs.IncrementalEncoder):

    def encode(self, input, final = False):
        return binascii.b2a_hex(input)


class IncrementalDecoder(codecs.IncrementalDecoder):

    def decode(self, input, final = False):
        return binascii.a2b_hex(input)


class StreamWriter(Codec, codecs.StreamWriter):
    pass


class StreamReader(Codec, codecs.StreamReader):
    pass


def getregentry():
    return codecs.CodecInfo(name='hex', encode=hex_encode, decode=hex_decode, incrementalencoder=IncrementalEncoder, incrementaldecoder=IncrementalDecoder, streamwriter=StreamWriter, streamreader=StreamReader)
