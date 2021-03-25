#ifndef DLISIO_LIS_TYPES_H
#define DLISIO_LIS_TYPES_H

#include <stdint.h>

#include "../common.h"

#ifdef __cplusplus
extern "C" {
#endif

/** Basic LIS types
 *
 * lis reprc  lisio name    description
 * -------------------------------------------------------------
 * 56           i8          8-bit  2's compliment integer
 * 79           i16         16-bit 2's compliment integer
 * 73           i32         32-bit 2's compliment integer
 * 49           f16         16-bit floating point
 * 50           f32low      32-bit low resolution floating point
 * 68           f32         32-bit floating point
 * 70           f32fixed    32-bit fixed point
 * 65           ascii       Alphanumeric
 * 66           bytes       Byte Format
 * 77           mask        variable-length bitmask
 * -------------------------------------------------------------
 *
 */

/* (reprc 56) 8-bit signed integer */
DLISIO_API
const char* lis_i8(const char*, std::int8_t*);

/* (reprc 79) 16-bit signed integer */
DLISIO_API
const char* lis_i16(const char*, std::int16_t*);

/* (reprc 73) 32-bit signed integer */
DLISIO_API
const char* lis_i32(const char*, std::int32_t*);

/* (reprc 49) 16-bit floating point */
DLISIO_API
const char* lis_f16(const char*, float*);

/* (reprc 68) 32-bit floating point
 *
 * Note: small precision loss may apply. It's not expected to be a problem
 * as loss might happen around precisions 2^(-127) and 2^(-128), which are
 * unlikely to happen in reality.
 */
DLISIO_API
const char* lis_f32(const char*, float*);

/* (reprc 50) 32-bit low resolution floating point
 *
 * Caution: value is represented as float, though much larger values can be
 * stored according to specification due to 15-bit exponent. As per IEEE 754,
 * exponent is 8-bit (less than LIS) and fraction is 23-bit (more precise than
 * LIS). It means that values in approximately next ranges are lost:
 *   [2^128, 2^32768)
 *   (-2^32768, -2^128]
 *   with precision around (2^(-32768), 2^(-128))
 *
 * It is assumed that stored values are reasonable and floats should be enough
 * in all real cases.
 */
DLISIO_API
const char* lis_f32low(const char*, float*);

/* (reprc 70) 32-bit fixed point - 2's complement with binary point in the
 * middle
 *
 * Note: some numbers can't be represented correctly by IEEE 754 floats.
 * Problem happens for values with high precision which do not fit into floats.
 * There is no strictly defined precision loss range here, but it might already
 * appear for numbers outside of [-256, 256] range.
 *
 * Using double type instead would have solved the issue.
 * This type, however, is not expected to be used frequently as it's too
 * different from the standard ones. Hence precision loss is considered
 * acceptable.
 */
DLISIO_API
const char* lis_f32fix(const char*, float*);

/* (reprc 65) String (Alphanumeric)  - variable length string
 *
 * The alphanumeric type does not contain its own length. Rather, the length
 * is either implied by the standard or explicitly stated by some other type in
 * the file.
 *
 * The standard does not explicitly define a max length for alphanumerics. Thus
 * the theoretical max length is the max value of the biggest int in the
 * standard, which is 2,147,483,647 (reprc 73).
 *
 * In practice it seems like the length typically is represented by reprc 66
 * (byte), which essentially is a uint8_t, limiting the max length to a more
 * reasonable 256 characters.
 */
DLISIO_API
const char* lis_string(const char*, const std::int32_t, char*);

/* (reprc 66) Byte */
DLISIO_API
const char* lis_byte(const char*, std::uint8_t*);

/* (reprc 77) Mask - bitmask */
DLISIO_API
const char* lis_mask(const char*, const std::int32_t, char*);

#define LIS_I8     56 // (reprc 56) 8-bit signed integer
#define LIS_I16    79 // (reprc 79) 16-bit signed integer
#define LIS_I32    73 // (reprc 73) 32-bit signed integer
#define LIS_F16    49 // (reprc 49) 16-bit floating point
#define LIS_F32    68 // (reprc 68) 32-bit floating point
#define LIS_F32LOW 50 // (reprc 50) 32-bit low resolution floating point
#define LIS_F32FIX 70 // (reprc 70) 32-bit fixed point
#define LIS_STRING 65 // (reprc 65) Alphanumeric  - variable length string
#define LIS_BYTE   66 // (reprc 66) Byte
#define LIS_MASK   77 // (reprc 77) Mask - bitmask

#define LIS_VARIABLE_LENGTH 0

// values below represent size on disk (in bytes)
#define LIS_SIZEOF_I8       1
#define LIS_SIZEOF_I16      2
#define LIS_SIZEOF_I32      4
#define LIS_SIZEOF_F16      2
#define LIS_SIZEOF_F32      4
#define LIS_SIZEOF_F32LOW   4
#define LIS_SIZEOF_F32FIX   4
#define LIS_SIZEOF_STRING   LIS_VARIABLE_LENGTH
#define LIS_SIZEOF_BYTE     1
#define LIS_SIZEOF_MASK     LIS_VARIABLE_LENGTH
#define LIS_SIZEOF_SUPPRESS LIS_VARIABLE_LENGTH

// Format string representation
// Defined by the ASCII codes in Appendix B, lis79
#define LIS_FMT_EOL      '\0'
#define LIS_FMT_I8       's' // (reprc 56) 8-bit signed integer
#define LIS_FMT_I16      'i' // (reprc 79) 16-bit signed integer
#define LIS_FMT_I32      'l' // (reprc 73) 32-bit signed integer
#define LIS_FMT_F16      'e' // (reprc 49) 16-bit floating point
#define LIS_FMT_F32      'f' // (reprc 68) 32-bit floating point
#define LIS_FMT_F32LOW   'r' // (reprc 50) 32-bit low resolution floating point
#define LIS_FMT_F32FIX   'p' // (reprc 70) 32-bit fixed point
#define LIS_FMT_STRING   'a' // (reprc 65) Alphanumeric - variable length string
#define LIS_FMT_BYTE     'b' // (reprc 66) Byte
#define LIS_FMT_MASK     'm' // (reprc 77) Mask - bitmask
#define LIS_FMT_SUPPRESS 'S' // Suppressed output

/** Byte size of a LIS type
 *
 * get the size (in bytes) of a particular data type. Expects a LIS_F32 or
 * similar type code.
 *
 * Returns a negative value passed an invalid type code.
 */
DLISIO_API
int lis_sizeof_type(int);

#ifdef __cplusplus
}
#endif

#endif // DLISIO_LIS_TYPES_H

