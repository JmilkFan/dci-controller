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
    ..


#.  Run DCI Controller API (via WSGI :doc:`api-uwsgi <../install/config-wsgi>`)

    .. code-block:: console

       dci-controller-api --config-file /etc/dci-controller/dci-controller.conf
    ..
