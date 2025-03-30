#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\requests\certs.py
import os.path
try:
    from certifi import where
except ImportError:

    def where():
        return os.path.join(os.path.dirname(__file__), 'cacert.pem')


if __name__ == '__main__':
    print where()
