===================
Install from Source
===================

This section describes how to install and configure the DCI Controller API
Service for CentOS7.x from source code.

* Operating System: CentOS7.x
* Programing Language: Python3


Install from git repository
----------------------------

#.  Installation.

    .. code-block:: bash

        # YUM
        yum install -y epel-release
        yum install -y git
        yum install -y gcc
        yum install -y gcc-c++
        yum install -y make
        yum install -y scons
        yum install -y python-pip
        yum install -y python-devel
        yum install -y python3
        yum install -y python3-devel

        # PyPI
        pip2 install future==0.18.2
        pip2 install lxml==4.6.4
        pip2 install pathlib2==2.3.6
        pip2 install PyYAML==5.4.1
        pip3 install -U pip==21.3.1 setuptools==57.5.0
        pip3 install future==0.18.2
        pip3 install sphinx==4.3.0
        pip3 install tox==3.24.4

        # tf-api-client
        $ git clone https://github.com/tungstenfabric/tf-api-client.git -b R2011 /opt/tf-api-client/
        $ cd /opt/tf-api-client/
        $ scons --target=x86_64
        $ cd /opt/tf-api-client/build/debug/api-lib/
        $ pip3 install -r requirements.txt
        $ python3 setup.py install
        $ cd doc/source
        $ make html

        # dci-controller
        $ git clone https://github.com/JmilkFan/dci-controller.git ~/workspace/dci-controller/
        $ cd ~/workspace/dci-controller/
        $ pip3 install -r requirements.txt -e .
    ..
