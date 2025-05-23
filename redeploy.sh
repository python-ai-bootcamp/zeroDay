#!/bin/bash
if [ "$1" == "--help" ];then
    echo "./$(basename "$0") [--help|--clear-data=true]"
    echo "--clear-data=true     data folder will be cleared. unless specified a copy of files  under ./data directory will be saved for post redeply"
    echo "--help                show this help file"
else
    service zeroDay stop
    cd /opt
    mkdir -p ./archivedDeployments
    archiveName=`date +%Y_%m_%d__%H_%M_%S.tar.gz`
    mv ./zeroDay/resources/keys/private_keys ./archivedDeployments/
    mv ./zeroDay/resources/uncommitted_configurations ./archivedDeployments/
    tar -zcvf ./archivedDeployments/${archiveName} ./zeroDay/*
    rm -rf ./zeroDay
    yum install git -y
    git clone https://github.com/python-ai-bootcamp/zeroDay.git
    if [ "$1" == "--clear-data=true" ];then
        echo "--clear-data=true, data will be cleared"
    else
        tar -zxvf ./archivedDeployments/${archiveName} ./zeroDay/data
    fi
    cd ./zeroDay
    rm -rf ./resources/keys/private_keys
    rm -rf ./resources/uncommitted_configurations
    mv ../archivedDeployments/private_keys ./resources/keys/
    mv ../archivedDeployments/uncommitted_configurations ./resources/
    git remote set-url origin git@github.com:python-ai-bootcamp/zeroDay.git
    chmod 777 ./installService.sh ./tailLog.sh ./redeploy.sh ./renewCertificate.sh ./rebuildDockerImage.sh
    service zeroDay start
    cd $PWD
    $SHELL
fi