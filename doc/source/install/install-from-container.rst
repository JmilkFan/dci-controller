======================
Install from Container
======================


Install from docker container
-----------------------------

#. Build docker image

   .. code-block:: bash

        $ cp ~/workspace/dci-controller/deployment/Dockerfile ~/workspace/
        $ cp ~/workspace/dci-controller/deployment/docker-entrypoint.sh ~/workspace/
        $ cd ~/workspace/
        $ docker image build  -t dci-controller-api:v1.0 .
        # or
        $ docker build --build-arg http_proxy=http://<IP>:<PORT> --build-arg https_proxy=http://<IP>:<PORT> -t dci-controller-api:v1.0 .
   ..


#.  And make a copy of it for further modifications

    .. code-block:: bash

        $ mkdir /etc/dci-controller/
        $ cd ~/workspace/dci-controller/
        $ tox -egenconfig
        $ cp etc/dci-controller/dci-controller.conf.sample /etc/dci-controller/dci-controller.conf
    ..


#.  Edit ``dci-controller.conf`` with your favorite editor. Below is an example
    which contains basic settings you likely need to configure.

    .. code-block:: ini

        [DEFAULT]
        debug = True
        api_workers=2
        api_paste_config=/etc/dci-controller/api-paste.ini
        log_file = /var/log/dci-controller/dci-controller-api.log
        ...

        [database]
        backend = sqlalchemy
        connection = sqlite:////etc/dci-controller/dci-controller.sqlite
    ..


#. Launch docker container by docker-compose

   .. code-block:: bash

        $ yum install docker-compose -y

        $ touch /etc/dci-controller/dci-controller.sqlite
        $ mkdir /var/log/dci-controller/

        $ cd ~/workspace/dci-controller/deployment/
        $ docker-compose -f docker-compose.yml up -d
        $ docker ps
        #docker-compose -f docker-compose.yml down
   ..
