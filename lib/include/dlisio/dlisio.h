#ifndef DLISIO_H
#define DLISIO_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/*
 * Read Storage Unit Label (SUL).
 * seqnum, layout, maxlen and id are nullable
 * Assure beforehand that xs contains at least DLIS_SUL_SIZE bytes
 */
#define DLIS_SUL_SIZE 80
int dlis_sul( const char* xs,
              int* seqnum,
              int* major,
              int* minor,
              int* layout,
              int64_t* maxlen,
              char* id );

/*
 * Look for something that is probably the SUL.
 *
 * In some files there are (possibly) random bytes before the SUL. Maybe this
 * is a proprietary dialect or copies gone wrong, but often the rest of the
 * file is fine.  This should be one of the first functions to call when
 * reading a DLIS file.
 *
 * Search [begin, begin+limit) for something that looks like it is the SUL.
 * This check is not exhaustive - call dlis_sul to check that it actually *is*
 * a SUL.
 *
 * The output paramter offset is the offset of the *first byte* of the SUL. If
 * the file is conforming to the RP66 standard, this should be 0.
 *
 * If this function cannot find anything that could be a SUL within the search
 * limit, it will abort the search and return DLIS_NOTFOUND. If this is the
 * case, the file is probably broken beyond repair, or not a DLIS file.
 *
 * This function returns DLIS_INCONSISTENT if it finds something that looks
 * like a SUL, but which cannot ever form a proper one. This usually comes from
 * data being clipped or bytes lost, and manual inspection has to be done to
 * check what is going on. Sometimes this can be recovered by searching past
 * this, looking for visible record envelopes.
 */
int dlis_find_sul(const char* from,
                  long long search_limit,
                  long long* offset);

/*
 * Look for something that is probably a visible record envelope
 *
 * Behaves similarly to dlis_find_sul, but for the visible envelope.
 */
int dlis_find_vrl(const char* from,
                  long long search_limit,
                  long long* offset);

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

/*
 * Query how many bytes to trim off the end of a record segment
 *
 * This function inspects the record segment body, and computes the number of
 * bytes to trimmed off the end.
 *
 * The attributes argument is the attributes byte, described by DLIS_SEGATTR_*,
 * and the attrs output parameter of dlis_lrsh. begin and end are pointers to
 * the first and one-past-end of the segment body respectively.
 *
 * The output parameter size is the number of bytes to trim.
 *
 * Returns DLIS_OK on success.
 *
 * Quite often, from a very peculiar interpretation of RP66, the padding
 * reported by pad bytes is the size of the segment *including the header*, in
 * which case (sizeof_body-trim < 0). When size > distance(begin, end), this
 * function returns DLIS_BAD_SIZE. It is up to the caller to determine if this
 * is an error, and how to handle it. dlisio reports what the file says
 * faithfully.
 *
 * Example:
 *
 * read_segment(&buffer, &segment_len);
 * int size = 0;
 * err = dlis_trim_record_segment(attrs,
 *                                buffer.data,
 *                                buffer.data + buffer.size,
 *                                &size);
 *
 * switch (err) {
 *     case DLIS_OK:
 *         buffer.size -= size;
 *         return OK;
 *
 *      case DLIS_BAD_SIZE:
 *           if (size - buffer.size != DLIS_LRSH_SIZE)
 *               return report_invalid_padding();
 *
 *           buffer.size = 0;
 *           return OK;
 *
 *      default:
 *           return report_other_error();
 * }
 */
int dlis_trim_record_segment(uint8_t attrs,
                             const char* begin,
                             const char* end,
                             int* size);

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
#define DLIS_FMT_OBJREF 'O'
#define DLIS_FMT_ATTREF 'A'
#define DLIS_FMT_STATUS 'q'
#define DLIS_FMT_UNITS  'Q'

/*
 * Parse and pack arbitrary data
 *
 * The dlis_packf (inspired by sscanf) reads arbitrary bytes in RP66 format,
 * and pack them into the dst area as native C data. No padding bytes are
 * inserted, which means the data can be read from this array by computing the
 * correct offset and memcpy'd into a typed variable.
 *
 * fmt is a sscanf-inspired format string of conversion specifiers
 * (DLIS_FMT_*). The size of each type depends on the most natural
 * corresponding C type, e.g. SSHORT is int8_t, and UNORM is uint16_t. The
 * arguments to a dlis_type() function in dlisio/types.h is the type being used
 * as a target type for a conversion specifier.
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
 * err = dlis_packf("Uffi", src, bytes);
 * if (err) exit(1);
 *
 * memcpy(&C1, bytes,      sizeof(C1));
 * memcpy(C2,  bytes + 2,  sizeof(C2));
 * memcpy(&c3, bytes + 10, sizeof(C3));
 */
int dlis_packf( const char* fmt, const void* src, void* dst );

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
 * Returns DLIS_OK on success, and DLIS_INVALID_ARGS if the format strings
 * contain any invalid format specifier. The output params are non-zero if
 * there are any variable-length values in the format specifier, and 0 if all
 * types are fixed-length. If the function fails, the output variable is
 * untouched.
 *
 * To compute the length of a fixed-size string, use dlis_pack_size. src is the
 * size of the pack on disk, and dst the length of the packed string in memory,
 * i.e.  UVARI is 4 bytes, not inconsistent. For individual object sizes, refer
 * to the DLIS_SIZEOF constants in dlisio/types.h
 *
 * NOTE:
 * dlis_pack_size considers the src variable-size when fmt has UVARI, but the
 * dst fixed-size. This will return DLIS_OK, but set src to
 * DLIS_VARIABLE_LENGTH (= 0).
 *
 * For both functions, both src and dst can be NULL, in which case no data will
 * be written.
 */
int dlis_pack_varsize(const char* fmt, int* src, int* dst);
int dlis_pack_size(const char* fmt, int* src, int* dst);

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
 * there with millions of logical records.
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
 * allocsize: upper bound on the number of records read for this invocation.
 *            Should be the same as the size allocated in tells/residuals/explicits.
 * initial_residual: number of still-to-process bytes in the last seen visible envelope.
 *                   If called from the start of the file (past the storage unit
 *                   label) this should be 0. Upon return, this will be the
 *                   remaining bytes of the current VR at the end of the
 *                   previously-read record, i.e. the value needed to resume.
 * next: the first byte past the end. For successive invocations, this points
 *       to the first, un-read record.
 * count: number of processed logical records.
 *        Incremented for every logical record - this is the actual size of output arrays
 * tells: distance (<=0) from end of the file [end param] to the
 *        1) start of logical record OR
 *        2) start of visible envelope if LR alligns with VE boundaries
 * residuals: bytes remaining for processing in the last encountered visible record.
 *            For LR alligning with VE boundaries value is 0 (not VE size)
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
 * Return value
 * ------------
 *  DLIS_OK: when all records in [begin, end) are read, or when reading the
 *           next record would overflow allocsize. To determine which one,
 *           check the value of next. If next == end, all records are read.
 *  DLIS_TRUNCATED: end was reached before full logical record was read
 *  DLIS_INVALID_ARGS: begin is same as end
 *  DLIS_INCONSISTENT: error on reading headers was thrown by internal function
 *  DLIS_UNEXPECTED_VALUE: VR length < 20 bytes or LRS length < 16
 *
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
 *     reallocate(allocsize, &tells, &residuals, &explicits);
 *     begin = next;
 * }
 *
 * size_t filesize = file.end - file.begin + 80;
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
 * Compute a fingerprint, a string-like representation of an object reference.
 *
 * All objects specified by RP66 should be uniquely identified by a combination
 * of the containing set, the origin- and copy number, and an identifier. The
 * fingerprint function maps these parameters into a unique string of
 * object_fingerprint_len length that's suitable for identifiers, dictionary
 * keys etc.
 *
 * the len function, like strlen, returns the length *excluding* the
 * terminating zero ('\0').
 *
 * The fingerprint is not guaranteed to be stable between releases of dlisio.
 * The fingerprint function assumes a buffer of at least fingerprint_len
 * length, and *does not* write the terminating zero '\0'
 *
 * The len function returns the length of the fingerprint in bytes on success,
 * negative otherwise.
 */
int dlis_object_fingerprint_len(int32_t type_len,
                                const char* type,
                                int32_t id_len,
                                const char* id,
                                int32_t origin,
                                uint8_t copynum);

int dlis_object_fingerprint(int32_t type_len,
                            const char* type,
                            int32_t id_len,
                            const char* id,
                            int32_t origin,
                            uint8_t copynum,
                            char* fingerprint);

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
    DLIS_BAD_SIZE,
    DLIS_NOTFOUND,
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
