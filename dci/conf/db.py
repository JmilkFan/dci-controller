from oslo_config import cfg

from dci.common.i18n import _


opts = [
    cfg.StrOpt('url',
               default="redis://@127.0.0.1:6379/0",
               help=_("""
Redis connection URL.

e.g. url = redis://[<username>:][<password>]@127.0.0.1:6379/dci_controller
                      """)),
]

opt_group = cfg.OptGroup(name='redis',
                         title='Options for the Redis DB.')

DB_OPTS = (opts)


def register_opts(conf):
    conf.register_group(opt_group)
    conf.register_opts(opts, group=opt_group)


def list_opts():
    return {
        opt_group: DB_OPTS
    }
