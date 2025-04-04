#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\rsa\cli.py
from __future__ import with_statement, print_function
import abc
import sys
from optparse import OptionParser
import rsa
import rsa.bigfile
import rsa.pkcs1
HASH_METHODS = sorted(rsa.pkcs1.HASH_METHODS.keys())

def keygen():
    parser = OptionParser(usage='usage: %prog [options] keysize', description='Generates a new RSA keypair of "keysize" bits.')
    parser.add_option('--pubout', type='string', help='Output filename for the public key. The public key is not saved if this option is not present. You can use pyrsa-priv2pub to create the public key file later.')
    parser.add_option('-o', '--out', type='string', help='Output filename for the private key. The key is written to stdout if this option is not present.')
    parser.add_option('--form', help='key format of the private and public keys - default PEM', choices=('PEM', 'DER'), default='PEM')
    cli, cli_args = parser.parse_args(sys.argv[1:])
    if len(cli_args) != 1:
        parser.print_help()
        raise SystemExit(1)
    try:
        keysize = int(cli_args[0])
    except ValueError:
        parser.print_help()
        print('Not a valid number: %s' % cli_args[0], file=sys.stderr)
        raise SystemExit(1)

    print('Generating %i-bit key' % keysize, file=sys.stderr)
    pub_key, priv_key = rsa.newkeys(keysize)
    if cli.pubout:
        print('Writing public key to %s' % cli.pubout, file=sys.stderr)
        data = pub_key.save_pkcs1(format=cli.form)
        with open(cli.pubout, 'wb') as outfile:
            outfile.write(data)
    data = priv_key.save_pkcs1(format=cli.form)
    if cli.out:
        print('Writing private key to %s' % cli.out, file=sys.stderr)
        with open(cli.out, 'wb') as outfile:
            outfile.write(data)
    else:
        print('Writing private key to stdout', file=sys.stderr)
        sys.stdout.write(data)


class CryptoOperation(object):
    __metaclass__ = abc.ABCMeta
    keyname = 'public'
    usage = 'usage: %%prog [options] %(keyname)s_key'
    description = None
    operation = 'decrypt'
    operation_past = 'decrypted'
    operation_progressive = 'decrypting'
    input_help = 'Name of the file to %(operation)s. Reads from stdin if not specified.'
    output_help = 'Name of the file to write the %(operation_past)s file to. Written to stdout if this option is not present.'
    expected_cli_args = 1
    has_output = True
    key_class = rsa.PublicKey

    def __init__(self):
        self.usage = self.usage % self.__class__.__dict__
        self.input_help = self.input_help % self.__class__.__dict__
        self.output_help = self.output_help % self.__class__.__dict__

    @abc.abstractmethod
    def perform_operation(self, indata, key, cli_args = None):
        pass

    def __call__(self):
        cli, cli_args = self.parse_cli()
        key = self.read_key(cli_args[0], cli.keyform)
        indata = self.read_infile(cli.input)
        print(self.operation_progressive.title(), file=sys.stderr)
        outdata = self.perform_operation(indata, key, cli_args)
        if self.has_output:
            self.write_outfile(outdata, cli.output)

    def parse_cli(self):
        parser = OptionParser(usage=self.usage, description=self.description)
        parser.add_option('-i', '--input', type='string', help=self.input_help)
        if self.has_output:
            parser.add_option('-o', '--output', type='string', help=self.output_help)
        parser.add_option('--keyform', help='Key format of the %s key - default PEM' % self.keyname, choices=('PEM', 'DER'), default='PEM')
        cli, cli_args = parser.parse_args(sys.argv[1:])
        if len(cli_args) != self.expected_cli_args:
            parser.print_help()
            raise SystemExit(1)
        return (cli, cli_args)

    def read_key(self, filename, keyform):
        print('Reading %s key from %s' % (self.keyname, filename), file=sys.stderr)
        with open(filename, 'rb') as keyfile:
            keydata = keyfile.read()
        return self.key_class.load_pkcs1(keydata, keyform)

    def read_infile(self, inname):
        if inname:
            print('Reading input from %s' % inname, file=sys.stderr)
            with open(inname, 'rb') as infile:
                return infile.read()
        print('Reading input from stdin', file=sys.stderr)
        return sys.stdin.read()

    def write_outfile(self, outdata, outname):
        if outname:
            print('Writing output to %s' % outname, file=sys.stderr)
            with open(outname, 'wb') as outfile:
                outfile.write(outdata)
        else:
            print('Writing output to stdout', file=sys.stderr)
            sys.stdout.write(outdata)


class EncryptOperation(CryptoOperation):
    keyname = 'public'
    description = 'Encrypts a file. The file must be shorter than the key length in order to be encrypted. For larger files, use the pyrsa-encrypt-bigfile command.'
    operation = 'encrypt'
    operation_past = 'encrypted'
    operation_progressive = 'encrypting'

    def perform_operation(self, indata, pub_key, cli_args = None):
        return rsa.encrypt(indata, pub_key)


class DecryptOperation(CryptoOperation):
    keyname = 'private'
    description = 'Decrypts a file. The original file must be shorter than the key length in order to have been encrypted. For larger files, use the pyrsa-decrypt-bigfile command.'
    operation = 'decrypt'
    operation_past = 'decrypted'
    operation_progressive = 'decrypting'
    key_class = rsa.PrivateKey

    def perform_operation(self, indata, priv_key, cli_args = None):
        return rsa.decrypt(indata, priv_key)


class SignOperation(CryptoOperation):
    keyname = 'private'
    usage = 'usage: %%prog [options] private_key hash_method'
    description = 'Signs a file, outputs the signature. Choose the hash method from %s' % ', '.join(HASH_METHODS)
    operation = 'sign'
    operation_past = 'signature'
    operation_progressive = 'Signing'
    key_class = rsa.PrivateKey
    expected_cli_args = 2
    output_help = 'Name of the file to write the signature to. Written to stdout if this option is not present.'

    def perform_operation(self, indata, priv_key, cli_args):
        hash_method = cli_args[1]
        if hash_method not in HASH_METHODS:
            raise SystemExit('Invalid hash method, choose one of %s' % ', '.join(HASH_METHODS))
        return rsa.sign(indata, priv_key, hash_method)


class VerifyOperation(CryptoOperation):
    keyname = 'public'
    usage = 'usage: %%prog [options] public_key signature_file'
    description = 'Verifies a signature, exits with status 0 upon success, prints an error message and exits with status 1 upon error.'
    operation = 'verify'
    operation_past = 'verified'
    operation_progressive = 'Verifying'
    key_class = rsa.PublicKey
    expected_cli_args = 2
    has_output = False

    def perform_operation(self, indata, pub_key, cli_args):
        signature_file = cli_args[1]
        with open(signature_file, 'rb') as sigfile:
            signature = sigfile.read()
        try:
            rsa.verify(indata, signature, pub_key)
        except rsa.VerificationError:
            raise SystemExit('Verification failed.')

        print('Verification OK', file=sys.stderr)


class BigfileOperation(CryptoOperation):

    def __init__(self):
        CryptoOperation.__init__(self)
        self.file_objects = []

    def __del__(self):
        for fobj in self.file_objects:
            fobj.close()

    def __call__(self):
        cli, cli_args = self.parse_cli()
        key = self.read_key(cli_args[0], cli.keyform)
        infile = self.get_infile(cli.input)
        outfile = self.get_outfile(cli.output)
        print(self.operation_progressive.title(), file=sys.stderr)
        self.perform_operation(infile, outfile, key, cli_args)

    def get_infile(self, inname):
        if inname:
            print('Reading input from %s' % inname, file=sys.stderr)
            fobj = open(inname, 'rb')
            self.file_objects.append(fobj)
        else:
            print('Reading input from stdin', file=sys.stderr)
            fobj = sys.stdin
        return fobj

    def get_outfile(self, outname):
        if outname:
            print('Will write output to %s' % outname, file=sys.stderr)
            fobj = open(outname, 'wb')
            self.file_objects.append(fobj)
        else:
            print('Will write output to stdout', file=sys.stderr)
            fobj = sys.stdout
        return fobj


class EncryptBigfileOperation(BigfileOperation):
    keyname = 'public'
    description = 'Encrypts a file to an encrypted VARBLOCK file. The file can be larger than the key length, but the output file is only compatible with Python-RSA.'
    operation = 'encrypt'
    operation_past = 'encrypted'
    operation_progressive = 'encrypting'

    def perform_operation(self, infile, outfile, pub_key, cli_args = None):
        return rsa.bigfile.encrypt_bigfile(infile, outfile, pub_key)


class DecryptBigfileOperation(BigfileOperation):
    keyname = 'private'
    description = 'Decrypts an encrypted VARBLOCK file that was encrypted with pyrsa-encrypt-bigfile'
    operation = 'decrypt'
    operation_past = 'decrypted'
    operation_progressive = 'decrypting'
    key_class = rsa.PrivateKey

    def perform_operation(self, infile, outfile, priv_key, cli_args = None):
        return rsa.bigfile.decrypt_bigfile(infile, outfile, priv_key)


encrypt = EncryptOperation()
decrypt = DecryptOperation()
sign = SignOperation()
verify = VerifyOperation()
encrypt_bigfile = EncryptBigfileOperation()
decrypt_bigfile = DecryptBigfileOperation()
