from oslo_config import cfg

from dci.common.i18n import _


opts = [
    cfg.StrOpt('mysql_engine',
               default='InnoDB',
               help=_('MySQL engine to use.'))
]

opt_group = cfg.OptGroup(name='database',
                         title='Options for the database service')


def register_opts(conf):
    conf.register_opts(opts, group=opt_group)


DB_OPTS = (opts)


def list_opts():
    return {
        opt_group: DB_OPTS
    }
