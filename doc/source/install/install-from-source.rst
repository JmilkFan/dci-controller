==================================
Install DCI Controller from Source
==================================

This section describes how to install and configure the DCI Controller API
Service for CentOS7.x from source code.

* Operating System: CentOS7.x
* Programing Language: Python3


Install from git repository
----------------------------

#.  Installation environment dependency.

    .. code-block:: console

        yum install python3-devel -y
        yum install gcc -y
    ..


#.  Clone the dci-Controller git repository to the management server.

    .. code-block:: console

        cd ~/workspace/
        git clone https://github.com/JmilkFan/dci-controller.git
    ..

#.  Set up the dci-controller-api config file

    First, generate a sample configuration file, using tox

    .. code-block:: console

        cd ~/workspace/dci-controller
        tox -e genconfig
    ..

    And make a copy of it for further modifications

    .. code-block:: console

        cp -r ~/workspace/dci-controller/etc/dci-controller/ /etc
        cd /etc/dci-controller/
        ln -s dci-controller.conf.sample dci-controller.conf
    ..

#.  Install DCI Controller packages.

    .. code-block:: console

        cd ~/workspace/dci-controller
        pip3 install -r requirements.txt -e .
    ..

#.  Generate project documents.

    .. code-block:: console

        tox -edocs
    ..

#.  Generate API documents.

    .. code-block:: console

        tox -eapi-ref
    ..


.. include:: common.rst
