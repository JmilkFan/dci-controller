from oslo_config import cfg

from dci.conf import api
from dci.conf import db

CONF = cfg.CONF

api.register_opts(CONF)
db.register_opts(CONF)
