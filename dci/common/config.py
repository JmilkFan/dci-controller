from oslo_config import cfg

from dci import version


def parse_args(argv, default_config_files=None):
    version_string = version.version_info.release_string()
    cfg.CONF(argv[1:],
             project='dci_controller',
             version=version_string,
             default_config_files=default_config_files)
