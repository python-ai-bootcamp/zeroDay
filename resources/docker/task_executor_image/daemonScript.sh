#!/bin/bash
exit_script() {
    echo "`date`:: sandbox service docker daemon:: recieved SIGTERM or SIGINT signal, setting continueWorking='false', will exit in next iteration"
    continueWorking=false
}

trap exit_script SIGINT SIGTERM
continueWorking="true"
while [ "${continueWorking}" == "true" ];
do
  echo "`date`:: sandbox service docker daemon:: continueWorking='${continueWorking}' -> not exiting"
  sleep 5;
done;
