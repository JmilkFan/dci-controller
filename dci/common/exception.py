from http import HTTPStatus
import six
from six.moves import http_client

from oslo_log import log

from dci.common.i18n import _
from dci.conf import CONF


LOG = log.getLogger(__name__)


class DCIException(Exception):
    """Base DCI Controller Exception

    To correctly use this class, inherit from it and define
    a '_msg_fmt' property. That message will get printf'd
    with the keyword arguments provided to the constructor.

    If you need to access the message from an exception you should use
    six.text_type(exc)

    """
    _msg_fmt = _("An unknown exception occurred.")
    code = http_client.INTERNAL_SERVER_ERROR
    headers = {}
    safe = False

    def __init__(self, message=None, **kwargs):
        self.kwargs = kwargs

        if 'code' not in self.kwargs:
            try:
                self.kwargs['code'] = self.code
            except AttributeError:
                pass

        if not message:
            try:
                message = self._msg_fmt % kwargs
            except Exception:
                # kwargs doesn't match a variable in self._msg_fmt
                # log the issue and the kwargs
                LOG.exception('Exception in string format operation')
                for name, value in kwargs.items():
                    LOG.error("%(name)s: %(value)s",
                              {"name": name, "value": value})

                if CONF.fatal_exception_format_errors:
                    raise
                else:
                    # at least get the core self._msg_fmt out if something
                    # happened
                    message = self._msg_fmt

        super(DCIException, self).__init__(message)

    @property
    def message(self):
        return self.__str__()

    def __str__(self):
        """Encode to utf-8 then wsme api can consume it as well."""
        if not six.PY3:
            return six.text_type(self.args[0]).encode('utf-8')

        return self.args[0]

    def __unicode__(self):
        """Return a unicode representation of the exception message."""
        return six.text_type(self.args[0])


class Forbidden(DCIException):
    _msg_fmt = _("Forbidden")
    code = http_client.FORBIDDEN


class Conflict(DCIException):
    _msg_fmt = _('Conflict.')
    code = http_client.CONFLICT


class Invalid(DCIException):
    _msg_fmt = _("Invalid parameters.")
    code = http_client.BAD_REQUEST


class ConfigInvalid(DCIException):
    _msg_fmt = _("Invalid configuration. %(msg)s")


class InvalidAPIResponse(Invalid):
    _msg_fmt = _('Bad API response from %(service)s for %(api)s API. '
                 'Details: %(msg)s')


class CapabilityNotSupported(DCIException):
    _msg_fmt = _("%(msg)s")


class InvalidAPIRequest(Invalid):
    _msg_fmt = _("%(msg)s")


class ValidationError(Exception):
    pass


class ConnectionRefused(Exception):
    pass


class HTTPBadRequest(DCIException):
    _msg_fmt = _("%(explanation)s")


class DBOperationException(DCIException):
    _msg_fmt = _("%(msg)s")


# Cannot be templated as the error syntax varies.
# msg needs to be constructed when raised.
class InvalidParameterValue(Invalid):
    _msg_fmt = _("%(err)s")


class NotFound(DCIException):
    _msg_fmt = _("Resource could not be found.")
    code = HTTPStatus.NOT_FOUND


class ResourceNotFound(NotFound):
    _msg_fmt = _("%(resource)s not found %(msg)s")


class RecordAlreadyExists(DCIException):
    _msg_fmt = _("Database record with uuid %(uuid)s already exists.")


class MXDeviceNotConnected(DCIException):
    _msg_fmt = _("Not connected to MX device %(name)s.")


class SSHCLIExecutionError(DCIException):
    _msg_fmt = _("SSHCLI execution error, please check the outputs or "
                 "netmiko session_log file /tmp/netmiko_session_log.txt.")


class L3VPNSRv6SlicingError(DCIException):
    _msg_fmt = _("%(err)s")
