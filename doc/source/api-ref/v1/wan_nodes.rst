WAN Node APIs
-------------

#.  Create

    .. code-block:: console

        curl -i "http://localhost:6699/v1/wan_nodes" \
        -X POST \
        -H 'Content-type: application/json' \
        -H 'Accept: application/json' \
        -d '
        {
          "name": "wan_node1",
          "ssh_host": "192.168.30.2",
          "ssh_port": 22,
          "ssh_username": "username",
          "ssh_password": "1qaz@WSX",
          "as_number": 100
        }
        '
    ..


#. Update

   .. code-block:: console

        curl -i "http://localhost:6699/v1/wan_nodes/56ba33cc-ee19-4eeb-b4b3-6d0f9faa92e1" \
        -X PUT \
        -H 'Content-type: application/json' \
        -H 'Accept: application/json' \
        -d '
        {
          "name": "site3",
          "ssh_host": "10.33.70.13",
          "ssh_port": 65535,
          "ssh_username": "root",
          "ssh_password": "1qaz@WSX"
        }
        '
   ..


#. Get one

   .. code-block:: console

        curl -i "http://localhost:6699/v1/wan_nodes/31dbaae2-1bbd-44e3-b42f-2c915d88495b" \
        -X GET \
        -H 'Content-type: application/json' \
        -H 'Accept: application/json'
   ..


#. Get all

   .. code-block:: console

        curl -i "http://localhost:6699/v1/wan_nodes" \
        -X GET \
        -H 'Content-type: application/json' \
        -H 'Accept: application/json'
   ..


#. Delete

   .. code-block:: console

        curl -i "http://localhost:6699/v1/wan_nodes/d5fa50f4-87a7-4345-86c0-abd762282da5" \
        -X DELETE \
        -H 'Content-type: application/json' \
        -H 'Accept: application/json'
   ..
