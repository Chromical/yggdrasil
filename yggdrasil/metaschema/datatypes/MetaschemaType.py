import copy
import json
import uuid
import pprint
import jsonschema
from yggdrasil import backwards, tools
from yggdrasil.metaschema import get_metaschema, get_validator
from yggdrasil.metaschema.datatypes import (
    MetaschemaTypeError, compare_schema, YGG_MSG_HEAD, get_type_class,
    conversions)
from yggdrasil.metaschema.properties import get_metaschema_property


def _get_single_array_element(arr):
    return arr[0]


class MetaschemaType(object):
    r"""Base type that should be subclassed by user defined types. Attributes
    should be overwritten to match the type.

    Arguments:
        **kwargs: All keyword arguments are assumed to be type definition
            properties which will be used to validate serialized/deserialized
            messages.

    Attributes:
        name (str): Name of the type for use in YAML files & form options.
        description (str): A short description of the type.
        properties (list): List of JSON schema properties that this type uses.
        definition_properties (list): Type properties that are required for YAML
            or form entries specifying the type. These will also be used to
            validate type definitions.
        metadata_properties (list): Type properties that are required for
            deserializing instances of the type that have been serialized.
        python_types (list): List of python types that this type encompasses.
        specificity (int): Specificity of the type. Types with larger values are
            more specific while types with smaller values are more general. Base
            types have a specificity of 0. More specific types are checked first
            before more general ones.
        is_fixed (bool): True if the type is a fixed version of another type. See
            FixedMetaschemaType for details.

    """

    name = 'base'
    description = 'A generic base type for users to build on.'
    properties = ['type', 'title']
    definition_properties = ['type']
    metadata_properties = ['type']
    extract_properties = ['type', 'title']
    python_types = []
    specificity = 0
    is_fixed = False
    _empty_msg = b''
    _replaces_existing = False
    
    def __init__(self, **typedef):
        self._typedef = {}
        typedef.setdefault('type', self.name)
        self.update_typedef(**typedef)

    # Methods to be overridden by subclasses
    @classmethod
    def encode_data(cls, obj, typedef):
        r"""Encode an object's data.

        Args:
            obj (object): Object to encode.
            typedef (dict): Type definition that should be used to encode the
                object.

        Returns:
            string: Encoded object.

        """
        raise NotImplementedError("Method must be overridden by the subclass.")

    @classmethod
    def encode_data_readable(cls, obj, typedef):
        r"""Encode an object's data in a readable format.

        Args:
            obj (object): Object to encode.
            typedef (dict): Type definition that should be used to encode the
                object.

        Returns:
            string: Encoded object.

        """
        return cls.encode_data(obj, typedef)

    @classmethod
    def decode_data(cls, obj, typedef):
        r"""Decode an object.

        Args:
            obj (string): Encoded object to decode.
            typedef (dict): Type definition that should be used to decode the
                object.

        Returns:
            object: Decoded object.

        """
        raise NotImplementedError("Method must be overridden by the subclass.")

    @classmethod
    def transform_type(cls, obj, typedef=None):
        r"""Transform an object based on type info.

        Args:
            obj (object): Object to transform.
            typedef (dict): Type definition that should be used to transform the
                object.

        Returns:
            object: Transformed object.

        """
        return obj

    @classmethod
    def coerce_type(cls, obj, typedef=None, **kwargs):
        r"""Coerce objects of specific types to match the data type.

        Args:
            obj (object): Object to be coerced.
            typedef (dict, optional): Type defintion that object should be
                coerced to. Defaults to None.
            **kwargs: Additional keyword arguments are metadata entries that may
                aid in coercing the type.

        Returns:
            object: Coerced object.

        """
        return obj

    # Methods not to be modified by subclasses
    @classmethod
    def issubtype(cls, t):
        r"""Determine if this type is a subclass of the provided type.

        Args:
            t (str): Type name to check against.

        Returns:
            bool: True if this type is a subtype of the specified type t.

        """
        return (cls.name == t)

    @classmethod
    def validate(cls, obj, raise_errors=False):
        r"""Validate an object to check if it could be of this type.

        Args:
            obj (object): Object to validate.
            raise_errors (bool, optional): If True, errors will be raised when
                the object fails to be validated. Defaults to False.

        Returns:
            bool: True if the object could be of this type, False otherwise.

        """
        if not cls.python_types:
            raise NotImplementedError("Attribute 'python_types' must be set.")
        out = isinstance(obj, cls.python_types)
        if (not out) and raise_errors:
            raise ValueError(("Object of type '%s' is not one of the accepted "
                              + "Python types (%s) for this type (%s).") %
                             (type(obj), cls.python_types, cls.name))
        return out

    @classmethod
    def normalize(cls, obj):
        r"""Normalize an object, if possible, to conform to this type.

        Args:
            obj (object): Object to normalize.

        Returns:
            object: Normalized object.

        """
        return obj

    @classmethod
    def encode_type(cls, obj, typedef=None, **kwargs):
        r"""Encode an object's type definition.

        Args:
            obj (object): Object to encode.
            typedef (dict, optional): Type properties that should be used to
                initialize the encoded type definition in certain cases.
                Defaults to None and is ignored.
            **kwargs: Additional keyword arguments are treated as additional
                schema properties.

        Raises:
            MetaschemaTypeError: If the object is not the correct type.

        Returns:
            dict: Encoded type definition.

        """
        obj = cls.coerce_type(obj, typedef=typedef)
        if typedef is None:
            typedef = {}
        if not cls.validate(obj):
            raise MetaschemaTypeError("Object could not be encoded as '%s' type."
                                      % cls.name)
        out = copy.deepcopy(kwargs)
        for x in cls.properties:
            itypedef = typedef.get(x, out.get(x, None))
            if x == 'type':
                out['type'] = cls.name
            elif x == 'title':
                if itypedef is not None:
                    out[x] = itypedef
            else:
                prop_cls = get_metaschema_property(x)
                out[x] = prop_cls.encode(obj, typedef=itypedef)
        return out

    @classmethod
    def get_extract_properties(cls, metadata):
        r"""Get the list of properties that should be kept when extracting a
        typedef from message metadata.

        Args:
            metadata (dict): Metadata that typedef is being extracted from.

        Returns:
            list: Keywords that should be kept in the typedef.

        """
        return copy.deepcopy(cls.extract_properties)

    @classmethod
    def extract_typedef(cls, metadata, reqkeys=None):
        r"""Extract the minimum typedef required for this type from the provided
        metadata.

        Args:
            metadata (dict): Message metadata.
            reqkeys (list, optional): Set of keys to keep in the definition.
                Defaults to the required definition keys.

        Returns:
            dict: Encoded type definition with unncessary properties removed.

        """
        out = copy.deepcopy(metadata)
        if reqkeys is None:
            reqkeys = cls.get_extract_properties(metadata)
        keylist = [k for k in out.keys()]
        for k in keylist:
            if k not in reqkeys:
                del out[k]
        return out

    def update_typedef(self, **kwargs):
        r"""Update the current typedef with new values.

        Args:
            **kwargs: All keyword arguments are considered to be new type
                definitions. If they are a valid definition property, they
                will be copied to the typedef associated with the instance.

        Returns:
            dict: A dictionary of keyword arguments that were not added to the
                type definition.

        Raises:
            MetaschemaTypeError: If the current type does not match the type being
                updated to.

        """
        typename0 = self._typedef.get('type', None)
        typename1 = kwargs.get('type', None)
        # Check typename to make sure this is possible
        if typename1 and typename0 and (typename1 != typename0):
            raise MetaschemaTypeError(
                "Cannot update typedef for type '%s' to be '%s'."
                % (typename0, typename1))
        # Copy over valid properties
        all_keys = [k for k in kwargs.keys()]
        # req_keys = self.definition_schema().get('required', [])
        for k in all_keys:
            # if k in req_keys:
            self._typedef[k] = kwargs.pop(k)
        # Validate
        self.validate_definition(self._typedef)
        return kwargs

    @classmethod
    def metaschema(cls):
        r"""JSON meta schema for validating schemas for this type."""
        return get_metaschema()

    @classmethod
    def validator(cls):
        r"""JSON schema validator for the meta schema that includes added types."""
        return get_validator()

    @classmethod
    def definition_schema(cls):
        r"""JSON schema for validating a type definition schema."""
        out = {'title': cls.name,
               'description': cls.description,
               'type': 'object',
               'required': copy.deepcopy(cls.definition_properties),
               'properties': {'type': {'enum': [cls.name]}}}
        return out

    @classmethod
    def metadata_schema(cls):
        r"""JSON schema for validating a JSON serialization of the type."""
        out = {'title': cls.name,
               'description': cls.description,
               'type': 'object',
               'required': copy.deepcopy(cls.metadata_properties),
               'properties': {'type': {'enum': [cls.name]}}}
        return out

    @classmethod
    def validate_metadata(cls, obj):
        r"""Validates an encoded object.

        Args:
            obj (string): Encoded object to validate.

        """
        if ((isinstance(obj, dict) and ('type' in obj)
             and (obj['type'] != cls.name))):
            type_cls = get_type_class(obj['type'])
            if type_cls.is_fixed and type_cls.issubtype(cls.name):
                obj = type_cls.typedef_fixed2base(obj)
        # jsonschema.validate(obj, cls.metaschema(), cls=cls.validator())
        jsonschema.validate(obj, cls.metadata_schema(), cls=cls.validator())

    @classmethod
    def validate_definition(cls, obj):
        r"""Validates a type definition.

        Args:
            obj (object): Type definition to validate.

        """
        # jsonschema.validate(obj, cls.metaschema(), cls=cls.validator())
        jsonschema.validate(obj, cls.definition_schema(), cls=cls.validator())

    @classmethod
    def validate_instance(cls, obj, typedef):
        r"""Validates an object against a type definition.

        Args:
            obj (object): Object to validate against a type definition.
            typedef (dict): Type definition to validate against.

        """
        # cls.validate_definition(typedef)
        jsonschema.validate(obj, typedef, cls=cls.validator())

    @classmethod
    def normalize_definition(cls, obj):
        r"""Normalizes a type definition.

        Args:
            obj (object): Type definition to normalize.

        Returns:
            object: Normalized type definition.

        """
        for x in cls.properties:
            if x not in obj:
                prop_cls = get_metaschema_property(x)
                obj = prop_cls.normalize_in_schema(obj)
        return obj

    @classmethod
    def check_encoded(cls, metadata, typedef=None, raise_errors=False,
                      typedef_validated=False):
        r"""Checks if the metadata for an encoded object matches the type
        definition.

        Args:
            metadata (dict): Meta data to be tested.
            typedef (dict, optional): Type properties that object should
                be tested against. Defaults to None and object may have
                any values for the type properties (so long as they match
                the schema.
            raise_errors (bool, optional): If True, any errors determining that
                encoded object is not of this type will be raised. Defaults to
                False.
            typedef_validated (bool, optional): If True, the type definition
                is taken as already having been validated and will not be
                validated again during the encoding process. Defaults to False.

        Returns:
            bool: True if the metadata matches the type definition, False
                otherwise.

        """
        try:
            cls.validate_metadata(metadata)
        except jsonschema.exceptions.ValidationError:
            if raise_errors:
                raise
            return False
        if typedef is not None:
            if not typedef_validated:
                try:
                    cls.validate_definition(typedef)
                except jsonschema.exceptions.ValidationError:
                    if raise_errors:
                        raise
                    return False
            errors = [e for e in compare_schema(metadata, typedef)]
            if errors:
                error_msg = "Error(s) in comparison:"
                for e in errors:
                    error_msg += ('\t%s' % e)
                if raise_errors:
                    raise ValueError(error_msg)
                return False
        return True

    @classmethod
    def check_decoded(cls, obj, typedef=None, raise_errors=False,
                      typedef_validated=False):
        r"""Checks if an object is of the this type.

        Args:
            obj (object): Object to be tested.
            typedef (dict, optional): Type properties that object should be tested
                against. Defaults to None and is not used.
            raise_errors (bool, optional): If True, any errors determining that
                decoded object is not of this type will be raised. Defaults to
                False.
            typedef_validated (bool, optional): If True, the type definition
                is taken as already having been validated and will not be
                validated again during the encoding process. Defaults to False.

        Returns:
            bool: Truth of if the input object is of this type.

        """
        if not cls.validate(obj, raise_errors=raise_errors):
            return False
        if typedef is None:
            return True
        # Validate definition
        if not typedef_validated:
            try:
                cls.validate_definition(typedef)
            except jsonschema.exceptions.ValidationError:
                if raise_errors:
                    raise
                return False
        # Validate instance against definition
        try:
            cls.validate_instance(obj, typedef)
        except jsonschema.exceptions.ValidationError:
            if raise_errors:
                raise
            return False
        return True

    @classmethod
    def encode(cls, obj, typedef=None, typedef_validated=False, **kwargs):
        r"""Encode an object.

        Args:
            obj (object): Object to encode.
            typedef (dict, optional): Type properties that object should
                be tested against. Defaults to None and object may have
                any values for the type properties (so long as they match
                the schema.
            typedef_validated (bool, optional): If True, the type definition
                is taken as already having been validated and will not be
                validated again during the encoding process. Defaults to False.
            **kwargs: Additional keyword arguments are added to the metadata.

        Returns:
            tuple(dict, bytes): Encoded object with type definition and data
                serialized to bytes.

        Raises:
            ValueError: If the object does not match the type definition.
            ValueError: If the encoded metadata does not match the type
                definition.
            TypeError: If the encoded data is not of bytes type.

        """
        # Coerce, then check object, then transform
        obj = cls.coerce_type(obj, typedef=typedef,
                              typedef_validated=typedef_validated, **kwargs)
        cls.check_decoded(obj, typedef, raise_errors=True,
                          typedef_validated=typedef_validated)
        obj_t = cls.transform_type(obj, typedef)
        # Encode
        metadata = cls.encode_type(obj_t, typedef=typedef)
        data = cls.encode_data(obj_t, metadata)
        # Add extra keyword arguments to metadata, ensuring type not overwritten
        for k, v in kwargs.items():
            if (k in metadata) and (v != metadata[k]):
                error_str = ("Key '%s' set by the type encoder.\n"
                             + " User defined value:\n%s\n"
                             + "Type encoder defined value:\n%s\n") % (
                                 k, pprint.pformat(v), pprint.pformat(metadata[k]))
                raise RuntimeError(error_str)
            metadata[k] = v
        return metadata, data

    @classmethod
    def decode(cls, metadata, data, typedef=None, typedef_validated=False):
        r"""Decode an object.

        Args:
            metadata (dict): Meta data describing the data.
            data (bytes): Encoded data.
            typedef (dict, optional): Type properties that decoded object should
                be tested against. Defaults to None and object may have any
                values for the type properties (so long as they match the schema).
            typedef_validated (bool, optional): If True, the type definition
                is taken as already having been validated and will not be
                validated again during the encoding process. Defaults to False.

        Returns:
            object: Decoded object.

        Raises:
            ValueError: If the metadata does not match the type definition.
            ValueError: If the decoded object does not match type definition.

        """
        conv_func = None
        if not cls.check_encoded(metadata, typedef,
                                 typedef_validated=typedef_validated):
            if ('type' in metadata) and (typedef == {'type': 'bytes'}):
                new_cls = get_type_class(metadata['type'])
                return new_cls.decode(metadata, data)
            if ((isinstance(metadata, dict)
                 and (len(metadata.get('items', [])) == 1)
                 and cls.check_encoded(metadata['items'][0], typedef))):
                conv_func = _get_single_array_element
            else:
                conv_func = conversions.get_conversion(metadata.get('type', None),
                                                       cls.name)
            if not conv_func:
                cls.check_encoded(metadata, typedef, raise_errors=True,
                                  typedef_validated=typedef_validated)
        if conv_func:
            new_cls = get_type_class(metadata['type'])
            out = conv_func(new_cls.decode(metadata, data))
        else:
            out = cls.decode_data(data, metadata)
        out = cls.transform_type(out, typedef)
        return out

    def serialize(self, obj, no_metadata=False, dont_encode=False, **kwargs):
        r"""Serialize a message.

        Args:
            obj (object): Python object to be formatted.
            no_metadata (bool, optional): If True, no metadata will be added to
                the serialized message. Defaults to False.
            dont_encode (bool, optional): If True, the input message will not
                be encoded using type specific or JSON encoding. Defaults to
                False.
            **kwargs: Additional keyword arguments are added to the metadata.

        Returns:
            bytes, str: Serialized message.

        """
        if ((isinstance(obj, backwards.bytes_type)
             and ((obj == tools.YGG_MSG_EOF) or kwargs.get('raw', False)
                  or dont_encode))):
            metadata = kwargs
            data = obj
            is_raw = True
        else:
            metadata, data = self.encode(obj, typedef=self._typedef,
                                         typedef_validated=True, **kwargs)
            is_raw = False
        for k in ['size', 'data']:
            if k in metadata:
                raise RuntimeError("'%s' is a reserved keyword in the metadata." % k)
        if not is_raw:
            data = backwards.as_bytes(json.dumps(data, sort_keys=True))
        if no_metadata:
            return data
        metadata['size'] = len(data)
        metadata.setdefault('id', str(uuid.uuid4()))
        metadata = backwards.as_bytes(json.dumps(metadata, sort_keys=True))
        msg = YGG_MSG_HEAD + metadata + YGG_MSG_HEAD + data
        return msg
    
    def deserialize(self, msg, no_data=False, metadata=None, dont_decode=False):
        r"""Deserialize a message.

        Args:
            msg (str, bytes): Message to be deserialized.
            no_data (bool, optional): If True, only the metadata is returned.
                Defaults to False.
            metadata (dict, optional): Metadata that should be used to deserialize
                the message instead of the current header content. Defaults to
                None and is not used.
            dont_decode (bool, optional): If True, type specific and JSON
                decoding will not be used to decode the message. Defaults to
                False.

        Returns:
            tuple(obj, dict): Deserialized message and header information.

        Raises:
            TypeError: If msg is not bytes type (str on Python 2).
            ValueError: If msg does not contain the header separator.

        """
        if not isinstance(msg, backwards.bytes_type):
            raise TypeError("Message to be deserialized is not bytes type.")
        # Check for header
        if YGG_MSG_HEAD in msg:
            if metadata is not None:
                raise ValueError("Metadata in header and provided by keyword.")
            _, metadata, data = msg.split(YGG_MSG_HEAD, 2)
            if len(metadata) == 0:
                metadata = dict(size=len(data))
            else:
                metadata = json.loads(backwards.as_unicode(metadata))
        else:
            data = msg
            if metadata is None:
                metadata = dict(size=len(msg))
                if (((len(msg) > 0) and (msg != tools.YGG_MSG_EOF)
                     and (self._typedef != {'type': 'bytes'})
                     and (not dont_decode))):
                    raise ValueError("Header marker not in message.")
        # Set flags based on data
        metadata['incomplete'] = (len(data) < metadata['size'])
        if (data == tools.YGG_MSG_EOF):
            metadata['raw'] = True
        # Return based on flags
        if no_data:
            return metadata
        elif len(data) == 0:
            return self._empty_msg, metadata
        elif (metadata['incomplete'] or metadata.get('raw', False)
              or (metadata.get('type', None) == 'direct') or dont_decode):
            return data, metadata
        else:
            data = json.loads(backwards.as_unicode(data))
            obj = self.decode(metadata, data, self._typedef,
                              typedef_validated=True)
        return obj, metadata