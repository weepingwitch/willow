try:
    ''.format_map({})
except AttributeError: # Python < 3.2
    import string
    def format_map(format_string, mapping, _format=string.Formatter().vformat):
        return _format(format_string, None, mapping)
    del string

    #XXX works on CPython 2.6
    # http://stackoverflow.com/questions/2444680/how-do-i-add-my-own-custom-attributes-to-existing-built-in-python-types-like-a/2450942#2450942
    import ctypes as c

    class PyObject_HEAD(c.Structure):
        _fields_ = [
            ('HEAD', c.c_ubyte * (object.__basicsize__ -  c.sizeof(c.c_void_p))),
            ('ob_type', c.c_void_p)
        ]

    _get_dict = c.pythonapi._PyObject_GetDictPtr
    _get_dict.restype = c.POINTER(c.py_object)
    _get_dict.argtypes = [c.py_object]

    def get_dict(object):
        return _get_dict(object).contents.value

    get_dict(str)['format_map'] = format_map
else: # Python 3.2+
    def format_map(format_string, mapping):
        return format_string.format_map(mapping)
