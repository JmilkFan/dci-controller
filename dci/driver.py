"""Device Drivers for networking."""


import abc


class BaseDeviceDriver(object, metaclass=abc.ABCMeta):

    def __init__(self, *args, **kwargs):
        self.vendor = None
        self.model = None
        self.version = None

        self._initialized = False
        self.connection_info = {}

    @property
    def is_initialized(self):
        return self._initialized

    @abc.abstractmethod
    def liveness(self):
        """Connectivity check of network device.
        """
        return

    @abc.abstractmethod
    def set_initialized(self):
        """Initialize network device.
        """
        return


class SRv6VPNDeviceDriver(object, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def create_l3vpnv4_over_srv6_be(self):
        return


class DeviceDriver(SRv6VPNDeviceDriver, BaseDeviceDriver):

    def liveness(self):
        raise NotImplementedError()

    def set_initialized(self):
        raise NotImplementedError()

    def create_l3vpnv4_over_srv6_be(self):
        raise NotImplementedError()
