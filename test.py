from jnpr.junos import Device
from jnpr.junos.utils.config import Config

dev = Device(host='172.27.100.253',
             user='root',
             password='1qaz@WSX').open()
with Config(dev, mode='private') as cu:
    # perpare
    bgp_peer_local = '1.1.1.1'
    bgp_peer_remote = '2.2.2.2'
    action = 'delete'
    cu.load('%s policy-options policy-statement send-evpn term 1 from protocol evpn' % action, format='set')
    cu.load('%s policy-options policy-statement send-evpn term 1 then next-hop self' % action, format='set')
    cu.load('%s policy-options policy-statement send-evpn term 1 then accept' % action, format='set')
    cu.load('%s protocols bgp group DCI-EVPN-T5 type internal' % action, format='set')
    cu.load('%s protocols bgp group DCI-EVPN-T5 local-address %s' % (action, bgp_peer_local), format='set')
    cu.load('%s protocols bgp group DCI-EVPN-T5 family evpn signaling' % action, format='set')
    cu.load('%s protocols bgp group DCI-EVPN-T5 export send-evpn' % action, format='set')
    cu.load('%s protocols bgp group DCI-EVPN-T5 local-as 100' % action, format='set')
    cu.load('%s protocols bgp group DCI-EVPN-T5 neighbor %s' % (action, bgp_peer_remote), format='set')
    cu.load('%s protocols bgp group DCI-EVPN-T5 vpn-apply-export' % action, format='set')
    cu.load('%s policy-options policy-statement DCI-EVPN-T5-EXPORT term STATIC from protocol static' % action, format='set')
    cu.load('%s policy-options policy-statement DCI-EVPN-T5-EXPORT term STATIC then accept' % action, format='set')
    #cu.load('%s routing-instances DCI-EVPN-T5-RI-01 protocols evpn ip-prefix-routes advertise direct-nexthop' % action, format='set')
    #cu.load('%s routing-instances DCI-EVPN-T5-RI-01 protocols evpn ip-prefix-routes encapsulation vxlan' % action, format='set')
    #cu.load('%s routing-instances DCI-EVPN-T5-RI-01 protocols evpn ip-prefix-routes vni 100' % action, format='set')
    #cu.load('%s routing-instances DCI-EVPN-T5-RI-01 protocols evpn ip-prefix-routes export DCI-EVPN-T5-EXPORT' % action, format='set')
    cu.load('%s routing-instances DCI-EVPN-T5-RI-01 protocols evpn' % action, format='set')
    cu.load('%s routing-instances DCI-EVPN-T5-RI-01 instance-type vrf' % action, format='set')
    cu.load('%s routing-instances DCI-EVPN-T5-RI-01 route-distinguisher 1.1.1.1:100' % action, format='set')
    cu.load('%s routing-instances DCI-EVPN-T5-RI-01 vrf-target target:100:100' % action, format='set')
    cu.load('%s routing-instances DCI-EVPN-T5-RI-01 vrf-table-label' % action, format='set')
    cu.pdiff()
    cu.commit()
dev.close()
