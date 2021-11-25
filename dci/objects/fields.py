from oslo_versionedobjects import fields as object_fields

# Import fields from oslo_versionedobjects
EnumField = object_fields.EnumField
IntegerField = object_fields.IntegerField
UUIDField = object_fields.UUIDField
StringField = object_fields.StringField
DateTimeField = object_fields.DateTimeField
BooleanField = object_fields.BooleanField
ObjectField = object_fields.ObjectField
ListOfObjectsField = object_fields.ListOfObjectsField
ListOfStringsField = object_fields.ListOfStringsField
DictOfStringsField = object_fields.DictOfStringsField
IPAddressField = object_fields.IPAddressField
IPNetworkField = object_fields.IPNetworkField
UnspecifiedDefault = object_fields.UnspecifiedDefault
ListOfDictOfNullableStringsField = (
    object_fields.ListOfDictOfNullableStringsField)
