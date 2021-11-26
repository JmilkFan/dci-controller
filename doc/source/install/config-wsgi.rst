======================================
Installing DCI Controller API via WSGI
======================================

dci-controller-api service can be run either as a Python command that runs
a web serve or As a WSGI application hosted by uwsgi. This document is a
guide to deploy dci-controller-api using uwsgi.

WSGI Application
----------------

The function ``dci.api.wsgi_app.init_application`` will setup a WSGI
application to run behind uwsgi.

Watcher API behind uwsgi
------------------------

Create a ``dci-controller-api-uwsgi`` file with content below:

.. code-block:: ini

    [uwsgi]
    chmod-socket = 666
    socket = /var/run/uwsgi/dci-controller-wsgi-api.socket
    lazy-apps = true
    add-header = Connection: close
    buffer-size = 65535
    hook-master-start = unix_signal:15 gracefully_kill_them_all
    thunder-lock = true
    plugins = python
    enable-threads = true
    worker-reload-mercy = 90
    exit-on-reload = false
    die-on-term = true
    master = true
    processes = 2
    wsgi-file = /usr/local/bin/dci-controller-wsgi-api

.. end

Start dci-controller-api:

.. code-block:: console

    # uwsgi --ini /etc/dci-controller/dci-controller-api-uwsgi.ini

.. end
