#ifndef DLISIO_EXCEPTION_HPP
#define DLISIO_EXCEPTION_HPP

namespace dlisio {

struct eof_error : public std::runtime_error {
    using std::runtime_error::runtime_error;
};

struct io_error : public std::runtime_error {
    using std::runtime_error::runtime_error;
    explicit io_error( int no ) : runtime_error( std::strerror( no ) ) {}
};

struct not_implemented : public std::logic_error {
    explicit not_implemented( const std::string& msg ) :
        logic_error( "Not implemented yet: " + msg )
    {}
};

struct not_found : public std::runtime_error {
    explicit not_found( const std::string& msg )
        : runtime_error( msg )
    {}
};

} // namespace dlisio

#endif // DLISIO_EXCEPTION_HPP
