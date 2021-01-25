#ifndef DLISIO_LIS_PACKF_H
#define DLISIO_LIS_PACKF_H

#include "../common.h"

#ifdef __cplusplus
extern "C" {
#endif

/*
 * Parse and pack arbitrary data
 *
 * The lis_packf (inspired by sscanf) reads arbitrary bytes in RP66 format,
 * and pack them into the dst area as native C data. No padding bytes are
 * inserted, which means the data can be read from this array by computing the
 * correct offset and memcpy'd into a typed variable.
 *
 * fmt is a sscanf-inspired format string of conversion specifiers
 * (LIS_FMT_*). The size of each type depends on the most natural corresponding
 * C type, e.g. SSHORT is int8_t, and UNORM is uint16_t. The arguments to a
 * lis_type() function in lisio/primitives.h is the type being used as a target
 * type for a conversion specifier.
 *
 * String types are always written as int32_t + len bytes, without a zero
 * terminator.
 *
 * Example:
 *
 * Extracting a frame with three channels:
 * C1 -> 1x1 unorm   (i16)
 * C2 -> 2x1 fsingle (f32)
 * C3 -> 1x1 uvari   (yields i32)
 *
 * int16_t C1;
 * float C2[2];
 * int32_t C3;
 *
 * unsigned char bytes[2 + 2*4 + 4];
 * err = lis_packf("Uffi", src, bytes);
 * if (err) exit(1);
 *
 * memcpy(&C1, bytes,      sizeof(C1));
 * memcpy(C2,  bytes + 2,  sizeof(C2));
 * memcpy(&c3, bytes + 10, sizeof(C3));
 */
DLISIO_API
int lis_packf( const char* fmt, const void* src, void* dst );

/*
 * lis_packflen is to lis_packf as strlen is to strings
 *
 * lis_packflen counts the number of bytes read from src, and what would be
 * written to dst, by lis_packf with the same fmt and src.
 *
 * This is particularly useful when wanting to only pack *parts* of a record,
 * e.g. when certain columns are filtered out.
 */
DLISIO_API
int lis_packflen(const char* fmt, const void* src, int* nread, int* nwrite);

/*
 * Check if a format string for packing is var-size or fixed-size
 *
 * This function is intended for checking if format strings built from
 * inspecting records is fixed-sized or not, which in turn can guide if it's
 * possible to random-access onto variables. The output variables are booleans
 * - the src output is true if the format is variable-size on disk, and the dst
 * output is true if the format is variable-size *in memory*. This is
 * determined by the presence of UVARI and ORIGIN which are variable-sized on
 * disk, but fixed-size in memory.
 *
 * This functionality can be implemented by manually checking if the format
 * string contains any of "sSoOAQ", but is provided for convenience.
 *
 * Returns LIS_OK on success, and LIS_INVALID_ARGS if the format strings
 * contain any invalid format specifier. The output params are non-zero if
 * there are any variable-length values in the format specifier, and 0 if all
 * types are fixed-length. If the function fails, the output variable is
 * untouched.
 *
 * To compute the length of a fixed-size string, use lis_pack_size. src is the
 * size of the pack on disk, and dst the length of the packed string in memory,
 * i.e.  UVARI is 4 bytes, not inconsistent. For individual object sizes, refer
 * to the LIS_SIZEOF constants in lisio/primitives.h
 *
 * NOTE:
 * lis_pack_size considers the src variable-size when fmt has UVARI, but the
 * dst fixed-size. This will return LIS_OK, but set src to
 * LIS_VARIABLE_LENGTH (= 0).
 *
 * For both functions, both src and dst can be NULL, in which case no data will
 * be written.
 */
DLISIO_API
int lis_pack_size(const char* fmt, int* src, int* dst);

#ifdef __cplusplus
}
#endif

#endif // DLISIO_LIS_PACKF_H
