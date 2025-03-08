#!/bin/bash
service zeroDay stop
cd /opt
mkdir -p archivedDeployments
tar -zcvf ./archivedDeployments/`date +%Y_%m_%d__%H_%M_%S`.tar.gz ./zeroDay/*
rm -rf ./zeroDay
yum install git -y
git clone https://github.com/python-ai-bootcamp/zeroDay.git
cd ./zeroDay
git remote set-url origin git@github.com:python-ai-bootcamp/zeroDay.git
chmod 777 ./installService.sh ./tailLog.sh ./redeploy.sh ./renewCertificate.sh
service zeroDay start
cd $PWD
$SHELL
