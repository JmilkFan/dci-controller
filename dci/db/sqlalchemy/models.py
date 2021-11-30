"""SQLAlchemy models for accelerator service."""

from oslo_db import options as db_options
from oslo_db.sqlalchemy import models
from oslo_utils import timeutils
from sqlalchemy import Column
from sqlalchemy import Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer
from sqlalchemy import String
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
    netconf_port = Column(Integer, nullable=True)
    netconf_username = Column(String(36), nullable=False)
    netconf_password = Column(String(36), nullable=False)
    tf_api_server_host = Column(String(36), nullable=False)
    tf_api_server_port = Column(Integer, nullable=True)
    tf_username = Column(String(36), nullable=False)
    tf_password = Column(String(36), nullable=False)
    tf_project = Column(String(36), nullable=True)
    state = Column(Enum('active', 'inactive'), nullable=False)


class L3EVPNDCI(Base):
    """Represents the L3 EVPN DCI."""

    __tablename__ = 'l3_evpn_dcis'

    uuid = Column(String(36), primary_key=True)
    name = Column(String(36), nullable=True)
    # TODO(fanguiju): Associate to sites table, and use SQL Association query.
    east_site_uuid = Column(String(36), nullable=False)
    west_site_uuid = Column(String(36), nullable=False)
    east_site_subnet_cidr = Column(String(36), nullable=False)
    west_site_subnet_cidr = Column(String(36), nullable=False)
    state = Column(Enum('active', 'inactive'), nullable=False)


class L2EVPNDCI(Base):
    """Represents the L2 EVPN DCI."""

    __tablename__ = 'l2_evpn_dcis'

    uuid = Column(String(36), primary_key=True)
    name = Column(String(36), nullable=True)
    east_site_uuid = Column(String(36), nullable=False)
    west_site_uuid = Column(String(36), nullable=False)
    subnet_cidr = Column(String(36), nullable=False)
    east_site_subnet_allocation_pool = Column(String(36), nullable=False)
    west_site_subnet_allocation_pool = Column(String(36), nullable=False)
    vn_route_target = Column(String(36), nullable=False)
    inter_vlan_id = Column(Integer, nullable=False)
    dci_vni = Column(Integer, nullable=False)
    state = Column(Enum('active', 'inactive'), nullable=False)
