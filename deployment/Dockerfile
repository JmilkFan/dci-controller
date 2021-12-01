FROM centos:centos7.9.2009

MAINTAINER fanguiju

## YUM
RUN yum install -y epel-release git gcc gcc-c++ make
RUN yum install -y scons
RUN yum install -y python-pip python-devel
RUN yum install -y python3 python3-devel

## PyPI
# scons requirements
RUN pip2 install future==0.18.2
RUN pip2 install lxml==4.6.4
RUN pip2 install pathlib2==2.3.6
RUN pip2 install pyyaml==5.4.1
# dci-controller requirements
RUN pip3 install -U pip==21.3.1 setuptools==57.5.0

# tf-api-client
RUN git clone https://github.com/tungstenfabric/tf-api-client.git -b R2011 /opt/tf-api-client/
WORKDIR /opt/tf-api-client/
RUN scons --target=x86_64
WORKDIR /opt/tf-api-client/build/debug/api-lib/
RUN pip3 install -r requirements.txt
RUN python3 setup.py install

# dci-controller
ENV DCI_C_SRC=/opt/dci-controller/
RUN mkdir $DCI_C_SRC
COPY ./dci-controller/ $DCI_C_SRC
WORKDIR $DCI_C_SRC
RUN pip3 install -r requirements.txt
RUN python3 setup.py install
RUN cp -r etc/dci-controller/ /etc/

# clean source code
RUN rm -rf $DCI_C_SRC

COPY bootstrap.sh /opt/bootstrap.sh
RUN chmod 755 /opt/bootstrap.sh

# run cmd
ENTRYPOINT ["/opt/bootstrap.sh"]
CMD ["/usr/local/bin/dci-controller-api"]
