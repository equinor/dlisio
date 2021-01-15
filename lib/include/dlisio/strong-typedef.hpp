#ifndef DLISIO_EXT_STRONG_TYPEDEF
#define DLISIO_EXT_STRONG_TYPEDEF

#include <type_traits>
#include <utility>

namespace dlisio {
namespace detail {

using std::swap;

template< typename Tag, typename T >
class strong_typedef {
public:
    using value_type = T;

    constexpr static bool nothrow_copy_constructible =
        std::is_nothrow_copy_constructible< value_type >::value;

    constexpr static bool nothrow_move_constructible =
        std::is_nothrow_move_constructible< value_type >::value;

    constexpr static bool nothrow_swappable =
        noexcept (swap( std::declval< T& >(), std::declval< T& >() ));

    constexpr static bool nothrow_eq =
        noexcept (std::declval< const T& >() == std::declval< const T& >());

    constexpr static bool nothrow_ne =
        noexcept (std::declval< const T& >() != std::declval< const T& >());

    constexpr static bool nothrow_lt =
        noexcept (std::declval< const T& >() < std::declval< const T& >());

    constexpr static bool nothrow_le =
        noexcept (std::declval< const T& >() <= std::declval< const T& >());

    constexpr static bool nothrow_gt =
        noexcept (std::declval< const T& >() < std::declval< const T& >());

    constexpr static bool nothrow_ge =
        noexcept (std::declval< const T& >() >= std::declval< const T& >());

    strong_typedef() = default;
    strong_typedef( const strong_typedef& ) = default;
    strong_typedef( strong_typedef&& )      = default;

    strong_typedef& operator = ( const strong_typedef& ) = default;
    strong_typedef& operator = ( strong_typedef&& )      = default;

    explicit strong_typedef( const T& x )
        noexcept(strong_typedef::nothrow_copy_constructible);

    explicit strong_typedef( T&& x )
        noexcept(strong_typedef::nothrow_move_constructible);

    explicit operator T&() noexcept (true);
    explicit operator const T&() const noexcept (true);

    bool operator == ( const strong_typedef& ) const noexcept (nothrow_eq);
    bool operator != ( const strong_typedef& ) const noexcept (nothrow_ne);
    bool operator <  ( const strong_typedef& ) const noexcept (nothrow_lt);
    bool operator <= ( const strong_typedef& ) const noexcept (nothrow_le);
    bool operator >  ( const strong_typedef& ) const noexcept (nothrow_gt);
    bool operator >= ( const strong_typedef& ) const noexcept (nothrow_ge);

private:
    T value;
    /*
     * Inherit the noexcept property of the underlying swap operation. Usually
     * swap is noexcept (although for strings it's only conditionally after
     * C++17, and not really at all before)
     */
    friend void swap( strong_typedef& a, strong_typedef& b )
        noexcept (nothrow_swappable) {
        swap( static_cast< T& >( a ), static_cast< T& >( b ) );
    }
};

template< typename Tag, typename T >
strong_typedef< Tag, T >::strong_typedef( const T& x )
        noexcept(strong_typedef::nothrow_copy_constructible)
    : value( x ) {}

template< typename Tag, typename T >
strong_typedef< Tag, T >::strong_typedef( T&& x )
        noexcept(strong_typedef::nothrow_move_constructible)
    : value( std::move( x ) ) {}

template< typename Tag, typename T >
strong_typedef< Tag, T >::operator T&() noexcept(true) {
    return this->value;
}

template< typename Tag, typename T >
strong_typedef< Tag, T >::operator const T&() const noexcept(true) {
    return this->value;
}

template< typename Tag, typename T >
bool strong_typedef< Tag, T >::operator ==
    ( const strong_typedef& rhs ) const
    noexcept (nothrow_eq)
{
    return this->value == rhs.value;
}

template< typename Tag, typename T >
bool strong_typedef< Tag, T >::operator !=
    ( const strong_typedef& rhs ) const
    noexcept (nothrow_ne)
{
    return this->value != rhs.value;
}

template< typename Tag, typename T >
bool strong_typedef< Tag, T >::operator <
    ( const strong_typedef& rhs ) const
    noexcept (nothrow_lt)
{
    return this->value < rhs.value;
}

template< typename Tag, typename T >
bool strong_typedef< Tag, T >::operator <=
    ( const strong_typedef& rhs ) const
    noexcept (nothrow_le)
{
    return this->value <= rhs.value;
}

template< typename Tag, typename T >
bool strong_typedef< Tag, T >::operator >
    ( const strong_typedef& rhs ) const
noexcept (nothrow_gt)
{
    return this->value > rhs.value;
}

template< typename Tag, typename T >
bool strong_typedef< Tag, T >::operator >=
    ( const strong_typedef& rhs ) const
    noexcept (nothrow_ge)
{
    return this->value >= rhs.value;
}

template< typename Tag, typename T >
void swap( strong_typedef< Tag, T >& a,
           strong_typedef< Tag, T >& b )
    noexcept (strong_typedef< Tag, T >::nothrow_swappable)
{
}

} // namespace detail

} // namespace dlis

#endif // DLISIO_EXT_STRONG_TYPEDEF
