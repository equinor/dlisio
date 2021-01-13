#ifndef DLISIO_RECORDS_HPP
#define DLISIO_RECORDS_HPP

#include <complex>
#include <cstdint>
#include <exception>
#include <tuple>
#include <type_traits>
#include <utility>
#include <vector>

#include <mpark/variant.hpp>

#include <dlisio/types.h>

namespace dl = dlis;

namespace dlis {
/*
 * Parsing and parsing input
 *
 * the strategy is to first parse the EFLR template and build a parsing guide,
 * expressed as the object_template. Later, this template instantiates the
 * default object in the set, and edits the fields as it goes along. The value
 * field can be zero or more values, so it's neatly stored as a vector, but the
 * *type* is indeterminate until the representation code is understood.
 *
 * The variant is a perfect fit for this.
 *
 * A variant-of-vector seems a better fit than vector-of-variants, both because
 * the max-size-overhead isn't so bad (all vectors are the same size), but the
 * type-resolution only has to be done once, and the unstructuring of the
 * vector can be contained inside the visitor.
 */
using value_vector = mpark::variant<
    mpark::monostate,
    std::vector< fshort >,
    std::vector< fsingl >,
    std::vector< fsing1 >,
    std::vector< fsing2 >,
    std::vector< isingl >,
    std::vector< vsingl >,
    std::vector< fdoubl >,
    std::vector< fdoub1 >,
    std::vector< fdoub2 >,
    std::vector< csingl >,
    std::vector< cdoubl >,
    std::vector< sshort >,
    std::vector< snorm  >,
    std::vector< slong  >,
    std::vector< ushort >,
    std::vector< unorm  >,
    std::vector< ulong  >,
    std::vector< uvari  >,
    std::vector< ident  >,
    std::vector< ascii  >,
    std::vector< dtime  >,
    std::vector< origin >,
    std::vector< obname >,
    std::vector< objref >,
    std::vector< attref >,
    std::vector< status >,
    std::vector< units  >
>;

/*
 * Assigned error severity.
 */
enum class error_severity {
    INFO     = 1, // everything seems fine, but situation itself is not typical
    MINOR    = 2, // contradicts specification, but recovery is most likely ok
    MAJOR    = 3, // contradicts specification, not sure if recovery is ok
    CRITICAL = 4, // broken beyond repair, could not recover
};

/*
 * Error which is caused by violations with regards to rp66 protocol.
 *
 * It can be classified by us in different severity levels. In some situations
 * we might know that violation is common and have a good idea how to recover.
 * In other situations violation might be too severe for us to do anything about
 * it.
 */
struct dlis_error {
    error_severity severity;
    std::string problem;
    std::string specification;
    std::string action;
};

struct error_handler {
    virtual void log(const error_severity &level, const std::string &context,
                     const std::string &problem,const std::string &specification,
                     const std::string &action)
        const noexcept(false) = 0;

    virtual ~error_handler() = default;
};

struct record {
    bool isexplicit()  const noexcept (true);
    bool isencrypted() const noexcept (true);

    int type;
    std::uint8_t attributes;
    bool consistent;
    std::vector< char > data;
};

/*
 * The structure of an attribute as described in 3.2.2.1
 *
 * Error handling:
 *
 * Due to the intricate structure of a dlis-file, dlisio typically over-parses
 * when a certain piece of information is queried. This would typically make
 * any warnings or errors issued from the parsing routines pre-mature and might
 * result in the query failing due to an error in some (from a
 * user-perspective) unrelated data.
 *
 * To combat this, the result of parsing routines (and the state of the
 * parsed object) is communicated through error codes set on the object.
 *
 *      It is the consumers responsibility to check the state of the
 *      object before using its content.
 *
 * object_attribute.log contains a list of dlis::dlis_error, which provide
 * human-readable explanation of the problem
 */
struct object_attribute {
    dl::ident           label = {};
     // cppcheck-suppress constStatement
    dl::uvari           count = dl::uvari{ 1 };
    representation_code reprc = representation_code::ident;
    dl::units           units = {};
    dl::value_vector    value = {};
    bool invariant            = false;

    std::vector< dl::dlis_error > log;

    bool operator == (const object_attribute& ) const noexcept (true);
};

/*
 * The Object Set Template (3.2.1 EFLR: General layout) is just an ordered set
 * of attributes, so just alias a vector
 */
using object_template = std::vector< object_attribute >;

/*
 * Parsing output and semantic objects
 *
 * C++ representation of the set of logical record types (listed in Appendix A
 * - Logical Record Types, described in Chapter 5 - Static and Frame Data)
 *
 * They all derive from basic_object, but that's just a low-syntactical
 * overhead way of adding the object-name field, which is present in every
 * object. In fact, this object-name preceeds the attributes and is introduced
 * by the component descriptor (3.2.2.1 Component Descriptor figure 3-4). It
 * carries no other semantic or operational significance and should be
 * considered an implementation detail.
 *
 * While not very clear on the matter, in practice every attribute of even
 * well-specified object types (such as CHANNEL) can be absent. Because of
 * this, every attribute is an Optional. The lack of a value in the optional
 * means either that the attribute is explicitly marked absent (see
 * DLIS_ROLE_ABSATR), or not present at all in the object template. It is
 * impossible to distinguish these cases without consulting the template
 * itself.
 *
 * The member variables are designed and enriched with the intention that
 * member variables are set with the object_attribute::into functions. Other
 * code expects that all objects have the two methods set and remove:
 *
 * void set( const object_attribute& );
 * void remove( const object_attribute& );
 *
 * These should map object attribute label to the right member variable, and
 * set/unset respectively - remove is called when encoutering ABSATR, set
 * otherwise.
 */

/*
 * All objects have an object name (3.2.2.1 Component Descriptor figure 3-4)
 */
struct basic_object {
    void set( const object_attribute& )    noexcept (false);
    void remove( const object_attribute& ) noexcept (false);

    std::size_t len() const noexcept (true);
    const dl::object_attribute&
    at( const std::string& ) const noexcept (false);

    bool operator == (const basic_object&) const noexcept (true);
    bool operator != (const basic_object&) const noexcept (true);

    dl::obname object_name;
    dl::ident type;
    std::vector< object_attribute > attributes;
    std::vector< dl::dlis_error > log;
};

/* Object set
 *
 * The object SET, as defined by rp66v1 chapter 3.2.1 is a series of objects -
 * all derived from the same object template, all of the same type.
 *
 * Due to the variable sized data in the SET and OBJECTs within it, there is
 * no easy way of randomly accessing specific objects. Making an index to
 * achieve random access would require a full parse too, so there is really no
 * good way of parsing single objects. Hence the entire set is parsed and
 * cached in one go.
 *
 * However, parsing a lot of sets is expensive and often unnecessary. To avoid
 * the upfront cost of parsing, object_set is a self parsing type. I.e.  it is
 * initialized with a buffer of raw bytes making up the set - which is
 * comparably much cheaper to extract than the actual parsing. The parsing is
 * considered an implementation detail of the class and will be postponed until
 * the first outside query for objects.
 *
 * Typical object queries will revolve around the type of object - hence
 * parsing the set type (and name) independently of the rest of the set makes
 * sense.
 *
 * Caching the raw bytes on the object also makes it independent of IO.
 *
 * Encrypted Records:
 *
 * encrypted records cannot be parsed by dlisio without being decrypted first.
 * As object_set does its parsing itself, it _will_ fail on construction if
 * given an encrypted record.
 *
 * Log:
 *
 * As well as attributes, every object set should have information about issues
 * that arose during parsing.
 */
using object_vector = std::vector< basic_object >;

struct object_set {
public:
    explicit object_set( dl::record ) noexcept (false);

    int role; // TODO: enum class?
    dl::ident type;
    dl::ident name;

    std::vector< dl::dlis_error > log;

    dl::object_vector& objects() noexcept (false);
private:
    dl::record          record;
    dl::object_vector   objs;
    dl::object_template tmpl;

    void parse() noexcept (true);
    bool parsed = false;

    const char* parse_set_component(const char* cur) noexcept (false);
    const char* parse_template(const char* cur) noexcept (false);
    const char* parse_objects(const char* cur) noexcept (false);
};

struct matcher {
    virtual bool match(const dl::ident& pattern, const dl::ident& candidate)
        const noexcept (false) = 0;

    virtual ~matcher() = default;
};

/* A queryable pool of metadata objects */
class pool {
public:
    explicit pool( std::vector< dl::object_set > e ) : eflrs(std::move(e)) {};

    std::vector< dl::ident > types() const noexcept (true);

    object_vector get(const std::string& type,
                      const std::string& name,
                      const dl::matcher& matcher,
                      const error_handler& errorhandler) noexcept (false);

    object_vector get(const std::string& type,
                      const dl::matcher& matcher,
                      const error_handler& errorhandler) noexcept (false);

private:
    std::vector< dl::object_set > eflrs;
};

} // namespace dlis

#endif //DLISIO_RECORDS_HPP
