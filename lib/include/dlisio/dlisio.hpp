#ifndef DLISIO_HPP
#define DLISIO_HPP

#include <cstddef>
#include <cstdint>


namespace dl {

/*
 * Read Storage Unit Label (SUL).
 * seqnum, layout, maxlen and id are nullable
 * Assure beforehand that xs contains at least SUL_SIZE bytes
 */
constexpr int SUL_SIZE = 80;
int sul( const char* xs,
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
 * This check is not exhaustive - call dl::sul to check that it actually *is*
 * a SUL.
 *
 * The output paramter offset is the offset of the *first byte* of the SUL. If
 * the file is conforming to the RP66 standard, this should be 0.
 *
 * If this function cannot find anything that could be a SUL within the search
 * limit, it will abort the search and return ERROR_NOTFOUND. If this is the
 * case, the file is probably broken beyond repair, or not a DLIS file.
 *
 * This function returns ERROR_INCONSISTENT if it finds something that looks
 * like a SUL, but which cannot ever form a proper one. This usually comes from
 * data being clipped or bytes lost, and manual inspection has to be done to
 * check what is going on. Sometimes this can be recovered by searching past
 * this, looking for visible record envelopes.
 */
int find_sul(const char* from,
             long long search_limit,
             long long* offset);

/*
 * Look for something that is probably a visible record envelope
 *
 * Behaves similarly to dl::find_sul, but for the visible envelope.
 */
int find_vrl(const char* from,
             long long search_limit,
             long long* offset);

/*
 * Check if the 12 next bytes looks like a tapemark.
 */
int tapemark(const char* buffer, int size);

constexpr int VRL_SIZE = 4;
int vrl( const char* xs,
         int* len,
         int* version );

/* logical-record-segment-header */
constexpr int LRSH_SIZE = 4;
int lrsh( const char* xs,
          int* length,
          uint8_t* attrs,
          int* type );

/*
 * dl::segment_attributes is pure convenience - it queries all segment
 * attributes (booleans). In languages where the header is available and
 * bitwise operations readily available, use the keys directly, but it's very
 * useful when dlopen'd etc., or as a quick way of forwarding flags to a host
 * library
 */
int segment_attributes( uint8_t,
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
int encryption_packet_info( const char*,
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
 * The component function outputs the dl::component_role enum, which can
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
 * dl::component( descriptor, &role );
 *
 * switch( role ) {
 *      case SET:
 *          dl::component_set( descriptor, role, &type, &name );
 *          [prepare for building template]
 *          break;
 *      case OBJECT:
 *          dl::component_object( descriptor, role, &obname );
 *          [read object according to template]
 *          break;
 *      ...
 * }
 */

constexpr int DESCRIPTOR_SIZE = 1;
int component( uint8_t descriptor, int* role );

int component_set( uint8_t descriptor,
                   int role,
                   int* type,
                   int* name );

int component_object( uint8_t descriptor,
                      int role,
                      int* obname );

int component_attrib( uint8_t descriptor,
                      int role,
                      int* label,
                      int* count,
                      int* reprcode,
                      int* units,
                      int* value );

const char* component_str( int );

/*
 * Query how many bytes to trim off the end of a record segment
 *
 * This function inspects the record segment body, and computes the number of
 * bytes to trimmed off the end.
 *
 * The attributes argument is the attributes byte, described by SEGATTR_*,
 * and the attrs output parameter of dl::lrsh. begin and end are pointers to
 * the first and one-past-end of the segment body respectively.
 *
 * The output parameter size is the number of bytes to trim.
 *
 * Returns ERROR_OK on success.
 *
 * For encrypted records trim size is always 0 and code is ERROR_OK. Padbytes
 * are encrypted, hence can't be trimmed before record is decrypted. To
 * preserve consistency trailing length and checksum are not trimmed either.
 *
 * Quite often, from a very peculiar interpretation of RP66, the padding
 * reported by pad bytes is the size of the segment *including the header*, in
 * which case (sizeof_body-trim < 0). When size > distance(begin, end), this
 * function returns ERROR_BAD_SIZE. It is up to the caller to determine if this
 * is an error, and how to handle it. dlisio reports what the file says
 * faithfully.
 *
 * Example:
 *
 * read_segment(&buffer, &segment_len);
 * int size = 0;
 * err = dl::trim_record_segment(attrs,
 *                               buffer.data,
 *                               buffer.data + buffer.size,
 *                               &size);
 *
 * switch (err) {
 *     case ERROR_OK:
 *         buffer.size -= size;
 *         return OK;
 *
 *      case ERROR_BAD_SIZE:
 *           if (size - buffer.size != LRSH_SIZE)
 *               return report_invalid_padding();
 *
 *           buffer.size = 0;
 *           return OK;
 *
 *      default:
 *           return report_other_error();
 * }
 */
int trim_record_segment(uint8_t attrs,
                        const char* begin,
                        const char* end,
                        int* size);

constexpr char FMT_EOL     = '\0';
constexpr char FMT_FSHORT  = 'r';
constexpr char FMT_FSINGL  = 'f';
constexpr char FMT_FSING1  = 'b';
constexpr char FMT_FSING2  = 'B';
constexpr char FMT_ISINGL  = 'x';
constexpr char FMT_VSINGL  = 'V';
constexpr char FMT_FDOUBL  = 'F';
constexpr char FMT_FDOUB1  = 'z';
constexpr char FMT_FDOUB2  = 'Z';
constexpr char FMT_CSINGL  = 'c';
constexpr char FMT_CDOUBL  = 'C';
constexpr char FMT_SSHORT  = 'd';
constexpr char FMT_SNORM   = 'D';
constexpr char FMT_SLONG   = 'l';
constexpr char FMT_USHORT  = 'u';
constexpr char FMT_UNORM   = 'U';
constexpr char FMT_ULONG   = 'L';
constexpr char FMT_UVARI   = 'i';
constexpr char FMT_IDENT   = 's';
constexpr char FMT_ASCII   = 'S';
constexpr char FMT_DTIME   = 'j';
constexpr char FMT_ORIGIN  = 'J';
constexpr char FMT_OBNAME  = 'o';
constexpr char FMT_OBJREF  = 'O';
constexpr char FMT_ATTREF  = 'A';
constexpr char FMT_STATUS  = 'q';
constexpr char FMT_UNITS   = 'Q';

/*
 * Parse and pack arbitrary data
 *
 * The dl::packf (inspired by sscanf) reads arbitrary bytes in RP66 format,
 * and pack them into the dst area as native C data. No padding bytes are
 * inserted, which means the data can be read from this array by computing the
 * correct offset and memcpy'd into a typed variable.
 *
 * fmt is a sscanf-inspired format string of conversion specifiers
 * (dl::fmt_*). The size of each type depends on the most natural
 * corresponding C type, e.g. SSHORT is int8_t, and UNORM is uint16_t. The
 * arguments to a type_frombytes() function in dlisio/types.hpp is the type being used
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
 * err = dl::packf("Uffi", src, bytes);
 * if (err) exit(1);
 *
 * memcpy(&C1, bytes,      sizeof(C1));
 * memcpy(C2,  bytes + 2,  sizeof(C2));
 * memcpy(&c3, bytes + 10, sizeof(C3));
 */
int packf( const char* fmt, const void* src, void* dst );

/*
 * dl::packflen is to dl::packf as strlen is to strings
 *
 * dl::packflen counts the number of bytes read from src, and what would be
 * written to dst, by dl::packf with the same fmt and src.
 *
 * This is particularly useful when wanting to only pack *parts* of a record,
 * e.g. when certain columns are filtered out.
 */
int packflen(const char* fmt, const void* src, int* nread, int* nwrite);

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
 * Returns ERROR_OK on success, and ERROR_INVALID_ARGS if the format strings
 * contain any invalid format specifier. The output params are non-zero if
 * there are any variable-length values in the format specifier, and 0 if all
 * types are fixed-length. If the function fails, the output variable is
 * untouched.
 *
 * To compute the length of a fixed-size string, use dl::pack_size. src is the
 * size of the pack on disk, and dst the length of the packed string in memory,
 * i.e.  UVARI is 4 bytes, not inconsistent. For individual object sizes, refer
 * to the SIZEOF constants in dlisio/types.hpp
 *
 * NOTE:
 * dl::pack_size considers the src variable-size when fmt has UVARI, but the
 * dst fixed-size. This will return ERROR_OK, but set src to
 * VARIABLE_LENGTH (= 0).
 *
 * For both functions, both src and dst can be NULL, in which case no data will
 * be written.
 */

int pack_varsize(const char* fmt, int* src, int* dst);

int pack_size(const char* fmt, int* src, int* dst);

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

enum segment_attribute {
    SEGATTR_EXFMTLR = 1 << 7,
    SEGATTR_PREDSEG = 1 << 6,
    SEGATTR_SUCCSEG = 1 << 5,
    SEGATTR_ENCRYPT = 1 << 4,
    SEGATTR_ENCRPKT = 1 << 3,
    SEGATTR_CHCKSUM = 1 << 2,
    SEGATTR_TRAILEN = 1 << 1,
    SEGATTR_PADDING = 1 << 0,
};

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
int object_fingerprint_size(int32_t type_len,
                            const char* type,
                            int32_t id_len,
                            const char* id,
                            int32_t origin,
                            uint8_t copynum,
                            int* size);

int object_fingerprint(int32_t type_len,
                       const char* type,
                       int32_t id_len,
                       const char* id,
                       int32_t origin,
                       uint8_t copynum,
                       char* fingerprint);


/*
 * A table of the component roles, given by the three high bits of the
 * component
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
enum COMPONENT_ROLE {
    COMP_ROLE_ABSATR = 0,
    COMP_ROLE_ATTRIB = 1 << 5,
    COMP_ROLE_INVATR = 1 << 6,
    COMP_ROLE_OBJECT = 1 << 6 | 1 << 5,
    COMP_ROLE_RESERV = 1 << 7,
    COMP_ROLE_RDSET  = 1 << 7 | 1 << 5,
    COMP_ROLE_RSET   = 1 << 7 | 1 << 6,
    COMP_ROLE_SET    = 1 << 7 | 1 << 6 | 1 << 5,
};

enum STRUCTURE {
    STRUCTURE_UNKNOWN,
    STRUCTURE_RECORD,
    STRUCTURE_FIXREC,
    STRUCTURE_RECSTM,
    STRUCTURE_FIXSTM,
};

enum ERRCODE {
    ERROR_OK = 0,
    ERROR_INCONSISTENT,
    ERROR_UNEXPECTED_VALUE,
    ERROR_INVALID_ARGS,
    ERROR_TRUNCATED,
    ERROR_BAD_SIZE,
    ERROR_NOTFOUND,
};

} // namespace dl

#endif //DLISIO_HPP
