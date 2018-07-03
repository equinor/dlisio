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


#ifdef __cplusplus
}
#endif

#endif //DLISIO_H
