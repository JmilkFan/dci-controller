L3 VPN SRv6 Slicing APIs
------------------------

#.  Create

    .. code-block:: console

        curl -i "http://localhost:6699/v1/l3vpn_srv6_slicings" \
        -X POST \
        -H 'Content-type: application/json' \
        -H 'Accept: application/json' \
        -d '
        {
            "name": "slicing02",
            "east_site_uuid": "475e972b-6935-49d3-9960-5adafad2d1b4",
            "east_site_subnet_cidr": "172.16.1.0/24",
            "west_site_uuid": "21864f04-b023-4c76-976c-de738a87bd79",
            "west_site_subnet_cidr": "172.16.2.0/24",
            "routing_type": "be",
            "ingress_node": "4c3ba0a0-257f-4a71-aaf5-289210257c93",
            "egress_node": "3334ec0e-b9a9-4b26-ad1d-85dedd502e49",
            "route_target": "100:200"
        }
        '
    ..


#. Get one

   .. code-block:: console

        curl -i "http://localhost:6699/v1/l3evpn_dci/4788d374-43e6-44ee-a093-57cd89bd3b2f" \
        -X GET \
        -H 'Content-type: application/json' \
        -H 'Accept: application/json'
   ..


#. Get all

   .. code-block:: console

        curl -i "http://localhost:6699/v1/l3vpn_srv6_slicings" \
        -X GET \
        -H 'Content-type: application/json' \
        -H 'Accept: application/json'
   ..


#. Delete

   .. code-block:: console

        curl -i "http://localhost:6699/v1/l3vpn_srv6_slicings/d95a6682-2928-4069-9e52-5147eaeb8785" \
        -X DELETE \
        -H 'Content-type: application/json' \
        -H 'Accept: application/json'
   ..
