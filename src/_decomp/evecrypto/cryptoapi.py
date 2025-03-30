#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evecrypto\cryptoapi.py
import blue
from hashlib import sha256

def crypto_hash(*args):
    return sha256(blue.marshal.Save(args)).digest()


def sign(data):
    packedData = blue.marshal.Save(data)
    hashed = crypto_hash(packedData)
    signed = asymmetricKey.Sign(hashed)
    return (packedData, signed)


def verify(signedData):
    hashed = crypto_hash(signedData[0])
    return (blue.marshal.Load(signedData[0]), asymmetricKey.VerifySignature(hashed, signedData[1]))


def create_context():
    return CryptoApiCryptoContext()


def get_random_bytes(byteCount):
    return blue.crypto.GenerateRandomBytes(byteCount)


class CryptoApiCryptoContext:

    def __init__(self):
        self.encryptedSymmetricKey = None
        self.encryptedSymmetricIV = None
        self.symmetricKeyCipher = None

    def __CreateActualCipher(self, cipher, encryptedKey, encryptedIV):
        if cipher is None:
            cipher = blue.SymmetricCipher()
            key = asymmetricKey.Decrypt(encryptedKey)
            iv = asymmetricKey.Decrypt(encryptedIV)
            cipher.LoadKey(key, iv)
        return cipher

    def Initialize(self, request = None):
        symmetricCipher = None
        if request is not None:
            encryptedKey = request.get('crypting_sessionkey')
            encryptedIV = request.get('crypting_sessioniv')
        else:
            key = get_random_bytes(32)
            iv = get_random_bytes(16)
            symmetricCipher = blue.SymmetricCipher()
            symmetricCipher.LoadKey(key, iv)
            encryptedKey = asymmetricKey.Encrypt(key)
            encryptedIV = asymmetricKey.Encrypt(iv)
        self.encryptedSymmetricKey = encryptedKey
        self.encryptedSymmetricIV = encryptedIV
        self.symmetricKeyCipher = self.__CreateActualCipher(symmetricCipher, self.encryptedSymmetricKey, self.encryptedSymmetricIV)
        return {'crypting_sessionkey': encryptedKey,
         'crypting_sessioniv': encryptedIV}

    def SymmetricDecryption(self, cryptedPacket):
        return self.symmetricKeyCipher.Decrypt(str(cryptedPacket))

    def SymmetricEncryption(self, plainPacket):
        return self.symmetricKeyCipher.Encrypt(str(plainPacket))

    def OptionalSymmetricEncryption(self, plainPacket):
        if self.symmetricKeyCipher is not None:
            return self.SymmetricEncryption(plainPacket)
        return plainPacket


asymmetricKey = blue.crypto.GetSharedAsymmetricCipher()
