#!/bin/bash
if [ "$1" == "--help" ];then
    echo "./$(basename "$0") [--help|--clear-data=true]"
    echo "--clear-data=true     data folder will be cleared. unless specified a copy of files  under ./data directory will be saved for post redeply"
    echo "--help                show this help file"
else
    echo "stopping task_runner container as a hack, so that zeroDay service will be stopable. this may take a few seconds..."    
    docker container stop task_runner
    service zeroDay stop
    cd /opt
    mkdir -p archivedDeployments
    archiveName=`date +%Y_%m_%d__%H_%M_%S.tar.gz`
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
    git remote set-url origin git@github.com:python-ai-bootcamp/zeroDay.git
    chmod 777 ./installService.sh ./tailLog.sh ./redeploy.sh ./renewCertificate.sh
    service zeroDay start
    cd $PWD
    $SHELL
fi