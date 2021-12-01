#!/bin/bash

if [ "$1" = '/usr/local/bin/dci-controller-api' ]; then

    # Initialize database
    /usr/local/bin/dci-controller-dbsync --config-file /etc/dci-controller/dci-controller.conf upgrade

    # Run api service
    /usr/local/bin/dci-controller-api --config-file /etc/dci-controller/dci-controller.conf
fi
