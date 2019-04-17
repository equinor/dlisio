#ifndef DLISIO_COMMON_H
#define DLISIO_COMMON_H

/*
 * symbol visibility (export and import)
 *
 * The DLISIO_EXPORT symbol is set by cmake when building shared libraries.
 *
 * If linking to a shared build on Windows the DLISIO_SHARED symbol must be
 * defined too,
 */

/* make sure the symbol always exists */
#if defined(DLISIO_API)
    #error DLISIO_API is already defined
#endif

#define DLISIO_API

#if defined(DLISIO_EXPORT)
    #if defined(_MSC_VER)
        #undef DLISIO_API
        #define DLISIO_API __declspec(dllexport)
    #endif

    /*
     * nothing in particular is needed for symbols to be visible on non-MSVC
     * compilers
     */
#endif

#if !defined(DLISIO_EXPORT)
    #if defined(_MSC_VER) && defined(DLISIO_SHARED)
        /*
         * TODO: maybe this could be addressed by checking #ifdef _DLL, rather
         * than relying on DLISIO_SHARED being set.
         */
        #undef DLISIO_API
        #define DLISIO_API __declspec(dllimport)
    #endif

    /* assume gcc style exports if gcc or clang */
    #if defined(__GNUC__) || defined(__clang__)
        #undef DLISIO_API
        #define DLISIO_API __attribute__ ((visibility ("default")))
    #endif
#endif

#endif //DLISIO_COMMON_H
