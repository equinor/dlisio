#ifndef DLISIO_PYTHON_EXCEPTION_HPP
#define DLISIO_PYTHON_EXCEPTION_HPP

namespace {

void runtime_warning( const char* msg ) {
    int err = PyErr_WarnEx( PyExc_RuntimeWarning, msg, 1 );
    if( err ) throw py::error_already_set();
}

void user_warning( const char* msg ) {
    int err = PyErr_WarnEx( PyExc_UserWarning, msg, 1 );
    if( err ) throw py::error_already_set();
}

void user_warning( const std::string& msg ) {
    user_warning( msg.c_str() );
}

}

#endif // DLISIO_PYTHON_EXCEPTION_HPP
