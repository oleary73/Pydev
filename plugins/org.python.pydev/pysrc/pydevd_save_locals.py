"""
Utility for saving locals.

Working for python and python stackless 2.7 for now (to work for other versions
the expected structures have to be updated).
"""
import platform
import sys


version_info = sys.version_info
version = '%d.%d' % version_info[0:2]


try:
    import stackless  # @UnresolvedImport @UnusedImport
    is_stackless = True
except:
    is_stackless = False

try:
    is_cpython = platform.python_implementation().lower() == 'cpython'
except:
    is_cpython = False


def save_locals(locals_dict, frame):
    '''
    Stub which does nothing. We'll generate the proper version later on
    if we are able to make the mapping to the proper python version.
    '''


def create_save_locals():
    try:
        import ctypes
    except:
        import traceback;traceback.print_exc()
        return lambda *args, **kwargs: None

    # Max static block nesting within a function
    CO_MAXBLOCKS = 20

    # Maximum number of locals we can index.
    MAX_LOCALS = 256

    # Should be set to True if Py_TRACE_REFS is true, which is the case if linking
    # against the debug Python libraries.  This could potentially be detected by
    # using sys.getsizeof on a stack frame object.
    HEAD_EXTRA = False


    def get_frame_fields():
        fields = [
            ('_base_', PyObjectHeadWrapperVar),
            ('f_back', ctypes.c_void_p),  # _frame * -- previous frame
        ]

        if is_stackless:
            fields.extend([
                # Warning - STACKLESS only (f_code when STACKLESS is false)
                ('f_execute', ctypes.c_void_p),  # PyFrame_ExecFunc * - Stackless only, PyCodeObject *f_code otherwise
            ])
        else:
            fields.extend([
                # Python only
                ('f_code', ctypes.c_void_p),  # PyCodeObject * -- code segment
            ])

        fields.extend([
            ('f_builtins', ctypes.py_object),  # PyObject * -- builtin symbol table (PyDictObject)
            ('f_globals', ctypes.py_object),  # PyObject * -- global symbol table (PyDictObject)
            ('f_locals', ctypes.py_object),  # PyObject * -- local symbol table (any mapping)
            ('f_valuestack', ctypes.POINTER(ctypes.c_void_p)),  # PyObject ** -- points after the last local

             # Frame creation sets to f_valuestack.
             # Frame evaluation usually NULLs it, but a frame that yields sets it
             # to the current stack top
            ('f_stacktop', ctypes.POINTER(ctypes.c_void_p)),  # PyObject ** -- Next free slot in f_valuestack.

            ('f_trace', ctypes.c_void_p),  # PyObject * -- Trace function

            # In a generator, we need to be able to swap between the exception
            # state inside the generator and the exception state of the calling
            # frame (which shouldn't be impacted when the generator "yields"
            # from an except handler).
            # These three fields exist exactly for that, and are unused for
            # non-generator frames. See the SAVE_EXC_STATE and SWAP_EXC_STATE
            # macros in ceval.c for details of their use.
            ('f_exc_type', ctypes.c_void_p),  # PyObject *
            ('f_exc_value', ctypes.c_void_p),  # PyObject *
            ('f_exc_traceback', ctypes.c_void_p),  # PyObject *

            ('f_tstate', ctypes.c_void_p),  # PyThreadState *
            ('f_lasti', ctypes.c_int),  # int -- Last instruction if called

            # Call PyFrame_GetLineNumber() instead of reading this field
            # directly.  As of 2.3 f_lineno is only valid when tracing is
            # active (i.e. when f_trace is set).  At other times we use
            # PyCode_Addr2Line to calculate the line from the current
            # bytecode index.
            ('f_lineno', ctypes.c_int),  # int -- Current line number, but see above
            ('f_iblock', ctypes.c_int),  # int -- index in f_blockstack
            ('f_blockstack', PyTryBlockWrapper * CO_MAXBLOCKS),  # PyTryBlock[CO_MAXBLOCKS] -- for try and loop blocks
        ])

        if is_stackless:
            fields.extend([
                # Warning - STACKLESS only
                ('f_code', ctypes.c_void_p),  # PyCodeObject * -- code segment - Stackless only!
            ])

        fields.extend([
            # Technically this is variable length, but to eliminate the need
            # to create multiple frame wrappers we'll set it to a constant.
            ('f_localsplus', ctypes.py_object * MAX_LOCALS),  # PyObject *[N] -- locals+stack, dynamically sized
        ])

        return fields



    class PyTryBlockWrapper(ctypes.Structure):
        _fields_ = [
            ('b_type', ctypes.c_int),  # int -- what kind of block this is
            ('b_handler', ctypes.c_int),  # int -- where to jump to find handler
            ('b_level', ctypes.c_int),  # int -- value stack level to pop to
        ]


    class PyObjectHeadWrapper(ctypes.Structure):
        # PyObject_HEAD
        # This is a macro which expands to the declarations of the fields of the PyObject type;
        # it is used when declaring new types which represent objects without a varying length.
        # The specific fields it expands to depend on the definition of Py_TRACE_REFS.
        # By default, that macro is not defined, and PyObject_HEAD expands to:
        #
        # Py_ssize_t ob_refcnt;
        # PyTypeObject *ob_type;
        # When Py_TRACE_REFS is defined, it expands to:
        #
        # PyObject *_ob_next, *_ob_prev;
        # Py_ssize_t ob_refcnt;
        # PyTypeObject *ob_type;
        #
        if HEAD_EXTRA:
            _fields_ = [
                ('_ob_next', ctypes.c_void_p),  # PyObject *
                ('_ob_prev', ctypes.c_void_p),  # PyObject *
                ('ob_refcnt', ctypes.c_ssize_t),  # Py_ssize_t
                ('ob_type', ctypes.c_void_p),  # _typeobject *
            ]
        else:
            _fields_ = [
                ('ob_refcnt', ctypes.c_ssize_t),  # Py_ssize_t
                ('ob_type', ctypes.c_void_p),  # _typeobject *
            ]



    class PyObjectHeadWrapperVar(ctypes.Structure):
        # PyObject_VAR_HEAD
        # This is a macro which expands to the declarations of the fields of the PyVarObject type;
        # it is used when declaring new types which represent objects with a
        # length that varies from instance to instance. This macro always expands
        # to:
        #
        # PyObject_HEAD
        # Py_ssize_t ob_size;
        _anonymous_ = ['_base_']
        _fields_ = [
            ('_base_', PyObjectHeadWrapper),
            ('ob_size', ctypes.c_ssize_t),  # Py_ssize_t
        ]


    # Currently unused (just for information purposes for now -- python 2.7).
    class PyCodeObjectWrapper(ctypes.Structure):

        _anonymous_ = ['_base_']
        _fields_ = [
            ('_base_', PyObjectHeadWrapper),
        ]


        _fields_.extend([
            ('co_argcount', ctypes.c_int),  # int co_argcount;        /* #arguments, except *args */
            ('co_nlocals', ctypes.c_int),  # int co_nlocals;        /* #local variables */
            ('co_stacksize', ctypes.c_int),  # int co_stacksize;        /* #entries needed for evaluation stack */
            ('co_flags', ctypes.c_int),  # int co_flags;        /* CO_..., see below */
            ('co_code', ctypes.c_void_p),  # PyObject *co_code;        /* instruction opcodes */
            ('co_consts', ctypes.c_void_p),  # PyObject *co_consts;    /* list (constants used) */
            ('co_names', ctypes.c_void_p),  # PyObject *co_names;        /* list of strings (names used) */
            ('co_varnames', ctypes.c_void_p),  # PyObject *co_varnames;    /* tuple of strings (local variable names) */
            ('co_freevars', ctypes.c_void_p),  # PyObject *co_freevars;    /* tuple of strings (free variable names) */
            ('co_cellvars', ctypes.c_void_p),  # PyObject *co_cellvars;      /* tuple of strings (cell variable names) */

            # /* The rest doesn't count for hash/cmp */
            ('co_filename', ctypes.c_void_p),  # PyObject *co_filename;    /* string (where it was loaded from) */
            ('co_name', ctypes.c_void_p),  # PyObject *co_name;        /* string (name, for reference) */
            ('co_firstlineno', ctypes.c_int),  # int co_firstlineno;        /* first source line number */
            ('co_lnotab', ctypes.c_void_p),  # PyObject *co_lnotab;    /* string (encoding addr<->lineno mapping) See Objects/lnotab_notes.txt for details. */
            ('co_zombieframe', ctypes.c_void_p),  # void *co_zombieframe;     /* for optimization only (see frameobject.c) */
            ('co_weakreflist', ctypes.c_void_p),  # PyObject *co_weakreflist;   /* to support weakrefs to code objects */

        ])


    class FrameWrapper(ctypes.Structure):
        _anonymous_ = ['_base_']
        _fields_ = get_frame_fields()


    def save_locals(locals_dict, frame):
        """
        Copy values from locals_dict into the fast stack slots in the given frame.

        void
        PyFrame_LocalsToFast(PyFrameObject *f, int clear)
        {
            /* Merge f->f_locals into fast locals */
            PyObject *locals, *map;
            PyObject **fast;
            PyObject *error_type, *error_value, *error_traceback;
            PyCodeObject *co;
            Py_ssize_t j;
            Py_ssize_t ncells, nfreevars;
            if (f == NULL)
                return;

            locals = f->f_locals;
            co = f->f_code;
            map = co->co_varnames;
            if (locals == NULL)
                return;

            if (!PyTuple_Check(map))
                return;

            PyErr_Fetch(&error_type, &error_value, &error_traceback);
            fast = f->f_localsplus;
            j = PyTuple_GET_SIZE(map);

            if (j > co->co_nlocals)
                j = co->co_nlocals;
            if (co->co_nlocals)
                dict_to_map(co->co_varnames, j, locals, fast, 0, clear);

            ncells = PyTuple_GET_SIZE(co->co_cellvars);
            nfreevars = PyTuple_GET_SIZE(co->co_freevars);

            if (ncells || nfreevars) {
                dict_to_map(co->co_cellvars, ncells,
                            locals, fast + co->co_nlocals, 1, clear);

                /* Same test as in PyFrame_FastToLocals() above. */
                if (co->co_flags & CO_OPTIMIZED) {
                    dict_to_map(co->co_freevars, nfreevars,
                        locals, fast + co->co_nlocals + ncells, 1,
                        clear);
                }
            }
            PyErr_Restore(error_type, error_value, error_traceback);
        }

        """
        co = frame.f_code
        frame_pointer = ctypes.c_void_p(id(frame))
        frame_wrapper = ctypes.cast(frame_pointer, ctypes.POINTER(FrameWrapper))

        for i, name in enumerate(co.co_varnames):
            if name in locals_dict:
                frame_wrapper[0].f_localsplus[i] = locals_dict[name]

    return save_locals


if is_cpython and version in ('2.7',):
    #This is only valid for CPython!
    save_locals = create_save_locals()

