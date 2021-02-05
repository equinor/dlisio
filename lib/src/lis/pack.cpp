#include <cstdint>
#include <cstring>
#include <ciso646>
#include <cassert>
#include <iterator>
#include <type_traits>

#include <dlisio/lis/pack.h>
#include <dlisio/lis/types.h>
#include <dlisio/dlis/dlisio.h> // DLIS_OK etc for pack, should not be here

namespace {

/*
 * The lis_packf function uses a dispatch table for interpreting and expanding
 * raw bytes into native C++ data types. There are 10 primary data types
 * specified by LIS79 (Appendix B).
 *
 * Instead of populating the dispatch table by hand, generate it with the
 * interpret function. The interpret() function essentially generates this code
 * for all RP66 data types:
 *
 * float f;
 * src = lis_f32( src, &f );
 * memcpy( dst, &f, 4 );
 * dst += 4;
 */

struct cursor {
    const char* src;
    char* dst;
    int written;

    void advance(int nbytes) noexcept (true) {
        if (this->dst) this->dst += nbytes;
        this->written += nbytes;
    }

    cursor& invalidate() noexcept (true) {
        this->src = nullptr;
        return *this;
    }

    bool invalid() const noexcept (true) {
        return !this->src;
    }
};

/*
 * Forward-declare the with-string overload so that all packs know to consider
 * it when recursing pack(dst, ptrs, ...)
 */
template < typename... Ts >
int pack(char* dst,
         const std::int32_t* len,
         const char* str,
         const Ts* ... ptrs) noexcept (true);

int pack(char*) noexcept (true) {
    return 0;
}

template < typename T, typename... Ts >
int pack(char* dst, const T* ptr, const Ts* ... ptrs) noexcept (true) {
    constexpr int size = sizeof(T);
    if (dst) {
        std::memcpy(dst, ptr, size);
        dst += size;
    }
    return size + pack(dst, ptrs ...);
}

template < typename... Ts >
int pack(char* dst,
         const std::int32_t* len,
         const char* str,
         const Ts* ... ptrs) noexcept (true)
{
    const auto size = sizeof(*len) + *len;
    if (dst) {
        std::memcpy(dst, len, sizeof(*len));
        std::memcpy(dst + sizeof(*len), str, *len);
        dst += size;
    }
    return size + pack(dst, ptrs ...);
}

template < typename T >
T* address( T& t ) noexcept (true) {
    return std::addressof( t );
}

template < typename F, typename... Args >
cursor interpret( cursor cur, F func, Args ... args ) noexcept (true) {
    cur.src = func( cur.src, address( args ) ... );
    const auto written = pack(cur.dst, address( args ) ...);
    cur.advance(written);
    return cur;
}

template < typename... Args >
cursor interpret( cursor cur, const char* f(const char*, Args* ...) )
noexcept (true)
{
    /*
     * the inner-interpret takes pointers to initialised variables which serve
     * as buffers for func to write into, and pack to read from. It's
     * essentially creating a tuple< Args ... > by abusing function parameters
     * to statically create function calls with enough space on the stack, and
     * dispatch to the right function reference for the actual byte-to-variable
     * work
     */
    return interpret( cur, f, Args() ... );
}

cursor packf(const char* fmt, const char* src, char* dst) noexcept (true) {
    /*
     * The public lis_packf function assumes both src and dst are valid
     * pointers, but the worker packf function has no such restriction. In
     * addition, packflen is *essentially* packf, but it outputs the
     * byte-count, instead of doing writes.
     *
     * This function implements both these operations
     */
    cursor cur = {src, dst, 0};

    while (true) {
        switch (*fmt++) {
            case LIS_FMT_EOL:
                return cur;

            case LIS_FMT_I8     : cur = interpret(cur, lis_i8);     break;
            case LIS_FMT_I16    : cur = interpret(cur, lis_i16);    break;
            case LIS_FMT_I32    : cur = interpret(cur, lis_i32);    break;
            case LIS_FMT_F16    : cur = interpret(cur, lis_f16);    break;
            case LIS_FMT_F32    : cur = interpret(cur, lis_f32);    break;
            case LIS_FMT_F32LOW : cur = interpret(cur, lis_f32low); break;
            case LIS_FMT_F32FIX : cur = interpret(cur, lis_f32fix); break;
            case LIS_FMT_BYTE   : cur = interpret(cur, lis_byte);   break;
            /* Because lis_string and lis_mask do not encode their own length
             * we currently assume that these can't be used as types in IFLRs
             */
            default:
                return cur.invalidate();
        }
    }
}

} // namespace

int lis_packf( const char* fmt, const void* src, void* dst ) {
    assert(src);
    assert(dst);

    auto csrc = static_cast< const char* >(src);
    auto cdst = static_cast< char* >(dst);
    const auto cur = packf(fmt, csrc, cdst);

    if (cur.invalid())
        return DLIS_UNEXPECTED_VALUE;

    return DLIS_OK;
}

int lis_packflen(const char* fmt, const void* src, int* nread, int* nwrite) {
    auto csrc = static_cast< const char* >(src);
    const auto cur = packf(fmt, csrc, nullptr);

    if (cur.invalid())
        return DLIS_UNEXPECTED_VALUE;

    if (nread)  *nread  = std::distance(csrc, cur.src);
    if (nwrite) *nwrite = cur.written;
    return DLIS_OK;
}
