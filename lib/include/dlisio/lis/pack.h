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
 * fmt is a sscanf-inspired format string of conversion specifiers (LIS_FMT_*).
 * The size of each type depends on the most natural corresponding C type, e.g.
 * I8 is int8_t, and F32 is float. The arguments to a lis_type() function in
 * lisio/types.h is the type being used as a target type for a conversion
 * specifier.
 *
 * String types are always written as int32_t + len bytes, without a zero
 * terminator.
 *
 * Example:
 *
 * Extracting a frame with three channels:
 * C1 -> 1x1 i16     (int32_t)
 * C2 -> 2x1 f32     (float)
 * C3 -> 1x1 byte    (uint8_t)
 *
 * int32_t C1;
 * float   C2[2];
 * uint8_t C3;
 *
 * unsigned char bytes[2 + 2*4 + 4];
 * err = lis_packf("IDDB", src, bytes);
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

#ifdef __cplusplus
}
#endif

#endif // DLISIO_LIS_PACKF_H
