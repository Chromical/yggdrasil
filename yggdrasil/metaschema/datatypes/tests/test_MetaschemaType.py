import numpy as np
import copy
import pprint
import jsonschema
from yggdrasil.tests import assert_raises, assert_equal
from yggdrasil.metaschema.datatypes import MetaschemaTypeError
from yggdrasil.tests import YggTestClassInfo


class TestMetaschemaType(YggTestClassInfo):
    r"""Test class for MetaschemaType class."""

    _mod = 'MetaschemaType'
    _cls = 'MetaschemaType'
    _explicit = False

    def __init__(self, *args, **kwargs):
        super(TestMetaschemaType, self).__init__(*args, **kwargs)
        self._empty_msg = b''
        self._typedef = {}
        self._valid_encoded = []
        # {'type': self.import_cls.name,
        # 'data': 'nothing'}]
        self._invalid_encoded = [{}]
        self._valid_decoded = ['nothing']
        self._invalid_decoded = [None]
        self._compatible_objects = []
        self._encode_type_kwargs = {}
        self._encode_data_kwargs = {}
        self._valid_normalize = [(None, None)]

    @property
    def mod(self):
        r"""str: Absolute name of module containing class to be tested."""
        return 'yggdrasil.metaschema.datatypes.%s' % self._mod

    @property
    def typedef(self):
        r"""dict: Type definition."""
        out = copy.deepcopy(self._typedef)
        out['type'] = self.import_cls.name
        return out

    @property
    def inst_kwargs(self):
        r"""dict: Keyword arguments for creating a class instance."""
        return self._typedef

    def assert_result_equal(self, x, y):
        r"""Assert that serialized/deserialized objects equal."""
        if isinstance(x, dict):
            if not isinstance(y, dict):  # pragma: debug
                raise AssertionError("Second variable is not a dictionary.")
            for k in x.keys():
                if k not in y:  # pragma: debug
                    print('x')
                    pprint.pprint(x)
                    print('y')
                    pprint.pprint(y)
                    raise AssertionError("Key '%s' not in second dictionary." % k)
                self.assert_result_equal(x[k], y[k])
            for k in y.keys():
                if k not in x:  # pragma: debug
                    print('x')
                    pprint.pprint(x)
                    print('y')
                    pprint.pprint(y)
                    raise AssertionError("Key '%s' not in first dictionary." % k)
        elif isinstance(x, (list, tuple)):
            if not isinstance(y, (list, tuple)):  # pragma: debug
                raise AssertionError("Second variable is not a list or tuple.")
            if len(x) != len(y):  # pragma: debug
                print('x')
                pprint.pprint(x)
                print('y')
                pprint.pprint(y)
                raise AssertionError("Sizes do not match. %d vs. %d"
                                     % (len(x), len(y)))
            for ix, iy in zip(x, y):
                self.assert_result_equal(ix, iy)
        elif isinstance(x, np.ndarray):
            np.testing.assert_array_equal(x, y)
        else:
            if isinstance(y, (dict, list, tuple, np.ndarray)):  # pragma: debug
                print('x')
                pprint.pprint(x)
                print('y')
                pprint.pprint(y)
                raise AssertionError("Compared objects are different types. "
                                     "%s vs. %s" % (type(x), type(y)))
            assert_equal(x, y)

    def test_validate(self):
        r"""Test validation."""
        if self._cls == 'MetaschemaType':
            for x in self._valid_decoded:
                assert_raises(NotImplementedError, self.import_cls.validate, x)
        else:
            for x in self._valid_decoded:
                assert_equal(self.import_cls.validate(x), True)

    def test_normalize(self):
        r"""Test normalization."""
        for (x, y) in self._valid_normalize:
            z = self.import_cls.normalize(x)
            self.assert_result_equal(z, y)

    def test_fixed2base(self):
        r"""Test conversion of type definition from fixed type to the base."""
        if self._explicit:
            t1 = self.typedef
            x1 = self.import_cls.typedef_fixed2base(t1)
            t2 = copy.deepcopy(x1)
            t2['type'] = t1['type']
            x2 = self.import_cls.typedef_fixed2base(t2)
            assert_equal(x1, x2)
            y = self.import_cls.typedef_base2fixed(x1)
            assert_equal(y, self.typedef)

    def test_extract_typedef(self):
        r"""Test extract_typedef."""
        if len(self._valid_encoded) > 0:
            self.import_cls.extract_typedef(self._valid_encoded[0])

    def test_update_typedef(self):
        r"""Test update_typedef raises error on non-matching typename."""
        self.instance.update_typedef(**self.typedef)
        assert_raises(MetaschemaTypeError, self.instance.update_typedef,
                      type='invalid')
        if self._explicit:
            typedef_base = self.import_cls.typedef_fixed2base(self.typedef)
            self.instance.update_typedef(**typedef_base)

    def test_definition_schema(self):
        r"""Test definition schema."""
        s = self.import_cls.definition_schema()
        # jsonschema.Draft3Validator.check_schema(s)
        jsonschema.Draft4Validator.check_schema(s)

    def test_metadata_schema(self):
        r"""Test metadata schema."""
        s = self.import_cls.metadata_schema()
        # jsonschema.Draft3Validator.check_schema(s)
        jsonschema.Draft4Validator.check_schema(s)

    def test_encode_data(self):
        r"""Test encode/decode data & type."""
        if self._cls == 'MetaschemaType':
            for x in self._valid_decoded:
                assert_raises(NotImplementedError, self.import_cls.encode_type, x)
                assert_raises(NotImplementedError, self.import_cls.encode_data,
                              x, self.typedef)
            assert_raises(NotImplementedError, self.import_cls.decode_data, None,
                          self.typedef)
        else:
            for x in self._valid_decoded:
                y = self.import_cls.encode_type(x, **self._encode_type_kwargs)
                z = self.import_cls.encode_data(x, y, **self._encode_data_kwargs)
                x2 = self.import_cls.decode_data(z, y)
                self.assert_result_equal(x2, x)
            if self._cls != 'JSONNullMetaschemaType':
                assert_raises(MetaschemaTypeError, self.import_cls.encode_type, None)

    def test_check_encoded(self):
        r"""Test check_encoded."""
        # Test invalid for incorrect typedef
        if len(self._valid_encoded) > 0:
            assert_equal(self.import_cls.check_encoded(self._valid_encoded[0],
                                                       {}), False)
        # Test valid
        for x in self._valid_encoded:
            assert_equal(self.import_cls.check_encoded(x, self.typedef), True)
        # Test invalid
        for x in self._invalid_encoded:
            assert_equal(self.import_cls.check_encoded(x, self.typedef), False)

    def test_check_decoded(self):
        r"""Test check_decoded."""
        # Not implemented for base class
        if self._cls == 'MetaschemaType':
            for x in self._valid_decoded:
                assert_raises(NotImplementedError, self.import_cls.check_decoded,
                              x, self.typedef)
        else:
            # Test object alone
            if len(self._valid_decoded) > 0:
                x = self._valid_decoded[0]
                assert_equal(self.import_cls.check_decoded(x, None), True)
            # Test valid
            for x in self._valid_decoded:
                assert_equal(self.import_cls.check_decoded(x, self.typedef), True)
            # Test invalid with incorrect typedef
            for x in self._valid_decoded:
                assert_equal(self.import_cls.check_decoded(x, {}), False)
            # Test invalid
            for x in self._invalid_decoded:
                assert_equal(self.import_cls.check_decoded(x, self.typedef), False)

    def test_encode_errors(self):
        r"""Test error on encode."""
        if self._cls == 'MetaschemaType':
            assert_raises(NotImplementedError, self.import_cls.encode,
                          self._invalid_decoded[0], self.typedef)
        else:
            assert_raises((ValueError, jsonschema.exceptions.ValidationError),
                          self.import_cls.encode,
                          self._invalid_decoded[0], self.typedef)

    def test_decode_errors(self):
        r"""Test error on decode."""
        assert_raises((ValueError, jsonschema.exceptions.ValidationError),
                      self.import_cls.decode,
                      self._invalid_encoded[0], self.typedef)

    def test_transform_type(self):
        r"""Test transform_type."""
        for x, y, typedef in self._compatible_objects:
            z = self.import_cls.transform_type(x, typedef)
            self.assert_result_equal(z, y)

    def test_serialize(self):
        r"""Test serialize/deserialize."""
        if self._cls == 'MetaschemaType':
            for x in self._valid_decoded:
                assert_raises(NotImplementedError, self.instance.serialize, x)
        else:
            for x in self._valid_decoded:
                msg = self.instance.serialize(x)
                y = self.instance.deserialize(msg)
                self.assert_result_equal(y[0], x)

    def test_serialize_error(self):
        r"""Test error when serializing metadata that already contains 'data'."""
        if (self._cls != 'MetaschemaType') and (len(self._valid_decoded) > 0):
            assert_raises(RuntimeError, self.instance.serialize,
                          self._valid_decoded[0], data='something')

    def test_deserialize_error(self):
        r"""Test error when deserializing message that is not bytes."""
        assert_raises(TypeError, self.instance.deserialize, self)
        assert_raises(ValueError, self.instance.deserialize, b'invalid')
        
    def test_deserialize_empty(self):
        r"""Test call for empty string."""
        out = self.instance.deserialize(self._empty_msg)
        self.assert_result_equal(out[0], self.instance._empty_msg)
        assert_equal(out[1], dict(size=0, incomplete=False))
        # assert_equal(out, self.instance._empty_msg)

    def test_deserialize_incomplete(self):
        r"""Test call for incomplete message."""
        if (self._cls != 'MetaschemaType') and (len(self._valid_decoded) > 0):
            out = self.instance.serialize(self._valid_decoded[0])
            obj, metadata = self.instance.deserialize(out[:-1])
            assert_equal(metadata['incomplete'], True)