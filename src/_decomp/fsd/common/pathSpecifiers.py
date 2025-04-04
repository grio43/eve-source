#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsd\common\pathSpecifiers.py
import re
import itertools
import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

def GetPathSpecifierRegex(specifier):

    def regexMatch(match):
        if match.group(0) == '*':
            return '[A-Za-z0-9_\\-\\.]*'
        if match.group(0) == '...':
            return '(?:[A-Za-z0-9_\\-\\.]+/)*[A-Za-z0-9_\\-\\.]*'
        if match.group(0) == '.':
            return '\\.'
        return match.group(0)

    return '^' + re.sub('(\\.\\.\\.|\\*|\\.)', regexMatch, specifier) + '$'


def CompilePathSpecifier(specifier):
    return re.compile(GetPathSpecifierRegex(specifier))


def ComposeFilenameAndDirectoriesForMatching(filename, directories):
    filepathForMatching = '/'.join(directories)
    if filepathForMatching != '':
        filepathForMatching += '/' + filename
    else:
        filepathForMatching = filename
    return filepathForMatching


def PathMatchesSpecifier(path, specifier):
    return specifier.match(path) is not None


slashSeparator = re.compile('[/\\\\]')

def GetMaxRecursionDepth(specifier):
    if '...' in specifier:
        return -1
    return len(re.split(slashSeparator, specifier)) - 1


def MatchSpecifierList(filename, directoriesFromRoot, specifierList):
    path = ComposeFilenameAndDirectoriesForMatching(filename, directoriesFromRoot)
    return MatchSpecifierListWithRelativePath(path, specifierList)


def MatchSpecifierListWithRelativePath(path, specifierList):
    return any(itertools.imap(lambda (p, s): PathMatchesSpecifier(p, s), itertools.imap(lambda i: (path, i), specifierList)))


def CompilerSpecifierToList(specifier):
    if isinstance(specifier, basestring):
        return [CompilePathSpecifier(specifier)]
    else:
        return map(CompilePathSpecifier, specifier)


class PathConditional(object):

    def __init__(self, includes = None, excludes = None):
        if includes is not None:
            self.includes = CompilerSpecifierToList(includes)
        else:
            self.includes = None
        if excludes is not None:
            self.excludes = CompilerSpecifierToList(excludes)
        else:
            self.excludes = None

    def Matches(self, path):
        if self.includes is not None:
            if not MatchSpecifierListWithRelativePath(path, self.includes):
                return False
        if self.excludes is not None:
            if MatchSpecifierListWithRelativePath(path, self.excludes):
                log.debug('Path %s excluded' % path)
                return False
            log.debug('Path %s was not excluded by provided excludes' % path)
        else:
            log.debug('No exclude modifiers to test on %s' % path)
        return True
