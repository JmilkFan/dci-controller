from oslo_utils import importutils


class DCIManager(object):

    def __init__(self, device_driver):
        """Load the driver from the one specified in args, or from flags."""

        self.driver = importutils.import_object(device_driver)
