#ifndef DLISIO_PYTHON_IO_HPP
#define DLISIO_PYTHON_IO_HPP

namespace dl {

struct bookmark {
    std::fpos_t pos;

    /*
     * the remaining bytes of the "previous" visible record. if 0, the current
     * object is the visible record label
     */
    int residual = 0;

    int isexplicit = 0;
    int isencrypted = 0;

    /*
     * only pos is used for seeking and repositioning - tell is used only for
     * __repr__ and debugging purposes
     */
    long long tell = 0;
};

}

#endif // DLISIO_PYTHON_IO_HPP
