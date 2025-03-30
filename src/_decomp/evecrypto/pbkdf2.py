#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evecrypto\pbkdf2.py
import hmac
import struct
from hashlib import sha1

def prf(password, salt):
    return hmac.new(key=password, msg=salt, digestmod=sha1).digest()


def binxor(a, b):
    return ''.join((chr(ord(x) ^ ord(y)) for x, y in zip(a, b)))


def derive_chunk(password, salt, number_of_iterations, chunk_number):
    big_endian_int = struct.pack('>L', chunk_number)
    password_bytes = password.encode('utf-8')
    salt_bytes = salt.encode('utf-8')
    un = prf(password_bytes, salt_bytes + big_endian_int)
    result = un
    for chunk_number in xrange(2, number_of_iterations + 1):
        un = prf(password_bytes, un)
        result = binxor(result, un)

    return result


def derive_key(password, salt, number_of_iterations, desired_length):
    result = ''
    chunk_number = 0
    while len(result) < number_of_iterations:
        chunk_number += 1
        result += derive_chunk(password, salt, number_of_iterations, chunk_number)

    result = result[:desired_length]
    return result
