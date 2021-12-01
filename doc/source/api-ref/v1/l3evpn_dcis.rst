L3 EVPN DCI APIs
----------------

#.  Create

    .. code-block:: console

        curl -i "http://localhost:6699/v1/l3evpn_dcis" \
        -X POST \
        -H 'Content-type: application/json' \
        -H 'Accept: application/json' \
        -d '
        {
          "name": "l3dci-vn-02",
          "east_site_uuid": "298b73fb-ef22-47c7-a7cf-f7476edae7cc",
          "east_site_subnet_cidr": "192.168.100.0/24",
          "west_site_uuid": "9ebbebc2-cf4c-4d1b-852a-ae4a968b68d2",
          "west_site_subnet_cidr": "172.16.100.0/24"
        }
        '
    ..


#. Get one

   .. code-block:: console

        curl -i "http://localhost:6699/v1/l3evpn_dci/{uuid}" \
        -X GET \
        -H 'Content-type: application/json' \
        -H 'Accept: application/json'
   ..


#. Get all

   .. code-block:: console

        curl -i "http://localhost:6699/v1/l3evpn_dcis" \
        -X GET \
        -H 'Content-type: application/json' \
        -H 'Accept: application/json'
   ..


#. Delete

   .. code-block:: console

        curl -i "http://localhost:6699/v1/l3evpn_dcis/{uuid}" \
        -X DELETE \
        -H 'Content-type: application/json' \
        -H 'Accept: application/json'
   ..
