#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsd\schemas\schemaCompare.py
import collections

def _SchemaListEqual(schemaNodeList, otherSchemaNodeList):
    if len(schemaNodeList) != len(otherSchemaNodeList):
        return False
    for schemaNode in schemaNodeList:
        if schemaNode not in otherSchemaNodeList:
            return False

    return True


def _SchemaDictEqual(schema, otherSchema):
    keySet = set(schema.keys())
    otherKeySet = set(otherSchema.keys())
    if len(set.symmetric_difference(keySet, otherKeySet)) != 0:
        return False
    for schemaKey, schemaNode in schema.iteritems():
        if isinstance(schemaNode, list):
            if not _SchemaListEqual(schemaNode, otherSchema[schemaKey]):
                return False
        elif isinstance(schemaNode, dict):
            if not _SchemaDictEqual(schemaNode, otherSchema[schemaKey]):
                return False
        elif schemaNode != otherSchema[schemaKey]:
            return False

    return True


def SchemasEqual(schema, otherSchema):
    return _SchemaDictEqual(schema, otherSchema)
