#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsd\schemas\loaders\objectLoader.py
import ctypes
import array
import cStringIO
from fsd.schemas.path import FsdDataPathObject
import fsd.schemas.predefinedStructTypes as structTypes

class ObjectLoader(object):

    def __init__(self, data, offset, schema, path, extraState):
        self.__data__ = data
        self.__offset__ = offset
        self.__schema__ = schema
        self.__extraState__ = extraState
        self.__path__ = path
        self.__hasOptionalAttributes__ = False
        self.__offsetAttributesOffsetLookupTable__ = {}
        if 'size' not in schema:
            if self.__schema__['optionalValueLookups']:
                self.__hasOptionalAttributes__ = True
                optionalAttributesField = structTypes.uint64.unpack_from(data, offset + schema['endOfFixedSizeData'])[0]
                optionalLookups = dict(schema['optionalValueLookups'])
                __offsetAttributes__ = []
                for curr_attr in schema['attributesWithVariableOffsets']:
                    if curr_attr in optionalLookups:
                        if optionalAttributesField & optionalLookups[curr_attr]:
                            __offsetAttributes__.append(curr_attr)
                    else:
                        __offsetAttributes__.append(curr_attr)

            else:
                __offsetAttributes__ = schema['attributesWithVariableOffsets'][:]
            offsetAttributeArrayStart = offset + schema.get('endOfFixedSizeData', 0) + 8
            offsetAttributeOffsetsType = ctypes.c_uint32 * len(__offsetAttributes__)
            self.__variableDataOffsetBase__ = offsetAttributeArrayStart + ctypes.sizeof(offsetAttributeOffsetsType)
            offsetData = data[offsetAttributeArrayStart:offsetAttributeArrayStart + ctypes.sizeof(offsetAttributeOffsetsType)]
            offsetTable = array.array('I', offsetData).tolist()
            for k, v in zip(__offsetAttributes__, offsetTable):
                self.__offsetAttributesOffsetLookupTable__[k] = v

    def __repr__(self):
        return '<FSD Object: %s >' % self.__path__

    def __str__(self):
        representation = cStringIO.StringIO()
        attributeData = {}
        for attributeName, attributeSchema in self.__schema__['attributes'].iteritems():
            if self.__attributeIsPresent__(attributeName, attributeSchema):
                attributeValue = getattr(self, attributeName)
                if attributeSchema['type'] == 'object':
                    attributeData[attributeName] = repr(attributeValue)
                else:
                    attributeData[attributeName] = attributeValue
            else:
                attributeData[attributeName] = '-- not present --'

        representation.write('<FSD Object %s: %s>\n' % (self.__path__, attributeData))
        return representation.getvalue()

    def __getitem__(self, key):
        if key not in self.__schema__['attributes']:
            raise KeyError("Object: %s - Attribute '%s' is not in the schema for this object.                It may be removed by the 'usage' flag under the build configuration that produced this data." % (self.__path__, key))
        attributeSchema = self.__schema__['attributes'][key]
        if key in self.__schema__['constantAttributeOffsets']:
            return self.__extraState__.RepresentSchemaNode(self.__data__, self.__offset__ + self.__schema__['constantAttributeOffsets'][key], FsdDataPathObject('.%s' % str(key), parent=self.__path__), attributeSchema)
        else:
            if key not in self.__offsetAttributesOffsetLookupTable__:
                if 'default' in attributeSchema:
                    return attributeSchema['default']
                raise KeyError("Object: %s - Attribute '%s' is not present on this instance." % (self.__path__, key))
            return self.__extraState__.RepresentSchemaNode(self.__data__, self.__variableDataOffsetBase__ + self.__offsetAttributesOffsetLookupTable__[key], FsdDataPathObject('.%s' % str(key), parent=self.__path__), attributeSchema)

    def __getattr__(self, name):
        try:
            return self.__getitem__(name)
        except KeyError as e:
            raise AttributeError(str(e))

    def __attributeIsPresent__(self, attributeName, attributeSchema):
        attributeIsOptional = 'isOptional' in attributeSchema
        attributeHasDefault = 'default' in attributeSchema
        if attributeIsOptional and not attributeHasDefault:
            if not hasattr(self, attributeName):
                return False
        return True

    def __getBinaryObjectAttributes__(self):
        attributes = []
        for attributeName, attributeSchema in self.__schema__['attributes'].iteritems():
            if self.__attributeIsPresent__(attributeName, attributeSchema):
                attributes.append(attributeName)

        return sorted(attributes)

    def __dir__(self):
        attributes = set()
        attributes.update(dir(type(self)))
        attributes.update(list(self.__dict__))
        attributes.update(self.__getBinaryObjectAttributes__())
        return sorted(attributes)
