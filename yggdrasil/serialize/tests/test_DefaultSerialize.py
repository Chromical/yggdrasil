import copy
import numpy as np
import unittest
from yggdrasil.tests import YggTestClassInfo
from yggdrasil import backwards, tools, serialize
from yggdrasil.serialize import DefaultSerialize
from yggdrasil.metaschema.datatypes import encode_type


class TestDefaultSerialize(YggTestClassInfo):
    r"""Test class for DefaultSerialize class."""

    testing_option_kws = {}

    def __init__(self, *args, **kwargs):
        super(TestDefaultSerialize, self).__init__(*args, **kwargs)
        self._cls = 'DefaultSerialize'
        self._empty_msg = b''
        self._header_info = dict(arg1='1', arg2='two')
        self.attr_list += ['datatype', 'typedef', 'numpy_dtype']

    @property
    def mod(self):
        r"""Module for class to be tested."""
        return 'yggdrasil.serialize.%s' % self.cls

    def get_testing_options(self):
        r"""Get testing options."""
        return self.import_cls.get_testing_options(**self.testing_option_kws)

    @property
    def testing_options(self):
        r"""dict: Testing options."""
        if getattr(self, '_testing_options', None) is None:
            self._testing_options = self.get_testing_options()
        return self._testing_options
    
    @property
    def inst_kwargs(self):
        r"""Keyword arguments for creating the test instance."""
        out = super(TestDefaultSerialize, self).inst_kwargs
        out.update(self.testing_options['kwargs'])
        return out

    def empty_head(self, msg):
        r"""dict: Empty header for message only contains the size."""
        out = dict(size=len(msg), incomplete=False)
        if msg == tools.YGG_MSG_EOF:
            out['eof'] = True
        return out

    def map_sent2recv(self, obj):
        r"""Convert a sent object into a received one."""
        return obj

    def assert_result_equal(self, x, y):
        r"""Assert that serialized/deserialized objects equal."""
        self.assert_equal(x, self.map_sent2recv(y))

    def test_field_specs(self):
        r"""Test field specifiers."""
        self.assert_equal(self.instance.is_user_defined,
                          self.testing_options.get('is_user_defined', False))
        self.assert_equal(self.instance.numpy_dtype,
                          self.testing_options['dtype'])
        self.assert_equal(self.instance.typedef,
                          self.testing_options['typedef'])
        self.assert_equal(self.instance.extra_kwargs,
                          self.testing_options['extra_kwargs'])
        
    def test_serialize(self):
        r"""Test serialize/deserialize."""
        for iobj in self.testing_options['objects']:
            msg = self.instance.serialize(iobj)
            iout, ihead = self.instance.deserialize(msg)
            self.assert_result_equal(iout, iobj)
            # self.assert_equal(ihead, self.empty_head(msg))

    def test_deserialize_error(self):
        r"""Test error when deserializing message that is not bytes."""
        self.assert_raises(TypeError, self.instance.deserialize, None)
        
    def test_serialize_sinfo(self):
        r"""Test serialize/deserialize with serializer info."""
        if self.testing_options.get('is_user_defined', False):
            self.assert_raises(RuntimeError, self.instance.serialize,
                               self.testing_options['objects'][0],
                               add_serializer_info=True)
        else:
            hout = copy.deepcopy(self._header_info)
            hout.update(self.instance.serializer_info)
            temp_seri = serialize.get_serializer(
                seritype=self.instance.serializer_info['seritype'])
            for iobj in self.testing_options['objects']:
                hout.update(encode_type(iobj, typedef=self.instance.typedef))
                msg = self.instance.serialize(iobj, header_kwargs=self._header_info,
                                              add_serializer_info=True)
                iout, ihead = self.instance.deserialize(msg)
                hout.update(size=ihead['size'], id=ihead['id'],
                            incomplete=False)
                self.assert_result_equal(iout, iobj)
                self.assert_equal(ihead, hout)
                # Use info to reconstruct serializer
                iout, ihead = temp_seri.deserialize(msg)
                self.assert_result_equal(iout, iobj)
                self.assert_equal(ihead, hout)
                new_seri = serialize.get_serializer(**ihead)
                iout, ihead = new_seri.deserialize(msg)
                self.assert_result_equal(iout, iobj)
                self.assert_equal(ihead, hout)
            
    def test_serialize_header(self):
        r"""Test serialize/deserialize with header."""
        for iobj in self.testing_options['objects']:
            msg = self.instance.serialize(iobj, header_kwargs=self._header_info)
            iout, ihead = self.instance.deserialize(msg)
            self.assert_result_equal(iout, iobj)
            # self.assert_equal(ihead, self._header_info)
        
    def test_serialize_eof(self):
        r"""Test serialize/deserialize EOF."""
        iobj = tools.YGG_MSG_EOF
        msg = self.instance.serialize(iobj)
        iout, ihead = self.instance.deserialize(msg)
        self.assert_equal(iout, iobj)
        # self.assert_equal(ihead, self.empty_head(msg))
        
    def test_serialize_eof_header(self):
        r"""Test serialize/deserialize EOF with header."""
        iobj = tools.YGG_MSG_EOF
        msg = self.instance.serialize(iobj, header_kwargs=self._header_info)
        iout, ihead = self.instance.deserialize(msg)
        self.assert_equal(iout, iobj)
        # self.assert_equal(ihead, self.empty_head(msg))
        
    def test_serialize_no_format(self):
        r"""Test serialize/deserialize without format string."""
        if (len(self._inst_kwargs) == 0) and (self._cls == 'DefaultSerialize'):
            for iobj in self.testing_options['objects']:
                msg = self.instance.serialize(iobj,
                                              header_kwargs=self._header_info)
                iout, ihead = self.instance.deserialize(msg)
                self.assert_result_equal(iout, iobj)
                # self.assert_equal(ihead, self._header_info)
            # self.assert_raises(Exception, self.instance.serialize, ['msg', 0])
        
    def test_deserialize_empty(self):
        r"""Test call for empty string."""
        out, head = self.instance.deserialize(self._empty_msg)
        self.assert_result_equal(out, self.testing_options['empty'])
        self.assert_equal(head, self.empty_head(self._empty_msg))


class TestDefaultSerialize_format(TestDefaultSerialize):
    r"""Test class for DefaultSerialize class with format."""

    testing_option_kws = {'as_format': True}


class TestDefaultSerialize_array(TestDefaultSerialize_format):
    r"""Test class for DefaultSerialize class with format as array."""

    testing_option_kws = {'as_format': True, 'as_array': True}


class TestDefaultSerialize_func(TestDefaultSerialize):
    r"""Test class for DefaultSerialize class with functions."""

    testing_option_kws = {'as_format': True}
    
    def __init__(self, *args, **kwargs):
        super(TestDefaultSerialize_func, self).__init__(*args, **kwargs)
        self.func_serialize = self._func_serialize
        self.func_deserialize = self._func_deserialize

    def get_testing_options(self):
        r"""Get testing options."""
        out = {'kwargs': {'func_serialize': self.func_serialize,
                          'func_deserialize': self.func_deserialize},
               'empty': b'',
               'objects': [['one', np.int32(1), 1.0],
                           ['two', np.int32(2), 1.0]],
               'extra_kwargs': {},
               'typedef': {'type': 'bytes'},
               'dtype': None,
               'is_user_defined': True}
        return out
        
    def _func_serialize(self, args):
        r"""Method that serializes using repr."""
        return backwards.as_bytes(repr(args))

    def _func_deserialize(self, args):
        r"""Method that deserializes using eval."""
        if len(args) == 0:
            return self.testing_options['empty']
        x = eval(backwards.as_str(args))
        return x


class FakeSerializer(DefaultSerialize.DefaultSerialize):

    def func_serialize(self, args):
        r"""Method that serializes using repr."""
        return backwards.as_bytes(repr(args))

    def func_deserialize(self, args):
        r"""Method that deserializes using eval."""
        if len(args) == 0:
            return []
        x = eval(backwards.as_str(args))
        return x


class TestDefaultSerialize_class(TestDefaultSerialize_func):
    r"""Test class for DefaultSerialize class with classes."""

    def get_testing_options(self):
        r"""Get testing options."""
        temp_seri = FakeSerializer()
        assert(issubclass(temp_seri.__class__, DefaultSerialize.DefaultSerialize))
        out = super(TestDefaultSerialize_class, self).get_testing_options()
        out['kwargs'] = {'func_serialize': temp_seri,
                         'func_deserialize': temp_seri}
        return out
        

class TestDefaultSerialize_alias(TestDefaultSerialize_format):
    r"""Test class for DefaultSerialize class with alias."""

    def setup(self, *args, **kwargs):
        r"""Create an instance of the class."""
        super(TestDefaultSerialize_alias, self).setup(*args, **kwargs)
        alias = self.instance
        self._instance = DefaultSerialize.DefaultSerialize()
        self._instance._alias = alias


class TestDefaultSerialize_type(TestDefaultSerialize):
    r"""Test class for DefaultSerialize class with types."""

    def get_testing_options(self):
        r"""Get testing options."""
        out = {'kwargs': {'type': 'float'},
               'empty': b'',
               'objects': [float(x) for x in range(5)],
               'extra_kwargs': {},
               'typedef': {'type': 'float'},
               'dtype': None}
        return out


class TestDefaultSerialize_func_error(TestDefaultSerialize_func):
    r"""Test class for DefaultSerialize class with incorrect functions."""

    def _func_serialize(self, args):
        r"""Method that serializes using repr."""
        return args

    def test_serialize(self):
        r"""Test serialize with function that dosn't return correct type."""
        self.assert_raises(TypeError, self.instance.serialize, (1,))

    @unittest.skipIf(True, 'Error testing')
    def test_serialize_header(self):
        r"""Disabled: Test serialize/deserialize with header."""
        pass

    @unittest.skipIf(True, 'Error testing')
    def test_serialize_sinfo(self):
        r"""Disabled: Test serialize/deserialize with serializer info."""
        pass

    @unittest.skipIf(True, 'Error testing')
    def test_field_specs(self):
        r"""Disabled: Test field specifiers."""
        pass