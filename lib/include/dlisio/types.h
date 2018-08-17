#ifndef DLISIO_TYPES_H
#define DLISIO_TYPES_H

#include <stdint.h>

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

const char* dlis_sshort( const char*, int8_t* );
const char* dlis_snorm(  const char*, int16_t* );
const char* dlis_slong(  const char*, int32_t* );

const char* dlis_ushort( const char*, uint8_t* );
const char* dlis_unorm(  const char*, uint16_t* );
const char* dlis_ulong(  const char*, uint32_t* );

const char* dlis_fshort( const char*, float* );
const char* dlis_fsingl( const char*, float* );
const char* dlis_fdoubl( const char*, double* );

/* IBM and VAX floats */
const char* dlis_isingl( const char*, float* );
const char* dlis_vsingl( const char*, float* );

/* complex or validated floats */
const char* dlis_fsing1( const char*, float* V, float* A );
const char* dlis_fsing2( const char*, float* V, float* A, float* B );
const char* dlis_csingl( const char*, float* R, float* I );

const char* dlis_fdoub1( const char*, double* V, double* A );
const char* dlis_fdoub2( const char*, double* V, double* A, double* B );
const char* dlis_cdoubl( const char*, double* R, double* I );

const char* dlis_uvari( const char*, int32_t* out );

const char* dlis_ident( const char*, int32_t* len, char* out );
const char* dlis_ascii( const char*, int32_t* len, char* out );

#define DLIS_TZ_LST 0 // local standard
#define DLIS_TZ_DST 1 // local daylight savings
#define DLIS_TZ_GMT 2 // greenwich mean time

#define DLIS_YEAR_ZERO 1900
int dlis_year( int );

const char* dlis_dtime( const char*, int* Y,
                                     int* TZ,
                                     int* M,
                                     int* D,
                                     int* H,
                                     int* MN,
                                     int* S,
                                     int* MS );

const char* dlis_origin( const char*, int32_t* out );

/* obname = { origin, ushort, ident } */
const char* dlis_obname( const char*, int32_t* origin,
                                      uint8_t* copy_number,
                                      int32_t* idlen,
                                      char* identifier );

/* objref = { ident, obname } */
const char* dlis_objref( const char*, int32_t* ident_len,
                                      char* ident,
                                      int32_t* origin,
                                      uint8_t* copy_number,
                                      int32_t* objname_len,
                                      char* identifier );

/* attref = { ident, obname, ident } */
const char* dlis_attref( const char*, int32_t* ident1_len,
                                      char* ident1,
                                      int32_t* origin,
                                      uint8_t* copy_number,
                                      char* identifier,
                                      int32_t ident2_len,
                                      char* ident2 );

const char* dlis_status( const char*, uint8_t* );
const char* dlis_units( const char*, uint8_t*, char* );

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

#ifdef __cplusplus
}
#endif

#endif //DLISIO_TYPES_H
