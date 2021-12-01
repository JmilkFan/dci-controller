L2 EVPN DCI APIs
----------------

#.  Create

    .. code-block:: console

        curl -i "http://localhost:6699/v1/l2evpn_dcis" \
        -X POST \
        -H 'Content-type: application/json' \
        -H 'Accept: application/json' \
        -d '
        {
          "name": "l2dci-vn-03",
          "east_site_uuid": "5fd5b64c-fc38-40a6-a0f8-3918ae8f479b",
          "west_site_uuid": "8aebaf82-17e5-4769-b918-906019df2b12",
          "subnet_cidr": "192.168.200.0/24",
          "east_site_subnet_allocation_pool": "192.168.200.3,192.168.200.100",
          "west_site_subnet_allocation_pool": "192.168.200.101,192.168.200.200"
        }
        '
    ..


#. Get one

   .. code-block:: console

        curl -i "http://localhost:6699/v1/l2evpn_dci/{uuid}" \
        -X GET \
        -H 'Content-type: application/json' \
        -H 'Accept: application/json'
   ..


#. Get all

   .. code-block:: console

        curl -i "http://localhost:6699/v1/l2evpn_dcis" \
        -X GET \
        -H 'Content-type: application/json' \
        -H 'Accept: application/json'
   ..


#. Delete

   .. code-block:: console

        curl -i "http://localhost:6699/v1/l2evpn_dcis/{uuid}" \
        -X DELETE \
        -H 'Content-type: application/json' \
        -H 'Accept: application/json'
   ..
