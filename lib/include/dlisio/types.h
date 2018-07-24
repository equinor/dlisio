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

const char* dlis_dtime( const char*, int* Y,
                                     int* TZ,
                                     int* M,
                                     int* D,
                                     int* H,
                                     int* MN,
                                     int* S,
                                     int* MS );

const char* dlis_origin( const char*, int32_t* out );

const char* dlis_obname( const char*, int32_t* origin,
                              uint8_t* copy_number,
                              char* identifier );

/* objref = { ident, obname } */
const char* dlis_objref( const char*, int32_t* ident_len,
                                      char* ident,
                                      int32_t* origin,
                                      uint8_t* copy_number,
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

#ifdef __cplusplus
}
#endif

#endif //DLISIO_TYPES_H
