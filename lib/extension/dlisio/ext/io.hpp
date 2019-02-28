#ifndef DLISIO_PYTHON_IO_HPP
#define DLISIO_PYTHON_IO_HPP

#include <array>
#include <fstream>
#include <string>
#include <tuple>
#include <vector>

#include <mio/mio.hpp>

#include <dlisio/ext/types.hpp>

namespace dl {

struct record {
    bool isexplicit()  const noexcept (true);
    bool isencrypted() const noexcept (true);

    int type;
    std::uint8_t attributes;
    bool consistent;
    std::vector< char > data;
};

class stream {
public:
    explicit stream( const std::string& path ) noexcept (false);

    record  at( int i ) noexcept (false);
    record& at( int i, record& ) noexcept (false);

    void reindex( std::vector< long long >,
                  std::vector< int > )
        noexcept (false);

    void close();

    void read( char* dst, long long offset, int n );

private:
    std::fstream fs;
    std::vector< long long > tells;
    std::vector< int > residuals;

    /*
     * if this is true, there are no gaps inbetween tells, i.e. the file
     * pointer should be at the next tell after reading. When stream is indexed
     * with custom offsets, e.g. to account for broken files, this must be
     * disabled and the safety check is gone
     */
    bool contiguous = true;
};


struct stream_offsets {
    std::vector< long long > tells;
    std::vector< int > residuals;
    std::vector< int > explicits;

    void resize( std::size_t ) noexcept (false);
};

void map_source( mio::mmap_source&, const std::string& ) noexcept (false);

long long findsul( mio::mmap_source& file ) noexcept (false);
long long findvrl( mio::mmap_source& path, long long from ) noexcept (false);

stream_offsets findoffsets( mio::mmap_source& path,
                            long long from )
noexcept (false);

}

#endif // DLISIO_PYTHON_IO_HPP
