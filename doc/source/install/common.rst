Configure DCI Controller
------------------------

#.  Edit ``dci-controller.conf`` with your favorite editor. Below is an example
    which contains basic settings you likely need to configure.

    .. code-block:: ini

        [DEFAULT]
        debug = True
        api_workers=1
        api_paste_config=/etc/dci-controller/api-paste.ini
        ...

        [database]
        backend = sqlalchemy
        connection = sqlite:///dci-controller.sqlite
    ..


#.  To create alembic migrations use:

    .. code-block:: ini

        dci-controller-dbsync --config-file etc/dci-controller/dci-controller.conf revision --message "initdb" --autogenerate

    ..


#.  Upgrade can be performed by:

    .. code-block:: ini

        dci-controller-dbsync - for backward compatibility
        dci-controller-dbsync --config-file etc/dci-controller/dci-controller.conf upgrade
        dci-controller-dbsync upgrade --revision head

    ..

#.  Stamp db with most recent migration version, without actually running
    migrations:

    .. code-block:: ini

        dci-controller-dbsync stamp --revision head

    ..


#.  Run DCI Controller API (via WSGI :doc:`api-uwsgi <../install/config-wsgi>`)

    .. code-block:: console

       dci-controller-api --config-file /etc/dci-controller/dci-controller.conf
    ..
