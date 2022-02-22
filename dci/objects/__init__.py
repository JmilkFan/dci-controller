def register_all():
    __import__('dci.objects.site')
    __import__('dci.objects.wan_node')
    __import__('dci.objects.evpn_vpls_over_srv6_be_slicing')
