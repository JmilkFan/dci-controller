Sites APIs
----------

#.  Create

    .. code-block:: console

        curl -i "http://localhost:6699/v1/sites" \
        -X POST \
        -H 'Content-type: application/json' \
        -H 'Accept: application/json' \
        -d '
        {
          "name": "site1",
          "netconf_host": "10.33.70.3",
          "netconf_port": 65535,
          "netconf_username": "root",
          "netconf_password": "1qaz@WSX",
          "tf_api_server_host": "10.33.70.1",
          "tf_username": "admin",
          "tf_password": "1qaz@WSX",
          "os_auth_url": "http://10.33.70.1:35357/v3",
          "os_region": "RegionOne",
          "os_project_domain_name": "Default",
          "os_user_domain_name": "Default",
          "os_project_name": "project01",
          "os_username": "admin",
          "os_password": "1qaz@WSX"
        }
        '
    ..


#. Update

   .. code-block:: console

       curl -i "http://localhost:6699/v1/sites/{uuid}" \
       -X PUT \
       -H 'Content-type: application/json' \
       -H 'Accept: application/json' \
       -d '
        {
          "name": "site1",
          "netconf_host": "10.33.70.3",
          "netconf_port": 65535,
          "netconf_username": "root",
          "netconf_password": "1qaz@WSX",
          "tf_api_server_host": "10.33.70.1",
          "tf_username": "admin",
          "tf_password": "1qaz@WSX",
          "os_auth_url": "http://10.33.70.1:35357/v3",
          "os_region": "RegionOne",
          "os_project_domain_name": "Default",
          "os_user_domain_name": "Default",
          "os_project_name": "admin",
          "os_username": "admin",
          "os_password": "1qaz@WSX"
        }
       '
   ..


#. Get one

   .. code-block:: console

        curl -i "http://localhost:6699/v1/sites/{uuid}" \
        -X GET \
        -H 'Content-type: application/json' \
        -H 'Accept: application/json'
   ..


#. Get all

   .. code-block:: console

        curl -i "http://localhost:6699/v1/sites" \
        -X GET \
        -H 'Content-type: application/json' \
        -H 'Accept: application/json'
   ..


#. Delete

   .. code-block:: console

        curl -i "http://localhost:6699/v1/sites/{uuid}" \
        -X DELETE \
        -H 'Content-type: application/json' \
        -H 'Accept: application/json'
   ..
