#ifndef DLISIO_H
#define DLISIO_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

int dlis_sul( const char* xs,
              int* seqnum,
              int* major,
              int* minor,
              int* layout,
              int64_t* maxlen,
              char* id );

#define DLIS_VRL_SIZE 4
int dlis_vrl( const char* xs,
              int* len,
              int* version );

/* logical-record-segment-header */
#define DLIS_LRSH_SIZE 4
int dlis_lrsh( const char* xs,
               int* length,
               uint8_t* attrs,
               int* type );

/*
 * dlis_segment_attributes is pure convenience - it queries all segment
 * attributes (booleans). In languages where the header is available and
 * bitwise operations readily available, use the keys directly, but it's very
 * useful when dlopen'd etc., or as a quick way of forwarding flags to a host
 * library
 */
int dlis_segment_attributes( uint8_t,
                             int* explicit_formatting,
                             int* has_predecessor,
                             int* has_successor,
                             int* is_encrypted,
                             int* has_encryption_packet,
                             int* has_checksum,
                             int* has_trailing_length,
                             int* has_padding );
/*
 * Query the encryption packet, but don't actually read it.
 *
 * Returns the length *of the encryption packet*, so if there is none (it is
 * optional), len is set to zero.
 */
int dlis_encryption_packet_info( const char*,
                                 int* len,
                                 int* companycode );

/*
 * The component is the first thing that comes in a set, and the first piece of
 * information that describes actual data.
 *
 * The first component of a record is always a Set. After the set follows a set
 * of attributes, the Template, that describe all objects in this record. The
 * Template is terminated by encountering an object.
 *
 * The dlis_component function outputs the dlis_component_role enum, which can
 * be used to determine how to interpret the rest of the descriptor (set,
 * object, attrib).
 *
 * The component_ functions take the descriptor *and* the role as arguments.
 * This is a sanity check - if set is invoked with an object descriptor,
 * UNEXPECTED_VALUE will be returned, and no arguments modified.
 *
 * If a mandatory flag is not set, these functions return INCONSISTENT. This
 * might not necessarily be an application error, only information for a
 * warning about more inconsistenties later.
 *
 * The intended use is something along the lines of:
 *
 * read(&descriptor);
 * dlis_component( descriptor, &role );
 *
 * switch( role ) {
 *      case SET:
 *          dlis_component_set( descriptor, role, &type, &name );
 *          [prepare for building template]
 *          break;
 *      case OBJECT:
 *          dlis_component_object( descriptor, role, &obname );
 *          [read object according to template]
 *          break;
 *      ...
 * }
 */

#define DLIS_DESCRIPTOR_SIZE 1
int dlis_component( uint8_t descriptor, int* role );

int dlis_component_set( uint8_t descriptor,
                        int role,
                        int* type,
                        int* name );

int dlis_component_object( uint8_t descriptor,
                           int role,
                           int* obname );

int dlis_component_attrib( uint8_t descriptor,
                           int role,
                           int* label,
                           int* count,
                           int* reprcode,
                           int* units,
                           int* value );

const char* dlis_component_str( int );


#define DLIS_FMT_EOL    '\0'
#define DLIS_FMT_FSHORT 'r'
#define DLIS_FMT_FSINGL 'f'
#define DLIS_FMT_FSING1 'b'
#define DLIS_FMT_FSING2 'B'
#define DLIS_FMT_ISINGL 'x'
#define DLIS_FMT_VSINGL 'V'
#define DLIS_FMT_FDOUBL 'F'
#define DLIS_FMT_FDOUB1 'z'
#define DLIS_FMT_FDOUB2 'Z'
#define DLIS_FMT_CSINGL 'c'
#define DLIS_FMT_CDOUBL 'C'
#define DLIS_FMT_SSHORT 'd'
#define DLIS_FMT_SNORM  'D'
#define DLIS_FMT_SLONG  'l'
#define DLIS_FMT_USHORT 'u'
#define DLIS_FMT_UNORM  'U'
#define DLIS_FMT_ULONG  'L'
#define DLIS_FMT_UVARI  'i'
#define DLIS_FMT_IDENT  's'
#define DLIS_FMT_ASCII  'S'
#define DLIS_FMT_DTIME  'j'
#define DLIS_FMT_ORIGIN 'J'
#define DLIS_FMT_OBNAME 'o'
#define DLIS_FMT_OBJREF 'O'//is O ever a good idea?
#define DLIS_FMT_ATTREF 'A'
#define DLIS_FMT_STATUS 'q'
#define DLIS_FMT_UNITS  'Q'


/*
 * Parse and pack arbitrary data
 *
 * The dlis_packf (inspired by sscanf) reads ??bytes arbitrary bytes?? in RP66
 * format, and packs it(?) into the dst area. No padding bytes are inserted, which
 * means the data can be read from this array by computing the correct offset
 * and memcpy'd into a typed variable.
 *
 * fmt is a sscanf-inspired format string of conversion specifiers
 * (DLIS_FMT_*). The size of each type depends on the most natural
 * corresponding C type, e.g. SSHORT is int8_t, and UNORM is uint16_t. ??would full table be useful to anyone?? The
 * arguments to a dlis_type() function in dlisio/types.h is the type being used
 * as a target type for a conversion specifier.
 *
 * String types are always written as int32_t + len bytes, without a zero
 * terminator.
 *
 * Example:
 *
 * Extracting a frame with three channels:
 * C1 -> 1x1 unorm (i16)
 * C2 -> 2x1 fsingle (f32)
 * C3 -> 1x1 uvari (yields i32)
 *
 * int16_t C1;
 * float C2[2];
 * int32_t C3;
 *
 * unsigned char bytes[2 + 2*4 + 4];
 * err = dlis_packf( "Uffi", src, bytes );
 * if (err) exit(1);
 *
 * memcpy( &C1, bytes, sizeof(C1) );
 * memcpy( C2, bytes + 2, sizeof(C2) );
 * memcpy( &c3, bytes + 10, sizeof(C3) );
 */
int dlis_packf( const char* fmt, const void* src, void* dst );

/*
 * Check if a format string for packing is var-size or fixed-size
 *
 * This function is intended for checking if format strings built from
 * inspecting records is fixed-sized or not, which in turn can guide if it's
 * possible to random-access onto variables. Note size refers to the size of
 * the the *output* parameter, i.e. UVARI (variable-length unsigned int) is
 * considered fixed-size.
 *
 * This functionality can be implemented by manually checking if the format
 * string contains any of "sSoOAQ", but is provided for convenience.
 *
 * Returns DLIS_OK on success, and DLIS_INVALID_ARGS if the format strings
 * contain any invalid format specifier. out is non-zero if there are any
 * variable-length values in the format specifier, and 0 if all types are
 * fixed-length. If the function fails, the output variable is untouched.
 *
 * To compute the length of a fixed-size string, use dlis_pack_size
 */
int dlis_pack_varsize( const char* fmt, int* out );

int dlis_pack_size( const char* fmt, int* size );

/*
 * A table of the record attributes, high bit first:
 *
 * 1 Logical Record Structure
 *      If set, means explicit record formatting
 * 2 Predecessor
 *      If set, this is *not* the first segment of the logical record
 * 3 Successor
 *      If set, this is *not* the last segment of the logical record
 * 4 Encryption
 *      If set, the record is encrypted
 * 5 Encryption Packet
 *      If set, an encryption packet exists
 * 6 Checksum
 *      If set, there is a checksum
 * 7 Trailing Length
 *      If set, there is a trailing length
 * 8 Padding
 *      If set, the record is padded
 */

enum dlis_segment_attribute {
    DLIS_SEGATTR_EXFMTLR = 1 << 7,
    DLIS_SEGATTR_PREDSEG = 1 << 6,
    DLIS_SEGATTR_SUCCSEG = 1 << 5,
    DLIS_SEGATTR_ENCRYPT = 1 << 4,
    DLIS_SEGATTR_ENCRPKT = 1 << 3,
    DLIS_SEGATTR_CHCKSUM = 1 << 2,
    DLIS_SEGATTR_TRAILEN = 1 << 1,
    DLIS_SEGATTR_PADDING = 1 << 0,
};

/*
 * Find offsets of logical records
 *
 * Finding the offsets where logical segments start is not quite straight
 * forward, because logical records aren't required to align with visible
 * record envelopes. Additionally, there's no requirement that visible records
 * nor logical records are of equal length. Furthermore, there are files out
 * there with number of logical records in the millions.
 *
 * This function finds the start of logical records [1], and outputs:
 * 1. the (negative) distance from end to record
 * 2. the bytes *remaining* in this visible record
 * 3. if this record is explicitly formatted or not
 *
 * Because it's unknown how many records there are in a file (or even a section
 * of a file), pre-allocation of output arrays is impractical. Instead, it is
 * designed to be "resumable" - when allocated output arrays are exhausted, the
 * function returns (with DLIS_OK), and more space can be allocated (or
 * something else altogether). If invoked again with the same initial_residual,
 * end, and count, and next as the new begin, the effect will be the same as if
 * the larger allocation was given to the original call.
 *
 * It records the (record - end) negative distance, because it makes "fixing"
 * the offsets (i.e. making them 0-offset from start-of-file) easier with
 * multiple invocations. It also allows begin to change, which is more natural
 * than the one-beyond-last. For a reference, see examples.
 *
 * Using begin/end pairs of pointers allows this function to find positions of
 * logical records from the middle of files and sequences, and leaves actual
 * reading from file/disk to the caller. This is particularly useful with
 * memory mapped files, as it would be an efficient code path to quickly
 * indexing a new file.
 *
 * No arrays are compressed, i.e. the tells[0], residuals[0] and explicits[0]
 * all describe the same logical record.
 *
 * Records are read until either:
 * 1. the end-of-file is reached (given by end)
 * 2. allocsize records are read
 *
 * Both are considered success, and return DLIS_OK. If end-of-file is reached
 * => next == end
 *
 * For every recorded record, count is incremented. Count *must* be initialised
 * before calling this function. Count is *not* reset between invocations.
 *
 * Arguments
 * ---------
 * begin: start of memory area
 * end: one-beyond memory area
 * allocsize: the size allocated in tells/residuals/explicits. this is an upper
 *            bound on the number of records read for this invocation
 * initial_residual: how far into the previous visible envlope begin is. If
 *                   called from the start of the file (past the storage unit
 *                   label) this should be 0. Upon return, this will be the
 *                   remaining bytes of the current VRL at the end of the
 *                   previously-read record, i.e. the value needed to resume.
 * next: the first byte past the end. For successive invocations, this points
 *       to the first, un-read record.
 * count: incremented for every logical record - this is the size of output
 *        arrays
 * tells: distances begin, record
 * residuals: bytes remaining in this visible record
 * explicits: if record is explicit
 *
 * next and explicits are optional, and can be NULL. However, unless deciding
 * information is sourced elsewhere, it will now be impossible to distinguish
 * some cases
 *
 * When non-ok error codes are returned, all outputs are updated to the last
 * good known value. This allows manual investigation of issues, before the
 * mapping is resumed. When encountering broken files or minor protocol
 * violations, this enables skipping bits and resuming interpretation.
 *
 * Errors
 * ------
 *  DLIS_OK: when all records in [begin, end) are recorded, or when reading the
 *           next record would overflow allocsize. To determine which one,
 *           check the value of next. If next == end, all records are read.
 *
 * Examples
 * --------
 *
 * count = 0;
 * initial_residual = 0;
 * begin = file.begin + 80; // start-of-file + SUL
 * while (true) {
 *     err = dlis_record_offset( begin,
 *                               end,
 *                               allocsize,
 *                               &initial_residual,
 *                               &next,
 *                               &count,
 *                               count + tells,
 *                               count + residuals,
 *                               count + explicits );
 *
 *     if (err != DLIS_OK) exit(EXIT_FAILURE);
 *     if (next == end) break;
 *
 *     double_arraysize(allocsize, &tells, &residuals, &explicits);
 *     begin = next;
 * }
 *
 * size_t filesize = file.begin + 80;
 * for (int i = 0; i < count; ++i)
 *     tells[i] += filesize;
 *
 * Evident from this example, only tells needs to be updated. count,
 * initial_residual, and begin/next are designed to carry between calls.
 *
 * [1] not segments
 */
int dlis_index_records( const char* begin,
                        const char* end,
                        size_t allocsize,
                        int* initial_residual,
                        const char** next,
                        int* count,
                        long long* tells,
                        int* residuals,
                        int* explicits );


/*
 * A table of the component roles, given by the three high bits of the
 * dlis_component
 *
 * Bits Role     Type
 * ---------------------------------
 * 000  ABSATR   Absent attributes
 * 001  ATTRIB   Attribute
 * 010  INVATR   Invariant Attribute
 * 011  OBJECT   Object
 * 100  reserved    -
 * 101  RDSET    Redundant Set
 * 110  RSET     Replacement Set
 * 111  SET      Set
 */
enum dlis_component_role {
    DLIS_ROLE_ABSATR = 0,
    DLIS_ROLE_ATTRIB = 1 << 5,
    DLIS_ROLE_INVATR = 1 << 6,
    DLIS_ROLE_OBJECT = 1 << 6 | 1 << 5,
    DLIS_ROLE_RESERV = 1 << 7,
    DLIS_ROLE_RDSET  = 1 << 7 | 1 << 5,
    DLIS_ROLE_RSET   = 1 << 7 | 1 << 6,
    DLIS_ROLE_SET    = 1 << 7 | 1 << 6 | 1 << 5,
};

enum DLIS_STRUCTURE {
    DLIS_STRUCTURE_UNKNOWN,
    DLIS_STRUCTURE_RECORD,
    DLIS_STRUCTURE_FIXREC,
    DLIS_STRUCTURE_RECSTM,
    DLIS_STRUCTURE_FIXSTM,
};

enum DLIS_ERRCODE {
    DLIS_OK = 0,
    DLIS_INCONSISTENT,
    DLIS_UNEXPECTED_VALUE,
    DLIS_INVALID_ARGS,
    DLIS_TRUNCATED,
};

enum dlis_eflr_type_code {
    DLIS_FHLR   = 0,
    DLIS_OLR    = 1,
    DLIS_AXIS   = 2,
    DLIS_CHANNL = 3,
    DLIS_FRAME  = 4,
    DLIS_STATIC = 5,
    DLIS_SCRIPT = 6,
    DLIS_UPDATE = 7,
    DLIS_UDI    = 8,
    DLIS_LNAME  = 9,
    DLIS_SPEC   = 10,
    DLIS_DICT   = 11,
};


#ifdef __cplusplus
}
#endif

#endif //DLISIO_H
