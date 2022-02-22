# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

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

from dci.common import constants
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
    tf_api_server_host = Column(String(36), nullable=False)
    tf_api_server_port = Column(Integer, nullable=False)
    tf_username = Column(String(36), nullable=False)
    tf_password = Column(String(36), nullable=False)
    # TODO(fanguiju): Implement openstackclient and check the account infos.
    os_auth_url = Column(String(36), nullable=True)
    os_region = Column(String(36), nullable=True)
    os_project_domain_name = Column(String(36), nullable=True)
    os_user_domain_name = Column(String(36), nullable=True)
    os_project_name = Column(String(36), nullable=True)
    os_username = Column(String(36), nullable=True)
    os_password = Column(String(36), nullable=True)
    state = Column(Enum(constants.ACTIVE, constants.INACTIVE), nullable=False)


class WANNode(Base):
    """Represents the WAN Node."""

    __tablename__ = 'wan_nodes'

    uuid = Column(String(36), primary_key=True)
    name = Column(String(36), nullable=True)
    vendor = Column(Enum(constants.HUAWEI), nullable=False)
    netconf_host = Column(String(36), nullable=False)
    netconf_port = Column(Integer, nullable=False)
    netconf_username = Column(String(36), nullable=False)
    netconf_password = Column(String(36), nullable=False)
    as_number = Column(Integer, nullable=True)
    state = Column(Enum(constants.ACTIVE, constants.INACTIVE), nullable=False)


class EVPNVPLSoSRv6BESlicing(Base):
    """Represents the EVPN VPLS over SRv6 BE network slicing."""

    __tablename__ = 'evpn_vpls_over_srv6_be_slicings'

    uuid = Column(String(36), primary_key=True)
    name = Column(String(36), nullable=False)
    subnet_cidr = Column(String(36), nullable=False)
    state = Column(Enum(constants.ACTIVE, constants.INACTIVE), nullable=False)

    ###
    # East configuration.
    ##
    east_site_uuid = Column(String(36), nullable=False)
    east_wan_node_uuid = Column(String(36), nullable=False)

    # DCN VN
    east_site_vn_uuid = Column(String(36), nullable=False)
    east_site_vn_vni = Column(Integer, nullable=False)
    east_site_route_target = Column(Integer, nullable=False)
    east_site_subnet_allocation_pool = Column(String(36), nullable=False)

    # Access VPN
    east_access_vpn_vni = Column(Integer, nullable=False)
    east_access_vpn_route_target = Column(Integer, nullable=False)
    east_access_vpn_route_distinguisher = Column(Integer, nullable=False)

    # WAN VPN
    east_wan_vpn_route_target = Column(Integer, nullable=False)
    east_wan_vpn_route_distinguisher = Column(Integer, nullable=False)

    # VPN Splicing
    east_access_vpn_bridge_domain = Column(Integer, nullable=False)
    east_wan_vpn_bridge_domain = Column(Integer, nullable=False)
    east_splicing_vlan_id = Column(Integer, nullable=False)

    ###
    # West configuration.
    ###
    west_site_uuid = Column(String(36), nullable=False)
    west_wan_node_uuid = Column(String(36), nullable=False)

    # DCN VN
    west_site_vn_uuid = Column(String(36), nullable=False)
    west_site_subnet_allocation_pool = Column(String(36), nullable=False)
    west_site_vn_vni = Column(Integer, nullable=False)
    west_site_route_target = Column(Integer, nullable=False)

    # Access VPN
    west_access_vpn_vni = Column(Integer, nullable=False)
    west_access_vpn_route_target = Column(Integer, nullable=False)
    west_access_vpn_route_distinguisher = Column(Integer, nullable=False)

    # WAN VPN
    west_wan_vpn_route_target = Column(Integer, nullable=False)
    west_wan_vpn_route_distinguisher = Column(Integer, nullable=False)

    # VPN Splicing
    west_access_vpn_bridge_domain = Column(Integer, nullable=False)
    west_wan_vpn_bridge_domain = Column(Integer, nullable=False)
    west_splicing_vlan_id = Column(Integer, nullable=False)
