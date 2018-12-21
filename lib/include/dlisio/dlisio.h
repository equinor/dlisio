#ifndef DLISIO_H
#define DLISIO_H

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
