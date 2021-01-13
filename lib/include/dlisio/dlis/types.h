#ifndef DLISIO_TYPES_H
#define DLISIO_TYPES_H

#include <stdint.h>

#include "../common.h"

#ifdef __cplusplus
extern "C" {
#endif

/*
 * A family of primitive functions to parse the data types specified by RP66.
 * They all return a pointer to the first character NOT consumed by calling
 * this function.
 *
 * If the output argument is NULL it is not written, but distance is still
 * calculated. This is necessary for variable-length strings to ensure a large
 * enough buffer. Strings will NOT be null terminated
 */

DLISIO_API const char* dlis_sshort(const char*, int8_t*);
DLISIO_API const char* dlis_snorm( const char*, int16_t*);
DLISIO_API const char* dlis_slong( const char*, int32_t*);

DLISIO_API const char* dlis_ushort(const char*, uint8_t*);
DLISIO_API const char* dlis_unorm( const char*, uint16_t*);
DLISIO_API const char* dlis_ulong( const char*, uint32_t*);

DLISIO_API const char* dlis_fshort(const char*, float*);
DLISIO_API const char* dlis_fsingl(const char*, float*);
DLISIO_API const char* dlis_fdoubl(const char*, double*);

/* IBM and VAX floats */
DLISIO_API const char* dlis_isingl(const char*, float*);
DLISIO_API const char* dlis_vsingl(const char*, float*);

/* complex or validated floats */
DLISIO_API const char* dlis_fsing1(const char*, float* V, float* A);
DLISIO_API const char* dlis_fsing2(const char*, float* V, float* A, float* B);
DLISIO_API const char* dlis_csingl(const char*, float* R, float* I);

DLISIO_API const char* dlis_fdoub1(const char*, double* V, double* A);
DLISIO_API const char* dlis_fdoub2(const char*, double* V, double* A, double* B);
DLISIO_API const char* dlis_cdoubl(const char*, double* R, double* I);

DLISIO_API const char* dlis_uvari(const char*, int32_t* out);

DLISIO_API const char* dlis_ident(const char*, int32_t* len, char* out);
DLISIO_API const char* dlis_ascii(const char*, int32_t* len, char* out);

#define DLIS_TZ_LST 0 // local standard
#define DLIS_TZ_DST 1 // local daylight savings
#define DLIS_TZ_GMT 2 // greenwich mean time

#define DLIS_YEAR_ZERO 1900
DLISIO_API
int dlis_year( int );

DLISIO_API
const char* dlis_dtime(const char*, int* Y,
                                    int* TZ,
                                    int* M,
                                    int* D,
                                    int* H,
                                    int* MN,
                                    int* S,
                                    int* MS);

DLISIO_API
const char* dlis_origin( const char*, int32_t* out );

/* obname = { origin, ushort, ident } */
DLISIO_API
const char* dlis_obname( const char*, int32_t* origin,
                                      uint8_t* copy_number,
                                      int32_t* idlen,
                                      char* identifier );

/* objref = { ident, obname } */
DLISIO_API
const char* dlis_objref( const char*, int32_t* ident_len,
                                      char* ident,
                                      int32_t* origin,
                                      uint8_t* copy_number,
                                      int32_t* objname_len,
                                      char* identifier );

/* attref = { ident, obname, ident } */
DLISIO_API
const char* dlis_attref( const char*, int32_t* ident1_len,
                                      char* ident1,
                                      int32_t* origin,
                                      uint8_t* copy_number,
                                      int32_t* objname_len,
                                      char* identifier,
                                      int32_t* ident2_len,
                                      char* ident2 );

/* status is a boolean */
DLISIO_API const char* dlis_status(const char*, uint8_t*);
DLISIO_API const char* dlis_units(const char*, int32_t*, char*);

/*
 * A family of the reverse operation, i.e. transform a native data type to an
 * RP66 compatible one.
 *
 * They share the same name as the parsing functions, except for a trailing o.
 *
 * Unlike the input functions, they work on fixed-size unsigned numbers as
 * buffers, to make return-values more ergonomic
 */
DLISIO_API void* dlis_sshorto(void*, int8_t);
DLISIO_API void* dlis_snormo( void*, int16_t);
DLISIO_API void* dlis_slongo( void*, int32_t);

DLISIO_API void* dlis_ushorto(void*, uint8_t);
DLISIO_API void* dlis_unormo( void*, uint16_t);
DLISIO_API void* dlis_ulongo( void*, uint32_t);

DLISIO_API void* dlis_fsinglo(void*, float);
DLISIO_API void* dlis_fdoublo(void*, double);

/* IBM and VAX floats */
DLISIO_API void* dlis_isinglo(void*, float);
DLISIO_API void* dlis_vsinglo(void*, float);

/* complex or validated floats */
DLISIO_API void* dlis_fsing1o(void*, float, float);
DLISIO_API void* dlis_fsing2o(void*, float, float, float);
DLISIO_API void* dlis_csinglo(void*, float, float);

DLISIO_API void* dlis_fdoub1o(void*, double, double);
DLISIO_API void* dlis_fdoub2o(void*, double, double, double);
DLISIO_API void* dlis_cdoublo(void*, double, double);

DLISIO_API void* dlis_uvario( void*, int32_t, int width );

DLISIO_API void* dlis_idento(void*, uint8_t len, const char* in);
DLISIO_API void* dlis_asciio(void*, int32_t len, const char* in, std::uint8_t);

DLISIO_API void* dlis_origino(void*, int32_t);
DLISIO_API void* dlis_statuso(void*, uint8_t);

DLISIO_API
int dlis_yearo( int );
DLISIO_API
void* dlis_dtimeo( void*, int Y,
                          int TZ,
                          int M,
                          int D,
                          int H,
                          int MN,
                          int S,
                          int MS );

/* obname = { origin, ushort, ident } */
DLISIO_API
void* dlis_obnameo( void*, int32_t origin,
                           uint8_t copy_number,
                           uint8_t idlen,
                           const char* identifier );

/* objref = { ident, obname } */
DLISIO_API
void* dlis_objrefo( void*, uint8_t ident_len,
                           const char* ident,
                           int32_t origin,
                           uint8_t copy_number,
                           uint8_t objname_len,
                           const char* identifier );

/* attref = { ident, obname, ident } */
DLISIO_API
void* dlis_attrefo( void*, uint8_t ident1_len,
                           const char* ident1,
                           int32_t origin,
                           uint8_t copy_number,
                           uint8_t objname_len,
                           const char* identifier,
                           uint8_t ident2_len,
                           const char* ident2 );

DLISIO_API
void* dlis_unitso( void*, uint8_t len, const char* in );

/*
 * get the size (in bytes) of a particular data type. Expects a DLIS_UNORM or
 * similar type code.
 *
 * Returns a negative value passed an invalid type code.
 */
DLISIO_API int dlis_sizeof_type(int);

#define DLIS_FSHORT 1  // Low precision floating point
#define DLIS_FSINGL 2  // IEEE single precision floating point
#define DLIS_FSING1 3  // Validated single precision floating point
#define DLIS_FSING2 4  // Two-way validated single precision floating point
#define DLIS_ISINGL 5  // IBM single precision floating point
#define DLIS_VSINGL 6  // VAX single precision floating point
#define DLIS_FDOUBL 7  // IEEE double precision floating point
#define DLIS_FDOUB1 8  // Validated double precision floating point
#define DLIS_FDOUB2 9  // Two-way validated double precision floating point
#define DLIS_CSINGL 10 // Single precision complex
#define DLIS_CDOUBL 11 // Double precision complex
#define DLIS_SSHORT 12 // Short signed integer
#define DLIS_SNORM  13 // Normal signed integer
#define DLIS_SLONG  14 // Long signed integer
#define DLIS_USHORT 15 // Short unsigned integer
#define DLIS_UNORM  16 // Normal unsigned integer
#define DLIS_ULONG  17 // Long unsigned integer
#define DLIS_UVARI  18 // Variable-length unsigned integer
#define DLIS_IDENT  19 // Variable-length identifier
#define DLIS_ASCII  20 // Variable-length ASCII character string
#define DLIS_DTIME  21 // Date and time
#define DLIS_ORIGIN 22 // Origin reference
#define DLIS_OBNAME 23 // Object name
#define DLIS_OBJREF 24 // Object reference
#define DLIS_ATTREF 25 // Attribute reference
#define DLIS_STATUS 26 // Boolean status
#define DLIS_UNITS  27 // Units expression
#define DLIS_UNDEF  66 // Undefined value

#define DLIS_VARIABLE_LENGTH 0

// values below represent size on disk (in bytes)
#define DLIS_SIZEOF_FSHORT 2
#define DLIS_SIZEOF_FSINGL 4
#define DLIS_SIZEOF_FSING1 8
#define DLIS_SIZEOF_FSING2 12
#define DLIS_SIZEOF_ISINGL 4
#define DLIS_SIZEOF_VSINGL 4
#define DLIS_SIZEOF_FDOUBL 8
#define DLIS_SIZEOF_FDOUB1 16
#define DLIS_SIZEOF_FDOUB2 24
#define DLIS_SIZEOF_CSINGL 8
#define DLIS_SIZEOF_CDOUBL 16
#define DLIS_SIZEOF_SSHORT 1
#define DLIS_SIZEOF_SNORM  2
#define DLIS_SIZEOF_SLONG  4
#define DLIS_SIZEOF_USHORT 1
#define DLIS_SIZEOF_UNORM  2
#define DLIS_SIZEOF_ULONG  4
#define DLIS_SIZEOF_UVARI  DLIS_VARIABLE_LENGTH
#define DLIS_SIZEOF_IDENT  DLIS_VARIABLE_LENGTH
#define DLIS_SIZEOF_ASCII  DLIS_VARIABLE_LENGTH
#define DLIS_SIZEOF_DTIME  8
#define DLIS_SIZEOF_ORIGIN DLIS_VARIABLE_LENGTH
#define DLIS_SIZEOF_OBNAME DLIS_VARIABLE_LENGTH
#define DLIS_SIZEOF_OBJREF DLIS_VARIABLE_LENGTH
#define DLIS_SIZEOF_ATTREF DLIS_VARIABLE_LENGTH
#define DLIS_SIZEOF_STATUS 1
#define DLIS_SIZEOF_UNITS  DLIS_VARIABLE_LENGTH

#ifdef __cplusplus
}
#endif

#endif //DLISIO_TYPES_H
