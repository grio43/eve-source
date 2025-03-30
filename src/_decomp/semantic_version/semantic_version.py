#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\semantic_version\semantic_version.py
from eveProto.generated.eve.semanticversion_pb2 import Specification as EveSpecification
from eveProto.generated.eve_public.semanticversion_pb2 import Specification as EvePublicSpecification
from functools import total_ordering

def _parse_semantic_version(text):
    try:
        ascii_semantic_version_string = text.encode('ascii')
    except UnicodeError:
        raise RuntimeError('Could not coerce {} to ASCII, version must only contain valid ASCII characters'.format(text))

    tokens = _tokenize(ascii_semantic_version_string)
    major, minor, patch, prerelease_tags, build_tags = _parse_tokens(tokens)
    return SemanticVersion(major, minor, patch, prerelease_tags, build_tags)


def _determine_next_token(character):
    if character.isdigit():
        return ('number', character)
    if character.isalnum():
        return ('tag', character)
    if character == '.':
        return ('seperator', None)
    if character == '-':
        return ('prerelease', None)
    if character == '+':
        return ('build', None)


def _tokenize(ascii_string):
    tokens = []
    current_token = None
    for idx, character in enumerate(ascii_string):
        if current_token is None:
            current_token = _determine_next_token(character)
            continue
        if current_token[0] == 'number':
            if character.isdigit():
                current_token = (current_token[0], current_token[1] + character)
                continue
            else:
                tokens.append(current_token)
                current_token = _determine_next_token(character)
                continue
        if current_token[0] == 'tag':
            if character.isalnum() or character == '-':
                current_token = (current_token[0], current_token[1] + character)
                continue
            else:
                tokens.append(current_token)
                current_token = _determine_next_token(character)
                continue
        if current_token[0] == 'seperator' or current_token[0] == 'prerelease' or current_token[0] == 'build':
            tokens.append(current_token)
            current_token = _determine_next_token(character)
            continue
        raise RuntimeError('Error parsing version string, reached {} of {}'.format(ascii_string[0:idx], self.text))

    tokens.append(current_token)
    return tokens


def _parse_tokens(tokens):
    current_state = 'major'
    major = None
    minor = None
    patch = None
    prerelease_tags = []
    build_tags = []
    for token in tokens:
        if current_state == 'major':
            if major is None:
                if token[0] != 'number':
                    raise RuntimeError('Error parsing version string, major version must be a number')
                major = int(token[1])
                continue
            else:
                if token[0] != 'seperator':
                    raise RuntimeError('Error parsing version string, versions must have a . seperator')
                current_state = 'minor'
                continue
        if current_state == 'minor':
            if minor is None:
                if token[0] != 'number':
                    raise RuntimeError('Error parsing version string, minor version must be a number')
                minor = int(token[1])
                continue
            else:
                if token[0] != 'seperator':
                    raise RuntimeError('Error parsing version string, versions must have a . seperator')
                current_state = 'patch'
                continue
        if current_state == 'patch':
            if patch is None:
                if token[0] != 'number':
                    raise RuntimeError('Error parsing version string, patch version must be a number')
                patch = int(token[1])
                continue
            else:
                if token[0] != 'prerelease' and token[0] != 'build':
                    raise RuntimeError('Error parsing version string, unexpected token following versions {} {}', token[0], token[1])
                if token[0] == 'prerelease':
                    current_state = 'prerelease_tags'
                    continue
                if token[0] == 'build':
                    current_state = 'build_tags'
                    continue
        if current_state == 'prerelease_tags':
            if token[0] != 'tag' and token[0] != 'number' and token[0] != 'seperator' and token[0] != 'build':
                raise RuntimeError('Error parsing version string, unexpected token following prerelease tags {} {}', token[0], token[1])
            if token[0] == 'build':
                current_state = 'build_tags'
                continue
            if token[0] == 'tag':
                prerelease_tags.append(token[1])
                continue
            if token[0] == 'number':
                prerelease_tags.append(str(token[1]))
            if token[0] == 'seperator':
                continue
        if current_state == 'build_tags':
            if token[0] != 'tag' and token[0] != 'number' and token[0] != 'seperator':
                raise RuntimeError('Error parsing version string, unexpected token following build tags {} {}', token[0], token[1])
            if token[0] == 'tag':
                build_tags.append(token[1])
                continue
            if token[0] == 'number':
                build_tags.append(str(token[1]))
            if token[0] == 'seperator':
                continue

    if major is None:
        raise RuntimeError('Error parsing version Major version missing.')
    if minor is None:
        raise RuntimeError('Error parsing version Minor version missing.')
    if patch is None:
        raise RuntimeError('Error parsing version Patch version missing.')
    return (major,
     minor,
     patch,
     prerelease_tags,
     build_tags)


@total_ordering

class SemanticVersion(object):

    def __init__(self, major, minor, patch, prerelease_tags, build_tags):
        self.major = major
        self.minor = minor
        self.patch = patch
        self.prerelease_tags = [ tag.encode('ascii') for tag in prerelease_tags ]
        self.build_tags = [ tag.encode('ascii') for tag in build_tags ]

    @staticmethod
    def from_proto(version_proto):
        return SemanticVersion(version_proto.major, version_proto.minor, version_proto.patch, version_proto.prerelease_tags, version_proto.build_tags)

    @staticmethod
    def from_string(version_string):
        return _parse_semantic_version(version_string)

    def to_eve_proto(self):
        return self._to_proto(EveSpecification)

    def to_eve_public_proto(self):
        return self._to_proto(EvePublicSpecification)

    def _to_proto(self, specification_class):
        spec = specification_class(major=self.major, minor=self.minor, patch=self.patch)
        for tag in self.prerelease_tags:
            spec.prerelease_tags.append(tag)

        for tag in self.build_tags:
            spec.build_tags.append(tag)

        return spec

    def __eq__(self, other):
        if not isinstance(other, SemanticVersion):
            return False
        return self.major == other.major and self.minor == other.minor and self.patch == other.patch and self.prerelease_tags == other.prerelease_tags and self.build_tags == other.build_tags

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        if not isinstance(other, SemanticVersion):
            return False
        if self.major != other.major:
            return self.major < other.major
        if self.minor != other.minor:
            return self.minor < other.minor
        if self.patch != other.patch:
            return self.patch < other.patch
        len_our_prerelease_tags = len(self.prerelease_tags)
        len_other_prerelease_tags = len(other.prerelease_tags)
        if len_our_prerelease_tags > 0 and len_other_prerelease_tags == 0:
            return True
        if len_other_prerelease_tags > 0 and len_our_prerelease_tags == 0:
            return False
        for idx, tag in enumerate(self.prerelease_tags):
            if idx == len_other_prerelease_tags:
                return False
            other_tag = other.prerelease_tags[idx]
            if tag.isdigit() and not other_tag.isdigit():
                return True
            if tag.isdigit() and other_tag.isdigit():
                our_num = int(tag)
                other_num = int(other_tag)
                if our_num == other_num:
                    continue
                return our_num < other_num
            if tag == other_tag:
                continue
            return tag < other_tag

        return len_our_prerelease_tags < len_other_prerelease_tags

    def __hash__(self):
        return hash((self.major,
         self.minor,
         self.patch,
         tuple(self.prerelease_tags),
         tuple(self.build_tags)))

    def __repr__(self):
        prerelease_string = ''
        if len(self.prerelease_tags) > 0:
            prerelease_string = '-' + '.'.join(self.prerelease_tags)
        build_string = ''
        if len(self.build_tags) > 0:
            build_string = '+' + '.'.join(self.build_tags)
        return '%s.%s.%s%s%s' % (self.major,
         self.minor,
         self.patch,
         prerelease_string,
         build_string)
