#!/bin/bash
exit_script() {
    echo "recieved signal, setting continueWorking=false"
    continueWorking=false
}

trap exit_script SIGINT SIGTERM
continueWorking="true"
while [ "${continueWorking}" == "true" ];
do
  echo "`date`:: continueWorking='${continueWorking}', so i'm continuing to work"
  sleep 1;
done;
