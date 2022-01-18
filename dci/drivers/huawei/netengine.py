"""
Driver for HUAWEI NetEngine.
"""

from dci import driver


class NetEngineDriver(driver.DeviceDriver):
    """Executes commands relating to HUAWEI NetEngine Driver."""

    def __init__(self, *args, **kwargs):
        super(NetEngineDriver, self).__init__(*args, **kwargs)
