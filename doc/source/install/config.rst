========================
Configure DCI Controller
========================


Configure dci-controller-api Service
------------------------------------


#.  Generate the dci-controller-api config file

    First, generate a sample configuration file, using tox

    .. code-block:: bash

        cd ~/workspace/dci-controller/ && tox -egenconfig
    ..


#.  And make a copy of it for further modifications

    .. code-block:: bash

        cp etc/dci-controller/dci-controller.conf.sample etc/dci-controller/dci-controller.conf
    ..


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


#.  Upgrade DB migrations  can be performed by (for backward compatibility):

    .. code-block:: ini

        dci-controller-dbsync --config-file etc/dci-controller/dci-controller.conf upgrade

    ..


#.  Run dci-controller-api Service (via WSGI :doc:`api-uwsgi <../install/deploy-via-wsgi>`)

    .. code-block:: bash

        cd ~/workspace/dci-controller/ && dci-controller-api --config-dir etc/dci-controller
    ..


#.  NOTE: To initialization alembic migrations use (Developer mode):

    .. code-block:: ini

        dci-controller-dbsync --config-file etc/dci-controller/dci-controller.conf revision --message "initdb" --autogenerate
    ..
