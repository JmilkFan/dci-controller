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

from vnc_api import exceptions as vnc_api_exceptions
from vnc_api import vnc_api

from oslo_log import log

from dci.common.i18n import _LE
from dci.common.i18n import _LI
from dci.common.i18n import _LW


LOG = log.getLogger(__name__)


TF_DEFAULT_DOMAIN = 'default-domain'
TF_DEFAULT_IPAM = 'dci-controller-default-ipam'
TF_DEFAULT_ROUTR_TARGET = 'target:100:100'


class Client(object):
    """Tungsten Fabric client by VNC API Client.
    """

    def __init__(self, host, port, username, password, project):

        self.project_name = project

        self.client = None
        if not self.client:
            self._connect(host, port, username, password, project)

        # NOTE(fanguiju): Use the special IPAM dci-controller-default-ipam.
        self.ipam_o = None
        try:
            self.ipam_o = self.client.network_ipam_read(
                fq_name=[TF_DEFAULT_DOMAIN,
                         project,
                         TF_DEFAULT_IPAM])
        except vnc_api_exceptions.NoIdError:
            LOG.info(_LI("Initialization default IPAM "
                         "[dci-controller-default-ipam.]"))
            self._create_default_ipam_with_user_defined_subnet()

    def _connect(self, host, port, username, password, project):
        try:
            self.client = vnc_api.VncApi(api_server_host=host,
                                         api_server_port=port,
                                         username=username,
                                         password=password,
                                         tenant_name=project)
        except Exception as err:
            LOG.error(_LE("Failed to connect Tungsten Fabric VNC API "
                          "Server [%(host)s], details %(err)s"),
                      {'host': host, 'err': err})
            raise err

    def _get_default_project_obj(self):
        try:
            project_o = self.client.project_read(fq_name=[TF_DEFAULT_DOMAIN,
                                                          self.project_name])
        except vnc_api_exceptions.NoIdError as err:
            LOG.error(_LE("Failedto get default project [%(project)s], "
                          "details %(err)s"),
                      {'project': TF_DEFAULT_DOMAIN + ':' + self.project_name,
                       'err': err})
            raise err
        return project_o

    def _create_default_ipam_with_user_defined_subnet(self):

        project_o = self._get_default_project_obj()

        # Network IPAM Type
        ipam_t = vnc_api.IpamType(ipam_method='dhcp')

        # Create Network IPAM Object
        ipam_o = vnc_api.NetworkIpam(name=TF_DEFAULT_IPAM,
                                     parent_obj=project_o,
                                     network_ipam_mgmt=ipam_t,
                                     ipam_subnet_method='user-defined-subnet')

        LOG.info(_LI("create default IPAM [%s]"), TF_DEFAULT_IPAM)
        ipam_uuid = self.client.network_ipam_create(ipam_o)
        self.ipam_o = self.client.network_ipam_read(id=ipam_uuid)

    def _get_subnet_type(self, subnet_cidr):
        prefix, prefix_len = subnet_cidr.split('/')
        subnet_t = vnc_api.SubnetType(ip_prefix=prefix,
                                      ip_prefix_len=int(prefix_len))
        return subnet_t

    def create_virtal_network_with_user_defined_subnet(
            self, vn_name, subnet_cidr, subnet_allocation_pool=None,
            route_target=None, forwarding_mode='l2_l3'):
        project_o = self._get_default_project_obj()

        # Create user defined Subnet Type for Virtual Network.
        subnet_t = self._get_subnet_type(subnet_cidr)
        if subnet_allocation_pool:
            start_ip, end_ip = subnet_allocation_pool.split(',')
            allocation_pools_t = vnc_api.AllocationPoolType(
                start=start_ip,
                end=end_ip,
                vrouter_specific_pool=True)
            ipam_subnet_t = vnc_api.IpamSubnetType(
                subnet=subnet_t,
                allocation_pools=[allocation_pools_t])
        else:
            ipam_subnet_t = vnc_api.IpamSubnetType(subnet=subnet_t)
        vn_subnet_t = vnc_api.VnSubnetsType(ipam_subnets=[ipam_subnet_t])

        # Creste Virtual Network Type
        # NOTE(fanguiju): Alway use `automatic` vxlan_network_identifier_mode.
        vn_t = vnc_api.VirtualNetworkType(forwarding_mode=forwarding_mode)

        # Create Route Target List Type, use default route target.
        if route_target:
            route_target_list_t = vnc_api.RouteTargetList(
                route_target=[route_target])
        else:
            # NOTE(fanguiju): L3 EVPN VLAN only use the default route target.
            route_target_list_t = vnc_api.RouteTargetList(
                route_target=[TF_DEFAULT_ROUTR_TARGET])

        # Create Virtual Network
        LOG.info(_LI("create virtual network [%s]"), vn_name)
        vn_o = vnc_api.VirtualNetwork(name=vn_name,
                                      parent_obj=project_o,
                                      virtual_network_properties=vn_t,
                                      address_allocation_mode='user-defined-subnet-only',  # noqa
                                      route_target_list=route_target_list_t)
        vn_o.set_network_ipam(ref_obj=self.ipam_o, ref_data=vn_subnet_t)
        vn_uuid = self.client.virtual_network_create(vn_o)
        return vn_uuid

    def get_virtual_network_obj(self, vn_uuid):
        try:
            vn_o = self.client.virtual_network_read(id=vn_uuid)
        except vnc_api_exceptions.NoIdError as err:
            LOG.error(_LE("Failed to get virtual network [%(id)s], "
                          "deails %(err)s"),
                      {'id': vn_uuid, 'err': err})
            raise err
        return vn_o

    def get_virtual_network_vni(self, vn_uuid):
        vn_o = self.get_virtual_network_obj(vn_uuid)
        # NOTE(fanguiju): In different modes, TF will use different VNI !!
        #
        #   if VxLAN Identifier Mode == User Configured:
        #       vni = VirtualNetworkObject.virtual_network_properties.\
        #           vxlan_network_identifier
        #   else VxLAN Identifier Mode == Auto Configured:
        #       vni = VirtualNetworkObject.virtual_network_network_id
        vni = vn_o.virtual_network_network_id
        return vni

    def get_virtual_network_obj_by_name(self, vn_name):
        try:
            vn_o = self.client.virtual_network_read(
                fq_name=[TF_DEFAULT_DOMAIN, self.project_name, vn_name])
        except vnc_api_exceptions.NoIdError as err:
            LOG.error(_LE("Failed to get virtual network [%(name)s], "
                          "deails %(err)s"),
                      {'name': vn_name, 'err': err})
            raise err
        return vn_o

    def delete_virtual_network(self, vn_name):
        LOG.info(_LI("delete virtual network [%s]"), vn_name)
        try:
            self.client.virtual_network_delete(
                fq_name=[TF_DEFAULT_DOMAIN, self.project_name, vn_name])
        except vnc_api_exceptions.NoIdError:
            LOG.warning(_LW("Failed to delete virtual network [%s], "
                            "not found."), vn_name)
        except vnc_api_exceptions.RefsExistError as err:
            LOG.error(_LE("Failed to delete virtual network [%(name)s], "
                          "details %(err)s"),
                      {'name': vn_name, 'err': err})
            raise err

    def retry_to_delete_virtual_network(self, vn_name):
        retry = 3
        while retry:
            try:
                self.delete_virtual_network(vn_name)
                break
            except vnc_api_exceptions.RefsExistError as err:
                # NODE(fanguiju): Just only raise the RefsExistError exception.
                raise err
            except Exception as err:
                LOG.error(_LE("Failed to delete virtual network, "
                              "retry count [-%(cnt)s], details %(err)s"),
                          {'cnt': retry, 'err': err})
                retry -= 1
