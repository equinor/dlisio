#ifndef DLISIO_PYTHON_EXCEPTION_HPP
#define DLISIO_PYTHON_EXCEPTION_HPP

namespace {

/*
 * for some reason, pybind does not defined IOError, so make a quick
 * regular-looking exception like that and register its translation
 */
struct io_error : public std::runtime_error {
    using std::runtime_error::runtime_error;
    explicit io_error( int no ) : runtime_error( std::strerror( no ) ) {}
};

struct eof_error : public std::runtime_error {
    using std::runtime_error::runtime_error;
};

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
