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

import urllib.parse as urlparse

from sqlalchemy import Column
from sqlalchemy import Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import relationship
from sqlalchemy import String

from oslo_db import options as db_options
from oslo_db.sqlalchemy import models
from oslo_db.sqlalchemy import types as db_types
from oslo_utils import timeutils

from dci.common import constants
from dci.common import paths
from dci.conf import CONF
from dci.db import types


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
    tf_api_server_host = Column(types.IPAddress(), nullable=False)
    tf_api_server_port = Column(Integer, nullable=False)
    tf_username = Column(String(36), nullable=False)
    tf_password = Column(String(36), nullable=False)
    os_auth_url = Column(String(36), nullable=True)
    os_region = Column(String(36), nullable=True)
    os_project_domain_name = Column(String(36), nullable=True)
    os_user_domain_name = Column(String(36), nullable=True)
    os_project_name = Column(String(36), nullable=True)
    os_username = Column(String(36), nullable=True)
    os_password = Column(String(36), nullable=True)
    state = Column(Enum(constants.ACTIVE, constants.INACTIVE), nullable=False)

    wan_nodes = relationship(
        'WANNode',
        lazy='subquery',
        backref='wan_nodes',
        foreign_keys='WANNode.site_uuid',
        primaryjoin='Site.uuid == WANNode.site_uuid')


class WANNode(Base):
    """Represents the WAN Node."""

    __tablename__ = 'wan_nodes'

    uuid = Column(String(36), primary_key=True)
    name = Column(String(36), nullable=True)
    vendor = Column(Enum(constants.HUAWEI), nullable=False)
    netconf_host = Column(types.IPAddress(), nullable=False)
    netconf_port = Column(Integer, nullable=False)
    netconf_username = Column(String(36), nullable=False)
    netconf_password = Column(String(36), nullable=False)
    as_number = Column(Integer, nullable=True)
    roles = Column(db_types.JsonEncodedList, nullable=False)
    site_uuid = Column(String(36), ForeignKey('sites.uuid'))
    state = Column(Enum(constants.ACTIVE, constants.INACTIVE), nullable=False)

    # for EVPN VPLS over SRv6 BE WAN VPN
    preset_evpn_vpls_o_srv6_be_locator_arg = Column(String(36), nullable=False)
    preset_evpn_vpls_o_srv6_be_locator = Column(String(36), nullable=False)

    # for EVPN VxLAN Access VPN
    preset_evpn_vxlan_nve_intf = Column(String(36), nullable=False)
    preset_evpn_vxlan_nve_intf_ipaddr = Column(types.IPAddress(), nullable=False)  # noqa
    preset_evpn_vxlan_nve_peer_ipaddr = Column(types.IPAddress(), nullable=False)  # noqa

    # for VPN splicing
    preset_wan_vpn_bd_intf = Column(String(36), nullable=False)
    preset_access_vpn_bd_intf = Column(String(36), nullable=False)


class EVPNVPLSoSRv6BESlicing(Base):
    """Represents the EVPN VPLS over SRv6 BE network slicing."""

    __tablename__ = 'evpn_vpls_over_srv6_be_slicings'

    uuid = Column(String(36), primary_key=True)
    name = Column(String(36), nullable=False)
    subnet_cidr = Column(types.CIDR(), nullable=False)
    state = Column(Enum(constants.ACTIVE, constants.INACTIVE), nullable=False)

    ###
    # East configuration.
    ##
    east_site_uuid = Column(String(36), nullable=False)

    # DCN VN
    east_dcn_vn_uuid = Column(String(36), nullable=False)
    east_dcn_vn_vni = Column(String(16), nullable=False)
    east_dcn_vn_route_target = Column(String(16), nullable=False)
    east_dcn_vn_subnet_allocation_pool = Column(String(36), nullable=False)

    # Access VPN
    east_access_vpn_vni = Column(String(16), nullable=False)
    east_access_vpn_route_target = Column(String(16), nullable=False)
    east_access_vpn_route_distinguisher = Column(String(16), nullable=False)

    # WAN VPN
    east_wan_vpn_route_target = Column(String(16), nullable=False)
    east_wan_vpn_route_distinguisher = Column(String(16), nullable=False)

    # VPN Splicing
    east_access_vpn_bridge_domain = Column(String(16), nullable=False)
    east_wan_vpn_bridge_domain = Column(String(16), nullable=False)
    east_splicing_vlan_id = Column(String(16), nullable=False)

    ###
    # West configuration.
    ###
    west_site_uuid = Column(String(36), nullable=False)

    # DCN VN
    west_dcn_vn_uuid = Column(String(36), nullable=False)
    west_dcn_vn_vni = Column(String(16), nullable=False)
    west_dcn_vn_route_target = Column(String(16), nullable=False)
    west_dcn_vn_subnet_allocation_pool = Column(String(36), nullable=False)

    # Access VPN
    west_access_vpn_vni = Column(String(16), nullable=False)
    west_access_vpn_route_target = Column(String(16), nullable=False)
    west_access_vpn_route_distinguisher = Column(String(16), nullable=False)

    # WAN VPN
    west_wan_vpn_route_target = Column(String(16), nullable=False)
    west_wan_vpn_route_distinguisher = Column(String(16), nullable=False)

    # VPN Splicing
    west_access_vpn_bridge_domain = Column(String(16), nullable=False)
    west_wan_vpn_bridge_domain = Column(String(16), nullable=False)
    west_splicing_vlan_id = Column(String(16), nullable=False)
