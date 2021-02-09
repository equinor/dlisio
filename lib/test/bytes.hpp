#include <cstring>
#include <sstream>
#include <iomanip>
#include <catch2/catch.hpp>

/*
 * Custom type for byte arrays, for nicely printing mismatch between expected
 * and actual parameters to comparison of byte arrays.
 *
 * This type exists mostly for Catch's stringmaker to have something to hook
 * into, as it relies on the type system to pick the correct specialisation.
 * Using std::array is pretty clumsy, and (unsigned) char* already means
 * "print-as-string".
 */
template< std::size_t N, typename T = char >
struct bytes {
    using value_type = T[N];

    bytes() = default;
    bytes( const value_type& xs ) {
        using std::begin;
        using std::end;
        std::copy( begin( xs ), end( xs ), begin( this->data ) );
    }

    bytes( std::initializer_list< std::size_t > xs ) {
        using std::begin;
        using std::end;
        std::copy( begin( xs ), end( xs ), begin( this->data ) );
    }

    operator value_type& ()             { return this->data; }
    operator const value_type& () const { return this->data; }

    value_type data;
};

namespace {

template< typename T, std::size_t N >
class BytesEqualsMatcher : public Catch::MatcherBase< bytes< N > > {
public:
    explicit BytesEqualsMatcher( T x ) : lhs( x ) {}

    virtual bool match( const bytes< N >& rhs ) const override {
        static_assert( sizeof( T ) == N, "sizeof(T) must be equal to N" );
        return std::memcmp( &this->lhs, rhs, sizeof( T ) ) == 0;
    }

    virtual std::string describe() const override {
        bytes< N > lhsb;
        std::memcpy( lhsb, &this->lhs, N );

        using str = Catch::StringMaker< bytes< N > >;
        return "== " + str::convert( lhsb );
    }

private:
    T lhs;
};

template< typename T >
BytesEqualsMatcher< T, sizeof( T ) > BytesEquals( T lhs ) {
    return BytesEqualsMatcher< T, sizeof( T ) >{ lhs };
}

}

namespace Catch {

/*
 * print bytes as a hex sequence
 */
template< std::size_t N >
struct StringMaker< bytes< N > > {
    static std::string convert( const bytes< N >& xs ) {
        std::stringstream ss;
        ss << std::hex;

        /*
         * Convert every byte to unsigned char (even though the byte array
         * stores as unspecified signed) to preserve representation as a byte,
         * so it doesn't change once widened to an int. Once an int, the
         * std::hex manipulator picks it up and writes it as a hex value
         */
        for( unsigned char x : xs.data ) {
            ss << std::setfill( '0' )
               << std::setw( 2 )
               << int( x ) << ' '
               ;
        }

        auto s = ss.str();
        /* remove trailing space */
        s.pop_back();
        return s;
    }
};

}
