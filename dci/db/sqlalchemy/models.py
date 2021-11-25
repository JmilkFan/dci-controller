"""SQLAlchemy models for accelerator service."""

from oslo_db import options as db_options
from oslo_db.sqlalchemy import models
from oslo_utils import timeutils
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import orm
from sqlalchemy import schema
from sqlalchemy import String
from sqlalchemy import Text
import urllib.parse as urlparse

from dci.common import paths
from dci.conf import CONF


_DEFAULT_SQL_CONNECTION = 'sqlite:///' + paths.state_path_def('dci-controller.sqlite')  # noqa
db_options.set_defaults(CONF, connection=_DEFAULT_SQL_CONNECTION)


def table_args():
    engine_name = urlparse.urlparse(CONF.database.connection).scheme
    if engine_name == 'mysql':
        return {'mysql_engine': CONF.database.mysql_engine,
                'mysql_charset': "utf8"}
    return None


class DCIBase(models.TimestampMixin, models.ModelBase):
    metadata = None

    def as_dict(self):
        d = {}
        for c in self.__table__.columns:
            d[c.name] = self[c.name]
        return d

    @staticmethod
    def delete_values():
        return {'deleted': True,
                'deleted_at': timeutils.utcnow()}

    def delete(self, session):
        """Delete this object."""
        updated_values = self.delete_values()
        self.update(updated_values)
        self.save(session=session)
        return updated_values


Base = declarative_base(cls=DCIBase)


class Site(Base):
    """Represents the DCI sites."""

    __tablename__ = 'sites'

    uuid = Column(String(36), primary_key=True)
    name = Column(String(36), nullable=True)
    netconf_host = Column(String(36), nullable=False)
    netconf_username = Column(String(36), nullable=False)
    netconf_password = Column(String(36), nullable=False)
    state = Column(Enum('active', 'inactive'), nullable=False)
