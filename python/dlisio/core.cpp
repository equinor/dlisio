#if defined(_DEBUG) && defined(_MSC_VER)
#  define _CRT_NOFORCE_MAINFEST 1
#  undef _DEBUG
#  include <Python.h>
#  include <bytesobject.h>
#  define _DEBUG 1
#else
#  include <Python.h>
#  include <bytesobject.h>
#endif

PyMethodDef module_functions[] = {
    { NULL },
};

/* module initialization */
#if PY_MAJOR_VERSION >= 3
static struct PyModuleDef dlisio_module = {
        PyModuleDef_HEAD_INIT,
        "core",   /* name of module */
        NULL,     /* module documentation, may be NULL */
        -1,      /* size of per-interpreter state of the module, or -1 if the module keeps state in global variables. */
        module_functions, 
};

PyMODINIT_FUNC PyInit_core( void ) {
    PyObject* m = PyModule_Create(&dlisio_module);
    if( !m ) return NULL;
    return m;
}
#else
PyMODINIT_FUNC init_core( void ) {
    Py_InitModule("core", module_functions);
}
#endif
