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
          "tf_project": "project01"
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
         "tf_project": "project01"
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
