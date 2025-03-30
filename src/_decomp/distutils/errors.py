#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\stdlib\distutils\errors.py
__revision__ = '$Id: errors.py 82110 2010-06-20 13:38:51Z kristjan.jonsson $'

class DistutilsError(Exception):
    pass


class DistutilsModuleError(DistutilsError):
    pass


class DistutilsClassError(DistutilsError):
    pass


class DistutilsGetoptError(DistutilsError):
    pass


class DistutilsArgError(DistutilsError):
    pass


class DistutilsFileError(DistutilsError):
    pass


class DistutilsOptionError(DistutilsError):
    pass


class DistutilsSetupError(DistutilsError):
    pass


class DistutilsPlatformError(DistutilsError):
    pass


class DistutilsExecError(DistutilsError):
    pass


class DistutilsInternalError(DistutilsError):
    pass


class DistutilsTemplateError(DistutilsError):
    pass


class DistutilsByteCompileError(DistutilsError):
    pass


class CCompilerError(Exception):
    pass


class PreprocessError(CCompilerError):
    pass


class CompileError(CCompilerError):
    pass


class LibError(CCompilerError):
    pass


class LinkError(CCompilerError):
    pass


class UnknownFileError(CCompilerError):
    pass
