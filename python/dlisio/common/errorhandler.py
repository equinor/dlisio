from enum import Enum
from dlisio import core

import logging
log = logging.getLogger(__name__)

class Actions(Enum):
    """
    Actions available for various specification violations
    """
    LOG_DEBUG   = lambda msg: log.debug(msg)
    """logging.debug"""
    LOG_INFO    = lambda msg: log.info(msg)
    """logging.info"""
    LOG_WARNING = lambda msg: log.warning(msg)
    """logging.warning"""
    LOG_ERROR   = lambda msg: log.error(msg)
    """logging.error"""
    RAISE       = lambda msg: ErrorHandler.raise_msg(msg)
    """raise RuntimeError"""
    SWALLOW     = lambda msg: ErrorHandler.swallow(msg)
    """pass"""

    def __init__(self, handle):
        self.handle = handle

class ErrorHandler(core.error_handler):
    """ Defines rules about error handling

    Many .dlis files happen to be not compliant with specification or simply
    broken. This class gives user some control over handling of such files.

    When dlisio encounters a specification violation, it categories the issue
    based on the severity of the violation. Some issues are easy to ignore
    while other might force dlisio to give up on its current task.
    ErrorHandler supplies an interface for changing how dlisio reacts to
    different violation in the file.

    Different categories are *info*, *minor*, *major* and *critical*:

    ======== ===================================================================
    Severity Description
    ======== ===================================================================
    critical Any issue that forces dlisio stop its current objective prematurely
             is categorised as critical.

             By default a critical error raises a RuntimeError.

             An example would be file indexing, which happens at load. Suppose
             the indexing fails midways through the file. There is no way for
             dlisio to reliably keep indexing the file.
             However, it is likely that the file is readable up until the point
             of failure. Changing the behaviour of critical from raising an
             Exception to logging would in this case mean that a partially
             indexed file is returned by load.
    major    Result of a direct specification violation in the file. dlisio
             makes an assumption about what broken information [1] should have
             been and continues parsing the file on this assumption.
             If no other major or critical issues are reported, it's likely that
             assumption was correct and that dlisio parsed the file correctly.
             However, no guarantees can be made.

             By default a warning is logged.

             [1] Note that "information" in this case refers to the data in the
             file that tells dlisio how the file should be parsed, not to the
             actual parsed data.

    minor    Like Major issues, this is also a result of a direct specification
             violation. dlisio makes similar assumptions to keep parsing the
             file. Minor issues are generally less severe and, in contrast to
             major issues, are more likely to be handled correctly.
             However, still no guarantees can be made about the parsed data.

             By default an info message is logged.
    info     Issue doesn't contradict specification, but situation is peculiar.

             By default a debug message is logged.

    ======== ===================================================================

    ErrorHandler only applies to issues related to parsing information from the
    file. These are issues that otherwise would force dlisio to fail, such as
    direct violations of the RP66v1 specification.
    It does not apply to inconsistencies and issues in the parsed data.
    This means that cases where dlisio enforces behaviour of the parsed data,
    such as object-to-object references, are out of scope for the ErrorHandler.

    Please also note that ErrorHandler doesn't redefine issues categories, it
    only changes default behavior.

    Attributes
    ----------
    info:
        Action for merely information message

    minor:
        Action for minor specification violation

    major:
        Action for major specification violation

    critical:
        Action for critical specification violation


    Warnings
    --------
    Escaping errors is a good solution when user needs to read as much data as
    possible, for example, to have a general overview over the file. However
    user must be careful when using this mode during close inspection.
    If user decides to accept errors, they must be aware that some returned data
    will be spoiled. Most likely it will be data which is stored in the file
    near the failure.

    Warnings
    --------
    Be careful not to ignore too much information when investigating files.
    If you want to debug a broken part of the file, you should look at all
    issues to get a full picture of the situation.

    Examples
    --------
    Define your own rules:

    >>> from dlisio.common import ErrorHandler, Actions
    >>> def myhandler(msg):
    ...     logging.getLogger('custom').info("error in dlisio")
    ...     raise RuntimeError("Custom handler: " + msg)
    >>> errorhandler = ErrorHandler(
    ...     info     = Actions.SWALLOW,
    ...     minor    = Actions.LOG_WARNING,
    ...     major    = Actions.RAISE,
    ...     critical = myhandler)

    Parse a file:

    >>> from dlisio import dlis
    >>> files = dlis.load(path)
    RuntimeError: "...."
    >>> handler = ErrorHandler(critical=Actions.LOG_ERROR)
    >>> files = dlis.load(path, error_handler=handler)
    [ERROR] "...."
    >>> for f in files:
    ...  pass

    """
    @staticmethod
    def raise_msg(msg):
        raise RuntimeError(msg)

    @staticmethod
    def swallow(msg):
        pass

    def __init__(self, info     = Actions.LOG_DEBUG,
                       minor    = Actions.LOG_INFO,
                       major    = Actions.LOG_WARNING,
                       critical = Actions.RAISE):

        core.error_handler.__init__(self)

        self.info     = info
        self.minor    = minor
        self.major    = major
        self.critical = critical

    def log(self, severity, context='', problem='', spec='', action='', debug=''):
        msg = ErrorHandler.format_error(
            severity, context, problem, spec, action, debug)

        """ Overrides dl::error_handler::log """
        if   severity == core.error_severity.info:     handler = self.info
        elif severity == core.error_severity.minor:    handler = self.minor
        elif severity == core.error_severity.major:    handler = self.major
        elif severity == core.error_severity.critical: handler = self.critical
        else:
            err='Unknown error severity. Original msg was: {}'
            raise RuntimeError(err.format(msg))

        handler(msg)

    @staticmethod
    def format_severity(severity):
        if   severity == core.error_severity.info:     return "info"
        elif severity == core.error_severity.minor:    return "minor"
        elif severity == core.error_severity.major:    return "major"
        elif severity == core.error_severity.critical: return "critical"
        else:                                          return severity

    # TODO: check if that helps for named fileheader issue
    # TODO: nested format
    @staticmethod
    def format_error(severity, context, problem, spec, action, debug):
        format = '\n{:<{align}} {}'
        severity = ErrorHandler.format_severity(severity)

        problem  = format.format('Problem:',  problem,  align=13)
        context  = format.format('Where:',    context,  align=13)
        severity = format.format('Severity:', severity, align=13)

        if spec:
            spec = format.format('RP66V1 ref:', spec, align=13)

        if action:
            action = format.format('Action taken:', action, align=13)

        if debug:
            debug = format.format("Debug info:", debug, align=13)

        msg = "{}{}{}{}{}{}"
        return msg.format(problem, context, severity, spec, action, debug)
