#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evecrypto\crypto.py
import evecrypto.cryptoapi as cryptoapi
import evecrypto.placebo as placebo
import evecrypto.settings as settings
if settings.cryptoPack == 'CryptoAPI':
    impl = cryptoapi
else:
    impl = placebo
CryptoHash = impl.crypto_hash
CryptoCreateContext = impl.create_context
GetRandomBytes = impl.get_random_bytes
Sign = impl.sign
Verify = impl.verify
