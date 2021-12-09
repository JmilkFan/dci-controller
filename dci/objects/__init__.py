def register_all():
    __import__('dci.objects.site')
    __import__('dci.objects.l2evpn_dci')
    __import__('dci.objects.l3evpn_dci')
    __import__('dci.objects.wan_node')
    __import__('dci.objects.l3vpn_srv6_slicing')
